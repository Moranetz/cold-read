from __future__ import annotations
"""
Compound Techniques — Multi-Technique Stacks with Synergy/Diminishing Returns
===============================================================================
Maps known effective technique combinations, their multipliers, and the
interaction effects between techniques when deployed together.

Three types of interaction:
    SYNERGY    — techniques amplify each other (multiplier > sum of parts)
    ADDITIVE   — techniques stack linearly (no interaction effect)
    DIMINISHING — techniques partially cancel or saturate (multiplier < sum)

Sources:
    - Ranked combinations from LINGUISTIC_PERSUASION/5_RANKINGS (40 ranks, 6 tiers)
    - Interaction discovery from calibration/results/interaction_discovery.json
    - Adams (Win Bigly): high_ground + identity_lock + thinking_past_the_sale
    - Cialdini (Pre-Suasion): unity + reciprocity + commitment_consistency
    - Voss (Never Split the Difference): labeling + calibrated_question + pacing

CALIBRATION STATUS:
    Diminishing returns curve: EMPIRICAL (interaction_discovery.json, N=8000)
        5 interactions stacked: +1.9pp AUC
        10 interactions stacked: +2.17pp AUC
        15 interactions stacked: +2.17pp AUC (saturation at ~10)

    Compound stack multipliers: UNCALIBRATED ESTIMATES
        Derived from LINGUISTIC_PERSUASION/5_RANKINGS which uses a weighted
        opinion methodology (40% effect size, 25% synergy estimate, 20%
        vulnerability depth, 15% field success). The specific multipliers
        (1.42x-2.1x) are plausible but NOT empirically measured on any
        dataset. Treat as directional guidance, not ground truth.

    Platform effectiveness per compound: UNCALIBRATED ESTIMATES
        Hand-assigned based on platform culture analysis, not engagement data.
        The technique_analyzer feedback loop is designed to calibrate these
        over time with real performance data.

    Implication: deploying more than 3 techniques per stimulus produces
    negligible lift and increases detection risk. Optimal is 2-3.
    This conclusion IS empirically supported by the interaction stacking data.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOUND STACKS — Named combinations with known multipliers
# ═══════════════════════════════════════════════════════════════════════════════
# Multiplier is relative to single-technique baseline.
# Platform ratings indicate where the compound works best (0.0-1.0).

COMPOUND_STACKS = {
    # ─── TIER 1: Critical Intensity (1.9x - 2.5x) ──────────────────────

    "deliberation_bypass": {
        "techniques": ["emotional_appeal_negative", "urgency_appeal", "authority_endorsement"],
        "multiplier": 2.1,
        "mechanism": "Emotion hijacks amygdala, urgency compresses decision window, authority suppresses questioning. Deliberation circuit drops to near-zero.",
        "platform": {"reddit": 0.15, "twitter": 0.7, "linkedin": 0.4, "substack": 0.3},
        "detection_note": "High detection on Reddit (obvious pressure). Works on Twitter in crisis/breaking contexts.",
    },
    "authority_threat": {
        "techniques": ["expert_testimony", "fear_mongering", "urgency_appeal"],
        "multiplier": 1.95,
        "mechanism": "Authority establishes credibility, fear creates threat perception, urgency prevents verification.",
        "platform": {"reddit": 0.1, "twitter": 0.6, "linkedin": 0.3, "substack": 0.2},
        "detection_note": "Classic high-pressure pattern. Flagged quickly on all but fast-scroll platforms.",
    },

    # ─── TIER 2: High Effectiveness (1.6x - 1.89x) ─────────────────────

    "ecommerce_conversion": {
        "techniques": ["social_proof", "scarcity_appeal", "urgency_appeal"],
        "multiplier": 1.85,
        "mechanism": "Social proof validates desire, scarcity creates FOMO, urgency compresses decision time. Impulse purchase bypass.",
        "platform": {"reddit": 0.1, "twitter": 0.5, "linkedin": 0.4, "substack": 0.2},
        "detection_note": "Booking.com pattern. Works in commercial context, instant detection in organic social.",
    },
    "influencer_stack": {
        "techniques": ["expert_testimony", "social_proof", "identity_lock"],
        "multiplier": 1.68,
        "mechanism": "Authority + social validation + identity framing. Recommendation feels like advice from aspirational peer.",
        "platform": {"reddit": 0.5, "twitter": 0.8, "linkedin": 0.85, "substack": 0.7},
        "detection_note": "LinkedIn native format. Works when poster has genuine credentials.",
    },
    "pricing_influence": {
        "techniques": ["anchoring", "contrast_principle", "scarcity_appeal"],
        "multiplier": 1.72,
        "mechanism": "Anchor sets high reference, contrast makes target seem cheap, scarcity prevents comparison shopping.",
        "platform": {"reddit": 0.2, "twitter": 0.4, "linkedin": 0.5, "substack": 0.4},
        "detection_note": "Obvious in organic social. Works in commercial/pricing contexts.",
    },

    # ─── TIER 3: Natural Compounds (1.4x - 1.6x) ───────────────────────
    # These are the ones that pass organic detection on social platforms.

    "adams_high_ground": {
        "techniques": ["high_ground_maneuver", "identity_lock", "thinking_past_the_sale"],
        "multiplier": 1.65,
        "mechanism": "Claim universally held value (high ground), frame compliance as identity ('people who care about X'), then discuss implementation details as if the decision is already made. Adams' core playbook from Win Bigly.",
        "platform": {"reddit": 0.7, "twitter": 0.9, "linkedin": 0.85, "substack": 0.8},
        "detection_note": "Extremely hard to detect. Feels like natural moral reasoning.",
    },
    "vulnerability_narrative": {
        "techniques": ["self_disclosure", "storytelling", "curiosity_gap"],
        "multiplier": 1.55,
        "mechanism": "Personal vulnerability builds trust (insula drops), story structure creates engagement, curiosity gap keeps them reading. Reddit's highest-performing organic compound.",
        "platform": {"reddit": 0.95, "twitter": 0.7, "linkedin": 0.9, "substack": 0.95},
        "detection_note": "Lowest detection risk. Indistinguishable from genuine sharing.",
    },
    "voss_negotiation": {
        "techniques": ["labeling", "calibrated_question", "pacing_and_leading"],
        "multiplier": 1.50,
        "mechanism": "Label their emotion (resistance drops), ask calibrated question (they solve your problem), pace then lead (redirect without triggering reactance). Voss' core stack.",
        "platform": {"reddit": 0.8, "twitter": 0.4, "linkedin": 0.75, "substack": 0.6},
        "detection_note": "Works in reply/comment format. Too subtle for short-form.",
    },
    "obligation_stack": {
        "techniques": ["reciprocity", "commitment_consistency", "guilt_tripping"],
        "multiplier": 1.55,
        "mechanism": "Give value first (reciprocity obligation), reference prior agreement (consistency pressure), invoke guilt for considering non-compliance. Cialdini compound.",
        "platform": {"reddit": 0.4, "twitter": 0.3, "linkedin": 0.5, "substack": 0.5},
        "detection_note": "Works in existing relationships. Detectable in cold outreach.",
    },
    "social_pressure": {
        "techniques": ["social_proof", "bandwagon", "loss_frame"],
        "multiplier": 1.52,
        "mechanism": "Others are doing it (proof), momentum is building (bandwagon), you'll miss out if you don't (loss). Classic FOMO compound.",
        "platform": {"reddit": 0.3, "twitter": 0.7, "linkedin": 0.6, "substack": 0.4},
        "detection_note": "Moderate detection. Works better as background signal than direct pitch.",
    },
    "intellectual_seduction": {
        "techniques": ["curiosity_gap", "perspective_shifting", "evidence_based"],
        "multiplier": 1.48,
        "mechanism": "Open a knowledge gap, then reframe the issue from an unexpected angle, supported by specific data. The reader feels smarter, not sold to.",
        "platform": {"reddit": 0.85, "twitter": 0.6, "linkedin": 0.8, "substack": 0.9},
        "detection_note": "Very low detection. Reads as genuine intellectual contribution.",
    },
    "empathic_redirect": {
        "techniques": ["empathy_appeal", "pacing_and_leading", "future_pacing"],
        "multiplier": 1.45,
        "mechanism": "Acknowledge their situation (empathy), match their state then redirect (pace-lead), paint the improved future (future pace). Therapy-derived compound.",
        "platform": {"reddit": 0.8, "twitter": 0.4, "linkedin": 0.7, "substack": 0.8},
        "detection_note": "Low detection. Reads as genuine care and advice.",
    },
    "authority_with_vulnerability": {
        "techniques": ["expert_testimony", "self_disclosure", "contrast_principle"],
        "multiplier": 1.50,
        "mechanism": "Establish expertise, then show vulnerability ('even I struggled with this'), then contrast before/after. The vulnerability makes the authority credible rather than threatening.",
        "platform": {"reddit": 0.85, "twitter": 0.65, "linkedin": 0.9, "substack": 0.85},
        "detection_note": "LinkedIn's #1 format. 'I used to think... then I learned...'",
    },
    "tribal_mobilization": {
        "techniques": ["unity", "identity_lock", "emotional_appeal_negative"],
        "multiplier": 1.58,
        "mechanism": "Invoke shared group membership (unity), frame action as identity requirement (lock), activate emotional urgency about the threat to the group. Political mobilization compound.",
        "platform": {"reddit": 0.6, "twitter": 0.8, "linkedin": 0.5, "substack": 0.7},
        "detection_note": "Works in political/cause contexts. Detectable in commercial.",
    },
    "foot_in_door_escalation": {
        "techniques": ["foot_in_the_door", "commitment_consistency", "reciprocity"],
        "multiplier": 1.45,
        "mechanism": "Small initial yes, reference that commitment for larger ask, add reciprocity obligation. Classic Cialdini escalation ladder.",
        "platform": {"reddit": 0.4, "twitter": 0.3, "linkedin": 0.5, "substack": 0.5},
        "detection_note": "Requires multi-touch. Works in DM/email sequences, not single posts.",
    },
    "contrarian_hook": {
        "techniques": ["curiosity_gap", "perspective_shifting", "rhetorical_question"],
        "multiplier": 1.42,
        "mechanism": "Open with unexpected claim (gap), reframe from new angle (shift), ask question that presupposes the new frame (rhetorical). Drives engagement through disagreement.",
        "platform": {"reddit": 0.85, "twitter": 0.9, "linkedin": 0.7, "substack": 0.8},
        "detection_note": "Extremely low detection. Reads as genuine contrarian thinking.",
    },

    # ─── TIER 4: Dating-Specific Compounds (1.48x - 1.72x) ─────────────
    # Optimized for 1:1 conversational dynamics on dating platforms.

    "high_ground_presuasion": {
        "techniques": ["high_ground_maneuver", "presupposition", "calibrated_question"],
        "multiplier": 1.72,
        "mechanism": "Prime the value frame with a leading question, then claim the universal value. The target already agreed to the premise — opposing now means opposing their own stated value. Adams + Cialdini compound.",
        "platform": {"reddit": 0.75, "twitter": 0.85, "linkedin": 0.9, "substack": 0.8},
        "detection_note": "Low detection. Reads as principled conversation, not direction.",
        "context": "dating",
    },
    "elicitation_misread": {
        "techniques": ["labeling", "presupposition", "perspective_shifting"],
        "multiplier": 1.58,
        "mechanism": "State something slightly wrong as a presupposition. Target corrects with real information they wouldn't have volunteered to a direct question. Bustamante CIA elicitation applied to social dynamics.",
        "platform": {"reddit": 0.85, "twitter": 0.6, "linkedin": 0.8, "substack": 0.7},
        "detection_note": "Very low detection. Feels like natural misunderstanding, not technique.",
        "context": "dating",
    },
    "push_pull_validation": {
        "techniques": ["contrast_principle", "identity_lock", "labeling"],
        "multiplier": 1.62,
        "mechanism": "Challenge then validate in the same exchange. The challenge creates uncertainty, the validation resolves it — intermittent reinforcement creates engagement. Bateman Mode core stack.",
        "platform": {"reddit": 0.7, "twitter": 0.75, "linkedin": 0.65, "substack": 0.6},
        "detection_note": "Moderate detection if overused. Best in small doses across exchanges.",
        "context": "dating",
    },
    "vulnerability_labeling": {
        "techniques": ["self_disclosure", "labeling", "pacing_and_leading"],
        "multiplier": 1.55,
        "mechanism": "Share something real, then label their emotional reaction to your disclosure. Double bonding — they bond to your vulnerability AND feel seen by your label. Aron 1997 + Voss compound.",
        "platform": {"reddit": 0.9, "twitter": 0.5, "linkedin": 0.8, "substack": 0.9},
        "detection_note": "Very low detection. Indistinguishable from emotionally attuned conversation.",
        "context": "dating",
    },
    "presuasion_future_pace": {
        "techniques": ["presupposition", "future_pacing", "emotional_appeal_positive"],
        "multiplier": 1.65,
        "mechanism": "Prime the emotional state with a presupposed question, then paint a shared future while they're in that state. The brain can't distinguish imagined futures from desired ones. Cialdini + Schacter 2007.",
        "platform": {"reddit": 0.6, "twitter": 0.7, "linkedin": 0.75, "substack": 0.8},
        "detection_note": "Low detection. Reads as enthusiasm, not direction.",
        "context": "dating",
    },
    "shared_reality_identity": {
        "techniques": ["labeling", "identity_lock", "unity"],
        "multiplier": 1.68,
        "mechanism": "Name their inner experience they haven't articulated, then frame the connection as shared identity. 'People like us' activates tribal bonding. Echterhoff 2009 + Adams.",
        "platform": {"reddit": 0.85, "twitter": 0.8, "linkedin": 0.85, "substack": 0.8},
        "detection_note": "Very low detection. Feels like genuine recognition of shared experience.",
        "context": "dating",
    },
    "curiosity_qualification": {
        "techniques": ["curiosity_gap", "identity_lock", "calibrated_question"],
        "multiplier": 1.52,
        "mechanism": "Open a knowledge gap, make them earn the answer through qualification. Effort justification increases their valuation of the interaction. Festinger 1957 + Loewenstein 1994.",
        "platform": {"reddit": 0.8, "twitter": 0.85, "linkedin": 0.7, "substack": 0.75},
        "detection_note": "Low detection. Reads as playful selectiveness.",
        "context": "dating",
    },
    "inoculation_high_ground": {
        "techniques": ["inoculation", "high_ground_maneuver", "self_disclosure"],
        "multiplier": 1.60,
        "mechanism": "Address the likely objection before it forms, claim the universal value, then support with personal vulnerability. The objection is dead, the moral position is unassailable, and the vulnerability makes it genuine. McGuire 1961 + Adams.",
        "platform": {"reddit": 0.85, "twitter": 0.7, "linkedin": 0.85, "substack": 0.85},
        "detection_note": "Very low detection. Reads as thoughtful self-awareness.",
        "context": "dating",
    },
    "thinking_past_presupposition": {
        "techniques": ["thinking_past_the_sale", "presupposition", "future_pacing"],
        "multiplier": 1.58,
        "mechanism": "Discuss implementation details as if the decision is already made, with the decision embedded as background assumption. Disagreeing requires actively stopping something already in motion. Adams core technique.",
        "platform": {"reddit": 0.6, "twitter": 0.7, "linkedin": 0.8, "substack": 0.7},
        "detection_note": "Low detection. Reads as confident planning, not presumption.",
        "context": "dating",
    },
    "pacing_elicitation": {
        "techniques": ["pacing_and_leading", "labeling", "presupposition"],
        "multiplier": 1.50,
        "mechanism": "Match their current state, then make a presupposed statement that leads them deeper. Feels like natural conversational flow, not direction. Voss + Bustamante compound.",
        "platform": {"reddit": 0.8, "twitter": 0.5, "linkedin": 0.75, "substack": 0.8},
        "detection_note": "Very low detection. Indistinguishable from attentive listening.",
        "context": "dating",
    },
    "narrative_presuasion": {
        "techniques": ["narrative_transportation", "presupposition", "calibrated_question"],
        "multiplier": 1.55,
        "mechanism": "Tell a story that puts them in a specific emotional state, then ask a presupposed question while counterargument generation is suppressed by transportation. Green & Brock 2000 + Cialdini.",
        "platform": {"reddit": 0.9, "twitter": 0.5, "linkedin": 0.7, "substack": 0.95},
        "detection_note": "Very low detection. Story format suppresses analytical processing.",
        "context": "dating",
    },
    "triple_bond": {
        "techniques": ["labeling", "self_disclosure", "unity"],
        "multiplier": 1.48,
        "mechanism": "Mirror their communication style (implicit), validate their identity with a label, share at matching vulnerability level. Three bonding signals in one exchange — similarity, recognition, intimacy. Chartrand 1999 + Aron 1997.",
        "platform": {"reddit": 0.85, "twitter": 0.5, "linkedin": 0.8, "substack": 0.85},
        "detection_note": "Lowest detection of all dating compounds. Reads as natural rapport.",
        "context": "dating",
    },
    "scarcity_vulnerability": {
        "techniques": ["scarcity_appeal", "self_disclosure", "future_pacing"],
        "multiplier": 1.70,
        "mechanism": "Introduce genuine time constraint, frame it as personal vulnerability (not pressure), then let them imagine the loss. Loss aversion is 2x gain motivation. The vulnerability makes the scarcity feel real, not manufactured. Kahneman & Tversky 1979.",
        "platform": {"reddit": 0.4, "twitter": 0.6, "linkedin": 0.5, "substack": 0.6},
        "detection_note": "Moderate detection if scarcity feels artificial. Requires genuine constraint.",
        "context": "dating",
    },
    "qualification_ladder": {
        "techniques": ["identity_lock", "calibrated_question", "self_disclosure"],
        "multiplier": 1.52,
        "mechanism": "Gradually increase qualification across exchanges. They work harder to impress. Then reward with vulnerability — the contrast between your earlier reserve and your openness feels earned. Effort justification + Aron's escalating disclosure.",
        "platform": {"reddit": 0.7, "twitter": 0.6, "linkedin": 0.75, "substack": 0.7},
        "detection_note": "Low detection. Reads as selective but genuine interest.",
        "context": "dating",
    },
    "inoculation_curiosity_disclosure": {
        "techniques": ["inoculation", "curiosity_gap", "self_disclosure"],
        "multiplier": 1.55,
        "mechanism": "Pre-empt their defense, open a knowledge gap they can't resist, then close it with intimacy. Three-step sequence that disarms, hooks, and bonds. McGuire 1961 + Loewenstein 1994 + Aron 1997.",
        "platform": {"reddit": 0.85, "twitter": 0.6, "linkedin": 0.75, "substack": 0.85},
        "detection_note": "Low detection. Each step feels organic in sequence.",
        "context": "dating",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DIMINISHING RETURNS MODEL
# ═══════════════════════════════════════════════════════════════════════════════
# From calibration/results/interaction_discovery.json:
#   1 technique:  1.0x (baseline)
#   2 techniques: ~1.3-1.5x (strong synergy)
#   3 techniques: ~1.4-1.7x (moderate additional lift)
#   4 techniques: ~1.5-1.8x (diminishing — detection risk rises faster than lift)
#   5+ techniques: saturation — no additional persuasion lift, detection risk dominant

# EMPIRICAL diminishing returns (calibrate_compounds.py, N=20,000):
#   0 techniques: 83.9% success (baseline)
#   1 technique:  82.6% (-1.3pp)
#   2 techniques: 83.4% (+0.7pp from 1)
#   3 techniques: 83.3% (-0.1pp)
#   4 techniques: 82.6% (-0.7pp)
#   5 techniques: 81.2% (-1.5pp)
#   6 techniques: 80.7% (-0.4pp)
#   7+ techniques: 79.2% (-0.4pp)
#
# The curve is FLAT to slightly NEGATIVE. More techniques = slightly worse.
# This means: compound stacking does NOT produce synergy in this dataset.
# The value of compounds is in COHERENCE (techniques that reinforce one
# narrative) not ACCUMULATION (more techniques = more persuasion).

TECHNIQUE_COUNT_MULTIPLIER = {
    1: 1.0,
    2: 1.01,   # EMPIRICAL: negligible lift from adding a second technique
    3: 1.00,   # EMPIRICAL: flat — no additional lift
    4: 0.99,   # EMPIRICAL: slight negative — more techniques = slight decline
    5: 0.97,   # EMPIRICAL: declining
}


def get_diminishing_return_factor(n_techniques: int) -> float:
    """Per-technique marginal factor from empirical calibration (N=20,000).

    The data shows a FLAT curve — adding more techniques does not increase
    persuasion effectiveness in naturalistic text. The value of compound
    stacks is coherence (techniques that fit together narratively), not
    accumulation.
    """
    if n_techniques in TECHNIQUE_COUNT_MULTIPLIER:
        return TECHNIQUE_COUNT_MULTIPLIER[n_techniques]
    return 0.95  # 6+: actively counterproductive


def find_best_compound(platform: str, content_type: str = None,
                       min_platform_score: float = 0.5,
                       context: str = None) -> list[dict]:
    """Find compound stacks ranked by effectiveness for a platform.

    Args:
        platform: Target platform (reddit, twitter, linkedin, substack).
        content_type: Reserved for future content-type filtering.
        min_platform_score: Minimum platform effectiveness threshold (0.0-1.0).
        context: Filter by stack context (e.g. "dating"). If None, returns all
            stacks. If specified, returns only stacks with a matching "context"
            field.

    Returns list of {name, techniques, multiplier, platform_score, mechanism}.
    """
    results = []
    for name, stack in COMPOUND_STACKS.items():
        # Context filter: if caller specifies a context, only include matching stacks
        if context is not None and stack.get("context") != context:
            continue
        platform_score = stack["platform"].get(platform, 0.0)
        if platform_score < min_platform_score:
            continue
        results.append({
            "name": name,
            "techniques": stack["techniques"],
            "multiplier": stack["multiplier"],
            "platform_score": platform_score,
            "effective_multiplier": round(stack["multiplier"] * platform_score, 2),
            "mechanism": stack["mechanism"],
            "detection_note": stack["detection_note"],
        })

    results.sort(key=lambda x: x["effective_multiplier"], reverse=True)
    return results
