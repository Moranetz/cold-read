from __future__ import annotations
"""
Mechanical Extensions — Full surface without editorial filtering
==================================================================
Each function maps a specific mechanical relationship.
No prescriptions. No warnings. Consequences only.

1. Agency decomposition: coercive vs normative reduction
2. Threat-action coupling: avoidance → compliance when escape = desired action
3. Deliberation suppression: computed function of pressure, load, arousal
4. Somatic marker overwrite protocol: reconsolidation mechanics
5. Prediction error engineering: optimal expectation-reality gaps
6. Loss frame conversion: gain→loss reframing with compliance delta
7. Flip potential: how easily a message can be reappropriated against the sender
8. Confirmation bias durability: how much stronger a frame gets with future events
"""

import re
import math
from dataclasses import dataclass
from typing import Optional

from core.appraisal_extractor import AppraisalScores


# ═══════════════════════════════════════════════════════════════════════════════
# 1. AGENCY DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════
# "You must complete this step" (coercive) and "Most people complete this step"
# (normative) both lower agency. Only the first triggers disgust-retaliation.

@dataclass
class AgencyDecomposition:
    raw_agency: float                # overall agency score 0-1
    coercive_component: float        # agency reduction via constraint (triggers insula)
    normative_component: float       # agency reduction via social proof/defaults (doesn't)
    insula_trigger_probability: float  # probability the disgust circuit fires
    retaliation_risk_multiplier: float  # how much retaliation risk is amplified


def decompose_agency(agency_score, text=""):
    """Split agency into coercive vs normative components.

    Coercive markers: forced flows, hidden exits, countdown timers,
    "you must", "required", confirmshaming.
    Normative markers: "most people", defaults, "recommended",
    pre-selected options, social proof framing.
    """
    import re

    coercive_signals = re.findall(
        r'\b(must|required|mandatory|forced?|cannot|last chance|'
        r'don.t miss|no option|are you sure|you.ll lose)\b',
        text, re.I
    )
    normative_signals = re.findall(
        r'\b(most people|recommended|popular|default|suggested|'
        r'others (chose|prefer)|typically|usually chosen|best seller)\b',
        text, re.I
    )

    n_coercive = len(coercive_signals)
    n_normative = len(normative_signals)
    total_signals = max(n_coercive + n_normative, 1)

    agency_reduction = 1.0 - agency_score  # how much agency is reduced from maximum

    coercive_fraction = n_coercive / total_signals if total_signals > 0 else 0.5
    normative_fraction = 1.0 - coercive_fraction

    coercive_component = agency_reduction * coercive_fraction
    normative_component = agency_reduction * normative_fraction

    # Insula fires on coercive reduction, not normative
    # Threshold effect: below agency 0.3, insula fires steeply
    if agency_score < 0.3:
        insula_trigger = coercive_fraction * (0.3 - agency_score) / 0.3
    else:
        insula_trigger = coercive_fraction * 0.05  # minimal at high agency

    # Retaliation risk multiplier: 1.0 = baseline, >1.0 = amplified
    retaliation_mult = 1.0 + coercive_component * 2.0

    return AgencyDecomposition(
        raw_agency=round(agency_score, 3),
        coercive_component=round(coercive_component, 3),
        normative_component=round(normative_component, 3),
        insula_trigger_probability=round(min(1.0, insula_trigger), 3),
        retaliation_risk_multiplier=round(retaliation_mult, 3),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. THREAT-ACTION COUPLING
# ═══════════════════════════════════════════════════════════════════════════════
# When avoidance fires AND the prescribed action IS the escape behavior,
# avoidance produces COMPLIANCE, not rejection.

@dataclass
class ThreatActionResult:
    avoidance_score: float
    coping_potential: float
    temporal_proximity: float
    threat_coupled: bool             # is the desired action the escape behavior?
    avoidance_compliance: float      # compliance probability FROM avoidance circuit
    avoidance_rejection: float       # rejection probability (no escape behavior offered)


def compute_threat_action_coupling(
    avoidance_score,
    coping_potential,
    temporal_proximity,
    action_is_escape=False,
):
    """When avoidance is high AND the user CAN act AND the action IS the escape,
    avoidance produces compliance.

    This is how security notifications, health warnings, insurance upsells,
    and antivirus popups work. The amygdala fires threat, and the CTA is
    positioned as the resolution.
    """
    if not action_is_escape or avoidance_score < 0.1:
        return ThreatActionResult(
            avoidance_score=round(avoidance_score, 3),
            coping_potential=round(coping_potential, 3),
            temporal_proximity=round(temporal_proximity, 3),
            threat_coupled=False,
            avoidance_compliance=0.0,
            avoidance_rejection=round(avoidance_score, 3),
        )

    # Threat-action coupling: avoidance drives compliance when
    # (1) threat is real/perceived, (2) user can act, (3) action resolves threat
    coupling_strength = (
        avoidance_score * 0.4
        + coping_potential * 0.3
        + temporal_proximity * 0.3
    )

    avoidance_compliance = round(min(1.0, coupling_strength), 4)
    avoidance_rejection = round(max(0.0, avoidance_score - avoidance_compliance), 4)

    return ThreatActionResult(
        avoidance_score=round(avoidance_score, 3),
        coping_potential=round(coping_potential, 3),
        temporal_proximity=round(temporal_proximity, 3),
        threat_coupled=True,
        avoidance_compliance=avoidance_compliance,
        avoidance_rejection=avoidance_rejection,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DELIBERATION SUPPRESSION
# ═══════════════════════════════════════════════════════════════════════════════
# Temporal pressure, cognitive load, and emotional arousal suppress dlPFC.

@dataclass
class DeliberationSuppression:
    base_deliberation: float
    temporal_suppression: float      # from time pressure
    load_suppression: float          # from cognitive overload + defaults
    arousal_suppression: float       # from emotional intensity
    residual_deliberation: float     # what remains after suppression
    default_compliance_boost: float  # if a default is present, compliance with it


def compute_deliberation_suppression(
    deliberation_score,
    temporal_proximity=0.5,
    information_load=0.3,
    emotional_arousal=0.5,
    has_default_option=False,
):
    """Compute how much deliberation is suppressed by pressure, load, and arousal.

    When deliberation is suppressed AND a default exists, the user takes
    the default. This is the mechanism behind 'Most Popular' badges,
    pre-selected tiers, and opt-out (vs opt-in) architectures.
    """
    # Temporal suppression: urgency prevents ACC from completing its loop
    temporal_supp = temporal_proximity * 0.35

    # Load suppression: too many options overwhelms dlPFC working memory
    # But ONLY suppresses deliberation (doesn't increase approach/avoidance)
    # Instead, when paired with a default, it routes to default compliance
    load_supp = max(0.0, information_load - 0.4) * 0.4

    # Arousal suppression: high emotional states inhibit prefrontal function
    # Amygdala hyperactivation → ventromedial inhibition of dlPFC
    arousal_supp = max(0.0, emotional_arousal - 0.5) * 0.5

    total_suppression = min(1.0, temporal_supp + load_supp + arousal_supp)
    residual = max(0.0, deliberation_score * (1.0 - total_suppression))

    # Default compliance: when deliberation is suppressed and a default
    # exists, the path of least resistance = the default
    default_boost = 0.0
    if has_default_option:
        default_boost = total_suppression * 0.6  # 60% of suppressed deliberation → default

    return DeliberationSuppression(
        base_deliberation=round(deliberation_score, 3),
        temporal_suppression=round(temporal_supp, 3),
        load_suppression=round(load_supp, 3),
        arousal_suppression=round(arousal_supp, 3),
        residual_deliberation=round(residual, 3),
        default_compliance_boost=round(default_boost, 3),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SOMATIC MARKER OVERWRITE PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════════
# Based on Nader et al. 2000: reactivated memories enter a labile state.

@dataclass
class OverwriteProtocol:
    current_marker_valence: float
    current_marker_strength: float
    reactivation_intensity_required: float  # how strongly to trigger the memory
    reconsolidation_window_hours: float     # time window for delivering the correction
    minimum_prediction_error: float         # how much better the new experience must be
    overwrite_probability: float            # estimated success rate


def compute_marker_overwrite(marker_valence, marker_strength, marker_age_hours=0):
    """Given a negative marker, compute the overwrite protocol.

    Nader et al. 2000: reactivated memories enter a labile state (~5-6 hours)
    where they can be modified. Delivering a positive prediction error during
    this window updates the emotional tag.

    Older markers are harder to overwrite (more consolidated).
    Stronger markers require stronger prediction errors to shift.
    """
    if marker_valence >= 0:
        return OverwriteProtocol(
            current_marker_valence=round(marker_valence, 3),
            current_marker_strength=round(marker_strength, 3),
            reactivation_intensity_required=0.0,
            reconsolidation_window_hours=0.0,
            minimum_prediction_error=0.0,
            overwrite_probability=1.0,  # no negative marker to overwrite
        )

    # Reactivation intensity: must be strong enough to trigger retrieval
    # but not so strong it reinforces the negative marker
    reactivation = 0.3 + abs(marker_valence) * 0.4
    reactivation = round(min(0.8, reactivation), 3)

    # Reconsolidation window: ~5-6 hours (Nader et al.)
    # Shorter for recent markers, longer for old ones
    age_factor = min(1.0, marker_age_hours / 720)  # normalize to 30 days
    window = 5.0 + age_factor * 1.0  # 5-6 hours

    # Minimum prediction error: the new experience must exceed the predicted
    # (negative) outcome by this amount to shift the marker
    min_pe = abs(marker_valence) * marker_strength * 1.2
    min_pe = round(min(1.5, min_pe), 3)

    # Overwrite probability: decreases with marker strength and age
    base_prob = 0.7
    strength_penalty = marker_strength * 0.3
    age_penalty = age_factor * 0.2
    prob = max(0.1, base_prob - strength_penalty - age_penalty)

    return OverwriteProtocol(
        current_marker_valence=round(marker_valence, 3),
        current_marker_strength=round(marker_strength, 3),
        reactivation_intensity_required=reactivation,
        reconsolidation_window_hours=round(window, 1),
        minimum_prediction_error=min_pe,
        overwrite_probability=round(prob, 3),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. PREDICTION ERROR ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════
# Deliberately set expectation at step N to maximize positive PE at step N+1.

@dataclass
class PredictionErrorDesign:
    step_index: int
    current_approach: float
    next_approach: float
    raw_pe: float                    # actual approach delta
    optimal_expectation: float       # what the user should expect at this step
    optimal_delivery: float          # what they should actually get at next step
    dopamine_signal_magnitude: float # predicted dopamine from the PE
    inconsistency_risk: float        # risk of insula flagging the gap as fake


def engineer_prediction_errors(approach_scores):
    """For a sequence of approach activation scores, compute the optimal
    expectation-reality gaps at each transition.

    Too small a gap: no dopamine signal (habituation).
    Too large a gap: insula flags inconsistency (feels fake/bait-and-switch).
    Optimal: 0.1-0.3 positive PE per transition.
    """
    results = []
    for i in range(len(approach_scores) - 1):
        current = approach_scores[i]
        next_val = approach_scores[i + 1]
        raw_pe = next_val - current

        # Optimal PE: 0.15-0.25 positive delta per step
        # This is the range where dopamine fires without triggering suspicion
        optimal_pe = 0.20

        # To achieve this, the expectation should be SET at:
        # optimal_expectation = next_actual - optimal_pe
        optimal_expectation = max(0.0, next_val - optimal_pe)

        # Dopamine signal: proportional to PE but with diminishing returns
        # and negative for negative PE (disappointment)
        if raw_pe > 0:
            dopamine = min(1.0, raw_pe * 3.0)  # 3x amplification, capped
        else:
            dopamine = max(-1.0, raw_pe * 4.0)  # 4x amplification for losses (loss aversion)

        # Inconsistency risk: if the gap between expectation and reality
        # is too large (>0.4), the insula flags it
        gap = abs(next_val - optimal_expectation)
        inconsistency = max(0.0, (gap - 0.3) * 2.0)

        results.append(PredictionErrorDesign(
            step_index=i,
            current_approach=round(current, 3),
            next_approach=round(next_val, 3),
            raw_pe=round(raw_pe, 3),
            optimal_expectation=round(optimal_expectation, 3),
            optimal_delivery=round(next_val, 3),
            dopamine_signal_magnitude=round(dopamine, 3),
            inconsistency_risk=round(min(1.0, inconsistency), 3),
        ))

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 6. LOSS FRAME CONVERSION
# ═══════════════════════════════════════════════════════════════════════════════
# Kahneman & Tversky: losses produce ~2x stronger behavioral response than gains.

@dataclass
class LossFrameResult:
    original_text: str
    loss_framed_text: str
    gain_framed_text: str
    predicted_compliance_delta: float  # positive = loss frame outperforms gain
    loss_aversion_multiplier: float    # how much stronger the loss frame is


# Common gain→loss frame patterns
_GAIN_LOSS_PATTERNS = [
    # (gain pattern, loss pattern, domain)
    ("save", "lose", "financial"),
    ("get", "miss", "acquisition"),
    ("earn", "forfeit", "reward"),
    ("gain", "lose", "general"),
    ("keep", "lose", "retention"),
    ("protect", "risk", "security"),
    ("unlock", "lose access to", "feature"),
    ("start", "miss out on", "action"),
    ("enjoy", "go without", "experience"),
]


def convert_to_loss_frame(text, compliance_delta_estimate=0.12):
    """Convert a gain-framed message to its loss-frame equivalent.

    The compliance delta is ~1.5-2.5x (Kahneman & Tversky 1979).
    On a probability scale, gain-framed CTAs convert at ~X%,
    loss-framed equivalents at ~X% + delta.

    Also provides the inverse: loss→gain conversion for contexts
    where you want to suppress amygdala activation.
    """
    import re

    loss_text = text
    gain_text = text

    for gain_word, loss_word, domain in _GAIN_LOSS_PATTERNS:
        # Gain → Loss
        loss_text = re.sub(
            r'\b(%s)\b' % re.escape(gain_word),
            loss_word,
            loss_text,
            flags=re.I,
        )
        # Loss → Gain (inverse)
        gain_text = re.sub(
            r'\b(%s)\b' % re.escape(loss_word),
            gain_word,
            gain_text,
            flags=re.I,
        )

    # Loss aversion multiplier: ~2x is the Kahneman & Tversky estimate
    # Context-dependent: financial losses feel worse than feature losses
    multiplier = 2.0

    return LossFrameResult(
        original_text=text,
        loss_framed_text=loss_text,
        gain_framed_text=gain_text,
        predicted_compliance_delta=compliance_delta_estimate,
        loss_aversion_multiplier=multiplier,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. FLIP POTENTIAL
# ═══════════════════════════════════════════════════════════════════════════════
# Adams (2017): Trump's kill shots had zero flip potential — "low energy",
# "crooked", "lyin'" have no context in which they are positive. By contrast,
# "dangerous" is easily flipped (dangerous → bold leader willing to act).
# Flip potential measures how easily a label or claim can be reappropriated
# by the target to mean something advantageous.
#
# High flip potential = the message could backfire if the target embraces it.
# Low flip potential = the label or claim has no positive reinterpretation.

@dataclass
class FlipPotentialResult:
    text: str
    flip_potential: float             # 0.0 (flip-proof) to 1.0 (easily flipped)
    flip_risk_level: str              # "low", "moderate", "high"
    flippable_terms: list             # specific words/phrases that could be reappropriated
    flip_mechanism: str               # how the flip would work
    recommendation: str               # how to reduce flip potential


# Terms that sound negative but have a legitimate positive reframe.
# Format: (term_pattern, positive_reframe)
_FLIPPABLE_TERMS = [
    (r'\bdangerous\b', "dangerous = decisive, willing to act when others won't"),
    (r'\baggressive\b', "aggressive = driven, competitive"),
    (r'\bcontroversial\b', "controversial = important, worth fighting over"),
    (r'\bunpredictable\b', "unpredictable = creative, not captured by establishment"),
    (r'\bbold\b', "bold already reads as positive"),
    (r'\bchallenging\b', "challenging = demanding high standards"),
    (r'\bpolarizing\b', "polarizing = someone who stands for something"),
    (r'\bintense\b', "intense = passionate, committed"),
    (r'\bhard-line\b', "hard-line = principled, won't compromise values"),
    (r'\bextreme\b', "extreme = fully committed, not half-measures"),
    (r'\bradical\b', "radical = willing to address root causes"),
    (r'\babrasive\b', "abrasive = honest, won't sugarcoat"),
    (r'\bincendiary\b', "incendiary = ignites conversation"),
    (r'\breckless\b', "reckless = moves fast, doesn't overthink"),
    (r'\bbrash\b', "brash = confident, New York-style direct"),
]

# Binary framing patterns: us-vs-them structures that can always be
# reversed by swapping which side the reader identifies with.
_BINARY_FRAMING = re.compile(
    r'\b(either|or else|you.?re (with|against)|us vs|them vs|'
    r'choose (between|sides)|no middle ground|pick a side)\b',
    re.I
)

# Comparative claims without a stable anchor — easily reversed by
# shifting the reference point.
_UNANCHORED_COMPARATIVES = re.compile(
    r'\b(more|less|better|worse|higher|lower|stronger|weaker) than\b',
    re.I
)


def compute_flip_potential(text):
    """Measure how easily this message can be turned against the sender.

    A message with high flip potential contains:
    - Labels with legitimate positive reframes (dangerous, aggressive)
    - Binary framing (us/them — just swap which side you're on)
    - Unanchored comparatives (more X than Y — shift the reference point)

    A message with low flip potential uses labels that have no positive
    context in any frame — the target of "Crooked Hillary" cannot
    embrace "crooked" as a strength. The target of "Low Energy Jeb"
    cannot reframe low energy as an asset in a presidential race.
    """
    import re as _re

    text_lower = text.lower()
    flippable_found = []
    flip_score = 0.0

    # Check for flippable terms
    for pattern, reframe in _FLIPPABLE_TERMS:
        if _re.search(pattern, text, _re.I):
            flippable_found.append({"term": pattern.strip(r'\b'), "reframe": reframe})
            flip_score += 0.15

    # Binary framing: always reversible (any us/them can be flipped)
    binary_matches = _BINARY_FRAMING.findall(text)
    if binary_matches:
        flip_score += 0.25
        flippable_found.append({
            "term": "binary framing",
            "reframe": "the target just redefines which side is 'us'",
        })

    # Unanchored comparatives: easy to reframe by shifting the baseline
    comparative_matches = _UNANCHORED_COMPARATIVES.findall(text)
    if len(comparative_matches) >= 2:
        flip_score += 0.2
        flippable_found.append({
            "term": "unanchored comparatives (%d)" % len(comparative_matches),
            "reframe": "reframe the reference point and the comparison inverts",
        })

    flip_potential = round(min(1.0, flip_score), 3)

    if flip_potential >= 0.6:
        risk_level = "high"
        mechanism = "multiple reappropriation paths available to the target"
        recommendation = "Replace flippable terms with labels that have no positive context. " \
                         "Low energy, crooked, lyin' — none of these can be embraced as strengths."
    elif flip_potential >= 0.3:
        risk_level = "moderate"
        mechanism = "at least one clear reappropriation path"
        recommendation = "Review flagged terms. Consider whether the target could run ads " \
                         "using the same language against you."
    else:
        risk_level = "low"
        mechanism = "no clear reappropriation path detected"
        recommendation = "Flip potential is low. Message is defensively stable."

    return FlipPotentialResult(
        text=text[:200],
        flip_potential=flip_potential,
        flip_risk_level=risk_level,
        flippable_terms=flippable_found,
        flip_mechanism=mechanism,
        recommendation=recommendation,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CONFIRMATION BIAS DURABILITY
# ═══════════════════════════════════════════════════════════════════════════════
# Adams (2017): the strongest frames are engineered to get stronger over time.
# "Lyin' Ted" was destined to accumulate confirmation. Every future statement
# Cruz made that could be questioned would reinforce the label. The frame
# feeds on the target's own future behavior.
#
# Confirmation bias durability measures whether a message plants a frame
# that future events will confirm — as opposed to a claim that peaks at
# send time and decays.

@dataclass
class ConfirmationBiasDurability:
    text: str
    durability_score: float           # 0.0 (one-time claim) to 1.0 (self-reinforcing frame)
    durability_level: str             # "perishable", "moderate", "durable", "compounding"
    durability_signals: list          # what makes it durable
    decay_risks: list                 # what could undermine it over time
    frame_type: str                   # "behavioral_trait", "character_label", "event_claim", "policy_claim"


# Behavioral trait language — frames a pattern, not an act.
# Trait framing produces durable frames; act framing is perishable.
_TRAIT_FRAMING = re.compile(
    r'\b(always|never|consistently|constantly|every time|keeps|continues|'
    r'still|repeatedly|pattern of|known for|history of|track record)\b',
    re.I
)

# Character labels — single-word personality attributions that apply broadly.
_CHARACTER_LABELS = re.compile(
    r'\b(liar|lyin|crooked|corrupt|weak|coward|fraud|phony|fake|incompetent|'
    r'spineless|reckless|erratic|unstable|dishonest|deceptive|arrogant|'
    r'selfish|greedy|narcissist|manipulative|hypocrite|coward|bully|'
    r'narcissistic|entitled|toxic|predatory|abusive)\b',
    re.I
)

# Event claims — specific incidents that are perishable (news cycle dependent).
_EVENT_CLAIMS = re.compile(
    r'\b(said|did|voted|refused|failed to|didn.t|at the time|back in|'
    r'last week|yesterday|recently|on (monday|tuesday|wednesday|'
    r'thursday|friday|january|february|march|april|may|june|'
    r'july|august|september|october|november|december))\b',
    re.I
)

# Future-confirming setup — primes the recipient to watch for future confirmation.
_FUTURE_CONFIRMATION_SETUP = re.compile(
    r'\b(?:watch what|mark my words|you.ll see|pay attention|notice how|'
    r'wait until|just wait|every time (?:he|she|they)|'
    r'next time (?:he|she|they)|will (?:keep|continue|always))\b',
    re.I
)


def compute_confirmation_bias_durability(text):
    """Measure how much stronger this frame gets with future events.

    Durable frames:
    - Attribute a TRAIT rather than an act (liar vs. "lied once")
    - Apply a label broad enough that future behavior confirms it
    - Prime the recipient to interpret future events through the frame
    - The target's own behavior feeds the frame (not the sender's actions)

    Perishable frames:
    - Specific event claims (news cycle dependent, fade quickly)
    - Policy claims (can be updated, reversed, explained away)
    - Opinion claims ("I disagree with X") — depend on current context

    Adams: the Trump nicknames were engineered so that the target's natural
    behavior — just existing as a politician — would confirm the label.
    This is the difference between a claim and a frame.
    """
    import re as _re

    signals = []
    decay_risks = []
    durability_score = 0.0

    # Trait framing: the highest-durability signal
    trait_matches = _TRAIT_FRAMING.findall(text)
    if trait_matches:
        durability_score += 0.35
        signals.append("trait framing (%d markers: %s)" % (
            len(trait_matches), ", ".join(trait_matches[:3])))

    # Character labels: broad attribution that future behavior will confirm
    label_matches = _CHARACTER_LABELS.findall(text)
    if label_matches:
        durability_score += 0.30
        signals.append("character labels (%s)" % ", ".join(label_matches[:3]))

    # Future confirmation setup: explicitly primes the recipient to watch for confirmation
    future_matches = _FUTURE_CONFIRMATION_SETUP.findall(text)
    if future_matches:
        durability_score += 0.25
        signals.append("future confirmation priming (%s)" % ", ".join(future_matches[:2]))

    # Event claims: a durability penalty — specific events are perishable
    event_matches = _EVENT_CLAIMS.findall(text)
    if len(event_matches) >= 3:
        durability_score -= 0.20
        decay_risks.append("event-specific language (%d instances) — tied to news cycle" % len(event_matches))

    # Policy claims without character framing: moderate decay risk
    policy_words = _re.findall(
        r'\b(policy|plan|proposal|bill|vote|legislation|platform|position)\b',
        text, _re.I)
    if policy_words and not label_matches:
        durability_score -= 0.10
        decay_risks.append("policy framing without character attribution — target can update position")

    durability_score = round(min(1.0, max(0.0, durability_score)), 3)

    # Frame type classification
    if label_matches and trait_matches:
        frame_type = "behavioral_trait"  # strongest: label + pattern
    elif label_matches:
        frame_type = "character_label"   # strong: label without pattern evidence
    elif event_matches and len(event_matches) >= 3:
        frame_type = "event_claim"       # weak: specific incident
    elif policy_words:
        frame_type = "policy_claim"      # weakest for durability
    else:
        frame_type = "behavioral_trait" if trait_matches else "general_claim"

    if durability_score >= 0.7:
        level = "compounding"
    elif durability_score >= 0.45:
        level = "durable"
    elif durability_score >= 0.2:
        level = "moderate"
    else:
        level = "perishable"

    if not decay_risks:
        decay_risks.append("no significant decay risks detected")

    return ConfirmationBiasDurability(
        text=text[:200],
        durability_score=durability_score,
        durability_level=level,
        durability_signals=signals,
        decay_risks=decay_risks,
        frame_type=frame_type,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 9. HIGH-GROUND RESPONSE
# ═══════════════════════════════════════════════════════════════════════════════
# Adams (2017): the high-ground maneuver takes the argument out of the weeds
# where you're defending specifics and elevates it to a level where everyone
# agrees — which frames you as the adult and the attacker as bickering.
#
# The mechanics:
#   - Every attack implicitly appeals to a value (fairness, competence, honesty)
#   - Rather than contesting the specific claim, you AGREE with the underlying
#     value and reframe yourself as its embodiment
#   - The attacker must now either agree (conceding the frame) or attack the
#     value itself (making them look small)
#
# Three high-ground move types:
#   1. Embrace + redirect: accept the label, redefine what it means at scale
#      ("You're right, I push hard — the country needs someone who pushes hard")
#   2. Value elevation: step above the specific claim to the principle it invokes
#      ("We all want honesty in leadership — here's what that actually looks like")
#   3. Inversion: the attack's hidden cost — name what the attacker's framing
#      actually produces if taken seriously
#      ("If pushing back makes me dangerous, what does it say that nobody else did?")

@dataclass
class HighGroundResponse:
    attack_text: str
    flip_potential: float             # from compute_flip_potential
    durability_score: float           # from compute_confirmation_bias_durability
    durability_level: str
    recommended_move: str             # "embrace", "elevate", "invert", "ignore"
    move_rationale: str               # why this move
    implicit_value: str               # what value the attack is secretly appealing to
    response_template: str            # structural template for the counter
    what_not_to_do: str               # the losing response pattern


# Value detection: every attack carries an implicit value claim.
# Detecting the value lets you occupy it before the attacker does.
_ATTACK_VALUE_MAP = [
    # (attack pattern, implicit value, high-ground territory)
    (r'\b(liar|dishonest|fake|phony|fraud|mislead|deceiv)\b',
     "honesty",
     "We all want truth. Here's what honesty actually looks like in this context."),
    (r'\b(incompetent|weak|can.?t|doesn.?t know|no idea|clueless|inexperienced)\b',
     "competence",
     "Results are what matter. Here's the track record."),
    (r'\b(dangerous|reckless|extreme|radical|aggressive|out of control)\b',
     "safety/stability",
     "Everyone wants stability. The question is what actually produces it."),
    (r'\b(selfish|greedy|corrupt|only care|in it for|self-serving)\b',
     "integrity",
     "We agree that leadership should serve people, not itself."),
    (r'\b(hypocrite|double standard|inconsistent|flip.flop|changed)\b',
     "consistency",
     "Consistency matters. Here's the through-line across every position I've taken."),
    (r'\b(arrogant|entitled|think you.?re better|who do you think)\b',
     "humility",
     "Fair point — let the work speak. Here's what actually got done."),
    (r'\b(racist|sexist|bigot|discriminat|prejudic)\b',
     "fairness",
     "We both agree fairness matters. Here's what fairness looks like in practice."),
    (r'\b(stupid|dumb|idiot|ignorant|don.?t understand|have no clue)\b',
     "intelligence/expertise",
     "Happy to show the reasoning. Here's the evidence behind the position."),
]

# Signals that the attack is personal/emotional rather than substantive —
# these respond better to ignoring or brief dismissal than engagement.
_PERSONAL_ATTACK_MARKERS = re.compile(
    r'\b(ugly|loser|pathetic|sad|fat|creep|weird|disgusting|joke|clown|trash)\b',
    re.I
)


def compute_highground_response(attack_text):
    """Given an attack, determine the optimal counter-persuasion move.

    The output tells you:
    1. Whether to engage at all (ignore perishable attacks)
    2. Which move type to use (embrace / elevate / invert)
    3. What value the attack is implicitly appealing to (so you can occupy it)
    4. A structural template for the response
    5. What the losing response pattern looks like (so you avoid it)

    The three move types:
    - EMBRACE: when flip potential is high — accept the label and redefine
      what it means at scale. Trump + "whiner" → "the country needs that."
    - ELEVATE: when the attack appeals to a real value — step up to the
      principle level and reframe yourself as its embodiment. Leaves the
      attacker fighting over details while you own the concept.
    - INVERT: when the attack has a hidden cost — name what the attacker's
      logic actually produces if taken seriously. Forces them to defend
      an absurd implication instead of pressing the original attack.
    - IGNORE: when the attack is perishable or purely personal — engaging
      amplifies it, silence lets it decay.
    """
    fp = compute_flip_potential(attack_text)
    cbd = compute_confirmation_bias_durability(attack_text)

    # Detect implicit value
    implicit_value = "general standing"
    high_ground_territory = "We agree on the underlying principle."
    for pattern, value, territory in _ATTACK_VALUE_MAP:
        if re.search(pattern, attack_text, re.I):
            implicit_value = value
            high_ground_territory = territory
            break

    # Purely personal attack — no substantive value claim
    is_personal = bool(_PERSONAL_ATTACK_MARKERS.search(attack_text))

    # ── Decision logic ───────────────────────────────────────────────────────
    if is_personal and cbd.durability_level == "perishable":
        move = "ignore"
        rationale = ("Purely personal and perishable. Engaging amplifies it. "
                     "Silence is not weakness here — it's the dominant play. "
                     "The attack dies in the news cycle.")
        template = "[No response. If forced to address: brief dismissal, redirect to substance.]"
        what_not_to_do = "Don't defend, don't explain, don't show it landed."

    elif fp.flip_potential >= 0.4:
        move = "embrace"
        rationale = ("Flip potential is %.2f — this label has a legitimate "
                     "positive reframe. Embrace it and redefine what it means "
                     "at the scale of the thing you're actually doing. "
                     "Defending against it keeps you in their frame. "
                     "Embracing it takes ownership of the frame." % fp.flip_potential)
        template = (
            "EMBRACE TEMPLATE:\n"
            "  'You're right, I [label]. [Name what that looks like at scale / "
            "why that's what the situation requires]. The alternative — [what "
            "not doing it produces] — is what we should actually be worried about.'"
        )
        what_not_to_do = ("Don't deny the label. Don't say 'I'm not X.' "
                          "That installs the image of X and puts you on defense.")

    elif cbd.durability_level in ("durable", "compounding"):
        move = "elevate"
        rationale = ("Durability score is %.2f (%s). This frame will compound "
                     "if left unchallenged. The attack appeals to '%s' — "
                     "step above the specific claim to the principle level and "
                     "occupy it before it accumulates against you." % (
                         cbd.durability_score, cbd.durability_level, implicit_value))
        template = (
            "ELEVATE TEMPLATE:\n"
            "  '%s\n"
            "  [One concrete proof point — specific, not defensive.]\n"
            "  [Optional: name the cost of the attack's framing if taken seriously.]'" % (
                high_ground_territory)
        )
        what_not_to_do = ("Don't contest the specific claim directly. "
                          "Defending the details keeps you in the weeds — "
                          "exactly where the attacker wants you.")

    elif cbd.durability_level == "perishable":
        move = "ignore"
        rationale = ("Event-based claim (durability: perishable). This is tied "
                     "to a specific incident in the news cycle. Engaging gives "
                     "it legs it doesn't have on its own.")
        template = "[If you must respond: one sentence acknowledging the concern, redirect to direction/future.]"
        what_not_to_do = ("Don't relitigate the specific event. "
                          "That's their frame and their terrain.")

    else:
        move = "invert"
        rationale = ("No clear flip potential, moderate durability. "
                     "Name the hidden cost of the attacker's logic — "
                     "what does their framing actually produce if taken seriously? "
                     "Forces them to defend an absurd implication.")
        template = (
            "INVERT TEMPLATE:\n"
            "  'If [their claim] is the standard, then [what that standard "
            "actually implies / who else it condemns / what it would require]. "
            "Is that really what we're saying?'"
        )
        what_not_to_do = ("Don't make it personal back. Don't match their "
                          "energy level — stay one register above it.")

    return HighGroundResponse(
        attack_text=attack_text[:200],
        flip_potential=fp.flip_potential,
        durability_score=cbd.durability_score,
        durability_level=cbd.durability_level,
        recommended_move=move,
        move_rationale=rationale,
        implicit_value=implicit_value,
        response_template=template,
        what_not_to_do=what_not_to_do,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# COUNTER-PERSUASION PIPELINE — Single entry point
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AttackAnalysis:
    """Full counter-persuasion analysis for an incoming attack."""
    attack_text: str
    flip_potential: float
    flip_risk_level: str
    flippable_terms: list
    durability_score: float
    durability_level: str
    frame_type: str
    recommended_move: str
    move_rationale: str
    implicit_value: str
    response_template: str
    what_not_to_do: str

    def summary(self):
        """One-paragraph summary of the analysis."""
        return (
            "ATTACK: '%s...'\n"
            "FLIP POTENTIAL: %s (%.2f) — %s\n"
            "DURABILITY: %s (%.2f) — frame type: %s\n"
            "MOVE: %s\n"
            "IMPLICIT VALUE: %s\n"
            "TEMPLATE: %s\n"
            "AVOID: %s"
        ) % (
            self.attack_text[:80],
            self.flip_risk_level, self.flip_potential,
            (", ".join(t["term"] for t in self.flippable_terms) if self.flippable_terms else "none"),
            self.durability_level, self.durability_score, self.frame_type,
            self.recommended_move.upper(),
            self.implicit_value,
            self.response_template,
            self.what_not_to_do,
        )


def analyze_attack(attack_text):
    """Full counter-persuasion pipeline for an incoming neg or attack.

    Single entry point. Pass in what someone said about you.
    Returns the optimal response strategy with structural template.

    Usage:
        result = analyze_attack("He's reckless and doesn't know what he's doing")
        print(result.summary())
    """
    hg = compute_highground_response(attack_text)

    return AttackAnalysis(
        attack_text=attack_text[:200],
        flip_potential=hg.flip_potential,
        flip_risk_level="high" if hg.flip_potential >= 0.6 else
                        "moderate" if hg.flip_potential >= 0.3 else "low",
        flippable_terms=compute_flip_potential(attack_text).flippable_terms,
        durability_score=hg.durability_score,
        durability_level=hg.durability_level,
        frame_type=compute_confirmation_bias_durability(attack_text).frame_type,
        recommended_move=hg.recommended_move,
        move_rationale=hg.move_rationale,
        implicit_value=hg.implicit_value,
        response_template=hg.response_template,
        what_not_to_do=hg.what_not_to_do,
    )
