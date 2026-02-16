"""DX7 Envelope Generator.

The DX7 EG has 4 rates (R1-R4) and 4 levels (L1-L4), each in range 0-99.
The envelope traverses stages:

    Gate On:
        Stage 0: L4 -> L1 at Rate 1  (attack)
        Stage 1: L1 -> L2 at Rate 2  (decay 1)
        Stage 2: L2 -> L3 at Rate 3  (sustain / decay 2)
    Gate Off:
        Stage 3: current -> L4 at Rate 4  (release)

After Stage 3 completes, the envelope becomes idle.

Rate values 0-99 map to durations via the DX7's exponential rate table.
Level values 0-99 map to linear amplitude 0.0-1.0 via the DX7 level table.
"""

from __future__ import annotations

import numpy as np
from enum import IntEnum
from typing import Optional


class EnvelopeStage(IntEnum):
    """Envelope stage identifiers."""
    IDLE = -1
    ATTACK = 0   # L4 -> L1
    DECAY1 = 1   # L1 -> L2
    DECAY2 = 2   # L2 -> L3  (sustain)
    RELEASE = 3  # current -> L4


# ---------------------------------------------------------------------------
# DX7 rate-to-time conversion
# ---------------------------------------------------------------------------
# The DX7 maps rate 0-99 to an internal increment value that determines how
# fast the envelope ramps.  Higher rates = faster transitions.  The
# relationship is exponential.  We model this by converting rate to a
# time-constant (seconds) and then deriving per-sample increment.
#
# Based on reverse-engineering data from the DX7 firmware:
#   rate 0  => ~40 s  (very slow)
#   rate 99 => ~1 ms  (nearly instant)
#
# The mapping is:  time_seconds = 10^( (5.0 - rate * 0.07) ) * 0.001
# This produces an exponential curve that closely matches measured DX7 data.
# For the fastest rates we clamp to a minimum time.

_MIN_RATE_TIME = 0.0005  # 0.5 ms minimum transition time


def _rate_to_time(rate: int) -> float:
    """Convert a DX7 rate value (0-99) to time in seconds for a full-scale
    transition.  The result approximates the real DX7 behaviour."""
    rate = int(np.clip(rate, 0, 99))
    if rate == 99:
        return _MIN_RATE_TIME
    # Attempt to replicate the DX7's exponential mapping.
    # DX7 rates map roughly logarithmically: each increase of ~15 in rate
    # halves the time.  We use the formula:
    #   t = 10^(a - b * rate)
    # Calibrated so that rate 0 ~ 41 s, rate 50 ~ 0.38 s, rate 99 ~ 0.5 ms
    exponent = 4.6 - rate * 0.0693
    t = 10.0 ** (exponent) * 0.001
    return max(t, _MIN_RATE_TIME)


def _level_to_amplitude(level: int) -> float:
    """Convert a DX7 level value (0-99) to a linear amplitude 0.0-1.0.

    The DX7 level curve is roughly:
      - Level 0 = silence (0.0)
      - Level 99 = full (1.0)
    The mapping is exponential in the lower range, becoming more linear
    towards the top.  We use a power curve that approximates measured data.
    """
    level = int(np.clip(level, 0, 99))
    if level == 0:
        return 0.0
    if level == 99:
        return 1.0
    # Attempt a piece-wise approximation:
    # The DX7 uses a TL (total level) lookup table.  The curve is
    # approximately: amplitude = (level / 99)^2.0 for a good fit
    # but the real DX7 is closer to a shifted exponential.  We use:
    #   amplitude = 10^( (level - 99) * 0.05 )
    # Which gives dB-linear mapping:  each step ~ 0.5 dB
    db = (level - 99) * 0.4134  # ~41 dB range over 0-99
    return float(10.0 ** (db / 20.0))


# Pre-compute lookup tables for speed.
RATE_TIMES: np.ndarray = np.array([_rate_to_time(r) for r in range(100)],
                                   dtype=np.float64)
LEVEL_AMPS: np.ndarray = np.array([_level_to_amplitude(l)
                                    for l in range(100)], dtype=np.float64)


class Envelope:
    """DX7 4-rate / 4-level envelope generator.

    Parameters
    ----------
    rates : tuple of 4 ints
        Rate values R1-R4, each in 0-99.
    levels : tuple of 4 ints
        Level values L1-L4, each in 0-99.
    sample_rate : int
        Audio sample rate in Hz.
    """

    def __init__(
        self,
        rates: tuple[int, int, int, int] = (99, 99, 99, 99),
        levels: tuple[int, int, int, int] = (99, 99, 0, 0),
        sample_rate: int = 44100,
    ) -> None:
        self.rates = tuple(int(np.clip(r, 0, 99)) for r in rates)
        self.levels = tuple(int(np.clip(l, 0, 99)) for l in levels)
        self.sample_rate = sample_rate

        # Pre-convert levels to amplitudes.
        self._level_amps: tuple[float, ...] = tuple(
            LEVEL_AMPS[l] for l in self.levels
        )
        # L4 amplitude (the starting / release-target level).
        self._l4_amp: float = self._level_amps[3]

        # Runtime state.
        self._stage: EnvelopeStage = EnvelopeStage.IDLE
        self._current_value: float = 0.0
        self._target_value: float = 0.0
        self._increment: float = 0.0  # per-sample increment towards target
        self._samples_remaining: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def stage(self) -> EnvelopeStage:
        """Return the current envelope stage."""
        return self._stage

    @property
    def value(self) -> float:
        """Current envelope output (0.0-1.0)."""
        return self._current_value

    @property
    def is_idle(self) -> bool:
        return self._stage == EnvelopeStage.IDLE

    @property
    def is_active(self) -> bool:
        """True if the envelope is in any non-idle stage."""
        return self._stage != EnvelopeStage.IDLE

    def gate_on(self) -> None:
        """Trigger the envelope (note-on).

        The envelope starts from L4 amplitude and ramps toward L1 at Rate 1.
        """
        self._current_value = self._l4_amp
        self._enter_stage(EnvelopeStage.ATTACK)

    def gate_off(self) -> None:
        """Release the envelope (note-off).

        The envelope ramps from its current value toward L4 at Rate 4.
        """
        if self._stage == EnvelopeStage.IDLE:
            return
        self._enter_stage(EnvelopeStage.RELEASE)

    def render(self, num_samples: int) -> np.ndarray:
        """Generate *num_samples* of envelope output.

        Returns
        -------
        np.ndarray
            Float64 array of shape (num_samples,) with values in [0.0, 1.0].
        """
        out = np.empty(num_samples, dtype=np.float64)
        offset = 0

        while offset < num_samples:
            remaining = num_samples - offset

            if self._stage == EnvelopeStage.IDLE:
                # Fill the rest with the idle value.
                out[offset:] = self._current_value
                break

            if self._stage == EnvelopeStage.DECAY2:
                # Sustain stage: hold at L3 until gate off.
                # Still ramp toward L3 if we haven't reached it yet.
                if self._samples_remaining <= 0:
                    # Already at sustain level -- hold.
                    out[offset:] = self._current_value
                    break
                chunk = min(remaining, self._samples_remaining)
                self._fill_ramp(out, offset, chunk)
                offset += chunk
                if self._samples_remaining <= 0:
                    self._current_value = self._target_value
                    # Stay in DECAY2 (sustain hold) with no more ramping.
                continue

            # Normal stage processing: ATTACK, DECAY1, RELEASE
            if self._samples_remaining <= 0:
                # Stage complete -- advance.
                self._current_value = self._target_value
                self._advance_stage()
                continue

            chunk = min(remaining, self._samples_remaining)
            self._fill_ramp(out, offset, chunk)
            offset += chunk

            if self._samples_remaining <= 0:
                self._current_value = self._target_value
                self._advance_stage()

        return out

    def reset(self) -> None:
        """Reset the envelope to idle state at zero amplitude."""
        self._stage = EnvelopeStage.IDLE
        self._current_value = 0.0
        self._target_value = 0.0
        self._increment = 0.0
        self._samples_remaining = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fill_ramp(self, buf: np.ndarray, offset: int, count: int) -> None:
        """Write *count* samples of linear ramp into *buf* starting at *offset*."""
        end = offset + count
        indices = np.arange(1, count + 1, dtype=np.float64)
        buf[offset:end] = self._current_value + self._increment * indices
        # Clamp to [0, 1].
        np.clip(buf[offset:end], 0.0, 1.0, out=buf[offset:end])
        self._current_value = float(buf[end - 1])
        self._samples_remaining -= count

    def _enter_stage(self, stage: EnvelopeStage) -> None:
        """Configure the envelope for the given stage."""
        self._stage = stage

        if stage == EnvelopeStage.IDLE:
            self._increment = 0.0
            self._samples_remaining = 0
            return

        # Determine target and rate index.
        if stage == EnvelopeStage.ATTACK:
            target = self._level_amps[0]  # L1
            rate_idx = 0
        elif stage == EnvelopeStage.DECAY1:
            target = self._level_amps[1]  # L2
            rate_idx = 1
        elif stage == EnvelopeStage.DECAY2:
            target = self._level_amps[2]  # L3
            rate_idx = 2
        elif stage == EnvelopeStage.RELEASE:
            target = self._l4_amp  # L4
            rate_idx = 3
        else:
            self._stage = EnvelopeStage.IDLE
            return

        self._target_value = target
        rate = self.rates[rate_idx]

        # Compute ramp duration.
        delta = abs(target - self._current_value)
        if delta < 1e-9:
            # Already at target -- zero-length stage.
            self._current_value = target
            self._samples_remaining = 0
            self._increment = 0.0
            return

        # The rate-to-time table gives the time for a *full-scale* transition
        # (0.0 to 1.0).  We scale proportionally to the actual delta.
        full_time = RATE_TIMES[rate]
        stage_time = full_time * delta  # seconds for this delta
        stage_time = max(stage_time, 1.0 / self.sample_rate)  # at least 1 sample

        self._samples_remaining = max(1, int(round(stage_time * self.sample_rate)))
        self._increment = (target - self._current_value) / self._samples_remaining

    def _advance_stage(self) -> None:
        """Move to the next stage after the current one completes."""
        if self._stage == EnvelopeStage.ATTACK:
            self._enter_stage(EnvelopeStage.DECAY1)
        elif self._stage == EnvelopeStage.DECAY1:
            self._enter_stage(EnvelopeStage.DECAY2)
        elif self._stage == EnvelopeStage.DECAY2:
            # Sustain hold -- do nothing, stay in DECAY2.
            self._samples_remaining = 0
        elif self._stage == EnvelopeStage.RELEASE:
            self._current_value = self._target_value
            self._stage = EnvelopeStage.IDLE
