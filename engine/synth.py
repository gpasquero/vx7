"""DX7 Polyphonic Synthesizer.

Manages a pool of Voice objects with 16-voice polyphony (matching the
original DX7).  Handles note-on/off allocation, voice stealing, preset
loading, and audio mixing.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from .voice import Voice


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_POLYPHONY: int = 16
DEFAULT_SAMPLE_RATE: int = 44100


# ---------------------------------------------------------------------------
# Synth
# ---------------------------------------------------------------------------

class Synth:
    """Polyphonic DX7 synthesizer.

    Parameters
    ----------
    polyphony : int
        Maximum number of simultaneous voices (default 16).
    sample_rate : int
        Audio sample rate in Hz (default 44100).
    """

    def __init__(
        self,
        polyphony: int = DEFAULT_POLYPHONY,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ) -> None:
        self.polyphony = polyphony
        self.sample_rate = sample_rate

        # Voice pool.
        self.voices: list[Voice] = [
            Voice(sample_rate=sample_rate) for _ in range(polyphony)
        ]

        # Map from MIDI note -> voice index (for note-off lookup).
        self._note_to_voice: dict[int, int] = {}

        # Current preset (kept so new voices can be initialised).
        self._current_preset: Optional[dict[str, Any]] = None

        # Master volume (linear, 0.0 - 1.0).
        self.master_volume: float = 0.8

    # ------------------------------------------------------------------
    # Preset management
    # ------------------------------------------------------------------

    def load_preset(self, preset: dict[str, Any]) -> None:
        """Load a preset/patch into all voices.

        Parameters
        ----------
        preset : dict
            DX7 preset dictionary (see Voice.load_preset for format).
        """
        self._current_preset = preset
        for voice in self.voices:
            voice.load_preset(preset)

    # ------------------------------------------------------------------
    # Note on / off
    # ------------------------------------------------------------------

    def note_on(self, note: int, velocity: int) -> None:
        """Trigger a note.

        Parameters
        ----------
        note : int
            MIDI note number (0-127).
        velocity : int
            MIDI velocity (1-127).  Velocity 0 is treated as note-off.
        """
        if velocity == 0:
            self.note_off(note)
            return

        # If this note is already playing, release the old voice first.
        if note in self._note_to_voice:
            old_idx = self._note_to_voice.pop(note)
            self.voices[old_idx].gate_off()

        # Find a free voice.
        voice_idx = self._allocate_voice()

        # If the allocated voice was playing a different note, clean up the
        # note mapping.
        old_note = self.voices[voice_idx].note
        if old_note >= 0 and old_note in self._note_to_voice:
            if self._note_to_voice[old_note] == voice_idx:
                del self._note_to_voice[old_note]

        # Assign and trigger.
        self._note_to_voice[note] = voice_idx
        voice = self.voices[voice_idx]

        # Reload preset if one is set (ensures fresh operator state).
        if self._current_preset is not None:
            voice.load_preset(self._current_preset)

        voice.gate_on(note, velocity)

    def note_off(self, note: int) -> None:
        """Release a note.

        Parameters
        ----------
        note : int
            MIDI note number (0-127).
        """
        if note not in self._note_to_voice:
            return

        voice_idx = self._note_to_voice.pop(note)
        self.voices[voice_idx].gate_off()

    def all_notes_off(self) -> None:
        """Release all currently sounding notes."""
        for voice in self.voices:
            voice.gate_off()
        self._note_to_voice.clear()

    def panic(self) -> None:
        """Immediately silence all voices (hard reset)."""
        for voice in self.voices:
            voice.reset()
        self._note_to_voice.clear()

    # ------------------------------------------------------------------
    # Audio rendering
    # ------------------------------------------------------------------

    def render(self, num_samples: int) -> np.ndarray:
        """Mix all active voices and return the audio buffer.

        Parameters
        ----------
        num_samples : int
            Number of audio samples to generate.

        Returns
        -------
        np.ndarray
            Float64 array of shape (num_samples,) in range [-1.0, 1.0].
        """
        mix = np.zeros(num_samples, dtype=np.float64)

        for voice in self.voices:
            if voice.is_active() or voice._active:
                mix += voice.render(num_samples)

        # Apply master volume.
        mix *= self.master_volume

        # Soft clip to prevent harsh distortion.
        np.clip(mix, -1.0, 1.0, out=mix)

        return mix

    # ------------------------------------------------------------------
    # Voice allocation
    # ------------------------------------------------------------------

    def _allocate_voice(self) -> int:
        """Find a voice to use for a new note.

        Strategy:
        1. First, look for a completely idle voice (not active).
        2. If none, steal the oldest active voice (highest age counter).

        Returns
        -------
        int
            Index into self.voices.
        """
        # 1. Find an idle voice.
        for i, voice in enumerate(self.voices):
            if not voice.is_active() and not voice._active:
                return i

        # 2. Find a released (gate off but still decaying) voice -- prefer
        #    stealing these over held notes.
        best_released_idx: int = -1
        best_released_age: int = -1
        best_held_idx: int = -1
        best_held_age: int = -1

        for i, voice in enumerate(self.voices):
            if not voice._gate:
                # Released voice.
                if voice.age > best_released_age:
                    best_released_age = voice.age
                    best_released_idx = i
            else:
                # Still held.
                if voice.age > best_held_age:
                    best_held_age = voice.age
                    best_held_idx = i

        if best_released_idx >= 0:
            return best_released_idx

        if best_held_idx >= 0:
            return best_held_idx

        # Fallback: just use voice 0.
        return 0

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def active_voice_count(self) -> int:
        """Number of currently active (sounding) voices."""
        return sum(1 for v in self.voices if v.is_active() or v._active)

    def get_voice_status(self) -> list[dict[str, Any]]:
        """Return status information for all voices (useful for UI)."""
        status = []
        for i, voice in enumerate(self.voices):
            status.append({
                "index": i,
                "note": voice.note,
                "active": voice.is_active(),
                "gate": voice._gate,
                "age": voice.age,
            })
        return status
