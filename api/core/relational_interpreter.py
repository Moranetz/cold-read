from __future__ import annotations
"""
Relational Interpreter — User-Only Behavioral Translation Layer
===============================================================
Converts mechanical persuasion outputs into private, plain-English
interpretations for the user. This module does NOT generate outbound
messages to send. It only explains the pattern being observed.
"""

from dataclasses import dataclass, asdict
from typing import Optional

from core.appraisal_extractor import AppraisalScores
from core.circuit_predictor import BehavioralPrediction, CircuitActivations


@dataclass
class RelationalInterpretation:
    """Private explanation surface for the user."""

    pattern_label: str
    confidence: str
    signal_present: str
    plain_english_inference: str
    clean_internal_translation: str
    what_this_does_not_prove: str
    guardedness_read: str
    pressure_read: str
    congruence_read: str
    distancing_read: str
    ambiguity_read: str
    next_move: str
    autonomy_protection: str
    tactical_empathy: str
    calibrated_question_posture: str
    response_style: str
    user_only: bool = True
    suggested_outbound_text: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class RelationalInterpreter:
    """Translate behavioral mechanics into concise user-only explanations."""

    def interpret(
        self,
        stimulus: str,
        appraisal: AppraisalScores,
        circuits: CircuitActivations,
        prediction: BehavioralPrediction,
    ) -> RelationalInterpretation:
        pattern_label = self._pattern_label(appraisal, circuits, prediction)
        confidence = self._confidence(circuits)
        signal_present = self._signal_present(pattern_label, appraisal, circuits, prediction)
        plain = self._plain_english(pattern_label, appraisal, prediction)
        translation = self._clean_translation(pattern_label, prediction)
        not_prove = self._what_this_does_not_prove(pattern_label)
        guardedness = self._guardedness_read(appraisal, prediction)
        pressure = self._pressure_read(appraisal, prediction)
        congruence = self._congruence_read(circuits, prediction)
        distancing = self._distancing_read(pattern_label, prediction)
        ambiguity = self._ambiguity_read(pattern_label, appraisal, circuits)
        next_move = self._next_move(pattern_label, appraisal, prediction)
        autonomy = self._autonomy_protection(pattern_label)
        empathy = self._tactical_empathy(pattern_label, appraisal)
        calibrated_question = self._calibrated_question_posture(pattern_label, appraisal, prediction)
        response_style = self._response_style(pattern_label, prediction)

        return RelationalInterpretation(
            pattern_label=pattern_label,
            confidence=confidence,
            signal_present=signal_present,
            plain_english_inference=plain,
            clean_internal_translation=translation,
            what_this_does_not_prove=not_prove,
            guardedness_read=guardedness,
            pressure_read=pressure,
            congruence_read=congruence,
            distancing_read=distancing,
            ambiguity_read=ambiguity,
            next_move=next_move,
            autonomy_protection=autonomy,
            tactical_empathy=empathy,
            calibrated_question_posture=calibrated_question,
            response_style=response_style,
        )

    def _signal_present(
        self,
        pattern_label: str,
        appraisal: AppraisalScores,
        circuits: CircuitActivations,
        prediction: BehavioralPrediction,
    ) -> str:
        if pattern_label == "hostile_or_trapped_dynamic":
            return "pressure and backlash risk are present under the surface"
        if pattern_label == "soft_rejection_or_distancing":
            return "distancing is present, even if the tone stays socially smooth"
        if pattern_label == "ambiguity_or_non-commitment":
            return "ambiguity is present and the signal is not yet behaviorally solid"
        if pattern_label == "short_term_pull_low_durability":
            return "pull is present, but durability is weak"
        if pattern_label == "clear_alignment":
            return "the signal is largely congruent and behaviorally aligned"
        if circuits.conflict_level > 0.55:
            return "mixed signal with internal conflict is present"
        return "partial relevance is present, but the pattern is not clean yet"

    def _pattern_label(
        self,
        appraisal: AppraisalScores,
        circuits: CircuitActivations,
        prediction: BehavioralPrediction,
    ) -> str:
        if prediction.retaliation_probability >= 0.18 and appraisal.agency < 0.3:
            return "hostile_or_trapped_dynamic"
        if prediction.predicted_behavior == "DELAY" or circuits.dominant == "deliberation":
            return "ambiguity_or_non-commitment"
        if prediction.predicted_behavior == "REJECTION" or circuits.dominant == "avoidance":
            return "soft_rejection_or_distancing"
        if prediction.immediate_compliance > prediction.repeat_compliance + 0.12:
            return "short_term_pull_low_durability"
        if prediction.compliance_prob >= 0.55 and prediction.repeat_compliance >= 0.45:
            return "clear_alignment"
        return "mixed_signal_pattern"

    def _confidence(self, circuits: CircuitActivations) -> str:
        if circuits.conflict_level < 0.35:
            return "high"
        if circuits.conflict_level < 0.6:
            return "medium"
        return "low"

    def _plain_english(
        self,
        pattern_label: str,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
    ) -> str:
        if pattern_label == "ambiguity_or_non-commitment":
            return (
                "The pattern points to hesitation, vagueness, or insufficient willingness "
                "to make a concrete move. The issue looks more logistical and motivational "
                "than emotional."
            )
        if pattern_label == "soft_rejection_or_distancing":
            return (
                "The pattern points to withdrawal or distancing. The person may be trying "
                "to keep things pleasant while still reducing closeness or commitment."
            )
        if pattern_label == "short_term_pull_low_durability":
            return (
                "There is enough positive pull for momentary engagement, but the structure "
                "does not look durable. This often shows up as chemistry without reliable follow-through."
            )
        if pattern_label == "hostile_or_trapped_dynamic":
            return (
                "The pattern points to pressure, low agency, and backlash risk. Even if the "
                "surface remains polite, the underlying dynamic is unstable."
            )
        if pattern_label == "clear_alignment":
            return (
                "The pattern points to genuine fit and relatively stable willingness. "
                "What is being signaled looks clearer than performative."
            )
        return (
            "The pattern is mixed. There are signs of interest or relevance, but not enough "
            "clarity to treat the situation as settled."
        )

    def _clean_translation(self, pattern_label: str, prediction: BehavioralPrediction) -> str:
        if pattern_label == "ambiguity_or_non-commitment":
            return "This is not a clarity-rich yes. Unless the behavior sharpens, treat it as non-commitment."
        if pattern_label == "soft_rejection_or_distancing":
            return "This may not be about my worth. It does look like they are creating distance."
        if pattern_label == "short_term_pull_low_durability":
            return "They may like the connection, but not enough to carry it in a reliable way."
        if pattern_label == "hostile_or_trapped_dynamic":
            return "Even if this gets a short-term result, it is likely to leave a bruise."
        if pattern_label == "clear_alignment":
            return "The behavior and the signal match. I do not need to over-interpret scraps."
        return "There is not enough consistency here to build certainty on top of it."

    def _what_this_does_not_prove(self, pattern_label: str) -> str:
        if pattern_label == "clear_alignment":
            return "It does not prove permanence, exclusivity, or deep emotional maturity."
        return "It does not prove what the other person feels deep down, and it does not measure my value."

    def _guardedness_read(
        self,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
    ) -> str:
        if appraisal.certainty < 0.3 or prediction.predicted_behavior == "DELAY":
            return "guardedness is elevated; the person is not moving in an open-handed way yet"
        if appraisal.certainty > 0.7 and appraisal.agency > 0.6:
            return "guardedness looks low; the signal is relatively direct"
        return "guardedness is present but not dominant"

    def _pressure_read(
        self,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
    ) -> str:
        if appraisal.agency < 0.3 and prediction.retaliation_probability >= 0.12:
            return "the pressure signature is high: low agency plus backlash risk"
        if appraisal.agency < 0.45:
            return "there is some pressure in the frame; room to choose feels reduced"
        return "pressure does not appear to be the main driver"

    def _congruence_read(
        self,
        circuits: CircuitActivations,
        prediction: BehavioralPrediction,
    ) -> str:
        if circuits.conflict_level < 0.3 and prediction.repeat_compliance >= prediction.immediate_compliance - 0.05:
            return "behavior and underlying pull look fairly congruent"
        if circuits.conflict_level > 0.6:
            return "the signal is incongruent; different systems are pulling in different directions"
        return "congruence is partial; some pieces line up, others do not"

    def _distancing_read(
        self,
        pattern_label: str,
        prediction: BehavioralPrediction,
    ) -> str:
        if pattern_label == "soft_rejection_or_distancing":
            return "distance is being created without fully naming it"
        if prediction.predicted_behavior == "DELAY":
            return "distancing may be happening through delay rather than direct refusal"
        return "distancing is not the clearest active pattern"

    def _ambiguity_read(
        self,
        pattern_label: str,
        appraisal: AppraisalScores,
        circuits: CircuitActivations,
    ) -> str:
        if pattern_label == "ambiguity_or_non-commitment":
            return "ambiguity is high enough that you should treat this as unresolved, not implied clarity"
        if circuits.conflict_level > 0.5 or appraisal.certainty < 0.45:
            return "some ambiguity remains; avoid building a cathedral on scraps"
        return "ambiguity is relatively contained"

    def _next_move(
        self,
        pattern_label: str,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
    ) -> str:
        if pattern_label == "hostile_or_trapped_dynamic":
            return "de-pressurize the frame, name less, and create a clean exit or a lower-stakes path"
        if pattern_label == "soft_rejection_or_distancing":
            return "stop chasing clarity through pressure; respond once, briefly, and let behavior do the talking"
        if pattern_label == "ambiguity_or_non-commitment":
            return "make the next step smaller and concrete, then watch whether the person actually moves"
        if pattern_label == "short_term_pull_low_durability":
            return "slow the pace and require consistency before increasing investment"
        if pattern_label == "clear_alignment":
            return "move one notch more specific while preserving ease and agency"
        if appraisal.agency < 0.45:
            return "reduce constraint before asking for more signal"
        return "keep the next move light, specific, and easy to decline"

    def _autonomy_protection(self, pattern_label: str) -> str:
        if pattern_label in {"hostile_or_trapped_dynamic", "ambiguity_or_non-commitment"}:
            return "protect autonomy by lowering pressure and making non-participation socially cheap"
        if pattern_label == "soft_rejection_or_distancing":
            return "protect both sides by not cornering the person into a clarifying performance"
        return "preserve choice by keeping the next move clear and voluntary"

    def _tactical_empathy(self, pattern_label: str, appraisal: AppraisalScores) -> str:
        if pattern_label == "hostile_or_trapped_dynamic":
            return "treat the friction as a felt constraint problem before treating it as a persuasion problem"
        if pattern_label == "soft_rejection_or_distancing":
            return "assume the person may be trying to soften discomfort, not write a manifesto"
        if appraisal.certainty < 0.35:
            return "assume hesitation before assuming refusal, manipulation, or hidden certainty"
        return "mirror the likely pressure point without over-narrating it"

    def _calibrated_question_posture(
        self,
        pattern_label: str,
        appraisal: AppraisalScores,
        prediction: BehavioralPrediction,
    ) -> str:
        if pattern_label == "hostile_or_trapped_dynamic":
            return "if you ask anything, make it a low-pressure diagnostic question with an easy no"
        if pattern_label == "soft_rejection_or_distancing":
            return "avoid cross-examination; one short question max, only if silence would create more friction"
        if pattern_label == "ambiguity_or_non-commitment":
            return "ask a narrow next-step question, not a feelings autopsy"
        if prediction.compliance_prob >= 0.55 and appraisal.agency >= 0.6:
            return "use a concrete forward question that keeps choice intact"
        return "prefer one calibrated question over a stack of clarifying probes"

    def _response_style(self, pattern_label: str, prediction: BehavioralPrediction) -> str:
        if pattern_label in {"ambiguity_or_non-commitment", "soft_rejection_or_distancing"}:
            return "brief_warm_boundaried"
        if pattern_label == "hostile_or_trapped_dynamic":
            return "calm_firm_exit"
        if pattern_label == "clear_alignment":
            return "open_specific_grounded"
        if pattern_label == "short_term_pull_low_durability":
            return "slow_down_and_require_consistency"
        return "measured_non-pursuing"
