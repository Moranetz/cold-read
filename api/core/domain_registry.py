from __future__ import annotations
"""
Domain-Specific Weight Registry — Separate fitted parameters per domain
========================================================================
Universal weights treat all contexts identically. This is wrong:
scarcity drives purchase urgency at 2x the weight it drives opinion change.
Moral reframing is highest-weight in campaign messaging but irrelevant
in e-commerce. Authority citation works for crisis PR with media but
produces reactance with regulators.

Three domain registries + universal fallback:
    ecommerce   — optimized for purchase/conversion behavior
    campaign    — optimized for belief shift + vote intention
    crisis_pr   — optimized for trust recovery + counter-narrative suppression

Each weight carries:
    value       — the parameter value
    provenance  — FITTED / CONSTRAINED / UNCALIBRATED
    citation    — literature or data source
    confidence_interval — bounds if known
    domain      — which domain this weight belongs to
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

from core.circuit_predictor import WEIGHT_REGISTRY


class Provenance(str, Enum):
    FITTED = "FITTED"
    CONSTRAINED = "CONSTRAINED"
    UNCALIBRATED = "UNCALIBRATED"


class StakeholderType(str, Enum):
    MEDIA = "media"
    REGULATORS = "regulators"
    CUSTOMERS = "customers"
    EMPLOYEES = "employees"
    INVESTORS = "investors"


@dataclass
class DomainWeight:
    """A single weight with full provenance tracking."""
    name: str
    value: float
    provenance: str
    citation: str
    confidence_interval: tuple = (None, None)
    domain: str = "universal"

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "provenance": self.provenance,
            "citation": self.citation,
            "confidence_interval": list(self.confidence_interval),
            "domain": self.domain,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STAKEHOLDER PROFILES — Auto-loaded recipient parameters for crisis PR
# ═══════════════════════════════════════════════════════════════════════════════

STAKEHOLDER_PROFILES = {
    "media": {
        "elaboration_likelihood": 0.9,
        "openness": 0.8,
        "liberty_oppression": 0.7,
        "involvement": 0.7,
        "agreeableness": 0.4,
    },
    "regulators": {
        "authority_subversion": 0.8,
        "elaboration_likelihood": 0.85,
        "conscientiousness": 0.8,
        "involvement": 0.8,
        "agreeableness": 0.3,
    },
    "customers": {
        "elaboration_likelihood": 0.5,
        "involvement": 0.8,
        "neuroticism": 0.6,
        "agreeableness": 0.5,
    },
    "investors": {
        "conscientiousness": 0.85,
        "elaboration_likelihood": 0.8,
        "neuroticism": 0.3,
        "involvement": 0.8,
        "agreeableness": 0.4,
    },
    "employees": {
        "loyalty_betrayal": 0.7,
        "involvement": 0.9,
        "elaboration_likelihood": 0.5,
        "neuroticism": 0.6,
        "agreeableness": 0.6,
    },
}


class DomainWeightRegistry:
    """Domain-specific weight sets for the circuit predictor pipeline.

    Stores technique modifier overrides and circuit weight adjustments
    that differ by domain. The universal() fallback returns the current
    circuit_predictor weights unchanged.
    """

    def __init__(self, domain: str, weights: dict = None, technique_overrides: dict = None,
                 domain_outcomes: list = None):
        self.domain = domain
        self._weights = weights or {}
        self._technique_overrides = technique_overrides or {}
        self._domain_outcomes = domain_outcomes or []

    def get_weight(self, name: str) -> Optional[DomainWeight]:
        return self._weights.get(name)

    def get_technique_override(self, technique_name: str) -> Optional[dict]:
        return self._technique_overrides.get(technique_name)

    def list_fitted_weights(self) -> list:
        return [w for w in self._weights.values()
                if w.provenance in ("FITTED", Provenance.FITTED)]

    def list_uncalibrated_weights(self) -> list:
        return [w for w in self._weights.values()
                if w.provenance in ("UNCALIBRATED", Provenance.UNCALIBRATED)]

    def list_all_weights(self) -> list:
        return list(self._weights.values())

    @property
    def outcome_names(self) -> list:
        return list(self._domain_outcomes)

    def provenance_summary(self) -> dict:
        counts = {"FITTED": 0, "CONSTRAINED": 0, "UNCALIBRATED": 0}
        for w in self._weights.values():
            counts[w.provenance] = counts.get(w.provenance, 0) + 1
        return counts

    # ═══════════════════════════════════════════════════════════════════════
    # FACTORY METHODS
    # ═══════════════════════════════════════════════════════════════════════

    @classmethod
    def universal(cls) -> DomainWeightRegistry:
        """Return universal weights from circuit_predictor — the Session 1-2 baseline."""
        weights = {}
        for name, entry in WEIGHT_REGISTRY.items():
            weights[name] = DomainWeight(
                name=name,
                value=entry["value"],
                provenance=entry["status"],
                citation=entry["citation"][:120],
                domain="universal",
            )
        return cls(domain="universal", weights=weights)

    @classmethod
    def ecommerce(cls) -> DomainWeightRegistry:
        """E-commerce weight registry — fitted to purchase/conversion behavior.

        Key differences from universal:
            - scarcity techniques: circuit modifier weight *= 2.0
            - loss_frame: valence shift *= 1.5 (Knutson et al. 2007)
            - social_proof x high_extraversion: amplified 1.4x
            - price_anchoring/anchoring: weight *= 1.8
            - reciprocity: strongest approach activation, approach += 0.25
            - urgency_appeal: temporal_proximity shift *= 1.6
            - false_scarcity/false_urgency: insula_activation *= 1.3
        """
        weights = {
            "ecom.scarcity_circuit_multiplier": DomainWeight(
                name="ecom.scarcity_circuit_multiplier",
                value=2.0,
                provenance="UNCALIBRATED",
                citation="Scarcity drives purchase urgency at ~2x the weight it drives opinion change",
                domain="ecommerce",
            ),
            "ecom.loss_frame_valence_multiplier": DomainWeight(
                name="ecom.loss_frame_valence_multiplier",
                value=1.5,
                provenance="CONSTRAINED",
                citation="Knutson et al. 2007: NAc activation predicts purchase, insula predicts rejection",
                confidence_interval=(1.2, 1.8),
                domain="ecommerce",
            ),
            "ecom.social_proof_extraversion_multiplier": DomainWeight(
                name="ecom.social_proof_extraversion_multiplier",
                value=1.4,
                provenance="UNCALIBRATED",
                citation="Social shopping amplification for high-extraversion recipients",
                domain="ecommerce",
            ),
            "ecom.anchoring_weight_multiplier": DomainWeight(
                name="ecom.anchoring_weight_multiplier",
                value=1.8,
                provenance="UNCALIBRATED",
                citation="Price anchoring maps directly to anchoring technique in purchase context",
                domain="ecommerce",
            ),
            "ecom.reciprocity_approach_bonus": DomainWeight(
                name="ecom.reciprocity_approach_bonus",
                value=0.25,
                provenance="UNCALIBRATED",
                citation="Free trials/samples produce strongest approach activation in e-commerce",
                domain="ecommerce",
            ),
            "ecom.urgency_temporal_multiplier": DomainWeight(
                name="ecom.urgency_temporal_multiplier",
                value=1.6,
                provenance="UNCALIBRATED",
                citation="Countdown timers drive cart completion — temporal_proximity shift amplified",
                domain="ecommerce",
            ),
            "ecom.false_scarcity_insula_multiplier": DomainWeight(
                name="ecom.false_scarcity_insula_multiplier",
                value=1.3,
                provenance="UNCALIBRATED",
                citation="Savvy shoppers detect artificial scarcity — insula amplified",
                domain="ecommerce",
            ),
        }

        technique_overrides = {
            "scarcity_appeal": {
                "circuit_mods_multiplier": {"avoidance": 2.0, "deliberation": 2.0},
                "note": "scarcity drives purchase urgency at 2x universal weight",
            },
            "loss_frame": {
                "appraisal_shift_multiplier": {"valence": 1.5},
                "note": "loss aversion amplified in spending context (Knutson 2007)",
            },
            "anchoring": {
                "circuit_mods_multiplier": {"deliberation": 1.8},
                "note": "price anchoring is dominant in purchase decisions",
            },
            "reciprocity": {
                "approach_bonus": 0.25,
                "note": "free trials/samples = strongest approach activation",
            },
            "urgency_appeal": {
                "appraisal_shift_multiplier": {"temporal_proximity": 1.6},
                "note": "countdown timers drive cart completion",
            },
            "false_scarcity": {
                "insula_multiplier": 1.3,
                "note": "savvy shoppers detect artificial scarcity",
            },
            "false_urgency": {
                "insula_multiplier": 1.3,
                "note": "artificial urgency triggers insula in experienced shoppers",
            },
            "social_proof": {
                "extraversion_interaction_multiplier": 1.4,
                "note": "social shopping amplification for high-extraversion",
            },
        }

        return cls(
            domain="ecommerce",
            weights=weights,
            technique_overrides=technique_overrides,
            domain_outcomes=["purchase_probability", "cart_add_probability",
                             "return_probability", "review_sentiment_predicted"],
        )

    @classmethod
    def campaign(cls) -> DomainWeightRegistry:
        """Campaign messaging registry — optimizes for belief_shift, vote_intention_shift.

        Key differences:
            - moral_reframing: highest-weight technique (Feinberg & Willer 2015)
            - authority_citation: depends on recipient's authority_subversion MF score
            - in-group signaling: loyalty_betrayal x flag_waving dominates
            - fear_appeal: diminishing returns (habituation model)
            - emotional_narrative: emotionality_weight *= 1.6
            - logical_appeal: weight *= 0.7 (weaker for campaign than crisis)
        """
        weights = {
            "campaign.moral_reframing_low_mf_bonus": DomainWeight(
                name="campaign.moral_reframing_low_mf_bonus",
                value=0.3,
                provenance="CONSTRAINED",
                citation="Feinberg & Willer 2015: framing using recipient's LOW moral foundations increases support",
                confidence_interval=(0.2, 0.4),
                domain="campaign",
            ),
            "campaign.moral_reframing_high_mf_bonus": DomainWeight(
                name="campaign.moral_reframing_high_mf_bonus",
                value=0.1,
                provenance="UNCALIBRATED",
                citation="Preaching to choir = weaker effect than reframing",
                domain="campaign",
            ),
            "campaign.authority_high_subversion_multiplier": DomainWeight(
                name="campaign.authority_high_subversion_multiplier",
                value=1.5,
                provenance="UNCALIBRATED",
                citation="High authority_subversion recipients defer to authority citations",
                domain="campaign",
            ),
            "campaign.authority_low_subversion_multiplier": DomainWeight(
                name="campaign.authority_low_subversion_multiplier",
                value=0.6,
                provenance="UNCALIBRATED",
                citation="Low authority_subversion produces reactance to authority appeals",
                domain="campaign",
            ),
            "campaign.authority_low_subversion_insula": DomainWeight(
                name="campaign.authority_low_subversion_insula",
                value=0.15,
                provenance="UNCALIBRATED",
                citation="Authority appeals to low-authority recipients trigger reactance (insula)",
                domain="campaign",
            ),
            "campaign.loyalty_approach_bonus": DomainWeight(
                name="campaign.loyalty_approach_bonus",
                value=0.35,
                provenance="UNCALIBRATED",
                citation="In-group signaling dominates partisan messaging when loyalty_betrayal > 0.6",
                domain="campaign",
            ),
            "campaign.loyalty_social_proof_multiplier": DomainWeight(
                name="campaign.loyalty_social_proof_multiplier",
                value=1.5,
                provenance="UNCALIBRATED",
                citation="Social proof amplified by loyalty foundation in partisan context",
                domain="campaign",
            ),
            "campaign.fear_habituation_rate": DomainWeight(
                name="campaign.fear_habituation_rate",
                value=0.3,
                provenance="UNCALIBRATED",
                citation="Fear appeal diminishing returns: effectiveness = base / (1 + 0.3 * exposure_count)",
                domain="campaign",
            ),
            "campaign.emotional_narrative_multiplier": DomainWeight(
                name="campaign.emotional_narrative_multiplier",
                value=1.6,
                provenance="UNCALIBRATED",
                citation="Emotional narrative is strongest technique for campaign messaging",
                domain="campaign",
            ),
            "campaign.logical_appeal_multiplier": DomainWeight(
                name="campaign.logical_appeal_multiplier",
                value=0.7,
                provenance="UNCALIBRATED",
                citation="Logical appeal weaker for campaign than crisis — emotional resonance dominates",
                domain="campaign",
            ),
        }

        technique_overrides = {
            "emotional_appeal_positive": {
                "emotionality_multiplier": 1.6,
                "note": "emotional narrative strongest for campaign",
            },
            "emotional_appeal_negative": {
                "emotionality_multiplier": 1.6,
                "note": "emotional narrative strongest for campaign",
            },
            "storytelling": {
                "emotionality_multiplier": 1.6,
                "note": "narrative techniques amplified in campaign context",
            },
            "logical_appeal": {
                "circuit_mods_multiplier": {"deliberation": 0.7},
                "note": "logical appeal weaker for campaign than crisis",
            },
            "evidence_based": {
                "circuit_mods_multiplier": {"deliberation": 0.7},
                "note": "evidence-based weaker in campaign context",
            },
        }

        return cls(
            domain="campaign",
            weights=weights,
            technique_overrides=technique_overrides,
            domain_outcomes=["belief_change", "share_amplify_probability",
                             "counter_argue_probability"],
        )

    @classmethod
    def crisis_pr(cls) -> DomainWeightRegistry:
        """Crisis PR registry — optimizes for trust_recovery + counter-narrative suppression.

        Key differences:
            - transparency (self_disclosure + evidence_based): weight *= 2.0
            - defensive techniques (whataboutism, straw_man, red_herring): NEGATIVE effectiveness
            - empathy_appeal: works for customers, produces reactance with regulators
            - logical_appeal + evidence_based: weight *= 1.8 (credibility recovery)
            - response_timing modulator affects trust_recovery
        """
        weights = {
            "crisis.transparency_multiplier": DomainWeight(
                name="crisis.transparency_multiplier",
                value=2.0,
                provenance="UNCALIBRATED",
                citation="Transparency (self_disclosure + evidence_based) is the only path to trust recovery",
                domain="crisis_pr",
            ),
            "crisis.defensive_approach_multiplier": DomainWeight(
                name="crisis.defensive_approach_multiplier",
                value=0.5,
                provenance="UNCALIBRATED",
                citation="Defensive techniques (whataboutism, straw_man, red_herring) produce negative effectiveness",
                domain="crisis_pr",
            ),
            "crisis.defensive_retaliation_bonus": DomainWeight(
                name="crisis.defensive_retaliation_bonus",
                value=0.35,
                provenance="UNCALIBRATED",
                citation="Defensive techniques amplify backlash — retaliation_probability increases",
                domain="crisis_pr",
            ),
            "crisis.empathy_customer_approach_bonus": DomainWeight(
                name="crisis.empathy_customer_approach_bonus",
                value=0.2,
                provenance="UNCALIBRATED",
                citation="Empathy appeal works for customers in crisis context",
                domain="crisis_pr",
            ),
            "crisis.empathy_regulator_insula_bonus": DomainWeight(
                name="crisis.empathy_regulator_insula_bonus",
                value=0.2,
                provenance="UNCALIBRATED",
                citation="Empathy appeal with regulators perceived as deflection — insula activation",
                domain="crisis_pr",
            ),
            "crisis.logical_evidence_multiplier": DomainWeight(
                name="crisis.logical_evidence_multiplier",
                value=1.8,
                provenance="UNCALIBRATED",
                citation="Logical appeal + evidence_based strongest for crisis PR credibility recovery",
                domain="crisis_pr",
            ),
            "crisis.timing_fast_trust_bonus": DomainWeight(
                name="crisis.timing_fast_trust_bonus",
                value=0.15,
                provenance="UNCALIBRATED",
                citation="Response within hours: trust_recovery_bonus = +0.15",
                domain="crisis_pr",
            ),
            "crisis.timing_slow_trust_penalty": DomainWeight(
                name="crisis.timing_slow_trust_penalty",
                value=-0.20,
                provenance="UNCALIBRATED",
                citation="Response after days: trust_penalty = -0.20, avoidance += 0.1",
                domain="crisis_pr",
            ),
            "crisis.timing_very_slow_retaliation": DomainWeight(
                name="crisis.timing_very_slow_retaliation",
                value=0.25,
                provenance="UNCALIBRATED",
                citation="Response after weeks: retaliation_probability += 0.25",
                domain="crisis_pr",
            ),
        }

        technique_overrides = {
            "self_disclosure": {
                "circuit_mods_multiplier": {"approach": 2.0},
                "insula_multiplier": 0.5,
                "note": "transparency is the path to trust recovery in crisis",
            },
            "evidence_based": {
                "circuit_mods_multiplier": {"deliberation": 1.8},
                "note": "evidence + logic strongest for credibility recovery",
            },
            "logical_appeal": {
                "circuit_mods_multiplier": {"deliberation": 1.8},
                "note": "logical appeal strongest in crisis context",
            },
            "whataboutism": {
                "approach_multiplier": 0.5,
                "retaliation_bonus": 0.35,
                "note": "defensive technique — amplifies backlash",
            },
            "straw_man": {
                "approach_multiplier": 0.5,
                "retaliation_bonus": 0.35,
                "note": "defensive technique — amplifies backlash",
            },
            "red_herring": {
                "approach_multiplier": 0.5,
                "retaliation_bonus": 0.35,
                "note": "defensive technique — amplifies backlash",
            },
            "empathy_appeal": {
                "stakeholder_dependent": True,
                "customer_approach_bonus": 0.2,
                "regulator_insula_bonus": 0.2,
                "note": "works for customers, produces reactance with regulators",
            },
        }

        return cls(
            domain="crisis_pr",
            weights=weights,
            technique_overrides=technique_overrides,
            domain_outcomes=["trust_recovery", "counter_narrative_suppression",
                             "brand_sentiment_shift"],
        )
