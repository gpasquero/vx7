"""DX7 Algorithm definitions and rendering.

The DX7 has 32 algorithms, each defining how 6 operators (numbered 1-6) are
connected.  Operators can be:
  - **Carriers**: their output is summed to produce the final audio.
  - **Modulators**: their output phase-modulates another operator.
  - **Feedback**: one operator in each algorithm feeds back into itself.

Algorithm data format
---------------------
Each algorithm is described by an AlgorithmDef with:
  - ``carriers``:  frozenset of operator indices (0-based: op1=0 .. op6=5)
  - ``modulations``: tuple of (source, destination) pairs -- source modulates
    destination (both 0-based).
  - ``feedback_op``: index of the operator with self-feedback (0-based).

All 32 algorithms are transcribed from the original Yamaha DX7 operator's
manual algorithm chart.

Convention used in comments:
  - Operators are referred to by their DX7 number (1-6) but stored 0-indexed.
  - ``6->5->4->3->2->1*`` means OP6 modulates OP5, OP5 modulates OP4, etc.
    The asterisk (*) marks carriers.
  - ``fb:N`` indicates which operator has self-feedback.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .operator import Operator


# ---------------------------------------------------------------------------
# Algorithm data structure
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AlgorithmDef:
    """Definition of a single DX7 algorithm."""
    carriers: frozenset[int]
    modulations: tuple[tuple[int, int], ...]
    feedback_op: int  # 0-based operator index


# ---------------------------------------------------------------------------
# All 32 DX7 algorithms
# ---------------------------------------------------------------------------
# Transcribed from the Yamaha DX7 operator's manual algorithm chart,
# cross-referenced with the Dexed open-source emulator.
#
# Operators are 0-indexed: op0 = DX7 "OP 1", ... op5 = DX7 "OP 6".
# (src, dst) means src's output phase-modulates dst.
# carriers = operators whose output goes to the audio bus.
# feedback_op = operator that feeds back into itself.

ALGORITHMS: list[AlgorithmDef] = [
    # Algo 1:  6->5->4->3->2->1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 3), (3, 2), (2, 1), (1, 0)),
        feedback_op=5,
    ),
    # Algo 2:  6->5->4->3->2->1*   fb:2
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 3), (3, 2), (2, 1), (1, 0)),
        feedback_op=1,
    ),
    # Algo 3:  6->5->4->1*  3->2->1*   fb:6  (two stacks merge at OP1)
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 3), (3, 0), (2, 1), (1, 0)),
        feedback_op=5,
    ),
    # Algo 4:  6->5->4->3->2->1*   fb:4
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 3), (3, 2), (2, 1), (1, 0)),
        feedback_op=3,
    ),
    # Algo 5:  6->5->4->3*   2->1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((5, 4), (4, 3), (3, 2), (1, 0)),
        feedback_op=5,
    ),
    # Algo 6:  6->5->4->3*   2->1*   fb:5
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((5, 4), (4, 3), (3, 2), (1, 0)),
        feedback_op=4,
    ),
    # Algo 7:  6->5->4+3 -> 2 -> 1*   fb:6  (ops 4,3 both mod op 2)
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 3), (3, 1), (2, 1), (1, 0)),
        feedback_op=5,
    ),
    # Algo 8:  4->3   6->5   (3+5)->2->1*   fb:4
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((3, 2), (5, 4), (2, 1), (4, 1), (1, 0)),
        feedback_op=3,
    ),
    # Algo 9:  4->3   6->5   (3+5)->2->1*   fb:2
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((3, 2), (5, 4), (2, 1), (4, 1), (1, 0)),
        feedback_op=1,
    ),
    # Algo 10:  6->5->4*   3->2->1*   fb:3
    AlgorithmDef(
        carriers=frozenset({0, 3}),
        modulations=((5, 4), (4, 3), (2, 1), (1, 0)),
        feedback_op=2,
    ),
    # Algo 11:  6->5->4*   3->2->1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 3}),
        modulations=((5, 4), (4, 3), (2, 1), (1, 0)),
        feedback_op=5,
    ),
    # Algo 12:  2->1*   6->5->4->3*   fb:2
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((1, 0), (5, 4), (4, 3), (3, 2)),
        feedback_op=1,
    ),
    # Algo 13:  2->1*   6->5->4->3*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((1, 0), (5, 4), (4, 3), (3, 2)),
        feedback_op=5,
    ),
    # Algo 14:  6->5->4->3*   2->1*   fb:6  (same topology as 5, fb:6)
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((5, 4), (4, 3), (3, 2), (1, 0)),
        feedback_op=5,
    ),
    # Algo 15:  6->5->3*   2->1*   fb:2  (5 skips 4, goes direct to 3)
    AlgorithmDef(
        carriers=frozenset({0, 2}),
        modulations=((1, 0), (5, 4), (4, 2)),
        feedback_op=1,
    ),
    # Algo 16:  6->5   (5+3+2)->1*   4->3   fb:6
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 0), (3, 2), (2, 0), (1, 0)),
        feedback_op=5,
    ),
    # Algo 17:  6->5   3->2   (5+4+2)->1*   fb:2
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((5, 4), (4, 0), (3, 0), (2, 1), (1, 0)),
        feedback_op=1,
    ),
    # Algo 18:  3->2   6->5->4   (2+4)->1*   fb:3
    AlgorithmDef(
        carriers=frozenset({0}),
        modulations=((2, 1), (5, 4), (4, 3), (1, 0), (3, 0)),
        feedback_op=2,
    ),
    # Algo 19:  6->5->(4*+3*+2*)   1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3}),
        modulations=((5, 4), (4, 3), (4, 2), (4, 1)),
        feedback_op=5,
    ),
    # Algo 20:  3->2->1*   6->(5*+4*)   fb:3
    AlgorithmDef(
        carriers=frozenset({0, 3, 4}),
        modulations=((2, 1), (1, 0), (5, 4), (5, 3)),
        feedback_op=2,
    ),
    # Algo 21:  6->(5*+4*+3*)   2->1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 2, 3, 4}),
        modulations=((5, 4), (5, 3), (5, 2), (1, 0)),
        feedback_op=5,
    ),
    # Algo 22:  6->(5*+4*+3*+2*+1*)   fb:6  (6 modulates all others)
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3, 4}),
        modulations=((5, 4), (5, 3), (5, 2), (5, 1), (5, 0)),
        feedback_op=5,
    ),
    # Algo 23:  6->5->4*   3*   2->1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 2, 3}),
        modulations=((5, 4), (4, 3), (1, 0)),
        feedback_op=5,
    ),
    # Algo 24:  6->5->(4*+3*)   2*   1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3}),
        modulations=((5, 4), (4, 3), (4, 2)),
        feedback_op=5,
    ),
    # Algo 25:  6->5->4*   3*   2*   1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3}),
        modulations=((5, 4), (4, 3)),
        feedback_op=5,
    ),
    # Algo 26:  6->5->4*   6->3*   2->1*   fb:6  (6 feeds both 5 and 3)
    AlgorithmDef(
        carriers=frozenset({0, 2, 3}),
        modulations=((5, 4), (4, 3), (5, 2), (1, 0)),
        feedback_op=5,
    ),
    # Algo 27:  6->5*   3->2->1*   4*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 3, 4}),
        modulations=((2, 1), (1, 0), (5, 4)),
        feedback_op=5,
    ),
    # Algo 28:  5->4->3*   2->1*   6*   fb:5
    AlgorithmDef(
        carriers=frozenset({0, 2, 5}),
        modulations=((4, 3), (3, 2), (1, 0)),
        feedback_op=4,
    ),
    # Algo 29:  6->5*   4->3*   2*   1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 4}),
        modulations=((5, 4), (3, 2)),
        feedback_op=5,
    ),
    # Algo 30:  5->4->3*   6*   2*   1*   fb:5
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 5}),
        modulations=((4, 3), (3, 2)),
        feedback_op=4,
    ),
    # Algo 31:  6->5*   4*   3*   2*   1*   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3, 4}),
        modulations=((5, 4),),
        feedback_op=5,
    ),
    # Algo 32:  6*   5*   4*   3*   2*   1*   all carriers   fb:6
    AlgorithmDef(
        carriers=frozenset({0, 1, 2, 3, 4, 5}),
        modulations=(),
        feedback_op=5,
    ),
]

assert len(ALGORITHMS) == 32, f"Expected 32 algorithms, got {len(ALGORITHMS)}"


# ---------------------------------------------------------------------------
# DX7 feedback level conversion
# ---------------------------------------------------------------------------
# The DX7 feedback parameter is 0-7.  0 = no feedback.
# Each step doubles the feedback amount, expressed in radians.

FEEDBACK_LEVELS: np.ndarray = np.array(
    [0.0,
     math.pi / 256.0,
     math.pi / 128.0,
     math.pi / 64.0,
     math.pi / 32.0,
     math.pi / 16.0,
     math.pi / 8.0,
     math.pi / 4.0],
    dtype=np.float64,
)


def feedback_param_to_level(param: int) -> float:
    """Convert DX7 feedback parameter (0-7) to feedback level in radians."""
    param = int(np.clip(param, 0, 7))
    return float(FEEDBACK_LEVELS[param])


# ---------------------------------------------------------------------------
# Topological sort for rendering order
# ---------------------------------------------------------------------------

def _build_dependency_order(algo: AlgorithmDef) -> list[int]:
    """Compute a rendering order for the 6 operators such that every
    modulator is rendered before the operator it modulates.

    Returns a list of operator indices (0-5) in the order they should be
    rendered.
    """
    # Build adjacency: who modulates whom.
    modulated_by: dict[int, set[int]] = {i: set() for i in range(6)}
    for src, dst in algo.modulations:
        modulated_by[dst].add(src)

    # Topological sort (Kahn's algorithm).
    # Feedback creates a self-loop; remove it for sorting purposes.
    if algo.feedback_op >= 0:
        modulated_by[algo.feedback_op].discard(algo.feedback_op)

    in_degree = {i: len(modulated_by[i]) for i in range(6)}
    queue: list[int] = sorted(i for i in range(6) if in_degree[i] == 0)
    order: list[int] = []

    while queue:
        op = queue.pop(0)
        order.append(op)
        for dst in range(6):
            if op in modulated_by[dst]:
                modulated_by[dst].discard(op)
                in_degree[dst] -= 1
                if in_degree[dst] == 0:
                    # Insert sorted to maintain deterministic order.
                    queue.append(dst)
                    queue.sort()

    # Safety: append any missing operators.
    for i in range(6):
        if i not in order:
            order.append(i)

    return order


# Pre-compute rendering orders for all 32 algorithms.
_RENDER_ORDERS: list[list[int]] = [
    _build_dependency_order(algo) for algo in ALGORITHMS
]


# ---------------------------------------------------------------------------
# Algorithm rendering
# ---------------------------------------------------------------------------

def apply_algorithm(
    operators: Sequence[Operator],
    algorithm_index: int,
    feedback_param: int,
    num_samples: int,
    base_freq: float,
    sample_rate: int = 44100,
    feedback_buffers: Optional[list[np.ndarray]] = None,
    pitch_mod: Optional[np.ndarray] = None,
    amp_mod: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Render audio for one block using the specified DX7 algorithm.

    Parameters
    ----------
    operators : sequence of 6 Operator instances
        The operators, indexed 0-5.
    algorithm_index : int
        Algorithm number 0-31 (0-based; DX7 algorithms 1-32).
    feedback_param : int
        DX7 feedback parameter 0-7.
    num_samples : int
        Number of audio samples to generate.
    base_freq : float
        Base frequency of the note in Hz.
    sample_rate : int
        Audio sample rate.
    feedback_buffers : list of np.ndarray, optional
        List of 6 arrays, each of shape (2,), holding per-operator feedback
        state.  Created automatically if None.
    pitch_mod : np.ndarray, optional
        LFO pitch modulation, shape (num_samples,), bipolar.
    amp_mod : np.ndarray, optional
        LFO amplitude modulation, shape (num_samples,), unipolar (1.0 = none).

    Returns
    -------
    np.ndarray
        Mixed carrier output, float64, shape (num_samples,).
    """
    assert len(operators) == 6, "Must provide exactly 6 operators"
    algo = ALGORITHMS[algorithm_index]
    fb_level = feedback_param_to_level(feedback_param)

    if feedback_buffers is None:
        feedback_buffers = [np.zeros(2, dtype=np.float64) for _ in range(6)]

    # Build modulation map: for each operator, collect which operators
    # modulate it.
    mod_sources: dict[int, list[int]] = {i: [] for i in range(6)}
    for src, dst in algo.modulations:
        mod_sources[dst].append(src)

    # Storage for each operator's output.
    op_outputs: list[Optional[np.ndarray]] = [None] * 6

    # Get rendering order.
    order = _RENDER_ORDERS[algorithm_index]

    for op_idx in order:
        op = operators[op_idx]

        # Collect modulation input from already-rendered modulators.
        mod_input: Optional[np.ndarray] = None
        for src_idx in mod_sources[op_idx]:
            if src_idx == op_idx:
                continue  # Self-feedback handled separately.
            src_out = op_outputs[src_idx]
            if src_out is not None:
                if mod_input is None:
                    mod_input = src_out.copy()
                else:
                    mod_input += src_out

        is_fb_op = (op_idx == algo.feedback_op and fb_level > 0)
        is_carrier = op_idx in algo.carriers

        if is_fb_op:
            # Render with self-feedback.
            output = op.render_with_feedback(
                num_samples, fb_level, feedback_buffers[op_idx]
            )
            if is_carrier:
                # render_with_feedback scales by mod_index; rescale to carrier
                # amplitude.
                if op._mod_index > 1e-12:
                    output = output * (op._amplitude / op._mod_index)
        else:
            # Normal render.
            output = op.render(
                num_samples,
                modulation=mod_input,
                as_carrier=is_carrier,
            )

        # Apply LFO amplitude modulation to carriers.
        if is_carrier and amp_mod is not None:
            output = output * amp_mod

        op_outputs[op_idx] = output

    # Mix carriers.
    mix = np.zeros(num_samples, dtype=np.float64)
    num_carriers = len(algo.carriers)
    for c_idx in algo.carriers:
        if op_outputs[c_idx] is not None:
            mix += op_outputs[c_idx]

    # Normalise by number of carriers to prevent clipping.
    if num_carriers > 1:
        mix /= math.sqrt(num_carriers)

    return mix
