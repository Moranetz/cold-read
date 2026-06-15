from __future__ import annotations
"""
Recipient Profile — 16-Dimension Individual Difference Model
=============================================================
Models WHO is being persuaded, not just WHAT the stimulus contains.

16 dimensions across 4 categories:
    Big Five Personality (5)  — Costa & McCrae 1992
    Moral Foundations (6)     — Haidt & Graham 2007
    Political Orientation (2) — Dual-axis model
    Situational (3)           — ELM + topic-specific state

Each dimension modulates how the same stimulus produces different
circuit activations in different recipients. A fear appeal that
triggers high avoidance in a high-neuroticism individual may
barely register in a low-neuroticism one.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class RecipientProfile:
    """16-dimension recipient model for individual-difference modulation.

    All continuous floats. Personality and moral foundations are 0.0-1.0.
    Political axes are -1.0 to 1.0. Situational dimensions are 0.0-1.0.
    """

    # ─── Big Five Personality (Costa & McCrae 1992) ─────────────────────
    openness: float = 0.5              # 0.0-1.0
    conscientiousness: float = 0.5     # 0.0-1.0
    extraversion: float = 0.5          # 0.0-1.0
    agreeableness: float = 0.5         # 0.0-1.0
    neuroticism: float = 0.5           # 0.0-1.0

    # ─── Moral Foundations Theory (Haidt & Graham 2007) ─────────────────
    care_harm: float = 0.5             # 0.0-1.0
    fairness_cheating: float = 0.5     # 0.0-1.0
    loyalty_betrayal: float = 0.5      # 0.0-1.0
    authority_subversion: float = 0.5  # 0.0-1.0
    sanctity_degradation: float = 0.5  # 0.0-1.0
    liberty_oppression: float = 0.5    # 0.0-1.0

    # ─── Political Orientation (dual-axis) ──────────────────────────────
    economic_ideology: float = 0.0     # -1.0 (left) to 1.0 (right)
    social_ideology: float = 0.0       # -1.0 (libertarian) to 1.0 (authoritarian)

    # ─── Situational (topic-specific) ───────────────────────────────────
    prior_belief: float = 0.5          # 0.0-1.0 (pre-existing stance on THIS topic)
    involvement: float = 0.5           # 0.0-1.0 (how much they care about THIS topic)
    elaboration_likelihood: float = 0.5  # 0.0-1.0 (central vs peripheral processing)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_vector(self) -> list:
        return [
            self.openness, self.conscientiousness, self.extraversion,
            self.agreeableness, self.neuroticism,
            self.care_harm, self.fairness_cheating, self.loyalty_betrayal,
            self.authority_subversion, self.sanctity_degradation, self.liberty_oppression,
            self.economic_ideology, self.social_ideology,
            self.prior_belief, self.involvement, self.elaboration_likelihood,
        ]

    def validate(self) -> bool:
        """Check all dimensions are in valid ranges."""
        for dim in ["openness", "conscientiousness", "extraversion",
                     "agreeableness", "neuroticism", "care_harm",
                     "fairness_cheating", "loyalty_betrayal", "authority_subversion",
                     "sanctity_degradation", "liberty_oppression",
                     "prior_belief", "involvement", "elaboration_likelihood"]:
            val = getattr(self, dim)
            if not (0.0 <= val <= 1.0):
                return False
        for dim in ["economic_ideology", "social_ideology"]:
            val = getattr(self, dim)
            if not (-1.0 <= val <= 1.0):
                return False
        return True
