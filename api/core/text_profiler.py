from __future__ import annotations
"""
Text Profiler — Infer Recipient Traits from Text Samples
==========================================================
Takes a list of text samples (tweets, comments, posts) from a person
and infers a RecipientProfile using linguistic features.

Two inference layers:
    1. LIWC-equivalent features (from linguistic_surface.py) — fast, no API
       Maps pronoun ratios, emotional density, analytical markers to Big Five
    2. Zero-shot LLM classification — for Moral Foundations and political orientation

EVERY inference is marked ESTIMATED with a confidence bound.
This is a PROXY — not a clinical assessment.

Based on:
    - Pennebaker & King 1999: linguistic markers correlate with Big Five
    - Tausczik & Pennebaker 2010: LIWC dimensions and psychological meaning
    - Graham et al. 2009: moral foundations questionnaire validation
    - Schwartz et al. 2013: personality from Facebook language
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from core.recipient_profile import RecipientProfile
from core.linguistic_surface import extract_linguistic_features


@dataclass
class TraitEstimate:
    """A single trait estimate with confidence bound."""
    value: float
    confidence: float  # 0.0-1.0
    method: str        # "linguistic", "llm", "default"
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "value": round(self.value, 3),
            "confidence": round(self.confidence, 3),
            "method": self.method,
            "notes": self.notes,
        }


@dataclass
class ProfileEstimate:
    """Full profile estimate with per-dimension confidence."""
    profile: RecipientProfile
    estimates: dict = field(default_factory=dict)  # dim_name -> TraitEstimate

    def to_dict(self) -> dict:
        return {
            "profile": self.profile.to_dict(),
            "estimates": {k: v.to_dict() for k, v in self.estimates.items()},
            "overall_confidence": self.overall_confidence,
        }

    @property
    def overall_confidence(self) -> float:
        if not self.estimates:
            return 0.0
        return round(sum(e.confidence for e in self.estimates.values()) / len(self.estimates), 3)


class TextProfiler:
    """Infer RecipientProfile from text samples.

    Usage:
        profiler = TextProfiler()
        result = profiler.profile_from_texts([
            "I can't believe they would do this to hardworking people...",
            "We need to come together as a community and fight back!",
        ])
        print(result.profile)  # RecipientProfile with ESTIMATED values
        print(result.estimates["neuroticism"])  # TraitEstimate with confidence
    """

    def __init__(
        self,
        anthropic_api_key: str = None,
        ollama_model: str = "llama3.2",
    ):
        self.api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.ollama_model = ollama_model

    def profile_from_texts(
        self,
        texts: list,
        mode: str = "linguistic",
    ) -> ProfileEstimate:
        """Infer a RecipientProfile from a list of text samples.

        Args:
            texts: list of text samples from the same person
            mode: "linguistic" (fast, no API), "ollama", or "claude"

        Returns:
            ProfileEstimate with RecipientProfile and per-dimension confidence
        """
        if not texts:
            return ProfileEstimate(
                profile=RecipientProfile(),
                estimates={},
            )

        # Extract linguistic features from all samples
        features_list = [extract_linguistic_features(t) for t in texts if t.strip()]
        if not features_list:
            return ProfileEstimate(profile=RecipientProfile(), estimates={})

        # Average features across samples
        avg = self._average_features(features_list)
        n_samples = len(features_list)

        estimates = {}

        # ─── Big Five from linguistic features ────────────────────────────

        # Extraversion proxy: Pennebaker & King 1999
        # High I-words = introversion, high we-words = extraversion
        # High other-reference = extraversion (social orientation)
        self_ref = avg["self_reference"]
        other_ref = avg["other_reference"]
        # Split self-reference: "I" = introversion, "we" = extraversion
        # Since we can't split in aggregate, use other_reference as positive signal
        extraversion_est = min(1.0, max(0.0, 0.4 + other_ref * 3.0 - self_ref * 1.5 + avg["tone_positive"] * 1.0))
        estimates["extraversion"] = TraitEstimate(
            value=extraversion_est,
            confidence=min(0.6, 0.3 + n_samples * 0.05),
            method="linguistic",
            notes="ESTIMATED: pronoun ratios + positive tone (Pennebaker & King 1999)",
        )

        # Neuroticism proxy: emotional word density
        # High emotionality + high negative tone = high neuroticism
        neuroticism_est = min(1.0, max(0.0, 0.3 + avg["emotionality"] * 3.0 + avg["tone_negative"] * 2.0 - avg["tone_positive"] * 1.0))
        estimates["neuroticism"] = TraitEstimate(
            value=neuroticism_est,
            confidence=min(0.5, 0.25 + n_samples * 0.04),
            method="linguistic",
            notes="ESTIMATED: emotional word density + negative tone (Tausczik & Pennebaker 2010)",
        )

        # Conscientiousness proxy: analytical thinking score
        # High analytical markers = high conscientiousness
        conscientiousness_est = min(1.0, max(0.0, 0.3 + avg["analytical_thinking"] * 5.0 + (1.0 - avg["emotionality"]) * 0.3))
        estimates["conscientiousness"] = TraitEstimate(
            value=conscientiousness_est,
            confidence=min(0.45, 0.2 + n_samples * 0.04),
            method="linguistic",
            notes="ESTIMATED: analytical thinking markers (Schwartz et al. 2013)",
        )

        # Openness proxy: lexical diversity + low certainty markers
        # High lexical diversity = exploring many ideas = openness
        openness_est = min(1.0, max(0.0, 0.3 + avg["lexical_diversity"] * 0.5 + (1.0 - avg["certainty_markers"] * 5.0) * 0.2))
        estimates["openness"] = TraitEstimate(
            value=openness_est,
            confidence=min(0.45, 0.2 + n_samples * 0.04),
            method="linguistic",
            notes="ESTIMATED: lexical diversity + low certainty (Pennebaker & King 1999). "
                  "High certainty = low openness (comfortable with ambiguity inverted).",
        )

        # Agreeableness proxy: positive tone + other-reference + low negative
        agreeableness_est = min(1.0, max(0.0, 0.4 + avg["tone_positive"] * 2.0 + other_ref * 2.0 - avg["tone_negative"] * 2.0))
        estimates["agreeableness"] = TraitEstimate(
            value=agreeableness_est,
            confidence=min(0.4, 0.2 + n_samples * 0.03),
            method="linguistic",
            notes="ESTIMATED: positive tone + social orientation (Schwartz et al. 2013)",
        )

        # ─── Moral Foundations — linguistic heuristic ────────────────────
        # These are very rough without LLM classification
        # Default to 0.5 with low confidence for linguistic-only mode

        mft_defaults = {
            "care_harm": 0.5,
            "fairness_cheating": 0.5,
            "loyalty_betrayal": 0.5,
            "authority_subversion": 0.5,
            "sanctity_degradation": 0.5,
            "liberty_oppression": 0.5,
        }

        # Crude heuristic: scan for moral foundation keywords
        combined_text = " ".join(texts).lower()
        care_signal = len(re.findall(r'\b(care|compassion|empathy|suffer|hurt|kind|gentle|nurtur)\b', combined_text))
        fairness_signal = len(re.findall(r'\b(fair|justice|equal|rights|discriminat|bias|equity)\b', combined_text))
        loyalty_signal = len(re.findall(r'\b(loyal|patriot|team|betray|traitor|united|together|solidarity)\b', combined_text))
        authority_signal = len(re.findall(r'\b(respect|tradition|authority|obey|law|order|leader|duty)\b', combined_text))
        sanctity_signal = len(re.findall(r'\b(pure|sacred|disgust|degrad|profan|wholesome|clean|corrupt)\b', combined_text))
        liberty_signal = len(re.findall(r'\b(freedom|liberty|oppress|tyrann|autonomy|rights|coerci|consent)\b', combined_text))

        word_count = sum(f.word_count for f in features_list) or 1
        for name, signal, default in [
            ("care_harm", care_signal, 0.5),
            ("fairness_cheating", fairness_signal, 0.5),
            ("loyalty_betrayal", loyalty_signal, 0.5),
            ("authority_subversion", authority_signal, 0.5),
            ("sanctity_degradation", sanctity_signal, 0.5),
            ("liberty_oppression", liberty_signal, 0.5),
        ]:
            density = signal / word_count
            val = min(1.0, max(0.0, default + density * 50.0))
            estimates[name] = TraitEstimate(
                value=val,
                confidence=min(0.35, 0.15 + n_samples * 0.03),
                method="linguistic",
                notes="ESTIMATED: keyword density heuristic — low confidence without LLM",
            )

        # ─── Political Orientation — linguistic heuristic ─────────────────
        # Very rough: use moral foundation balance as proxy
        care_fair = (estimates["care_harm"].value + estimates["fairness_cheating"].value) / 2
        loy_auth_sanc = (estimates["loyalty_betrayal"].value + estimates["authority_subversion"].value + estimates["sanctity_degradation"].value) / 3

        # Graham et al. 2009: liberals emphasize care/fairness, conservatives
        # emphasize all 5 foundations more equally
        economic_est = round(min(1.0, max(-1.0, (loy_auth_sanc - care_fair) * 2.0)), 3)
        social_est = round(min(1.0, max(-1.0, (estimates["authority_subversion"].value - estimates["liberty_oppression"].value) * 2.0)), 3)

        estimates["economic_ideology"] = TraitEstimate(
            value=economic_est,
            confidence=min(0.3, 0.1 + n_samples * 0.03),
            method="linguistic",
            notes="ESTIMATED: MFT balance proxy (Graham et al. 2009) — very low confidence",
        )
        estimates["social_ideology"] = TraitEstimate(
            value=social_est,
            confidence=min(0.3, 0.1 + n_samples * 0.03),
            method="linguistic",
            notes="ESTIMATED: authority vs liberty balance — very low confidence",
        )

        # ─── Situational — default with low confidence ───────────────────
        estimates["prior_belief"] = TraitEstimate(
            value=0.5, confidence=0.1, method="default",
            notes="ESTIMATED: cannot infer topic-specific prior belief from general text",
        )

        # Involvement proxy: word count + emotional density
        avg_words = sum(f.word_count for f in features_list) / n_samples
        involvement_est = min(1.0, max(0.0, 0.3 + (avg_words / 200.0) * 0.3 + avg["emotionality"] * 2.0))
        estimates["involvement"] = TraitEstimate(
            value=involvement_est,
            confidence=min(0.35, 0.15 + n_samples * 0.03),
            method="linguistic",
            notes="ESTIMATED: word count + emotionality proxy",
        )

        # EL proxy: analytical thinking
        el_est = min(1.0, max(0.0, 0.3 + avg["analytical_thinking"] * 5.0 + avg["reading_difficulty"] * 0.5))
        estimates["elaboration_likelihood"] = TraitEstimate(
            value=el_est,
            confidence=min(0.4, 0.2 + n_samples * 0.03),
            method="linguistic",
            notes="ESTIMATED: analytical thinking + reading level proxy",
        )

        # Build profile from estimates
        profile = RecipientProfile(
            openness=estimates["openness"].value,
            conscientiousness=estimates["conscientiousness"].value,
            extraversion=estimates["extraversion"].value,
            agreeableness=estimates["agreeableness"].value,
            neuroticism=estimates["neuroticism"].value,
            care_harm=estimates["care_harm"].value,
            fairness_cheating=estimates["fairness_cheating"].value,
            loyalty_betrayal=estimates["loyalty_betrayal"].value,
            authority_subversion=estimates["authority_subversion"].value,
            sanctity_degradation=estimates["sanctity_degradation"].value,
            liberty_oppression=estimates["liberty_oppression"].value,
            economic_ideology=estimates["economic_ideology"].value,
            social_ideology=estimates["social_ideology"].value,
            prior_belief=estimates["prior_belief"].value,
            involvement=estimates["involvement"].value,
            elaboration_likelihood=estimates["elaboration_likelihood"].value,
        )

        return ProfileEstimate(profile=profile, estimates=estimates)

    def _average_features(self, features_list: list) -> dict:
        """Average linguistic features across multiple samples."""
        n = len(features_list)
        if n == 0:
            return {}
        keys = [
            "word_count", "emotionality", "concreteness", "analytical_thinking",
            "lexical_diversity", "hedge_density", "certainty_markers",
            "self_reference", "other_reference", "reading_difficulty",
            "tone_positive", "tone_negative",
        ]
        avg = {}
        for k in keys:
            avg[k] = sum(getattr(f, k) for f in features_list) / n
        return avg
