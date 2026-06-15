from __future__ import annotations
"""
Domain Predictor — Domain-Aware Persuasion Prediction
=======================================================
Wraps CircuitPredictor with domain-specific weight loading.
Returns standard circuit scores PLUS domain-specific outcome metrics.

Usage:
    dp = DomainPredictor()
    result = dp.predict("Buy now! 50% off!", domain="ecommerce")
    result = dp.predict(msg, domain="campaign", exposure_count=3, recipient=profile)
    result = dp.predict(stmt, domain="crisis_pr", crisis_severity=0.8,
                        response_timing=0.1, stakeholder_type="media")
"""

import math
from dataclasses import dataclass, field
from typing import Optional

from core.appraisal_extractor import AppraisalExtractor, AppraisalScores
from core.circuit_predictor import CircuitPredictor, CircuitActivations, BehavioralPrediction
from core.technique_detector import TechniqueDetector
from core.technique_to_circuit import TechniqueCircuitMapper, TECHNIQUE_MODIFIERS
from core.recipient_profile import RecipientProfile
from core.recipient_modulator import RecipientModulator
from core.domain_registry import DomainWeightRegistry, STAKEHOLDER_PROFILES


@dataclass
class DomainPrediction:
    """Full prediction with domain-specific outcomes."""
    # Standard circuit scores (always present)
    approach: float = 0.0
    avoidance: float = 0.0
    deliberation: float = 0.0
    immediate_compliance: float = 0.0
    repeat_compliance: float = 0.0
    retaliation_probability: float = 0.0
    insula_activation: float = 0.0

    # Domain-specific outcomes
    domain_outcomes: dict = field(default_factory=dict)

    # Meta
    domain: str = "universal"
    weights_used: str = "universal"
    provenance_summary: dict = field(default_factory=dict)

    # Full prediction object
    prediction: Optional[BehavioralPrediction] = None

    def to_dict(self) -> dict:
        return {
            "approach": self.approach,
            "avoidance": self.avoidance,
            "deliberation": self.deliberation,
            "immediate_compliance": self.immediate_compliance,
            "repeat_compliance": self.repeat_compliance,
            "retaliation_probability": self.retaliation_probability,
            "insula_activation": self.insula_activation,
            "domain_outcomes": self.domain_outcomes,
            "domain": self.domain,
            "weights_used": self.weights_used,
            "provenance_summary": self.provenance_summary,
        }


class DomainPredictor:
    """Wraps CircuitPredictor with domain-specific weight loading.

    Applies domain-specific technique modifier overrides and computes
    domain-specific outcome metrics alongside standard circuit scores.
    """

    def __init__(self, extraction_mode="heuristic"):
        self.extractor = AppraisalExtractor()
        self.technique_detector = TechniqueDetector()
        self.technique_mapper = TechniqueCircuitMapper()
        self.predictor = CircuitPredictor()
        self.modulator = RecipientModulator()
        self.extraction_mode = extraction_mode

        # Pre-build registries
        self._registries = {
            "universal": DomainWeightRegistry.universal(),
            "ecommerce": DomainWeightRegistry.ecommerce(),
            "campaign": DomainWeightRegistry.campaign(),
            "crisis_pr": DomainWeightRegistry.crisis_pr(),
        }

    def predict(
        self,
        stimulus: str,
        domain: str = "universal",
        recipient: Optional[RecipientProfile] = None,
        # Campaign-specific
        exposure_count: int = 0,
        # Crisis PR-specific
        crisis_severity: float = 0.5,
        response_timing: float = 0.5,
        stakeholder_type: Optional[str] = None,
    ) -> DomainPrediction:
        """Run domain-aware prediction pipeline.

        Args:
            stimulus: text to analyze
            domain: "universal", "ecommerce", "campaign", "crisis_pr"
            recipient: optional RecipientProfile for individual-difference modulation
            exposure_count: (campaign) how many times audience has seen similar fear appeals
            crisis_severity: (crisis_pr) 0.0-1.0
            response_timing: (crisis_pr) 0.0=instant, 1.0=delayed weeks
            stakeholder_type: (crisis_pr) "media", "regulators", "customers", "employees", "investors"
        """
        registry = self._registries.get(domain, self._registries["universal"])

        # Step 1: Extract appraisals
        appraisal = self.extractor.extract(stimulus, mode=self.extraction_mode)

        # Step 2: Detect techniques
        techniques = self.technique_detector.detect(stimulus, mode="heuristic")

        # Step 3: Apply technique modifiers (universal baseline)
        modified_appraisal_dict, insula_signal, circuit_mults = self.technique_mapper.apply(
            appraisal.to_dict(), techniques, 0.0
        )

        # Step 4: Apply domain-specific technique overrides
        insula_signal, circuit_mults, approach_bonus, retaliation_bonus = self._apply_domain_overrides(
            domain, registry, techniques, modified_appraisal_dict,
            insula_signal, circuit_mults, recipient,
            exposure_count=exposure_count,
            stakeholder_type=stakeholder_type,
        )

        # Step 5: Apply recipient modulation if provided
        # For crisis_pr, auto-load stakeholder profile if no explicit recipient
        effective_recipient = recipient
        if effective_recipient is None and domain == "crisis_pr" and stakeholder_type:
            effective_recipient = self._build_stakeholder_recipient(stakeholder_type)

        if effective_recipient is not None:
            modified_appraisal_dict, insula_signal, recipient_mults, _ = self.modulator.modulate(
                profile=effective_recipient,
                appraisal_dict=modified_appraisal_dict,
                insula_signal=insula_signal,
                circuit_multipliers=circuit_mults,
                detected_techniques=techniques.detected_names,
            )
            # Merge recipient multipliers
            for k in circuit_mults:
                circuit_mults[k] *= recipient_mults.get(k, 1.0)

        # Step 6: Compute circuits
        effective_appraisal = AppraisalScores(**modified_appraisal_dict)
        approach = self.predictor.compute_approach(effective_appraisal)
        avoidance = self.predictor.compute_avoidance(effective_appraisal, insula_signal)
        deliberation = self.predictor.compute_deliberation(effective_appraisal, approach, avoidance)

        # Apply multipliers
        approach = round(max(0.0, approach * circuit_mults.get("approach", 1.0)), 4)
        avoidance = round(max(0.0, avoidance * circuit_mults.get("avoidance", 1.0)), 4)
        deliberation = round(max(0.0, deliberation * circuit_mults.get("deliberation", 1.0)), 4)

        # Apply approach bonus from domain overrides (e.g., reciprocity in ecommerce)
        approach = round(max(0.0, approach + approach_bonus), 4)

        circuits = CircuitActivations(approach=approach, avoidance=avoidance, deliberation=deliberation)

        # Step 7: Compute behavioral prediction using standard formulas
        raw_scores = [approach, -avoidance, -deliberation]
        max_s = max(raw_scores)
        exp_scores = [math.exp(s - max_s) for s in raw_scores]
        total = sum(exp_scores)
        compliance_prob = round(exp_scores[0] / total, 4)

        # Standard time horizons
        immediate_compliance = compliance_prob
        durability = round(
            effective_appraisal.certainty * effective_appraisal.valence
            - effective_appraisal.temporal_proximity * (1.0 - effective_appraisal.certainty),
            4,
        )
        agency_penalty = max(0.0, 0.5 - effective_appraisal.agency) * 0.8
        disgust_penalty = insula_signal * 0.5
        repeat_base = immediate_compliance * max(0.0, (durability + 1.0) / 2.0)
        repeat_compliance = round(max(0.0, min(1.0,
            repeat_base - agency_penalty - disgust_penalty
        )), 4)

        retaliation = round(max(0.0, min(1.0,
            0.4 * avoidance * (1.0 - effective_appraisal.agency)
            + 0.3 * insula_signal * (1.0 - effective_appraisal.agency)
            + 0.2 * max(0.0, 0.3 - effective_appraisal.agency)
            - 0.3 * effective_appraisal.valence
            + retaliation_bonus
        )), 4)

        # Step 8: Compute domain-specific outcomes
        domain_outcomes = self._compute_domain_outcomes(
            domain, circuits, effective_appraisal, insula_signal,
            immediate_compliance, repeat_compliance, retaliation,
            durability, crisis_severity, response_timing, stakeholder_type,
        )

        return DomainPrediction(
            approach=approach,
            avoidance=avoidance,
            deliberation=deliberation,
            immediate_compliance=immediate_compliance,
            repeat_compliance=repeat_compliance,
            retaliation_probability=retaliation,
            insula_activation=round(min(1.0, max(0.0, insula_signal)), 4),
            domain_outcomes=domain_outcomes,
            domain=domain,
            weights_used=domain,
            provenance_summary=registry.provenance_summary(),
        )

    def _apply_domain_overrides(
        self, domain, registry, techniques, appraisal_dict,
        insula_signal, circuit_mults, recipient,
        exposure_count=0, stakeholder_type=None,
    ):
        """Apply domain-specific technique modifier overrides."""
        approach_bonus = 0.0
        retaliation_bonus = 0.0

        if domain == "ecommerce":
            for tech_name in techniques.detected_names:
                override = registry.get_technique_override(tech_name)
                if not override:
                    continue

                # Circuit modifier multipliers (e.g., scarcity *= 2.0)
                for circuit, mult in override.get("circuit_mods_multiplier", {}).items():
                    circuit_mults[circuit] *= mult

                # Appraisal shift multipliers (e.g., loss_frame valence *= 1.5)
                for dim, mult in override.get("appraisal_shift_multiplier", {}).items():
                    base_shift = TECHNIQUE_MODIFIERS.get(tech_name, {}).get("appraisal_shifts", {}).get(dim, 0)
                    extra = base_shift * (mult - 1.0)
                    if dim in appraisal_dict:
                        appraisal_dict[dim] = round(min(1.0, max(0.0, appraisal_dict[dim] + extra)), 3)

                # Approach bonus (e.g., reciprocity += 0.25)
                approach_bonus += override.get("approach_bonus", 0.0)

                # Insula multiplier (e.g., false_scarcity *= 1.3)
                insula_mult = override.get("insula_multiplier", 1.0)
                if insula_mult != 1.0:
                    insula_signal *= insula_mult

                # Social proof x extraversion interaction
                if override.get("extraversion_interaction_multiplier") and recipient:
                    if recipient.extraversion > 0.7:
                        circuit_mults["approach"] *= override["extraversion_interaction_multiplier"]

            # E-commerce baseline: scarcity/urgency/anchoring contexts boost approach
            scarcity_urgency = {"scarcity_appeal", "urgency_appeal", "false_scarcity",
                                "false_urgency", "loss_frame", "anchoring"}
            active_purchase_drivers = scarcity_urgency.intersection(set(techniques.detected_names))
            if active_purchase_drivers:
                # Each active purchase driver adds approach boost
                approach_bonus += len(active_purchase_drivers) * 0.15
                # Urgency suppresses deliberation further in purchase context
                circuit_mults["deliberation"] *= 0.75

        elif domain == "campaign":
            for tech_name in techniques.detected_names:
                override = registry.get_technique_override(tech_name)
                if override:
                    for circuit, mult in override.get("circuit_mods_multiplier", {}).items():
                        circuit_mults[circuit] *= mult
                    emot_mult = override.get("emotionality_multiplier", 1.0)
                    if emot_mult != 1.0:
                        # Amplify the emotional impact — boost valence shift
                        if "valence" in appraisal_dict:
                            shift = (appraisal_dict["valence"] - 0.5) * (emot_mult - 1.0)
                            appraisal_dict["valence"] = round(min(1.0, max(0.0,
                                appraisal_dict["valence"] + shift)), 3)

            # Moral reframing (Feinberg & Willer 2015)
            if recipient:
                mft_scores = {
                    "care_harm": recipient.care_harm,
                    "fairness_cheating": recipient.fairness_cheating,
                    "loyalty_betrayal": recipient.loyalty_betrayal,
                    "authority_subversion": recipient.authority_subversion,
                    "sanctity_degradation": recipient.sanctity_degradation,
                    "liberty_oppression": recipient.liberty_oppression,
                }
                low_mf = [k for k, v in mft_scores.items() if v < 0.4]
                high_mf = [k for k, v in mft_scores.items() if v > 0.6]

                # Check if stimulus invokes any moral foundations
                # (proxy: check if any MFT-related techniques are detected)
                mft_techniques = {"empathy_appeal", "emotional_appeal_negative",
                                  "emotional_appeal_positive", "storytelling",
                                  "authority_endorsement", "bandwagon"}
                invokes_mft = any(t in techniques.detected_names for t in mft_techniques)

                if invokes_mft:
                    if low_mf:
                        approach_bonus += 0.3  # reframing using LOW foundations = stronger
                    elif high_mf:
                        approach_bonus += 0.1  # preaching to choir = weaker

                # Authority citation depends on recipient's authority_subversion
                if any(t in techniques.detected_names for t in ["authority_endorsement", "expert_testimony"]):
                    if recipient.authority_subversion > 0.6:
                        circuit_mults["approach"] *= 1.5
                    elif recipient.authority_subversion < 0.4:
                        circuit_mults["approach"] *= 0.6
                        insula_signal += 0.15

                # In-group signaling: loyalty_betrayal > 0.6
                if recipient.loyalty_betrayal > 0.6:
                    if any(t in techniques.detected_names for t in ["bandwagon", "social_proof", "authority_endorsement"]):
                        approach_bonus += 0.35
                        circuit_mults["approach"] *= 1.5

            # Fear appeal habituation
            if "fear_mongering" in techniques.detected_names and exposure_count > 0:
                habituation = 1.0 / (1.0 + 0.3 * exposure_count)
                # Reduce the fear effect
                circuit_mults["avoidance"] *= habituation

        elif domain == "crisis_pr":
            for tech_name in techniques.detected_names:
                override = registry.get_technique_override(tech_name)
                if not override:
                    continue

                # Transparency techniques amplified
                for circuit, mult in override.get("circuit_mods_multiplier", {}).items():
                    circuit_mults[circuit] *= mult

                # Insula multiplier for transparency
                insula_mult = override.get("insula_multiplier", 1.0)
                if insula_mult != 1.0:
                    insula_signal *= insula_mult

                # Defensive techniques: negative effectiveness
                approach_mult = override.get("approach_multiplier", 1.0)
                if approach_mult != 1.0:
                    circuit_mults["approach"] *= approach_mult

                retaliation_bonus += override.get("retaliation_bonus", 0.0)

                # Stakeholder-dependent techniques (empathy_appeal)
                if override.get("stakeholder_dependent") and stakeholder_type:
                    if stakeholder_type == "customers":
                        approach_bonus += override.get("customer_approach_bonus", 0.0)
                    elif stakeholder_type == "regulators":
                        insula_signal += override.get("regulator_insula_bonus", 0.0)

        return insula_signal, circuit_mults, approach_bonus, retaliation_bonus

    def _build_stakeholder_recipient(self, stakeholder_type: str) -> RecipientProfile:
        """Build a RecipientProfile from stakeholder type defaults."""
        overrides = STAKEHOLDER_PROFILES.get(stakeholder_type, {})
        return RecipientProfile(**overrides)

    def _compute_domain_outcomes(
        self, domain, circuits, appraisal, insula_signal,
        immediate_compliance, repeat_compliance, retaliation,
        durability, crisis_severity, response_timing, stakeholder_type,
    ) -> dict:
        """Compute domain-specific behavioral outcome metrics."""

        if domain == "ecommerce":
            # Purchase probability: approach-dominant, certainty-modulated
            purchase_prob = round(min(1.0, max(0.0,
                immediate_compliance * 0.7
                + appraisal.certainty * 0.15
                + appraisal.coping_potential * 0.15
                - insula_signal * 0.2
            )), 4)

            # Cart add probability: slightly easier than purchase
            cart_add_prob = round(min(1.0, max(0.0,
                purchase_prob * 1.15 + 0.05
            )), 4)

            # Return probability: inverse of durability
            return_prob = round(min(1.0, max(0.0,
                0.3 - durability * 0.25
                + insula_signal * 0.2
                + max(0.0, 0.5 - appraisal.agency) * 0.3
            )), 4)

            # Review sentiment: positive valence + agency → positive reviews
            review_sentiment = round(min(1.0, max(0.0,
                appraisal.valence * 0.4
                + appraisal.agency * 0.3
                + appraisal.certainty * 0.2
                - insula_signal * 0.3
            )), 4)

            return {
                "purchase_probability": purchase_prob,
                "cart_add_probability": cart_add_prob,
                "return_probability": return_prob,
                "review_sentiment_predicted": review_sentiment,
            }

        elif domain == "campaign":
            # Belief change: approach - avoidance, modulated by deliberation
            belief_change = round(min(1.0, max(0.0,
                circuits.approach * 0.4
                - circuits.avoidance * 0.2
                + appraisal.goal_relevance * 0.2
                + appraisal.certainty * 0.1
                - circuits.deliberation * 0.1
            )), 4)

            # Share/amplify probability: emotional + relevant = viral
            share_prob = round(min(1.0, max(0.0,
                abs(appraisal.valence - 0.5) * 0.4  # emotional intensity
                + appraisal.goal_relevance * 0.3
                + (1.0 - appraisal.certainty) * 0.1  # controversy amplifies sharing
                + immediate_compliance * 0.2
            )), 4)

            # Counter-argue probability: high deliberation + low approach
            counter_argue = round(min(1.0, max(0.0,
                circuits.deliberation * 0.4
                + (1.0 - circuits.approach) * 0.2
                + insula_signal * 0.2
                + (1.0 - appraisal.valence) * 0.1
            )), 4)

            return {
                "belief_change": belief_change,
                "share_amplify_probability": share_prob,
                "counter_argue_probability": counter_argue,
            }

        elif domain == "crisis_pr":
            # Trust recovery: transparency + timing + stakeholder match
            trust_base = round(min(1.0, max(0.0,
                circuits.approach * 0.3
                + appraisal.certainty * 0.2
                + appraisal.agency * 0.15
                - circuits.avoidance * 0.15
                - insula_signal * 0.2
            )), 4)

            # Apply timing modulator
            timing_mod = 0.0
            if response_timing < 0.2:
                timing_mod = 0.15
            elif response_timing > 0.5:
                timing_mod = -0.20
            trust_recovery = round(min(1.0, max(0.0, trust_base + timing_mod)), 4)

            # Timing affects avoidance and retaliation too
            if response_timing > 0.5:
                # Already factored into retaliation via the main predict() loop
                pass

            # Counter-narrative suppression: high approach + low avoidance
            counter_narrative = round(min(1.0, max(0.0,
                circuits.approach * 0.35
                - circuits.avoidance * 0.25
                + appraisal.certainty * 0.2
                + appraisal.coping_potential * 0.1
                - retaliation * 0.15
            )), 4)

            # Brand sentiment shift: net positive movement
            brand_sentiment = round(min(1.0, max(-1.0,
                trust_recovery * 0.4
                + appraisal.valence * 0.2
                - retaliation * 0.3
                - crisis_severity * 0.1
            )), 4)

            return {
                "trust_recovery": trust_recovery,
                "counter_narrative_suppression": counter_narrative,
                "brand_sentiment_shift": brand_sentiment,
            }

        # Universal: no domain-specific outcomes
        return {}
