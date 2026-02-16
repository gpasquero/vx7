"""Optional MIDI input handler for the VX7 DX7 emulator.

MIDI support is entirely optional.  If python-rtmidi is not installed the
application continues to work via the on-screen keyboard.  MIDI can be
enabled and disabled at runtime without restarting the app.

All public methods are safe to call from any thread.  Callbacks are invoked
on the rtmidi listener thread -- callers that need to interact with the GUI
or audio engine should use appropriate synchronisation.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class MidiHandler:
    """Optional MIDI input handler using python-rtmidi.

    MIDI is not required -- the app works without it via the on-screen
    keyboard.  MIDI can be enabled / disabled at runtime.
    """

    # MIDI status bytes (upper nibble -- channel is lower nibble).
    _NOTE_OFF = 0x80
    _NOTE_ON = 0x90
    _CONTROL_CHANGE = 0xB0

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._enabled = False
        self._midi_in: Optional[object] = None  # rtmidi.MidiIn instance
        self._port_index: Optional[int] = None
        self._port_name: Optional[str] = None
        self._note_on_cb: Optional[Callable[[int, int], None]] = None
        self._note_off_cb: Optional[Callable[[int], None]] = None
        self._cc_cb: Optional[Callable[[int, int], None]] = None
        self._available = self._check_rtmidi()

    # ------------------------------------------------------------------
    # Availability / state queries
    # ------------------------------------------------------------------

    @staticmethod
    def _check_rtmidi() -> bool:
        """Return True if python-rtmidi is installed and importable."""
        try:
            import rtmidi  # noqa: F401
            return True
        except ImportError:
            logger.info("python-rtmidi not installed -- MIDI support disabled")
            return False

    @property
    def available(self) -> bool:
        """Whether MIDI support is available (python-rtmidi installed)."""
        return self._available

    @property
    def enabled(self) -> bool:
        """Whether MIDI input is currently active."""
        with self._lock:
            return self._enabled

    @property
    def port_name(self) -> Optional[str]:
        """Name of the currently open port, or None."""
        with self._lock:
            return self._port_name

    # ------------------------------------------------------------------
    # Port enumeration
    # ------------------------------------------------------------------

    def list_ports(self) -> list[str]:
        """List available MIDI input port names.

        Returns an empty list when python-rtmidi is not installed or if
        querying the system fails for any reason.
        """
        if not self._available:
            return []
        try:
            import rtmidi
            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()
            del midi_in
            return ports
        except Exception:
            logger.exception("Failed to enumerate MIDI ports")
            return []

    # ------------------------------------------------------------------
    # Opening / closing ports
    # ------------------------------------------------------------------

    def open_port(self, port_index: int) -> bool:
        """Open a MIDI input port by index.

        If a port is already open it is closed first.  Returns True on
        success, False on any failure.
        """
        if not self._available:
            logger.warning("Cannot open MIDI port -- rtmidi not available")
            return False

        with self._lock:
            return self._open_port_locked(port_index)

    def _open_port_locked(self, port_index: int) -> bool:
        """Internal port opener -- must be called with *_lock* held."""
        # Close any existing connection first.
        self._close_port_locked()

        try:
            import rtmidi

            midi_in = rtmidi.MidiIn()
            ports = midi_in.get_ports()

            if port_index < 0 or port_index >= len(ports):
                logger.error(
                    "MIDI port index %d out of range (0..%d)",
                    port_index,
                    len(ports) - 1,
                )
                del midi_in
                return False

            midi_in.open_port(port_index)
            midi_in.set_callback(self._midi_callback)
            # We do not need sysex or timing for basic use.
            midi_in.ignore_types(sysex=True, timing=True, active_sense=True)

            self._midi_in = midi_in
            self._port_index = port_index
            self._port_name = ports[port_index]
            logger.info("Opened MIDI port %d: %s", port_index, self._port_name)
            return True

        except Exception:
            logger.exception("Failed to open MIDI port %d", port_index)
            self._midi_in = None
            self._port_index = None
            self._port_name = None
            return False

    def close_port(self) -> None:
        """Close the current MIDI port (if any)."""
        with self._lock:
            self._close_port_locked()

    def _close_port_locked(self) -> None:
        """Internal port closer -- must be called with *_lock* held."""
        if self._midi_in is not None:
            try:
                self._midi_in.close_port()
            except Exception:
                logger.exception("Error closing MIDI port")
            try:
                del self._midi_in
            except Exception:
                pass
            self._midi_in = None
            self._port_index = None
            name = self._port_name
            self._port_name = None
            logger.info("Closed MIDI port: %s", name)

    # ------------------------------------------------------------------
    # Enable / disable
    # ------------------------------------------------------------------

    def enable(self, port_index: int = 0) -> bool:
        """Enable MIDI input on the given port.

        Opens the port (closing any previously open port) and marks MIDI
        as enabled.  Returns True on success.
        """
        if not self._available:
            logger.warning("Cannot enable MIDI -- rtmidi not available")
            return False

        with self._lock:
            if not self._open_port_locked(port_index):
                return False
            self._enabled = True
            logger.info("MIDI enabled on port %d", port_index)
            return True

    def disable(self) -> None:
        """Disable MIDI input and close the port."""
        with self._lock:
            self._enabled = False
            self._close_port_locked()
            logger.info("MIDI disabled")

    # ------------------------------------------------------------------
    # Auto-detect
    # ------------------------------------------------------------------

    def auto_connect(self) -> bool:
        """Try to connect to the first available MIDI input port.

        Returns True if a port was found and opened successfully, False
        otherwise.  This is a convenience wrapper around :meth:`enable`.
        """
        ports = self.list_ports()
        if not ports:
            logger.info("No MIDI ports detected for auto-connect")
            return False

        for index, name in enumerate(ports):
            logger.info("Auto-connect: trying port %d (%s)", index, name)
            if self.enable(index):
                return True

        logger.warning("Auto-connect: failed to open any MIDI port")
        return False

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def set_callbacks(
        self,
        note_on: Callable[[int, int], None],
        note_off: Callable[[int], None],
        cc: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """Set callback functions for MIDI events.

        Parameters
        ----------
        note_on : callable(note: int, velocity: int)
            Called on Note On messages (velocity > 0).
        note_off : callable(note: int)
            Called on Note Off messages (including Note On with velocity 0).
        cc : callable(control: int, value: int), optional
            Called on Control Change messages.
        """
        with self._lock:
            self._note_on_cb = note_on
            self._note_off_cb = note_off
            self._cc_cb = cc

    # ------------------------------------------------------------------
    # Internal MIDI message parsing
    # ------------------------------------------------------------------

    def _midi_callback(self, event: tuple, data: object = None) -> None:
        """Internal callback invoked by rtmidi on its listener thread.

        *event* is a tuple ``(message_bytes, delta_time)`` where
        ``message_bytes`` is a list of ints.

        Parsed message types:

        * ``0x90`` -- Note On (velocity > 0); Note On with velocity 0 is
          treated as Note Off.
        * ``0x80`` -- Note Off.
        * ``0xB0`` -- Control Change.

        Running status is handled by rtmidi itself so we do not need to
        track it here.
        """
        try:
            message, _delta_time = event
            if not message:
                return

            status = message[0]
            msg_type = status & 0xF0  # strip channel nibble

            # Grab a snapshot of the callbacks under the lock so that the
            # actual invocations happen outside the lock (avoids potential
            # deadlocks if a callback tries to call back into MidiHandler).
            with self._lock:
                if not self._enabled:
                    return
                note_on_cb = self._note_on_cb
                note_off_cb = self._note_off_cb
                cc_cb = self._cc_cb

            if msg_type == self._NOTE_ON and len(message) >= 3:
                note = message[1] & 0x7F
                velocity = message[2] & 0x7F
                if velocity == 0:
                    # Note On with velocity 0 is equivalent to Note Off.
                    if note_off_cb is not None:
                        note_off_cb(note)
                else:
                    if note_on_cb is not None:
                        note_on_cb(note, velocity)

            elif msg_type == self._NOTE_OFF and len(message) >= 3:
                note = message[1] & 0x7F
                if note_off_cb is not None:
                    note_off_cb(note)

            elif msg_type == self._CONTROL_CHANGE and len(message) >= 3:
                control = message[1] & 0x7F
                value = message[2] & 0x7F
                if cc_cb is not None:
                    cc_cb(control, value)

        except Exception:
            # Never let an exception escape into the rtmidi thread.
            logger.exception("Error in MIDI callback")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def destroy(self) -> None:
        """Release all MIDI resources.

        Safe to call multiple times.  After calling destroy the handler
        should not be reused.
        """
        with self._lock:
            self._enabled = False
            self._note_on_cb = None
            self._note_off_cb = None
            self._cc_cb = None
            self._close_port_locked()
            logger.info("MidiHandler destroyed")
