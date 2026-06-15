from __future__ import annotations
"""
UX Pattern Library — Circuit-Level Success/Failure Mappings
============================================================
Structured database of concrete UX patterns tagged by:
    - Which limbic circuit they activate/suppress
    - Which appraisal dimensions they target
    - Pattern category (permission, pricing, social proof, error, etc.)
    - Success vs failure examples with specific products

Based on Part 7 of the limbic decision engineering research.
Each example identifies the SPECIFIC circuit and SPECIFIC appraisal dimension.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UXPattern:
    category: str
    outcome: str                    # "success" or "failure"
    product: str                    # specific product example
    description: str
    circuit: str                    # "approach", "avoidance", "deliberation"
    circuit_detail: str             # specific pathway description
    appraisal_scores: dict          # estimated scores for relevant dimensions
    mechanism: str                  # why it works/fails at the circuit level
    somatic_marker_effect: str      # what marker gets encoded


PATTERNS: list[UXPattern] = [

    # ── Novelty / Pattern Interruption ───────────────────────────────────

    UXPattern(
        category="novelty",
        outcome="failure",
        product="Generic landing page",
        description="Stock photography, 'Learn More' button, template layout",
        circuit="deliberation",
        circuit_detail="Zero prediction error signal — brain habituates immediately",
        appraisal_scores={"novelty": 0.0, "valence": 0.4},
        mechanism="Provides zero novelty signal. The hippocampus pattern-matches to "
                  "'generic website template' and the amygdala allocates no attention. "
                  "No prediction error means no salience.",
        somatic_marker_effect="None — stimulus is below the encoding threshold",
    ),
    UXPattern(
        category="novelty",
        outcome="success",
        product="Slack",
        description="Loading messages: 'Herding cats...', 'Reticulating splines...'",
        circuit="approach",
        circuit_detail="Humor generates novelty prediction error that suppresses insula uncertainty",
        appraisal_scores={"novelty": 0.5, "valence": 0.6},
        mechanism="Novelty sweet spot (0.3-0.6): novel enough to generate a positive prediction "
                  "error, familiar enough to not trigger amygdala threat. Humor specifically "
                  "suppresses the insula's uncertainty signal during loading.",
        somatic_marker_effect="'This app has personality' — differentiates from generic competitors",
    ),
    UXPattern(
        category="novelty",
        outcome="success",
        product="Headspace",
        description="Single onboarding question instead of feature carousel",
        circuit="approach",
        circuit_detail="Pattern interruption: user expects carousel, gets personal question",
        appraisal_scores={"novelty": 0.4, "goal_relevance": 0.9},
        mechanism="The question activates the dlPFC's self-referential processing network "
                  "(DMN overlap). User has STATED their goal, which primes the vmPFC to "
                  "evaluate everything that follows against that reference point.",
        somatic_marker_effect="'This app asked about ME' — high goal-relevance marker",
    ),

    # ── Permission Requests ──────────────────────────────────────────────

    UXPattern(
        category="permission",
        outcome="failure",
        product="Generic iOS app",
        description="Permission dialog on app launch, 3 seconds in",
        circuit="avoidance",
        circuit_detail="Amygdala: unknown entity requesting access = threat",
        appraisal_scores={"coping_potential": 0.1, "certainty": 0.1, "agency": 0.2},
        mechanism="No context for decision. vmPFC has no somatic marker to retrieve. "
                  "Amygdala classifies unknown request as threat by default.",
        somatic_marker_effect="None encoded — too early for marker formation",
    ),
    UXPattern(
        category="permission",
        outcome="success",
        product="Duolingo",
        description="Delays permission request until after first XP celebration",
        circuit="approach",
        circuit_detail="NAc: dopamine elevated from reward just earned",
        appraisal_scores={"valence": 0.85, "goal_relevance": 0.9, "coping_potential": 0.8},
        mechanism="Request rides the positive somatic marker being actively encoded. "
                  "2-3x higher opt-in rate because approach circuit is already dominant.",
        somatic_marker_effect="Positive marker actively encoding at request moment",
    ),

    # ── Pricing ──────────────────────────────────────────────────────────

    UXPattern(
        category="pricing",
        outcome="failure",
        product="Generic SaaS",
        description="3-tier comparison matrix with 20 feature rows",
        circuit="deliberation",
        circuit_detail="ACC overload -> dlPFC working memory exceeded (4+/-1 chunks)",
        appraisal_scores={"certainty": 0.2, "coping_potential": 0.3},
        mechanism="Too many comparison dimensions for working memory. ACC flags "
                  "'decision too expensive to compute.' Default under overload: DELAY.",
        somatic_marker_effect="vmPFC encodes 'pricing page = unresolved cognitive strain'",
    ),
    UXPattern(
        category="pricing",
        outcome="success",
        product="Superhuman",
        description="One tier, one price: '$30/month. The fastest email experience ever made.'",
        circuit="approach",
        circuit_detail="Amygdala binary approach/avoid, no ACC conflict needed",
        appraisal_scores={"certainty": 0.9, "coping_potential": 0.95},
        mechanism="7-dimensional appraisal reduced to 1-dimensional gut check. "
                  "No deliberation circuit involvement for binary yes/no.",
        somatic_marker_effect="Clean decision marker — low cognitive residue",
    ),

    # ── Social Proof ─────────────────────────────────────────────────────

    UXPattern(
        category="social_proof",
        outcome="failure",
        product="Generic landing page",
        description="'Trusted by 10,000+ customers' above the fold",
        circuit="deliberation",
        circuit_detail="ACC not in conflict yet — user just arrived",
        appraisal_scores={"goal_relevance": 0.1},
        mechanism="Addresses a question the limbic system hasn't asked. "
                  "ACC isn't running conflict resolution. Filed as noise by amygdala.",
        somatic_marker_effect="None — signal has no limbic weight at this timing",
    ),
    UXPattern(
        category="social_proof",
        outcome="success",
        product="Basecamp",
        description="Testimonials placed directly below pricing section",
        circuit="approach",
        circuit_detail="ACC conflict active -> TPJ processes testimonial perspective -> vmPFC borrows marker",
        appraisal_scores={"certainty": 0.7},
        mechanism="Arrives at maximum decisional uncertainty. Social proof is a "
                  "TRANSPLANTED SOMATIC MARKER — the TPJ lets the vmPFC borrow "
                  "someone else's body-state as a proxy for the missing direct experience.",
        somatic_marker_effect="Vicarious positive marker transplanted at decision point",
    ),

    # ── Error States ─────────────────────────────────────────────────────

    UXPattern(
        category="error",
        outcome="failure",
        product="Generic form",
        description="Red banner: 'Error: Invalid input'",
        circuit="avoidance",
        circuit_detail="Amygdala threat (red + ERROR = danger), negative prediction error",
        appraisal_scores={"goal_relevance": 0.9, "coping_potential": 0.1, "agency": 0.1, "valence": 0.15},
        mechanism="Saturated red triggers hard-coded threat association. Coping potential "
                  "0.1 + goal relevance 0.9 = FRUSTRATION compound. Highest avoidance tendency.",
        somatic_marker_effect="Strong negative marker: 'this app = frustration'",
    ),
    UXPattern(
        category="error",
        outcome="success",
        product="Stripe",
        description="Live validation with orange border, gentle shake, 'This doesn't look like a complete card number'",
        circuit="deliberation",
        circuit_detail="Mirror neurons respond to shake (proprioceptive 'something's off'), ACC not amygdala",
        appraisal_scores={"coping_potential": 0.7, "agency": 0.6, "valence": 0.5},
        mechanism="Orange not red — no threat association. Hedge language 'doesn't look like' "
                  "implies uncertainty, not verdict. Routes to deliberation, not avoidance.",
        somatic_marker_effect="Mild neutral marker — 'fixable, not broken'",
    ),

    # ── Scarcity ─────────────────────────────────────────────────────────

    UXPattern(
        category="scarcity",
        outcome="failure",
        product="Booking.com",
        description="Fake countdown timer, 'Only 3 left!', '12 people looking'",
        circuit="avoidance",
        circuit_detail="Amygdala loss-aversion initially -> hippocampus false-alarm encoding -> insula disgust",
        appraisal_scores={"agency": 0.1},
        mechanism="Works on first exposure. After 2-3 exposures, hippocampus learns "
                  "'this timer is fake.' Insula fires disgust. Agency drops from 0.5 to 0.1. "
                  "Disgust has highest RETALIATION action tendency.",
        somatic_marker_effect="Progressive: neutral -> negative -> disgust marker over exposures",
    ),
    UXPattern(
        category="scarcity",
        outcome="success",
        product="Apple",
        description="'Currently unavailable' — factual, no theatrics",
        circuit="approach",
        circuit_detail="Amygdala loss-aversion without insula manipulation detection",
        appraisal_scores={"agency": 0.8, "certainty": 0.9},
        mechanism="Real scarcity INCREASES valence via variable-ratio neurochemistry. "
                  "NAc assigns higher value to intermittently available rewards. "
                  "No insula trigger because agency remains high.",
        somatic_marker_effect="Positive scarcity marker — 'this is genuinely valuable'",
    ),

    # ── Notifications ────────────────────────────────────────────────────

    UXPattern(
        category="notification",
        outcome="failure",
        product="Generic app",
        description="Content-calendar scheduled notification at 2pm Tuesday",
        circuit="approach",
        circuit_detail="Weak hippocampal association — low arousal context",
        appraisal_scores={"temporal_proximity": 0.3, "valence": 0.3},
        mechanism="Notification inherits emotional state of the TIME SLOT (boredom). "
                  "Somatic marker encoded: 'this app = boredom filler.'",
        somatic_marker_effect="Low-approach marker: 'boredom filler'",
    ),
    UXPattern(
        category="notification",
        outcome="success",
        product="Strava",
        description="Event-triggered: 'Your friend just finished a 5K'",
        circuit="approach",
        circuit_detail="TPJ social processing + oxytocin social bonding",
        appraisal_scores={"temporal_proximity": 0.95, "goal_relevance": 0.8, "valence": 0.8},
        mechanism="Friend's ACTUAL activity creates psychological presence effect. "
                  "Event-triggered notifications inherit the EMOTIONAL STATE of the event, "
                  "not the time slot.",
        somatic_marker_effect="High-approach marker: 'Strava = connected to friend's real life'",
    ),

    # ── CTAs ─────────────────────────────────────────────────────────────

    UXPattern(
        category="cta",
        outcome="failure",
        product="Generic",
        description="'Submit' button or 'Yes, I want to 10x my revenue!'",
        circuit="deliberation",
        circuit_detail="No NAc activation ('Submit' predicts nothing) or ACC skepticism (hyperbolic claim)",
        appraisal_scores={"valence": 0.2, "certainty": 0.3},
        mechanism="'Submit' generates zero reward prediction. Hyperbolic claims trigger "
                  "dlPFC analysis — the ACC's implausibility detector activates.",
        somatic_marker_effect="None (Submit) or skepticism marker (hyperbolic)",
    ),
    UXPattern(
        category="cta",
        outcome="success",
        product="Notion",
        description="'Get Notion free' — 4 words",
        circuit="approach",
        circuit_detail="Hippocampus (brand familiarity) + NAc ('free' = zero loss) + premotor ('Get' = action verb)",
        appraisal_scores={"valence": 0.8, "coping_potential": 0.9, "certainty": 0.8},
        mechanism="Three circuits firing approach simultaneously with ZERO competing "
                  "avoidance signal. 'Get' activates motor preparation. 'Free' eliminates "
                  "loss-aversion. Brand familiarity provides hippocampal positive prior.",
        somatic_marker_effect="Triple-approach marker with motor priming",
    ),

    # ── Loading States ───────────────────────────────────────────────────

    UXPattern(
        category="loading",
        outcome="failure",
        product="Generic",
        description="Spinner with no context",
        circuit="avoidance",
        circuit_detail="Insula uncertainty signal escalating -> amygdala threat after ~8s",
        appraisal_scores={"certainty": 0.1, "coping_potential": 0.2},
        mechanism="Information vacuum. Insula uncertainty signal escalates over time. "
                  "After ~8 seconds, amygdala classifies the unknown as threat.",
        somatic_marker_effect="Anxiety marker that compounds with each exposure",
    ),
    UXPattern(
        category="loading",
        outcome="success",
        product="Slack",
        description="Witty loading messages ('Herding cats...', 'Reticulating splines...')",
        circuit="approach",
        circuit_detail="Novelty appraisal suppresses insula uncertainty with positive distractor",
        appraisal_scores={"novelty": 0.5, "valence": 0.6, "certainty": 0.4},
        mechanism="Humor is a novelty signal that suppresses the insula's uncertainty signal. "
                  "Replaces anxiety with amusement during the loading gap.",
        somatic_marker_effect="Mild positive marker: 'this app has personality'",
    ),
    UXPattern(
        category="loading",
        outcome="success",
        product="Stripe",
        description="Optimistic UI — success state shown before server confirms",
        circuit="approach",
        circuit_detail="Dopamine prediction signal fires immediately on success display",
        appraisal_scores={"valence": 0.8, "certainty": 0.7, "temporal_proximity": 0.9},
        mechanism="Success state shown BEFORE server confirms. Only ONE negative prediction "
                  "error if transaction fails, vs sustained uncertainty-aversion.",
        somatic_marker_effect="Immediate positive marker from predicted success",
    ),

    # ── Checkout ─────────────────────────────────────────────────────────

    UXPattern(
        category="checkout",
        outcome="failure",
        product="Generic e-commerce",
        description="Multi-page checkout (4 steps: shipping, billing, review, confirm)",
        circuit="deliberation",
        circuit_detail="Each page transition = ACC re-evaluation point",
        appraisal_scores={"coping_potential": 0.45, "certainty": 0.4},
        mechanism="Tug-of-war between hippocampal sunk-cost marker ('I've come this far') "
                  "and insula uncertainty ('how much more?'). Each transition resets the effort calculation.",
        somatic_marker_effect="Cumulative cognitive strain marker",
    ),
    UXPattern(
        category="checkout",
        outcome="success",
        product="Shopify",
        description="One-page checkout — everything visible on single scrollable surface",
        circuit="approach",
        circuit_detail="Zero ACC re-evaluation points, constant temporal-proximity signal",
        appraisal_scores={"coping_potential": 0.85, "certainty": 0.8, "temporal_proximity": 0.9},
        mechanism="Visible 'Complete order' button = constant temporal-proximity signal. "
                  "Scrolling = proprioceptive motor-commitment reinforcing sunk-cost.",
        somatic_marker_effect="Clean completion marker — no accumulated friction",
    ),

    # ── Cancellation ─────────────────────────────────────────────────────

    UXPattern(
        category="cancellation",
        outcome="failure",
        product="Generic SaaS",
        description="7-click hostile retention flow with confirmshaming",
        circuit="avoidance",
        circuit_detail="Insula disgust + anger = highest RETALIATION action tendency",
        appraisal_scores={"agency": 0.1, "valence": 0.1},
        mechanism="TPJ detects agency asymmetry: 'these barriers serve THEM, not me.' "
                  "Insula generates DISGUST. User doesn't just leave — they leave and tell others.",
        somatic_marker_effect="'This brand = predatory' — extremely high salience, retrieved in ALL future encounters",
    ),
    UXPattern(
        category="cancellation",
        outcome="success",
        product="Spotify",
        description="One question + clear summary of losses",
        circuit="approach",
        circuit_detail="Question provides agency. Loss summary activates LEGITIMATE loss-aversion.",
        appraisal_scores={"agency": 0.8, "certainty": 0.8, "valence": 0.4},
        mechanism="Real consequences presented without artificial barriers. Some users reverse "
                  "because the vmPFC's loss-preview generated a genuine aversive marker about losing playlists. "
                  "Presenting real consequences and letting the limbic system compute.",
        somatic_marker_effect="Respectful interaction marker — even if user cancels, brand stays positive",
    ),

    # ── Empty States ─────────────────────────────────────────────────────

    UXPattern(
        category="empty_state",
        outcome="failure",
        product="Generic search",
        description="'No results found. Try different keywords.'",
        circuit="avoidance",
        circuit_detail="Negative prediction error: high goal-relevance + zero coping potential",
        appraisal_scores={"goal_relevance": 0.9, "coping_potential": 0.1, "valence": 0.1},
        mechanism="Frustration-disappointment compound. User expected results (high prediction), "
                  "got nothing (maximum negative prediction error).",
        somatic_marker_effect="Frustration marker associated with search function",
    ),
    UXPattern(
        category="empty_state",
        outcome="success",
        product="Pinterest",
        description="'People with similar taste love...' — always shows something",
        circuit="approach",
        circuit_detail="NAc always gets a reward pathway. TPJ social-referencing.",
        appraisal_scores={"valence": 0.6, "goal_relevance": 0.5, "coping_potential": 0.7},
        mechanism="NEVER allow a true zero state. NAc must maintain activation above baseline. "
                  "Pinterest's social-referencing activates TPJ + personalized coping signal.",
        somatic_marker_effect="'This app always has something for me'",
    ),
]


class UXPatternLibrary:
    """Searchable library of circuit-level UX patterns."""

    def __init__(self):
        self.patterns = PATTERNS

    def by_category(self, category: str) -> list[UXPattern]:
        return [p for p in self.patterns if p.category == category]

    def successes(self) -> list[UXPattern]:
        return [p for p in self.patterns if p.outcome == "success"]

    def failures(self) -> list[UXPattern]:
        return [p for p in self.patterns if p.outcome == "failure"]

    def by_circuit(self, circuit: str) -> list[UXPattern]:
        return [p for p in self.patterns if p.circuit == circuit]

    def for_weak_dimension(self, dimension: str) -> list[UXPattern]:
        """Find success patterns that score well on a given dimension.
        Use this to suggest fixes when a dimension is dragging the score down.

        Novelty is special: sweet spot is 0.3-0.6, so 'good' means in-range,
        not maxed. For all others, >= 0.7 is the threshold.
        """
        results = []
        for p in self.patterns:
            if p.outcome == "success" and dimension in p.appraisal_scores:
                score = p.appraisal_scores[dimension]
                if dimension == "novelty":
                    if 0.3 <= score <= 0.6:
                        results.append(p)
                elif score >= 0.7:
                    results.append(p)
        return results

    def categories(self) -> list[str]:
        return sorted(set(p.category for p in self.patterns))

    def search(self, query: str) -> list[UXPattern]:
        """Full-text search across all pattern fields."""
        q = query.lower()
        return [
            p for p in self.patterns
            if q in p.description.lower()
            or q in p.mechanism.lower()
            or q in p.product.lower()
            or q in p.category.lower()
        ]
