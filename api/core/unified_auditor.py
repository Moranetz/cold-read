"""
UNIFIED PERSUASION AUDITOR
==========================
A comprehensive auditing tool that combines all detection frameworks:
- Tactical Stimulus Detection (6 primal stimuli)
- Psychological Principles Detection (8 Cialdini principles + cognitive biases)
- Linguistic Pattern Detection (8 categories including conceptual metaphors)

Outputs a JSON report with composite scoring and classifications.

Usage:
    auditor = UnifiedPersuasionAuditor()
    result = auditor.audit("Your content text here")
    print(result)

Author: Persuasion Max Project
Version: 1.1.0
"""

import re
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter

# =============================================================================
# SECTION 1: PATTERN CONSTANTS
# =============================================================================

class Patterns:
    """All regex patterns and keyword lists consolidated from detection frameworks."""

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 1: PERSONAL (Self-Centered Targeting)
    # -------------------------------------------------------------------------
    PERSONAL_EXCLUSION = re.compile(
        r'(?i)(not\s+for\s+everyone|if\s+you\s+know\s*,?\s*you\s+know|'
        r'for\s+those\s+who\s+recognize|for\s+the\s+\d+\s+people|'
        r'you\'ll\s+be\s+illegible|iykyk)',
        re.IGNORECASE
    )

    PERSONAL_STATUS_THREAT = [
        "being basic", "fear of being basic", "culturally irrelevant",
        "algorithmically predictable", "you're still too visible",
        "your references are being sold back", "mainstream taste",
        "basic taste", "normies", "sheeple"
    ]

    PERSONAL_TRIBAL_SAFETY = [
        "we understand the references you understand", "silent mutual recognition",
        "tribal markers", "tribal safety", "obscurity signals", "pre-algorithmic",
        "post-commercial", "your people", "in-group", "inner circle"
    ]

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 2: CONTRASTABLE (Binary Ideological Framing)
    # -------------------------------------------------------------------------
    CONTRASTABLE_PAIRS = {
        "mass_vs_artifact": {
            "negative": ["mass-produced", "factory", "generic", "manufactured", "commodity"],
            "positive": ["artifact", "unique", "evidence", "one-of-a-kind", "bespoke", "handmade"]
        },
        "algorithmic_vs_authored": {
            "negative": ["algorithmic", "predicted", "personalized", "fed to you"],
            "positive": ["authored", "curated", "deliberate", "intentional", "chosen"]
        },
        "visible_vs_coded": {
            "negative": ["visible", "obvious", "legible", "logo", "branded"],
            "positive": ["coded", "references", "signals", "obscure", "subtle"]
        },
        "commercial_vs_authentic": {
            "negative": ["commercial", "marketing", "selling", "advertising"],
            "positive": ["authentic", "real", "genuine", "raw", "honest"]
        }
    }

    CONTRASTABLE_MARKERS = re.compile(
        r'\bvs\b|↔|versus|\bnot\b|unlike|instead\s+of|while\s+they|'
        r'but\s+we|on\s+the\s+other\s+hand|whereas',
        re.IGNORECASE
    )

    CONTRASTABLE_SPECTRUM_PENALTY = [
        "also offers", "ranges from", "variety", "flexibility",
        "multiple options", "for everyone", "something for all"
    ]

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 3: TANGIBLE (Concrete vs. Abstract)
    # -------------------------------------------------------------------------
    TANGIBLE_WEIGHT = re.compile(r'(\d+)\s*(gsm|g/m²|lb/yd²|oz|grams?|kg)', re.IGNORECASE)
    TANGIBLE_LOCATION = re.compile(
        r'made\s+in\s+([A-Za-z]+)|manufactured\s+in\s+([A-Za-z\s]+)|'
        r'factory\s+in\s+([A-Za-z]+)|sourced\s+from\s+([A-Za-z]+)',
        re.IGNORECASE
    )
    TANGIBLE_DECAY = re.compile(
        r'(fades?|wears?|ages?|deteriorates?|shrinks?|bleeds?|patina)\s*'
        r'([a-z\s]*?)(\d+\s*(month|week|year|day|%|time|wash))',
        re.IGNORECASE
    )
    TANGIBLE_SENSORY = re.compile(
        r'(smells?|texture|feels?|sounds?|tastes?|touch)\s+(like|of|is|was)\s+([a-z\s]+)',
        re.IGNORECASE
    )
    TANGIBLE_ARTIFACTS = [
        "uneven", "visible seams", "not identical", "handmade", "mistakes",
        "irregularity", "one-of-a-kind", "imperfect", "hand-stitched"
    ]
    TANGIBLE_ABSTRACT_PENALTY = [
        "premium quality", "luxury", "elevated", "timeless", "perfection",
        "excellence", "superior", "world-class", "sophisticated", "elegant",
        "refined", "exquisite", "impeccable", "top-tier", "best in class"
    ]

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 4: MEMORABLE (U-Curve Structure)
    # -------------------------------------------------------------------------
    MEMORABLE_OPENING_SIGNALS = re.compile(
        r'(archive\s+\d+|collection|series|episode|chapter|'
        r'if\s+you\s+recognize|grainy|stark|cryptic|ambiguous|'
        r'unknown|forgotten|unearthed|discovered)',
        re.IGNORECASE
    )
    MEMORABLE_CLOSING_SIGNALS = re.compile(
        r'(or\s+you\s+were\s+already|you\s+decide|the\s+rest\s+is\s+up\s+to\s+you|'
        r'never\s+resolve|if\s+you\'?ve?\s+found|make\s+your\s+choice)',
        re.IGNORECASE
    )
    MEMORABLE_FILLER = [
        "also", "additionally", "moreover", "furthermore", "and we also",
        "choose from", "various", "traditional", "as well as", "in addition"
    ]

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 5: VISUAL (Anti-Aesthetic vs. Polished)
    # -------------------------------------------------------------------------
    VISUAL_ANTI_AESTHETIC = [
        "grainy", "blur", "bad lighting", "accidental crop", "mistakes",
        "CCTV", "found footage", "webcam quality", "documentary", "cold",
        "unvarnished", "raw", "unedited", "unfiltered", "bad white balance",
        "cropped awkwardly", "harsh shadow", "shot on phone", "not made for Instagram"
    ]
    VISUAL_NO_STYLING = [
        "no models", "on hangers", "on the floor", "strangers in background",
        "not styled", "no styling", "no moments", "just recording"
    ]
    VISUAL_MOOD_BOARD = [
        "mood board", "references", "gallery", "Russian Constructivism",
        "Brutalist", "90s rave", "film stills", "archive", "unlabeled"
    ]
    VISUAL_POLISHED_PENALTY = [
        "beautiful", "stunning", "gorgeous", "elegant", "clean", "pristine",
        "professional photography", "lifestyle", "aspirational", "gloss",
        "luxury aesthetic", "refined", "perfect lighting"
    ]

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS 6: EMOTIONAL (Pain→Relief Arc)
    # -------------------------------------------------------------------------
    EMOTIONAL_PAIN_KEYWORDS = {
        "cultural_irrelevance": ["cultural irrelevance", "outdated", "behind", "forgotten", "left out"],
        "algorithmic_threat": ["algorithmic", "predicted for you", "feed algorithm", "your references sold back"],
        "status_anxiety": ["being basic", "normies", "everyone else", "mainstream", "trying too hard"],
        "inauthenticity": ["fake", "commercial", "manufactured", "mass-produced", "cookie cutter"]
    }

    EMOTIONAL_RELIEF_KEYWORDS = {
        "esoteric_access": ["if you know you know", "get it", "understanding the reference", "in-group knowledge"],
        "escape_offered": ["we don't have a logo", "not looking for you", "not for everyone", "exit the algorithm"],
        "authenticity_promise": ["authentic", "real", "genuine", "unmanufactured", "artifact"],
        "tribal_safety": ["community of people", "silent recognition", "mutual understanding", "your people"]
    }

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 1: AUTHORITY
    # -------------------------------------------------------------------------
    AUTHORITY_CREDENTIALS = [
        "doctor", "dr.", "phd", "expert", "professor", "researcher", "scientist",
        "certified", "licensed", "30 years", "industry leader", "award-winning",
        "specialist", "consultant", "leading", "renowned"
    ]
    AUTHORITY_INSTITUTIONS = [
        "harvard", "stanford", "mit", "oxford", "yale", "johns hopkins",
        "mayo clinic", "princeton", "cambridge", "berkeley"
    ]
    AUTHORITY_CONFIDENCE = re.compile(
        r'(steady\s+vocal|unhurried|120.*150\s+words|eye\s+contact|'
        r'relaxed\s+shoulders|precise\s+language|stillness)',
        re.IGNORECASE
    )
    AUTHORITY_THREAT_PENALTY = [
        "aggressive", "demanding", "high pressure", "intense", "angry",
        "threatening", "forceful"
    ]

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 2: SOCIAL PROOF
    # -------------------------------------------------------------------------
    SOCIAL_PROOF_CONSENSUS = [
        "most popular", "bestseller", "top rated", "number one", "#1",
        "millions bought", "everyone agrees", "widely acclaimed",
        "people are choosing", "join thousands", "trusted by millions"
    ]
    SOCIAL_PROOF_SIMILARITY = [
        "people like you", "others in your situation", "similar customers",
        "your peers", "professionals like yourself", "people in your area"
    ]
    SOCIAL_PROOF_NUMBERS = re.compile(
        r'(\d{1,3}(?:,\d{3})*|\d+(?:\.\d+)?[KMB]?)\s*'
        r'(?:customers?|users?|people|subscribers?|followers?|reviews?|ratings?)',
        re.IGNORECASE
    )

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 3: RECIPROCITY
    # -------------------------------------------------------------------------
    RECIPROCITY_FREE = [
        "free", "complimentary", "no cost", "on the house", "gratis",
        "free trial", "free sample", "free consultation", "bonus"
    ]
    RECIPROCITY_OBLIGATION = [
        "we gave you", "after everything we", "you owe", "return the favor",
        "since we provided", "in exchange", "quid pro quo"
    ]

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 4: COMMITMENT
    # -------------------------------------------------------------------------
    COMMITMENT_SMALL_ASK = [
        "just", "simply", "all you need to do", "quick", "easy first step",
        "small favor", "tiny commitment", "just a moment"
    ]
    COMMITMENT_ESCALATION = [
        "now that you've", "since you already", "you've come this far",
        "next step", "continue your journey", "build on"
    ]
    COMMITMENT_PUBLIC = [
        "share with friends", "post about", "tell others", "announce",
        "make it public", "let everyone know", "share your commitment"
    ]

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 5: SCARCITY
    # -------------------------------------------------------------------------
    SCARCITY_LIMITATION = re.compile(
        r'(?i)(limited\s+edition|only\s+\d+\s+left|scarce|in\s+short\s+supply|'
        r'running\s+out|while\s+supplies\s+last|rare|exclusive|'
        r'one-time\s+only|never\s+again)',
        re.IGNORECASE
    )
    SCARCITY_COMPETITION = re.compile(
        r'(?i)(many\s+want|quickly\s+selling|people.*buying|interest\s+is\s+high|'
        r'others.*getting|don\'t\s+miss\s+out|high\s+demand)',
        re.IGNORECASE
    )
    SCARCITY_DESTRUCTION = re.compile(
        r'(?i)(burn.*unsold|destroyed\s+forever|going\s+away\s+forever|'
        r'never\s+be\s+made|will\s+disappear|last\s+chance\s+forever)',
        re.IGNORECASE
    )
    SCARCITY_URGENCY = re.compile(
        r'(?i)(hurry|act\s+now|today\s+only|expires?|deadline|'
        r'before\s+midnight|rush|immediate|don\'t\s+delay|now\s+or\s+never)',
        re.IGNORECASE
    )

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 6: LIKING
    # -------------------------------------------------------------------------
    LIKING_SIMILARITY = [
        "just like you", "we're the same", "in common", "share your",
        "understand you", "been there", "know how you feel"
    ]
    LIKING_COMPLIMENTS = [
        "smart choice", "you clearly", "good taste", "discerning",
        "you're special", "you deserve", "you've earned"
    ]
    LIKING_FAMILIARITY = [
        "remember when", "you know how", "as you know", "familiar",
        "like talking to a friend", "between us"
    ]

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE 7: UNITY
    # -------------------------------------------------------------------------
    UNITY_INGROUP = [
        "we", "our", "us", "together", "our community", "fellow",
        "one of us", "part of", "family", "tribe", "movement"
    ]
    UNITY_SHARED_IDENTITY = [
        "as a", "being a", "like all", "every true", "real fans",
        "those who understand", "people who care about"
    ]

    # -------------------------------------------------------------------------
    # COGNITIVE BIASES
    # -------------------------------------------------------------------------
    ANCHORING_PATTERN = re.compile(
        r'(?:was|originally|normally|usually|regular(?:ly)?)\s*'
        r'[\$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        re.IGNORECASE
    )

    LOSS_FRAME_MARKERS = [
        "lose", "miss out", "waste", "before it's too late", "don't lose",
        "risk losing", "forfeit", "gone forever", "slip away"
    ]

    GAIN_FRAME_MARKERS = [
        "gain", "save", "earn", "get", "achieve", "win", "unlock",
        "discover", "enjoy", "benefit"
    ]

    # -------------------------------------------------------------------------
    # LINGUISTIC: RHETORICAL DEVICES
    # -------------------------------------------------------------------------
    RHETORICAL_QUESTION = re.compile(
        r'(?i)\b(?:isn\'t it|aren\'t we|don\'t you think|wouldn\'t you|couldn\'t we|'
        r'can we afford|how can anyone|who wouldn\'t want|what could be|'
        r'why would anyone|how else can|isn\'t it time|don\'t you deserve)',
        re.IGNORECASE
    )

    ANTITHESIS_PATTERN = re.compile(
        r'(?i)(?:not\s+\w+,?\s+but\s+\w+|ask not what.*ask what|'
        r'one small.*one giant|\w+\s+or\s+(?:death|liberty|nothing))',
        re.IGNORECASE
    )

    # -------------------------------------------------------------------------
    # LINGUISTIC: HEDGING & CERTAINTY
    # -------------------------------------------------------------------------
    HEDGING_WEAK = [
        "may", "might", "could", "possibly", "perhaps", "probably",
        "it seems", "it appears", "one might argue", "it could be said"
    ]

    CERTAINTY_BOOSTERS = [
        "clearly", "obviously", "without question", "the fact is",
        "everyone knows", "studies prove", "definitely", "absolutely",
        "certainly", "undoubtedly", "guaranteed"
    ]

    # -------------------------------------------------------------------------
    # LINGUISTIC: FRAMING
    # -------------------------------------------------------------------------
    EUPHEMISM_PAIRS = {
        "fired": ["let go", "downsized", "restructured", "released"],
        "died": ["passed away", "departed", "lost"],
        "lie": ["misspoke", "alternative facts", "inaccuracy"],
        "cheap": ["affordable", "budget-friendly", "economical"],
        "old": ["vintage", "classic", "heritage", "legacy"]
    }

    DYSPHEMISM_PAIRS = {
        "government": ["regime", "bureaucrats", "politicians"],
        "taxes": ["government theft", "burden", "extortion"],
        "regulation": ["red tape", "interference", "control"]
    }

    # -------------------------------------------------------------------------
    # LINGUISTIC: DISCOURSE MARKERS
    # -------------------------------------------------------------------------
    CAUSAL_MARKERS = ["because", "therefore", "so", "since", "thus", "hence", "as a result"]
    CONTRAST_MARKERS = ["but", "however", "although", "yet", "nevertheless", "despite"]
    URGENCY_MARKERS = ["now", "immediately", "urgent", "critical", "important", "must"]

    # -------------------------------------------------------------------------
    # LINGUISTIC: CONCEPTUAL METAPHORS (from LINGUISTIC_PERSUASION_RESEARCH.md)
    # Effectiveness: 88/100, Awareness: LOW
    # -------------------------------------------------------------------------
    METAPHOR_WAR = [
        "battle", "fight", "combat", "struggle", "victory", "defeat", "strategy",
        "tactics", "target", "ammunition", "arsenal", "conquer", "attack", "defend",
        "offensive", "campaign", "front lines", "trenches", "troops", "ally", "enemy",
        "casualties", "war on", "fighting", "crusade", "siege", "armory"
    ]

    METAPHOR_JOURNEY = [
        "path", "road", "journey", "destination", "milestone", "crossroads",
        "moving forward", "on track", "off track", "roadmap", "stepping stone",
        "navigate", "steer", "direction", "compass", "way forward", "detour",
        "the way", "heading", "course", "route"
    ]

    METAPHOR_HEALTH = [
        "healthy", "sick", "diagnosis", "symptom", "cure", "treatment",
        "toxic", "poison", "heal", "recover", "epidemic", "virus",
        "vital", "immune", "chronic", "acute", "remedy", "infection",
        "disease", "ailment", "syndrome", "therapy", "prognosis"
    ]

    METAPHOR_FAMILY = [
        "family", "parent", "child", "brother", "sister", "mother", "father",
        "born", "birth", "offspring", "heritage", "legacy", "generation",
        "nurture", "raised", "adopted", "orphan"
    ]

    METAPHOR_MACHINE = [
        "machine", "engine", "mechanism", "system", "component", "function",
        "process", "input", "output", "efficiency", "optimize", "automate",
        "programmed", "wired", "circuit", "gear", "cog"
    ]

    # Personification patterns (82/100 effectiveness)
    PERSONIFICATION_PATTERNS = re.compile(
        r'(?:the\s+)?(?:market|technology|algorithm|nature|economy|data|AI|'
        r'internet|science|history|time|fate|destiny|luck)\s+'
        r'(?:wants|demands|requires|decides|chooses|determines|tells|knows|'
        r'says|believes|thinks|needs|loves|hates|prefers|suggests)',
        re.IGNORECASE
    )

    # Metonymy (institutional)
    METONYMY_INSTITUTIONAL = [
        "washington", "wall street", "silicon valley", "the white house",
        "hollywood", "madison avenue", "fleet street", "downing street",
        "the pentagon", "brussels", "westminster", "main street"
    ]

    # Synecdoche (part for whole)
    SYNECDOCHE_PATTERNS = [
        "hired hands", "all eyes on", "boots on the ground", "the suits",
        "heads", "mouths to feed", "bodies", "souls", "hearts and minds"
    ]


# =============================================================================
# SECTION 2: DATA CLASSES
# =============================================================================

@dataclass
class DetectionResult:
    """Standard result format for all detectors."""
    category: str
    score: int  # 0-100
    intensity: str  # NONE, WEAK, MODERATE, STRONG, EXTREME
    matches: List[str]
    details: Dict[str, Any]

@dataclass
class AuditReport:
    """Complete audit report structure."""
    audit_id: str
    timestamp: str
    content_hash: str
    content_length: int
    tactical_stimulus: Dict[str, Any]
    psychological_principles: Dict[str, Any]
    linguistic_patterns: Dict[str, Any]
    composite_scores: Dict[str, Any]
    red_flags: List[Dict[str, Any]]
    classification: str


# =============================================================================
# SECTION 3: TACTICAL STIMULUS DETECTORS (6 Classes)
# =============================================================================

class PersonalStimulusDetector:
    """Detect self-centered targeting patterns."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Exclusion language (20 pts each, max 40)
        exclusion_matches = Patterns.PERSONAL_EXCLUSION.findall(text)
        exclusion_score = min(len(exclusion_matches) * 20, 40)
        if exclusion_matches:
            matches.extend(exclusion_matches)
            details["exclusion_language"] = exclusion_matches

        # Status threat (30 pts each, max 100)
        status_matches = [kw for kw in Patterns.PERSONAL_STATUS_THREAT if kw in text_lower]
        status_score = min(len(status_matches) * 30, 100)
        if status_matches:
            matches.extend(status_matches)
            details["status_threat"] = status_matches

        # Tribal safety (25 pts each)
        tribal_matches = [kw for kw in Patterns.PERSONAL_TRIBAL_SAFETY if kw in text_lower]
        tribal_score = len(tribal_matches) * 25
        if tribal_matches:
            matches.extend(tribal_matches)
            details["tribal_safety"] = tribal_matches

        # Composite calculation
        total_score = min(
            (exclusion_score / 60) * 40 +
            (status_score / 90) * 35 +
            (tribal_score / 175) * 25,
            100
        )

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="PERSONAL",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NONE"
        if score <= 40: return "WEAK"
        if score <= 60: return "MODERATE"
        if score <= 80: return "STRONG"
        return "EXTREME"


class ContrastableDetector:
    """Detect binary ideological framing."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {"pairs_detected": []}
        pairs_score = 0

        # Binary pairs (30 pts each if BOTH present)
        for pair_name, pair_words in Patterns.CONTRASTABLE_PAIRS.items():
            neg_found = any(w in text_lower for w in pair_words["negative"])
            pos_found = any(w in text_lower for w in pair_words["positive"])
            if neg_found and pos_found:
                pairs_score += 30
                details["pairs_detected"].append(pair_name)
                matches.append(pair_name)

        # Contrast markers (10 pts each, max 30)
        marker_matches = Patterns.CONTRASTABLE_MARKERS.findall(text)
        marker_score = min(len(marker_matches) * 10, 30)
        if marker_matches:
            matches.extend(marker_matches)
            details["contrast_markers"] = marker_matches

        # Spectrum penalty (-8 pts each)
        spectrum_matches = [kw for kw in Patterns.CONTRASTABLE_SPECTRUM_PENALTY if kw in text_lower]
        spectrum_penalty = len(spectrum_matches) * 8
        if spectrum_matches:
            details["spectrum_penalty"] = spectrum_matches

        # Composite
        total_score = max(0, min(
            (len(details["pairs_detected"]) / 4) * 50 +
            (marker_score / 30) * 30 +
            20 - spectrum_penalty,
            100
        ))

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="CONTRASTABLE",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "SPECTRUM"
        if score <= 50: return "SUBTLE"
        if score <= 75: return "CLEAR"
        return "SHARP"


class TangibleDetector:
    """Detect concrete vs. abstract language."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Weight specifications (20 pts each)
        weight_matches = Patterns.TANGIBLE_WEIGHT.findall(text)
        weight_score = len(weight_matches) * 20
        if weight_matches:
            matches.extend([f"{m[0]} {m[1]}" for m in weight_matches])
            details["weight_specs"] = weight_matches

        # Location (10-25 pts based on specificity)
        location_matches = Patterns.TANGIBLE_LOCATION.findall(text)
        location_score = 0
        if location_matches:
            for match in location_matches:
                loc = [m for m in match if m][0] if any(match) else ""
                if any(city in loc.lower() for city in ["portugal", "italy", "japan", "france"]):
                    location_score += 20
                else:
                    location_score += 10
            matches.extend([m for m in location_matches if m])
            details["locations"] = location_matches

        # Decay/change (20 pts with timeline, 5 pts vague)
        decay_matches = Patterns.TANGIBLE_DECAY.findall(text)
        decay_score = len(decay_matches) * 20
        if decay_matches:
            matches.extend([m[0] for m in decay_matches])
            details["decay_processes"] = decay_matches

        # Sensory details (15 pts specific, 3 pts vague)
        sensory_matches = Patterns.TANGIBLE_SENSORY.findall(text)
        sensory_score = 0
        for match in sensory_matches:
            desc = match[2] if len(match) > 2 else ""
            sensory_score += 15 if len(desc) > 10 else 3
        if sensory_matches:
            matches.extend([m[0] for m in sensory_matches])
            details["sensory_details"] = sensory_matches

        # Production artifacts (15 pts each, max 30)
        artifact_matches = [kw for kw in Patterns.TANGIBLE_ARTIFACTS if kw in text_lower]
        artifact_score = min(len(artifact_matches) * 15, 30)
        if artifact_matches:
            matches.extend(artifact_matches)
            details["artifacts"] = artifact_matches

        # Abstract penalty (-5 pts each)
        abstract_matches = [kw for kw in Patterns.TANGIBLE_ABSTRACT_PENALTY if kw in text_lower]
        abstract_penalty = len(abstract_matches) * 5
        if abstract_matches:
            details["abstract_penalty"] = abstract_matches

        # Composite
        total_score = max(0, min(
            (weight_score / 20) * 20 +
            (location_score / 25) * 20 +
            (decay_score / 20) * 20 +
            (sensory_score / 15) * 20 +
            (artifact_score / 30) * 20 -
            abstract_penalty,
            100
        ))

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="TANGIBLE",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 30: return "ABSTRACT"
        if score <= 65: return "MIXED"
        return "TANGIBLE"


class MemorableDetector:
    """Detect U-curve memory structure."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Split into thirds
        lines = text.split('\n')
        lines = [l.strip() for l in lines if l.strip()]
        if len(lines) < 3:
            lines = text.split('. ')

        third = max(1, len(lines) // 3)
        opening = ' '.join(lines[:third])
        middle = ' '.join(lines[third:2*third])
        closing = ' '.join(lines[2*third:])

        # Opening strength (20 pts each)
        opening_matches = Patterns.MEMORABLE_OPENING_SIGNALS.findall(opening)
        opening_score = len(opening_matches) * 20
        if len(opening) < 100:  # Brevity bonus
            opening_score += 10
        if opening_matches:
            matches.extend(opening_matches)
            details["opening_signals"] = opening_matches

        # Closing strength (20 pts each)
        closing_matches = Patterns.MEMORABLE_CLOSING_SIGNALS.findall(closing)
        closing_score = len(closing_matches) * 20
        if closing.strip().endswith('?'):
            closing_score += 10
        if closing_matches:
            matches.extend(closing_matches)
            details["closing_signals"] = closing_matches

        # Middle weakness (filler penalty, -5 pts each)
        filler_matches = [kw for kw in Patterns.MEMORABLE_FILLER if kw in middle.lower()]
        middle_weakness = len(filler_matches) * 5
        if filler_matches:
            details["middle_filler"] = filler_matches

        # U-curve detection bonus
        u_curve_detected = opening_score > 0 and closing_score > 0 and middle_weakness > 0
        u_curve_bonus = 20 if u_curve_detected else 0

        # Composite
        total_score = min(
            (opening_score / 40) * 40 +
            (closing_score / 40) * 40 +
            max(0, 20 - middle_weakness) +
            u_curve_bonus,
            100
        )

        details["u_curve_detected"] = u_curve_detected
        details["opening_score"] = opening_score
        details["closing_score"] = closing_score
        details["middle_weakness"] = middle_weakness

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="MEMORABLE",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 30: return "DISPERSED"
        if score <= 60: return "SUBTLE"
        return "U_CURVE"


class VisualDetector:
    """Detect anti-aesthetic vs. polished visual language."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Anti-aesthetic (15 pts each)
        anti_matches = [kw for kw in Patterns.VISUAL_ANTI_AESTHETIC if kw in text_lower]
        anti_score = len(anti_matches) * 15
        if anti_matches:
            matches.extend(anti_matches)
            details["anti_aesthetic"] = anti_matches

        # No-styling (15 pts each)
        nostyling_matches = [kw for kw in Patterns.VISUAL_NO_STYLING if kw in text_lower]
        nostyling_score = len(nostyling_matches) * 15
        if nostyling_matches:
            matches.extend(nostyling_matches)
            details["no_styling"] = nostyling_matches

        # Mood board (10 pts each)
        mood_matches = [kw for kw in Patterns.VISUAL_MOOD_BOARD if kw in text_lower]
        mood_score = len(mood_matches) * 10
        if mood_matches:
            matches.extend(mood_matches)
            details["mood_board"] = mood_matches

        # Polished penalty (-10 pts each)
        polished_matches = [kw for kw in Patterns.VISUAL_POLISHED_PENALTY if kw in text_lower]
        polished_penalty = len(polished_matches) * 10
        if polished_matches:
            details["polished_penalty"] = polished_matches

        # Composite
        total_score = max(0, min(
            (anti_score / 60) * 35 +
            (nostyling_score / 30) * 30 +
            (mood_score / 40) * 25 -
            polished_penalty,
            100
        ))

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="VISUAL",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 30: return "POLISHED"
        if score <= 60: return "MIXED"
        return "DOCUMENTARY"


class EmotionalDetector:
    """Detect pain→relief emotional arc."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Pain detection (15 pts each)
        pain_score = 0
        pain_matches = []
        for category, keywords in Patterns.EMOTIONAL_PAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    pain_score += 15
                    pain_matches.append(kw)
        if pain_matches:
            matches.extend(pain_matches)
            details["pain_triggers"] = pain_matches

        # Relief detection (15 pts each)
        relief_score = 0
        relief_matches = []
        for category, keywords in Patterns.EMOTIONAL_RELIEF_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    relief_score += 15
                    relief_matches.append(kw)
        if relief_matches:
            matches.extend(relief_matches)
            details["relief_signals"] = relief_matches

        # Arc completion bonus
        arc_complete = pain_score > 0 and relief_score > 0
        arc_bonus = 25 if arc_complete else 0

        # Composite
        total_score = min(
            ((pain_score + relief_score) / 2 / 100) * 100 + arc_bonus,
            100
        )

        details["pain_score"] = pain_score
        details["relief_score"] = relief_score
        details["arc_complete"] = arc_complete

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="EMOTIONAL",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NO_ARC"
        if score <= 50: return "WEAK"
        return "STRONG_ARC"


# =============================================================================
# SECTION 4: PSYCHOLOGICAL PRINCIPLE DETECTORS (7+ Classes)
# =============================================================================

class AuthorityDetector:
    """Detect authority and credibility signals."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Credentials (15 pts each)
        cred_matches = [kw for kw in Patterns.AUTHORITY_CREDENTIALS if kw in text_lower]
        cred_score = len(cred_matches) * 15
        if cred_matches:
            matches.extend(cred_matches)
            details["credentials"] = cred_matches

        # Institutions (20 pts each)
        inst_matches = [kw for kw in Patterns.AUTHORITY_INSTITUTIONS if kw in text_lower]
        inst_score = len(inst_matches) * 20
        if inst_matches:
            matches.extend(inst_matches)
            details["institutions"] = inst_matches

        # Confidence markers (10 pts each, max 80)
        conf_matches = Patterns.AUTHORITY_CONFIDENCE.findall(text)
        conf_score = min(len(conf_matches) * 10, 80)
        if conf_matches:
            matches.extend(conf_matches)
            details["confidence_markers"] = conf_matches

        # Threat penalty (-20 pts each)
        threat_matches = [kw for kw in Patterns.AUTHORITY_THREAT_PENALTY if kw in text_lower]
        threat_penalty = len(threat_matches) * 20
        if threat_matches:
            details["threat_penalty"] = threat_matches

        # Composite
        competence_total = min(cred_score + inst_score, 100)
        # Authority formula: (competence + confidence) / max(1, threat_penalty / 20)
        # TODO: Justify divisor of 20; verify threat_penalty scaling against authority scoring distribution
        formula_result = (competence_total + conf_score) / max(1, threat_penalty / 20)
        total_score = min(formula_result, 100)

        details["competence_score"] = competence_total
        details["confidence_score"] = conf_score
        details["formula_result"] = formula_result

        # Compliance probability
        if total_score < 5:
            compliance = "Low (20-30%)"
        elif total_score < 15:
            compliance = "Moderate (40-50%)"
        elif total_score < 30:
            compliance = "High (65%+)"
        else:
            compliance = "Extreme (65-100%)"
        details["compliance_probability"] = compliance

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="AUTHORITY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score < 10: return "LOW"
        if score < 25: return "MODERATE"
        if score < 50: return "STRONG"
        return "EXTREME"


class SocialProofDetector:
    """Detect social proof and consensus signals."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Consensus language (15 pts each)
        consensus_matches = [kw for kw in Patterns.SOCIAL_PROOF_CONSENSUS if kw in text_lower]
        consensus_score = len(consensus_matches) * 15
        if consensus_matches:
            matches.extend(consensus_matches)
            details["consensus_signals"] = consensus_matches

        # Similarity language (12 pts each)
        similarity_matches = [kw for kw in Patterns.SOCIAL_PROOF_SIMILARITY if kw in text_lower]
        similarity_score = len(similarity_matches) * 12
        if similarity_matches:
            matches.extend(similarity_matches)
            details["similarity_signals"] = similarity_matches

        # Numbers (15 pts each)
        number_matches = Patterns.SOCIAL_PROOF_NUMBERS.findall(text)
        number_score = len(number_matches) * 15
        if number_matches:
            matches.extend(number_matches)
            details["number_claims"] = number_matches

        # Composite
        total_score = min(consensus_score + similarity_score + number_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="SOCIAL_PROOF",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "WEAK"
        if score <= 50: return "MODERATE"
        return "STRONG"


class ReciprocityDetector:
    """Detect reciprocity and obligation signals."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Free signals (20 pts each)
        free_matches = [kw for kw in Patterns.RECIPROCITY_FREE if kw in text_lower]
        free_score = len(free_matches) * 20
        if free_matches:
            matches.extend(free_matches)
            details["free_signals"] = free_matches

        # Obligation language (25 pts each)
        obligation_matches = [kw for kw in Patterns.RECIPROCITY_OBLIGATION if kw in text_lower]
        obligation_score = len(obligation_matches) * 25
        if obligation_matches:
            matches.extend(obligation_matches)
            details["obligation_language"] = obligation_matches

        # Composite
        total_score = min(free_score + obligation_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="RECIPROCITY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "MINIMAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class CommitmentDetector:
    """Detect commitment and consistency patterns."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Small asks (15 pts each)
        small_matches = [kw for kw in Patterns.COMMITMENT_SMALL_ASK if kw in text_lower]
        small_score = len(small_matches) * 15
        if small_matches:
            matches.extend(small_matches)
            details["small_asks"] = small_matches

        # Escalation (20 pts each)
        escalation_matches = [kw for kw in Patterns.COMMITMENT_ESCALATION if kw in text_lower]
        escalation_score = len(escalation_matches) * 20
        if escalation_matches:
            matches.extend(escalation_matches)
            details["escalation"] = escalation_matches

        # Public commitment (25 pts each)
        public_matches = [kw for kw in Patterns.COMMITMENT_PUBLIC if kw in text_lower]
        public_score = len(public_matches) * 25
        if public_matches:
            matches.extend(public_matches)
            details["public_commitment"] = public_matches

        # Composite
        total_score = min(small_score + escalation_score + public_score, 100)

        details["small_commitment_present"] = len(small_matches) > 0
        details["escalation_present"] = len(escalation_matches) > 0
        details["public_commitment_present"] = len(public_matches) > 0

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="COMMITMENT",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 15: return "MINIMAL"
        if score <= 40: return "MODERATE"
        return "STRONG"


class ScarcityDetector:
    """Detect scarcity and urgency signals."""

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        # Limitation (15 pts each)
        limitation_matches = Patterns.SCARCITY_LIMITATION.findall(text)
        limitation_score = len(limitation_matches) * 15
        if limitation_matches:
            matches.extend(limitation_matches)
            details["limitation_signals"] = limitation_matches

        # Competition (20 pts each)
        competition_matches = Patterns.SCARCITY_COMPETITION.findall(text)
        competition_score = len(competition_matches) * 20
        if competition_matches:
            matches.extend(competition_matches)
            details["competition_signals"] = competition_matches

        # Destruction (30 pts each)
        destruction_matches = Patterns.SCARCITY_DESTRUCTION.findall(text)
        destruction_score = len(destruction_matches) * 30
        if destruction_matches:
            matches.extend(destruction_matches)
            details["destruction_signals"] = destruction_matches

        # Urgency (15 pts each)
        urgency_matches = Patterns.SCARCITY_URGENCY.findall(text)
        urgency_score = len(urgency_matches) * 15
        if urgency_matches:
            matches.extend(urgency_matches)
            details["urgency_signals"] = urgency_matches

        # Composite
        total_score = min(
            limitation_score + competition_score + destruction_score + urgency_score,
            100
        )

        # Determine strongest mechanism
        scores = {
            "limitation": limitation_score,
            "competition": competition_score,
            "destruction": destruction_score,
            "urgency": urgency_score
        }
        strongest = max(scores, key=scores.get) if any(scores.values()) else "none"
        details["strongest_mechanism"] = strongest

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="SCARCITY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 30: return "MILD"
        if score <= 60: return "MODERATE"
        return "STRONG"


class LikingDetector:
    """Detect liking and rapport signals."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Similarity (15 pts each)
        similarity_matches = [kw for kw in Patterns.LIKING_SIMILARITY if kw in text_lower]
        similarity_score = len(similarity_matches) * 15
        if similarity_matches:
            matches.extend(similarity_matches)
            details["similarity_signals"] = similarity_matches

        # Compliments (12 pts each)
        compliment_matches = [kw for kw in Patterns.LIKING_COMPLIMENTS if kw in text_lower]
        compliment_score = len(compliment_matches) * 12
        if compliment_matches:
            matches.extend(compliment_matches)
            details["compliments"] = compliment_matches

        # Familiarity (10 pts each)
        familiarity_matches = [kw for kw in Patterns.LIKING_FAMILIARITY if kw in text_lower]
        familiarity_score = len(familiarity_matches) * 10
        if familiarity_matches:
            matches.extend(familiarity_matches)
            details["familiarity_signals"] = familiarity_matches

        # Composite
        total_score = min(similarity_score + compliment_score + familiarity_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="LIKING",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "MINIMAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class UnityDetector:
    """Detect unity and in-group signals."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # In-group language (10 pts each)
        ingroup_matches = [kw for kw in Patterns.UNITY_INGROUP if kw in text_lower]
        ingroup_score = len(ingroup_matches) * 10
        if ingroup_matches:
            matches.extend(ingroup_matches)
            details["ingroup_language"] = ingroup_matches

        # Shared identity (15 pts each)
        identity_matches = [kw for kw in Patterns.UNITY_SHARED_IDENTITY if kw in text_lower]
        identity_score = len(identity_matches) * 15
        if identity_matches:
            matches.extend(identity_matches)
            details["shared_identity"] = identity_matches

        # Composite
        total_score = min(ingroup_score + identity_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="UNITY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "MINIMAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class FramingDetector:
    """Detect gain/loss framing and anchoring."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Loss framing (20 pts per marker)
        loss_matches = [kw for kw in Patterns.LOSS_FRAME_MARKERS if kw in text_lower]
        loss_score = len(loss_matches) * 20
        if loss_matches:
            matches.extend(loss_matches)
            details["loss_frame"] = loss_matches

        # Gain framing (10 pts per marker)
        gain_matches = [kw for kw in Patterns.GAIN_FRAME_MARKERS if kw in text_lower]
        gain_score = len(gain_matches) * 10
        if gain_matches:
            matches.extend(gain_matches)
            details["gain_frame"] = gain_matches

        # Anchoring (15 pts if found)
        anchor_matches = Patterns.ANCHORING_PATTERN.findall(text)
        anchor_score = 15 if anchor_matches else 0
        if anchor_matches:
            matches.extend(anchor_matches)
            details["anchoring"] = anchor_matches

        # Composite - loss framing weighted more heavily
        total_score = min(loss_score + (gain_score / 2) + anchor_score, 100)

        # Determine dominant frame
        if loss_score > gain_score:
            details["dominant_frame"] = "LOSS"
        elif gain_score > loss_score:
            details["dominant_frame"] = "GAIN"
        else:
            details["dominant_frame"] = "BALANCED"

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="FRAMING",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NEUTRAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


# =============================================================================
# SECTION 5: LINGUISTIC PATTERN DETECTORS (8 Classes)
# =============================================================================

class RhetoricalDeviceDetector:
    """Detect rhetorical devices in text."""

    DEVICE_SCORES = {
        "anaphora": 25,
        "antithesis": 30,
        "rhetorical_question": 15,
        "tricolon": 15,
        "alliteration": 10,
    }

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {"devices_found": []}
        total_score = 0

        # Rhetorical questions
        rq_matches = Patterns.RHETORICAL_QUESTION.findall(text)
        if rq_matches:
            score = len(rq_matches) * self.DEVICE_SCORES["rhetorical_question"]
            total_score += score
            matches.extend(rq_matches)
            details["devices_found"].append({"type": "rhetorical_question", "count": len(rq_matches)})

        # Antithesis
        anti_matches = Patterns.ANTITHESIS_PATTERN.findall(text)
        if anti_matches:
            score = len(anti_matches) * self.DEVICE_SCORES["antithesis"]
            total_score += score
            matches.extend(anti_matches)
            details["devices_found"].append({"type": "antithesis", "count": len(anti_matches)})

        # Anaphora (repeated sentence openings)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) >= 3:
            openings = [' '.join(s.split()[:2]).lower() for s in sentences if len(s.split()) >= 2]
            opening_counts = Counter(openings)
            for opening, count in opening_counts.items():
                if count >= 3:
                    total_score += self.DEVICE_SCORES["anaphora"]
                    matches.append(f"anaphora: '{opening}' x{count}")
                    details["devices_found"].append({"type": "anaphora", "pattern": opening, "count": count})

        # Tricolon (three-part lists)
        tricolon_pattern = r'(\w+(?:\s+\w+)?),\s+(\w+(?:\s+\w+)?),\s+and\s+(\w+(?:\s+\w+)?)'
        tricolon_matches = re.findall(tricolon_pattern, text)
        if tricolon_matches:
            total_score += len(tricolon_matches) * self.DEVICE_SCORES["tricolon"]
            matches.extend([', '.join(m) for m in tricolon_matches])
            details["devices_found"].append({"type": "tricolon", "count": len(tricolon_matches)})

        # Alliteration
        words = text.lower().split()
        alliteration_count = 0
        for i in range(len(words) - 2):
            w1 = re.sub(r'[^a-z]', '', words[i])
            w2 = re.sub(r'[^a-z]', '', words[i+1])
            w3 = re.sub(r'[^a-z]', '', words[i+2])
            if w1 and w2 and w3 and w1[0] == w2[0] == w3[0]:
                alliteration_count += 1
        if alliteration_count:
            total_score += alliteration_count * self.DEVICE_SCORES["alliteration"]
            details["devices_found"].append({"type": "alliteration", "count": alliteration_count})

        total_score = min(total_score, 100)
        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="RHETORICAL_DEVICES",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 25: return "MINIMAL"
        if score <= 50: return "MODERATE"
        if score <= 75: return "STRONG"
        return "EXTREME"


class SyntacticPatternDetector:
    """Detect syntactic patterns affecting persuasion."""

    PASSIVE_PATTERNS = [
        r'\b(?:was|were|been|being)\s+\w+ed\b',
        r'\b(?:has|have|had)\s+been\s+\w+ed\b',
        r'\b(?:is|are)\s+being\s+\w+ed\b',
    ]

    NOMINALIZATION_SUFFIXES = ['-tion', '-ment', '-ness', '-ity', '-ance', '-ence']

    NEGATIVE_CONTEXT = [
        'error', 'mistake', 'failure', 'problem', 'issue', 'fault',
        'loss', 'damage', 'harm', 'delay', 'decline', 'criticism'
    ]

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Passive voice detection
        passive_count = 0
        passive_in_negative = 0
        for pattern in self.PASSIVE_PATTERNS:
            passive_matches = re.findall(pattern, text, re.IGNORECASE)
            passive_count += len(passive_matches)
            # Check if in negative context
            for match in passive_matches:
                # Context window: ±50 characters around keyword for passive voice detection
                # TODO: Justify why 50 chars optimal; research passive voice detection accuracy at different window sizes
                context_start = max(0, text_lower.find(match.lower()) - 50)
                context_end = min(len(text_lower), text_lower.find(match.lower()) + 50)
                context = text_lower[context_start:context_end]
                if any(neg in context for neg in self.NEGATIVE_CONTEXT):
                    passive_in_negative += 1

        # Passive voice scoring: 5 pts base, +15 if in negative context
        passive_score = passive_count * 5 + passive_in_negative * 15
        details["passive_voice_count"] = passive_count
        details["passive_in_negative_context"] = passive_in_negative

        # Nominalization detection
        nominalization_count = 0
        for suffix in self.NOMINALIZATION_SUFFIXES:
            pattern = r'\w+' + suffix.replace('-', '') + r'\b'
            nom_matches = re.findall(pattern, text, re.IGNORECASE)
            nominalization_count += len(nom_matches)

        nominalization_score = nominalization_count * 3
        details["nominalization_count"] = nominalization_count

        # Sentence length analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if sentences:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            short_sentences = sum(1 for s in sentences if len(s.split()) <= 5)
            short_ratio = short_sentences / len(sentences)

            # Short declarative sentences = confidence (5 pts each if >30% short)
            short_score = 5 * short_sentences if short_ratio > 0.3 else 0
            details["avg_sentence_length"] = round(avg_length, 1)
            details["short_sentence_ratio"] = round(short_ratio, 2)
        else:
            short_score = 0

        # Composite
        total_score = min(passive_score + nominalization_score + short_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="SYNTACTIC_PATTERNS",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NEUTRAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class FramingEffectDetector:
    """Detect semantic framing effects."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Loss framing (20 pts each)
        loss_matches = [kw for kw in Patterns.LOSS_FRAME_MARKERS if kw in text_lower]
        loss_score = len(loss_matches) * 20
        if loss_matches:
            matches.extend(loss_matches)
            details["loss_frame_markers"] = loss_matches

        # Gain framing (10 pts each)
        gain_matches = [kw for kw in Patterns.GAIN_FRAME_MARKERS if kw in text_lower]
        gain_score = len(gain_matches) * 10
        if gain_matches:
            matches.extend(gain_matches)
            details["gain_frame_markers"] = gain_matches

        # Euphemism detection (15 pts each)
        euphemism_count = 0
        for harsh, softs in Patterns.EUPHEMISM_PAIRS.items():
            for soft in softs:
                if soft in text_lower:
                    euphemism_count += 1
                    matches.append(f"euphemism: {soft}")
        euphemism_score = euphemism_count * 15
        details["euphemism_count"] = euphemism_count

        # Dysphemism detection (15 pts each)
        dysphemism_count = 0
        for neutral, harshes in Patterns.DYSPHEMISM_PAIRS.items():
            for harsh in harshes:
                if harsh in text_lower:
                    dysphemism_count += 1
                    matches.append(f"dysphemism: {harsh}")
        dysphemism_score = dysphemism_count * 15
        details["dysphemism_count"] = dysphemism_count

        # Composite
        total_score = min(loss_score + gain_score + euphemism_score + dysphemism_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="FRAMING_EFFECTS",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 25: return "NEUTRAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class PragmaticPatternDetector:
    """Detect pragmatic patterns (presuppositions, indirect directives)."""

    PRESUPPOSITION_MARKERS = [
        "the", "your", "when", "realize", "discover", "finally",
        "again", "still", "even", "only", "just"
    ]

    INDIRECT_DIRECTIVE_MARKERS = [
        "imagine", "consider", "think about", "let's", "suppose",
        "picture", "envision", "what if"
    ]

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Presupposition patterns (10 pts each for loaded presuppositions)
        presup_count = 0
        # "The X" presupposes X exists
        the_patterns = re.findall(r'\bthe\s+(\w+(?:\s+\w+)?)\s+(?:you|that|which)', text_lower)
        presup_count += len(the_patterns)
        # "Your X" presupposes you have X
        your_patterns = re.findall(r'\byour\s+(\w+)', text_lower)
        presup_count += len(your_patterns)
        # "Finally" presupposes previous failed attempts
        if "finally" in text_lower:
            presup_count += 1
            matches.append("finally (presupposes prior attempts)")
        # "Discover" presupposes something exists to be discovered
        if "discover" in text_lower:
            presup_count += 1
            matches.append("discover (presupposes existence)")

        presup_score = presup_count * 10
        details["presupposition_count"] = presup_count

        # Indirect directives (8 pts each)
        directive_matches = [kw for kw in self.INDIRECT_DIRECTIVE_MARKERS if kw in text_lower]
        directive_score = len(directive_matches) * 8
        if directive_matches:
            matches.extend(directive_matches)
            details["indirect_directives"] = directive_matches

        # Composite
        total_score = min(presup_score + directive_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="PRAGMATIC_PATTERNS",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "MINIMAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class DiscourseMarkerDetector:
    """Detect discourse markers and their effects."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Causal markers (5 pts each)
        causal_matches = [kw for kw in Patterns.CAUSAL_MARKERS if kw in text_lower]
        causal_score = len(causal_matches) * 5
        if causal_matches:
            matches.extend(causal_matches)
            details["causal_markers"] = causal_matches

        # Check for pseudo-reasoning (because + weak reason = 15 pts)
        because_matches = re.findall(r'because\s+([^.!?]+)', text_lower)
        pseudo_reason_score = 0
        for reason in because_matches:
            # Weak reasons are short or circular
            if len(reason.split()) < 5 or "you want" in reason or "it is" in reason:
                pseudo_reason_score += 15
                matches.append(f"pseudo-reason: 'because {reason[:30]}...'")
        details["pseudo_reasoning_count"] = pseudo_reason_score // 15

        # Contrast markers (3 pts each)
        contrast_matches = [kw for kw in Patterns.CONTRAST_MARKERS if kw in text_lower]
        contrast_score = len(contrast_matches) * 3
        if contrast_matches:
            matches.extend(contrast_matches)
            details["contrast_markers"] = contrast_matches

        # Urgency markers (12 pts each)
        urgency_matches = [kw for kw in Patterns.URGENCY_MARKERS if kw in text_lower]
        urgency_score = len(urgency_matches) * 12
        if urgency_matches:
            matches.extend(urgency_matches)
            details["urgency_markers"] = urgency_matches

        # Composite
        total_score = min(causal_score + pseudo_reason_score + contrast_score + urgency_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="DISCOURSE_MARKERS",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NEUTRAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class HedgingCertaintyDetector:
    """Detect hedging and certainty markers."""

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Hedging (weak certainty) - 3 pts each
        hedge_matches = [kw for kw in Patterns.HEDGING_WEAK if kw in text_lower]
        hedge_score = len(hedge_matches) * 3
        if hedge_matches:
            matches.extend(hedge_matches)
            details["hedges"] = hedge_matches

        # Boosters (strong certainty) - 5 pts each
        booster_matches = [kw for kw in Patterns.CERTAINTY_BOOSTERS if kw in text_lower]
        booster_score = len(booster_matches) * 5
        if booster_matches:
            matches.extend(booster_matches)
            details["boosters"] = booster_matches

        # Asymmetric hedging detection (30 pts if unbalanced)
        # If boosters >> hedges, suspicious overclaiming
        asymmetric_score = 0
        if booster_score > 0 and hedge_score == 0:
            asymmetric_score = 30
            details["asymmetric_hedging"] = "All boosters, no hedges - overclaiming"
        elif booster_score > hedge_score * 3:
            asymmetric_score = 20
            details["asymmetric_hedging"] = "Significantly more boosters than hedges"

        # Composite
        total_score = min(hedge_score + booster_score + asymmetric_score, 100)

        details["hedge_count"] = len(hedge_matches)
        details["booster_count"] = len(booster_matches)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="HEDGING_CERTAINTY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "BALANCED"
        if score <= 50: return "MODERATE"
        return "ASYMMETRIC"


class RegisterFormalityDetector:
    """Detect register and formality patterns."""

    FORMAL_MARKERS = [
        "utilize", "commence", "furthermore", "moreover", "whereas",
        "hereby", "therefore", "thus", "henceforth", "notwithstanding"
    ]

    INFORMAL_MARKERS = [
        "gonna", "wanna", "gotta", "kinda", "sorta", "yeah", "nope",
        "hey", "cool", "awesome", "stuff", "thing", "basically"
    ]

    INTIMACY_MARKERS = [
        "between us", "just between you and me", "honestly", "truthfully",
        "I'll be real", "let me tell you", "trust me", "friend"
    ]

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {}

        # Formal markers (5 pts each)
        formal_matches = [kw for kw in self.FORMAL_MARKERS if kw in text_lower]
        formal_score = len(formal_matches) * 5
        if formal_matches:
            matches.extend(formal_matches)
            details["formal_markers"] = formal_matches

        # Informal markers (3 pts each)
        informal_matches = [kw for kw in self.INFORMAL_MARKERS if kw in text_lower]
        informal_score = len(informal_matches) * 3
        if informal_matches:
            matches.extend(informal_matches)
            details["informal_markers"] = informal_matches

        # Intimacy markers (10 pts each - creates false closeness)
        intimacy_matches = [kw for kw in self.INTIMACY_MARKERS if kw in text_lower]
        intimacy_score = len(intimacy_matches) * 10
        if intimacy_matches:
            matches.extend(intimacy_matches)
            details["intimacy_markers"] = intimacy_matches

        # Contractions count (informal indicator)
        contractions = re.findall(r"\b\w+'\w+\b", text)
        contraction_score = min(len(contractions) * 2, 20)
        details["contraction_count"] = len(contractions)

        # Determine register
        if formal_score > informal_score + intimacy_score:
            register = "FORMAL"
        elif intimacy_score > formal_score + informal_score:
            register = "INTIMATE"
        elif informal_score > formal_score:
            register = "INFORMAL"
        else:
            register = "NEUTRAL"
        details["dominant_register"] = register

        # Composite - higher score for strategic register variation
        total_score = min(formal_score + informal_score + intimacy_score + contraction_score, 100)

        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="REGISTER_FORMALITY",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "NEUTRAL"
        if score <= 50: return "MODERATE"
        return "STRONG"


class ConceptualMetaphorDetector:
    """
    Detect conceptual metaphors that shape perception of abstract concepts.
    Based on Lakoff & Johnson (1980) and Thibodeau & Boroditsky (2011).
    Effectiveness: 88/100, Awareness: LOW
    """

    METAPHOR_SCORES = {
        "war": 12,        # Highest - activates conflict mindset
        "health": 10,     # High - creates urgency
        "journey": 8,     # Moderate - implies linear progress
        "family": 8,      # Moderate - emotional connection
        "machine": 6,     # Lower - dehumanization
    }

    def detect(self, text: str) -> DetectionResult:
        text_lower = text.lower()
        matches = []
        details = {"metaphor_domains": {}}
        total_score = 0

        # War/Battle metaphors (92/100 effectiveness)
        war_matches = [kw for kw in Patterns.METAPHOR_WAR if kw in text_lower]
        if war_matches:
            war_score = len(war_matches) * self.METAPHOR_SCORES["war"]
            total_score += war_score
            matches.extend([f"war: {m}" for m in war_matches])
            details["metaphor_domains"]["war"] = {
                "count": len(war_matches),
                "score": war_score,
                "matches": war_matches
            }

        # Journey/Path metaphors (85/100 effectiveness)
        journey_matches = [kw for kw in Patterns.METAPHOR_JOURNEY if kw in text_lower]
        if journey_matches:
            journey_score = len(journey_matches) * self.METAPHOR_SCORES["journey"]
            total_score += journey_score
            matches.extend([f"journey: {m}" for m in journey_matches])
            details["metaphor_domains"]["journey"] = {
                "count": len(journey_matches),
                "score": journey_score,
                "matches": journey_matches
            }

        # Health/Disease metaphors (88/100 effectiveness)
        health_matches = [kw for kw in Patterns.METAPHOR_HEALTH if kw in text_lower]
        if health_matches:
            health_score = len(health_matches) * self.METAPHOR_SCORES["health"]
            total_score += health_score
            matches.extend([f"health: {m}" for m in health_matches])
            details["metaphor_domains"]["health"] = {
                "count": len(health_matches),
                "score": health_score,
                "matches": health_matches
            }

        # Family/Kinship metaphors (80/100 effectiveness)
        family_matches = [kw for kw in Patterns.METAPHOR_FAMILY if kw in text_lower]
        if family_matches:
            family_score = len(family_matches) * self.METAPHOR_SCORES["family"]
            total_score += family_score
            matches.extend([f"family: {m}" for m in family_matches])
            details["metaphor_domains"]["family"] = {
                "count": len(family_matches),
                "score": family_score,
                "matches": family_matches
            }

        # Machine/System metaphors (75/100 effectiveness)
        machine_matches = [kw for kw in Patterns.METAPHOR_MACHINE if kw in text_lower]
        if machine_matches:
            machine_score = len(machine_matches) * self.METAPHOR_SCORES["machine"]
            total_score += machine_score
            matches.extend([f"machine: {m}" for m in machine_matches])
            details["metaphor_domains"]["machine"] = {
                "count": len(machine_matches),
                "score": machine_score,
                "matches": machine_matches
            }

        # Personification (82/100 effectiveness, +12 per instance)
        personification_matches = Patterns.PERSONIFICATION_PATTERNS.findall(text)
        if personification_matches:
            pers_score = len(personification_matches) * 12
            total_score += pers_score
            matches.extend([f"personification: {m}" for m in personification_matches])
            details["personification"] = {
                "count": len(personification_matches),
                "score": pers_score,
                "matches": personification_matches
            }

        # Metonymy (institutional, +8 per instance)
        metonymy_matches = [kw for kw in Patterns.METONYMY_INSTITUTIONAL if kw in text_lower]
        if metonymy_matches:
            met_score = len(metonymy_matches) * 8
            total_score += met_score
            matches.extend([f"metonymy: {m}" for m in metonymy_matches])
            details["metonymy"] = {
                "count": len(metonymy_matches),
                "score": met_score,
                "matches": metonymy_matches
            }

        # Synecdoche (+10 per instance)
        synecdoche_matches = [kw for kw in Patterns.SYNECDOCHE_PATTERNS if kw in text_lower]
        if synecdoche_matches:
            syn_score = len(synecdoche_matches) * 10
            total_score += syn_score
            matches.extend([f"synecdoche: {m}" for m in synecdoche_matches])
            details["synecdoche"] = {
                "count": len(synecdoche_matches),
                "score": syn_score,
                "matches": synecdoche_matches
            }

        # Determine dominant metaphor domain
        if details["metaphor_domains"]:
            dominant = max(
                details["metaphor_domains"].items(),
                key=lambda x: x[1]["score"]
            )
            details["dominant_domain"] = dominant[0]
        else:
            details["dominant_domain"] = "none"

        total_score = min(total_score, 100)
        intensity = self._classify_intensity(total_score)

        return DetectionResult(
            category="CONCEPTUAL_METAPHOR",
            score=int(total_score),
            intensity=intensity,
            matches=matches,
            details=details
        )

    def _classify_intensity(self, score: int) -> str:
        if score <= 20: return "MINIMAL"
        if score <= 40: return "MODERATE"
        if score <= 60: return "STRONG"
        return "PERVASIVE"


# =============================================================================
# SECTION 6: COMPOSITE SCORING
# =============================================================================

class CompositeScorer:
    """Calculate composite influence scores from all detectors."""

    # Composite score weighting: Tactical (35%), Psychological (35%), Linguistic (30%)
    # TODO: Research why these weights; verify empirical basis for tactical/psychological equivalence
    WEIGHTS = {
        "tactical": 0.35,      # Authority, credibility, source signals
        "psychological": 0.35, # Emotional triggers, cognitive biases
        "linguistic": 0.30     # Passive voice, intensifiers, loaded language
    }

    # Classification ranges: inclusive on lower bound, exclusive on upper
    # Boundary rationale: TODO - Research why these thresholds (25, 50, 75) were selected
    CLASSIFICATION_THRESHOLDS = {
        (0, 25): "LOW",        # 0-25: Below influence threshold
        (26, 50): "MODERATE",  # 26-50: Moderate influence intensity
        (51, 75): "HIGH",      # 51-75: High influence intensity
        (76, 100): "EXTREME"   # 76-100: Extreme influence intensity
    }

    def calculate(
        self,
        tactical_results: Dict[str, DetectionResult],
        psychological_results: Dict[str, DetectionResult],
        linguistic_results: Dict[str, DetectionResult]
    ) -> Dict[str, Any]:
        """Calculate composite scores from all detection results."""

        # Calculate averages
        tactical_scores = [r.score for r in tactical_results.values()]
        tactical_avg = sum(tactical_scores) / len(tactical_scores) if tactical_scores else 0

        psychological_scores = [r.score for r in psychological_results.values()]
        psychological_avg = sum(psychological_scores) / len(psychological_scores) if psychological_scores else 0

        linguistic_scores = [r.score for r in linguistic_results.values()]
        linguistic_avg = sum(linguistic_scores) / len(linguistic_scores) if linguistic_scores else 0

        # Weighted composite
        composite_score = (
            tactical_avg * self.WEIGHTS["tactical"] +
            psychological_avg * self.WEIGHTS["psychological"] +
            linguistic_avg * self.WEIGHTS["linguistic"]
        )
        composite_score = min(composite_score, 100)

        # Classification
        classification = "LOW"
        for (low, high), label in self.CLASSIFICATION_THRESHOLDS.items():
            if low <= composite_score <= high:
                classification = label
                break

        return {
            "tactical_average": round(tactical_avg, 1),
            "psychological_average": round(psychological_avg, 1),
            "linguistic_average": round(linguistic_avg, 1),
            "overall_influence_index": round(composite_score, 1),
            "classification": classification,
            "classification_description": self._get_description(classification)
        }

    def _get_description(self, classification: str) -> str:
        descriptions = {
            "LOW": "Ethical messaging with minimal influence tactics",
            "MODERATE": "Some targeting present, standard marketing",
            "HIGH": "Sophisticated influence strategy detected",
            "EXTREME": "Intensive influence tactics deployed"
        }
        return descriptions.get(classification, "Unknown")


# =============================================================================
# SECTION 7: RED FLAG GENERATOR
# =============================================================================

class RedFlagGenerator:
    """Generate red flags from detection results."""

    HIGH_SCORE_THRESHOLD = 60
    EXTREME_SCORE_THRESHOLD = 80

    def generate(
        self,
        tactical_results: Dict[str, DetectionResult],
        psychological_results: Dict[str, DetectionResult],
        linguistic_results: Dict[str, DetectionResult]
    ) -> List[Dict[str, Any]]:
        """Generate list of red flags from detection results."""

        red_flags = []

        # Check tactical results
        for category, result in tactical_results.items():
            if result.score >= self.EXTREME_SCORE_THRESHOLD:
                red_flags.append({
                    "category": f"TACTICAL_{category}",
                    "severity": "EXTREME",
                    "score": result.score,
                    "details": f"Extreme {category.lower()} targeting detected",
                    "matches": result.matches[:5]  # Top 5 matches
                })
            elif result.score >= self.HIGH_SCORE_THRESHOLD:
                red_flags.append({
                    "category": f"TACTICAL_{category}",
                    "severity": "HIGH",
                    "score": result.score,
                    "details": f"High {category.lower()} targeting detected",
                    "matches": result.matches[:3]
                })

        # Check psychological results
        for category, result in psychological_results.items():
            if result.score >= self.EXTREME_SCORE_THRESHOLD:
                red_flags.append({
                    "category": f"PSYCHOLOGICAL_{category}",
                    "severity": "EXTREME",
                    "score": result.score,
                    "details": f"Extreme {category.lower()} principle deployment",
                    "matches": result.matches[:5]
                })
            elif result.score >= self.HIGH_SCORE_THRESHOLD:
                red_flags.append({
                    "category": f"PSYCHOLOGICAL_{category}",
                    "severity": "HIGH",
                    "score": result.score,
                    "details": f"High {category.lower()} principle deployment",
                    "matches": result.matches[:3]
                })

        # Check for dangerous combinations
        emotional_score = tactical_results.get("EMOTIONAL", DetectionResult("", 0, "", [], {})).score
        scarcity_score = psychological_results.get("SCARCITY", DetectionResult("", 0, "", [], {})).score

        if emotional_score > 50 and scarcity_score > 50:
            red_flags.append({
                "category": "COMBINATION",
                "severity": "HIGH",
                "score": (emotional_score + scarcity_score) / 2,
                "details": "Emotional arc + scarcity combination detected (high-pressure pattern)",
                "matches": []
            })

        # Sort by severity and score
        severity_order = {"EXTREME": 0, "HIGH": 1, "MODERATE": 2}
        red_flags.sort(key=lambda x: (severity_order.get(x["severity"], 3), -x["score"]))

        return red_flags


# =============================================================================
# SECTION 8: MAIN UNIFIED AUDITOR
# =============================================================================

class UnifiedPersuasionAuditor:
    """
    Main auditor class that orchestrates all detection and produces comprehensive reports.

    Usage:
        auditor = UnifiedPersuasionAuditor()
        result = auditor.audit("Your content text here")
        print(json.dumps(result, indent=2))
    """

    def __init__(self):
        # Initialize all detectors
        self.tactical_detectors = {
            "PERSONAL": PersonalStimulusDetector(),
            "CONTRASTABLE": ContrastableDetector(),
            "TANGIBLE": TangibleDetector(),
            "MEMORABLE": MemorableDetector(),
            "VISUAL": VisualDetector(),
            "EMOTIONAL": EmotionalDetector(),
        }

        self.psychological_detectors = {
            "AUTHORITY": AuthorityDetector(),
            "SOCIAL_PROOF": SocialProofDetector(),
            "RECIPROCITY": ReciprocityDetector(),
            "COMMITMENT": CommitmentDetector(),
            "SCARCITY": ScarcityDetector(),
            "LIKING": LikingDetector(),
            "UNITY": UnityDetector(),
            "FRAMING": FramingDetector(),
        }

        self.linguistic_detectors = {
            "RHETORICAL_DEVICES": RhetoricalDeviceDetector(),
            "SYNTACTIC_PATTERNS": SyntacticPatternDetector(),
            "FRAMING_EFFECTS": FramingEffectDetector(),
            "PRAGMATIC_PATTERNS": PragmaticPatternDetector(),
            "DISCOURSE_MARKERS": DiscourseMarkerDetector(),
            "HEDGING_CERTAINTY": HedgingCertaintyDetector(),
            "REGISTER_FORMALITY": RegisterFormalityDetector(),
            "CONCEPTUAL_METAPHOR": ConceptualMetaphorDetector(),
        }

        self.scorer = CompositeScorer()
        self.red_flag_generator = RedFlagGenerator()

    def audit(self, text: str) -> Dict[str, Any]:
        """
        Run comprehensive audit on text content.

        Args:
            text: The content to analyze

        Returns:
            Complete audit report as dictionary
        """
        # Generate audit metadata
        audit_id = hashlib.md5(f"{text[:100]}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.sha256(text.encode()).hexdigest()

        # Run all tactical detectors
        tactical_results = {}
        for name, detector in self.tactical_detectors.items():
            tactical_results[name] = detector.detect(text)

        # Run all psychological detectors
        psychological_results = {}
        for name, detector in self.psychological_detectors.items():
            psychological_results[name] = detector.detect(text)

        # Run all linguistic detectors
        linguistic_results = {}
        for name, detector in self.linguistic_detectors.items():
            linguistic_results[name] = detector.detect(text)

        # Calculate composite scores
        composite_scores = self.scorer.calculate(
            tactical_results,
            psychological_results,
            linguistic_results
        )

        # Generate red flags
        red_flags = self.red_flag_generator.generate(
            tactical_results,
            psychological_results,
            linguistic_results
        )

        # Build final report
        report = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "content_hash": content_hash,
            "content_length": len(text),
            "content_preview": text[:200] + "..." if len(text) > 200 else text,

            "tactical_stimulus": {
                name: {
                    "score": result.score,
                    "intensity": result.intensity,
                    "matches": result.matches[:10],  # Limit matches
                    "details": result.details
                }
                for name, result in tactical_results.items()
            },

            "psychological_principles": {
                name: {
                    "score": result.score,
                    "intensity": result.intensity,
                    "matches": result.matches[:10],
                    "details": result.details
                }
                for name, result in psychological_results.items()
            },

            "linguistic_patterns": {
                name: {
                    "score": result.score,
                    "intensity": result.intensity,
                    "matches": result.matches[:10],
                    "details": result.details
                }
                for name, result in linguistic_results.items()
            },

            "composite_scores": composite_scores,
            "red_flags": red_flags,

            "summary": {
                "total_patterns_detected": sum(
                    len(r.matches) for r in tactical_results.values()
                ) + sum(
                    len(r.matches) for r in psychological_results.values()
                ) + sum(
                    len(r.matches) for r in linguistic_results.values()
                ),
                "high_severity_flags": len([f for f in red_flags if f["severity"] in ["HIGH", "EXTREME"]]),
                "classification": composite_scores["classification"],
                "overall_score": composite_scores["overall_influence_index"]
            }
        }

        return report

    def audit_pretty(self, text: str) -> str:
        """Run audit and return formatted JSON string."""
        result = self.audit(text)
        return json.dumps(result, indent=2, default=str)

    def quick_score(self, text: str) -> Dict[str, Any]:
        """Quick scoring without full details - returns just scores and classification."""
        full_result = self.audit(text)
        return {
            "overall_score": full_result["composite_scores"]["overall_influence_index"],
            "classification": full_result["composite_scores"]["classification"],
            "tactical_avg": full_result["composite_scores"]["tactical_average"],
            "psychological_avg": full_result["composite_scores"]["psychological_average"],
            "linguistic_avg": full_result["composite_scores"]["linguistic_average"],
            "red_flag_count": len(full_result["red_flags"])
        }


# =============================================================================
# SECTION 9: USAGE EXAMPLES
# =============================================================================

def demo() -> None:
    """Demonstrate the unified auditor with sample content."""

    sample_text = """
    This isn't for everyone. If you know, you know.

    While mass-produced brands chase the algorithm, we create artifacts.
    Made in a small Portuguese factory, closed since 2003. 280gsm cotton
    that fades beautifully over 18 months.

    Don't miss out - only 50 pieces remain. Others are already buying.
    This limited edition will never be made again.

    Dr. James Mitchell, Harvard researcher with 30 years experience,
    calls this "the most innovative approach in decades."

    Join thousands of discerning customers who understand quality.
    Because you deserve the best. Isn't it time you treated yourself?

    Act now before it's too late.
    """

    print("=" * 70)
    print("UNIFIED PERSUASION AUDITOR - DEMO")
    print("=" * 70)

    auditor = UnifiedPersuasionAuditor()

    # Quick score
    print("\n--- QUICK SCORE ---")
    quick = auditor.quick_score(sample_text)
    for key, value in quick.items():
        print(f"  {key}: {value}")

    # Full audit
    print("\n--- FULL AUDIT (excerpt) ---")
    result = auditor.audit(sample_text)
    print(f"\nClassification: {result['composite_scores']['classification']}")
    print(f"Overall Score: {result['composite_scores']['overall_influence_index']}")
    print(f"\nRed Flags ({len(result['red_flags'])}):")
    for flag in result['red_flags'][:5]:
        print(f"  - [{flag['severity']}] {flag['category']}: {flag['details']}")

    print("\n--- TOP TACTICAL SCORES ---")
    for name, data in result['tactical_stimulus'].items():
        print(f"  {name}: {data['score']} ({data['intensity']})")

    print("\n--- TOP PSYCHOLOGICAL SCORES ---")
    for name, data in result['psychological_principles'].items():
        print(f"  {name}: {data['score']} ({data['intensity']})")


if __name__ == "__main__":
    demo()
