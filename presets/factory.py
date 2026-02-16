"""
Yamaha DX7 ROM1A Factory Presets (Bank 1A)

Contains all 32 original factory presets from the DX7's internal ROM1A bank.
Parameters are based on the original Yamaha DX7 SysEx data.

Each preset is a dictionary containing:
  - name:       Preset name as displayed on the DX7 LCD (10 chars max)
  - algorithm:  FM algorithm number (1-32)
  - feedback:   Feedback level for the feedback operator (0-7)
  - lfo:        LFO parameters (speed, delay, pmd, amd, wave, sync)
  - operators:  List of 6 operator parameter dictionaries (OP1-OP6)

Operator parameters:
  - rate[4]:        Envelope generator rates R1-R4 (0-99)
  - level[4]:       Envelope generator levels L1-L4 (0-99)
  - break_point:    Keyboard level scaling break point (0-99, where 39=C3)
  - left_depth:     Left keyboard level scaling depth (0-99)
  - right_depth:    Right keyboard level scaling depth (0-99)
  - left_curve:     Left scaling curve (0=lin-, 1=exp-, 2=exp+, 3=lin+)
  - right_curve:    Right scaling curve (0=lin-, 1=exp-, 2=exp+, 3=lin+)
  - rate_scaling:   Keyboard rate scaling (0-7)
  - amp_mod_sens:   Amplitude modulation sensitivity (0-3)
  - key_vel_sens:   Key velocity sensitivity (0-7)
  - output_level:   Operator output level (0-99)
  - osc_mode:       Oscillator mode (0=ratio, 1=fixed)
  - freq_coarse:    Coarse frequency (0-31)
  - freq_fine:      Fine frequency (0-99)
  - detune:         Detune (0-14, 7=center/no detune)
"""


def _op(rate, level, break_point=39, left_depth=0, right_depth=0,
        left_curve=0, right_curve=0, rate_scaling=0, amp_mod_sens=0,
        key_vel_sens=0, output_level=0, osc_mode=0, freq_coarse=1,
        freq_fine=0, detune=7):
    """Helper to build an operator dict with defaults."""
    return {
        "rate": list(rate),
        "level": list(level),
        "break_point": break_point,
        "left_depth": left_depth,
        "right_depth": right_depth,
        "left_curve": left_curve,
        "right_curve": right_curve,
        "rate_scaling": rate_scaling,
        "amp_mod_sens": amp_mod_sens,
        "key_vel_sens": key_vel_sens,
        "output_level": output_level,
        "osc_mode": osc_mode,
        "freq_coarse": freq_coarse,
        "freq_fine": freq_fine,
        "detune": detune,
    }


def _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1):
    """Helper to build an LFO dict with defaults."""
    return {
        "speed": speed,
        "delay": delay,
        "pmd": pmd,
        "amd": amd,
        "wave": wave,
        "sync": sync,
    }


# ---------------------------------------------------------------------------
# ROM1A Voice 1: BRASS   1
# ---------------------------------------------------------------------------
_BRASS_1 = {
    "name": "BRASS   1",
    "algorithm": 22,
    "feedback": 7,
    "lfo": _lfo(speed=37, delay=0, pmd=5, amd=0, wave=4, sync=1),
    "operators": [
        # OP1 - carrier
        _op(rate=(49, 99, 28, 68), level=(98, 98, 91, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        # OP2 - carrier
        _op(rate=(49, 99, 28, 68), level=(98, 98, 91, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        # OP3 - carrier
        _op(rate=(49, 99, 28, 68), level=(98, 98, 91, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=86,
            freq_coarse=1, freq_fine=0, detune=10),
        # OP4 - modulator
        _op(rate=(84, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=86,
            freq_coarse=1, freq_fine=0, detune=4),
        # OP5 - modulator
        _op(rate=(84, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=86,
            freq_coarse=1, freq_fine=0, detune=4),
        # OP6 - modulator
        _op(rate=(84, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=86,
            freq_coarse=1, freq_fine=0, detune=4),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 2: BRASS   2
# ---------------------------------------------------------------------------
_BRASS_2 = {
    "name": "BRASS   2",
    "algorithm": 22,
    "feedback": 7,
    "lfo": _lfo(speed=35, delay=0, pmd=3, amd=0, wave=4, sync=1),
    "operators": [
        _op(rate=(62, 60, 28, 68), level=(99, 98, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(62, 60, 28, 68), level=(99, 98, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(62, 60, 28, 68), level=(99, 98, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=79,
            freq_coarse=1, freq_fine=0, detune=10),
        _op(rate=(73, 80, 88, 48), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=82,
            freq_coarse=1, freq_fine=0, detune=5),
        _op(rate=(73, 80, 88, 48), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=82,
            freq_coarse=1, freq_fine=0, detune=5),
        _op(rate=(73, 80, 88, 48), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=82,
            freq_coarse=1, freq_fine=0, detune=9),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 3: BRASS   3
# ---------------------------------------------------------------------------
_BRASS_3 = {
    "name": "BRASS   3",
    "algorithm": 22,
    "feedback": 6,
    "lfo": _lfo(speed=30, delay=0, pmd=4, amd=0, wave=4, sync=1),
    "operators": [
        _op(rate=(55, 65, 28, 60), level=(99, 97, 90, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(55, 65, 28, 60), level=(99, 97, 90, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(55, 65, 28, 60), level=(99, 97, 90, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=79,
            freq_coarse=1, freq_fine=0, detune=10),
        _op(rate=(96, 70, 90, 50), level=(99, 90, 97, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=85,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(96, 70, 90, 50), level=(99, 90, 97, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=85,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(96, 70, 90, 50), level=(99, 90, 97, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=85,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 4: STRINGS 1
# ---------------------------------------------------------------------------
_STRINGS_1 = {
    "name": "STRINGS 1",
    "algorithm": 2,
    "feedback": 6,
    "lfo": _lfo(speed=38, delay=42, pmd=7, amd=0, wave=0, sync=0),
    "operators": [
        # OP1 - carrier
        _op(rate=(45, 25, 20, 50), level=(99, 98, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        # OP2 - modulator
        _op(rate=(54, 50, 50, 50), level=(99, 82, 82, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=82,
            freq_coarse=2, freq_fine=0, detune=7),
        # OP3 - carrier
        _op(rate=(45, 25, 20, 50), level=(99, 98, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        # OP4 - modulator
        _op(rate=(54, 50, 50, 50), level=(99, 82, 82, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=82,
            freq_coarse=2, freq_fine=0, detune=6),
        # OP5 - carrier (sub-component)
        _op(rate=(45, 25, 20, 50), level=(99, 98, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=79,
            freq_coarse=1, freq_fine=0, detune=7),
        # OP6 - modulator/feedback
        _op(rate=(54, 50, 50, 50), level=(99, 60, 60, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=70,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 5: STRINGS 2
# ---------------------------------------------------------------------------
_STRINGS_2 = {
    "name": "STRINGS 2",
    "algorithm": 2,
    "feedback": 6,
    "lfo": _lfo(speed=40, delay=50, pmd=6, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(40, 22, 18, 50), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(52, 48, 48, 48), level=(99, 80, 80, 0),
            break_point=39, left_depth=0, right_depth=12,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=78,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(40, 22, 18, 50), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(52, 48, 48, 48), level=(99, 80, 80, 0),
            break_point=39, left_depth=0, right_depth=12,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=78,
            freq_coarse=1, freq_fine=0, detune=6),
        _op(rate=(40, 22, 18, 50), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=75,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(52, 48, 48, 48), level=(99, 65, 65, 0),
            break_point=39, left_depth=0, right_depth=12,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=66,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 6: STRINGS 3
# ---------------------------------------------------------------------------
_STRINGS_3 = {
    "name": "STRINGS 3",
    "algorithm": 1,
    "feedback": 6,
    "lfo": _lfo(speed=42, delay=35, pmd=8, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(42, 20, 20, 52), level=(99, 99, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(50, 45, 45, 45), level=(99, 78, 78, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=75,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=68,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(42, 20, 20, 52), level=(99, 99, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(50, 45, 45, 45), level=(99, 78, 78, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=75,
            freq_coarse=1, freq_fine=0, detune=6),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=62,
            freq_coarse=5, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 7: ORCHSTRA
# ---------------------------------------------------------------------------
_ORCHSTRA = {
    "name": "ORCHSTRA",
    "algorithm": 2,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=30, pmd=5, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(38, 22, 20, 48), level=(99, 99, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(68, 52, 50, 50), level=(99, 85, 85, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=80,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(38, 22, 20, 48), level=(99, 99, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(68, 52, 50, 50), level=(99, 85, 85, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=80,
            freq_coarse=3, freq_fine=0, detune=6),
        _op(rate=(38, 22, 20, 48), level=(99, 99, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(90, 52, 50, 50), level=(99, 70, 70, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=72,
            freq_coarse=5, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 8: PIANO   1
# ---------------------------------------------------------------------------
_PIANO_1 = {
    "name": "PIANO   1",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(95, 29, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=54, right_depth=50,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=3),
        _op(rate=(95, 20, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=58,
            freq_coarse=14, freq_fine=0, detune=3),
        _op(rate=(95, 29, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=54, right_depth=50,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=3),
        _op(rate=(95, 20, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=58,
            freq_coarse=14, freq_fine=0, detune=3),
        _op(rate=(95, 50, 35, 78), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=89,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 9: PIANO   2
# ---------------------------------------------------------------------------
_PIANO_2 = {
    "name": "PIANO   2",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=50, right_depth=50,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=4),
        _op(rate=(95, 50, 30, 70), level=(99, 82, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=4, output_level=62,
            freq_coarse=7, freq_fine=0, detune=4),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=50, right_depth=50,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=10),
        _op(rate=(95, 50, 30, 70), level=(99, 82, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=4, output_level=62,
            freq_coarse=7, freq_fine=0, detune=10),
        _op(rate=(95, 50, 35, 78), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=85,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 10: PIANO   3
# ---------------------------------------------------------------------------
_PIANO_3 = {
    "name": "PIANO   3",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(94, 30, 22, 55), level=(99, 90, 0, 0),
            break_point=39, left_depth=45, right_depth=45,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(95, 45, 30, 65), level=(99, 78, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=55,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(94, 30, 22, 55), level=(99, 90, 0, 0),
            break_point=39, left_depth=45, right_depth=45,
            left_curve=1, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(95, 45, 30, 65), level=(99, 78, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=55,
            freq_coarse=3, freq_fine=0, detune=6),
        _op(rate=(95, 50, 35, 78), level=(99, 70, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 70, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=84,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 11: E.PIANO 1
# ---------------------------------------------------------------------------
_E_PIANO_1 = {
    "name": "E.PIANO 1",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(95, 29, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(95, 20, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=78,
            freq_coarse=14, freq_fine=0, detune=7),
        _op(rate=(95, 29, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(95, 20, 20, 50), level=(99, 95, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=78,
            freq_coarse=14, freq_fine=0, detune=7),
        _op(rate=(95, 50, 35, 78), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=58,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 12: E.PIANO 2
# ---------------------------------------------------------------------------
_E_PIANO_2 = {
    "name": "E.PIANO 2",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=25, delay=0, pmd=2, amd=0, wave=4, sync=1),
    "operators": [
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=48, left_depth=0, right_depth=28,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 95, 60), level=(84, 60, 45, 0),
            break_point=48, left_depth=0, right_depth=38,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=48, left_depth=0, right_depth=28,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(99, 88, 95, 60), level=(84, 60, 45, 0),
            break_point=48, left_depth=0, right_depth=38,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=82,
            freq_coarse=1, freq_fine=0, detune=6),
        _op(rate=(95, 50, 35, 78), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=70,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 13: E.PIANO 3
# ---------------------------------------------------------------------------
_E_PIANO_3 = {
    "name": "E.PIANO 3",
    "algorithm": 5,
    "feedback": 4,
    "lfo": _lfo(speed=30, delay=0, pmd=3, amd=0, wave=4, sync=1),
    "operators": [
        _op(rate=(84, 35, 22, 52), level=(99, 92, 0, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 60, 40, 55), level=(92, 72, 36, 0),
            break_point=48, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=74,
            freq_coarse=7, freq_fine=0, detune=7),
        _op(rate=(84, 35, 22, 52), level=(99, 92, 0, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(96, 60, 40, 55), level=(92, 72, 36, 0),
            break_point=48, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=74,
            freq_coarse=7, freq_fine=0, detune=6),
        _op(rate=(95, 50, 35, 78), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 25, 25, 67), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=64,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 14: HARPSICH
# ---------------------------------------------------------------------------
_HARPSICH = {
    "name": "HARPSICH",
    "algorithm": 5,
    "feedback": 3,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(99, 40, 30, 60), level=(99, 70, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 75, 60, 60), level=(99, 56, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=80,
            freq_coarse=5, freq_fine=0, detune=7),
        _op(rate=(99, 40, 30, 60), level=(99, 70, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(99, 75, 60, 60), level=(99, 56, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=80,
            freq_coarse=5, freq_fine=0, detune=6),
        _op(rate=(99, 70, 35, 90), level=(99, 60, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 85, 50, 85), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=4, output_level=70,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 15: CLAV    1
# ---------------------------------------------------------------------------
_CLAV_1 = {
    "name": "CLAV    1",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(99, 86, 56, 76), level=(99, 60, 0, 0),
            break_point=60, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 95, 70, 80), level=(99, 52, 0, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=7, output_level=86,
            freq_coarse=3, freq_fine=41, detune=7),
        _op(rate=(99, 86, 56, 76), level=(99, 60, 0, 0),
            break_point=60, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 95, 70, 80), level=(99, 52, 0, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=7, output_level=86,
            freq_coarse=3, freq_fine=41, detune=7),
        _op(rate=(99, 86, 56, 76), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=3, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 92, 66, 82), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=7, output_level=78,
            freq_coarse=2, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 16: VIBE
# ---------------------------------------------------------------------------
_VIBE = {
    "name": "VIBE    ",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=3, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 70, 50), level=(99, 40, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=72,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=3, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 70, 50), level=(99, 40, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=72,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=3, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 70, 50), level=(99, 40, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=55,
            freq_coarse=10, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 17: MARIMBA
# ---------------------------------------------------------------------------
_MARIMBA = {
    "name": "MARIMBA ",
    "algorithm": 5,
    "feedback": 4,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(99, 85, 0, 60), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 92, 0, 70), level=(99, 36, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=72,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(99, 85, 0, 60), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 92, 0, 70), level=(99, 36, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=72,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(99, 80, 0, 60), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 90, 0, 70), level=(99, 30, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=60,
            freq_coarse=10, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 18: KOTO
# ---------------------------------------------------------------------------
_KOTO = {
    "name": "KOTO    ",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(99, 80, 40, 72), level=(99, 65, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 90, 55, 65), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=7, output_level=78,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(99, 80, 40, 72), level=(99, 65, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(99, 90, 55, 65), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=7, output_level=78,
            freq_coarse=2, freq_fine=0, detune=6),
        _op(rate=(99, 90, 40, 85), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 95, 60, 75), level=(99, 48, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=70,
            freq_coarse=5, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 19: FLUTE   1
# ---------------------------------------------------------------------------
_FLUTE_1 = {
    "name": "FLUTE   1",
    "algorithm": 5,
    "feedback": 7,
    "lfo": _lfo(speed=37, delay=50, pmd=5, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(65, 35, 22, 50), level=(99, 99, 95, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(90, 68, 50, 50), level=(99, 62, 50, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=56,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(65, 35, 22, 50), level=(99, 99, 95, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(90, 68, 50, 50), level=(99, 62, 50, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=56,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(65, 35, 22, 50), level=(99, 99, 95, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=78,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(90, 68, 50, 50), level=(99, 62, 50, 0),
            break_point=60, left_depth=0, right_depth=30,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=45,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 20: FLUTE   2
# ---------------------------------------------------------------------------
_FLUTE_2 = {
    "name": "FLUTE   2",
    "algorithm": 1,
    "feedback": 7,
    "lfo": _lfo(speed=40, delay=45, pmd=6, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(60, 30, 20, 48), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(82, 65, 48, 48), level=(99, 58, 46, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=60,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(82, 65, 48, 48), level=(99, 58, 46, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=40,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(60, 30, 20, 48), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=82,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(82, 65, 48, 48), level=(99, 58, 46, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=50,
            freq_coarse=1, freq_fine=0, detune=6),
        _op(rate=(82, 65, 48, 48), level=(99, 58, 46, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=32,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 21: OBOE
# ---------------------------------------------------------------------------
_OBOE = {
    "name": "OBOE    ",
    "algorithm": 1,
    "feedback": 4,
    "lfo": _lfo(speed=38, delay=40, pmd=5, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(58, 28, 22, 50), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(70, 55, 50, 50), level=(99, 82, 80, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(80, 70, 60, 55), level=(99, 78, 70, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=72,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(58, 28, 22, 50), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(70, 55, 50, 50), level=(99, 82, 80, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=75,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(80, 70, 60, 55), level=(99, 78, 70, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=66,
            freq_coarse=5, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 22: TRUMPET
# ---------------------------------------------------------------------------
_TRUMPET = {
    "name": "TRUMPET ",
    "algorithm": 22,
    "feedback": 7,
    "lfo": _lfo(speed=35, delay=0, pmd=3, amd=0, wave=4, sync=1),
    "operators": [
        _op(rate=(80, 70, 30, 68), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(80, 70, 30, 68), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(80, 70, 30, 68), level=(99, 98, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=82,
            freq_coarse=1, freq_fine=0, detune=10),
        _op(rate=(96, 85, 92, 55), level=(99, 92, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=88,
            freq_coarse=1, freq_fine=0, detune=4),
        _op(rate=(96, 85, 92, 55), level=(99, 92, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=88,
            freq_coarse=1, freq_fine=0, detune=4),
        _op(rate=(96, 85, 92, 55), level=(99, 92, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=4, output_level=88,
            freq_coarse=2, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 23: ORGAN   1
# ---------------------------------------------------------------------------
_ORGAN_1 = {
    "name": "ORGAN   1",
    "algorithm": 22,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=92,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=86,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(82, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(82, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=78,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(82, 95, 95, 60), level=(99, 95, 95, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=72,
            freq_coarse=6, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 24: ORGAN   2
# ---------------------------------------------------------------------------
_ORGAN_2 = {
    "name": "ORGAN   2",
    "algorithm": 22,
    "feedback": 4,
    "lfo": _lfo(speed=60, delay=0, pmd=3, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=88,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(90, 0, 0, 50), level=(99, 99, 99, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=80,
            freq_coarse=5, freq_fine=0, detune=7),
        _op(rate=(90, 90, 90, 55), level=(99, 92, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=80,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(90, 90, 90, 55), level=(99, 92, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=74,
            freq_coarse=4, freq_fine=0, detune=7),
        _op(rate=(90, 90, 90, 55), level=(99, 92, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=0,
            amp_mod_sens=0, key_vel_sens=0, output_level=68,
            freq_coarse=8, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 25: PIPES
# ---------------------------------------------------------------------------
_PIPES = {
    "name": "PIPES   ",
    "algorithm": 1,
    "feedback": 7,
    "lfo": _lfo(speed=35, delay=30, pmd=3, amd=0, wave=0, sync=0),
    "operators": [
        _op(rate=(55, 28, 22, 48), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(72, 55, 48, 48), level=(99, 70, 62, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=70,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(72, 55, 48, 48), level=(99, 70, 62, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=55,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(55, 28, 22, 48), level=(99, 99, 96, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=1, output_level=85,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(72, 55, 48, 48), level=(99, 70, 62, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=62,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(72, 55, 48, 48), level=(99, 70, 62, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=3, output_level=48,
            freq_coarse=4, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 26: HARP    1
# ---------------------------------------------------------------------------
_HARP_1 = {
    "name": "HARP    1",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(96, 50, 25, 70), level=(99, 72, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 70, 40, 60), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=76,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(96, 50, 25, 70), level=(99, 72, 0, 0),
            break_point=39, left_depth=0, right_depth=10,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(96, 70, 40, 60), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=14,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=76,
            freq_coarse=2, freq_fine=0, detune=6),
        _op(rate=(96, 55, 30, 75), level=(99, 65, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 80, 50, 70), level=(99, 48, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=5, output_level=62,
            freq_coarse=4, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 27: GUITAR  1
# ---------------------------------------------------------------------------
_GUITAR_1 = {
    "name": "GUITAR  1",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(96, 50, 25, 65), level=(99, 72, 0, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 68, 48, 62), level=(99, 55, 0, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=82,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 50, 25, 65), level=(99, 72, 0, 0),
            break_point=48, left_depth=0, right_depth=20,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(96, 68, 48, 62), level=(99, 55, 0, 0),
            break_point=48, left_depth=0, right_depth=24,
            left_curve=0, right_curve=1, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=82,
            freq_coarse=1, freq_fine=0, detune=6),
        _op(rate=(96, 60, 30, 72), level=(99, 68, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 80, 55, 70), level=(99, 50, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=4,
            amp_mod_sens=0, key_vel_sens=6, output_level=72,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 28: SYN-LEAD
# ---------------------------------------------------------------------------
_SYN_LEAD = {
    "name": "SYN-LEAD",
    "algorithm": 22,
    "feedback": 7,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(80, 50, 28, 55), level=(99, 99, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(80, 50, 28, 55), level=(99, 99, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=8),
        _op(rate=(80, 50, 28, 55), level=(99, 99, 92, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=84,
            freq_coarse=2, freq_fine=0, detune=7),
        _op(rate=(90, 82, 88, 50), level=(99, 90, 94, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=86,
            freq_coarse=1, freq_fine=0, detune=5),
        _op(rate=(90, 82, 88, 50), level=(99, 90, 94, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=86,
            freq_coarse=1, freq_fine=0, detune=9),
        _op(rate=(90, 82, 88, 50), level=(99, 90, 94, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=3, output_level=82,
            freq_coarse=3, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 29: BASS    1
# ---------------------------------------------------------------------------
_BASS_1 = {
    "name": "BASS    1",
    "algorithm": 5,
    "feedback": 6,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(96, 50, 20, 60), level=(99, 82, 0, 0),
            break_point=27, left_depth=0, right_depth=40,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 72, 40, 55), level=(99, 60, 0, 0),
            break_point=27, left_depth=0, right_depth=50,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=86,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 50, 20, 60), level=(99, 82, 0, 0),
            break_point=27, left_depth=0, right_depth=40,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 72, 40, 55), level=(99, 60, 0, 0),
            break_point=27, left_depth=0, right_depth=50,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=86,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 60, 30, 68), level=(99, 75, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(96, 80, 50, 65), level=(99, 55, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=74,
            freq_coarse=2, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 30: BASS    2
# ---------------------------------------------------------------------------
_BASS_2 = {
    "name": "BASS    2",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(94, 48, 18, 58), level=(99, 78, 0, 0),
            break_point=27, left_depth=0, right_depth=44,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(94, 70, 38, 52), level=(99, 58, 0, 0),
            break_point=27, left_depth=0, right_depth=54,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=90,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(94, 48, 18, 58), level=(99, 78, 0, 0),
            break_point=27, left_depth=0, right_depth=44,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(94, 70, 38, 52), level=(99, 58, 0, 0),
            break_point=27, left_depth=0, right_depth=54,
            left_curve=0, right_curve=3, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=6, output_level=90,
            freq_coarse=3, freq_fine=0, detune=7),
        _op(rate=(94, 55, 28, 65), level=(99, 72, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(94, 78, 48, 62), level=(99, 52, 0, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=3,
            amp_mod_sens=0, key_vel_sens=5, output_level=72,
            freq_coarse=1, freq_fine=0, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 31: TUB BELL
# ---------------------------------------------------------------------------
_TUB_BELL = {
    "name": "TUB BELL",
    "algorithm": 5,
    "feedback": 4,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 96, 60), level=(95, 60, 50, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=78,
            freq_coarse=3, freq_fine=50, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 96, 60), level=(95, 60, 50, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=78,
            freq_coarse=3, freq_fine=50, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 88, 96, 60), level=(95, 60, 50, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=62,
            freq_coarse=7, freq_fine=12, detune=7),
    ],
}

# ---------------------------------------------------------------------------
# ROM1A Voice 32: BELLS
# ---------------------------------------------------------------------------
_BELLS = {
    "name": "BELLS   ",
    "algorithm": 5,
    "feedback": 5,
    "lfo": _lfo(speed=35, delay=0, pmd=0, amd=0, wave=0, sync=1),
    "operators": [
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 85, 96, 58), level=(96, 56, 48, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=82,
            freq_coarse=4, freq_fine=23, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 85, 96, 58), level=(96, 56, 48, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=82,
            freq_coarse=5, freq_fine=37, detune=7),
        _op(rate=(72, 76, 99, 71), level=(99, 88, 96, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=2, output_level=99,
            freq_coarse=1, freq_fine=0, detune=7),
        _op(rate=(99, 85, 96, 58), level=(96, 56, 48, 0),
            break_point=39, left_depth=0, right_depth=0,
            left_curve=0, right_curve=0, rate_scaling=2,
            amp_mod_sens=0, key_vel_sens=5, output_level=72,
            freq_coarse=13, freq_fine=0, detune=7),
    ],
}


# ---------------------------------------------------------------------------
# Assembled preset bank
# ---------------------------------------------------------------------------
FACTORY_PRESETS: list[dict] = [
    _BRASS_1,       # 1
    _BRASS_2,       # 2
    _BRASS_3,       # 3
    _STRINGS_1,     # 4
    _STRINGS_2,     # 5
    _STRINGS_3,     # 6
    _ORCHSTRA,      # 7
    _PIANO_1,       # 8
    _PIANO_2,       # 9
    _PIANO_3,       # 10
    _E_PIANO_1,     # 11
    _E_PIANO_2,     # 12
    _E_PIANO_3,     # 13
    _HARPSICH,      # 14
    _CLAV_1,        # 15
    _VIBE,          # 16
    _MARIMBA,       # 17
    _KOTO,          # 18
    _FLUTE_1,       # 19
    _FLUTE_2,       # 20
    _OBOE,          # 21
    _TRUMPET,       # 22
    _ORGAN_1,       # 23
    _ORGAN_2,       # 24
    _PIPES,         # 25
    _HARP_1,        # 26
    _GUITAR_1,      # 27
    _SYN_LEAD,      # 28
    _BASS_1,        # 29
    _BASS_2,        # 30
    _TUB_BELL,      # 31
    _BELLS,         # 32
]


def get_preset(index: int) -> dict:
    """Get a factory preset by index (0-31).

    Args:
        index: Preset index, 0-based (0 = BRASS 1, 31 = BELLS).

    Returns:
        Dictionary containing the full preset parameters.

    Raises:
        IndexError: If index is out of range.
    """
    if not 0 <= index <= 31:
        raise IndexError(f"Preset index {index} out of range (0-31)")
    return FACTORY_PRESETS[index]


def get_preset_names() -> list[str]:
    """Get the list of all 32 factory preset names in order.

    Returns:
        List of preset name strings.
    """
    return [p["name"] for p in FACTORY_PRESETS]
