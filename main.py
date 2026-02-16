#!/usr/bin/env python3
"""VX7 - Virtual DX7 Synthesizer.

Main entry point.  Wires together the FM synthesis engine, the GUI,
the audio output, and the optional MIDI handler.

    python main.py
"""

from __future__ import annotations

import sys
import threading
from typing import Any

from engine.synth import Synth
from audio.output import AudioEngine
from midi.handler import MidiHandler
from gui.app import VX7App
from presets.factory import FACTORY_PRESETS, get_preset, get_preset_names


# ======================================================================
# Preset format conversion
# ======================================================================
# The factory preset format (presets/factory.py) uses:
#   - "operators": list of 6 dicts with keys like "rate", "level",
#     "freq_coarse", "freq_fine", "break_point", "detune" (7=center)
#   - "algorithm": 1-based (1-32)
#   - LFO uses "wave" and "sync"
#
# The engine Voice.load_preset() expects:
#   - "op1".."op6" as separate keys with "rate1".."rate4", "level1".."level4",
#     "coarse", "fine", "kls_breakpoint", "detune" (-7..+7, 0=center)
#   - "algorithm": 0-based (0-31)
#   - LFO uses "waveform" and "key_sync"
# ======================================================================

def convert_preset(factory_preset: dict[str, Any]) -> dict[str, Any]:
    """Convert a factory preset dict to the engine Voice format."""
    result: dict[str, Any] = {
        "name": factory_preset["name"],
        "algorithm": factory_preset["algorithm"] - 1,  # 1-based -> 0-based
        "feedback": factory_preset["feedback"],
    }

    # LFO conversion.
    lfo_src = factory_preset.get("lfo", {})
    result["lfo"] = {
        "waveform": lfo_src.get("wave", 0),
        "speed": lfo_src.get("speed", 35),
        "delay": lfo_src.get("delay", 0),
        "pmd": lfo_src.get("pmd", 0),
        "amd": lfo_src.get("amd", 0),
        "key_sync": bool(lfo_src.get("sync", 1)),
    }

    # Operators.
    ops = factory_preset.get("operators", [])
    for i, op in enumerate(ops):
        rates = op.get("rate", [99, 99, 99, 99])
        levels = op.get("level", [99, 99, 0, 0])
        detune_raw = op.get("detune", 7)
        detune = detune_raw - 7  # 0-14 (7=center) -> -7..+7 (0=center)

        result[f"op{i + 1}"] = {
            "osc_mode": op.get("osc_mode", 0),
            "coarse": op.get("freq_coarse", 1),
            "fine": op.get("freq_fine", 0),
            "detune": detune,
            "output_level": op.get("output_level", 0),
            "rate1": rates[0],
            "rate2": rates[1],
            "rate3": rates[2],
            "rate4": rates[3],
            "level1": levels[0],
            "level2": levels[1],
            "level3": levels[2],
            "level4": levels[3],
            "velocity_sensitivity": op.get("key_vel_sens", 0),
            "key_rate_scaling": op.get("rate_scaling", 0),
            "kls_breakpoint": op.get("break_point", 60),
            "kls_left_depth": op.get("left_depth", 0),
            "kls_right_depth": op.get("right_depth", 0),
            "kls_left_curve": op.get("left_curve", 0),
            "kls_right_curve": op.get("right_curve", 0),
        }

    return result


# ======================================================================
# Application controller
# ======================================================================

class VX7Controller:
    """Connects the synth engine, audio, MIDI, and GUI."""

    def __init__(self) -> None:
        # --- Synth engine ---
        self.synth = Synth(polyphony=16, sample_rate=44100)

        # --- Audio output ---
        self.audio = AudioEngine(sample_rate=44100)
        self.audio.set_render_callback(self.synth.render)

        # --- MIDI (optional) ---
        self.midi = MidiHandler()

        # --- GUI ---
        self.gui = VX7App()

        # --- State ---
        self._current_preset_index: int = 0
        self._preset_names: list[str] = get_preset_names()
        self._converted_presets: list[dict[str, Any]] = [
            convert_preset(p) for p in FACTORY_PRESETS
        ]

        # --- Wire everything ---
        self._setup_callbacks()
        self._load_preset(0)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_callbacks(self) -> None:
        """Connect GUI and MIDI callbacks to the synth engine."""
        # GUI note callbacks.
        self.gui.set_note_callback(self._on_note_on, self._on_note_off)
        self.gui.set_preset_callback(self._on_preset_select)
        self.gui.set_param_callback(self._on_param_change)

        # MIDI callbacks (thread-safe: synth.note_on/off are safe to call
        # from any thread since they only touch voice state that is read
        # during the audio callback's render() — Python's GIL serialises
        # these accesses).
        if self.midi.available:
            self.midi.set_callbacks(
                note_on=self._on_note_on,
                note_off=self._on_note_off,
            )
            # Try auto-connecting to the first available MIDI port.
            if self.midi.auto_connect():
                port = self.midi.port_name or "unknown"
                print(f"[VX7] MIDI connected: {port}")
            else:
                print("[VX7] No MIDI devices found (use on-screen keyboard)")
        else:
            print("[VX7] MIDI support not available (python-rtmidi not installed)")

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_note_on(self, note: int, velocity: int) -> None:
        self.synth.note_on(note, velocity)

    def _on_note_off(self, note: int) -> None:
        self.synth.note_off(note)

    def _on_preset_select(self, index: int) -> None:
        self._load_preset(index)

    def _on_param_change(self, param: str, value: object) -> None:
        if param == "volume":
            vol = float(value) if value is not None else 0.7
            self.audio.volume = vol
        elif param == "algorithm_up":
            self._change_algorithm(1)
        elif param == "algorithm_down":
            self._change_algorithm(-1)

    # ------------------------------------------------------------------
    # Preset management
    # ------------------------------------------------------------------

    def _load_preset(self, index: int) -> None:
        """Load a factory preset by index (0-31)."""
        index = max(0, min(index, len(self._converted_presets) - 1))
        self._current_preset_index = index
        preset = self._converted_presets[index]
        self.synth.load_preset(preset)

        name = preset["name"]
        algo = preset["algorithm"] + 1  # show 1-based to user

        # Update GUI.
        self.gui.update_preset(index, name)
        self.gui.update_algorithm(algo)
        self.gui.update_display(
            f"{index + 1:2d} {name:<13s}",
            f"ALGO {algo:2d}  FB {preset['feedback']}",
        )

    def _change_algorithm(self, delta: int) -> None:
        """Cycle algorithm up or down for the current preset."""
        preset = self._converted_presets[self._current_preset_index]
        new_algo = (preset["algorithm"] + delta) % 32
        preset["algorithm"] = new_algo
        self.synth.load_preset(preset)
        self.gui.update_algorithm(new_algo + 1)
        self.gui.update_display_line2(f"ALGO {new_algo + 1:2d}  FB {preset['feedback']}")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start audio and run the GUI main loop (blocks until closed)."""
        try:
            self.audio.start()
            print("[VX7] Audio engine started")
            print(f"[VX7] Latency: {self.audio.latency_ms:.1f} ms")
        except RuntimeError as e:
            print(f"[VX7] WARNING: Could not start audio: {e}")
            print("[VX7] Running in silent mode (no audio output)")

        try:
            self.gui.run()
        finally:
            self._shutdown()

    def _shutdown(self) -> None:
        """Clean up all resources."""
        print("[VX7] Shutting down...")
        self.synth.panic()
        self.audio.destroy()
        self.midi.destroy()
        print("[VX7] Goodbye!")


# ======================================================================
# Entry point
# ======================================================================

def main() -> None:
    print("=" * 50)
    print("  VX7 - Virtual DX7 Synthesizer")
    print("  FM Synthesis · 32 Factory Presets · MIDI")
    print("=" * 50)
    print()

    controller = VX7Controller()
    controller.run()


if __name__ == "__main__":
    main()
