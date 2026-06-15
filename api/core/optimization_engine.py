from __future__ import annotations
"""
Optimization Engine — Generate maximally persuasive content
=============================================================
Closes the loop between scoring and generation. Instead of just
telling you "this scores 0.72", it generates the text that scores 0.95.

Architecture:
    1. Takes a communication goal + context
    2. Generates N candidate phrasings via LLM
    3. Scores each through the full pipeline
    4. Identifies the highest-scoring variant
    5. Identifies the weakest dimension of the runner-up
    6. Generates new variants targeting that weak dimension
    7. Repeats for K iterations
    8. Returns the best stimulus found with its full appraisal profile

This is a furnace, not a thermometer.
"""

import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from core.appraisal_extractor import AppraisalExtractor, AppraisalScores
from core.circuit_predictor import CircuitPredictor, persuasion_effectiveness
from core.reframing_engine import ReframingEngine


@dataclass
class OptimizationResult:
    best_text: str
    best_effectiveness: float
    best_appraisal: dict
    best_circuits: dict
    best_prediction: dict
    iterations_run: int
    candidates_evaluated: int
    improvement_trajectory: list  # effectiveness at each iteration
    all_candidates: list          # every candidate scored

    def to_dict(self):
        return {
            "best_text": self.best_text,
            "best_effectiveness": self.best_effectiveness,
            "best_appraisal": self.best_appraisal,
            "best_circuits": self.best_circuits,
            "best_prediction": self.best_prediction,
            "iterations": self.iterations_run,
            "candidates_evaluated": self.candidates_evaluated,
            "improvement_trajectory": self.improvement_trajectory,
        }


GENERATION_SYSTEM_PROMPT = """You are a UX copywriter who understands cognitive appraisal theory. You write copy that scores high on the 7 dimensions the human limbic system evaluates:

- valence: how pleasant the immediate emotional response is
- goal_relevance: how directly it addresses what the reader cares about
- coping_potential: how capable the reader feels of acting
- agency: how much control the reader feels they have
- certainty: how confident the reader is about the outcome
- temporal_proximity: how immediate the benefit feels
- novelty: how unexpected (sweet spot: moderately novel, not bizarre)

You write like a human. No marketing jargon. No bullet points. Contractions. Sentence fragments when natural. First person or second person. The copy should feel like something a real product would ship, not something a copywriting course would produce."""

GENERATION_USER_TEMPLATE = """Communication goal: {goal}
Context: {context}
Target audience: {audience}
{weakness_instruction}

Generate exactly {n} different phrasings. Each should be a complete, deployable piece of copy (not a description of what it should say).

Return a JSON array of strings. Nothing else.
["{n} phrasings here"]"""

REFINEMENT_INSTRUCTION = """The current best version scores {effectiveness:.0%} effectiveness. Its weakest dimension is {weak_dim} at {weak_score:.2f}.

To improve: {reframe_suggestion}

Generate {n} new variants that specifically address the {weak_dim} weakness while maintaining the strengths of the current best. Each variant should feel natural, not forced."""


class OptimizationEngine:
    """Generate maximally persuasive content via iterative scoring and refinement."""

    def __init__(
        self,
        anthropic_api_key=None,
        ollama_model="llama3.2",
        extraction_mode="heuristic",
    ):
        self.api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.ollama_model = ollama_model
        self.extraction_mode = extraction_mode
        self.extractor = AppraisalExtractor(
            anthropic_api_key=self.api_key,
            ollama_model=ollama_model,
        )
        self.predictor = CircuitPredictor()
        self.reframer = ReframingEngine()

    def optimize(
        self,
        goal: str,
        context: str = "general",
        audience: str = "general web user",
        iterations: int = 3,
        candidates_per_round: int = 5,
        target_effectiveness: float = 0.90,
        domain: str = "universal",
    ) -> OptimizationResult:
        """Run the optimization loop.

        Args:
            goal: what the copy should achieve ("get user to start free trial")
            context: UX context (onboarding, checkout, cta, etc.)
            audience: who reads this
            iterations: max refinement rounds
            candidates_per_round: variants generated per round
            target_effectiveness: stop early if reached
        """
        all_candidates = []
        improvement_trajectory = []
        best_text = ""
        best_effectiveness = 0.0
        best_appraisal = {}
        best_circuits = {}
        best_prediction = {}
        weakness_instruction = ""

        for iteration in range(iterations):
            # Generate candidates
            candidates = self._generate_candidates(
                goal, context, audience,
                n=candidates_per_round,
                weakness_instruction=weakness_instruction,
            )

            if not candidates:
                break

            # Score each candidate
            round_results = []
            for text in candidates:
                score_data = self._score(text, context)
                round_results.append(score_data)
                all_candidates.append(score_data)

            # Find best in this round
            round_best = max(round_results, key=lambda x: x["effectiveness"])

            # Update global best
            if round_best["effectiveness"] > best_effectiveness:
                best_text = round_best["text"]
                best_effectiveness = round_best["effectiveness"]
                best_appraisal = round_best["appraisal"]
                best_circuits = round_best["circuits"]
                best_prediction = round_best["prediction"]

            improvement_trajectory.append(best_effectiveness)

            # Early stop if target reached
            if best_effectiveness >= target_effectiveness:
                break

            # Identify weakness for next round
            appraisal = AppraisalScores(**best_appraisal)
            weak_name, weak_val = appraisal.weakest_dimension()

            pred_obj = self.predictor.predict(appraisal)
            suggestions = self.reframer.diagnose(appraisal, pred_obj)
            reframe_text = suggestions[0].net_assessment if suggestions else "improve the weakest dimension"

            weakness_instruction = REFINEMENT_INSTRUCTION.format(
                effectiveness=best_effectiveness,
                weak_dim=weak_name,
                weak_score=weak_val,
                reframe_suggestion=reframe_text,
                n=candidates_per_round,
            )

        return OptimizationResult(
            best_text=best_text,
            best_effectiveness=best_effectiveness,
            best_appraisal=best_appraisal,
            best_circuits=best_circuits,
            best_prediction=best_prediction,
            iterations_run=len(improvement_trajectory),
            candidates_evaluated=len(all_candidates),
            improvement_trajectory=improvement_trajectory,
            all_candidates=all_candidates,
        )

    def _generate_candidates(self, goal, context, audience, n=5, weakness_instruction=""):
        """Generate candidate phrasings via LLM."""
        user_msg = GENERATION_USER_TEMPLATE.format(
            goal=goal,
            context=context,
            audience=audience,
            weakness_instruction=weakness_instruction,
            n=n,
        )

        # Try Claude API first, then Ollama
        raw = self._call_llm(GENERATION_SYSTEM_PROMPT, user_msg)
        if not raw:
            return []

        # Parse JSON array from response — forgiving parser
        try:
            cleaned = re.sub(r'^```(?:json)?\s*', '', raw.strip())
            cleaned = re.sub(r'\s*```$', '', cleaned)
            candidates = json.loads(cleaned)
            if isinstance(candidates, list):
                return [str(c).strip() for c in candidates if str(c).strip()]
        except json.JSONDecodeError:
            pass

        # Try to extract array from mixed text
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                # Fix common LLM JSON errors: trailing commas, unescaped quotes
                fixed = match.group()
                fixed = re.sub(r',\s*]', ']', fixed)  # trailing comma
                fixed = re.sub(r',\s*,', ',', fixed)   # double comma
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

        # Last resort: extract quoted strings
        quotes = re.findall(r'"([^"]{20,})"', raw)
        if quotes:
            return quotes[:n]
        return []

    def _score(self, text, context):
        """Score a candidate through the full pipeline."""
        appraisal = self.extractor.extract(text, mode=self.extraction_mode, context=context)
        pred = self.predictor.predict(appraisal)
        eff = persuasion_effectiveness(pred.circuits)
        return {
            "text": text,
            "effectiveness": eff,
            "appraisal": appraisal.to_dict(),
            "circuits": pred.circuits.to_dict(),
            "prediction": pred.to_dict(),
        }

    def _call_llm(self, system_prompt, user_msg):
        """Call Claude API or Ollama for generation."""
        import urllib.request

        # Try Claude first
        if self.api_key:
            try:
                payload = json.dumps({
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1500,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_msg}],
                }).encode()
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read())
                return "".join(b.get("text", "") for b in result.get("content", []))
            except Exception:
                pass

        # Fall back to Ollama
        try:
            payload = json.dumps({
                "model": self.ollama_model,
                "prompt": system_prompt + "\n\n" + user_msg,
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            return result.get("response", "")
        except Exception:
            return ""
