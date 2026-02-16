"""VX7 main application window.

Creates the top-level Tk window, instantiates the control panel, and
provides the public API for connecting the GUI to the synth engine
and audio output.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from .styles import (
    BODY_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT,
)
from .panel import VX7Panel


# Callback type aliases.
NoteOnCallback = Callable[[int, int], None]
NoteOffCallback = Callable[[int], None]
PresetCallback = Callable[[int], None]
ParamCallback = Callable[[str, object], None]


class VX7App:
    """Main VX7 application window."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("VX7 - Virtual DX7 Synthesizer")
        self.root.configure(bg=BODY_COLOR)
        self.root.resizable(False, False)

        # Center the window on screen.
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = (screen_h - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Build the panel.
        self._panel = VX7Panel(self.root)
        self._panel.pack(fill="both", expand=True)

        # Keyboard shortcut: Escape to quit.
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Computer keyboard -> piano key mapping.
        self._setup_computer_keyboard()

    # ------------------------------------------------------------------
    # Computer keyboard mapping
    # ------------------------------------------------------------------

    def _setup_computer_keyboard(self) -> None:
        """Map computer keyboard keys to piano MIDI notes.

        Uses a debounce mechanism for KeyRelease to defeat the OS
        auto-repeat which sends rapid Release/Press pairs.  When a
        KeyRelease arrives we schedule the actual release after a
        short delay.  If a KeyPress for the same key arrives before
        the timer fires we cancel the pending release — the note
        keeps sounding without interruption.
        """
        # Lower row: Z..M -> C3 (60) .. B3 (71)
        lower_keys = {
            "z": 60, "s": 61, "x": 62, "d": 63, "c": 64,
            "v": 65, "g": 66, "b": 67, "h": 68, "n": 69,
            "j": 70, "m": 71,
        }
        # Upper row: q..u -> C4 (72) .. B4 (83)
        upper_keys = {
            "q": 72, "2": 73, "w": 74, "3": 75, "e": 76,
            "r": 77, "5": 78, "t": 79, "6": 80, "y": 81,
            "7": 82, "u": 83,
        }

        self._key_map: dict[str, int] = {**lower_keys, **upper_keys}
        self._comp_keys_held: set[str] = set()
        # Pending release timers: key -> after-id
        self._release_timers: dict[str, str] = {}

        self.root.bind("<KeyPress>", self._on_keypress)
        self.root.bind("<KeyRelease>", self._on_keyrelease)

        # Arrow keys for preset navigation.
        self.root.bind("<Up>", self._on_preset_up)
        self.root.bind("<Down>", self._on_preset_down)

    def _on_keypress(self, event: tk.Event) -> None:
        key = event.char.lower() if event.char else event.keysym.lower()
        if key not in self._key_map:
            return

        # Cancel any pending release for this key (defeats auto-repeat).
        if key in self._release_timers:
            self.root.after_cancel(self._release_timers.pop(key))

        if key not in self._comp_keys_held:
            self._comp_keys_held.add(key)
            note = self._key_map[key]
            self._panel._key_press(note)

    def _on_keyrelease(self, event: tk.Event) -> None:
        key = event.char.lower() if event.char else event.keysym.lower()
        if key not in self._key_map or key not in self._comp_keys_held:
            return

        # Schedule the release after a short delay.  If a KeyPress
        # arrives within this window the release is cancelled.
        # 30 ms is enough to absorb the OS auto-repeat gap.
        timer_id = self.root.after(30, self._do_release, key)
        self._release_timers[key] = timer_id

    def _do_release(self, key: str) -> None:
        """Actually release the note after the debounce window."""
        self._release_timers.pop(key, None)
        if key in self._comp_keys_held:
            self._comp_keys_held.discard(key)
            note = self._key_map[key]
            self._panel._key_release(note)

    def _on_preset_up(self, _event: tk.Event) -> None:
        """Arrow Up -> next preset (higher number)."""
        self._panel.navigate_preset(1)

    def _on_preset_down(self, _event: tk.Event) -> None:
        """Arrow Down -> previous preset (lower number)."""
        self._panel.navigate_preset(-1)

    # ------------------------------------------------------------------
    # Callback setters
    # ------------------------------------------------------------------

    def set_note_callback(
        self,
        note_on_cb: Optional[NoteOnCallback],
        note_off_cb: Optional[NoteOffCallback],
    ) -> None:
        """Set callbacks for note on/off events from the GUI keyboard."""
        self._panel.set_note_callbacks(note_on_cb, note_off_cb)

    def set_preset_callback(self, cb: Optional[PresetCallback]) -> None:
        """Set callback for preset selection changes."""
        self._panel.set_preset_callback(cb)

    def set_param_callback(self, cb: Optional[ParamCallback]) -> None:
        """Set callback for parameter / function button changes."""
        self._panel.set_param_callback(cb)

    # ------------------------------------------------------------------
    # Display updates (called from synth/preset engine)
    # ------------------------------------------------------------------

    def update_display(self, line1: str, line2: str) -> None:
        """Update both lines of the LCD display."""
        self._panel.update_display(line1, line2)

    def update_display_line2(self, text: str) -> None:
        """Update only the second LCD line."""
        self._panel.update_display_line2(text)

    def update_preset(self, index: int, name: str) -> None:
        """Update the currently selected preset display."""
        self._panel.update_preset(index, name)

    def update_algorithm(self, algo_num: int) -> None:
        """Update the algorithm topology display."""
        self._panel.update_algorithm(algo_num)

    def set_operator_state(self, op_index: int, enabled: bool) -> None:
        """Enable/disable an operator visually."""
        self._panel.set_operator_state(op_index, enabled)

    def set_patch_number(self, num: int) -> None:
        """Update the 7-segment patch number display."""
        self._panel.set_patch_number(num)

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    @property
    def panel(self) -> VX7Panel:
        """Direct access to the panel widget."""
        return self._panel

    def get_volume(self) -> float:
        """Get the current master volume."""
        return self._panel.get_volume()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the Tk main loop (blocks until window is closed)."""
        self.root.mainloop()


# Allow quick testing: python -m gui.app
if __name__ == "__main__":
    app = VX7App()
    app.run()
