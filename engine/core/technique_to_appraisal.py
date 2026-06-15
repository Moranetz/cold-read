from __future__ import annotations
"""
Technique-to-Appraisal Bridge
==============================
Maps detected persuasion techniques (from unified_auditor) to their
appraisal dimension impacts. This bridges the existing detection system
with the new limbic prediction system.

When the auditor detects 'SCARCITY', this module tells the circuit
predictor: scarcity increases temporal_proximity (+0.3), decreases
certainty (-0.1), and may decrease agency (-0.2 if fake).

This turns a detection tool into a prediction tool.
"""

from dataclasses import dataclass


@dataclass
class AppraisalImpact:
    """How a detected technique shifts appraisal dimensions."""
    technique: str
    category: str  # tactical_stimulus, psychological, linguistic
    novelty: float = 0.0
    valence: float = 0.0
    goal_relevance: float = 0.0
    coping_potential: float = 0.0
    agency: float = 0.0
    certainty: float = 0.0
    temporal_proximity: float = 0.0
    disgust_risk: float = 0.0  # probability of triggering insula if overused

    def to_dict(self) -> dict:
        return {
            "technique": self.technique,
            "shifts": {
                "novelty": self.novelty,
                "valence": self.valence,
                "goal_relevance": self.goal_relevance,
                "coping_potential": self.coping_potential,
                "agency": self.agency,
                "certainty": self.certainty,
                "temporal_proximity": self.temporal_proximity,
            },
            "disgust_risk": self.disgust_risk,
        }


# ─── Technique impact mappings ──────────────────────────────────────────────
# Values are SHIFTS (deltas), not absolute scores.
# Positive = increases that dimension. Negative = decreases.
# disgust_risk = probability the insula fires if this technique is detected.

TECHNIQUE_IMPACTS: dict[str, AppraisalImpact] = {

    # ── Cialdini Psychological Principles ────────────────────────────────

    "AUTHORITY": AppraisalImpact(
        technique="AUTHORITY", category="psychological",
        certainty=+0.15, agency=-0.05,
        disgust_risk=0.3,  # synthetic authority triggers insula
    ),
    "SOCIAL_PROOF": AppraisalImpact(
        technique="SOCIAL_PROOF", category="psychological",
        certainty=+0.20, goal_relevance=+0.05,
        disgust_risk=0.1,
    ),
    "RECIPROCITY": AppraisalImpact(
        technique="RECIPROCITY", category="psychological",
        valence=+0.15, agency=-0.10,
        disgust_risk=0.2,  # forced reciprocity feels manipulative
    ),
    "COMMITMENT": AppraisalImpact(
        technique="COMMITMENT", category="psychological",
        certainty=+0.10, agency=-0.05,
        disgust_risk=0.15,
    ),
    "SCARCITY": AppraisalImpact(
        technique="SCARCITY", category="psychological",
        temporal_proximity=+0.30, certainty=-0.10, agency=-0.20,
        disgust_risk=0.6,  # fake scarcity is the #1 disgust trigger
    ),
    "LIKING": AppraisalImpact(
        technique="LIKING", category="psychological",
        valence=+0.15, goal_relevance=+0.05,
        disgust_risk=0.1,
    ),
    "UNITY": AppraisalImpact(
        technique="UNITY", category="psychological",
        valence=+0.10, goal_relevance=+0.15, certainty=+0.10,
        disgust_risk=0.05,
    ),
    "FRAMING": AppraisalImpact(
        technique="FRAMING", category="psychological",
        valence=+0.10, certainty=+0.05,
        disgust_risk=0.2,
    ),

    # ── Tactical Stimuli ─────────────────────────────────────────────────

    "PERSONAL": AppraisalImpact(
        technique="PERSONAL", category="tactical_stimulus",
        goal_relevance=+0.25, agency=+0.10,
        disgust_risk=0.15,
    ),
    "CONTRASTABLE": AppraisalImpact(
        technique="CONTRASTABLE", category="tactical_stimulus",
        certainty=+0.15, novelty=+0.10,
        disgust_risk=0.2,
    ),
    "TANGIBLE": AppraisalImpact(
        technique="TANGIBLE", category="tactical_stimulus",
        coping_potential=+0.15, certainty=+0.10,
        disgust_risk=0.05,
    ),
    "MEMORABLE": AppraisalImpact(
        technique="MEMORABLE", category="tactical_stimulus",
        novelty=+0.20, valence=+0.10,
        disgust_risk=0.05,
    ),
    "VISUAL": AppraisalImpact(
        technique="VISUAL", category="tactical_stimulus",
        novelty=+0.10, valence=+0.10, coping_potential=+0.05,
        disgust_risk=0.05,
    ),
    "EMOTIONAL": AppraisalImpact(
        technique="EMOTIONAL", category="tactical_stimulus",
        valence=+0.20, goal_relevance=+0.15,
        disgust_risk=0.3,  # high-intensity emotional appeals trigger insula
    ),

    # ── Linguistic Patterns ──────────────────────────────────────────────

    "RHETORICAL_DEVICES": AppraisalImpact(
        technique="RHETORICAL_DEVICES", category="linguistic",
        novelty=+0.10, certainty=+0.05,
        disgust_risk=0.1,
    ),
    "SYNTACTIC_PATTERNS": AppraisalImpact(
        technique="SYNTACTIC_PATTERNS", category="linguistic",
        coping_potential=+0.05, certainty=+0.05,
        disgust_risk=0.05,
    ),
    "FRAMING_EFFECTS": AppraisalImpact(
        technique="FRAMING_EFFECTS", category="linguistic",
        valence=+0.10, certainty=+0.10,
        disgust_risk=0.2,
    ),
    "PRAGMATIC_PATTERNS": AppraisalImpact(
        technique="PRAGMATIC_PATTERNS", category="linguistic",
        agency=-0.05, certainty=+0.05,
        disgust_risk=0.15,
    ),
    "HEDGING_CERTAINTY": AppraisalImpact(
        technique="HEDGING_CERTAINTY", category="linguistic",
        certainty=-0.10, agency=+0.05,
        disgust_risk=0.0,
    ),
    "CONCEPTUAL_METAPHOR": AppraisalImpact(
        technique="CONCEPTUAL_METAPHOR", category="linguistic",
        novelty=+0.15, coping_potential=+0.10,
        disgust_risk=0.05,
    ),
    "DISCOURSE_MARKERS": AppraisalImpact(
        technique="DISCOURSE_MARKERS", category="linguistic",
        coping_potential=+0.05, certainty=+0.05,
        disgust_risk=0.05,  # "however", "therefore" signal structured argumentation
    ),
    "REGISTER_FORMALITY": AppraisalImpact(
        technique="REGISTER_FORMALITY", category="linguistic",
        agency=-0.05, certainty=+0.10,
        disgust_risk=0.1,  # overly formal register can feel inauthentic
    ),
}


def apply_technique_impacts(
    base_appraisal: dict[str, float],
    detected_techniques: list[str],
) -> tuple[dict[str, float], float]:
    """Apply technique impacts to base appraisal scores.

    Returns:
        (adjusted_scores, aggregate_disgust_risk)
    """
    adjusted = dict(base_appraisal)
    disgust_signals = []

    for technique in detected_techniques:
        impact = TECHNIQUE_IMPACTS.get(technique)
        if not impact:
            continue

        for dim in ["novelty", "valence", "goal_relevance", "coping_potential",
                     "agency", "certainty", "temporal_proximity"]:
            shift = getattr(impact, dim)
            if shift != 0:
                adjusted[dim] = round(min(1.0, max(0.0, adjusted[dim] + shift)), 3)

        disgust_signals.append(impact.disgust_risk)

    # Aggregate disgust: compounds with multiple high-risk techniques
    if disgust_signals:
        # 1 - product of (1 - each risk) = probability at least one triggers
        no_disgust_prob = 1.0
        for d in disgust_signals:
            no_disgust_prob *= (1.0 - d)
        aggregate_disgust = round(1.0 - no_disgust_prob, 4)
    else:
        aggregate_disgust = 0.0

    return adjusted, aggregate_disgust
