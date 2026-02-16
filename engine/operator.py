"""DX7 FM Operator.

Each of the DX7's 6 operators is a sine-wave oscillator whose output can be
used as a carrier (audible) or a modulator (frequency-modulates another
operator).

Key parameters per operator:
    - Oscillator mode: ratio (frequency = note_freq * ratio) or fixed Hz
    - Coarse ratio 0-31, fine ratio 0-99  =>  combined frequency ratio
    - Detune -7..+7 (fine pitch offset in cents-like steps)
    - Output level 0-99  =>  amplitude via DX7's exponential curve
    - Envelope: 4 rates + 4 levels (see envelope.py)
    - Keyboard level scaling: breakpoint, left/right depth & curve
    - Velocity sensitivity 0-7
    - Key rate scaling 0-7 (scales envelope rates with pitch)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .envelope import Envelope, LEVEL_AMPS


# ---------------------------------------------------------------------------
# DX7 output-level to modulation-index / amplitude mapping
# ---------------------------------------------------------------------------
# The DX7 operator output level (0-99) maps to a "total level" attenuation.
# Level 99 = maximum output, level 0 = silence.
# The relationship is exponential (dB-linear):
#   TL_dB = (99 - level) * 0.75   (approx 74 dB range)
#   amplitude = 10^(-TL_dB / 20)
#
# For *modulator* operators, the output level determines the modulation
# index.  The DX7's maximum modulation index at level 99 is approximately
# 13.0 (in radians).  At level 0 it is 0.

_MAX_MODULATION_INDEX: float = 13.0  # radians, approximate DX7 max

# Pre-compute a lookup table: output_level -> linear amplitude (0.0 .. 1.0)
_OUTPUT_LEVEL_AMP = np.zeros(100, dtype=np.float64)
for _lvl in range(100):
    if _lvl == 0:
        _OUTPUT_LEVEL_AMP[_lvl] = 0.0
    else:
        _db = (99 - _lvl) * 0.75
        _OUTPUT_LEVEL_AMP[_lvl] = 10.0 ** (-_db / 20.0)


def output_level_to_amplitude(level: int) -> float:
    """Convert DX7 output level (0-99) to linear amplitude 0.0-1.0."""
    return float(_OUTPUT_LEVEL_AMP[int(np.clip(level, 0, 99))])


def output_level_to_mod_index(level: int) -> float:
    """Convert DX7 output level (0-99) to modulation index in radians."""
    return output_level_to_amplitude(level) * _MAX_MODULATION_INDEX


# ---------------------------------------------------------------------------
# Coarse + Fine ratio computation
# ---------------------------------------------------------------------------

def compute_frequency_ratio(coarse: int, fine: int) -> float:
    """Compute the operator frequency ratio from coarse (0-31) and fine (0-99).

    DX7 behaviour:
      - coarse == 0 => base ratio 0.5 (sub-octave)
      - coarse  1-31 => base ratio = coarse
      - fine 0-99 adds a fractional amount:
          ratio = base * (1.0 + fine * 0.01)
    """
    coarse = int(np.clip(coarse, 0, 31))
    fine = int(np.clip(fine, 0, 99))
    base = 0.5 if coarse == 0 else float(coarse)
    return base * (1.0 + fine * 0.01)


# ---------------------------------------------------------------------------
# Detune
# ---------------------------------------------------------------------------

_DETUNE_CENTS_PER_STEP: float = 1.018  # approximate cents per DX7 detune step


def detune_multiplier(detune: int) -> float:
    """Return the frequency multiplier for a detune value in -7..+7.

    Each step is approximately 1 cent on the DX7.
    """
    detune = int(np.clip(detune, -7, 7))
    cents = detune * _DETUNE_CENTS_PER_STEP
    return 2.0 ** (cents / 1200.0)


# ---------------------------------------------------------------------------
# Velocity sensitivity
# ---------------------------------------------------------------------------

def velocity_scale(velocity: int, sensitivity: int) -> float:
    """Return an amplitude multiplier for the given MIDI velocity (0-127)
    and DX7 velocity sensitivity (0-7).

    sensitivity 0 => velocity has no effect (always 1.0)
    sensitivity 7 => full velocity range
    """
    sensitivity = int(np.clip(sensitivity, 0, 7))
    if sensitivity == 0:
        return 1.0
    velocity = int(np.clip(velocity, 0, 127))
    # Normalise velocity to 0..1.
    vel_norm = velocity / 127.0
    # Scale the range based on sensitivity.  At sens=7 the quietest note
    # (vel=0) drops to ~0.  At lower sensitivities the floor rises.
    floor = 1.0 - (sensitivity / 7.0)
    return floor + (1.0 - floor) * vel_norm


# ---------------------------------------------------------------------------
# Keyboard Level Scaling
# ---------------------------------------------------------------------------

@dataclass
class KeyboardLevelScaling:
    """DX7 keyboard level scaling parameters for one operator.

    The DX7 divides the keyboard at a breakpoint.  Notes below and above the
    breakpoint are attenuated according to separate depth/curve settings.

    Attributes
    ----------
    breakpoint : int
        MIDI note number for the scaling breakpoint (default 60 = middle C).
    left_depth : int
        Scaling depth (0-99) for notes below the breakpoint.
    right_depth : int
        Scaling depth (0-99) for notes above the breakpoint.
    left_curve : int
        Curve type for left side: 0 = -lin, 1 = -exp, 2 = +exp, 3 = +lin.
    right_curve : int
        Curve type for right side: 0 = -lin, 1 = -exp, 2 = +exp, 3 = +lin.
    """
    breakpoint: int = 60
    left_depth: int = 0
    right_depth: int = 0
    left_curve: int = 0
    right_curve: int = 0

    def scale_factor(self, note: int) -> float:
        """Return an amplitude multiplier (dB offset converted to linear) for
        the given MIDI note number, applying keyboard level scaling."""
        distance = note - self.breakpoint
        if distance < 0:
            # Left of breakpoint.
            depth = self.left_depth
            curve = self.left_curve
            dist_abs = -distance
        elif distance > 0:
            depth = self.right_depth
            curve = self.right_curve
            dist_abs = distance
        else:
            return 1.0

        if depth == 0:
            return 1.0

        # Normalise distance: the DX7 keyboard spans ~5 octaves (61 keys
        # from the breakpoint to each end).
        norm = min(dist_abs / 48.0, 1.0)  # clamp at ~4 octaves

        # Curve types:
        #   0 = -linear  (attenuation increases linearly)
        #   1 = -exponential (attenuation increases exponentially)
        #   2 = +exponential (boost -- increases exponentially)
        #   3 = +linear (boost -- increases linearly)
        max_db = depth * 0.75  # DX7 depth maps roughly to 0-74 dB range

        if curve in (0, 1):
            # Negative curves: attenuate with distance.
            if curve == 0:
                db_offset = -max_db * norm
            else:
                db_offset = -max_db * (norm ** 2)
        elif curve in (2, 3):
            # Positive curves: boost with distance.
            if curve == 3:
                db_offset = max_db * norm
            else:
                db_offset = max_db * (norm ** 2)
        else:
            db_offset = 0.0

        return float(10.0 ** (db_offset / 20.0))


# ---------------------------------------------------------------------------
# Key Rate Scaling
# ---------------------------------------------------------------------------

def key_rate_scaling(rate: int, note: int, krs: int) -> int:
    """Apply key rate scaling to an envelope rate value.

    Higher notes get faster envelopes.  *krs* is 0-7.
    Returns adjusted rate clamped to 0-99.
    """
    krs = int(np.clip(krs, 0, 7))
    if krs == 0:
        return int(np.clip(rate, 0, 99))
    # The DX7 scales rates by roughly: adjustment = krs * (note - 36) / 36
    # for notes above C2.
    adjustment = krs * max(0, note - 36) / 36.0
    return int(np.clip(round(rate + adjustment), 0, 99))


# ---------------------------------------------------------------------------
# Operator data container
# ---------------------------------------------------------------------------

@dataclass
class OperatorParams:
    """All parameters for a single DX7 operator."""
    # Oscillator
    osc_mode: int = 0            # 0 = ratio, 1 = fixed frequency
    coarse: int = 1              # 0-31
    fine: int = 0                # 0-99
    detune: int = 0              # -7..+7

    # Output
    output_level: int = 99       # 0-99

    # Envelope
    rate1: int = 99
    rate2: int = 99
    rate3: int = 99
    rate4: int = 99
    level1: int = 99
    level2: int = 99
    level3: int = 99
    level4: int = 0

    # Sensitivity
    velocity_sensitivity: int = 0  # 0-7
    key_rate_scaling: int = 0      # 0-7

    # Keyboard level scaling
    kls: KeyboardLevelScaling = field(default_factory=KeyboardLevelScaling)


# ---------------------------------------------------------------------------
# Operator runtime
# ---------------------------------------------------------------------------

class Operator:
    """A single DX7 FM operator with oscillator, envelope, and level scaling.

    Parameters
    ----------
    params : OperatorParams, optional
        Operator parameters.  Defaults to a simple full-level sine.
    sample_rate : int
        Audio sample rate.
    """

    def __init__(
        self,
        params: Optional[OperatorParams] = None,
        sample_rate: int = 44100,
    ) -> None:
        self.params = params or OperatorParams()
        self.sample_rate = sample_rate

        # Build envelope from params.
        self.envelope = Envelope(
            rates=(self.params.rate1, self.params.rate2,
                   self.params.rate3, self.params.rate4),
            levels=(self.params.level1, self.params.level2,
                    self.params.level3, self.params.level4),
            sample_rate=sample_rate,
        )

        # Phase accumulator (in radians).
        self._phase: float = 0.0

        # Cached runtime values (set on gate_on).
        self._freq: float = 440.0          # computed operator frequency in Hz
        self._amplitude: float = 1.0       # output level * velocity * KLS
        self._mod_index: float = _MAX_MODULATION_INDEX  # for modulator use
        self._vel_scale: float = 1.0
        self._kls_scale: float = 1.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def gate_on(self, note: int, velocity: int, base_freq: float) -> None:
        """Trigger the operator for a new note.

        Parameters
        ----------
        note : int
            MIDI note number (0-127).
        velocity : int
            MIDI velocity (0-127).
        base_freq : float
            Base frequency of the note in Hz (already converted from MIDI note).
        """
        p = self.params

        # Compute operator frequency.
        if p.osc_mode == 0:
            # Ratio mode.
            ratio = compute_frequency_ratio(p.coarse, p.fine)
            self._freq = base_freq * ratio * detune_multiplier(p.detune)
        else:
            # Fixed frequency mode.
            # In fixed mode, coarse selects a power of 10 and fine adds linear Hz.
            # coarse: 0=1Hz, 1=10Hz, 2=100Hz, 3=1000Hz
            fixed_base = 10.0 ** min(p.coarse, 3)
            self._freq = fixed_base * (1.0 + p.fine * 0.01) * detune_multiplier(p.detune)

        # Velocity and keyboard level scaling.
        self._vel_scale = velocity_scale(velocity, p.velocity_sensitivity)
        self._kls_scale = p.kls.scale_factor(note)

        # Compute final amplitude and mod index.
        base_amp = output_level_to_amplitude(p.output_level)
        self._amplitude = base_amp * self._vel_scale * self._kls_scale
        self._mod_index = output_level_to_mod_index(p.output_level) * self._vel_scale * self._kls_scale

        # Reset phase.
        self._phase = 0.0

        # Apply key rate scaling to envelope rates and trigger.
        adjusted_rates = tuple(
            key_rate_scaling(r, note, p.key_rate_scaling)
            for r in (p.rate1, p.rate2, p.rate3, p.rate4)
        )
        self.envelope.rates = adjusted_rates
        # Rebuild internal timing (levels stay the same).
        self.envelope.gate_on()

    def gate_off(self) -> None:
        """Release the operator (note-off)."""
        self.envelope.gate_off()

    @property
    def is_active(self) -> bool:
        """True if the operator envelope has not reached idle."""
        return self.envelope.is_active

    def render(
        self,
        num_samples: int,
        modulation: Optional[np.ndarray] = None,
        as_carrier: bool = True,
        freq_ratio: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Render audio/modulation output for this operator.

        Parameters
        ----------
        num_samples : int
            Number of samples to generate.
        modulation : np.ndarray or None
            Phase-modulation input from other operators (in radians).
            Shape (num_samples,).
        as_carrier : bool
            If True, the output is scaled as a carrier (amplitude 0-1).
            If False, the output is scaled as a modulator (modulation index).
        freq_ratio : np.ndarray or None
            Per-sample frequency multiplier for pitch bend / LFO pitch mod.
            Shape (num_samples,).  None means no pitch modification.

        Returns
        -------
        np.ndarray
            Float64 array of shape (num_samples,).
        """
        # Generate envelope.
        env = self.envelope.render(num_samples)

        # Base phase increment per sample.
        base_phase_inc = 2.0 * math.pi * self._freq / self.sample_rate

        if freq_ratio is not None:
            # Per-sample varying frequency (pitch bend + LFO mod).
            phase_incs = base_phase_inc * freq_ratio
            cum_phase = np.cumsum(phase_incs)
            phase = self._phase + cum_phase
            final_phase = float(phase[-1]) if num_samples > 0 else self._phase
        else:
            # Constant frequency.
            t = np.arange(num_samples, dtype=np.float64)
            phase = self._phase + base_phase_inc * t
            final_phase = self._phase + base_phase_inc * num_samples

        # Apply phase modulation.
        if modulation is not None:
            phase = phase + modulation

        # Generate sine.
        output = np.sin(phase)

        # Scale by envelope and amplitude.
        if as_carrier:
            output *= env * self._amplitude
        else:
            output *= env * self._mod_index

        # Advance phase accumulator (keep within 0..2pi to avoid float issues).
        self._phase = final_phase % (2.0 * math.pi)

        return output

    def render_with_feedback(
        self,
        num_samples: int,
        feedback_level: float,
        feedback_buffer: np.ndarray,
        freq_ratio: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Render with self-feedback (the operator modulates itself).

        Parameters
        ----------
        num_samples : int
            Number of samples to generate.
        feedback_level : float
            Feedback amount (0.0 - 1.0, derived from DX7 feedback param 0-7).
        feedback_buffer : np.ndarray
            Array of length 2 holding the last two output samples from this
            operator (used to compute the feedback signal).  Updated in-place.
        freq_ratio : np.ndarray or None
            Per-sample frequency multiplier for pitch bend / LFO pitch mod.

        Returns
        -------
        np.ndarray
            Float64 output array of shape (num_samples,).
        """
        env = self.envelope.render(num_samples)

        base_phase_inc = 2.0 * math.pi * self._freq / self.sample_rate

        output = np.empty(num_samples, dtype=np.float64)

        # Feedback must be computed sample-by-sample because each sample's
        # output feeds back into the next.
        phase = self._phase
        fb0 = feedback_buffer[0]
        fb1 = feedback_buffer[1]

        for i in range(num_samples):
            # Feedback is the average of the last two outputs scaled by the
            # feedback amount.  This matches the DX7 hardware implementation.
            fb = feedback_level * (fb0 + fb1) * 0.5
            sample = math.sin(phase + fb)
            output[i] = sample
            fb0 = fb1
            fb1 = sample
            fr = freq_ratio[i] if freq_ratio is not None else 1.0
            phase += base_phase_inc * fr

        # Store feedback state.
        feedback_buffer[0] = fb0
        feedback_buffer[1] = fb1

        # Wrap phase.
        self._phase = phase % (2.0 * math.pi)

        # Apply envelope and scaling.  For feedback operators we scale as
        # modulator by default (the caller decides how to use the output).
        output *= env * self._mod_index

        return output

    def reset(self) -> None:
        """Reset the operator to initial state."""
        self._phase = 0.0
        self.envelope.reset()
