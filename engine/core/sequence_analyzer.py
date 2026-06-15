from __future__ import annotations
"""
Sequence Analyzer — Persuasion Trajectory Modeling
====================================================
Models a multi-step flow (onboarding, checkout, email drip) as a
TRAJECTORY through 7-dimensional appraisal space.

Novel contribution: nobody has modeled persuasion as a trajectory
through appraisal space with transition-level prediction error
computation.

Computes:
    - Momentum: is each step increasing or decreasing approach activation?
    - Conflict spikes: sudden ACC conflict signals at transitions
    - Dopamine prediction error chain: does each step deliver >= prior reward?
    - Somatic marker accumulation: consistent trajectory vs fatiguing oscillation
    - Weakest transition: the specific step most likely to cause drop-off

Based on:
    - Schultz (1997) — dopamine prediction error signals
    - Friston (2010) — free-energy / active inference
    - Scherer (2001) — appraisal as sequential checking process
"""

import math
from dataclasses import dataclass
from typing import Optional

from core.appraisal_extractor import AppraisalExtractor, AppraisalScores
from core.circuit_predictor import CircuitPredictor, CircuitActivations, persuasion_effectiveness
from core.reframing_engine import ReframingEngine


@dataclass
class StepResult:
    """Analysis of a single step in the sequence."""
    index: int
    text: str
    appraisal: dict
    circuits: dict
    effectiveness: float
    dominant_circuit: str


@dataclass
class TransitionMetrics:
    """Metrics for the transition between two consecutive steps."""
    from_step: int
    to_step: int
    approach_delta: float          # positive = momentum building
    avoidance_delta: float         # positive = threat increasing
    deliberation_delta: float      # positive = confusion increasing
    dopamine_prediction_error: float  # negative = disappointment
    conflict_spike: float          # how much ACC conflict jumps
    appraisal_shift: dict          # per-dimension change
    risk_level: str                # "safe", "warning", "critical"


@dataclass
class SequenceResult:
    """Complete sequence analysis."""
    steps: list
    transitions: list
    trajectory_metrics: dict
    weakest_transition: Optional[dict]
    reframe_suggestion: Optional[str]
    pca_projection: list           # 2D coordinates for visualization

    def to_dict(self):
        return {
            "n_steps": len(self.steps),
            "steps": [{"index": s.index, "text": s.text[:60],
                        "effectiveness": s.effectiveness,
                        "dominant": s.dominant_circuit,
                        "appraisal": s.appraisal} for s in self.steps],
            "transitions": [{"from": t.from_step, "to": t.to_step,
                             "approach_delta": t.approach_delta,
                             "dopamine_pe": t.dopamine_prediction_error,
                             "conflict_spike": t.conflict_spike,
                             "risk": t.risk_level} for t in self.transitions],
            "trajectory_metrics": self.trajectory_metrics,
            "weakest_transition": self.weakest_transition,
            "reframe_suggestion": self.reframe_suggestion,
            "pca_2d": self.pca_projection,
        }


class SequenceAnalyzer:
    """Analyze ordered stimulus sequences as trajectories through appraisal space."""

    def __init__(self, extraction_mode="heuristic"):
        self.extractor = AppraisalExtractor()
        self.predictor = CircuitPredictor()
        self.reframer = ReframingEngine()
        self.mode = extraction_mode

    def analyze(self, stimuli):
        """Analyze an ordered list of text stimuli.

        Args:
            stimuli: list of strings (e.g., onboarding screens in order)

        Returns:
            SequenceResult with full trajectory analysis
        """
        # Score each step
        steps = []
        for i, text in enumerate(stimuli):
            appraisal = self.extractor.extract(text, mode=self.mode)
            pred = self.predictor.predict(appraisal)
            eff = persuasion_effectiveness(pred.circuits)
            steps.append(StepResult(
                index=i,
                text=text,
                appraisal=appraisal.to_dict(),
                circuits=pred.circuits.to_dict(),
                effectiveness=eff,
                dominant_circuit=pred.circuits.dominant,
            ))

        # Compute transitions
        transitions = []
        for i in range(len(steps) - 1):
            curr = steps[i]
            next_s = steps[i + 1]
            t = self._compute_transition(curr, next_s)
            transitions.append(t)

        # Trajectory-level metrics
        trajectory = self._compute_trajectory_metrics(steps, transitions)

        # Find weakest transition
        weakest = None
        if transitions:
            worst = min(transitions, key=lambda t: t.dopamine_prediction_error)
            if worst.risk_level != "safe":
                weakest = {
                    "from_step": worst.from_step,
                    "to_step": worst.to_step,
                    "from_text": steps[worst.from_step].text[:60],
                    "to_text": steps[worst.to_step].text[:60],
                    "dopamine_pe": worst.dopamine_prediction_error,
                    "risk": worst.risk_level,
                    "biggest_dim_drop": max(worst.appraisal_shift.items(),
                                            key=lambda x: abs(x[1]) if x[1] < 0 else 0,
                                            default=("none", 0)),
                }

        # Reframe suggestion for weakest step
        reframe = None
        if weakest:
            weak_step = steps[weakest["to_step"]]
            appraisal = AppraisalScores(**weak_step.appraisal)
            from core.circuit_predictor import BehavioralPrediction
            dummy_pred = BehavioralPrediction()
            tradeoffs = self.reframer.diagnose(appraisal, dummy_pred)
            if tradeoffs:
                t = tradeoffs[0]
                reframe = "Step %d ('%s'): %s %s from %.2f to %.2f → %s" % (
                    weakest["to_step"],
                    weak_step.text[:40],
                    t.direction, t.dimension,
                    t.current_value, t.projected_value,
                    t.net_assessment,
                )

        # PCA projection
        pca_2d = self._pca_project(steps)

        return SequenceResult(
            steps=steps,
            transitions=transitions,
            trajectory_metrics=trajectory,
            weakest_transition=weakest,
            reframe_suggestion=reframe,
            pca_projection=pca_2d,
        )

    def _compute_transition(self, curr, next_s):
        """Compute metrics for a single step-to-step transition."""
        c_circ = curr.circuits
        n_circ = next_s.circuits

        approach_delta = n_circ["approach"] - c_circ["approach"]
        avoidance_delta = n_circ["avoidance"] - c_circ["avoidance"]
        deliberation_delta = n_circ["deliberation"] - c_circ["deliberation"]

        # Dopamine prediction error: the brain predicted the CURRENT step's
        # approach level would continue. If next step is LOWER, that's a
        # negative prediction error = disappointment.
        dopamine_pe = round(approach_delta, 4)

        # Conflict spike: how much does the ACC conflict level jump?
        # Conflict = closeness of top two circuits
        curr_conflict = c_circ.get("conflict_level", 0)
        next_conflict = n_circ.get("conflict_level", 0)
        conflict_spike = round(max(0, next_conflict - curr_conflict), 4)

        # Per-dimension shift
        dim_shift = {}
        for dim in curr.appraisal:
            dim_shift[dim] = round(next_s.appraisal[dim] - curr.appraisal[dim], 4)

        # Risk classification
        if dopamine_pe < -0.1 or avoidance_delta > 0.1:
            risk = "critical"
        elif dopamine_pe < -0.05 or conflict_spike > 0.15:
            risk = "warning"
        else:
            risk = "safe"

        return TransitionMetrics(
            from_step=curr.index,
            to_step=next_s.index,
            approach_delta=round(approach_delta, 4),
            avoidance_delta=round(avoidance_delta, 4),
            deliberation_delta=round(deliberation_delta, 4),
            dopamine_prediction_error=dopamine_pe,
            conflict_spike=conflict_spike,
            appraisal_shift=dim_shift,
            risk_level=risk,
        )

    def _compute_trajectory_metrics(self, steps, transitions):
        """Compute aggregate trajectory-level metrics."""
        if not transitions:
            return {"momentum": 0, "oscillation": 0, "consistency": 1.0}

        # Momentum: average approach delta across transitions
        approach_deltas = [t.approach_delta for t in transitions]
        momentum = sum(approach_deltas) / len(approach_deltas)

        # Oscillation: how much does approach activation swing?
        # Low oscillation = consistent trajectory = good
        if len(approach_deltas) > 1:
            mean_delta = momentum
            oscillation = math.sqrt(
                sum((d - mean_delta) ** 2 for d in approach_deltas) / len(approach_deltas)
            )
        else:
            oscillation = 0.0

        # Somatic marker consistency: does the valence stay on one side?
        valences = [s.appraisal["valence"] for s in steps]
        valence_flips = sum(1 for i in range(len(valences) - 1)
                           if (valences[i] > 0.5) != (valences[i + 1] > 0.5))
        consistency = 1.0 - (valence_flips / max(len(valences) - 1, 1))

        # Conflict spikes count
        critical_transitions = sum(1 for t in transitions if t.risk_level == "critical")
        warning_transitions = sum(1 for t in transitions if t.risk_level == "warning")

        # Overall trajectory effectiveness trend
        effs = [s.effectiveness for s in steps]
        if len(effs) >= 2:
            eff_trend = (effs[-1] - effs[0]) / max(len(effs) - 1, 1)
        else:
            eff_trend = 0.0

        # Cumulative prediction error (total dopamine debt/surplus)
        cumulative_pe = sum(t.dopamine_prediction_error for t in transitions)

        return {
            "momentum": round(momentum, 4),
            "oscillation": round(oscillation, 4),
            "consistency": round(consistency, 4),
            "critical_transitions": critical_transitions,
            "warning_transitions": warning_transitions,
            "effectiveness_trend": round(eff_trend, 4),
            "cumulative_prediction_error": round(cumulative_pe, 4),
            "interpretation": self._interpret_trajectory(
                momentum, oscillation, consistency, critical_transitions, cumulative_pe
            ),
        }

    def _interpret_trajectory(self, momentum, oscillation, consistency,
                              critical_count, cumulative_pe):
        """Human-readable trajectory interpretation."""
        parts = []
        if momentum > 0.02:
            parts.append("Positive momentum — each step builds approach activation.")
        elif momentum < -0.02:
            parts.append("Negative momentum — approach activation declining through the sequence.")
        else:
            parts.append("Flat momentum — approach activation neither building nor declining.")

        if oscillation > 0.08:
            parts.append("High oscillation — emotional register swings fatigue the vmPFC.")
        if consistency < 0.6:
            parts.append("Low consistency — valence flips between positive and negative, disrupting somatic marker accumulation.")
        if critical_count > 0:
            parts.append("%d critical transition(s) — high drop-off risk at these points." % critical_count)
        if cumulative_pe < -0.1:
            parts.append("Cumulative dopamine debt — sequence delivers less reward than it promises. User will feel disappointed.")
        elif cumulative_pe > 0.1:
            parts.append("Dopamine surplus — sequence exceeds expectations. Strong positive somatic marker encoding.")

        return " ".join(parts) if parts else "Sequence is stable with no significant risk factors."

    def _pca_project(self, steps):
        """Project 7D appraisal vectors to 2D using simple PCA."""
        if len(steps) < 2:
            return [{"x": 0, "y": 0, "label": s.text[:30]} for s in steps]

        # Get appraisal vectors
        vectors = []
        for s in steps:
            vectors.append([s.appraisal[d] for d in
                           ["novelty", "valence", "goal_relevance", "coping_potential",
                            "agency", "certainty", "temporal_proximity"]])

        n = len(vectors)
        d = 7

        # Center the data
        means = [sum(v[j] for v in vectors) / n for j in range(d)]
        centered = [[v[j] - means[j] for j in range(d)] for v in vectors]

        # Covariance matrix
        cov = [[0.0] * d for _ in range(d)]
        for i in range(d):
            for j in range(d):
                cov[i][j] = sum(c[i] * c[j] for c in centered) / max(n - 1, 1)

        # Power iteration for top 2 eigenvectors (simple, no numpy needed)
        def power_iter(matrix, n_iter=50):
            import random
            v = [random.gauss(0, 1) for _ in range(len(matrix))]
            for _ in range(n_iter):
                mv = [sum(matrix[i][j] * v[j] for j in range(len(v))) for i in range(len(matrix))]
                norm = math.sqrt(sum(x * x for x in mv)) or 1.0
                v = [x / norm for x in mv]
            return v

        pc1 = power_iter(cov)

        # Deflate for PC2
        cov2 = [[cov[i][j] - pc1[i] * pc1[j] * sum(pc1[k] * sum(cov[k][l] * pc1[l] for l in range(d)) for k in range(d))
                  for j in range(d)] for i in range(d)]
        pc2 = power_iter(cov2)

        # Project
        projected = []
        for i, c in enumerate(centered):
            x = sum(c[j] * pc1[j] for j in range(d))
            y = sum(c[j] * pc2[j] for j in range(d))
            projected.append({
                "x": round(x, 4),
                "y": round(y, 4),
                "step": i,
                "label": steps[i].text[:30],
                "effectiveness": steps[i].effectiveness,
            })

        return projected
