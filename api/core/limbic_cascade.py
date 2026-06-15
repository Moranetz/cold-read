from __future__ import annotations
"""
Limbic Cascade — 6-Stage Pipeline Orchestrator
================================================
Orchestrates the full neuroanatomical decision cascade:

    Stage 1: Sensory Ingestion (Thalamus) — multimodal channel count
    Stage 2: Emotional Tagging (Amygdala) — threat/approach classification
    Stage 3: Reward Prediction (Nucleus Accumbens) — incentive salience
    Stage 4: Memory Consultation (Hippocampus) — somatic marker retrieval
    Stage 5: Somatic Marker Integration (vmPFC) — body-state bias
    Stage 6: Conscious Deliberation (dlPFC/ACC) — rational override

Single entry point: analyze(text) -> CascadeResult

Based on:
    - LeDoux (1996) — amygdala fast path timing
    - Schultz (1997) — dopamine prediction error
    - Damasio (1994) — somatic marker retrieval
    - Knutson et al. (2007) — NAc/insula predict purchases
"""

from dataclasses import dataclass, field
from typing import Optional

from core.appraisal_extractor import AppraisalExtractor, AppraisalScores
from core.circuit_predictor import (
    CircuitPredictor,
    CircuitActivations,
    BehavioralPrediction,
    persuasion_effectiveness,
)
from core.somatic_marker_store import SomaticMarkerStore
from core.reframing_engine import ReframingEngine, TradeoffProjection
from core.ux_patterns import UXPatternLibrary
from core.relational_interpreter import RelationalInterpretation, RelationalInterpreter


@dataclass
class StageTrace:
    """Trace of what happened at each stage of the cascade."""
    stage: int
    name: str
    structure: str
    timing_ms: str
    output: dict


@dataclass
class CascadeResult:
    """Complete output of a limbic cascade analysis."""
    stimulus: str
    appraisal: AppraisalScores
    circuits: CircuitActivations
    prediction: BehavioralPrediction
    effectiveness: float
    somatic_marker_congruence: float
    insula_disgust_signal: float
    familiarity: float
    stages: list[StageTrace]
    tradeoffs: list
    top_fix: Optional[TradeoffProjection]
    relational_interpretation: Optional[RelationalInterpretation] = None

    def to_dict(self) -> dict:
        d = {
            "stimulus": self.stimulus[:200],
            "appraisal": self.appraisal.to_dict(),
            "circuits": self.circuits.to_dict(),
            "prediction": self.prediction.to_dict(),
            "effectiveness": self.effectiveness,
            "somatic_marker_congruence": self.somatic_marker_congruence,
            "insula_disgust_signal": self.insula_disgust_signal,
            "familiarity": self.familiarity,
            "weakest_dimension": self.appraisal.weakest_dimension(),
            "tradeoff_count": len(self.tradeoffs),
            "relational_interpretation": (
                self.relational_interpretation.to_dict()
                if self.relational_interpretation else None
            ),
        }
        if self.top_fix:
            d["top_fix"] = {
                "dimension": self.top_fix.dimension,
                "current": self.top_fix.current_value,
                "projected": self.top_fix.projected_value,
                "direction": self.top_fix.direction,
                "delta_immediate": self.top_fix.delta_immediate_compliance,
                "delta_repeat": self.top_fix.delta_repeat_compliance,
                "delta_retaliation": self.top_fix.delta_retaliation,
            }
        else:
            d["top_fix"] = None
        return d

    def summary(self) -> str:
        """Mechanical summary — no editorial language."""
        pred = self.prediction
        weak_name, weak_val = self.appraisal.weakest_dimension()
        strong_name, strong_val = self.appraisal.strongest_dimension()

        lines = [
            f"Effectiveness: {self.effectiveness:.0%}",
            f"Immediate compliance: {pred.immediate_compliance:.0%}",
            f"Repeat compliance: {pred.repeat_compliance:.0%}",
            f"Retaliation probability: {pred.retaliation_probability:.0%}",
            f"Dominant circuit: {self.circuits.dominant} ({pred.dominant_pathway})",
            f"Durability: {pred.durability:+.2f}",
            f"Strongest: {strong_name} ({strong_val:.2f})",
            f"Weakest: {weak_name} ({weak_val:.2f})",
        ]

        if self.top_fix:
            lines.append(
                f"Highest-impact change: {self.top_fix.direction} {self.top_fix.dimension} "
                f"from {self.top_fix.current_value:.2f} to {self.top_fix.projected_value:.2f} "
                f"→ immediate {self.top_fix.delta_immediate_compliance:+.2f}, "
                f"repeat {self.top_fix.delta_repeat_compliance:+.2f}, "
                f"retaliation {self.top_fix.delta_retaliation:+.2f}"
            )

        return "\n".join(lines)

    def operator_summary(self) -> str:
        """Cleaner operator-facing summary with explicit inference boundaries."""
        pred = self.prediction
        weak_name, weak_val = self.appraisal.weakest_dimension()
        lines = [
            f"Signal: {pred.predicted_behavior.lower()} "
            f"(immediate {pred.immediate_compliance:.0%} | repeat {pred.repeat_compliance:.0%} | retaliation {pred.retaliation_probability:.0%})",
            f"Dominant pathway: {pred.dominant_pathway} via {self.circuits.dominant}",
            f"Weakest dimension: {weak_name} ({weak_val:.2f})",
        ]

        if self.top_fix:
            lines.append(
                f"Highest-leverage change: {self.top_fix.direction} {self.top_fix.dimension} "
                f"to {self.top_fix.projected_value:.2f}"
            )

        rel = self.relational_interpretation
        if rel:
            lines.extend([
                "",
                "Interpretation",
                f"  Signal present: {rel.signal_present}",
                f"  Probably means: {rel.plain_english_inference}",
                f"  Do not infer: {rel.what_this_does_not_prove}",
                f"  Best next move: {rel.next_move}",
                "",
                "Operator Read",
                f"  Pattern: {rel.pattern_label} ({rel.confidence} confidence)",
                f"  Congruence: {rel.congruence_read}",
                f"  Guardedness: {rel.guardedness_read}",
                f"  Pressure: {rel.pressure_read}",
                f"  Distancing: {rel.distancing_read}",
                f"  Ambiguity: {rel.ambiguity_read}",
                f"  Tactical empathy: {rel.tactical_empathy}",
                f"  Autonomy protection: {rel.autonomy_protection}",
                f"  Calibrated question posture: {rel.calibrated_question_posture}",
                f"  Internal translation: {rel.clean_internal_translation}",
                f"  Response style: {rel.response_style}",
            ])

        return "\n".join(lines)


class LimbicCascade:
    """Full 6-stage limbic decision cascade analyzer.

    Usage:
        cascade = LimbicCascade()
        result = cascade.analyze("Get Notion free")
        print(result.summary())
    """

    def __init__(
        self,
        extraction_mode: str = "heuristic",
        ollama_model: str = "llama3.2",
        anthropic_api_key: str = None,
        marker_store_path: Optional[str] = None,
    ):
        self.extractor = AppraisalExtractor(
            ollama_model=ollama_model,
            anthropic_api_key=anthropic_api_key,
        )
        self.predictor = CircuitPredictor()
        self.markers = SomaticMarkerStore(store_path=marker_store_path)
        self.reframer = ReframingEngine()
        self.relational_interpreter = RelationalInterpreter()
        self.extraction_mode = extraction_mode

    def analyze(
        self,
        text: str,
        context: Optional[str] = None,
        multimodal_channels: int = 1,
        information_load: float = 0.3,
        contradictory_signals: float = 0.0,
        interoceptive_precision: float = 0.5,
    ) -> CascadeResult:
        """Run the full 6-stage limbic cascade on a text stimulus.

        Args:
            text: The stimulus to analyze (copy, CTA, notification, etc.)
            context: Brand/product context for somatic marker retrieval.
                     Defaults to text itself if not provided.
            multimodal_channels: Number of sensory channels (1=text only,
                                 2=text+visual, 3=text+visual+audio/haptic)
            information_load: 0-1, how much information the user must process
            contradictory_signals: 0-1, degree of mixed emotional cues
            interoceptive_precision: 0-1, how attentive user is to body signals
        """
        context = context or text[:100]
        stages = []

        # ── Stage 1: Sensory Ingestion (Thalamus) ──────────────────────
        multimodal_boost = min(0.15, 0.05 * (multimodal_channels - 1))
        stages.append(StageTrace(
            stage=1,
            name="Sensory Ingestion",
            structure="Thalamus -> Primary sensory cortices",
            timing_ms="0-50ms",
            output={
                "channels": multimodal_channels,
                "multimodal_boost": multimodal_boost,
                "note": "Multimodal stimuli produce stronger downstream limbic responses "
                        "(TRIBE v2: highest benefit in associative cortices)",
            },
        ))

        # ── Stage 2: Emotional Tagging (Amygdala) ──────────────────────
        appraisal = self.extractor.extract(text, mode=self.extraction_mode, context=context)
        # Amygdala fast path: classify as approach/avoid within ~150ms
        amygdala_threat = (1.0 - appraisal.valence) * (1.0 - appraisal.certainty)
        amygdala_verdict = "approach" if amygdala_threat < 0.4 else "threat" if amygdala_threat > 0.6 else "ambiguous"
        stages.append(StageTrace(
            stage=2,
            name="Emotional Tagging",
            structure="Amygdala (BLA + CeA)",
            timing_ms="50-200ms",
            output={
                "threat_level": round(amygdala_threat, 3),
                "fast_path_verdict": amygdala_verdict,
                "note": "LeDoux low road: thalamus -> amygdala bypasses cortex. "
                        "First impression forms before conscious processing.",
            },
        ))

        # ── Stage 3: Reward Prediction (Nucleus Accumbens) ─────────────
        reward_prediction = appraisal.valence * appraisal.goal_relevance
        reward_prediction = min(1.0, reward_prediction + multimodal_boost)
        stages.append(StageTrace(
            stage=3,
            name="Reward Prediction",
            structure="Nucleus Accumbens (shell: outcome value, core: approach behavior)",
            timing_ms="100-300ms",
            output={
                "incentive_salience": round(reward_prediction, 3),
                "dopamine_signal": "positive prediction" if reward_prediction > 0.5 else "weak/negative prediction",
                "note": "Dopamine fires on PREDICTION of reward, not consumption. "
                        "Maximum activity is JUST BEFORE reward arrives.",
            },
        ))

        # ── Stage 4: Memory Consultation (Hippocampus) ─────────────────
        marker = self.markers.retrieve(context)
        familiarity = 0.7 if marker else 0.3
        somatic_congruence = self.markers.congruence_score(context)
        disgust_signal = self.markers.disgust_signal(context)
        stages.append(StageTrace(
            stage=4,
            name="Memory Consultation",
            structure="Hippocampus (CA1: episodic recall, DG: pattern separation)",
            timing_ms="200-500ms",
            output={
                "prior_marker_exists": marker is not None,
                "marker_valence": marker.valence if marker else None,
                "marker_strength": marker.effective_strength if marker else None,
                "familiarity": familiarity,
                "note": "Hippocampus retrieves emotional CONTEXT of past experiences. "
                        "Emotional tag comes back with the episodic memory.",
            },
        ))

        # ── Stage 5: Somatic Marker Integration (vmPFC) ───────────────
        stages.append(StageTrace(
            stage=5,
            name="Somatic Marker Integration",
            structure="vmPFC (receives amygdala + hippocampus + insula)",
            timing_ms="300-1000ms",
            output={
                "somatic_congruence": somatic_congruence,
                "disgust_signal": disgust_signal,
                "body_loop": "active" if (marker and marker.source == "direct") else "as-if",
                "bias_direction": "approach" if somatic_congruence > 0.5 else "avoidance" if somatic_congruence < 0.5 else "neutral",
                "note": "vmPFC reconstructs the PHYSIOLOGICAL STATE of similar past decisions. "
                        "This body-state biases the current decision before consciousness.",
            },
        ))

        # ── Stage 6: Conscious Deliberation (dlPFC/ACC) ───────────────
        prediction = self.predictor.predict(
            appraisal=appraisal,
            somatic_marker_congruence=somatic_congruence,
            insula_disgust_signal=disgust_signal,
            familiarity=familiarity,
            information_load=information_load,
            contradictory_signals=contradictory_signals,
        )

        effectiveness = persuasion_effectiveness(
            circuits=prediction.circuits,
            somatic_marker_congruence=somatic_congruence,
            interoceptive_precision=interoceptive_precision,
        )

        stages.append(StageTrace(
            stage=6,
            name="Conscious Deliberation",
            structure="dlPFC (working memory) + ACC (conflict monitoring)",
            timing_ms="500-3000ms",
            output={
                "circuits": prediction.circuits.to_dict(),
                "behavioral_prediction": prediction.predicted_behavior,
                "dominant_pathway": prediction.dominant_pathway,
                "note": "By Stage 6, Stages 1-5 have already filtered, scored, "
                        "retrieved memories, and generated a somatic bias. "
                        "The dlPFC operates WITHIN this emotional frame.",
            },
        ))

        # ── Tradeoff surface ────────────────────────────────────────────
        tradeoffs = self.reframer.diagnose(
            appraisal, prediction,
            somatic_marker_congruence=somatic_congruence,
            insula_disgust_signal=disgust_signal,
            familiarity=familiarity,
        )
        top = self.reframer.top_fix(
            appraisal, prediction,
            somatic_marker_congruence=somatic_congruence,
            insula_disgust_signal=disgust_signal,
            familiarity=familiarity,
        )
        relational_interpretation = self.relational_interpreter.interpret(
            text, appraisal, prediction.circuits, prediction
        )

        return CascadeResult(
            stimulus=text,
            appraisal=appraisal,
            circuits=prediction.circuits,
            prediction=prediction,
            effectiveness=effectiveness,
            somatic_marker_congruence=somatic_congruence,
            insula_disgust_signal=disgust_signal,
            familiarity=familiarity,
            stages=stages,
            tradeoffs=tradeoffs,
            top_fix=top,
            relational_interpretation=relational_interpretation,
        )

    def compare(self, text_a: str, text_b: str, **kwargs) -> dict:
        """Analyze two stimuli and return the delta."""
        result_a = self.analyze(text_a, **kwargs)
        result_b = self.analyze(text_b, **kwargs)
        rel_a = result_a.relational_interpretation
        rel_b = result_b.relational_interpretation

        operator_delta = None
        if rel_a and rel_b:
            operator_delta = {
                "signal_shift": f"{rel_a.signal_present} -> {rel_b.signal_present}",
                "pressure_cleaner": "b" if result_b.prediction.retaliation_probability < result_a.prediction.retaliation_probability else "a",
                "congruence_cleaner": "b" if result_b.circuits.conflict_level < result_a.circuits.conflict_level else "a",
                "ambiguity_cleaner": "b" if result_b.appraisal.certainty > result_a.appraisal.certainty else "a",
                "next_move_upgrade": {
                    "a": rel_a.next_move,
                    "b": rel_b.next_move,
                },
                "autonomy_protection_upgrade": {
                    "a": rel_a.autonomy_protection,
                    "b": rel_b.autonomy_protection,
                },
                "tactical_empathy_upgrade": {
                    "a": rel_a.tactical_empathy,
                    "b": rel_b.tactical_empathy,
                },
            }

        return {
            "a": {"text": text_a[:100], "effectiveness": result_a.effectiveness,
                  "behavior": result_a.prediction.predicted_behavior,
                  "signal_present": rel_a.signal_present if rel_a else None,
                  "best_next_move": rel_a.next_move if rel_a else None},
            "b": {"text": text_b[:100], "effectiveness": result_b.effectiveness,
                  "behavior": result_b.prediction.predicted_behavior,
                  "signal_present": rel_b.signal_present if rel_b else None,
                  "best_next_move": rel_b.next_move if rel_b else None},
            "delta_effectiveness": round(result_b.effectiveness - result_a.effectiveness, 4),
            "a_appraisal": result_a.appraisal.to_dict(),
            "b_appraisal": result_b.appraisal.to_dict(),
            "operator_delta": operator_delta,
            "winner": "b" if result_b.effectiveness > result_a.effectiveness else "a",
        }
