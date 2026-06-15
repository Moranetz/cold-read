from __future__ import annotations
"""
Reframing Engine — Mechanical Tradeoff Surface
================================================
Reports the CONSEQUENCES of changing each appraisal dimension.
Does not prescribe which direction to move. Maps the full surface
of tradeoffs across three time horizons:

    immediate_compliance — action on this exposure
    repeat_compliance — action on next exposure
    retaliation_probability — active brand harm

For any stimulus, outputs: "If you increase dimension X from A to B,
immediate_compliance changes by +C, repeat_compliance by +D,
retaliation_probability by +E." The operator decides the tradeoff.
"""

from dataclasses import dataclass
from typing import Optional

from core.appraisal_extractor import AppraisalScores
from core.circuit_predictor import CircuitPredictor, BehavioralPrediction


@dataclass
class TradeoffProjection:
    """Predicted consequences of changing one appraisal dimension."""
    dimension: str
    current_value: float
    projected_value: float
    direction: str                   # "increase" or "decrease"
    delta_immediate_compliance: float
    delta_repeat_compliance: float
    delta_retaliation: float
    net_assessment: str              # mechanical summary, not editorial


DIMENSION_STEPS = {
    # For each dimension: (decrease_to, increase_to)
    # These are the values we project to when showing tradeoffs
    "novelty": (0.2, 0.6),
    "valence": (0.2, 0.8),
    "goal_relevance": (0.2, 0.8),
    "coping_potential": (0.2, 0.8),
    "agency": (0.1, 0.7),
    "certainty": (0.2, 0.8),
    "temporal_proximity": (0.2, 0.8),
}


class ReframingEngine:
    """Map the full tradeoff surface for any stimulus."""

    def __init__(self):
        self.predictor = CircuitPredictor()

    def map_surface(
        self,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
        somatic_marker_congruence: float = 0.5,
        insula_disgust_signal: float = 0.0,
        familiarity: float = 0.5,
    ) -> list:
        """For each dimension, project consequences of increasing and decreasing it.

        Returns list of TradeoffProjection objects showing the mechanical
        consequences of each possible change. No editorial recommendations.
        """
        current = appraisal.to_dict()
        projections = []

        for dim, (low_target, high_target) in DIMENSION_STEPS.items():
            current_val = current[dim]

            # Project: what if we INCREASE this dimension?
            if current_val < high_target - 0.05:
                proj_up = self._project(
                    appraisal, prediction, dim, high_target,
                    somatic_marker_congruence, insula_disgust_signal, familiarity,
                )
                projections.append(proj_up)

            # Project: what if we DECREASE this dimension?
            if current_val > low_target + 0.05:
                proj_down = self._project(
                    appraisal, prediction, dim, low_target,
                    somatic_marker_congruence, insula_disgust_signal, familiarity,
                )
                projections.append(proj_down)

        # Sort by absolute impact on immediate compliance
        projections.sort(key=lambda p: abs(p.delta_immediate_compliance), reverse=True)
        return projections

    def _project(self, appraisal, current_pred, dim, target_value,
                 somatic_marker_congruence, insula_disgust_signal, familiarity):
        """Project the consequence of changing one dimension to a target value."""
        current_val = appraisal.to_dict()[dim]
        direction = "increase" if target_value > current_val else "decrease"

        # Create modified appraisal
        modified = appraisal.to_dict()
        modified[dim] = target_value
        mod_appraisal = AppraisalScores(**modified)

        # Re-predict with modified appraisal
        mod_pred = self.predictor.predict(
            mod_appraisal,
            somatic_marker_congruence=somatic_marker_congruence,
            insula_disgust_signal=insula_disgust_signal,
            familiarity=familiarity,
        )

        # Compute deltas
        d_immediate = mod_pred.immediate_compliance - current_pred.immediate_compliance
        d_repeat = mod_pred.repeat_compliance - current_pred.repeat_compliance
        d_retaliation = mod_pred.retaliation_probability - current_pred.retaliation_probability

        # Mechanical summary — no editorial language
        parts = []
        if abs(d_immediate) > 0.02:
            parts.append("immediate_compliance %+.2f" % d_immediate)
        if abs(d_repeat) > 0.02:
            parts.append("repeat_compliance %+.2f" % d_repeat)
        if abs(d_retaliation) > 0.02:
            parts.append("retaliation %+.2f" % d_retaliation)
        net = "; ".join(parts) if parts else "negligible change across all horizons"

        return TradeoffProjection(
            dimension=dim,
            current_value=round(current_val, 3),
            projected_value=round(target_value, 3),
            direction=direction,
            delta_immediate_compliance=round(d_immediate, 4),
            delta_repeat_compliance=round(d_repeat, 4),
            delta_retaliation=round(d_retaliation, 4),
            net_assessment=net,
        )

    def diagnose(self, appraisal, prediction, **kwargs):
        """Map the full tradeoff surface. Returns list of TradeoffProjection."""
        return self.map_surface(appraisal, prediction, **kwargs)

    def top_fix(self, appraisal, prediction, **kwargs):
        """Return the projection with the largest positive impact on
        immediate compliance. This is mechanical, not editorial — it
        identifies the single change that moves the number most."""
        projections = self.map_surface(appraisal, prediction, **kwargs)
        positive = [p for p in projections if p.delta_immediate_compliance > 0]
        if not positive:
            return None
        return max(positive, key=lambda p: p.delta_immediate_compliance)
