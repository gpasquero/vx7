"""DX7 Voice -- a single note being played.

A Voice bundles together 6 Operators, 1 LFO, an algorithm selection, and a
feedback setting.  It receives gate-on / gate-off messages and renders audio.

The Voice loads its parameters from a *preset dictionary* whose format mirrors
the DX7 SysEx patch structure.
"""

from __future__ import annotations

import math
from typing import Any, Optional

import numpy as np

from .operator import Operator, OperatorParams, KeyboardLevelScaling
from .envelope import Envelope
from .lfo import LFO, LFOWaveform
from .algorithm import ALGORITHMS, apply_algorithm


# ---------------------------------------------------------------------------
# MIDI note -> frequency
# ---------------------------------------------------------------------------

def midi_note_to_freq(note: int) -> float:
    """Convert a MIDI note number (0-127) to frequency in Hz.

    Uses A4 = 440 Hz (MIDI note 69).
    """
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


# ---------------------------------------------------------------------------
# Default / init preset
# ---------------------------------------------------------------------------

def _default_preset() -> dict[str, Any]:
    """Return a minimal default preset (simple sine wave, algorithm 1)."""
    preset: dict[str, Any] = {
        "name": "INIT VOICE",
        "algorithm": 0,       # 0-based (DX7 algorithm 1)
        "feedback": 0,        # 0-7
        "lfo": {
            "waveform": 0,
            "speed": 35,
            "delay": 0,
            "pmd": 0,
            "amd": 0,
            "key_sync": True,
        },
        "pitch_eg": {
            "rates": [99, 99, 99, 99],
            "levels": [50, 50, 50, 50],
        },
    }
    # 6 operators.  Op 1 (index 0) is carrier at full level.
    # Ops 2-6 are at level 0 (silent).
    for i in range(6):
        op_key = f"op{i + 1}"
        preset[op_key] = {
            "osc_mode": 0,
            "coarse": 1,
            "fine": 0,
            "detune": 0,
            "output_level": 99 if i == 0 else 0,
            "rate1": 99, "rate2": 99, "rate3": 99, "rate4": 99,
            "level1": 99, "level2": 99, "level3": 99 if i == 0 else 0,
            "level4": 0,
            "velocity_sensitivity": 0,
            "key_rate_scaling": 0,
            "kls_breakpoint": 60,
            "kls_left_depth": 0,
            "kls_right_depth": 0,
            "kls_left_curve": 0,
            "kls_right_curve": 0,
        }
    return preset


# ---------------------------------------------------------------------------
# Voice class
# ---------------------------------------------------------------------------

class Voice:
    """A single polyphonic voice for the DX7 emulator.

    Parameters
    ----------
    sample_rate : int
        Audio sample rate in Hz.
    """

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate

        # Operators (created with defaults; overwritten by load_preset).
        self.operators: list[Operator] = [
            Operator(sample_rate=sample_rate) for _ in range(6)
        ]

        # LFO.
        self.lfo = LFO(sample_rate=sample_rate)

        # Algorithm (0-based: 0 = DX7 algorithm 1).
        self.algorithm: int = 0
        self.feedback: int = 0  # 0-7

        # Per-operator feedback state buffers (2 samples each).
        self._feedback_buffers: list[np.ndarray] = [
            np.zeros(2, dtype=np.float64) for _ in range(6)
        ]

        # Voice state.
        self._note: int = -1
        self._velocity: int = 0
        self._active: bool = False
        self._gate: bool = False
        self._age: int = 0  # increments each render call (for voice stealing)

        # Real-time controllers.
        self._pitch_bend_ratio: float = 1.0   # frequency multiplier (1.0 = center)
        self._mod_wheel: float = 0.0           # 0.0 - 1.0
        self._op_enabled: list[bool] = [True] * 6  # per-operator mute

        # Load default preset.
        self.load_preset(_default_preset())

    # ------------------------------------------------------------------
    # Preset loading
    # ------------------------------------------------------------------

    def load_preset(self, preset: dict[str, Any]) -> None:
        """Load a preset/patch dictionary into this voice.

        The preset dict should contain keys:
            - ``algorithm`` (int, 0-31)
            - ``feedback`` (int, 0-7)
            - ``lfo`` (dict with waveform, speed, delay, pmd, amd, key_sync)
            - ``op1`` .. ``op6`` (dicts with operator parameters)
        """
        self.algorithm = int(preset.get("algorithm", 0)) % 32
        self.feedback = int(np.clip(preset.get("feedback", 0), 0, 7))

        # LFO.
        lfo_data = preset.get("lfo", {})
        self.lfo = LFO(
            waveform=lfo_data.get("waveform", 0),
            speed=lfo_data.get("speed", 35),
            delay=lfo_data.get("delay", 0),
            pmd=lfo_data.get("pmd", 0),
            amd=lfo_data.get("amd", 0),
            key_sync=lfo_data.get("key_sync", True),
            sample_rate=self.sample_rate,
        )

        # Operators.
        for i in range(6):
            op_key = f"op{i + 1}"
            op_data = preset.get(op_key, {})

            kls = KeyboardLevelScaling(
                breakpoint=op_data.get("kls_breakpoint", 60),
                left_depth=op_data.get("kls_left_depth", 0),
                right_depth=op_data.get("kls_right_depth", 0),
                left_curve=op_data.get("kls_left_curve", 0),
                right_curve=op_data.get("kls_right_curve", 0),
            )

            params = OperatorParams(
                osc_mode=op_data.get("osc_mode", 0),
                coarse=op_data.get("coarse", 1),
                fine=op_data.get("fine", 0),
                detune=op_data.get("detune", 0),
                output_level=op_data.get("output_level", 0),
                rate1=op_data.get("rate1", 99),
                rate2=op_data.get("rate2", 99),
                rate3=op_data.get("rate3", 99),
                rate4=op_data.get("rate4", 99),
                level1=op_data.get("level1", 99),
                level2=op_data.get("level2", 99),
                level3=op_data.get("level3", 0),
                level4=op_data.get("level4", 0),
                velocity_sensitivity=op_data.get("velocity_sensitivity", 0),
                key_rate_scaling=op_data.get("key_rate_scaling", 0),
                kls=kls,
            )

            self.operators[i] = Operator(params=params,
                                          sample_rate=self.sample_rate)

    # ------------------------------------------------------------------
    # Note on / off
    # ------------------------------------------------------------------

    def gate_on(self, note: int, velocity: int) -> None:
        """Trigger the voice for a new note.

        Parameters
        ----------
        note : int
            MIDI note number (0-127).
        velocity : int
            MIDI velocity (1-127; 0 is treated as note-off by convention).
        """
        self._note = note
        self._velocity = velocity
        self._active = True
        self._gate = True
        self._age = 0

        base_freq = midi_note_to_freq(note)

        # Reset feedback buffers.
        for buf in self._feedback_buffers:
            buf[:] = 0.0

        # Trigger all operators.
        for op in self.operators:
            op.gate_on(note, velocity, base_freq)

        # Trigger LFO.
        self.lfo.gate_on()

    def gate_off(self) -> None:
        """Release the voice (note-off)."""
        self._gate = False
        for op in self.operators:
            op.gate_off()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Real-time controllers
    # ------------------------------------------------------------------

    def set_pitch_bend(self, ratio: float) -> None:
        """Set pitch bend as a frequency multiplier (1.0 = center)."""
        self._pitch_bend_ratio = ratio

    def set_mod_wheel(self, value: float) -> None:
        """Set mod wheel depth (0.0 - 1.0)."""
        self._mod_wheel = max(0.0, min(1.0, value))

    def set_operator_enabled(self, op_index: int, enabled: bool) -> None:
        """Enable or disable an operator (0-5)."""
        if 0 <= op_index < 6:
            self._op_enabled[op_index] = enabled

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, num_samples: int) -> np.ndarray:
        """Generate *num_samples* of audio for this voice.

        Returns
        -------
        np.ndarray
            Float64 array of shape (num_samples,) in range [-1.0, 1.0].
        """
        if not self._active:
            return np.zeros(num_samples, dtype=np.float64)

        self._age += 1

        # Generate LFO modulation (mod wheel adds extra PMD).
        pitch_mod, amp_mod = self.lfo.render(
            num_samples, extra_pmd=self._mod_wheel,
        )

        # Build per-sample frequency ratio from pitch bend + LFO pitch mod.
        freq_ratio = np.full(num_samples, self._pitch_bend_ratio,
                             dtype=np.float64)

        # Apply LFO pitch modulation.
        # pitch_mod is bipolar (-1..+1) scaled by PMD/99.
        # DX7 full PMD range is roughly +/- 1 octave (12 semitones).
        if np.any(pitch_mod != 0):
            pm_semitones = pitch_mod * 12.0
            freq_ratio = freq_ratio * (2.0 ** (pm_semitones / 12.0))

        # Render through the algorithm.
        output = apply_algorithm(
            operators=self.operators,
            algorithm_index=self.algorithm,
            feedback_param=self.feedback,
            num_samples=num_samples,
            base_freq=midi_note_to_freq(self._note),
            sample_rate=self.sample_rate,
            feedback_buffers=self._feedback_buffers,
            pitch_mod=pitch_mod,
            amp_mod=amp_mod,
            freq_ratio=freq_ratio,
            op_enabled=self._op_enabled,
        )

        # Check if voice has finished (all carrier envelopes idle).
        if not self._gate and not self.is_active():
            self._active = False

        return output

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_active(self) -> bool:
        """Return True if any carrier operator's envelope is still active.

        A voice should be considered active as long as at least one carrier
        envelope is producing output.  Once all carriers go idle, the voice
        can be recycled.
        """
        if self._gate:
            return True

        algo = ALGORITHMS[self.algorithm]
        for c_idx in algo.carriers:
            if self.operators[c_idx].is_active:
                return True
        return False

    @property
    def note(self) -> int:
        """The MIDI note currently assigned to this voice (-1 if none)."""
        return self._note

    @property
    def age(self) -> int:
        """How many render cycles this voice has been active."""
        return self._age

    def reset(self) -> None:
        """Hard-reset the voice to idle state."""
        self._note = -1
        self._velocity = 0
        self._active = False
        self._gate = False
        self._age = 0
        for op in self.operators:
            op.reset()
        self.lfo.reset()
        for buf in self._feedback_buffers:
            buf[:] = 0.0
