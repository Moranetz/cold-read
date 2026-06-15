"""
Cold Read — sales-shaped adapter over the Persuasion-Max engine.

Pure, offline, deterministic. No network, no API keys. Given a cold message it
returns: how five buyer archetypes are predicted to respond, which persuasion
mechanics the copy actually fires, and the single highest-leverage fix.

The engine itself is vendored unmodified under ../engine/core (see
engine/PROVENANCE.md). This file is the only translation layer between the
research engine's vocabulary and the outbound-sales surface.
"""
from __future__ import annotations
import os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ENGINE = os.path.normpath(os.path.join(_HERE, "..", "engine"))
if _ENGINE not in sys.path:
    sys.path.insert(0, _ENGINE)

from core.limbic_cascade import LimbicCascade            # noqa: E402
from core.appraisal_extractor import AppraisalExtractor  # noqa: E402
from core.circuit_predictor import CircuitPredictor      # noqa: E402
from core.unified_auditor import UnifiedPersuasionAuditor # noqa: E402
from core.preset_personas import get_persona             # noqa: E402

# --- Buyer archetypes: the 5 commercial personas, in sales language ----------
# Each maps to a real RecipientProfile preset inside the engine. The political
# presets are intentionally excluded — this surface is B2B outbound only.
BUYERS = [
    {"key": "impulse_buyer",        "name": "The Champion",
     "role": "Internal advocate / line manager",
     "blurb": "Feels the pain daily, moves on conviction, forwards your email upward."},
    {"key": "skeptical_researcher", "name": "The Evaluator",
     "role": "Technical / product buyer",
     "blurb": "Distrusts claims, wants proof and specifics, punishes hype."},
    {"key": "price_hunter",         "name": "The Economic Buyer",
     "role": "Procurement / Finance / CFO",
     "blurb": "Reads everything through cost and ROI; indifferent to vision."},
    {"key": "brand_loyalist",       "name": "The Incumbent User",
     "role": "Happy with their current vendor",
     "blurb": "Status-quo bias; a switch has to clear a high bar to feel worth it."},
    {"key": "social_shopper",       "name": "The Consensus Buyer",
     "role": "Committee / peer-driven",
     "blurb": "Moves when peers move; social proof and 'who else' carry the weight."},
]

# 7 appraisal dimensions, in operator language for the "what to fix" surface.
DIM_LABEL = {
    "novelty":           "pattern interrupt",
    "valence":           "tone / positivity",
    "goal_relevance":    "relevance to their job",
    "coping_potential":  "feels easy to act on",
    "agency":            "their sense of control",
    "certainty":         "clarity / specificity",
    "temporal_proximity":"urgency / timing",
}

_cascade  = LimbicCascade(extraction_mode="heuristic")
_appraise = AppraisalExtractor()
_circuit  = CircuitPredictor()
_auditor  = UnifiedPersuasionAuditor()


def _pct(x):
    try:
        return round(float(x) * 100, 1)
    except (TypeError, ValueError):
        return None


def _mechanics(text):
    """Collapse the auditor's three buckets into one clean 'firing' list."""
    audit = _auditor.audit(text)
    out = []
    buckets = {
        "tactical_stimulus":      "stimulus",
        "psychological_principles": "psychological",
        "linguistic_patterns":    "linguistic",
    }
    for bucket, cat in buckets.items():
        for name, data in (audit.get(bucket) or {}).items():
            if not isinstance(data, dict):
                continue
            score = data.get("score", 0) or 0
            intensity = (data.get("intensity") or "").upper()
            if score and score > 0 and intensity not in ("NONE", "ABSTRACT", "NEUTRAL"):
                out.append({
                    "name": name.replace("_", " ").title(),
                    "category": cat,
                    "intensity": intensity.title(),
                    "score": round(float(score), 1),
                })
    out.sort(key=lambda m: m["score"], reverse=True)
    composite = audit.get("composite_scores") or {}
    return out, composite, list(audit.get("red_flags") or [])


def score(text: str) -> dict:
    """Score a cold message. Returns the full sales-shaped result dict."""
    text = (text or "").strip()
    if not text:
        return {"error": "empty"}

    result    = _cascade.analyze(text)
    rdict     = result.to_dict()
    appraisal = _appraise.extract(text)

    # per-buyer prediction
    buyers = []
    for b in BUYERS:
        pred = _circuit.predict(appraisal, recipient=get_persona(b["key"]))
        buyers.append({
            **{k: b[k] for k in ("key", "name", "role", "blurb")},
            "reply_likelihood":   _pct(pred.immediate_compliance),
            "followup_receptive": _pct(pred.repeat_compliance),
            "annoyance_risk":     _pct(pred.retaliation_probability),
        })
    buyers.sort(key=lambda x: (x["reply_likelihood"] or 0), reverse=True)

    mechanics, composite, red_flags = _mechanics(text)

    # highest-leverage fix
    fix = None
    tf = getattr(result, "top_fix", None)
    if tf is not None:
        fix = {
            "direction":  tf.direction,
            "dimension":  tf.dimension,
            "dimension_label": DIM_LABEL.get(tf.dimension, tf.dimension.replace("_", " ")),
            "from":       round(tf.current_value, 2),
            "to":         round(tf.projected_value, 2),
            "delta_reply": _pct(tf.delta_immediate_compliance),
        }

    weak = rdict.get("weakest_dimension")
    if isinstance(weak, (list, tuple)) and weak:
        weak = weak[0]
    return {
        "ok": True,
        "effectiveness": _pct(rdict.get("effectiveness")),
        "friction": _pct(rdict.get("insula_disgust_signal")),  # 'reads as a pitch' signal
        "appraisal": {
            DIM_LABEL.get(k, k): round(float(v), 2)
            for k, v in (rdict.get("appraisal") or {}).items()
        },
        "weakest": DIM_LABEL.get(weak, weak),
        "buyers": buyers,
        "spread": round((buyers[0]["reply_likelihood"] or 0) - (buyers[-1]["reply_likelihood"] or 0), 1),
        "mechanics": mechanics,
        "red_flags": red_flags,
        "fix": fix,
    }


def list_buyers():
    return BUYERS


if __name__ == "__main__":
    import json
    sample = ("Hi Sarah, noticed Acme just raised your Series B — congrats. "
              "Most RevOps teams your size are still stitching forecasts together by hand. "
              "We cut that to one dashboard. Worth 15 minutes Thursday?")
    print(json.dumps(score(sample), indent=2))
