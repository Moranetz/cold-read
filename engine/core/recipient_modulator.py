from __future__ import annotations
"""
Recipient Modulator — Trait-Specific Weight Modulation
=======================================================
Takes a RecipientProfile + raw circuit computation parameters
and applies individual-difference modulations BEFORE circuit
computation. The same stimulus produces different circuit scores
for different recipients.

Each modulation is documented with literature citation or marked
UNCALIBRATED where the direction is from theory but the magnitude
is interpolated.

Integration point:
    stimulus → extract_appraisals → detect_techniques → apply_technique_modifiers
    → APPLY_RECIPIENT_MODULATION → compute_circuits → predict_behavior
"""

from dataclasses import dataclass, field
from typing import Optional

from core.recipient_profile import RecipientProfile


@dataclass
class ModulationResult:
    """Output of recipient modulation — modified weights and signals."""
    circuit_multipliers: dict = field(default_factory=lambda: {
        "approach": 1.0, "avoidance": 1.0, "deliberation": 1.0,
    })
    appraisal_shifts: dict = field(default_factory=dict)
    insula_mod: float = 0.0
    modulations_applied: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "circuit_multipliers": self.circuit_multipliers,
            "appraisal_shifts": self.appraisal_shifts,
            "insula_mod": self.insula_mod,
            "modulations_applied": self.modulations_applied,
        }


class RecipientModulator:
    """Apply recipient-profile modulations to circuit computation parameters.

    Does NOT compute circuits itself — returns modulated parameters that
    CircuitPredictor uses. This keeps the circuit formulas unchanged and
    adds recipient modulation as a separate, testable layer.
    """

    def modulate(
        self,
        profile: RecipientProfile,
        appraisal_dict: dict,
        insula_signal: float = 0.0,
        circuit_multipliers: Optional[dict] = None,
        detected_techniques: Optional[list] = None,
    ) -> tuple:
        """Apply all trait modulations.

        Args:
            profile: RecipientProfile with 16 dimensions
            appraisal_dict: dict of 7 appraisal scores (modified in-place copy)
            insula_signal: current insula disgust signal
            circuit_multipliers: current circuit multipliers (from technique mapper)
            detected_techniques: list of detected technique names (for technique-specific modulation)

        Returns:
            (modified_appraisal_dict, modified_insula, modified_circuit_multipliers, modulations_applied)
        """
        modified = dict(appraisal_dict)
        mults = dict(circuit_multipliers or {"approach": 1.0, "avoidance": 1.0, "deliberation": 1.0})
        insula = insula_signal
        techniques = detected_techniques or []
        applied = []

        # ═══════════════════════════════════════════════════════════════════
        # BIG FIVE MODULATIONS
        # ═══════════════════════════════════════════════════════════════════

        # HIGH NEUROTICISM (>0.7): heightened emotional reactivity
        if profile.neuroticism > 0.7:
            # Eysenck 1967: neurotic individuals show heightened amygdala
            # reactivity to ambiguous stimuli.
            # Neuroticism manifests differently depending on context:
            # - In urgency/scarcity contexts → FOMO (approach via anxiety)
            # - In threat/fear contexts → amplified avoidance
            has_urgency = any(t in techniques for t in [
                "urgency_appeal", "false_urgency", "scarcity_appeal",
                "false_scarcity", "loss_frame",
            ])
            has_threat = any(t in techniques for t in [
                "fear_mongering", "emotional_manipulation", "guilt_tripping",
            ])
            if has_urgency and not has_threat:
                # FOMO pathway: anxiety drives impulsive approach (Vohs & Faber 2007)
                mults["approach"] *= 1.3  # UNCALIBRATED: FOMO-driven approach
                mults["deliberation"] *= 0.75  # anxiety suppresses deliberation
                applied.append("high_neuroticism+urgency: FOMO approach*1.3, delib*0.75 (Vohs & Faber 2007)")
            else:
                # Threat pathway: heightened avoidance
                mults["avoidance"] *= 1.4  # CONSTRAINED: Eysenck 1967
                modified["valence"] = max(0.0, modified.get("valence", 0.5) - 0.1)
                applied.append("high_neuroticism: avoidance*1.4, valence-0.1 (Eysenck 1967)")

        # HIGH AGREEABLENESS (>0.7): elevated baseline compliance
        if profile.agreeableness > 0.7:
            # Graziano et al. 1996: agreeableness correlates with compliance
            # in social influence paradigms. Higher default approach.
            mults["approach"] *= 1.15  # CONSTRAINED: Graziano 1996
            # Reciprocity sensitivity — agreeable individuals feel stronger
            # obligation to reciprocate (Perugini et al. 2003)
            if "reciprocity" in techniques:
                mults["approach"] *= 1.15  # 1.3 total for reciprocity
            # Lower retaliation — agreeable individuals are less likely to
            # engage in active counterbehavior
            mults["avoidance"] *= 0.85  # UNCALIBRATED: reduced retaliation probability
            applied.append("high_agreeableness: approach*1.15, avoidance*0.85 (Graziano 1996)")

        # HIGH OPENNESS (>0.7): novelty-seeking, ambiguity tolerance
        if profile.openness > 0.7:
            # McCrae 1987: openness correlates with curiosity and tolerance
            # for ambiguity. Novel stimuli excite rather than threaten.
            if modified.get("novelty", 0.5) > 0.5:
                mults["approach"] *= 1.2  # UNCALIBRATED: novelty = exciting not threatening
            # Comfortable with ambiguity — certainty matters less
            modified["certainty"] = min(1.0, modified.get("certainty", 0.5) + 0.1)  # UNCALIBRATED
            applied.append("high_openness: novelty->approach*1.2, certainty+0.1 (McCrae 1987)")

        # LOW CONSCIENTIOUSNESS (<0.3): reduced systematic processing
        if profile.conscientiousness < 0.3:
            # Petty & Cacioppo 1986 (ELM): low need-for-cognition correlates
            # with peripheral route processing. Less systematic evaluation.
            mults["deliberation"] *= 0.6  # CONSTRAINED: ELM peripheral route
            # Higher impulse propensity — approach gains relative to deliberation
            mults["approach"] *= 1.2  # UNCALIBRATED: impulse propensity
            applied.append("low_conscientiousness: deliberation*0.6, approach*1.2 (ELM)")

        # HIGH EXTRAVERSION (>0.7): social influence susceptibility
        if profile.extraversion > 0.7:
            # Eysenck 1967 + social influence: extraverts are more responsive
            # to social cues. Social proof and bandwagon effects amplified.
            social_techniques = ["social_proof", "bandwagon", "bandwagon_pressure"]
            if any(t in techniques for t in social_techniques):
                mults["approach"] *= 1.4  # CONSTRAINED: social influence amplification
                mults["deliberation"] *= 0.75  # social cues bypass deliberation
            else:
                mults["approach"] *= 1.15  # baseline social orientation boost
            applied.append("high_extraversion: social_proof amplified (Eysenck 1967)")

        # ═══════════════════════════════════════════════════════════════════
        # MORAL FOUNDATIONS MODULATIONS (Haidt & Graham 2007)
        # ═══════════════════════════════════════════════════════════════════

        # HIGH CARE/HARM (>0.7): empathy-driven processing
        if profile.care_harm > 0.7:
            # Haidt 2001: care foundation drives empathic concern. Emotional
            # narratives and appeals to suffering are more persuasive.
            emotional_techniques = [
                "emotional_appeal_negative", "empathy_appeal", "storytelling",
                "emotional_appeal_positive", "emotional_manipulation",
                "appeal_to_pity", "guilt_tripping",
            ]
            has_emotional = any(t in techniques for t in emotional_techniques)
            if has_emotional:
                mults["approach"] *= 1.35  # UNCALIBRATED: empathy amplifies engagement
                modified["goal_relevance"] = min(1.0, modified.get("goal_relevance", 0.5) + 0.15)
                mults["deliberation"] *= 0.85  # empathic engagement bypasses some deliberation
            applied.append("high_care_harm: emotional narrative amplified (Haidt 2001)")

        # HIGH LOYALTY/BETRAYAL (>0.7): tribal signaling sensitivity
        if profile.loyalty_betrayal > 0.7:
            # Haidt & Graham 2007: loyalty foundation drives ingroup bias.
            # Tribal appeals and authority signals amplified.
            if "bandwagon" in techniques or "social_proof" in techniques or "bandwagon_pressure" in techniques:
                mults["approach"] *= 1.3  # UNCALIBRATED: ingroup signal amplification
            if "authority_endorsement" in techniques or "expert_testimony" in techniques:
                mults["approach"] *= 1.1  # authority as ingroup leader
                mults["deliberation"] *= 0.9
            applied.append("high_loyalty_betrayal: ingroup/authority amplified (Haidt & Graham 2007)")

        # HIGH AUTHORITY/SUBVERSION (>0.7): deference to expertise
        if profile.authority_subversion > 0.7:
            # Milgram 1963: authority sensitivity varies by individual.
            # High-authority individuals defer more to expert testimony.
            if "expert_testimony" in techniques or "authority_endorsement" in techniques:
                mults["approach"] *= 1.15  # CONSTRAINED: authority citation more persuasive
                mults["deliberation"] *= 0.85  # UNCALIBRATED: authority = don't question
            applied.append("high_authority_subversion: authority citation*1.15 (Milgram 1963)")

        # HIGH SANCTITY/DEGRADATION (>0.7): disgust sensitivity
        if profile.sanctity_degradation > 0.7:
            # Inbar et al. 2009: sanctity foundation correlates with disgust
            # sensitivity. Lower threshold for insula activation.
            insula *= 1.4  # UNCALIBRATED: lower threshold for insula activation
            applied.append("high_sanctity_degradation: insula*1.4 (Inbar 2009)")

        # HIGH LIBERTY/OPPRESSION (>0.7): reactance to coercion
        if profile.liberty_oppression > 0.7:
            # Brehm 1966 (Reactance Theory): individuals high on liberty
            # foundation show amplified reactance to perceived coercion.
            if "false_urgency" in techniques or "false_scarcity" in techniques:
                mults["avoidance"] *= 1.5  # UNCALIBRATED: reactance amplified
                insula += 0.15  # coercion detection
            # General agency sensitivity — low agency triggers stronger avoidance
            agency_val = modified.get("agency", 0.5)
            if agency_val < 0.4:
                mults["avoidance"] *= 1.2  # UNCALIBRATED: agency sensitivity
            applied.append("high_liberty_oppression: coercion reactance amplified (Brehm 1966)")

        # ═══════════════════════════════════════════════════════════════════
        # POLITICAL MODULATIONS (Graham et al. 2009)
        # ═══════════════════════════════════════════════════════════════════

        # CONSERVATIVE PROFILE (economic > 0.3 AND social > 0.3)
        if profile.economic_ideology > 0.3 and profile.social_ideology > 0.3:
            # Graham et al. 2009: conservatives weight all 5 foundations more
            # equally, with particular emphasis on loyalty/authority/sanctity.
            if "loyalty_betrayal" in techniques or "bandwagon" in techniques:
                mults["approach"] *= 1.1  # CONSTRAINED: Graham 2009
            if "authority_endorsement" in techniques or "expert_testimony" in techniques:
                mults["approach"] *= 1.1
            insula *= 1.1  # higher sanctity sensitivity
            applied.append("conservative_profile: loyalty/authority/sanctity amplified (Graham 2009)")

        # LIBERAL PROFILE (economic < -0.3 AND social < -0.3)
        if profile.economic_ideology < -0.3 and profile.social_ideology < -0.3:
            # Graham et al. 2009: liberals weight care and fairness more heavily.
            care_techniques = [
                "empathy_appeal", "emotional_appeal_negative", "emotional_manipulation",
                "appeal_to_pity", "storytelling", "emotional_appeal_positive",
            ]
            if any(t in techniques for t in care_techniques):
                mults["approach"] *= 1.25  # CONSTRAINED: care/fairness emphasis
            if modified.get("agency", 0.5) > 0.6:
                mults["approach"] *= 1.1  # liberty emphasis
            applied.append("liberal_profile: care/fairness amplified (Graham 2009)")

        # ═══════════════════════════════════════════════════════════════════
        # ELABORATION LIKELIHOOD MODULATION (Petty & Cacioppo 1986)
        # ═══════════════════════════════════════════════════════════════════

        el = profile.elaboration_likelihood

        # HIGH EL (>0.7): central route processing
        if el > 0.7:
            # Petty & Cacioppo 1986: high elaboration = central route.
            # Baseline: more deliberation, less impulsive approach
            mults["deliberation"] *= 1.25  # CONSTRAINED: central route baseline
            mults["approach"] *= 0.9  # UNCALIBRATED: less impulsive
            # Logical appeals gain weight
            if "logical_appeal" in techniques or "evidence_based" in techniques:
                mults["approach"] *= 1.2  # CONSTRAINED: central route processing
            # Peripheral cues discounted (social proof, urgency, emotion)
            peripheral = ["social_proof", "bandwagon", "urgency_appeal",
                          "false_urgency", "emotional_appeal_positive",
                          "emotional_appeal_negative", "bandwagon_pressure"]
            if any(t in techniques for t in peripheral):
                mults["approach"] *= 0.8  # CONSTRAINED: peripheral cues discounted
            # Weak arguments penalized
            fallacies = ["false_equivalence", "straw_man", "slippery_slope",
                         "false_dilemma", "ad_hominem", "false_scarcity"]
            if any(t in techniques for t in fallacies):
                mults["avoidance"] *= 1.3  # UNCALIBRATED: flawed logic caught
                insula += 0.1
            applied.append("high_EL: central route, deliberation*1.25, peripheral discounted (ELM)")

        # LOW EL (<0.3): peripheral route processing
        if el < 0.3:
            # Petty & Cacioppo 1986: low elaboration = peripheral route.
            # Baseline: less deliberation, more peripheral cue sensitivity
            mults["deliberation"] *= 0.7  # CONSTRAINED: peripheral route baseline
            mults["approach"] *= 1.1  # UNCALIBRATED: more impulsive
            # Peripheral cues amplified
            peripheral_present = ["social_proof", "bandwagon", "bandwagon_pressure",
                                  "urgency_appeal", "false_urgency"]
            if any(t in techniques for t in peripheral_present):
                mults["approach"] *= 1.25  # CONSTRAINED: peripheral cues dominate
            if "expert_testimony" in techniques or "authority_endorsement" in techniques:
                mults["approach"] *= 1.15
            # Complex arguments skipped
            if "logical_appeal" in techniques or "evidence_based" in techniques:
                mults["deliberation"] *= 0.7  # UNCALIBRATED: complex arguments skipped
            applied.append("low_EL: peripheral route, deliberation*0.7, peripheral amplified (ELM)")

        # ═══════════════════════════════════════════════════════════════════
        # INVOLVEMENT MODULATION
        # ═══════════════════════════════════════════════════════════════════

        # High involvement increases goal relevance and deliberation
        if profile.involvement > 0.7:
            modified["goal_relevance"] = min(1.0, modified.get("goal_relevance", 0.5) + 0.15)
            mults["deliberation"] *= 1.15  # UNCALIBRATED: more careful processing
            applied.append("high_involvement: goal_relevance+0.15, deliberation*1.15")

        # Low involvement reduces attention allocation
        if profile.involvement < 0.3:
            modified["goal_relevance"] = max(0.0, modified.get("goal_relevance", 0.5) - 0.15)
            mults["deliberation"] *= 0.8  # UNCALIBRATED: less careful processing
            applied.append("low_involvement: goal_relevance-0.15, deliberation*0.8")

        # Clamp insula
        insula = round(min(1.0, max(0.0, insula)), 3)

        # Clamp appraisal values
        for k in modified:
            modified[k] = round(min(1.0, max(0.0, modified[k])), 3)

        return modified, insula, mults, applied

    def apply_circuit_multipliers(
        self,
        approach: float,
        avoidance: float,
        deliberation: float,
        multipliers: dict,
    ) -> tuple:
        """Apply accumulated multipliers to raw circuit scores.

        Returns (approach, avoidance, deliberation) after modulation.
        """
        return (
            round(max(0.0, approach * multipliers.get("approach", 1.0)), 4),
            round(max(0.0, avoidance * multipliers.get("avoidance", 1.0)), 4),
            round(max(0.0, deliberation * multipliers.get("deliberation", 1.0)), 4),
        )
