"""
Persuasion-Max Core — Limbic Decision Engineering Engine

Neuroanatomical circuit-level persuasion analysis.
Scores stimuli on 7 cognitive appraisal dimensions,
predicts competing circuit activations (approach/avoidance/deliberation),
and outputs behavioral outcome probabilities.

Layers:
    1. Appraisal Extraction — 7 dimensions per Smith & Ellsworth / Scherer
    2. Circuit Prediction — approach/avoidance/deliberation competition
    3. Somatic Marker Store — Damasio's hypothesis as persistent computation
    4. Limbic Cascade — 6-stage pipeline orchestrator
    5. Reframing Engine — mechanical tradeoff surface (no editorial)
    6. Unified Auditor — technique detection (existing)
    7. Unified Generator — technique generation (existing)
    8. Integrity Detector — integrity pattern detection (existing)
"""

from core.appraisal_extractor import AppraisalExtractor, AppraisalScores
from core.circuit_predictor import CircuitPredictor, CircuitActivations, BehavioralPrediction
from core.somatic_marker_store import SomaticMarkerStore
from core.limbic_cascade import LimbicCascade, CascadeResult
from core.reframing_engine import ReframingEngine
from core.ux_patterns import UXPatternLibrary
from core.unified_auditor import UnifiedPersuasionAuditor
from core.unified_generator import UnifiedInfluenceGenerator
from core.integrity_detector import IntegrityPatterns
from core.recipient_profile import RecipientProfile
from core.recipient_modulator import RecipientModulator
from core.preset_personas import PRESET_PERSONAS, get_persona, list_personas
from core.text_profiler import TextProfiler
from core.domain_registry import DomainWeightRegistry
from core.domain_predictor import DomainPredictor, DomainPrediction
