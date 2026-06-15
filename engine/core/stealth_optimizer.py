from __future__ import annotations
"""
Stealth Optimizer — Maximize persuasion while passing organic detection
========================================================================
Uses the influence detector's signals as CONSTRAINTS, not warnings.
The goal: generate content that scores maximum effectiveness on the
limbic cascade while scoring "organic" on the influence detector.

This is the implementation tool. It answers:
"What's the most persuasive thing I can say that doesn't look persuasive?"

Architecture:
    1. Generate candidate via OptimizationEngine (max effectiveness)
    2. Run influence detector on the candidate
    3. If flagged: identify which signals tripped, suppress those specific
       features while preserving the persuasive appraisal profile
    4. Iterate until the content is both effective AND organic-passing

The constraint surface:
    - Technique count <= 2 per post (organic baseline)
    - No suspicious technique stacks
    - Linguistic profile within 1 SD of subreddit norm
    - Zero moral foundation targeting signals (MFT should be invisible)
    - Certainty markers < 2% (organic baseline)
    - Must pass influence detector as "organic"
"""

import re
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

from core.optimization_engine import OptimizationEngine, OptimizationResult
from core.influence_detector import InfluenceDetector
from core.linguistic_surface import extract_linguistic_features
from core.appraisal_extractor import AppraisalExtractor
from core.circuit_predictor import CircuitPredictor, persuasion_effectiveness


@dataclass
class StealthResult:
    """Content that is both maximally persuasive and organically camouflaged."""
    text: str
    effectiveness: float
    influence_risk: float        # should be < 0.3 (organic)
    influence_level: str         # should be "organic"
    appraisal: dict
    techniques_present: int      # should be <= 2
    iterations: int
    suppressed_signals: list     # what was removed to pass detection
    tradeoff: str                # what persuasive power was sacrificed

    def to_dict(self):
        return asdict(self)


# ─── Subreddit linguistic baselines ──────────────────────────────────────────
# These define what "organic" looks like per community.
# Expand by scraping actual subreddit top posts.

SUBREDDIT_NORMS = {
    "iOSProgramming": {
        "reading_difficulty": (0.3, 0.6),   # moderate-high (technical)
        "emotionality": (0.0, 0.01),         # very low (factual)
        "self_reference": (0.02, 0.08),      # moderate I-language
        "certainty_markers": (0.0, 0.015),   # low certainty language
        "tone": "technical, understated, specific",
    },
    "selfimprovement": {
        "reading_difficulty": (0.1, 0.35),   # easy-moderate
        "emotionality": (0.005, 0.03),       # moderate emotional
        "self_reference": (0.05, 0.12),      # high I-language (personal stories)
        "certainty_markers": (0.0, 0.02),
        "tone": "vulnerable, honest, personal",
    },
    "psychology": {
        "reading_difficulty": (0.25, 0.55),  # moderate-high
        "emotionality": (0.0, 0.015),        # low-moderate
        "self_reference": (0.02, 0.06),      # moderate
        "certainty_markers": (0.0, 0.01),    # low — hedged language preferred
        "tone": "analytical, nuanced, evidence-referencing",
    },
    "startups": {
        "reading_difficulty": (0.15, 0.4),
        "emotionality": (0.0, 0.02),
        "self_reference": (0.04, 0.10),      # founder stories
        "certainty_markers": (0.0, 0.015),
        "tone": "builder-voice, numbers, vulnerable about failure",
    },
    "entrepreneur": {
        "reading_difficulty": (0.15, 0.4),
        "emotionality": (0.0, 0.02),
        "self_reference": (0.04, 0.10),
        "certainty_markers": (0.0, 0.015),
        "tone": "pragmatic, results-oriented, no fluff",
    },
    "politics": {
        "reading_difficulty": (0.2, 0.5),
        "emotionality": (0.005, 0.04),       # higher emotional content allowed
        "self_reference": (0.02, 0.08),
        "certainty_markers": (0.0, 0.025),
        "tone": "passionate but substantiated, cite sources",
    },
    "default": {
        "reading_difficulty": (0.1, 0.4),
        "emotionality": (0.0, 0.025),
        "self_reference": (0.02, 0.10),
        "certainty_markers": (0.0, 0.02),
        "tone": "casual, conversational, lowercase ok",
    },
}


STEALTH_SYSTEM_PROMPT = """You are rewriting content to sound more natural and organic while preserving its persuasive intent.

Rules:
- Maximum 1-2 persuasion techniques, deployed INVISIBLY
- No marketing language, no urgency words, no scarcity signals
- Match the tone of someone genuinely sharing their experience
- Use lowercase, contractions, sentence fragments where natural
- The reader should feel like they're reading a real person's honest thought
- Specific details and numbers feel authentic. Vague claims feel manufactured.
- End with a genuine question or incomplete thought (invites engagement without demanding it)

Target subreddit tone: {tone}

The content must NOT trigger these detection signals:
{suppression_instructions}

Original content (persuasive but flagged):
"{original}"

Rewrite to preserve the persuasive EFFECT while eliminating the detectable SIGNATURES.
Return ONLY the rewritten text. No explanation."""


class StealthOptimizer:
    """Generate maximally persuasive content that passes organic detection."""

    def __init__(
        self,
        anthropic_api_key=None,
        ollama_model="llama3.2",
        extraction_mode="heuristic",
    ):
        self.optimizer = OptimizationEngine(
            anthropic_api_key=anthropic_api_key,
            ollama_model=ollama_model,
            extraction_mode=extraction_mode,
        )
        self.detector = InfluenceDetector(
            technique_mode="heuristic",
            appraisal_mode=extraction_mode,
        )
        self.extractor = AppraisalExtractor(ollama_model=ollama_model)
        self.predictor = CircuitPredictor()
        self.ollama_model = ollama_model
        self.api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    def optimize(
        self,
        goal: str,
        subreddit: str = "default",
        platform: str = "reddit",
        audience: str = "subreddit community member",
        max_stealth_iterations: int = 3,
        domain: str = "universal",
    ) -> StealthResult:
        """Generate content that is persuasive AND organic-passing.

        1. Generate high-effectiveness content via optimization engine
        2. Check against influence detector
        3. If flagged, rewrite to suppress detected signals
        4. Repeat until organic OR max iterations
        """
        # Step 1: Generate persuasive content
        opt_result = self.optimizer.optimize(
            goal=goal,
            context=self._platform_context(platform),
            audience=audience,
            iterations=2,
            candidates_per_round=3,
        )

        if not opt_result.best_text:
            return StealthResult(
                text="", effectiveness=0, influence_risk=0,
                influence_level="no_content", appraisal={},
                techniques_present=0, iterations=0,
                suppressed_signals=[], tradeoff="generation failed",
            )

        current_text = opt_result.best_text
        current_effectiveness = opt_result.best_effectiveness
        suppressed = []

        norms = SUBREDDIT_NORMS.get(subreddit, SUBREDDIT_NORMS["default"])

        for iteration in range(max_stealth_iterations):
            # Step 2: Check against influence detector
            report = self.detector.analyze(current_text, subreddit_context=subreddit)

            if report.risk_level == "organic":
                # Also check linguistic norms
                ling = extract_linguistic_features(current_text)
                norm_violations = self._check_norms(ling, norms)
                if not norm_violations:
                    break  # passes both checks

            # Step 3: Build suppression instructions
            instructions = self._build_suppression_instructions(report, norms)
            suppressed.extend([s.signal_type for s in report.signals])

            # Step 4: Rewrite
            rewritten = self._stealth_rewrite(current_text, instructions, norms.get("tone", ""))
            if rewritten and rewritten != current_text:
                current_text = rewritten
            else:
                break  # can't improve further

        # Final assessment
        final_report = self.detector.analyze(current_text, subreddit_context=subreddit)
        final_appraisal = self.extractor.extract(current_text, mode="heuristic")
        final_pred = self.predictor.predict(final_appraisal)
        final_effectiveness = persuasion_effectiveness(final_pred.circuits)

        effectiveness_cost = opt_result.best_effectiveness - final_effectiveness
        tradeoff = "%.0f%% effectiveness → %.0f%% after stealth optimization (−%.0f pp)" % (
            opt_result.best_effectiveness * 100,
            final_effectiveness * 100,
            effectiveness_cost * 100,
        )

        return StealthResult(
            text=current_text,
            effectiveness=final_effectiveness,
            influence_risk=final_report.overall_risk,
            influence_level=final_report.risk_level,
            appraisal=final_appraisal.to_dict(),
            techniques_present=final_report.technique_profile
                and sum(1 for v in final_report.technique_profile.values() if v.get("detected"))
                or 0,
            iterations=max_stealth_iterations,
            suppressed_signals=list(set(suppressed)),
            tradeoff=tradeoff,
        )

    def _check_norms(self, ling, norms):
        """Check if linguistic features fall within subreddit norms."""
        violations = []
        for feature in ["reading_difficulty", "emotionality", "self_reference", "certainty_markers"]:
            if feature in norms:
                lo, hi = norms[feature]
                val = getattr(ling, feature, 0)
                if val < lo or val > hi:
                    violations.append("%s=%.3f (norm: %.3f-%.3f)" % (feature, val, lo, hi))
        return violations

    def _build_suppression_instructions(self, report, norms):
        """Build specific instructions for suppressing detected signals."""
        instructions = []
        for signal in report.signals:
            if signal.signal_type == "technique_density":
                instructions.append("Reduce the number of identifiable persuasion techniques to 1-2 maximum. "
                                    "Hide techniques inside natural language — don't use their textbook forms.")
            elif signal.signal_type == "technique_stack":
                instructions.append("Remove the technique combination. Use at most one emotional appeal "
                                    "and one logical/evidence element. Never stack urgency + scarcity + social proof.")
            elif signal.signal_type == "moral_foundation_targeting":
                instructions.append("Remove overt moral/values language. Don't use words like 'patriot', "
                                    "'tradition', 'values', 'sacred', 'rights'. If the moral appeal is needed, "
                                    "embed it in a SPECIFIC personal story, not abstract language.")
            elif signal.signal_type == "outrage_optimization":
                instructions.append("Reduce the outrage signal. Replace accusatory framing with curious framing. "
                                    "'Why does this happen?' instead of 'They did this to us!'")
            elif signal.signal_type == "excessive_certainty":
                instructions.append("Replace certainty words (definitely, always, clearly, proven) with "
                                    "hedged language (I've noticed, in my experience, seems like, from what I can tell).")
            elif signal.signal_type == "emotional_without_analytical":
                instructions.append("Add at least one specific fact, number, or personal observation. "
                                    "Pure emotion without substance gets flagged.")
        return "\n".join(instructions) if instructions else "Make it sound more natural and less crafted."

    def _stealth_rewrite(self, text, suppression_instructions, tone):
        """Rewrite content to pass detection while preserving persuasive effect."""
        prompt = STEALTH_SYSTEM_PROMPT.format(
            tone=tone,
            suppression_instructions=suppression_instructions,
            original=text[:2000],
        )
        return self.optimizer._call_llm("", prompt)

    def _platform_context(self, platform):
        if platform == "reddit":
            return "cta"
        elif platform == "linkedin":
            return "landing"
        elif platform == "substack":
            return "landing"
        return "general"
