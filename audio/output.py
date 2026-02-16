"""Real-time audio output engine for VX7.

Uses the ``sounddevice`` library in callback mode to achieve low-latency audio
output.  The engine accepts a *render callback* (typically the synth engine's
``render()`` method) that is invoked from the audio thread to fill each buffer.

The DX7 was a mono synthesizer, so we default to a single output channel.

Usage::

    from audio import AudioEngine

    engine = AudioEngine()
    engine.set_render_callback(synth.render)   # synth.render(n) -> np.ndarray
    engine.start()
    ...
    engine.stop()
    engine.destroy()
"""

from __future__ import annotations

import sys
import threading
from typing import Callable, List, Optional

import numpy as np

try:
    import sounddevice as sd
except ImportError:
    sd = None  # type: ignore[assignment]
except OSError as _exc:
    # sounddevice wraps PortAudio -- if the shared lib is missing we get
    # an OSError at import time.  Degrade gracefully.
    sd = None  # type: ignore[assignment]
    print(
        f"[AudioEngine] Warning: failed to import sounddevice ({_exc}). "
        "Audio output will be unavailable.",
        file=sys.stderr,
    )


class AudioEngine:
    """Real-time audio output engine using sounddevice.

    Uses a callback-based approach for low-latency audio output.
    The *render_callback* is called from the audio thread to fill each
    buffer -- it should be connected to the synth engine's ``render()``
    method.

    Parameters
    ----------
    sample_rate : int, optional
        Sample rate in Hz (default 44100).
    block_size : int, optional
        Frames per audio buffer.  Lower values reduce latency but increase
        CPU load.  256 frames at 44100 Hz gives ~5.8 ms latency.
    channels : int, optional
        Number of output channels (default 1 -- mono, matching the DX7).
    """

    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_BLOCK_SIZE = 256
    DEFAULT_CHANNELS = 1

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        block_size: int = DEFAULT_BLOCK_SIZE,
        channels: int = DEFAULT_CHANNELS,
    ) -> None:
        self._sample_rate: int = sample_rate
        self._block_size: int = block_size
        self._channels: int = channels

        self._stream: Optional["sd.OutputStream"] = None
        self._render_callback: Optional[Callable[[int], np.ndarray]] = None
        self._running: bool = False
        self._device: Optional[int] = None

        # Volume is read from the audio thread (lock-free read of a Python
        # float is safe on CPython due to the GIL, but we use a lock for
        # correctness on other runtimes and to group multi-field updates).
        self._volume: float = 0.7
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def sample_rate(self) -> int:
        """Audio sample rate in Hz."""
        return self._sample_rate

    @property
    def block_size(self) -> int:
        """Frames per audio buffer."""
        return self._block_size

    @property
    def channels(self) -> int:
        """Number of output channels."""
        return self._channels

    @property
    def volume(self) -> float:
        """Master volume (0.0 -- 1.0)."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, float(value)))

    @property
    def running(self) -> bool:
        """True while the audio stream is active."""
        return self._running

    @property
    def latency_ms(self) -> float:
        """Theoretical output latency in milliseconds."""
        return self._block_size / self._sample_rate * 1000.0

    # ------------------------------------------------------------------
    # Render callback
    # ------------------------------------------------------------------

    def set_render_callback(self, callback: Callable[[int], np.ndarray]) -> None:
        """Set the audio render callback.

        The callback signature is::

            callback(num_samples: int) -> np.ndarray

        It must return a ``float64`` numpy array of *num_samples* values
        in the range ``-1.0`` to ``1.0``.
        """
        with self._lock:
            self._render_callback = callback

    # ------------------------------------------------------------------
    # Stream lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the audio output stream.

        Raises
        ------
        RuntimeError
            If ``sounddevice`` is not available.
        """
        if sd is None:
            raise RuntimeError(
                "sounddevice is not available -- cannot start audio output. "
                "Install it with: pip install sounddevice"
            )

        with self._lock:
            if self._running:
                return

            kwargs: dict = dict(
                samplerate=self._sample_rate,
                blocksize=self._block_size,
                channels=self._channels,
                dtype="float32",
                callback=self._audio_callback,
                latency="low",
            )
            if self._device is not None:
                kwargs["device"] = self._device

            self._stream = sd.OutputStream(**kwargs)
            self._stream.start()
            self._running = True

    def stop(self) -> None:
        """Stop the audio output stream.

        Safe to call even if the stream is not running.
        """
        with self._lock:
            self._running = False
            stream = self._stream
            self._stream = None

        # Close outside the lock -- the stream's stop/close may block briefly
        # waiting for the audio callback to finish.
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass

    def destroy(self) -> None:
        """Release all audio resources.

        After calling ``destroy()`` the engine should not be reused.
        """
        self.stop()
        with self._lock:
            self._render_callback = None

    # ------------------------------------------------------------------
    # Audio callback (runs in the real-time audio thread)
    # ------------------------------------------------------------------

    def _audio_callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time_info: object,
        status: "sd.CallbackFlags",
    ) -> None:
        """Sounddevice output callback.

        This method is invoked from a high-priority audio thread managed by
        PortAudio.  It **must** be real-time safe:

        * No Python allocations that could trigger GC (best effort).
        * No blocking I/O.
        * Must never raise -- if anything goes wrong, output silence.

        Parameters
        ----------
        outdata : np.ndarray
            Output buffer to fill, shape ``(frames, channels)``, dtype
            ``float32``.
        frames : int
            Number of frames requested.
        time_info : object
            PortAudio time information (unused).
        status : sd.CallbackFlags
            Status flags (e.g. output underflow).
        """
        # ``status`` is truthy on underflow / overflow -- we simply ignore it
        # and continue to avoid cascading dropouts.

        try:
            cb = self._render_callback
            if cb is not None:
                audio = cb(frames)

                # Apply master volume.  We read self._volume without a lock
                # for speed; on CPython a float read is atomic.
                vol = self._volume
                if vol != 1.0:
                    audio = audio * vol

                # Clip to valid range.
                np.clip(audio, -1.0, 1.0, out=audio)

                # Write into every output channel (handles mono and stereo).
                out_f32 = audio.astype(np.float32, copy=False)
                for ch in range(outdata.shape[1]):
                    outdata[:, ch] = out_f32
            else:
                outdata.fill(0)
        except Exception:
            # Last resort -- never allow an exception to escape into
            # PortAudio.  Fill with silence.
            outdata.fill(0)

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------

    @staticmethod
    def list_devices() -> List[dict]:
        """Return a list of available audio devices.

        Each entry is a dict with at least ``name``, ``max_input_channels``,
        ``max_output_channels``, and ``default_samplerate``.

        Raises
        ------
        RuntimeError
            If ``sounddevice`` is not available.
        """
        if sd is None:
            raise RuntimeError("sounddevice is not available.")
        devices = sd.query_devices()
        # query_devices() returns a DeviceList (list-like of dicts).
        return [dict(d) for d in devices]  # type: ignore[arg-type]

    @staticmethod
    def list_output_devices() -> List[dict]:
        """Return only devices that support audio output."""
        return [d for d in AudioEngine.list_devices()
                if d.get("max_output_channels", 0) > 0]

    def set_device(self, device_id: Optional[int]) -> None:
        """Select the output device by numeric ID.

        If the stream is currently running it will be stopped, reconfigured,
        and restarted automatically.

        Parameters
        ----------
        device_id : int or None
            Device index as returned by :meth:`list_devices`, or ``None``
            to revert to the system default.
        """
        was_running = self._running
        if was_running:
            self.stop()

        self._device = device_id

        if was_running:
            self.start()

    @staticmethod
    def default_device() -> dict:
        """Return information about the current default output device.

        Raises
        ------
        RuntimeError
            If ``sounddevice`` is not available.
        """
        if sd is None:
            raise RuntimeError("sounddevice is not available.")
        idx = sd.default.device[1]  # output device index
        return dict(sd.query_devices(idx))

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        state = "running" if self._running else "stopped"
        return (
            f"<AudioEngine {state} sr={self._sample_rate} "
            f"bs={self._block_size} ch={self._channels} vol={self._volume:.2f}>"
        )

    def __del__(self) -> None:
        # Best-effort cleanup if the caller forgets to call destroy().
        try:
            self.destroy()
        except Exception:
            pass


# ======================================================================
# Self-test: 440 Hz sine tone
# ======================================================================

if __name__ == "__main__":
    import time

    if sd is None:
        print("ERROR: sounddevice is not installed or not functional.")
        print("Install with:  pip install sounddevice")
        sys.exit(1)

    DURATION = 2.0          # seconds
    FREQUENCY = 440.0       # Hz (A4)
    AMPLITUDE = 0.3         # keep it comfortable

    # Phase accumulator shared between callbacks.
    _phase = 0.0
    _sr = AudioEngine.DEFAULT_SAMPLE_RATE

    def _test_tone(num_samples: int) -> np.ndarray:
        """Render a pure sine tone, maintaining phase across calls."""
        global _phase
        t = np.arange(num_samples, dtype=np.float64) / _sr
        samples = AMPLITUDE * np.sin(2.0 * np.pi * FREQUENCY * t + _phase)
        _phase += 2.0 * np.pi * FREQUENCY * num_samples / _sr
        # Keep phase in [0, 2*pi) to avoid float precision loss over time.
        _phase %= 2.0 * np.pi
        return samples

    engine = AudioEngine()
    engine.set_render_callback(_test_tone)

    print(f"Default output device: {AudioEngine.default_device()['name']}")
    print(f"Playing {FREQUENCY} Hz sine tone for {DURATION} seconds ...")
    print(f"  Sample rate : {engine.sample_rate} Hz")
    print(f"  Block size  : {engine.block_size} frames")
    print(f"  Latency     : {engine.latency_ms:.1f} ms")
    print(f"  Volume      : {engine.volume:.0%}")

    engine.start()
    time.sleep(DURATION)
    engine.stop()
    engine.destroy()

    print("Done.")
