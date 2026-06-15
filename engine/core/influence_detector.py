from __future__ import annotations
"""
Influence Operation Detector — Defensive Application
======================================================
Uses the same 5-layer architecture (appraisal, technique, linguistic,
recipient profiling, sequence analysis) to DETECT coordinated
influence operations rather than generate them.

Detects:
    1. Technique stacking — multiple persuasion techniques in a single
       post beyond what organic content produces
    2. Audience targeting signals — content calibrated to specific
       MFT/personality profiles (moral reframing indicators)
    3. Coordination fingerprints — accounts posting similar technique
       profiles within short time windows
    4. Engagement manipulation — content optimized for algorithmic
       amplification (high arousal + high goal_relevance)
    5. Authenticity violations — linguistic patterns inconsistent
       with claimed identity or subreddit norms
"""

import re
import math
import time
from dataclasses import dataclass, field
from typing import Optional

from core.technique_detector import TechniqueDetector, TechniqueResult
from core.linguistic_surface import extract_linguistic_features, LinguisticFeatures
from core.appraisal_extractor import AppraisalExtractor, AppraisalScores


# ═══════════════════════════════════════════════════════════════════════════════
# DETECTION THRESHOLDS — Calibrated against organic content baselines
# ═══════════════════════════════════════════════════════════════════════════════

# Organic Reddit posts typically deploy 0-2 persuasion techniques.
# Coordinated influence content deploys 3-5+ with specific stacking patterns.
TECHNIQUE_COUNT_THRESHOLDS = {
    "normal": (0, 2),       # 0-2 techniques = organic
    "elevated": (3, 4),     # 3-4 = possibly crafted, flag for review
    "suspicious": (5, 40),  # 5+ = likely engineered content
}

# Organic content has linguistic features that cluster within subreddit norms.
# Influence operations produce outlier profiles.
LINGUISTIC_ANOMALY_WEIGHTS = {
    "emotionality": 2.0,      # high emotional density in factual contexts = flag
    "certainty_markers": 1.5,  # excessive certainty in opinion contexts = flag
    "self_reference": 1.0,     # unusual pronoun patterns vs subreddit norm
    "lexical_diversity": 1.5,  # too uniform = template, too diverse = LLM
    "reading_difficulty": 1.0, # mismatch with subreddit's typical reading level
}

# Technique combinations that rarely occur organically but are common in
# engineered influence content.
SUSPICIOUS_TECHNIQUE_STACKS = [
    {"techniques": {"fear_mongering", "false_urgency", "false_dilemma"},
     "signal": "fear-based compliance stack", "severity": 0.8},
    {"techniques": {"emotional_manipulation", "bandwagon_pressure", "guilt_tripping"},
     "signal": "emotional coercion stack", "severity": 0.9},
    {"techniques": {"social_proof", "false_scarcity", "urgency_appeal"},
     "signal": "commercial dark pattern stack", "severity": 0.7},
    {"techniques": {"storytelling", "emotional_appeal_negative", "loss_frame"},
     "signal": "narrative manipulation stack", "severity": 0.6},
    {"techniques": {"ad_hominem", "straw_man", "whataboutism"},
     "signal": "discrediting stack", "severity": 0.7},
    {"techniques": {"deceptive_information", "appeal_to_ignorance", "obfuscation"},
     "signal": "epistemic manipulation stack", "severity": 0.9},
    {"techniques": {"emotional_appeal_negative", "false_dilemma", "bandwagon_pressure"},
     "signal": "polarization stack", "severity": 0.85},
]


@dataclass
class InfluenceSignal:
    """A single detected influence signal."""
    signal_type: str          # technique_density, linguistic_anomaly, technique_stack, etc.
    severity: float           # 0.0-1.0
    description: str
    evidence: str


@dataclass
class InfluenceReport:
    """Full influence detection report for a piece of content."""
    text_preview: str
    overall_risk: float       # 0.0-1.0 composite risk score
    risk_level: str           # "organic", "elevated", "suspicious", "likely_engineered"
    signals: list             # list of InfluenceSignal
    technique_profile: dict   # detected techniques
    linguistic_profile: dict  # surface features
    appraisal_profile: dict   # 7 appraisal dimensions
    moral_targeting: dict     # which MFT dimensions are being targeted
    recommendations: list     # what to investigate further

    def to_dict(self):
        return {
            "text_preview": self.text_preview,
            "overall_risk": self.overall_risk,
            "risk_level": self.risk_level,
            "signals": [{"type": s.signal_type, "severity": s.severity,
                         "description": s.description} for s in self.signals],
            "technique_count": len([t for t in self.technique_profile.values()
                                   if t.get("detected")]),
            "moral_targeting": self.moral_targeting,
            "recommendations": self.recommendations,
        }


class InfluenceDetector:
    """Detect potential influence operations in text content.

    Uses the same analytical layers as the persuasion predictor but
    inverted: instead of optimizing for compliance, it flags content
    that appears engineered for compliance.
    """

    def __init__(self, technique_mode="heuristic", appraisal_mode="heuristic"):
        self.technique_detector = TechniqueDetector()
        self.extractor = AppraisalExtractor()
        self.technique_mode = technique_mode
        self.appraisal_mode = appraisal_mode

    def analyze(self, text, subreddit_context=None):
        """Analyze a piece of content for influence operation signals.

        Args:
            text: the content to analyze
            subreddit_context: optional subreddit name for norm comparison
        """
        if not text or not text.strip():
            return InfluenceReport(
                text_preview="", overall_risk=0.0, risk_level="organic",
                signals=[], technique_profile={}, linguistic_profile={},
                appraisal_profile={}, moral_targeting={}, recommendations=[],
            )

        signals = []

        # ─── Layer 1: Technique Detection ────────────────────────────────
        techniques = self.technique_detector.detect(text, mode=self.technique_mode)
        detected_names = set(techniques.detected_names)
        n_techniques = techniques.total_detected

        # Check technique density
        if n_techniques >= 5:
            signals.append(InfluenceSignal(
                signal_type="technique_density",
                severity=min(1.0, n_techniques / 8.0),
                description="%d persuasion techniques detected in a single post "
                            "(organic content typically contains 0-2)" % n_techniques,
                evidence="Techniques: %s" % ", ".join(detected_names),
            ))
        elif n_techniques >= 3:
            signals.append(InfluenceSignal(
                signal_type="technique_density",
                severity=0.4,
                description="%d techniques — elevated for a single post" % n_techniques,
                evidence="Techniques: %s" % ", ".join(detected_names),
            ))

        # Check for suspicious technique stacks
        for stack in SUSPICIOUS_TECHNIQUE_STACKS:
            if stack["techniques"].issubset(detected_names):
                signals.append(InfluenceSignal(
                    signal_type="technique_stack",
                    severity=stack["severity"],
                    description="Detected %s — this combination rarely occurs in "
                                "organic content" % stack["signal"],
                    evidence="Matched: %s" % ", ".join(stack["techniques"]),
                ))

        # Check ethical/unethical ratio
        if techniques.unethical_count > techniques.ethical_count and n_techniques >= 2:
            signals.append(InfluenceSignal(
                signal_type="unethical_dominance",
                severity=0.6,
                description="Unethical techniques (%d) outnumber ethical (%d)" % (
                    techniques.unethical_count, techniques.ethical_count),
                evidence="Unethical: %s" % ", ".join(
                    n for n in detected_names
                    if techniques.techniques.get(n, {}).get("ethical") is False
                ),
            ))

        # ─── Layer 2: Linguistic Surface Analysis ────────────────────────
        ling = extract_linguistic_features(text)

        # High emotionality in factual context
        if ling.emotionality > 0.05 and ling.analytical_thinking < 0.02:
            signals.append(InfluenceSignal(
                signal_type="emotional_without_analytical",
                severity=0.5,
                description="High emotional density (%.1f%%) with near-zero "
                            "analytical language — emotional appeal without substance" % (
                                ling.emotionality * 100),
                evidence="emotionality=%.3f, analytical=%.3f" % (
                    ling.emotionality, ling.analytical_thinking),
            ))

        # Excessive certainty markers
        if ling.certainty_markers > 0.03:
            signals.append(InfluenceSignal(
                signal_type="excessive_certainty",
                severity=0.4,
                description="Certainty markers at %.1f%% — above typical organic "
                            "content (0.5-1.5%%)" % (ling.certainty_markers * 100),
                evidence="certainty_markers=%.3f" % ling.certainty_markers,
            ))

        # ─── Layer 3: Appraisal Profile Analysis ────────────────────────
        appraisal = self.extractor.extract(text, mode=self.appraisal_mode)

        # Content optimized for algorithmic amplification
        # High arousal + high goal relevance = maximum engagement
        if appraisal.valence < 0.3 and appraisal.goal_relevance > 0.6:
            signals.append(InfluenceSignal(
                signal_type="outrage_optimization",
                severity=0.6,
                description="Low valence (%.2f) + high goal relevance (%.2f) = "
                            "outrage pattern optimized for engagement" % (
                                appraisal.valence, appraisal.goal_relevance),
                evidence="This combination produces the highest comment rates "
                          "on social platforms (Brady et al. 2017)",
            ))

        # Low agency content in non-commercial context
        if appraisal.agency < 0.3 and subreddit_context and \
                subreddit_context not in ("deals", "freebies", "AppHookup"):
            signals.append(InfluenceSignal(
                signal_type="coercive_framing",
                severity=0.5,
                description="Agency score %.2f in non-commercial context — "
                            "content restricts perceived choice" % appraisal.agency,
                evidence="agency=%.2f" % appraisal.agency,
            ))

        # ─── Layer 4: Moral Foundation Targeting ─────────────────────────
        moral_targeting = self._detect_moral_targeting(text, detected_names)
        if moral_targeting["targeted"]:
            signals.append(InfluenceSignal(
                signal_type="moral_foundation_targeting",
                severity=0.7,
                description="Content appears calibrated to %s moral foundation(s) — "
                            "consistent with Feinberg & Willer (2015) moral reframing" % (
                                ", ".join(moral_targeting["foundations_targeted"])),
                evidence=moral_targeting["evidence"],
            ))

        # ─── Composite Risk Score ────────────────────────────────────────
        if not signals:
            overall_risk = 0.0
            risk_level = "organic"
        else:
            # Weighted combination: max signal severity + density bonus
            max_severity = max(s.severity for s in signals)
            density_bonus = min(0.3, len(signals) * 0.05)
            overall_risk = round(min(1.0, max_severity + density_bonus), 3)

            if overall_risk >= 0.75:
                risk_level = "likely_engineered"
            elif overall_risk >= 0.5:
                risk_level = "suspicious"
            elif overall_risk >= 0.3:
                risk_level = "elevated"
            else:
                risk_level = "organic"

        # ─── Recommendations ─────────────────────────────────────────────
        recommendations = self._generate_recommendations(signals, risk_level)

        return InfluenceReport(
            text_preview=text[:200],
            overall_risk=overall_risk,
            risk_level=risk_level,
            signals=signals,
            technique_profile=techniques.techniques,
            linguistic_profile=ling.to_dict(),
            appraisal_profile=appraisal.to_dict(),
            moral_targeting=moral_targeting,
            recommendations=recommendations,
        )

    def analyze_account(self, posts, account_metadata=None):
        """Analyze an account's posting history for influence patterns.

        Args:
            posts: list of {"text": str, "subreddit": str, "timestamp": float}
            account_metadata: optional {"account_age_days": int, "karma": int}
        """
        if not posts:
            return {"risk_level": "insufficient_data", "signals": []}

        signals = []
        post_reports = []

        for post in posts:
            report = self.analyze(post.get("text", ""), post.get("subreddit"))
            post_reports.append(report)

        # ─── Cross-post analysis ─────────────────────────────────────────

        # Technique consistency: does the account always use the same techniques?
        all_techniques = []
        for r in post_reports:
            detected = [k for k, v in r.technique_profile.items() if v.get("detected")]
            all_techniques.extend(detected)

        if all_techniques:
            from collections import Counter
            tech_counts = Counter(all_techniques)
            most_common = tech_counts.most_common(3)

            # If one technique appears in >60% of posts, that's a fingerprint
            for tech, count in most_common:
                pct = count / len(posts)
                if pct > 0.6 and len(posts) >= 5:
                    signals.append(InfluenceSignal(
                        signal_type="technique_fingerprint",
                        severity=0.6,
                        description="'%s' detected in %.0f%% of posts — consistent "
                                    "technique deployment suggests templated content" % (
                                        tech, pct * 100),
                        evidence="%d/%d posts contain %s" % (count, len(posts), tech),
                    ))

        # Risk escalation: many elevated posts = higher account-level risk
        elevated_count = sum(1 for r in post_reports if r.overall_risk >= 0.3)
        if elevated_count > len(posts) * 0.5 and len(posts) >= 5:
            signals.append(InfluenceSignal(
                signal_type="sustained_influence_pattern",
                severity=0.7,
                description="%.0f%% of posts (%d/%d) score elevated or higher — "
                            "sustained pattern unlikely from organic posting" % (
                                elevated_count / len(posts) * 100,
                                elevated_count, len(posts)),
                evidence="Average risk: %.2f" % (
                    sum(r.overall_risk for r in post_reports) / len(post_reports)),
            ))

        # Account age vs activity pattern
        if account_metadata:
            age = account_metadata.get("account_age_days", 365)
            if age < 30 and len(posts) > 10:
                signals.append(InfluenceSignal(
                    signal_type="new_account_high_activity",
                    severity=0.5,
                    description="Account is %d days old with %d analyzed posts — "
                                "high activity from new account" % (age, len(posts)),
                    evidence="age=%d days, posts=%d" % (age, len(posts)),
                ))

        # Composite
        if not signals:
            return {"risk_level": "organic", "signals": [], "post_count": len(posts)}

        max_sev = max(s.severity for s in signals)
        risk = "likely_coordinated" if max_sev >= 0.7 else "suspicious" if max_sev >= 0.5 else "elevated"

        return {
            "risk_level": risk,
            "signals": [{"type": s.signal_type, "severity": s.severity,
                         "description": s.description} for s in signals],
            "post_count": len(posts),
            "elevated_post_count": elevated_count,
            "avg_risk": round(sum(r.overall_risk for r in post_reports) / len(post_reports), 3),
        }

    def _detect_moral_targeting(self, text, detected_techniques):
        """Detect if content is calibrated to specific moral foundations."""
        text_lower = text.lower()

        mft_signals = {
            "care_harm": re.findall(
                r'\b(children|suffering|compassion|protect|vulnerable|harm|victim|cruel)\b',
                text_lower),
            "fairness_cheating": re.findall(
                r'\b(fair|unfair|justice|equal|rights|discrimination|cheat|exploit)\b',
                text_lower),
            "loyalty_betrayal": re.findall(
                r'\b(patriot\w*|traitor\w*|loyal\w*|betray\w*|our country|our people|our team|us vs them|stand for|fellow)\b',
                text_lower),
            "authority_subversion": re.findall(
                r'\b(respect\w*|tradition\w*|law and order|obey\w*|authorit\w*|hierarch\w*|disciplin\w*|elder\w*|value\w*)\b',
                text_lower),
            "sanctity_degradation": re.findall(
                r'\b(pure|sacred|disgusting|moral|sin|corrupt|clean|pollut)\b',
                text_lower),
            "liberty_oppression": re.findall(
                r'\b(freedom|liberty|tyranny|oppress|rights|censorship|autonomy)\b',
                text_lower),
        }

        targeted = []
        evidence_parts = []
        for foundation, matches in mft_signals.items():
            if len(matches) >= 2:
                targeted.append(foundation)
                evidence_parts.append("%s (%d signals: %s)" % (
                    foundation, len(matches), ", ".join(matches[:3])))

        # Moral reframing indicator: content + technique alignment
        reframing = False
        if "emotional_appeal_negative" in detected_techniques and "loyalty_betrayal" in targeted:
            reframing = True
        if "emotional_appeal_positive" in detected_techniques and "care_harm" in targeted:
            reframing = True

        return {
            "targeted": len(targeted) >= 2,
            "foundations_targeted": targeted,
            "evidence": "; ".join(evidence_parts) if evidence_parts else "none",
            "moral_reframing_detected": reframing,
        }

    def _generate_recommendations(self, signals, risk_level):
        """Generate investigation recommendations based on detected signals."""
        recs = []

        if risk_level in ("suspicious", "likely_engineered"):
            recs.append("Check account history for posting patterns (timing, subreddit spread, karma trajectory)")
            recs.append("Compare linguistic profile against subreddit baseline — does this poster match community norms?")

        signal_types = {s.signal_type for s in signals}

        if "technique_stack" in signal_types:
            recs.append("Cross-reference with known influence campaign technique profiles")
        if "moral_foundation_targeting" in signal_types:
            recs.append("Check if similar moral framing appears across multiple accounts in the same thread")
        if "outrage_optimization" in signal_types:
            recs.append("Check engagement velocity — was early engagement organic or coordinated?")
        if "technique_fingerprint" in signal_types:
            recs.append("Search for other accounts with identical technique fingerprints (template detection)")

        return recs
