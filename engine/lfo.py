"""DX7 Low Frequency Oscillator (LFO).

The DX7 LFO provides pitch modulation (vibrato) and amplitude modulation
(tremolo) to all 6 operators simultaneously.

Parameters:
    - Waveform: Triangle, Saw Down, Saw Up, Square, Sine, Sample & Hold
    - Speed: 0-99 (maps to ~0.06 Hz to ~50 Hz)
    - Delay: 0-99 (time before the LFO reaches full depth after key-on)
    - PMD: Pitch Mod Depth 0-99
    - AMD: Amplitude Mod Depth 0-99
    - Key Sync: if True, LFO phase resets on each key-on
"""

from __future__ import annotations

import math
from enum import IntEnum
from typing import Optional

import numpy as np


class LFOWaveform(IntEnum):
    """DX7 LFO waveform types."""
    TRIANGLE = 0
    SAW_DOWN = 1
    SAW_UP = 2
    SQUARE = 3
    SINE = 4
    SAMPLE_AND_HOLD = 5


# ---------------------------------------------------------------------------
# Speed / Delay conversion
# ---------------------------------------------------------------------------

def _speed_to_hz(speed: int) -> float:
    """Convert DX7 LFO speed (0-99) to frequency in Hz.

    The DX7 LFO frequency range is approximately 0.06 Hz (speed 0) to
    ~50 Hz (speed 99).  The mapping is roughly exponential.
    """
    speed = int(np.clip(speed, 0, 99))
    # Exponential mapping: hz = 0.06 * e^(speed * k)
    # Solve for k:  50 = 0.06 * e^(99*k)  =>  k = ln(50/0.06)/99 ~ 0.0684
    return 0.062 * math.exp(speed * 0.0684)


def _delay_to_seconds(delay: int) -> float:
    """Convert DX7 LFO delay (0-99) to fade-in time in seconds.

    delay 0 => 0 seconds (immediate)
    delay 99 => ~5 seconds
    """
    delay = int(np.clip(delay, 0, 99))
    if delay == 0:
        return 0.0
    return delay * delay * 0.0005  # quadratic curve, max ~ 4.9 s


# ---------------------------------------------------------------------------
# LFO class
# ---------------------------------------------------------------------------

class LFO:
    """DX7 Low Frequency Oscillator.

    Parameters
    ----------
    waveform : int
        Waveform type (0-5), see LFOWaveform.
    speed : int
        LFO speed 0-99.
    delay : int
        LFO delay 0-99.
    pmd : int
        Pitch modulation depth 0-99.
    amd : int
        Amplitude modulation depth 0-99.
    key_sync : bool
        If True, phase resets on gate_on.
    sample_rate : int
        Audio sample rate in Hz.
    """

    def __init__(
        self,
        waveform: int = LFOWaveform.TRIANGLE,
        speed: int = 35,
        delay: int = 0,
        pmd: int = 0,
        amd: int = 0,
        key_sync: bool = True,
        sample_rate: int = 44100,
    ) -> None:
        self.waveform = LFOWaveform(int(np.clip(waveform, 0, 5)))
        self.speed = int(np.clip(speed, 0, 99))
        self.delay = int(np.clip(delay, 0, 99))
        self.pmd = int(np.clip(pmd, 0, 99))
        self.amd = int(np.clip(amd, 0, 99))
        self.key_sync = key_sync
        self.sample_rate = sample_rate

        # Derived.
        self._freq: float = _speed_to_hz(self.speed)
        self._delay_time: float = _delay_to_seconds(self.delay)
        self._delay_samples: int = int(round(self._delay_time * sample_rate))

        # Runtime state.
        self._phase: float = 0.0           # 0.0 .. 1.0 normalised phase
        self._sample_counter: int = 0      # counts samples since gate_on
        self._sh_value: float = 0.0        # held Sample & Hold value
        self._sh_last_phase: float = 0.0   # phase at last S&H trigger

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def gate_on(self) -> None:
        """Reset LFO state for a new note (if key_sync is enabled)."""
        if self.key_sync:
            self._phase = 0.0
        self._sample_counter = 0
        self._sh_value = 0.0
        self._sh_last_phase = 0.0

    def render(
        self, num_samples: int, extra_pmd: float = 0.0,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generate LFO output for *num_samples*.

        Parameters
        ----------
        extra_pmd : float
            Additional pitch modulation depth (0.0-1.0) added by the mod
            wheel.  At 1.0 the effective PMD is clamped to 99.

        Returns
        -------
        pitch_mod : np.ndarray
            Pitch modulation values, bipolar (-1.0 .. +1.0) scaled by PMD.
            Shape (num_samples,).
        amp_mod : np.ndarray
            Amplitude modulation values, unipolar (0.0 .. 1.0) where 1.0
            means no attenuation, scaled by AMD.  Shape (num_samples,).
        """
        # Phase ramp for this block.
        phase_inc = self._freq / self.sample_rate
        t = np.arange(num_samples, dtype=np.float64)
        phases = (self._phase + phase_inc * t) % 1.0

        # Generate raw waveform in range -1.0 .. +1.0.
        raw = self._generate_waveform(phases)

        # Apply delay fade-in.
        if self._delay_samples > 0:
            fade = self._compute_delay_fade(num_samples)
            raw = raw * fade

        # Pitch modulation: bipolar, scaled by effective PMD / 99.
        effective_pmd = min(99.0, self.pmd + extra_pmd * 99.0)
        pmd_scale = effective_pmd / 99.0
        pitch_mod = raw * pmd_scale

        # Amplitude modulation: convert bipolar waveform to unipolar
        # attenuation.  When AMD = 0, amp_mod = 1.0 (no effect).
        # When AMD = 99, the LFO fully modulates the amplitude.
        amd_scale = self.amd / 99.0
        # raw is -1..+1; map to 0..1 attenuation depth.
        # amp_mod = 1.0 - amd_scale * (1.0 - raw) * 0.5
        # This gives: raw=+1 => amp_mod = 1.0, raw=-1 => amp_mod = 1.0 - amd_scale
        amp_mod = 1.0 - amd_scale * (1.0 - raw) * 0.5

        # Advance phase.
        self._phase = float((self._phase + phase_inc * num_samples) % 1.0)
        self._sample_counter += num_samples

        return pitch_mod, amp_mod

    def reset(self) -> None:
        """Reset LFO to initial state."""
        self._phase = 0.0
        self._sample_counter = 0
        self._sh_value = 0.0
        self._sh_last_phase = 0.0

    # ------------------------------------------------------------------
    # Waveform generation
    # ------------------------------------------------------------------

    def _generate_waveform(self, phases: np.ndarray) -> np.ndarray:
        """Generate the raw waveform for given normalised phases (0..1).

        Returns values in -1.0 .. +1.0.
        """
        wf = self.waveform

        if wf == LFOWaveform.SINE:
            return np.sin(2.0 * np.pi * phases)

        elif wf == LFOWaveform.TRIANGLE:
            # Triangle: linear ramp up then down.
            # phase 0 -> 0, phase 0.25 -> +1, phase 0.5 -> 0,
            # phase 0.75 -> -1, phase 1.0 -> 0
            return (2.0 * np.abs(2.0 * phases - 1.0) - 1.0) * -1.0

        elif wf == LFOWaveform.SAW_DOWN:
            return 1.0 - 2.0 * phases

        elif wf == LFOWaveform.SAW_UP:
            return 2.0 * phases - 1.0

        elif wf == LFOWaveform.SQUARE:
            return np.where(phases < 0.5, 1.0, -1.0).astype(np.float64)

        elif wf == LFOWaveform.SAMPLE_AND_HOLD:
            return self._sample_and_hold(phases)

        return np.sin(2.0 * np.pi * phases)

    def _sample_and_hold(self, phases: np.ndarray) -> np.ndarray:
        """Generate sample-and-hold waveform.

        A new random value is latched at each LFO cycle start (phase wraps
        past 0).
        """
        rng = np.random.default_rng()
        output = np.empty(len(phases), dtype=np.float64)
        current_value = self._sh_value
        last_phase = self._sh_last_phase

        for i in range(len(phases)):
            # Detect phase wrap (new cycle).
            if phases[i] < last_phase - 0.5:
                # Phase wrapped around -- latch new random value.
                current_value = rng.uniform(-1.0, 1.0)
            output[i] = current_value
            last_phase = phases[i]

        self._sh_value = current_value
        self._sh_last_phase = float(last_phase)
        return output

    # ------------------------------------------------------------------
    # Delay fade-in
    # ------------------------------------------------------------------

    def _compute_delay_fade(self, num_samples: int) -> np.ndarray:
        """Compute a fade-in ramp for the LFO delay.

        Returns an array of multipliers (0.0 to 1.0) of length *num_samples*.
        """
        if self._delay_samples <= 0:
            return np.ones(num_samples, dtype=np.float64)

        start = self._sample_counter
        end = start + num_samples
        t = np.arange(start, end, dtype=np.float64)

        fade = np.clip(t / self._delay_samples, 0.0, 1.0)
        return fade
