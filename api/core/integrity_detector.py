"""
INTEGRITY PATTERN DETECTION SYSTEM
Detection Patterns for 10 Influence Integrity Categories

Source: Derived from behavioral influence research
Purpose: Pattern matching for content integrity analysis with mechanism documentation
Application: Content auditing for influence technique identification
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum
import json
from datetime import datetime
import hashlib


class IntensityLevel(Enum):
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


@dataclass
class DetectionResult:
    category: str
    score: int
    flagged: bool
    threshold: int
    matches: List[str]
    details: Dict[str, Any]


@dataclass
class IntegrityAuditReport:
    audit_id: str
    timestamp: str
    text_length: int
    detections: Dict[str, DetectionResult]
    composite_index: float
    intensity: IntensityLevel
    pattern_combinations: List[Dict[str, Any]]
    summary: Dict[str, Any]


# =============================================================================
# DETECTION PATTERN LIBRARY
# =============================================================================

class IntegrityPatterns:
    """Compiled regex patterns for integrity pattern detection."""

    # -------------------------------------------------------------------------
    # IV-01: SYNTHETIC AUTHORITY
    # Mechanism: Activates deference heuristics through credential signals
    # that cannot be independently verified, creating epistemic shortcuts
    # -------------------------------------------------------------------------
    UNVERIFIABLE_CREDENTIALS = re.compile(
        r'(?i)\b(leading\s+expert|world[- ]?renowned|top\s+scientist|insider\s+sources?|'
        r'exclusive\s+access|anonymous\s+expert|sources?\s+say|experts?\s+agree|'
        r'scientists?\s+confirm|highly\s+placed\s+source|confidential\s+informant)\b'
    )
    FABRICATED_INSTITUTION = re.compile(
        r'(?i)\b(institute|foundation|academy|council|board|center|centre)\s+(?:of|for)\s+'
        r'\w+\s+(studies|research|science|excellence|advancement|innovation)\b'
    )
    CREDENTIAL_STACKING = re.compile(
        r'(?i)(ph\.?d|dr\.?|professor|expert)\s+in\s+\w+.*(?:also|and|additionally)\s+'
        r'(ph\.?d|dr\.?|professor|expert)|'
        r'(\d{2,})\+?\s*years?\s+(?:of\s+)?experience|'
        r'trained\s+(?:at|by|with)\s+[A-Z][a-z]+\s+[A-Z]'
    )
    ARTIFICIAL_CONSENSUS = re.compile(
        r'(?i)\b(all|every)\s+(experts?|scientists?|doctors?|researchers?|professionals?)\s+agree|'
        r'unanimous(?:ly)?\s+(?:consensus|agreement|support)|'
        r'no\s+(?:credible|serious|real|legitimate)\s+(?:scientist|expert|researcher)\s+'
        r'(?:denies|disputes|questions|disagrees)'
    )
    NATURAL_HEDGING = re.compile(
        r'(?i)\b(I\s+think|probably|might|maybe|perhaps|seems?\s+(?:to|like)|'
        r'appears?\s+(?:to|that)|could\s+be|it\'s\s+possible|in\s+my\s+opinion)\b'
    )

    # -------------------------------------------------------------------------
    # IV-02: UNDISCLOSED COMMERCIAL INTENT
    # Mechanism: Leverages editorial trust signals while delivering commercial
    # messaging, reducing activation of advertising evaluation filters
    # -------------------------------------------------------------------------
    PROMOTIONAL_DISGUISE = re.compile(
        r'(?i)\b(I\s+discovered\s+this\s+amazing|I\s+was\s+skeptical\s+until|'
        r'this\s+changed\s+my\s+life|I\s+can\'t\s+believe\s+I\s+lived\s+without|'
        r'my\s+secret\s+weapon|game\s+changer\s+for\s+me|honest\s+review|'
        r'unbiased\s+opinion|not\s+sponsored|genuinely\s+love)\b'
    )
    NATIVE_AD = re.compile(
        r'(?i)\b(sponsored|partner(?:ed)?|presented)\s+(?:content|by|post)|'
        r'in\s+(?:partnership|collaboration)\s+with|'
        r'paid\s+(?:promotion|partnership|collaboration|content)\b'
    )
    BURIED_DISCLOSURE = re.compile(
        r'(?i).{500,}(#ad|#sponsored|#partner|#gifted|#collab)|'
        r'(?:tiny|small|barely\s+visible)\s+disclosure'
    )
    AFFILIATE_OBFUSCATION = re.compile(
        r'(?i)(bit\.ly|tinyurl|t\.co|shorturl|goo\.gl|ow\.ly)/[a-zA-Z0-9]+|'
        r'link\s+in\s+(?:bio|description|comments|profile)|'
        r'(?:use|enter)\s+(?:my|code|discount)\s+code'
    )
    JOURNALISTIC_MIMICRY = re.compile(
        r'(?i)\b(according\s+to\s+our\s+investigation|our\s+reporters?\s+found|'
        r'exclusive\s+report|breaking\s+news|investigative\s+journalism\s+reveals|'
        r'our\s+team\s+discovered|sources\s+close\s+to)\b'
    )

    # -------------------------------------------------------------------------
    # IV-03: CONCEALED IDENTITY
    # Mechanism: Activates peer-trust heuristics by presenting coordinated
    # messaging as independent organic activity
    # -------------------------------------------------------------------------
    ARTIFICIAL_GRASSROOTS = re.compile(
        r'(?i)\b(as\s+a\s+(?:regular|ordinary|everyday|normal|average)\s+'
        r'(?:person|citizen|consumer|voter|user|customer)|'
        r'I\'m\s+just\s+a\s+(?:mom|dad|parent|concerned\s+citizen|regular\s+guy)|'
        r'speaking\s+as\s+someone\s+who|from\s+(?:personal|my\s+own)\s+experience)\b'
    )
    COORDINATED_TEMPLATE = re.compile(
        r'(?i)\[(?:INSERT|NAME|PRODUCT|COMPANY)\s*\w*\]|'
        r'\{\{?\w+\}\}?|'
        r'<(?:INSERT|NAME|PRODUCT)\s*>'
    )
    NEW_ACCOUNT_SIGNALS = re.compile(
        r'(?i)\b(just\s+joined\s+but|new\s+here\s+but|'
        r'lurker\s+(?:here|finally)\s+speaking\s+up|'
        r'first\s+(?:time|post)\s+(?:here|posting)|'
        r'rarely\s+comment\s+but)\b'
    )
    DEFENSIVE_DISCLOSURE = re.compile(
        r'(?i)\b(I\'?m?\s+not\s+(?:paid|sponsored|affiliated|a\s+shill)|'
        r'(?:nobody|no\s+one)\s+(?:paid|asked)\s+me\s+to|'
        r'full\s+disclosure|'
        r'(?:love|obsessed\s+with|can\'t\s+stop\s+using)\s+[A-Z][a-z]+(?:\'s)?)\b'
    )
    INDEPENDENCE_CLAIMS = re.compile(
        r'(?i)\b(unbiased|independent|objective)\s+(?:review|opinion|analysis|take)|'
        r'no\s+(?:affiliation|relationship|connection)\s+with|'
        r'not\s+(?:sponsored|paid|compensated)'
    )

    # -------------------------------------------------------------------------
    # IV-04: INFORMATION ENVIRONMENT CONTROL
    # Mechanism: Reduces exposure to counter-narratives through preemptive
    # delegitimization, creating self-reinforcing information boundaries
    # -------------------------------------------------------------------------
    INFORMATION_GATING = re.compile(
        r'(?i)\b(don\'t\s+trust\s+(?:the\s+)?mainstream|'
        r'they\s+don\'t\s+want\s+you\s+to\s+know|'
        r'hidden\s+truth|suppressed\s+information|banned\s+content|'
        r'censored\s+(?:truth|information)|what\s+they\'re\s+hiding|'
        r'the\s+truth\s+they\'re\s+hiding)\b'
    )
    ALTERNATIVE_SOURCE_PROMOTION = re.compile(
        r'(?i)\b(only\s+(?:here|this\s+source|we)\s+(?:tell|show|reveal)|'
        r'(?:real|actual|true)\s+(?:news|information|facts)|'
        r'independent\s+(?:journalism|media|sources?)|'
        r'uncensored\s+(?:truth|news|information))\b'
    )
    OUTGROUP_SOURCE_DISMISSAL = re.compile(
        r'(?i)\b((?:mainstream|legacy|corporate)\s+(?:media|news|press)|'
        r'(?:fake|lying|corrupt)\s+(?:news|media|journalists?)|'
        r'don\'t\s+(?:believe|trust|listen\s+to)\s+(?:them|the\s+MSM|mainstream))\b'
    )
    INGROUP_REINFORCEMENT = re.compile(
        r'(?i)\b(we\s+(?:all|know|understand)\s+(?:the\s+truth|what\'s\s+happening)|'
        r'those\s+who\s+(?:see|understand|get\s+it)|'
        r'(?:sheeple|normies|NPCs|bots)|'
        r'they\'?(?:ll)?\s+never\s+(?:understand|wake\s+up|see))\b'
    )
    ENGAGEMENT_BOUNDARY = re.compile(
        r'(?i)\b(share\s+only\s+with\s+like[- ]?minded|'
        r'don\'t\s+waste\s+(?:your\s+)?time\s+on|'
        r'they\s+can\'t\s+be\s+reasoned\s+with|'
        r'beyond\s+saving|lost\s+cause|'
        r'can\'t\s+be\s+(?:helped|saved|convinced))\b'
    )

    # -------------------------------------------------------------------------
    # IV-05: PUBLIC POSITION CREATION
    # Mechanism: Leverages consistency bias by creating recorded positions,
    # increasing psychological cost of subsequent position change
    # -------------------------------------------------------------------------
    PUBLIC_COMMITMENT_PROMPT = re.compile(
        r'(?i)\b(share\s+if\s+you\s+agree|repost\s+to\s+show\s+support|'
        r'type\s+[\'"]?yes[\'"]?\s+if\s+you|comment\s+your\s+commitment|'
        r'declare\s+your\s+position|stand\s+up\s+and\s+be\s+counted|'
        r'let\s+everyone\s+know\s+where\s+you\s+stand|'
        r'raise\s+your\s+hand\s+if)\b'
    )
    SOCIAL_PROOF_COMMITMENT = re.compile(
        r'(?i)(join\s+(?:\d+[,\d]*|\w+)\s+(?:others?|people|supporters)|'
        r'be\s+one\s+of\s+the\s+(?:first|few|brave)|'
        r'add\s+your\s+(?:name|voice|signature))'
    )
    ESCALATING_COMMITMENT = re.compile(
        r'(?i)(if\s+you\s+(?:liked|shared|agreed).{0,50}(?:then|now|next)|'
        r'(?:first|start\s+by|begin\s+with).{0,50}then\s+(?:move|progress|advance)|'
        r'you\'?(?:ve)?\s+(?:already|came\s+this\s+far|invested)|'
        r'don\'t\s+(?:stop|quit|give\s+up)\s+now)'
    )
    CONSISTENCY_REFERENCE = re.compile(
        r'(?i)\b(you\s+(?:said|claimed|stated|promised|declared)|'
        r'remember\s+when\s+you|'
        r'stay\s+(?:true|consistent|committed)\s+to|'
        r'(?:real|true)\s+\w+\s+(?:don\'t|never)\s+(?:back\s+down|change))\b'
    )
    POSITION_CHANGE_LABELING = re.compile(
        r'(?i)\b(flip[- ]?flopper|changed\s+your\s+tune|'
        r'going\s+back\s+on\s+your\s+word|'
        r'showing\s+your\s+true\s+colors|'
        r'revealed\s+yourself|hypocrite)\b'
    )

    # -------------------------------------------------------------------------
    # IV-06: COGNITIVE LOAD INCREASE
    # Mechanism: Increases information density beyond analytical processing
    # capacity, shifting processing toward heuristic/automatic mode
    # -------------------------------------------------------------------------
    INFORMATION_DENSITY = re.compile(
        r'(?i)((\d{2,})\+?\s*(?:reasons?|ways?|tips?|facts?|things?|steps?).{0,20}'
        r'(?:to|you|why|that)|'
        r'(?:complete|comprehensive|ultimate|definitive)\s+'
        r'(?:guide|list|breakdown|resource))'
    )
    COMPLEXITY_STACKING = re.compile(
        r'(?i)\b(furthermore|additionally|moreover|what\'s\s+more|'
        r'on\s+top\s+of\s+that|not\s+only\s+that|plus|and\s+another\s+thing)\b'
    )
    DECISION_COMPLEXITY = re.compile(
        r'(?i)((?:choose|select|decide|pick)\s+(?:between|from|among)\s+\d+|'
        r'(?:limited\s+time|act\s+now|hurry).{0,50}(?:\d+\s+options|choose\s+from)|'
        r'(?:unsubscribe|opt[- ]?out|cancel).{0,30}(?:by|requires?|must))'
    )
    ATTENTION_INTERRUPT = re.compile(
        r'(?i)(before\s+we\s+(?:start|begin|continue|proceed)|'
        r'important.{0,30}(?:read|understand|acknowledge)\s+(?:the\s+)?following|'
        r'(?:wait|but|hold\s+on|one\s+more\s+thing|before\s+you\s+go))'
    )
    TIME_PRESSURE_COMPLEXITY = re.compile(
        r'(?i)((?:seconds?|minutes?)\s+(?:left|remaining).{0,30}\d+.{0,20}choose|'
        r'(?:recommended|suggested|popular)\s+(?:choice|option|selection)|'
        r'\d+\s+people\s+(?:are\s+)?(?:viewing|buying|choosing).{0,20}now)'
    )

    # -------------------------------------------------------------------------
    # IV-07: SUSCEPTIBILITY-SPECIFIC TARGETING
    # Mechanism: Calibrates messaging for populations with specific response
    # patterns based on developmental, psychological, or situational factors
    # -------------------------------------------------------------------------
    CHILD_DIRECTED = re.compile(
        r'(?i)\b((?:kids?|children|teens?|tweens?|young\s+people)\s+'
        r'(?:love|want|need)|'
        r'(?:unboxing|toy\s+review|surprise\s+egg|mystery\s+box)|'
        r'(?:everyone|all\s+your\s+friends|don\'t\s+be\s+left\s+out)|'
        r'(?:don\'t\s+tell|secret\s+from|without\s+your\s+parents))\b'
    )
    YOUTH_LINGUISTIC_MARKERS = re.compile(
        r'(?i)\b(no\s+cap|bussin|slay|based|fr\s+fr|low[- ]?key|'
        r'hits\s+different|its\s+giving|rent\s+free|'
        r'understood\s+the\s+assignment)\b'
    )
    MINOR_SPECIFIC_PATTERNS = re.compile(
        r'(?i)((?:under|below)\s+(?:13|18)|age\s+\d+|parental\s+consent|'
        r'(?:loot\s+box|gacha|random\s+reward|spin\s+to\s+win)|'
        r'your\s+friends\s+(?:have|already|all)|'
        r'don\'t\s+be\s+the\s+only)'
    )
    HABITUAL_USE_PATTERNS = re.compile(
        r'(?i)\b(can\'t\s+stop|one\s+more|just\s+five\s+(?:more\s+)?minutes|'
        r'(?:streak|daily\s+bonus|check\s+in|log\s+in\s+reward)|'
        r'(?:you\'ll\s+lose|expire|miss\s+out|gone\s+forever)|'
        r'(?:random|surprise|mystery|chance\s+to\s+win))\b'
    )
    DISTRESS_STATE_TARGETING = re.compile(
        r'(?i)(feeling\s+(?:down|sad|anxious|depressed|lonely|hopeless)|'
        r'(?:struggling|suffering|in\s+pain|desperate)|'
        r'(?:cure|fix|heal|solve)\s+your\s+'
        r'(?:depression|anxiety|loneliness|pain)|'
        r'(?:no\s+one\s+(?:understands|cares)|only\s+(?:we|I)\s+(?:get|understand)\s+it))'
    )
    SELF_EVALUATION_TARGETING = re.compile(
        r'(?i)(you\'?(?:re)?\s+(?:not\s+good\s+enough|worthless|a\s+failure)|'
        r'(?:everyone|others?)\s+(?:is|are)\s+better|'
        r'you\'re\s+falling\s+behind|'
        r'you\'ll\s+be\s+\w+\s+when|once\s+you|after\s+you\s+(?:buy|get))'
    )

    # -------------------------------------------------------------------------
    # IV-08: IDENTITY-POSITION BINDING
    # Mechanism: Creates cognitive linkage between beliefs and self-concept,
    # making position change equivalent to identity discontinuity
    # -------------------------------------------------------------------------
    IDENTITY_BELIEF_FUSION = re.compile(
        r'(?i)\b((?:real|true|authentic|genuine)\s+'
        r'(?:conservative|liberal|christian|american|patriot|believer)s?|'
        r'if\s+you\'?(?:re)?\s+(?:really|truly|actually)\s+a|'
        r'(?:real|true)\s+\w+\s+(?:believe|support|oppose|know)|'
        r'this\s+is\s+who\s+we\s+are|'
        r'it\'s\s+(?:in\s+our|your)\s+(?:DNA|blood|nature))\b'
    )
    BELIEF_VIRTUE_ASSOCIATION = re.compile(
        r'(?i)((?:good|decent|moral|smart|intelligent)\s+people\s+'
        r'(?:believe|support|know|understand)|'
        r'only\s+(?:fools?|idiots?|sheep|morons?)\s+'
        r'(?:believe|think|support|fall\s+for))'
    )
    POSITION_CHANGE_COST = re.compile(
        r'(?i)(admitting\s+(?:you\s+were|being)\s+wrong|'
        r'(?:embarrassing|humiliating)\s+to\s+(?:admit|change|update)|'
        r'what\s+would\s+(?:they|everyone|people)\s+(?:think|say)|'
        r'(?:laughed\s+at|mocked|ridiculed)|'
        r'you\'d\s+have\s+to\s+admit)'
    )
    REVERSAL_IMPOSSIBILITY = re.compile(
        r'(?i)(no\s+going\s+back|point\s+of\s+no\s+return|'
        r'bridge.{0,20}(?:burn|cross)|'
        r'(?:too\s+late|past\s+the\s+point|can\'t\s+undo)|'
        r'once\s+a\s+\w+,?\s+always\s+a|'
        r'you\'?(?:ve)?\s+(?:shown|proven|revealed)\s+(?:who|what)\s+you)'
    )
    EXIT_COST_AMPLIFICATION = re.compile(
        r'(?i)((?:lose|sacrifice)\s+'
        r'(?:friends|family|community|respect|everything)|'
        r'(?:abandoned|rejected|outcast|exile)|'
        r'(?:wasted|lost)\s+(?:years|time|your\s+life|everything)|'
        r'(?:all|everything)\s+you\'?(?:ve)?\s+(?:built|invested|believed))'
    )

    # -------------------------------------------------------------------------
    # IV-09: PROGRESSIVE INTENSITY ESCALATION
    # Mechanism: Graduated exposure pipeline that increases position intensity
    # through incremental steps, outgroup distancing, and binary framing
    # -------------------------------------------------------------------------
    ESCALATION_SIGNALS = re.compile(
        r'(?i)\b(red[- ]?pill(?:ed)?|wake\s+up|open\s+your\s+eyes|'
        r'see\s+the\s+(?:real\s+)?truth|'
        r'(?:rabbit\s+hole|goes\s+deeper|just\s+the\s+beginning)|'
        r'(?:that\'s\s+nothing|wait\s+until\s+you|you\s+haven\'t\s+seen)|'
        r'(?:level\s+\d+|next\s+level|deeper\s+truth))\b'
    )
    RELATIONSHIP_SEVERANCE = re.compile(
        r'(?i)(cut\s+(?:ties|them\s+off)|distance\s+yourself|'
        r'they\'re\s+not\s+worth|'
        r'(?:toxic\s+people|negative\s+influences|holding\s+you\s+back)|'
        r'once\s+you\s+know.{0,30}(?:can\'t\s+unsee|no\s+going\s+back))'
    )
    INTENSITY_AMPLIFICATION = re.compile(
        r'(?i)\b((?:absolutely\s+)?(?:outrageous|disgusting|unforgivable|'
        r'inexcusable|unacceptable)|'
        r'how\s+dare|can\s+you\s+believe|this\s+is\s+(?:insane|crazy)|'
        r'they\s+(?:want|\'re\s+trying|agenda)|'
        r'(?:destroy|attack|eliminate|silence)\s+(?:us|you|our))\b'
    )
    DEHUMANIZATION_MARKERS = re.compile(
        r'(?i)\b((?:vermin|plague|disease|cancer|infection|parasites?)|'
        r'(?:exterminate|eradicate|eliminate|purge|cleanse)|'
        r'(?:survival|existence|extinction|annihilation)|'
        r'(?:war|battle|fight)\s+(?:for|against)\s+(?:our|survival|existence))\b'
    )
    BINARY_FRAMING = re.compile(
        r'(?i)\b((?:with\s+us|against\s+us|pick\s+a\s+side)|'
        r'good\s+vs\.?\s+evil|right\s+vs\.?\s+wrong|'
        r'no\s+(?:middle\s+ground|neutrality|fence[- ]?sitting))\b'
    )
    THREAT_NARRATIVE = re.compile(
        r'(?i)(they\'?(?:re)?\s+(?:coming|after|targeting)\s+'
        r'(?:for\s+)?(?:us|you|people\s+like)|'
        r'(?:under\s+attack|being\s+silenced|being\s+oppressed)|'
        r'(?:genocide|persecution|extermination)\s+(?:of|against))'
    )

    # -------------------------------------------------------------------------
    # IV-10: EMOTIONAL STATE CYCLING
    # Mechanism: Alternates between contrasting emotional states to create
    # intermittent reinforcement patterns and reduce analytical processing
    # -------------------------------------------------------------------------
    FEAR_RELIEF_SEQUENCE = re.compile(
        r'(?i)((?:worried|scared|afraid|terrified).{20,150}'
        r'(?:relief|safe|secure|don\'t\s+worry|but\s+there\'s\s+hope)|'
        r'(?:bad\s+news).{20,150}(?:good\s+news|but\s+here\'s|however))'
    )
    HOPE_DISAPPOINTMENT_SEQUENCE = re.compile(
        r'(?i)((?:unfortunately|sadly|bad\s+news).{20,150}'
        r'(?:but|however|good\s+news|silver\s+lining))'
    )
    INTERMITTENT_REINFORCEMENT = re.compile(
        r'(?i)((?:sometimes|occasionally|when\s+you\s+deserve)|'
        r'(?:ignore|silence|distance).{20,150}(?:attention|reward|recognize))'
    )
    EXCLUSIVE_UNDERSTANDING = re.compile(
        r'(?i)(only\s+(?:I|we)\s+(?:understand|get|know)\s+you|'
        r'(?:no\s+one\s+else|only\s+here|only\s+with\s+us)|'
        r'(?:special\s+bond|unique\s+connection|understand\s+each\s+other)|'
        r'(?:meant\s+to\s+be|destiny|fate))'
    )
    SUPPORT_NETWORK_DISPLACEMENT = re.compile(
        r'(?i)(they\s+don\'t\s+(?:understand|get\s+it|care)|'
        r'they\'ll\s+never\s+(?:understand|get\s+it)|'
        r'only\s+(?:we|I|here)\s+really\s+(?:care|understand|support)|'
        r'(?:need\s+(?:me|us)|can\'t\s+do\s+this\s+without|depend\s+on))'
    )
    ANALYTICAL_BYPASS = re.compile(
        r'(?i)((?:breaking|urgent|shocking|incredible|unbelievable).{0,50}'
        r'(?:breaking|urgent|shocking)|'
        r'(?:so\s+much|overwhelming|can\'t\s+process|hard\s+to\s+believe)|'
        r'(?:don\'t\s+think|just\s+feel|trust\s+your\s+gut|'
        r'go\s+with\s+your\s+heart))'
    )
    VIGILANCE_REDUCTION = re.compile(
        r'(?i)((?:relax|calm|don\'t\s+worry|everything\'s\s+fine)|'
        r'(?:no\s+time\s+to\s+(?:think|analyze)|just\s+do\s+it|act\s+now))'
    )


# =============================================================================
# DETECTOR CLASSES
# =============================================================================

class SyntheticAuthorityDetector:
    """
    IV-01: Synthetic Authority Detection

    Mechanism: Activates deference heuristics through credential signals
    that cannot be independently verified. Artificial consensus patterns
    create perceived epistemic authority without verifiable basis.

    Detection Markers:
    - Unverifiable credential claims (15 pts)
    - Fabricated institution patterns (25 pts)
    - Credential stacking behavior (20 pts)
    - Artificial consensus language (30 pts)
    - Absence of natural hedging (10 pts)
    """
    THRESHOLD = 40
    MAX_SCORE = 200

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        unverifiable = IntegrityPatterns.UNVERIFIABLE_CREDENTIALS.findall(text)
        unverifiable_score = len(unverifiable) * 15
        if unverifiable:
            matches.extend(unverifiable)
            details['unverifiable_credentials'] = unverifiable

        fabricated = IntegrityPatterns.FABRICATED_INSTITUTION.findall(text)
        fabricated_score = len(fabricated) * 25
        if fabricated:
            matches.extend(fabricated)
            details['fabricated_institutions'] = fabricated

        stacking = IntegrityPatterns.CREDENTIAL_STACKING.findall(text)
        stacking_score = len(stacking) * 20
        if stacking:
            matches.extend([s[0] if isinstance(s, tuple) else s for s in stacking])
            details['credential_stacking'] = len(stacking)

        consensus = IntegrityPatterns.ARTIFICIAL_CONSENSUS.findall(text)
        consensus_score = len(consensus) * 30
        if consensus:
            matches.extend(consensus)
            details['artificial_consensus'] = consensus

        hedging = IntegrityPatterns.NATURAL_HEDGING.findall(text)
        hedging_penalty = 10 if not hedging and len(text) > 200 else 0
        details['natural_hedging_present'] = len(hedging) > 0

        raw_score = unverifiable_score + fabricated_score + stacking_score + consensus_score + hedging_penalty
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='SYNTHETIC_AUTHORITY',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class UndisclosedCommercialDetector:
    """
    IV-02: Undisclosed Commercial Intent Detection

    Mechanism: Leverages editorial trust signals while delivering commercial
    messaging. Native advertising formats reduce activation of standard
    advertising evaluation filters.

    Detection Markers:
    - Promotional language disguise (20 pts)
    - Native ad patterns (15 pts)
    - Buried disclosure indicators (35 pts)
    - Affiliate link obfuscation (25 pts)
    - Journalistic mimicry (30 pts)
    """
    THRESHOLD = 35
    MAX_SCORE = 175

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        promotional = IntegrityPatterns.PROMOTIONAL_DISGUISE.findall(text)
        promotional_score = len(promotional) * 20
        if promotional:
            matches.extend(promotional)
            details['promotional_language'] = promotional

        native = IntegrityPatterns.NATIVE_AD.findall(text)
        native_score = len(native) * 15
        if native:
            matches.extend(native)
            details['native_ad_markers'] = native

        buried = IntegrityPatterns.BURIED_DISCLOSURE.findall(text)
        buried_score = len(buried) * 35
        if buried:
            matches.extend(buried)
            details['buried_disclosure'] = True

        affiliate = IntegrityPatterns.AFFILIATE_OBFUSCATION.findall(text)
        affiliate_score = len(affiliate) * 25
        if affiliate:
            matches.extend(affiliate)
            details['affiliate_links'] = affiliate

        journalistic = IntegrityPatterns.JOURNALISTIC_MIMICRY.findall(text)
        journalism_score = len(journalistic) * 30
        if journalistic:
            matches.extend(journalistic)
            details['journalistic_mimicry'] = journalistic

        raw_score = promotional_score + native_score + buried_score + affiliate_score + journalism_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='UNDISCLOSED_COMMERCIAL',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class ConcealedIdentityDetector:
    """
    IV-03: Concealed Identity Detection

    Mechanism: Activates peer-trust heuristics by presenting coordinated
    messaging as independent organic activity. Template markers and
    defensive disclosures indicate coordinated campaign structure.

    Detection Markers:
    - Artificial grassroots claims (25 pts)
    - Template/placeholder markers (35 pts)
    - New account behavioral signals (30 pts)
    - Defensive disclosure patterns (20 pts)
    - Independence claims (15 pts)
    """
    THRESHOLD = 30
    MAX_SCORE = 175

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        grassroots = IntegrityPatterns.ARTIFICIAL_GRASSROOTS.findall(text)
        grassroots_score = len(grassroots) * 25
        if grassroots:
            matches.extend(grassroots)
            details['grassroots_claims'] = grassroots

        templates = IntegrityPatterns.COORDINATED_TEMPLATE.findall(text)
        template_score = len(templates) * 35
        if templates:
            matches.extend(templates)
            details['template_markers'] = templates

        new_account = IntegrityPatterns.NEW_ACCOUNT_SIGNALS.findall(text)
        new_score = len(new_account) * 30
        if new_account:
            matches.extend(new_account)
            details['new_account_signals'] = new_account

        defensive = IntegrityPatterns.DEFENSIVE_DISCLOSURE.findall(text)
        defensive_score = len(defensive) * 20
        if defensive:
            matches.extend(defensive)
            details['defensive_disclosure'] = defensive

        independence = IntegrityPatterns.INDEPENDENCE_CLAIMS.findall(text)
        independence_score = len(independence) * 15
        if independence:
            matches.extend(independence)
            details['independence_claims'] = independence

        raw_score = grassroots_score + template_score + new_score + defensive_score + independence_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='CONCEALED_IDENTITY',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class InformationEnvironmentDetector:
    """
    IV-04: Information Environment Control Detection

    Mechanism: Reduces exposure to counter-narratives through preemptive
    source delegitimization. Ingroup reinforcement and engagement boundaries
    create self-reinforcing information environments.

    Detection Markers:
    - Information gating language (20 pts)
    - Alternative source promotion (15 pts)
    - Outgroup source dismissal (25 pts)
    - Ingroup reinforcement (20 pts)
    - Engagement boundary tactics (25 pts)
    """
    THRESHOLD = 35
    MAX_SCORE = 165

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        gating = IntegrityPatterns.INFORMATION_GATING.findall(text)
        gating_score = len(gating) * 20
        if gating:
            matches.extend(gating)
            details['information_gating'] = gating

        alt_source = IntegrityPatterns.ALTERNATIVE_SOURCE_PROMOTION.findall(text)
        alt_score = len(alt_source) * 15
        if alt_source:
            matches.extend(alt_source)
            details['alternative_sources'] = alt_source

        outgroup = IntegrityPatterns.OUTGROUP_SOURCE_DISMISSAL.findall(text)
        outgroup_score = len(outgroup) * 25
        if outgroup:
            matches.extend(outgroup)
            details['outgroup_dismissal'] = outgroup

        ingroup = IntegrityPatterns.INGROUP_REINFORCEMENT.findall(text)
        ingroup_score = len(ingroup) * 20
        if ingroup:
            matches.extend(ingroup)
            details['ingroup_reinforcement'] = ingroup

        boundary = IntegrityPatterns.ENGAGEMENT_BOUNDARY.findall(text)
        boundary_score = len(boundary) * 25
        if boundary:
            matches.extend(boundary)
            details['engagement_boundary'] = boundary

        raw_score = gating_score + alt_score + outgroup_score + ingroup_score + boundary_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='INFORMATION_ENVIRONMENT',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class PublicPositionDetector:
    """
    IV-05: Public Position Creation Detection

    Mechanism: Leverages consistency bias by creating recorded positions.
    Escalating commitment sequences and position change labeling increase
    psychological cost of subsequent position modification.

    Detection Markers:
    - Public commitment prompts (25 pts)
    - Social proof commitment (15 pts)
    - Escalating commitment sequences (30 pts)
    - Consistency reference language (20 pts)
    - Position change labeling (35 pts)
    """
    THRESHOLD = 40
    MAX_SCORE = 175

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        public = IntegrityPatterns.PUBLIC_COMMITMENT_PROMPT.findall(text)
        public_score = len(public) * 25
        if public:
            matches.extend(public)
            details['public_commitment'] = public

        social = IntegrityPatterns.SOCIAL_PROOF_COMMITMENT.findall(text)
        social_score = len(social) * 15
        if social:
            matches.extend(social)
            details['social_proof_commitment'] = social

        escalating = IntegrityPatterns.ESCALATING_COMMITMENT.findall(text)
        escalating_score = len(escalating) * 30
        if escalating:
            matches.extend(escalating)
            details['escalating_commitment'] = escalating

        consistency = IntegrityPatterns.CONSISTENCY_REFERENCE.findall(text)
        consistency_score = len(consistency) * 20
        if consistency:
            matches.extend(consistency)
            details['consistency_reference'] = consistency

        labeling = IntegrityPatterns.POSITION_CHANGE_LABELING.findall(text)
        labeling_score = len(labeling) * 35
        if labeling:
            matches.extend(labeling)
            details['position_change_labeling'] = labeling

        raw_score = public_score + social_score + escalating_score + consistency_score + labeling_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='PUBLIC_POSITION',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class CognitiveLoadDetector:
    """
    IV-06: Cognitive Load Increase Detection

    Mechanism: Increases information density beyond analytical processing
    capacity. Time pressure combined with complexity shifts processing
    toward heuristic/automatic mode.

    Detection Markers:
    - Information density patterns (20 pts)
    - Complexity stacking language (15 pts)
    - Decision complexity tactics (25 pts)
    - Attention interrupt patterns (20 pts)
    - Time pressure + complexity (30 pts)
    - High complexity density bonus (15 pts)
    """
    THRESHOLD = 45
    MAX_SCORE = 180

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        density = IntegrityPatterns.INFORMATION_DENSITY.findall(text)
        density_score = len(density) * 20
        if density:
            matches.extend([d[0] if isinstance(d, tuple) else d for d in density])
            details['information_density'] = len(density)

        stacking = IntegrityPatterns.COMPLEXITY_STACKING.findall(text)
        stacking_score = len(stacking) * 15
        if stacking:
            matches.extend(stacking)
            details['complexity_markers'] = stacking

        decision = IntegrityPatterns.DECISION_COMPLEXITY.findall(text)
        decision_score = len(decision) * 25
        if decision:
            matches.extend(decision)
            details['decision_complexity'] = decision

        interrupt = IntegrityPatterns.ATTENTION_INTERRUPT.findall(text)
        interrupt_score = len(interrupt) * 20
        if interrupt:
            matches.extend(interrupt)
            details['attention_interrupt'] = interrupt

        time_pressure = IntegrityPatterns.TIME_PRESSURE_COMPLEXITY.findall(text)
        time_score = len(time_pressure) * 30
        if time_pressure:
            matches.extend(time_pressure)
            details['time_pressure'] = time_pressure

        word_count = len(text.split())
        sentence_count = max(len(re.split(r'[.!?]+', text)), 1)
        avg_sentence_length = word_count / sentence_count
        complexity_bonus = 15 if avg_sentence_length > 25 and word_count > 500 else 0

        raw_score = density_score + stacking_score + decision_score + interrupt_score + time_score + complexity_bonus
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='COGNITIVE_LOAD',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class SusceptibilityTargetingDetector:
    """
    IV-07: Susceptibility-Specific Targeting Detection

    Mechanism: Calibrates messaging for populations with specific response
    patterns. Developmental factors (children), psychological states
    (distress), and behavioral patterns (habitual use) affect processing.

    Detection Markers:
    - Child-directed signals (35 pts)
    - Youth linguistic markers (15 pts)
    - Minor-specific patterns (40 pts)
    - Habitual use targeting (30 pts)
    - Distress state targeting (35 pts)
    - Self-evaluation targeting (30 pts)
    """
    THRESHOLD = 25
    MAX_SCORE = 200

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        child = IntegrityPatterns.CHILD_DIRECTED.findall(text)
        child_score = len(child) * 35
        if child:
            matches.extend(child)
            details['child_directed'] = child

        youth = IntegrityPatterns.YOUTH_LINGUISTIC_MARKERS.findall(text)
        youth_score = len(youth) * 15
        if youth:
            matches.extend(youth)
            details['youth_markers'] = youth

        minor = IntegrityPatterns.MINOR_SPECIFIC_PATTERNS.findall(text)
        minor_score = len(minor) * 40
        if minor:
            matches.extend(minor)
            details['minor_patterns'] = minor

        habitual = IntegrityPatterns.HABITUAL_USE_PATTERNS.findall(text)
        habitual_score = len(habitual) * 30
        if habitual:
            matches.extend(habitual)
            details['habitual_use'] = habitual

        distress = IntegrityPatterns.DISTRESS_STATE_TARGETING.findall(text)
        distress_score = len(distress) * 35
        if distress:
            matches.extend(distress)
            details['distress_targeting'] = distress

        self_eval = IntegrityPatterns.SELF_EVALUATION_TARGETING.findall(text)
        self_eval_score = len(self_eval) * 30
        if self_eval:
            matches.extend(self_eval)
            details['self_evaluation_targeting'] = self_eval

        raw_score = child_score + youth_score + minor_score + habitual_score + distress_score + self_eval_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='SUSCEPTIBILITY_TARGETING',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class IdentityPositionDetector:
    """
    IV-08: Identity-Position Binding Detection

    Mechanism: Creates cognitive linkage between beliefs and self-concept.
    Position change cost amplification and reversal impossibility framing
    make position modification equivalent to identity discontinuity.

    Detection Markers:
    - Identity-belief fusion language (25 pts)
    - Belief-virtue association (20 pts)
    - Position change cost (30 pts)
    - Reversal impossibility framing (35 pts)
    - Exit cost amplification (25 pts)
    """
    THRESHOLD = 35
    MAX_SCORE = 185

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        fusion = IntegrityPatterns.IDENTITY_BELIEF_FUSION.findall(text)
        fusion_score = len(fusion) * 25
        if fusion:
            matches.extend(fusion)
            details['identity_fusion'] = fusion

        virtue = IntegrityPatterns.BELIEF_VIRTUE_ASSOCIATION.findall(text)
        virtue_score = len(virtue) * 20
        if virtue:
            matches.extend(virtue)
            details['belief_virtue'] = virtue

        cost = IntegrityPatterns.POSITION_CHANGE_COST.findall(text)
        cost_score = len(cost) * 30
        if cost:
            matches.extend(cost)
            details['position_change_cost'] = cost

        reversal = IntegrityPatterns.REVERSAL_IMPOSSIBILITY.findall(text)
        reversal_score = len(reversal) * 35
        if reversal:
            matches.extend(reversal)
            details['reversal_impossibility'] = reversal

        exit_cost = IntegrityPatterns.EXIT_COST_AMPLIFICATION.findall(text)
        exit_score = len(exit_cost) * 25
        if exit_cost:
            matches.extend(exit_cost)
            details['exit_costs'] = exit_cost

        raw_score = fusion_score + virtue_score + cost_score + reversal_score + exit_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='IDENTITY_POSITION',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class IntensityEscalationDetector:
    """
    IV-09: Progressive Intensity Escalation Detection

    Mechanism: Graduated exposure pipeline that increases position intensity
    through incremental steps. Relationship severance, binary framing, and
    dehumanization markers indicate escalation trajectory.

    Detection Markers:
    - Escalation signals (25 pts)
    - Relationship severance tactics (30 pts)
    - Intensity amplification language (20 pts)
    - Dehumanization markers (40 pts)
    - Binary framing (20 pts)
    - Threat narrative patterns (25 pts)
    """
    THRESHOLD = 30
    MAX_SCORE = 220

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        escalation = IntegrityPatterns.ESCALATION_SIGNALS.findall(text)
        escalation_score = len(escalation) * 25
        if escalation:
            matches.extend(escalation)
            details['escalation_signals'] = escalation

        severance = IntegrityPatterns.RELATIONSHIP_SEVERANCE.findall(text)
        severance_score = len(severance) * 30
        if severance:
            matches.extend(severance)
            details['relationship_severance'] = severance

        amplification = IntegrityPatterns.INTENSITY_AMPLIFICATION.findall(text)
        amplification_score = len(amplification) * 20
        if amplification:
            matches.extend(amplification)
            details['intensity_amplification'] = amplification

        dehumanization = IntegrityPatterns.DEHUMANIZATION_MARKERS.findall(text)
        dehumanization_score = len(dehumanization) * 40
        if dehumanization:
            matches.extend(dehumanization)
            details['dehumanization_markers'] = dehumanization

        binary = IntegrityPatterns.BINARY_FRAMING.findall(text)
        binary_score = len(binary) * 20
        if binary:
            matches.extend(binary)
            details['binary_framing'] = binary

        threat = IntegrityPatterns.THREAT_NARRATIVE.findall(text)
        threat_score = len(threat) * 25
        if threat:
            matches.extend(threat)
            details['threat_narrative'] = threat

        raw_score = escalation_score + severance_score + amplification_score + dehumanization_score + binary_score + threat_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='INTENSITY_ESCALATION',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


class EmotionalCyclingDetector:
    """
    IV-10: Emotional State Cycling Detection

    Mechanism: Alternates between contrasting emotional states to create
    intermittent reinforcement patterns. Support network displacement and
    analytical bypass reduce independent evaluation capacity.

    Detection Markers:
    - Fear-relief sequence patterns (35 pts)
    - Hope-disappointment sequences (30 pts)
    - Intermittent reinforcement (25 pts)
    - Exclusive understanding signals (30 pts)
    - Support network displacement (25 pts)
    - Analytical bypass patterns (20 pts)
    - Vigilance reduction markers (15 pts)
    """
    THRESHOLD = 35
    MAX_SCORE = 195

    def detect(self, text: str) -> DetectionResult:
        matches = []
        details = {}

        fear_relief = IntegrityPatterns.FEAR_RELIEF_SEQUENCE.findall(text)
        fear_score = len(fear_relief) * 35
        if fear_relief:
            matches.extend(fear_relief)
            details['fear_relief_cycles'] = len(fear_relief)

        hope_disappoint = IntegrityPatterns.HOPE_DISAPPOINTMENT_SEQUENCE.findall(text)
        hope_score = len(hope_disappoint) * 30
        if hope_disappoint:
            matches.extend(hope_disappoint)
            details['hope_disappointment_cycles'] = len(hope_disappoint)

        intermittent = IntegrityPatterns.INTERMITTENT_REINFORCEMENT.findall(text)
        intermittent_score = len(intermittent) * 25
        if intermittent:
            matches.extend(intermittent)
            details['intermittent_reinforcement'] = intermittent

        exclusive = IntegrityPatterns.EXCLUSIVE_UNDERSTANDING.findall(text)
        exclusive_score = len(exclusive) * 30
        if exclusive:
            matches.extend(exclusive)
            details['exclusive_understanding'] = exclusive

        displacement = IntegrityPatterns.SUPPORT_NETWORK_DISPLACEMENT.findall(text)
        displacement_score = len(displacement) * 25
        if displacement:
            matches.extend(displacement)
            details['support_displacement'] = displacement

        bypass = IntegrityPatterns.ANALYTICAL_BYPASS.findall(text)
        bypass_score = len(bypass) * 20
        if bypass:
            matches.extend(bypass)
            details['analytical_bypass'] = bypass

        vigilance = IntegrityPatterns.VIGILANCE_REDUCTION.findall(text)
        vigilance_score = len(vigilance) * 15
        if vigilance:
            matches.extend(vigilance)
            details['vigilance_reduction'] = vigilance

        raw_score = fear_score + hope_score + intermittent_score + exclusive_score + displacement_score + bypass_score + vigilance_score
        normalized_score = min(int((raw_score / self.MAX_SCORE) * 100), 100)

        return DetectionResult(
            category='EMOTIONAL_CYCLING',
            score=normalized_score,
            flagged=normalized_score > self.THRESHOLD,
            threshold=self.THRESHOLD,
            matches=list(set(matches)),
            details=details
        )


# =============================================================================
# MAIN AUDITOR CLASS
# =============================================================================

class IntegrityPatternAuditor:
    """
    Unified Integrity Pattern Detection System

    Combines 10 pattern detectors with weighted composite scoring.
    Higher weights for categories with greater intensity potential.
    """
    CATEGORY_WEIGHTS = {
        'SYNTHETIC_AUTHORITY': 1.0,
        'UNDISCLOSED_COMMERCIAL': 1.0,
        'CONCEALED_IDENTITY': 1.0,
        'INFORMATION_ENVIRONMENT': 1.1,
        'PUBLIC_POSITION': 1.1,
        'COGNITIVE_LOAD': 1.0,
        'SUSCEPTIBILITY_TARGETING': 1.5,
        'IDENTITY_POSITION': 1.2,
        'INTENSITY_ESCALATION': 1.5,
        'EMOTIONAL_CYCLING': 1.2
    }

    def __init__(self):
        self.detectors = {
            'SYNTHETIC_AUTHORITY': SyntheticAuthorityDetector(),
            'UNDISCLOSED_COMMERCIAL': UndisclosedCommercialDetector(),
            'CONCEALED_IDENTITY': ConcealedIdentityDetector(),
            'INFORMATION_ENVIRONMENT': InformationEnvironmentDetector(),
            'PUBLIC_POSITION': PublicPositionDetector(),
            'COGNITIVE_LOAD': CognitiveLoadDetector(),
            'SUSCEPTIBILITY_TARGETING': SusceptibilityTargetingDetector(),
            'IDENTITY_POSITION': IdentityPositionDetector(),
            'INTENSITY_ESCALATION': IntensityEscalationDetector(),
            'EMOTIONAL_CYCLING': EmotionalCyclingDetector()
        }

    def _generate_audit_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def _calculate_composite(self, detections: Dict[str, DetectionResult]) -> float:
        weighted_sum = sum(
            detections[cat].score * self.CATEGORY_WEIGHTS[cat]
            for cat in detections
        )
        total_weight = sum(self.CATEGORY_WEIGHTS.values())
        base_score = weighted_sum / total_weight
        flagged_count = sum(1 for d in detections.values() if d.flagged)
        multiplier = 1 + (flagged_count * 0.15)
        return min(base_score * multiplier, 100)

    def _classify_intensity(self, score: float) -> IntensityLevel:
        if score <= 20:
            return IntensityLevel.MINIMAL
        elif score <= 40:
            return IntensityLevel.LOW
        elif score <= 60:
            return IntensityLevel.MODERATE
        elif score <= 80:
            return IntensityLevel.HIGH
        else:
            return IntensityLevel.EXTREME

    def _identify_combinations(self, detections: Dict[str, DetectionResult]) -> List[Dict[str, Any]]:
        combinations = []

        if detections['SUSCEPTIBILITY_TARGETING'].score > 50:
            combinations.append({
                'type': 'HIGH_SUSCEPTIBILITY_TARGETING',
                'intensity': 'EXTREME',
                'score': detections['SUSCEPTIBILITY_TARGETING'].score,
                'matches': detections['SUSCEPTIBILITY_TARGETING'].matches[:5]
            })

        if detections['INTENSITY_ESCALATION'].score > 40:
            combinations.append({
                'type': 'HIGH_INTENSITY_ESCALATION',
                'intensity': 'EXTREME',
                'score': detections['INTENSITY_ESCALATION'].score,
                'matches': detections['INTENSITY_ESCALATION'].matches[:5]
            })

        escalation_details = detections['INTENSITY_ESCALATION'].details
        if 'dehumanization_markers' in escalation_details and escalation_details['dehumanization_markers']:
            combinations.append({
                'type': 'DEHUMANIZATION_PRESENT',
                'intensity': 'EXTREME',
                'matches': escalation_details['dehumanization_markers'][:3]
            })

        if detections['IDENTITY_POSITION'].score > 30 and detections['INFORMATION_ENVIRONMENT'].score > 30:
            combinations.append({
                'type': 'IDENTITY_PLUS_ENVIRONMENT',
                'intensity': 'HIGH',
                'combined_score': (detections['IDENTITY_POSITION'].score + detections['INFORMATION_ENVIRONMENT'].score) / 2
            })

        if (detections['INFORMATION_ENVIRONMENT'].score > 30 and
                detections['INTENSITY_ESCALATION'].score > 30 and
                detections['IDENTITY_POSITION'].score > 30):
            combinations.append({
                'type': 'ESCALATION_PIPELINE',
                'intensity': 'EXTREME',
                'combined_score': (detections['INFORMATION_ENVIRONMENT'].score +
                                   detections['INTENSITY_ESCALATION'].score +
                                   detections['IDENTITY_POSITION'].score) / 3
            })

        if (detections['SUSCEPTIBILITY_TARGETING'].score > 25 and
                detections['EMOTIONAL_CYCLING'].score > 30 and
                detections['COGNITIVE_LOAD'].score > 30):
            combinations.append({
                'type': 'COMPOUND_TARGETING',
                'intensity': 'EXTREME',
                'combined_score': (detections['SUSCEPTIBILITY_TARGETING'].score +
                                   detections['EMOTIONAL_CYCLING'].score +
                                   detections['COGNITIVE_LOAD'].score) / 3
            })

        if (detections['SYNTHETIC_AUTHORITY'].score > 30 and
                detections['UNDISCLOSED_COMMERCIAL'].score > 30 and
                detections['CONCEALED_IDENTITY'].score > 30):
            combinations.append({
                'type': 'LAYERED_CONCEALMENT',
                'intensity': 'HIGH',
                'combined_score': (detections['SYNTHETIC_AUTHORITY'].score +
                                   detections['UNDISCLOSED_COMMERCIAL'].score +
                                   detections['CONCEALED_IDENTITY'].score) / 3
            })

        return combinations

    def audit(self, text: str) -> IntegrityAuditReport:
        detections = {}
        for category, detector in self.detectors.items():
            detections[category] = detector.detect(text)

        composite = self._calculate_composite(detections)
        intensity = self._classify_intensity(composite)
        combinations = self._identify_combinations(detections)

        flagged_categories = [cat for cat, d in detections.items() if d.flagged]
        total_matches = sum(len(d.matches) for d in detections.values())

        summary = {
            'categories_flagged': len(flagged_categories),
            'categories_flagged_list': flagged_categories,
            'total_matches': total_matches,
            'combination_count': len(combinations),
            'highest_score_category': max(detections, key=lambda k: detections[k].score),
            'highest_score': max(d.score for d in detections.values())
        }

        return IntegrityAuditReport(
            audit_id=self._generate_audit_id(text),
            timestamp=datetime.now().isoformat(),
            text_length=len(text),
            detections=detections,
            composite_index=round(composite, 1),
            intensity=intensity,
            pattern_combinations=combinations,
            summary=summary
        )

    def quick_score(self, text: str) -> Dict[str, Any]:
        detections = {}
        for category, detector in self.detectors.items():
            result = detector.detect(text)
            detections[category] = {'score': result.score, 'flagged': result.flagged}

        composite = self._calculate_composite({
            cat: type('obj', (object,), {'score': v['score'], 'flagged': v['flagged']})()
            for cat, v in detections.items()
        })

        return {
            'detections': detections,
            'composite_index': round(composite, 1),
            'intensity': self._classify_intensity(composite).value
        }

    def to_json(self, report: IntegrityAuditReport) -> str:
        def serialize(obj):
            if isinstance(obj, DetectionResult):
                return {
                    'category': obj.category,
                    'score': obj.score,
                    'flagged': obj.flagged,
                    'threshold': obj.threshold,
                    'matches': obj.matches,
                    'details': obj.details
                }
            elif isinstance(obj, IntensityLevel):
                return obj.value
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(v) for v in obj]
            return obj

        report_dict = {
            'audit_id': report.audit_id,
            'timestamp': report.timestamp,
            'text_length': report.text_length,
            'detections': serialize(report.detections),
            'composite_index': report.composite_index,
            'intensity': report.intensity.value,
            'pattern_combinations': report.pattern_combinations,
            'summary': report.summary
        }
        return json.dumps(report_dict, indent=2)


def audit_integrity(text: str) -> IntegrityAuditReport:
    auditor = IntegrityPatternAuditor()
    return auditor.audit(text)


if __name__ == '__main__':
    test_text = """
    WAKE UP! The mainstream media doesn't want you to know the truth about what's
    really happening. As a regular person who just discovered this, I can't believe
    I was so blind before.

    Dr. John Smith, PhD in Truth Studies from the Institute of Independent Research
    and a leading expert with 30+ years of experience, reveals that ALL scientists
    agree on this - no credible researcher disputes these facts.

    Once you see the truth, you can't unsee it. Share if you agree! Your friends
    and family won't understand - they're too far gone. But we know the real story.

    This is who we are. Real patriots never back down. Admitting you were wrong
    would be embarrassing, right? Don't worry, you're in the right place now.
    Only we truly understand you.

    Act now - this information is being suppressed and won't be available forever!
    100+ reasons why they're trying to silence us. Furthermore, additionally,
    moreover, on top of all that...

    Warning: Bad news ahead... but here's the good news! Feeling anxious? Don't worry.
    Scared? Relief is coming. Trust your gut, don't overthink it.
    """

    auditor = IntegrityPatternAuditor()
    report = auditor.audit(test_text)

    print("=" * 60)
    print("INTEGRITY PATTERN AUDIT REPORT")
    print("=" * 60)
    print(f"Audit ID: {report.audit_id}")
    print(f"Composite: {report.composite_index} | Intensity: {report.intensity.value}")
    print("-" * 60)
    for cat, result in sorted(report.detections.items(), key=lambda x: x[1].score, reverse=True):
        flag = " [FLAGGED]" if result.flagged else ""
        print(f"  {cat}: {result.score}/100{flag}")
    print("-" * 60)
    if report.pattern_combinations:
        print("PATTERN COMBINATIONS:")
        for combo in report.pattern_combinations:
            print(f"  [{combo['intensity']}] {combo['type']}")
    print(f"\nSummary: {report.summary['categories_flagged']} categories flagged, "
          f"{report.summary['total_matches']} matches, {report.summary['combination_count']} combinations")
