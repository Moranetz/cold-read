from __future__ import annotations
"""
Appraisal Extractor — 7 Cognitive Appraisal Dimensions
=======================================================
Scores any text stimulus on the 7 dimensions from Smith & Ellsworth (1985)
and Scherer (2001) that the limbic system evaluates before generating
an emotional response.

Three extraction modes:
    - heuristic: Fast regex/keyword scoring (batch processing, no API needed)
    - claude: Claude API with structured output (highest accuracy)
    - ollama: Local Ollama model with JSON format (offline, moderate accuracy)
"""

import json
import re
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class AppraisalScores:
    """7-dimension appraisal vector for a stimulus."""
    novelty: float = 0.5
    valence: float = 0.5
    goal_relevance: float = 0.5
    coping_potential: float = 0.5
    agency: float = 0.5
    certainty: float = 0.5
    temporal_proximity: float = 0.5

    def to_dict(self) -> dict:
        return asdict(self)

    def to_vector(self) -> list:
        return [
            self.novelty, self.valence, self.goal_relevance,
            self.coping_potential, self.agency, self.certainty,
            self.temporal_proximity,
        ]

    @property
    def mean(self) -> float:
        return sum(self.to_vector()) / 7

    def weakest_dimension(self) -> tuple:
        d = self.to_dict()
        name = min(d, key=d.get)
        return name, d[name]

    def strongest_dimension(self) -> tuple:
        d = self.to_dict()
        name = max(d, key=d.get)
        return name, d[name]


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — Grounded in Smith & Ellsworth (1985) operational definitions
# ═══════════════════════════════════════════════════════════════════════════════
# This is the single highest-leverage component in the pipeline.
# The quality of appraisal extraction determines whether the circuit
# formulas receive inputs extreme enough to differentiate outcomes.

CLAUDE_SYSTEM_PROMPT = """You are a cognitive appraisal scoring system implementing Smith & Ellsworth's (1985) appraisal theory and Scherer's (2001) component process model.

Your task: score a UX stimulus on 7 appraisal dimensions as experienced by a typical user encountering it for the first time.

CRITICAL: You are scoring the READER'S appraisal, not the text's intent. A scarcity message INTENDS to create urgency, but the reader may appraise it as manipulative (low agency) rather than urgent (high temporal proximity).

DIMENSION DEFINITIONS (from Smith & Ellsworth 1985, operationalized for UX):

1. novelty (0.0-1.0): How unexpected or pattern-breaking is this stimulus?
   0.0 = completely familiar template ("Learn More", standard spinner)
   0.3 = slightly unexpected element within familiar frame
   0.5 = moderately surprising (humor in loading state, unusual offer framing)
   0.7 = highly novel (never seen this pattern before — threshold where curiosity flips to unease)
   1.0 = completely unprecedented, potentially alarming

2. valence (0.0-1.0): How pleasant vs aversive is the IMMEDIATE emotional response?
   0.0 = strongly aversive (error + blame + red + caps = threat signal)
   0.2 = mildly unpleasant (generic rejection, vague warning)
   0.5 = neutral (informational, neither pleasant nor unpleasant)
   0.7 = pleasant (reward, celebration, warm acknowledgment)
   1.0 = strongly rewarding (unexpected gift, achievement unlocked, genuine delight)

3. goal_relevance (0.0-1.0): How directly does this address what the reader cares about?
   0.0 = completely irrelevant to any user goal (company boilerplate, generic feature list)
   0.3 = tangentially related (general category match but not specific)
   0.5 = moderately relevant (addresses a common need generically)
   0.7 = highly relevant (uses "you/your", references specific user context)
   1.0 = directly addresses the reader's primary active need

4. coping_potential (0.0-1.0): How capable does the reader feel of handling this?
   0.0 = completely overwhelmed (12 required fields, multi-page form, no guidance)
   0.2 = struggling (unclear next steps, ambiguous instructions)
   0.5 = manageable but requires effort (standard form, multiple choices)
   0.7 = easy (clear CTA, pre-filled fields, "takes 2 minutes")
   1.0 = effortless (one click, auto-complete, zero friction)

5. agency (0.0-1.0): How much control does the reader have?
   0.0 = completely controlled (forced flow, no exit, hidden cancel)
   0.2 = heavily constrained (confirmshaming, guilt-trip copy, fake urgency)
   0.5 = standard (normal form, expected interaction pattern)
   0.7 = empowered (visible alternatives, "skip", "no thanks", transparent process)
   1.0 = fully autonomous ("cancel anytime", "your choice", genuine opt-in/out)

6. certainty (0.0-1.0): How confident is the reader about what happens next?
   0.0 = complete uncertainty (vague promise, no preview, "results may vary")
   0.2 = low confidence (qualified claims, hidden terms, unclear pricing)
   0.5 = moderate (some social proof or specifics, but gaps remain)
   0.7 = high confidence (guarantee, specific numbers, testimonial at decision point)
   1.0 = complete certainty (money-back guarantee, free trial, preview of exact outcome)

7. temporal_proximity (0.0-1.0): How immediate is the consequence?
   0.0 = distant/abstract ("over the coming months", "long-term benefits")
   0.3 = near-future ("this week", "within days")
   0.5 = soon ("today", "by tonight")
   0.7 = very soon ("in minutes", "right away")
   1.0 = instant ("now", "immediately", real-time feedback, "your report is ready")"""

CLAUDE_USER_TEMPLATE = """Score this UX stimulus. The reader encounters it in the context of: {context}

STIMULUS: "{text}"

Return ONLY a JSON object with exactly these 7 keys, each a float 0.0-1.0:
{{"novelty": ..., "valence": ..., "goal_relevance": ..., "coping_potential": ..., "agency": ..., "certainty": ..., "temporal_proximity": ...}}"""

# Context descriptions for common UX positions
CONTEXT_DESCRIPTIONS = {
    "onboarding": "first-time app onboarding, user is evaluating whether to invest time",
    "checkout": "purchase checkout flow, user has already decided to buy and is completing payment",
    "error_state": "something went wrong, user expected success and got failure",
    "notification": "push notification or in-app alert, user was doing something else",
    "pricing": "pricing page, user is deciding whether the cost is worth it",
    "cancellation": "cancellation/unsubscribe flow, user has decided to leave",
    "empty_state": "search returned no results or content area is empty",
    "permission_request": "app is asking for device permissions (notifications, location, etc.)",
    "cta": "call-to-action button or link, user is deciding whether to click",
    "loading": "content is loading, user is waiting",
    "landing": "landing page, user just arrived and is forming first impression",
    "general": "general UX context, no specific position in a flow",
}


# ─── Heuristic signals (all patterns use \b word boundaries) ────────────────

_NOVELTY_HIGH = re.compile(
    r'\b(introducing|unveiled?|never[- ]before|first[- ]ever|breakthrough|'
    r'revolutionary|reimagined?|reinvent|disrupt|unprecedented|surprise|'
    r'exclusive|secret|hidden|shocking|unexpected)\b', re.I
)
_NOVELTY_LOW = re.compile(
    r'\b(standard|traditional|classic|conventional|usual|typical|'
    r'familiar|normal|regular|default|basic|simple)\b', re.I
)

_VALENCE_POS = re.compile(
    r'\b(free|love|beautiful|celebrate|reward|bonus|gift|win|'
    r'congrats|welcome|thank|enjoy|delight|happy|success|perfect|'
    r'amazing|incredible|wonderful|brilliant|excellent)\b', re.I
)
_VALENCE_NEG = re.compile(
    r'\b(error|fail(?:ed|ure)?|invalid|wrong|denied|rejected|expired|'
    r'warning|danger|risk|threat|problem|issue|broken|lost|miss(?:ed)?|'
    r'unfortunately|sorry|mistake|hate|terrible|awful)\b', re.I
)

_GOAL_RELEVANCE_HIGH = re.compile(
    r'\b(you|your|my|personali[sz]ed|for you|tailored|custom|'
    r'based on your|recommended for|matches? your|fits? your|'
    r'goals?|needs?|what you (?:want|need|care)|matters? to you)\b', re.I
)
_GOAL_RELEVANCE_LOW = re.compile(
    r'\b(we (?:built|made|created)|our (?:team|company|platform)|'
    r'features? include|announcing|introducing our|learn more about us)\b', re.I
)

_COPING_HIGH = re.compile(
    r'\b(easy|simple|one[- ]click|instant|automatic|no[- ]setup|'
    r'takes? \d+\s*(?:seconds?|minutes?|min)|step[- ]by[- ]step|guided|'
    r'pre[- ]?filled|template|ready[- ]made|done|quick)\b', re.I
)
_COPING_LOW = re.compile(
    r'\b(complex|difficult|advanced|requires?|mandatory|must|'
    r'multi[- ]step|extensive|comprehensive|complete all|fill out|'
    r'submit .{0,20} documents?|upload .{0,20} files?)\b', re.I
)

_AGENCY_HIGH = re.compile(
    r'\b(choose|option|prefer|skip|later|no thanks|decline|'
    r'your choice|you decide|opt[- ]?(?:in|out)|customize|control|'
    r'manage|cancel anytime|no commitment)\b', re.I
)
_AGENCY_LOW = re.compile(
    r'\b(required|mandatory|must|forced?|cannot skip|'
    r'no option|only way|you (?:have|need) to|non[- ]?negotiable|'
    r'are you sure|don.t miss|last chance)\b', re.I
)

_CERTAINTY_HIGH = re.compile(
    r'\b(guaranteed?|money[- ]back|refund|proven|verified|'
    r'trusted by \d|rated \d|\d+\s*stars?|100%|risk[- ]free|'
    r'no[- ]risk|case stud|testimonial|specific|exactly)\b', re.I
)
_CERTAINTY_LOW = re.compile(
    r'\b(maybe|might|could|possibly|results may vary|'
    r'no guarantee|subject to|terms apply|conditions|'
    r'estimated|approximately|uncertain)\b', re.I
)

_TEMPORAL_HIGH = re.compile(
    r'\b(now|today|instant|immediate|right away|starts? (?:now|today)|'
    r'already|live|real[- ]time|currently|this (?:second|moment)|'
    r'just (?:happened|finished|completed))\b', re.I
)
_TEMPORAL_LOW = re.compile(
    r'\b(eventually|over time|long[- ]term|in the (?:future|coming)|'
    r'weeks?|months?|years?|someday|gradually|soon|later|upcoming)\b', re.I
)


# ─── Negation-aware scoring ─────────────────────────────────────────────────

_NEGATION_WINDOW = re.compile(
    r'\b(no|not|don.?t|won.?t|can.?t|never|without|neither|nor|lack|'
    r'fail(?:ed|ure)?|miss(?:ing|ed)?|zero|none)\s+\w*\s*', re.I
)


def _count_negated(text, pattern):
    negated = 0
    for m in pattern.finditer(text):
        start = max(0, m.start() - 30)
        prefix = text[start:m.start()]
        if _NEGATION_WINDOW.search(prefix):
            negated += 1
    return negated


def _score_regex_dimension(text, high, low):
    h = len(high.findall(text))
    l = len(low.findall(text))
    h_negated = _count_negated(text, high)
    l_negated = _count_negated(text, low)
    h_effective = (h - h_negated) + l_negated
    l_effective = (l - l_negated) + h_negated
    total = abs(h_effective) + abs(l_effective)
    if total == 0:
        return 0.5
    raw = max(0, h_effective) / total
    return round(min(1.0, max(0.0, raw)), 3)


def _clamp_scores(raw_dict):
    """Clamp all scores to [0.0, 1.0] and handle missing/malformed values."""
    dims = ["novelty", "valence", "goal_relevance", "coping_potential",
            "agency", "certainty", "temporal_proximity"]
    cleaned = {}
    for k in dims:
        v = raw_dict.get(k, 0.5)
        try:
            cleaned[k] = round(min(1.0, max(0.0, float(v))), 3)
        except (TypeError, ValueError):
            cleaned[k] = 0.5
    return cleaned


class AppraisalExtractor:
    """Extract cognitive appraisal dimensions from text stimuli.

    Modes:
        heuristic — regex keyword matching, no API, fast, low accuracy
        claude    — Anthropic Claude API, structured output, high accuracy
        ollama    — local Ollama model, offline, moderate accuracy
    """

    def __init__(
        self,
        anthropic_api_key=None,
        claude_model="claude-sonnet-4-20250514",
        ollama_model="llama3.2",
        ollama_url="http://localhost:11434",
    ):
        self.anthropic_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.claude_model = claude_model
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url

    def extract_heuristic(self, text, context=None):
        """Fast regex-based extraction. No API required."""
        if not text or not text.strip():
            return AppraisalScores()  # all 0.5 for empty input
        return AppraisalScores(
            novelty=_score_regex_dimension(text, _NOVELTY_HIGH, _NOVELTY_LOW),
            valence=_score_regex_dimension(text, _VALENCE_POS, _VALENCE_NEG),
            goal_relevance=_score_regex_dimension(text, _GOAL_RELEVANCE_HIGH, _GOAL_RELEVANCE_LOW),
            coping_potential=_score_regex_dimension(text, _COPING_HIGH, _COPING_LOW),
            agency=_score_regex_dimension(text, _AGENCY_HIGH, _AGENCY_LOW),
            certainty=_score_regex_dimension(text, _CERTAINTY_HIGH, _CERTAINTY_LOW),
            temporal_proximity=_score_regex_dimension(text, _TEMPORAL_HIGH, _TEMPORAL_LOW),
        )

    def extract_claude(self, text, context=None):
        """Claude API extraction with structured output and context awareness."""
        import urllib.request

        if not self.anthropic_key:
            # Fall back to heuristic if no key available
            return self.extract_heuristic(text, context)

        ctx_label = context or "general"
        ctx_desc = CONTEXT_DESCRIPTIONS.get(ctx_label, CONTEXT_DESCRIPTIONS["general"])

        user_msg = CLAUDE_USER_TEMPLATE.format(
            text=text[:3000],
            context=ctx_desc,
        )

        payload = json.dumps({
            "model": self.claude_model,
            "max_tokens": 200,
            "system": CLAUDE_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_msg}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
        except Exception as e:
            # Fallback to heuristic on API failure
            return self.extract_heuristic(text, context)

        # Parse response
        raw_text = ""
        for block in result.get("content", []):
            if block.get("type") == "text":
                raw_text += block.get("text", "")

        # Extract JSON from response (handle markdown code blocks)
        raw_text = raw_text.strip()
        if raw_text.startswith("```"):
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)

        try:
            scores = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON from mixed text
            match = re.search(r'\{[^}]+\}', raw_text)
            if match:
                scores = json.loads(match.group())
            else:
                return self.extract_heuristic(text, context)

        return AppraisalScores(**_clamp_scores(scores))

    def extract_ollama(self, text, context=None):
        """Ollama local model extraction with JSON format enforcement."""
        import urllib.request

        ctx_label = context or "general"
        ctx_desc = CONTEXT_DESCRIPTIONS.get(ctx_label, CONTEXT_DESCRIPTIONS["general"])

        prompt = CLAUDE_SYSTEM_PROMPT + "\n\n" + CLAUDE_USER_TEMPLATE.format(
            text=text[:3000],
            context=ctx_desc,
        )

        payload = json.dumps({
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }).encode()

        req = urllib.request.Request(
            "%s/api/generate" % self.ollama_url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            raw = result.get("response", "{}")
            scores = json.loads(raw)
        except Exception:
            return self.extract_heuristic(text, context)

        return AppraisalScores(**_clamp_scores(scores))

    def extract(self, text, mode="heuristic", context=None):
        """Extract appraisal scores.

        Args:
            text: stimulus to analyze
            mode: "heuristic", "claude", "ollama", or "prompt" (alias for ollama)
            context: UX context label (onboarding, checkout, error_state, etc.)
        """
        if not text or not text.strip():
            return AppraisalScores()

        if mode == "claude":
            return self.extract_claude(text, context)
        elif mode in ("ollama", "prompt"):
            return self.extract_ollama(text, context)
        return self.extract_heuristic(text, context)
