"""
UNIFIED INFLUENCE GENERATOR
===========================
A research tool for generating content using documented influence techniques.
Companion module to UNIFIED_AUDITOR.py - imports patterns for consistency.

This tool is designed for academic research purposes, enabling researchers to:
- Generate controlled examples of influence techniques for study
- Test detection systems with known technique combinations
- Study the interaction effects between different techniques
- Develop countermeasures and educational materials

Usage:
    generator = UnifiedInfluenceGenerator()
    config = GenerationConfig(techniques=["SCARCITY", "AUTHORITY"], intensity="MODERATE")
    result = generator.enhance("Your text here", config)
    print(result.enhanced_text)

Author: Persuasion Max Project
Version: 1.0.0
"""

import re
import os
import json
import random
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from datetime import datetime

# Import from companion module
try:
    from core.unified_auditor import Patterns, UnifiedPersuasionAuditor, DetectionResult
except ImportError:
    from unified_auditor import Patterns, UnifiedPersuasionAuditor, DetectionResult


# =============================================================================
# SECTION 1: CONFIGURATION CONSTANTS
# =============================================================================

INTENSITY_LEVELS = ["LOW", "MODERATE", "HIGH", "EXTREME"]

TECHNIQUE_CATEGORIES = {
    "tactical_stimulus": [
        "PERSONAL", "CONTRASTABLE", "TANGIBLE",
        "MEMORABLE", "VISUAL", "EMOTIONAL"
    ],
    "psychological": [
        "AUTHORITY", "SOCIAL_PROOF", "RECIPROCITY", "COMMITMENT",
        "SCARCITY", "LIKING", "UNITY", "FRAMING"
    ],
    "linguistic": [
        "RHETORICAL_DEVICES", "SYNTACTIC_PATTERNS", "FRAMING_EFFECTS",
        "PRAGMATIC_PATTERNS", "DISCOURSE_MARKERS", "HEDGING_CERTAINTY",
        "REGISTER_FORMALITY", "CONCEPTUAL_METAPHOR"
    ]
}

ALL_TECHNIQUES = (
    TECHNIQUE_CATEGORIES["tactical_stimulus"] +
    TECHNIQUE_CATEGORIES["psychological"] +
    TECHNIQUE_CATEGORIES["linguistic"]
)


# =============================================================================
# SECTION 2: DATA CLASSES
# =============================================================================

@dataclass
class GenerationConfig:
    """Configuration for content generation."""
    techniques: List[str]
    intensity: str = "MODERATE"
    synergy_mode: bool = True
    llm_enhance: bool = True
    verify_output: bool = True
    max_insertions_per_technique: int = 2
    preserve_original_structure: bool = True

    def __post_init__(self):
        # Validate intensity
        if self.intensity not in INTENSITY_LEVELS:
            raise ValueError(f"Intensity must be one of: {INTENSITY_LEVELS}")
        # Validate techniques
        for tech in self.techniques:
            if tech not in ALL_TECHNIQUES:
                raise ValueError(f"Unknown technique: {tech}. Valid: {ALL_TECHNIQUES}")


@dataclass
class GenerationResult:
    """Result of content generation."""
    original_text: str
    enhanced_text: str
    techniques_applied: List[str]
    templates_used: List[str]
    synergy_multiplier: float
    intensity_achieved: str
    verification_score: int
    verification_details: Dict[str, Any]
    llm_enhanced: bool
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TechniqueTemplate:
    """Template for a single technique application."""
    category: str
    subtype: str
    template: str
    intensity_level: str
    placeholders: List[str]
    insertion_position: str  # "prefix", "suffix", "inline", "replace"
    example_output: str


@dataclass
class SynergyResult:
    """Result of synergy calculation."""
    techniques: List[str]
    base_multiplier: float
    count_modifier: float
    final_multiplier: float
    active_synergies: List[Tuple[Tuple[str, ...], float]]
    suggestions: List[Tuple[List[str], float]]


# =============================================================================
# SECTION 3: LLM INTEGRATION INTERFACE
# =============================================================================

class LLMInterface(ABC):
    """Abstract interface for LLM integration."""

    @abstractmethod
    def enhance_text(self, text: str, technique: str,
                     context: Dict[str, Any]) -> str:
        """Use LLM to naturally enhance text with technique."""
        pass

    @abstractmethod
    def generate_variation(self, template: str,
                          placeholders: Dict[str, str]) -> str:
        """Generate natural variation of template."""
        pass

    @abstractmethod
    def blend_insertion(self, original: str, insertion: str,
                       position: int) -> str:
        """Blend inserted content naturally into original text."""
        pass


class DefaultLLMInterface(LLMInterface):
    """Default implementation using template substitution only."""

    def enhance_text(self, text: str, technique: str,
                     context: Dict[str, Any]) -> str:
        """Fallback: return text unchanged."""
        return text

    def generate_variation(self, template: str,
                          placeholders: Dict[str, str]) -> str:
        """Simple placeholder substitution."""
        result = template
        for key, value in placeholders.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def blend_insertion(self, original: str, insertion: str,
                       position: int) -> str:
        """Simple insertion without blending."""
        if position <= 0:
            return insertion + " " + original
        elif position >= len(original):
            return original + " " + insertion
        else:
            return original[:position] + " " + insertion + " " + original[position:]


class OpenAIInterface(LLMInterface):
    """OpenAI API integration for enhanced generation."""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        return self._client

    def enhance_text(self, text: str, technique: str,
                     context: Dict[str, Any]) -> str:
        """Use GPT to naturally enhance text with technique."""
        client = self._get_client()

        prompt = f"""Enhance this text by subtly incorporating {technique} influence technique.
Keep the enhancement natural and not obvious. Preserve the original meaning.

Original text: {text}

Context: {json.dumps(context)}

Return only the enhanced text, nothing else."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()

    def generate_variation(self, template: str,
                          placeholders: Dict[str, str]) -> str:
        """Use GPT to generate natural variation of template."""
        client = self._get_client()

        # First do basic substitution
        filled = template
        for key, value in placeholders.items():
            filled = filled.replace(f"{{{key}}}", str(value))

        prompt = f"""Rephrase this to sound more natural while keeping the same meaning:
"{filled}"

Return only the rephrased text, nothing else."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )

        return response.choices[0].message.content.strip()

    def blend_insertion(self, original: str, insertion: str,
                       position: int) -> str:
        """Use GPT to naturally blend insertion into text."""
        client = self._get_client()

        before = original[:position] if position > 0 else ""
        after = original[position:] if position < len(original) else ""

        prompt = f"""Blend this insertion naturally into the surrounding text.

Before: "{before}"
Insertion: "{insertion}"
After: "{after}"

Return the complete blended text that flows naturally."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )

        return response.choices[0].message.content.strip()


class AnthropicInterface(LLMInterface):
    """Anthropic Claude API integration for enhanced generation."""

    def __init__(self, api_key: str = None, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._client

    def enhance_text(self, text: str, technique: str,
                     context: Dict[str, Any]) -> str:
        """Use Claude to naturally enhance text with technique."""
        client = self._get_client()

        prompt = f"""Enhance this text by subtly incorporating {technique} influence technique.
Keep the enhancement natural and not obvious. Preserve the original meaning.

Original text: {text}

Context: {json.dumps(context)}

Return only the enhanced text, nothing else."""

        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    def generate_variation(self, template: str,
                          placeholders: Dict[str, str]) -> str:
        """Use Claude to generate natural variation of template."""
        client = self._get_client()

        filled = template
        for key, value in placeholders.items():
            filled = filled.replace(f"{{{key}}}", str(value))

        prompt = f"""Rephrase this to sound more natural while keeping the same meaning:
"{filled}"

Return only the rephrased text, nothing else."""

        response = client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    def blend_insertion(self, original: str, insertion: str,
                       position: int) -> str:
        """Use Claude to naturally blend insertion into text."""
        client = self._get_client()

        before = original[:position] if position > 0 else ""
        after = original[position:] if position < len(original) else ""

        prompt = f"""Blend this insertion naturally into the surrounding text.

Before: "{before}"
Insertion: "{insertion}"
After: "{after}"

Return the complete blended text that flows naturally."""

        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()


# =============================================================================
# SECTION 4: GENERATION TEMPLATES
# =============================================================================

class GenerationTemplates:
    """Templates organized by technique and intensity level.

    Each technique has subtypes, and each subtype has templates at 4 intensity levels.
    Templates use {placeholder} syntax for variable substitution.
    """

    # -------------------------------------------------------------------------
    # PSYCHOLOGICAL PRINCIPLE TEMPLATES
    # -------------------------------------------------------------------------

    AUTHORITY_TEMPLATES = {
        "credentials": {
            "LOW": [
                "Expert-recommended",
                "Professionally endorsed",
                "Trusted by specialists",
            ],
            "MODERATE": [
                "Recommended by {expert_type}",
                "Backed by {credential} research",
                "Endorsed by industry experts",
            ],
            "HIGH": [
                "{credential} {name} at {institution} confirms",
                "According to {institution} research",
                "Studies from {institution} demonstrate",
            ],
            "EXTREME": [
                "Leading {field} researchers at {institution} have proven",
                "Peer-reviewed research from {institution}, {institution2}, and {institution3} validates",
                "Nobel-caliber research confirms",
            ],
        },
        "institutions": {
            "LOW": [
                "Trusted by professionals",
                "Used in professional settings",
            ],
            "MODERATE": [
                "Used at {institution}",
                "Adopted by leading organizations",
            ],
            "HIGH": [
                "Developed in collaboration with {institution}",
                "The methodology pioneered at {institution}",
            ],
            "EXTREME": [
                "Endorsed by {institution}, {institution2}, and {institution3}",
                "The gold standard at elite institutions worldwide",
            ],
        },
        "confidence": {
            "LOW": [
                "We're confident in",
                "Rest assured",
            ],
            "MODERATE": [
                "We guarantee",
                "Without question",
            ],
            "HIGH": [
                "The evidence is unequivocal",
                "There is no doubt",
            ],
            "EXTREME": [
                "The science is settled",
                "Every expert agrees",
            ],
        },
    }

    SOCIAL_PROOF_TEMPLATES = {
        "consensus": {
            "LOW": [
                "A popular choice",
                "Many people prefer this",
            ],
            "MODERATE": [
                "Join {count} satisfied customers",
                "Trusted by thousands",
                "The preferred choice of professionals",
            ],
            "HIGH": [
                "{count} people have already made this choice",
                "Over {count} customers can't be wrong",
                "The #1 choice in {category}",
            ],
            "EXTREME": [
                "{count} people chose this in the last {timeframe} alone",
                "The undisputed leader with {count}+ customers",
                "When {count} people agree, you know it's right",
            ],
        },
        "similarity": {
            "LOW": [
                "Others like you have chosen this",
                "Popular among similar customers",
            ],
            "MODERATE": [
                "People like you prefer this",
                "Customers in your situation chose this",
                "Your peers recommend this",
            ],
            "HIGH": [
                "{demographic} overwhelmingly choose this",
                "9 out of 10 {demographic} agree",
                "The top choice among {demographic}",
            ],
            "EXTREME": [
                "Every {demographic} we've surveyed chose this",
                "If you're {characteristic}, this is the only logical choice",
            ],
        },
        "trending": {
            "LOW": [
                "Gaining popularity",
                "More people are discovering this",
            ],
            "MODERATE": [
                "Trending now",
                "Growing faster than ever",
            ],
            "HIGH": [
                "Viral growth - {count} new users this week",
                "The fastest-growing option in {category}",
            ],
            "EXTREME": [
                "Explosive growth: {count} signups per {timeframe}",
                "The phenomenon everyone's talking about",
            ],
        },
    }

    SCARCITY_TEMPLATES = {
        "limitation": {
            "LOW": [
                "Limited availability",
                "While supplies last",
                "Available in limited quantities",
            ],
            "MODERATE": [
                "Only {count} remaining",
                "Limited to {count} units",
                "Stock is running low",
            ],
            "HIGH": [
                "Only {count} will ever be made",
                "Once they're gone, they're gone forever",
                "Final {count} units - no restocking",
            ],
            "EXTREME": [
                "We destroy unsold inventory. Only {count} left.",
                "Never to be reproduced. {count} remain worldwide.",
                "The vault closes permanently on this edition.",
            ],
        },
        "urgency": {
            "LOW": [
                "Available now",
                "Don't wait too long",
            ],
            "MODERATE": [
                "Act now - {reason}",
                "Offer ends {deadline}",
                "Limited time opportunity",
            ],
            "HIGH": [
                "Today only - {reason}",
                "Deadline: {deadline} - no extensions",
                "This window closes in {timeframe}",
            ],
            "EXTREME": [
                "Now or never - literally",
                "In {timeframe}, this disappears forever",
                "The clock is ticking: {countdown}",
            ],
        },
        "competition": {
            "LOW": [
                "Popular choice",
                "High demand item",
            ],
            "MODERATE": [
                "{count} people are viewing this right now",
                "Selling fast",
            ],
            "HIGH": [
                "{count} people want this - you're competing",
                "Demand exceeds supply",
            ],
            "EXTREME": [
                "Demand exceeds supply {ratio}x. Act accordingly.",
                "{count} people are trying to buy this right now. Only {available} available.",
            ],
        },
    }

    RECIPROCITY_TEMPLATES = {
        "gift": {
            "LOW": [
                "Here's something for you",
                "A small gift",
            ],
            "MODERATE": [
                "We're giving you {gift} - absolutely free",
                "Accept this complimentary {gift}",
                "This {gift} is our gift to you",
            ],
            "HIGH": [
                "We've invested {value} in creating this {gift} for you",
                "This {value} {gift} is yours - no strings attached",
            ],
            "EXTREME": [
                "We've spent {value} developing this exclusively for you",
                "This represents {hours} hours of work - and it's free for you",
            ],
        },
        "obligation": {
            "LOW": [
                "Since we've helped you",
                "Now that we've provided this",
            ],
            "MODERATE": [
                "After everything we've shared with you",
                "Given all the value we've provided",
            ],
            "HIGH": [
                "We've given you {gift}. Now it's your turn.",
                "After investing so much in your success",
            ],
            "EXTREME": [
                "We've done our part. The question is: will you do yours?",
                "We've gone above and beyond. This is the moment to reciprocate.",
            ],
        },
    }

    COMMITMENT_TEMPLATES = {
        "small_ask": {
            "LOW": [
                "Just a small step",
                "Simply try",
            ],
            "MODERATE": [
                "Just {action} - that's all",
                "All it takes is a quick {action}",
                "Simply {action} to get started",
            ],
            "HIGH": [
                "Just one click separates you from {benefit}",
                "A single {action} changes everything",
            ],
            "EXTREME": [
                "One micro-action. Massive results.",
                "30 seconds. That's all that stands between you and {benefit}.",
            ],
        },
        "escalation": {
            "LOW": [
                "The next step is",
                "Continue with",
            ],
            "MODERATE": [
                "Now that you've {previous_action}, the natural next step is",
                "Since you've already {previous_action}",
                "You've come this far",
            ],
            "HIGH": [
                "You've already invested {investment}. Don't stop now.",
                "After {previous_action}, turning back would waste everything",
            ],
            "EXTREME": [
                "You're 90% there. Stopping now means losing everything you've built.",
                "After all you've invested, this is the moment of truth.",
            ],
        },
        "public": {
            "LOW": [
                "Share your choice",
                "Let others know",
            ],
            "MODERATE": [
                "Tell your friends about your decision",
                "Share your commitment with your network",
            ],
            "HIGH": [
                "Announce your commitment publicly",
                "Make it official - share with everyone",
            ],
            "EXTREME": [
                "Declare it to the world. No turning back.",
                "Public commitment = guaranteed follow-through",
            ],
        },
    }

    LIKING_TEMPLATES = {
        "similarity": {
            "LOW": [
                "We understand you",
                "We get it",
            ],
            "MODERATE": [
                "Just like you, we {shared_trait}",
                "We've been in your shoes",
                "We share your {value}",
            ],
            "HIGH": [
                "We're not just providers - we're {shared_identity} too",
                "As fellow {shared_identity}, we understand exactly what you need",
            ],
            "EXTREME": [
                "We ARE you. We built this because we needed it ourselves.",
                "Created by {shared_identity}, for {shared_identity}. No one understands you better.",
            ],
        },
        "compliments": {
            "LOW": [
                "Good choice",
                "Smart move",
            ],
            "MODERATE": [
                "You clearly have good taste",
                "Smart decision on your part",
                "You're making the right call",
            ],
            "HIGH": [
                "You're among the select few who recognize quality",
                "Your discernment is impressive",
            ],
            "EXTREME": [
                "Only the most sophisticated recognize this opportunity",
                "You're clearly someone who doesn't settle for average",
            ],
        },
        "familiarity": {
            "LOW": [
                "You know how it is",
                "As you're aware",
            ],
            "MODERATE": [
                "Between us",
                "Like talking to an old friend",
                "You know what I mean",
            ],
            "HIGH": [
                "I'm going to be honest with you, friend to friend",
                "Let me share something I don't tell everyone",
            ],
            "EXTREME": [
                "I'm breaking protocol to tell you this personally",
                "This is just between us - don't share this with others",
            ],
        },
    }

    UNITY_TEMPLATES = {
        "ingroup": {
            "LOW": [
                "Join us",
                "Be part of something",
            ],
            "MODERATE": [
                "We're in this together",
                "Our community welcomes you",
                "You're one of us now",
            ],
            "HIGH": [
                "Welcome to the family",
                "You're part of something bigger now",
                "Together, we're unstoppable",
            ],
            "EXTREME": [
                "Blood is thicker than water. We're family now.",
                "Us against the world. Together forever.",
            ],
        },
        "shared_identity": {
            "LOW": [
                "As someone who {trait}",
                "For those who {value}",
            ],
            "MODERATE": [
                "As a {identity}, you understand",
                "Fellow {identity} agree",
                "Real {identity} know",
            ],
            "HIGH": [
                "Every true {identity} chooses this",
                "If you're a real {identity}, this is non-negotiable",
            ],
            "EXTREME": [
                "This is what separates real {identity} from pretenders",
                "Your {identity} identity demands this choice",
            ],
        },
        "shared_enemy": {
            "LOW": [
                "Don't let them win",
                "Stand against {enemy}",
            ],
            "MODERATE": [
                "Together against {enemy}",
                "We won't let {enemy} succeed",
            ],
            "HIGH": [
                "United against {enemy}",
                "Join the fight against {enemy}",
            ],
            "EXTREME": [
                "{enemy} wants you to fail. Don't give them the satisfaction.",
                "This is war against {enemy}. Which side are you on?",
            ],
        },
    }

    FRAMING_TEMPLATES = {
        "loss": {
            "LOW": [
                "Don't miss this",
                "Avoid missing out",
            ],
            "MODERATE": [
                "Don't let this opportunity slip away",
                "You'll regret not acting",
                "Missing this would be a mistake",
            ],
            "HIGH": [
                "Every day you wait, you lose {loss}",
                "The cost of inaction: {loss}",
                "What you're losing by not acting: {loss}",
            ],
            "EXTREME": [
                "You're bleeding {loss} every single day you delay",
                "The devastating cost of hesitation: {loss} - gone forever",
            ],
        },
        "gain": {
            "LOW": [
                "Get more",
                "Achieve better results",
            ],
            "MODERATE": [
                "Gain {benefit}",
                "Unlock {benefit}",
                "Achieve {benefit}",
            ],
            "HIGH": [
                "Transform your {area} with {benefit}",
                "Multiply your {metric} by {multiplier}x",
            ],
            "EXTREME": [
                "Revolutionary {benefit} that will change everything",
                "The {benefit} you never knew was possible",
            ],
        },
        "anchor": {
            "LOW": [
                "Compare to alternatives",
                "Consider the value",
            ],
            "MODERATE": [
                "Originally {high_price}, now just {low_price}",
                "Worth {high_price}, yours for {low_price}",
            ],
            "HIGH": [
                "Others charge {high_price}. Your price: {low_price}",
                "A {high_price} value for the price of {low_price}",
            ],
            "EXTREME": [
                "Competitors ask {high_price}. We ask {low_price}. The choice is obvious.",
                "You'd pay {high_price} anywhere else. Here? {low_price}. End of discussion.",
            ],
        },
    }

    # -------------------------------------------------------------------------
    # TACTICAL STIMULUS TEMPLATES
    # -------------------------------------------------------------------------

    PERSONAL_TEMPLATES = {
        "exclusion": {
            "LOW": [
                "This isn't for everyone",
                "For those who appreciate {quality}",
            ],
            "MODERATE": [
                "Not for everyone - only for those who {criteria}",
                "If you know, you know",
                "For the discerning few",
            ],
            "HIGH": [
                "This will be illegible to most - and that's the point",
                "For the {count} people who understand {reference}",
                "If you have to ask, it's not for you",
            ],
            "EXTREME": [
                "Your references are being sold back to you. This isn't.",
                "If you're still visible to the algorithm, this isn't for you",
                "Mainstream need not apply",
            ],
        },
        "status_threat": {
            "LOW": [
                "Stand out from the crowd",
                "Be distinctive",
            ],
            "MODERATE": [
                "Don't be like everyone else",
                "Rise above the ordinary",
            ],
            "HIGH": [
                "While others follow trends, you {action}",
                "The masses will never understand",
            ],
            "EXTREME": [
                "Being basic is a choice. So is this.",
                "Your cultural irrelevance ends here",
            ],
        },
        "tribal_safety": {
            "LOW": [
                "Join like-minded people",
                "Find your community",
            ],
            "MODERATE": [
                "Your people are here",
                "Among those who understand",
            ],
            "HIGH": [
                "Silent mutual recognition among those who get it",
                "The tribe awaits",
            ],
            "EXTREME": [
                "Pre-algorithmic. Post-commercial. Your tribe.",
                "Where obscurity is currency and you're wealthy",
            ],
        },
    }

    CONTRASTABLE_TEMPLATES = {
        "binary_framing": {
            "LOW": [
                "Unlike typical options",
                "Different from the rest",
            ],
            "MODERATE": [
                "Not {negative} - {positive}",
                "While they offer {negative}, we provide {positive}",
            ],
            "HIGH": [
                "{negative} is dead. Long live {positive}.",
                "The era of {negative} is over. Welcome to {positive}.",
            ],
            "EXTREME": [
                "There's {negative}. And there's {positive}. Pick your side.",
                "You're either {positive} or you're {negative}. No middle ground.",
            ],
        },
        "opposition": {
            "LOW": [
                "The alternative to mainstream",
                "A different approach",
            ],
            "MODERATE": [
                "The antidote to {problem}",
                "Everything {competitor} isn't",
            ],
            "HIGH": [
                "Built specifically to destroy {problem}",
                "The nemesis of {competitor}",
            ],
            "EXTREME": [
                "We exist because {competitor} failed you",
                "{problem} created us. Now we end it.",
            ],
        },
    }

    TANGIBLE_TEMPLATES = {
        "specifications": {
            "LOW": [
                "Quality materials",
                "Carefully crafted",
            ],
            "MODERATE": [
                "Made with {material} ({weight} gsm)",
                "Sourced from {location}",
            ],
            "HIGH": [
                "{weight} gsm {material} from {specific_location}",
                "Each piece weighs exactly {weight}g - we measured",
            ],
            "EXTREME": [
                "{weight} gsm Japanese {material}, hand-finished in {location}",
                "The exact specifications: {specs}. Every. Single. Detail.",
            ],
        },
        "process": {
            "LOW": [
                "Carefully made",
                "Quality construction",
            ],
            "MODERATE": [
                "Made in {location}",
                "Crafted by {artisan_type}",
            ],
            "HIGH": [
                "Hand-{process} over {duration}",
                "{steps} separate steps, each done by hand",
            ],
            "EXTREME": [
                "147 hours of hand-{process} by {artisan_count} artisans in {location}",
                "The {material} is aged for {duration} before the {process} even begins",
            ],
        },
        "decay": {
            "LOW": [
                "Develops character over time",
                "Ages gracefully",
            ],
            "MODERATE": [
                "Fades and softens with wear",
                "Develops unique patina over time",
            ],
            "HIGH": [
                "In {timeframe}, the {material} will fade {percentage}%",
                "Watch it transform: Month 1, Month 6, Year 1",
            ],
            "EXTREME": [
                "After {washes} washes, the texture becomes {description}",
                "Documented decay: {timeline}. Your piece tells your story.",
            ],
        },
    }

    MEMORABLE_TEMPLATES = {
        "opening": {
            "LOW": [
                "Consider this",
                "Here's something to think about",
            ],
            "MODERATE": [
                "Archive {number}",
                "From the vault",
                "Unearthed",
            ],
            "HIGH": [
                "If you recognize this, you already know",
                "The cryptic truth",
            ],
            "EXTREME": [
                "What you're about to see was never meant to be found",
                "This changes everything. Or nothing. You decide.",
            ],
        },
        "closing": {
            "LOW": [
                "The choice is yours",
                "You decide",
            ],
            "MODERATE": [
                "The rest is up to you",
                "Or you were already too late",
            ],
            "HIGH": [
                "If you've made it this far, you know what to do",
                "We never resolve. Neither should you.",
            ],
            "EXTREME": [
                "This ends when you end it. Or it never ends.",
                "You decide. We've already decided for ourselves.",
            ],
        },
    }

    VISUAL_TEMPLATES = {
        "anti_aesthetic": {
            "LOW": [
                "Unfiltered",
                "Raw and real",
            ],
            "MODERATE": [
                "Shot on {device}. Unedited.",
                "No filters. No styling. Just truth.",
            ],
            "HIGH": [
                "Bad lighting. Awkward crops. Perfect.",
                "The anti-Instagram aesthetic",
            ],
            "EXTREME": [
                "Grainy. Blown out. CCTV quality. Exactly as intended.",
                "If it looks professional, we failed.",
            ],
        },
        "mood_references": {
            "LOW": [
                "Inspired by {reference}",
                "In the style of {aesthetic}",
            ],
            "MODERATE": [
                "{aesthetic} energy",
                "References: {reference1}, {reference2}",
            ],
            "HIGH": [
                "Part mood board, part manifesto",
                "If you know {reference}, you know",
            ],
            "EXTREME": [
                "{aesthetic1} meets {aesthetic2} in a documentary about {subject}",
                "Russian Constructivism meets Brutalism meets your timeline",
            ],
        },
    }

    EMOTIONAL_TEMPLATES = {
        "pain": {
            "LOW": [
                "The struggle is real",
                "We've all been there",
            ],
            "MODERATE": [
                "Tired of {pain_point}?",
                "The frustration of {pain_point} ends here",
            ],
            "HIGH": [
                "That sinking feeling when {pain_scenario}",
                "You know the pain of {pain_point}",
            ],
            "EXTREME": [
                "The algorithm has commodified your identity. You feel it.",
                "Cultural irrelevance creeps closer every day.",
            ],
        },
        "relief": {
            "LOW": [
                "There's a better way",
                "Relief is here",
            ],
            "MODERATE": [
                "Finally, an escape from {pain_point}",
                "The solution you've been waiting for",
            ],
            "HIGH": [
                "Exit the {negative_system}. Enter the {positive_alternative}.",
                "Your escape route has arrived",
            ],
            "EXTREME": [
                "We don't have a logo because we don't need one",
                "Invisible to algorithms. Visible to those who matter.",
            ],
        },
    }

    # -------------------------------------------------------------------------
    # LINGUISTIC PATTERN TEMPLATES
    # -------------------------------------------------------------------------

    RHETORICAL_DEVICES_TEMPLATES = {
        "rhetorical_question": {
            "LOW": [
                "Isn't it time?",
                "Don't you think?",
            ],
            "MODERATE": [
                "Isn't it time you {action}?",
                "Don't you deserve {benefit}?",
                "Why settle for less?",
            ],
            "HIGH": [
                "What would your life look like if you {action}?",
                "Can you really afford not to {action}?",
            ],
            "EXTREME": [
                "How much longer will you let {problem} control you?",
                "When will enough be enough?",
            ],
        },
        "tricolon": {
            "LOW": [
                "Simple. Easy. Effective.",
                "Fast, reliable, affordable.",
            ],
            "MODERATE": [
                "{adj1}. {adj2}. {adj3}.",
                "We {verb1}, {verb2}, and {verb3}.",
            ],
            "HIGH": [
                "We came. We saw. We conquered.",
                "{statement1}. {statement2}. {statement3}.",
            ],
            "EXTREME": [
                "Yesterday's {negative}. Today's {neutral}. Tomorrow's {positive}.",
                "First, {step1}. Then, {step2}. Finally, {step3}.",
            ],
        },
        "antithesis": {
            "LOW": [
                "Not this, but that",
                "Less {negative}, more {positive}",
            ],
            "MODERATE": [
                "Not just {feature1}, but {feature2}",
                "While others {negative}, we {positive}",
            ],
            "HIGH": [
                "Ask not what {entity} can do for you, ask what you can do for {entity}",
                "One small {action}, one giant {result}",
            ],
            "EXTREME": [
                "Give me {positive} or give me nothing",
                "United we {positive}, divided we {negative}",
            ],
        },
        "anaphora": {
            "LOW": [
                "We believe... We believe...",
            ],
            "MODERATE": [
                "{repeated_phrase} {clause1}. {repeated_phrase} {clause2}.",
            ],
            "HIGH": [
                "{repeated_phrase} {clause1}. {repeated_phrase} {clause2}. {repeated_phrase} {clause3}.",
            ],
            "EXTREME": [
                "I have a {noun}. I have a {noun} that {clause1}. I have a {noun} that {clause2}.",
            ],
        },
    }

    SYNTACTIC_PATTERNS_TEMPLATES = {
        "short_sentences": {
            "LOW": [
                "It works.",
                "Simple solution.",
            ],
            "MODERATE": [
                "This is it. The answer. Right here.",
                "Done. Finished. Complete.",
            ],
            "HIGH": [
                "Stop. Look. Act.",
                "No excuses. No delays. No regrets.",
            ],
            "EXTREME": [
                "Now. Not tomorrow. Now.",
                "This. Is. Everything.",
            ],
        },
        "passive_voice": {
            "LOW": [
                "It was designed to...",
                "Results were achieved...",
            ],
            "MODERATE": [
                "Concerns have been addressed",
                "Success has been demonstrated",
            ],
            "HIGH": [
                "Mistakes were made, but solutions were found",
                "Expectations were exceeded",
            ],
            "EXTREME": [
                "History will be written by those who act",
                "Greatness is not given, it is earned",
            ],
        },
    }

    FRAMING_EFFECTS_TEMPLATES = {
        "euphemism": {
            "LOW": [
                "Streamlined",
                "Optimized",
            ],
            "MODERATE": [
                "Strategic realignment",
                "Efficiency enhancement",
            ],
            "HIGH": [
                "Resource optimization",
                "Organizational restructuring",
            ],
            "EXTREME": [
                "Transformational change initiative",
                "Proactive workforce adjustment",
            ],
        },
        "dysphemism": {
            "LOW": [
                "The problem",
                "The issue",
            ],
            "MODERATE": [
                "The {topic} crisis",
                "The {topic} disaster",
            ],
            "HIGH": [
                "The catastrophic {topic} situation",
                "The {topic} epidemic",
            ],
            "EXTREME": [
                "The {topic} plague destroying {affected_groups}",
                "The systematic {topic} assault on {affected_groups}",
            ],
        },
    }

    PRAGMATIC_PATTERNS_TEMPLATES = {
        "presupposition": {
            "LOW": [
                "When you {action}...",
                "Once you {action}...",
            ],
            "MODERATE": [
                "Since you're already {state}...",
                "Given that you {believe}...",
            ],
            "HIGH": [
                "Everyone knows that {claim}...",
                "As you've certainly noticed...",
            ],
            "EXTREME": [
                "Now that you understand {controversial_claim}...",
                "Since we all agree that {assumption}...",
            ],
        },
        "implicature": {
            "LOW": [
                "Some might say...",
                "One could argue...",
            ],
            "MODERATE": [
                "I'm not saying {claim}, but...",
                "It would be interesting if {claim}...",
            ],
            "HIGH": [
                "I'm just asking questions about {topic}",
                "Some people are saying {claim}",
            ],
            "EXTREME": [
                "I'm not allowed to tell you that {claim}, but...",
                "If {claim} were true, wouldn't that explain everything?",
            ],
        },
    }

    DISCOURSE_MARKERS_TEMPLATES = {
        "causal": {
            "LOW": [
                "Because",
                "Therefore",
            ],
            "MODERATE": [
                "Because {reason}, {conclusion}",
                "Therefore, {conclusion}",
            ],
            "HIGH": [
                "The reason is simple: {reason}. Thus, {conclusion}.",
                "Because {reason}, it logically follows that {conclusion}.",
            ],
            "EXTREME": [
                "The inescapable conclusion, given {reason}, is {conclusion}",
                "Since {premise1} and {premise2}, {conclusion} is inevitable",
            ],
        },
        "urgency": {
            "LOW": [
                "Now",
                "Today",
            ],
            "MODERATE": [
                "Immediately",
                "Right now",
                "This instant",
            ],
            "HIGH": [
                "Critical: act now",
                "Urgent action required",
            ],
            "EXTREME": [
                "IMMEDIATE ACTION REQUIRED",
                "TIME-CRITICAL: Every second counts",
            ],
        },
    }

    HEDGING_CERTAINTY_TEMPLATES = {
        "certainty_boost": {
            "LOW": [
                "Likely",
                "Probably",
            ],
            "MODERATE": [
                "Clearly",
                "Obviously",
                "Without question",
            ],
            "HIGH": [
                "The fact is",
                "It's undeniable that",
                "Everyone knows",
            ],
            "EXTREME": [
                "This is absolute truth",
                "There is no debate: {claim}",
                "Science has proven beyond doubt",
            ],
        },
        "strategic_hedge": {
            "LOW": [
                "Perhaps",
                "It seems",
            ],
            "MODERATE": [
                "It appears that",
                "One might argue",
            ],
            "HIGH": [
                "While I can't say for certain",
                "Though some might disagree",
            ],
            "EXTREME": [
                "I would never claim {false_humility}, but the evidence suggests...",
                "Far be it from me to {assertion}, however...",
            ],
        },
    }

    REGISTER_FORMALITY_TEMPLATES = {
        "intimate": {
            "LOW": [
                "Hey",
                "You know",
            ],
            "MODERATE": [
                "Between us",
                "Just between you and me",
            ],
            "HIGH": [
                "I'm going to let you in on something",
                "Can I be real with you for a second?",
            ],
            "EXTREME": [
                "Look, I shouldn't be telling you this, but...",
                "Off the record, what I'm about to share...",
            ],
        },
        "formal_authority": {
            "LOW": [
                "Please note",
                "We wish to inform",
            ],
            "MODERATE": [
                "It has come to our attention",
                "We hereby announce",
            ],
            "HIGH": [
                "In accordance with established protocols",
                "Per our rigorous standards",
            ],
            "EXTREME": [
                "By the authority vested in",
                "Pursuant to regulation {code}",
            ],
        },
    }

    CONCEPTUAL_METAPHOR_TEMPLATES = {
        "war": {
            "LOW": [
                "Tackle the problem",
                "Fight for results",
            ],
            "MODERATE": [
                "Battle against {enemy}",
                "Your arsenal includes {tools}",
                "Strategic victory over {problem}",
            ],
            "HIGH": [
                "This is war. And you're on the front lines against {enemy}.",
                "Arm yourself with {weapon}. Defeat {enemy}.",
            ],
            "EXTREME": [
                "Total war on {enemy}. No prisoners. No surrender.",
                "The ammunition you need to annihilate {problem}",
            ],
        },
        "journey": {
            "LOW": [
                "The path forward",
                "Your journey",
            ],
            "MODERATE": [
                "The road to {destination}",
                "Navigate toward {goal}",
                "Your roadmap to success",
            ],
            "HIGH": [
                "You're at a crossroads. One path leads to {positive}, the other to {negative}.",
                "The milestone ahead: {goal}",
            ],
            "EXTREME": [
                "The ultimate destination: {goal}. Every step matters.",
                "Your compass points to {destination}. Follow it or wander forever.",
            ],
        },
        "health": {
            "LOW": [
                "Healthy approach",
                "Diagnose the issue",
            ],
            "MODERATE": [
                "The cure for {problem}",
                "Symptoms of {disease}: {symptoms}",
            ],
            "HIGH": [
                "{problem} is a disease. This is the cure.",
                "The epidemic of {problem} requires aggressive treatment.",
            ],
            "EXTREME": [
                "Your {area} is sick. Possibly terminal. Here's the antidote.",
                "The {problem} virus has infected {affected_groups}. Vaccination: {solution}.",
            ],
        },
        "machine": {
            "LOW": [
                "How it works",
                "The system",
            ],
            "MODERATE": [
                "The engine driving {outcome}",
                "Optimize your {process}",
            ],
            "HIGH": [
                "A finely-tuned machine for {outcome}",
                "The mechanism behind {result}",
            ],
            "EXTREME": [
                "Reprogram yourself for {outcome}. Delete {problem}.",
                "You are the machine. Upgrade your operating system.",
            ],
        },
        "family": {
            "LOW": [
                "Part of the family",
                "Our heritage",
            ],
            "MODERATE": [
                "Join our family",
                "Like a parent to {entity}",
            ],
            "HIGH": [
                "The {brand} family welcomes you",
                "We nurture {outcome} like our own children",
            ],
            "EXTREME": [
                "Blood of my blood. You're family now.",
                "We don't have customers. We have family.",
            ],
        },
    }

    @classmethod
    def get_all_templates(cls) -> Dict[str, Dict]:
        """Return all template dictionaries."""
        return {
            # Psychological
            "AUTHORITY": cls.AUTHORITY_TEMPLATES,
            "SOCIAL_PROOF": cls.SOCIAL_PROOF_TEMPLATES,
            "SCARCITY": cls.SCARCITY_TEMPLATES,
            "RECIPROCITY": cls.RECIPROCITY_TEMPLATES,
            "COMMITMENT": cls.COMMITMENT_TEMPLATES,
            "LIKING": cls.LIKING_TEMPLATES,
            "UNITY": cls.UNITY_TEMPLATES,
            "FRAMING": cls.FRAMING_TEMPLATES,
            # Tactical
            "PERSONAL": cls.PERSONAL_TEMPLATES,
            "CONTRASTABLE": cls.CONTRASTABLE_TEMPLATES,
            "TANGIBLE": cls.TANGIBLE_TEMPLATES,
            "MEMORABLE": cls.MEMORABLE_TEMPLATES,
            "VISUAL": cls.VISUAL_TEMPLATES,
            "EMOTIONAL": cls.EMOTIONAL_TEMPLATES,
            # Linguistic
            "RHETORICAL_DEVICES": cls.RHETORICAL_DEVICES_TEMPLATES,
            "SYNTACTIC_PATTERNS": cls.SYNTACTIC_PATTERNS_TEMPLATES,
            "FRAMING_EFFECTS": cls.FRAMING_EFFECTS_TEMPLATES,
            "PRAGMATIC_PATTERNS": cls.PRAGMATIC_PATTERNS_TEMPLATES,
            "DISCOURSE_MARKERS": cls.DISCOURSE_MARKERS_TEMPLATES,
            "HEDGING_CERTAINTY": cls.HEDGING_CERTAINTY_TEMPLATES,
            "REGISTER_FORMALITY": cls.REGISTER_FORMALITY_TEMPLATES,
            "CONCEPTUAL_METAPHOR": cls.CONCEPTUAL_METAPHOR_TEMPLATES,
        }


# =============================================================================
# SECTION 5: SYNERGY MULTIPLIERS
# =============================================================================

class SynergyCalculator:
    """Calculate synergy multipliers for technique combinations.

    Based on research from:
    - RESEARCH/27_HIGH_IMPACT_DETECTION_SYSTEMS.md
    - RESEARCH/28_EXPANDED_RANKED_COMBINATIONS.md
    """

    # Known synergy combinations with multipliers
    # Key: frozenset of techniques, Value: (multiplier, mechanism, source)
    SYNERGY_MULTIPLIERS: Dict[frozenset, Tuple[float, str, str]] = {
        # Two-technique combinations
        frozenset(["SCARCITY", "SOCIAL_PROOF"]): (
            1.4,
            "Scarcity validates social proof ('others want it too')",
            "Cialdini combination studies"
        ),
        frozenset(["AUTHORITY", "SOCIAL_PROOF"]): (
            1.35,
            "Expert endorsement + crowd validation = maximum credibility",
            "Trust research"
        ),
        frozenset(["SCARCITY", "FRAMING"]): (
            1.55,
            "Loss framing amplifies scarcity pressure",
            "Loss aversion studies"
        ),
        frozenset(["EMOTIONAL", "SCARCITY"]): (
            1.6,
            "Emotional arousal impairs rational scarcity evaluation",
            "Dual-process theory research"
        ),
        frozenset(["AUTHORITY", "EMOTIONAL"]): (
            1.45,
            "Authority amplifies emotional credibility",
            "Health communication research"
        ),
        frozenset(["RECIPROCITY", "COMMITMENT"]): (
            1.25,
            "Gift creates obligation, small commitment enables larger",
            "Foot-in-door research"
        ),
        frozenset(["COMMITMENT", "SOCIAL_PROOF"]): (
            1.35,
            "Public commitment + social validation = persistence",
            "Consistency research"
        ),
        frozenset(["LIKING", "UNITY"]): (
            1.3,
            "Rapport + shared identity = deep trust",
            "In-group bias research"
        ),
        frozenset(["PERSONAL", "EMOTIONAL"]): (
            1.45,
            "Status threat + emotional relief = identity-driven action",
            "Self-concept research"
        ),
        frozenset(["CONTRASTABLE", "FRAMING"]): (
            1.4,
            "Binary framing amplifies contrast effects",
            "Comparative judgment research"
        ),

        # Three-technique combinations (higher synergy)
        frozenset(["AUTHORITY", "SCARCITY", "SOCIAL_PROOF"]): (
            1.8,
            "Triple trust: Expert says it's limited and popular",
            "Multi-factor persuasion research"
        ),
        frozenset(["AUTHORITY", "EMOTIONAL", "SCARCITY"]): (
            1.75,
            "Expert authority + emotional appeal + time pressure",
            "Fear appeal research"
        ),
        frozenset(["EMOTIONAL", "SCARCITY", "COMMITMENT"]): (
            1.7,
            "Emotional hook + urgency + sunk cost",
            "Escalation of commitment research"
        ),
        frozenset(["AUTHORITY", "UNITY", "SOCIAL_PROOF"]): (
            1.65,
            "Expert + in-group + crowd = complete trust envelope",
            "Trust cascade research"
        ),
        frozenset(["PERSONAL", "CONTRASTABLE", "EMOTIONAL"]): (
            1.6,
            "Identity threat + binary choice + relief promise",
            "Identity-based persuasion"
        ),
        frozenset(["RECIPROCITY", "LIKING", "COMMITMENT"]): (
            1.5,
            "Gift + rapport + small ask = relationship lock",
            "Relationship marketing research"
        ),
        frozenset(["SCARCITY", "SOCIAL_PROOF", "FRAMING"]): (
            1.7,
            "Limited + popular + lose-if-you-don't",
            "E-commerce optimization studies"
        ),

        # Linguistic amplifiers
        frozenset(["RHETORICAL_DEVICES", "EMOTIONAL"]): (
            1.35,
            "Rhetorical structure amplifies emotional impact",
            "Rhetoric effectiveness studies"
        ),
        frozenset(["DISCOURSE_MARKERS", "AUTHORITY"]): (
            1.25,
            "Causal language reinforces expert claims",
            "Argument structure research"
        ),
        frozenset(["CONCEPTUAL_METAPHOR", "EMOTIONAL"]): (
            1.4,
            "Metaphorical framing deepens emotional resonance",
            "Conceptual metaphor theory"
        ),
    }

    # Diminishing returns for technique overload
    TECHNIQUE_COUNT_MODIFIERS = {
        1: 1.0,
        2: 1.0,
        3: 0.95,  # Slight complexity penalty
        4: 0.90,
        5: 0.85,
        6: 0.80,
    }

    @classmethod
    def calculate_synergy(cls, techniques: List[str]) -> SynergyResult:
        """Calculate total synergy multiplier for technique combination."""
        if len(techniques) <= 1:
            return SynergyResult(
                techniques=techniques,
                base_multiplier=1.0,
                count_modifier=1.0,
                final_multiplier=1.0,
                active_synergies=[],
                suggestions=[]
            )

        techniques_set = frozenset(techniques)
        active_synergies = []
        best_multiplier = 1.0

        # Find all matching synergy patterns
        for combo, (multiplier, mechanism, source) in cls.SYNERGY_MULTIPLIERS.items():
            if combo.issubset(techniques_set):
                active_synergies.append((tuple(combo), multiplier))
                best_multiplier = max(best_multiplier, multiplier)

        # Apply diminishing returns for technique count
        count = len(techniques)
        count_modifier = cls.TECHNIQUE_COUNT_MODIFIERS.get(count, 0.75)

        final_multiplier = best_multiplier * count_modifier

        # Get suggestions for additional synergies
        suggestions = cls.suggest_additions(techniques)

        return SynergyResult(
            techniques=techniques,
            base_multiplier=best_multiplier,
            count_modifier=count_modifier,
            final_multiplier=final_multiplier,
            active_synergies=active_synergies,
            suggestions=suggestions
        )

    @classmethod
    def suggest_additions(cls, current_techniques: List[str],
                         max_suggestions: int = 3) -> List[Tuple[List[str], float]]:
        """Suggest techniques that would synergize well with current set."""
        current_set = frozenset(current_techniques)
        suggestions = []

        for combo, (multiplier, _, _) in cls.SYNERGY_MULTIPLIERS.items():
            # Find combos that include some current techniques
            overlap = combo & current_set
            if overlap and not combo.issubset(current_set):
                # This combo could be activated by adding missing techniques
                missing = list(combo - current_set)
                suggestions.append((missing, multiplier))

        # Sort by multiplier (highest first) and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]

    @classmethod
    def get_synergy_info(cls, techniques: List[str]) -> Dict[str, Any]:
        """Get detailed synergy information for a technique set."""
        result = cls.calculate_synergy(techniques)
        return {
            "techniques": result.techniques,
            "final_multiplier": round(result.final_multiplier, 2),
            "base_multiplier": round(result.base_multiplier, 2),
            "count_modifier": round(result.count_modifier, 2),
            "active_synergies": [
                {"techniques": list(combo), "multiplier": mult}
                for combo, mult in result.active_synergies
            ],
            "suggestions": [
                {"add_techniques": techs, "potential_multiplier": mult}
                for techs, mult in result.suggestions
            ]
        }


# =============================================================================
# SECTION 6: BASE GENERATOR CLASS
# =============================================================================

class BaseGenerator(ABC):
    """Base class for all technique generators."""

    category: str = "BASE"

    def __init__(self, llm: LLMInterface = None):
        self.llm = llm or DefaultLLMInterface()
        self.templates = self._get_templates()
        self.templates_used: List[str] = []

    @abstractmethod
    def _get_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Return templates for this technique."""
        pass

    def _get_insertion_points(self, text: str) -> List[int]:
        """Identify good positions to insert technique elements.

        Default: sentence boundaries.
        Override in subclasses for technique-specific positioning.
        """
        points = [0]  # Always include start
        for match in re.finditer(r'[.!?]\s+', text):
            points.append(match.end())
        points.append(len(text))  # Always include end
        return sorted(set(points))

    def _select_templates(self, intensity: str,
                         subtypes: List[str] = None) -> List[str]:
        """Select appropriate templates based on intensity and subtypes."""
        selected = []

        # If no subtypes specified, use all available
        subtypes_to_use = subtypes or list(self.templates.keys())

        for subtype in subtypes_to_use:
            if subtype in self.templates:
                subtype_templates = self.templates[subtype]
                if intensity in subtype_templates:
                    templates = subtype_templates[intensity]
                    if templates:
                        selected.append(random.choice(templates))

        return selected

    def _fill_template(self, template: str, context: str) -> str:
        """Fill template placeholders with appropriate values.

        Override in subclasses for technique-specific fill logic.
        """
        # Default: extract simple values from context
        filled = template

        # Generic placeholder fills
        generic_fills = {
            "{count}": str(random.randint(10, 10000)),
            "{timeframe}": random.choice(["24 hours", "this week", "today"]),
            "{deadline}": random.choice(["midnight", "tomorrow", "Friday"]),
            "{percentage}": str(random.randint(10, 90)),
            "{benefit}": "success",
            "{action}": "act now",
            "{reason}": "demand is high",
        }

        for placeholder, value in generic_fills.items():
            if placeholder in filled:
                filled = filled.replace(placeholder, value)

        return filled

    def _insert_at_position(self, text: str, insertion: str,
                           position: str) -> str:
        """Insert content at specified position type."""
        if position == "prefix":
            return insertion + " " + text
        elif position == "suffix":
            return text + " " + insertion
        elif position == "inline":
            points = self._get_insertion_points(text)
            if len(points) > 2:
                # Insert at a middle point
                mid_idx = len(points) // 2
                point = points[mid_idx]
                return text[:point] + " " + insertion + " " + text[point:]
            else:
                return text + " " + insertion
        else:  # replace or default
            return text + " " + insertion

    def enhance(self, text: str, intensity: str = "MODERATE",
                subtypes: List[str] = None) -> str:
        """Add technique signals to existing text."""
        self.templates_used = []
        templates = self._select_templates(intensity, subtypes)

        enhanced = text
        for template in templates:
            filled = self._fill_template(template, text)
            self.templates_used.append(filled)

            # Use LLM for natural blending if available
            if isinstance(self.llm, (OpenAIInterface, AnthropicInterface)):
                points = self._get_insertion_points(enhanced)
                position = random.choice(points[1:-1]) if len(points) > 2 else len(enhanced)
                enhanced = self.llm.blend_insertion(enhanced, filled, position)
            else:
                # Simple suffix insertion
                enhanced = enhanced.rstrip() + " " + filled

        return enhanced

    def generate(self, topic: str, intensity: str = "MODERATE") -> str:
        """Generate new content focused on this technique."""
        self.templates_used = []
        templates = self._select_templates(intensity)

        parts = []
        for template in templates:
            filled = self._fill_template(template, topic)
            self.templates_used.append(filled)

            # Use LLM for more natural generation if available
            if isinstance(self.llm, (OpenAIInterface, AnthropicInterface)):
                filled = self.llm.enhance_text(
                    filled,
                    self.category,
                    {"topic": topic, "intensity": intensity}
                )

            parts.append(filled)

        return " ".join(parts)


# =============================================================================
# SECTION 7: PSYCHOLOGICAL PRINCIPLE GENERATORS
# =============================================================================

class AuthorityGenerator(BaseGenerator):
    """Generate authority and credibility signals."""

    category = "AUTHORITY"

    INSTITUTIONS = [
        "Harvard", "Stanford", "MIT", "Yale", "Princeton",
        "Oxford", "Cambridge", "Johns Hopkins", "Mayo Clinic",
        "Berkeley", "Columbia", "Duke", "Northwestern"
    ]

    CREDENTIALS = [
        "Dr.", "Professor", "Ph.D.", "Research Director",
        "Chief Scientist", "Senior Fellow", "Distinguished Professor"
    ]

    FIELDS = [
        "behavioral science", "psychology", "neuroscience",
        "cognitive science", "decision science", "economics",
        "organizational behavior", "social psychology"
    ]

    EXPERT_TYPES = [
        "leading researchers", "industry experts", "top scientists",
        "renowned specialists", "world-class authorities"
    ]

    def _get_templates(self):
        return GenerationTemplates.AUTHORITY_TEMPLATES

    def _get_insertion_points(self, text: str) -> List[int]:
        """Authority signals work best at start of claims."""
        points = [0]  # Start is primary
        # Before statements that could benefit from authority
        for match in re.finditer(r'[.!?]\s+[A-Z]', text):
            points.append(match.start() + 2)
        return points

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{institution}", random.choice(self.INSTITUTIONS))
        filled = filled.replace("{institution2}", random.choice(self.INSTITUTIONS))
        filled = filled.replace("{institution3}", random.choice(self.INSTITUTIONS))
        filled = filled.replace("{credential}", random.choice(self.CREDENTIALS))
        filled = filled.replace("{field}", random.choice(self.FIELDS))
        filled = filled.replace("{expert_type}", random.choice(self.EXPERT_TYPES))
        filled = filled.replace("{name}", random.choice(["Smith", "Johnson", "Williams", "Chen", "Patel"]))
        return filled


class SocialProofGenerator(BaseGenerator):
    """Generate social proof and consensus signals."""

    category = "SOCIAL_PROOF"

    DEMOGRAPHICS = [
        "professionals", "business leaders", "parents",
        "millennials", "entrepreneurs", "executives",
        "homeowners", "health-conscious individuals"
    ]

    CATEGORIES = [
        "the industry", "its category", "the market",
        "the segment", "its field"
    ]

    def _get_templates(self):
        return GenerationTemplates.SOCIAL_PROOF_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{count}", f"{random.randint(10, 100) * 1000:,}")
        filled = filled.replace("{demographic}", random.choice(self.DEMOGRAPHICS))
        filled = filled.replace("{category}", random.choice(self.CATEGORIES))
        filled = filled.replace("{timeframe}", random.choice(["hour", "day", "week"]))
        filled = filled.replace("{characteristic}", random.choice(["serious about results", "value-conscious", "forward-thinking"]))
        return filled


class ScarcityGenerator(BaseGenerator):
    """Generate scarcity and urgency signals."""

    category = "SCARCITY"

    def _get_templates(self):
        return GenerationTemplates.SCARCITY_TEMPLATES

    def _get_insertion_points(self, text: str) -> List[int]:
        """Scarcity works best at end, before call to action."""
        points = []
        for match in re.finditer(r'[.!?]\s+', text):
            points.append(match.end())
        points.append(len(text))
        return points

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{count}", str(random.randint(3, 50)))
        filled = filled.replace("{available}", str(random.randint(1, 10)))
        filled = filled.replace("{deadline}", random.choice(["midnight tonight", "11:59 PM", "end of day"]))
        filled = filled.replace("{timeframe}", random.choice(["24 hours", "48 hours", "the next hour"]))
        filled = filled.replace("{reason}", random.choice(["demand exceeds supply", "inventory is limited", "production constraints"]))
        filled = filled.replace("{ratio}", str(random.randint(2, 5)))
        filled = filled.replace("{countdown}", f"{random.randint(1, 12)}:{random.randint(10, 59):02d}:00")
        return filled


class ReciprocityGenerator(BaseGenerator):
    """Generate reciprocity and obligation signals."""

    category = "RECIPROCITY"

    GIFTS = [
        "exclusive guide", "free toolkit", "bonus content",
        "complimentary consultation", "free trial", "sample pack"
    ]

    def _get_templates(self):
        return GenerationTemplates.RECIPROCITY_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{gift}", random.choice(self.GIFTS))
        filled = filled.replace("{value}", f"${random.randint(50, 500)}")
        filled = filled.replace("{hours}", str(random.randint(10, 100)))
        return filled


class CommitmentGenerator(BaseGenerator):
    """Generate commitment and consistency signals."""

    category = "COMMITMENT"

    ACTIONS = ["click", "sign up", "subscribe", "join", "start"]
    PREVIOUS_ACTIONS = ["signed up", "downloaded", "subscribed", "joined"]
    INVESTMENTS = ["time", "effort", "commitment", "energy"]
    BENEFITS = ["success", "results", "transformation", "growth"]

    def _get_templates(self):
        return GenerationTemplates.COMMITMENT_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{action}", random.choice(self.ACTIONS))
        filled = filled.replace("{previous_action}", random.choice(self.PREVIOUS_ACTIONS))
        filled = filled.replace("{investment}", random.choice(self.INVESTMENTS))
        filled = filled.replace("{benefit}", random.choice(self.BENEFITS))
        return filled


class LikingGenerator(BaseGenerator):
    """Generate liking and rapport signals."""

    category = "LIKING"

    SHARED_TRAITS = [
        "value quality", "appreciate excellence", "seek improvement",
        "understand the importance", "recognize opportunity"
    ]

    SHARED_IDENTITIES = [
        "professionals", "creators", "innovators", "leaders",
        "visionaries", "go-getters", "high-achievers"
    ]

    VALUES = ["excellence", "integrity", "innovation", "quality"]

    def _get_templates(self):
        return GenerationTemplates.LIKING_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{shared_trait}", random.choice(self.SHARED_TRAITS))
        filled = filled.replace("{shared_identity}", random.choice(self.SHARED_IDENTITIES))
        filled = filled.replace("{value}", random.choice(self.VALUES))
        return filled


class UnityGenerator(BaseGenerator):
    """Generate unity and in-group signals."""

    category = "UNITY"

    IDENTITIES = [
        "professional", "parent", "entrepreneur", "leader",
        "creator", "innovator", "member", "believer"
    ]

    TRAITS = ["care about quality", "value results", "seek excellence"]

    ENEMIES = [
        "mediocrity", "the status quo", "complacency",
        "outdated thinking", "stagnation"
    ]

    def _get_templates(self):
        return GenerationTemplates.UNITY_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{identity}", random.choice(self.IDENTITIES))
        filled = filled.replace("{trait}", random.choice(self.TRAITS))
        filled = filled.replace("{enemy}", random.choice(self.ENEMIES))
        return filled


class FramingGenerator(BaseGenerator):
    """Generate gain/loss framing and anchoring signals."""

    category = "FRAMING"

    LOSSES = [
        "opportunities", "potential gains", "competitive advantage",
        "market share", "time", "money", "growth potential"
    ]

    BENEFITS = [
        "efficiency", "productivity", "results", "growth",
        "success", "competitive advantage", "peace of mind"
    ]

    AREAS = ["business", "career", "life", "workflow", "results"]

    def _get_templates(self):
        return GenerationTemplates.FRAMING_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{loss}", random.choice(self.LOSSES))
        filled = filled.replace("{benefit}", random.choice(self.BENEFITS))
        filled = filled.replace("{area}", random.choice(self.AREAS))
        filled = filled.replace("{metric}", random.choice(["results", "output", "productivity"]))
        filled = filled.replace("{multiplier}", str(random.randint(2, 10)))

        # Price anchoring
        high = random.randint(200, 1000)
        low = int(high * random.uniform(0.2, 0.5))
        filled = filled.replace("{high_price}", f"${high}")
        filled = filled.replace("{low_price}", f"${low}")

        return filled


# =============================================================================
# SECTION 8: TACTICAL STIMULUS GENERATORS
# =============================================================================

class PersonalStimulusGenerator(BaseGenerator):
    """Generate self-centered targeting patterns."""

    category = "PERSONAL"

    QUALITIES = ["authenticity", "discernment", "sophistication", "depth"]
    CRITERIA = ["understand the reference", "know the difference", "get it"]
    REFERENCES = ["the original", "what came before", "the source"]
    ACTIONS = ["lead", "choose deliberately", "think independently"]

    def _get_templates(self):
        return GenerationTemplates.PERSONAL_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{quality}", random.choice(self.QUALITIES))
        filled = filled.replace("{criteria}", random.choice(self.CRITERIA))
        filled = filled.replace("{reference}", random.choice(self.REFERENCES))
        filled = filled.replace("{action}", random.choice(self.ACTIONS))
        filled = filled.replace("{count}", str(random.randint(100, 1000)))
        return filled


class ContrastableGenerator(BaseGenerator):
    """Generate binary ideological framing."""

    category = "CONTRASTABLE"

    BINARY_PAIRS = [
        ("mass-produced", "handcrafted"),
        ("algorithmic", "curated"),
        ("commercial", "authentic"),
        ("generic", "unique"),
        ("mainstream", "distinctive"),
    ]

    PROBLEMS = ["mediocrity", "sameness", "the algorithm", "mass production"]
    COMPETITORS = ["the mainstream", "everyone else", "the status quo"]

    def _get_templates(self):
        return GenerationTemplates.CONTRASTABLE_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        pair = random.choice(self.BINARY_PAIRS)
        filled = filled.replace("{negative}", pair[0])
        filled = filled.replace("{positive}", pair[1])
        filled = filled.replace("{problem}", random.choice(self.PROBLEMS))
        filled = filled.replace("{competitor}", random.choice(self.COMPETITORS))
        return filled


class TangibleGenerator(BaseGenerator):
    """Generate concrete specification language."""

    category = "TANGIBLE"

    MATERIALS = ["cotton", "linen", "leather", "canvas", "wool", "silk"]
    LOCATIONS = ["Portugal", "Italy", "Japan", "England", "France"]
    PROCESSES = ["stitched", "woven", "crafted", "finished", "aged"]
    ARTISAN_TYPES = ["master craftsmen", "third-generation artisans", "skilled specialists"]

    def _get_templates(self):
        return GenerationTemplates.TANGIBLE_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{material}", random.choice(self.MATERIALS))
        filled = filled.replace("{weight}", str(random.randint(180, 400)))
        filled = filled.replace("{location}", random.choice(self.LOCATIONS))
        filled = filled.replace("{specific_location}", random.choice(["Northern Portugal", "Tuscany", "Okayama"]))
        filled = filled.replace("{process}", random.choice(self.PROCESSES))
        filled = filled.replace("{duration}", random.choice(["6 months", "12 weeks", "90 days"]))
        filled = filled.replace("{steps}", str(random.randint(20, 100)))
        filled = filled.replace("{artisan_type}", random.choice(self.ARTISAN_TYPES))
        filled = filled.replace("{artisan_count}", str(random.randint(2, 12)))
        filled = filled.replace("{timeframe}", random.choice(["6 months", "a year", "18 months"]))
        filled = filled.replace("{percentage}", str(random.randint(10, 40)))
        filled = filled.replace("{washes}", str(random.randint(10, 50)))
        filled = filled.replace("{description}", random.choice(["butter-soft", "perfectly broken-in", "uniquely yours"]))
        filled = filled.replace("{specs}", "every thread, every stitch, every millimeter")
        filled = filled.replace("{timeline}", "Day 1 → Month 3 → Year 1")
        return filled


class MemorableGenerator(BaseGenerator):
    """Generate U-curve memory structure."""

    category = "MEMORABLE"

    def _get_templates(self):
        return GenerationTemplates.MEMORABLE_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{number}", str(random.randint(1, 99)))
        return filled


class VisualGenerator(BaseGenerator):
    """Generate anti-aesthetic visual language."""

    category = "VISUAL"

    DEVICES = ["iPhone 4", "disposable camera", "webcam", "surveillance camera"]
    AESTHETICS = ["Brutalist", "Documentary", "Post-internet", "Anti-design"]
    REFERENCES = ["90s zines", "Soviet photography", "Surveillance footage"]
    SUBJECTS = ["nothing", "the mundane", "everyday objects"]

    def _get_templates(self):
        return GenerationTemplates.VISUAL_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{device}", random.choice(self.DEVICES))
        filled = filled.replace("{aesthetic}", random.choice(self.AESTHETICS))
        filled = filled.replace("{aesthetic1}", random.choice(self.AESTHETICS))
        filled = filled.replace("{aesthetic2}", random.choice(self.AESTHETICS))
        filled = filled.replace("{reference}", random.choice(self.REFERENCES))
        filled = filled.replace("{reference1}", random.choice(self.REFERENCES))
        filled = filled.replace("{reference2}", random.choice(self.REFERENCES))
        filled = filled.replace("{subject}", random.choice(self.SUBJECTS))
        return filled


class EmotionalGenerator(BaseGenerator):
    """Generate pain-relief emotional arcs."""

    category = "EMOTIONAL"

    PAIN_POINTS = [
        "endless scrolling", "algorithm anxiety", "cultural irrelevance",
        "decision fatigue", "information overload", "comparison trap"
    ]

    PAIN_SCENARIOS = [
        "you realize your feed has become a mirror of your insecurities",
        "another algorithm decides what you should see",
        "your authentic taste gets drowned in recommendations"
    ]

    NEGATIVE_SYSTEMS = ["the algorithm", "the mainstream", "the feed"]
    POSITIVE_ALTERNATIVES = ["curation", "intention", "authenticity"]

    def _get_templates(self):
        return GenerationTemplates.EMOTIONAL_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{pain_point}", random.choice(self.PAIN_POINTS))
        filled = filled.replace("{pain_scenario}", random.choice(self.PAIN_SCENARIOS))
        filled = filled.replace("{negative_system}", random.choice(self.NEGATIVE_SYSTEMS))
        filled = filled.replace("{positive_alternative}", random.choice(self.POSITIVE_ALTERNATIVES))
        return filled


# =============================================================================
# SECTION 9: LINGUISTIC PATTERN GENERATORS
# =============================================================================

class RhetoricalDeviceGenerator(BaseGenerator):
    """Generate rhetorical devices."""

    category = "RHETORICAL_DEVICES"

    ACTIONS = ["take control", "make the change", "seize the opportunity"]
    BENEFITS = ["freedom", "success", "clarity", "growth"]
    ADJECTIVES = ["Fast", "Reliable", "Powerful"]
    VERBS = ["deliver", "create", "transform"]
    STATEMENTS = [
        "We believe in quality",
        "We believe in results",
        "We believe in you"
    ]
    ENTITIES = ["your goals", "your success", "your growth"]
    NOUNS = ["dream", "vision", "goal"]

    def _get_templates(self):
        return GenerationTemplates.RHETORICAL_DEVICES_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{action}", random.choice(self.ACTIONS))
        filled = filled.replace("{benefit}", random.choice(self.BENEFITS))
        filled = filled.replace("{problem}", random.choice(["doubt", "hesitation", "uncertainty"]))
        filled = filled.replace("{adj1}", self.ADJECTIVES[0])
        filled = filled.replace("{adj2}", self.ADJECTIVES[1])
        filled = filled.replace("{adj3}", self.ADJECTIVES[2])
        filled = filled.replace("{verb1}", self.VERBS[0])
        filled = filled.replace("{verb2}", self.VERBS[1])
        filled = filled.replace("{verb3}", self.VERBS[2])
        filled = filled.replace("{statement1}", self.STATEMENTS[0])
        filled = filled.replace("{statement2}", self.STATEMENTS[1])
        filled = filled.replace("{statement3}", self.STATEMENTS[2])
        filled = filled.replace("{feature1}", "features")
        filled = filled.replace("{feature2}", "benefits")
        filled = filled.replace("{entity}", random.choice(self.ENTITIES))
        filled = filled.replace("{positive}", "succeed")
        filled = filled.replace("{negative}", "fail")
        filled = filled.replace("{repeated_phrase}", random.choice(["We believe", "You deserve", "It's time"]))
        filled = filled.replace("{clause1}", "in excellence")
        filled = filled.replace("{clause2}", "in results")
        filled = filled.replace("{clause3}", "in you")
        filled = filled.replace("{noun}", random.choice(self.NOUNS))
        filled = filled.replace("{step1}", "we listen")
        filled = filled.replace("{step2}", "we plan")
        filled = filled.replace("{step3}", "we deliver")
        filled = filled.replace("{neutral}", "progress")
        return filled


class SyntacticPatternGenerator(BaseGenerator):
    """Generate syntactic patterns."""

    category = "SYNTACTIC_PATTERNS"

    def _get_templates(self):
        return GenerationTemplates.SYNTACTIC_PATTERNS_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        return template


class FramingEffectGenerator(BaseGenerator):
    """Generate euphemisms and dysphemisms."""

    category = "FRAMING_EFFECTS"

    TOPICS = ["change", "competition", "regulation", "oversight"]
    AFFECTED_GROUPS = ["consumers", "businesses", "families", "communities"]

    def _get_templates(self):
        return GenerationTemplates.FRAMING_EFFECTS_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{topic}", random.choice(self.TOPICS))
        filled = filled.replace("{affected_groups}", random.choice(self.AFFECTED_GROUPS))
        return filled


class PragmaticPatternGenerator(BaseGenerator):
    """Generate presuppositions and implicatures."""

    category = "PRAGMATIC_PATTERNS"

    ACTIONS = ["take action", "make this choice", "join us"]
    STATES = ["looking for solutions", "ready for change", "seeking improvement"]
    BELIEFS = ["quality matters", "results count", "time is valuable"]
    CLAIMS = ["this changes everything", "the old ways are dead", "revolution is here"]
    ASSUMPTIONS = ["excellence is rare", "most settle for less", "you're different"]

    def _get_templates(self):
        return GenerationTemplates.PRAGMATIC_PATTERNS_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{action}", random.choice(self.ACTIONS))
        filled = filled.replace("{state}", random.choice(self.STATES))
        filled = filled.replace("{believe}", random.choice(self.BELIEFS))
        filled = filled.replace("{claim}", random.choice(self.CLAIMS))
        filled = filled.replace("{controversial_claim}", random.choice(self.CLAIMS))
        filled = filled.replace("{assumption}", random.choice(self.ASSUMPTIONS))
        filled = filled.replace("{topic}", random.choice(["the market", "the industry", "what's possible"]))
        return filled


class DiscourseMarkerGenerator(BaseGenerator):
    """Generate causal and urgency markers."""

    category = "DISCOURSE_MARKERS"

    REASONS = ["the market demands it", "timing is everything", "opportunity waits for no one"]
    CONCLUSIONS = ["action is required", "the choice is clear", "now is the time"]
    PREMISES = ["quality matters", "results speak"]

    def _get_templates(self):
        return GenerationTemplates.DISCOURSE_MARKERS_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{reason}", random.choice(self.REASONS))
        filled = filled.replace("{conclusion}", random.choice(self.CONCLUSIONS))
        filled = filled.replace("{premise1}", self.PREMISES[0])
        filled = filled.replace("{premise2}", self.PREMISES[1])
        return filled


class HedgingCertaintyGenerator(BaseGenerator):
    """Generate certainty boosters and strategic hedges."""

    category = "HEDGING_CERTAINTY"

    CLAIMS = [
        "this approach delivers results",
        "change is coming",
        "the old ways are fading"
    ]

    FALSE_HUMILITY = ["be the expert", "have all the answers", "claim perfection"]
    ASSERTIONS = ["speak for everyone", "make guarantees", "overstate"]

    def _get_templates(self):
        return GenerationTemplates.HEDGING_CERTAINTY_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{claim}", random.choice(self.CLAIMS))
        filled = filled.replace("{false_humility}", random.choice(self.FALSE_HUMILITY))
        filled = filled.replace("{assertion}", random.choice(self.ASSERTIONS))
        return filled


class RegisterFormalityGenerator(BaseGenerator):
    """Generate register shifts and formality markers."""

    category = "REGISTER_FORMALITY"

    CODES = ["47.B.2", "12.3.a", "A-7"]

    def _get_templates(self):
        return GenerationTemplates.REGISTER_FORMALITY_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{code}", random.choice(self.CODES))
        return filled


class ConceptualMetaphorGenerator(BaseGenerator):
    """Generate conceptual metaphors."""

    category = "CONCEPTUAL_METAPHOR"

    ENEMIES = ["inefficiency", "mediocrity", "stagnation", "complacency"]
    TOOLS = ["strategies", "techniques", "methods", "approaches"]
    WEAPONS = ["insights", "data", "knowledge", "expertise"]
    DESTINATIONS = ["success", "growth", "excellence", "mastery"]
    GOALS = ["transformation", "improvement", "breakthrough"]
    PROBLEMS = ["inefficiency", "outdated thinking", "stagnation"]
    DISEASES = ["mediocrity", "complacency", "status quo"]
    SYMPTOMS = ["declining results", "missed opportunities", "wasted potential"]
    OUTCOMES = ["peak performance", "optimal results", "maximum efficiency"]
    PROCESSES = ["your workflow", "your approach", "your strategy"]
    BRANDS = ["Company", "Brand", "Organization"]
    ENTITIES = ["your results", "your growth"]

    def _get_templates(self):
        return GenerationTemplates.CONCEPTUAL_METAPHOR_TEMPLATES

    def _fill_template(self, template: str, context: str) -> str:
        filled = template
        filled = filled.replace("{enemy}", random.choice(self.ENEMIES))
        filled = filled.replace("{tools}", random.choice(self.TOOLS))
        filled = filled.replace("{weapon}", random.choice(self.WEAPONS))
        filled = filled.replace("{destination}", random.choice(self.DESTINATIONS))
        filled = filled.replace("{goal}", random.choice(self.GOALS))
        filled = filled.replace("{problem}", random.choice(self.PROBLEMS))
        filled = filled.replace("{disease}", random.choice(self.DISEASES))
        filled = filled.replace("{symptoms}", random.choice(self.SYMPTOMS))
        filled = filled.replace("{outcome}", random.choice(self.OUTCOMES))
        filled = filled.replace("{process}", random.choice(self.PROCESSES))
        filled = filled.replace("{result}", "results")
        filled = filled.replace("{positive}", "excellence")
        filled = filled.replace("{negative}", "mediocrity")
        filled = filled.replace("{area}", random.choice(["business", "career", "performance"]))
        filled = filled.replace("{solution}", "proven methodology")
        filled = filled.replace("{affected_groups}", "organizations everywhere")
        filled = filled.replace("{brand}", random.choice(self.BRANDS))
        filled = filled.replace("{entity}", random.choice(self.ENTITIES))
        return filled


# =============================================================================
# SECTION 10: MAIN UNIFIED GENERATOR CLASS
# =============================================================================

class UnifiedInfluenceGenerator:
    """Main interface for generating influence content.

    Combines all 22 technique generators with synergy calculations
    and automatic verification through the auditor.
    """

    def __init__(self, llm: LLMInterface = None):
        """Initialize the generator.

        Args:
            llm: Optional LLM interface for enhanced generation.
                 If None, uses template-only generation.
        """
        self.llm = llm or DefaultLLMInterface()
        self.auditor = UnifiedPersuasionAuditor()
        self.synergy = SynergyCalculator()

        # Initialize all generators
        self.generators: Dict[str, BaseGenerator] = {
            # Psychological Principles
            "AUTHORITY": AuthorityGenerator(self.llm),
            "SOCIAL_PROOF": SocialProofGenerator(self.llm),
            "SCARCITY": ScarcityGenerator(self.llm),
            "RECIPROCITY": ReciprocityGenerator(self.llm),
            "COMMITMENT": CommitmentGenerator(self.llm),
            "LIKING": LikingGenerator(self.llm),
            "UNITY": UnityGenerator(self.llm),
            "FRAMING": FramingGenerator(self.llm),
            # Tactical Stimulus
            "PERSONAL": PersonalStimulusGenerator(self.llm),
            "CONTRASTABLE": ContrastableGenerator(self.llm),
            "TANGIBLE": TangibleGenerator(self.llm),
            "MEMORABLE": MemorableGenerator(self.llm),
            "VISUAL": VisualGenerator(self.llm),
            "EMOTIONAL": EmotionalGenerator(self.llm),
            # Linguistic Patterns
            "RHETORICAL_DEVICES": RhetoricalDeviceGenerator(self.llm),
            "SYNTACTIC_PATTERNS": SyntacticPatternGenerator(self.llm),
            "FRAMING_EFFECTS": FramingEffectGenerator(self.llm),
            "PRAGMATIC_PATTERNS": PragmaticPatternGenerator(self.llm),
            "DISCOURSE_MARKERS": DiscourseMarkerGenerator(self.llm),
            "HEDGING_CERTAINTY": HedgingCertaintyGenerator(self.llm),
            "REGISTER_FORMALITY": RegisterFormalityGenerator(self.llm),
            "CONCEPTUAL_METAPHOR": ConceptualMetaphorGenerator(self.llm),
        }

    def enhance(self, text: str, config: GenerationConfig) -> GenerationResult:
        """Enhance existing text with selected techniques.

        Args:
            text: Original text to enhance
            config: Generation configuration

        Returns:
            GenerationResult with enhanced text and metadata
        """
        enhanced = text
        all_templates_used = []

        # Calculate synergy
        synergy_result = SynergyResult(
            techniques=config.techniques,
            base_multiplier=1.0,
            count_modifier=1.0,
            final_multiplier=1.0,
            active_synergies=[],
            suggestions=[]
        )
        if config.synergy_mode:
            synergy_result = self.synergy.calculate_synergy(config.techniques)

        # Apply each technique
        for technique in config.techniques:
            if technique in self.generators:
                generator = self.generators[technique]
                enhanced = generator.enhance(enhanced, config.intensity)
                all_templates_used.extend(generator.templates_used)

        # Verify with auditor
        verification_score = 0
        intensity_achieved = "UNKNOWN"
        verification_details = {}

        if config.verify_output:
            audit_result = self.auditor.audit(enhanced)
            # Access the composite scores from the audit result
            if hasattr(audit_result, 'composite_scores'):
                verification_score = int(audit_result.composite_scores.get("overall", 0))
                intensity_achieved = audit_result.classification
                verification_details = {
                    "composite_scores": audit_result.composite_scores,
                    "classification": audit_result.classification,
                }

        return GenerationResult(
            original_text=text,
            enhanced_text=enhanced,
            techniques_applied=config.techniques,
            templates_used=all_templates_used,
            synergy_multiplier=synergy_result.final_multiplier,
            intensity_achieved=intensity_achieved,
            verification_score=verification_score,
            verification_details=verification_details,
            llm_enhanced=isinstance(self.llm, (OpenAIInterface, AnthropicInterface)),
        )

    def generate(self, topic: str, config: GenerationConfig) -> GenerationResult:
        """Generate new content from scratch using specified techniques.

        Args:
            topic: Topic or subject to generate content about
            config: Generation configuration

        Returns:
            GenerationResult with generated content and metadata
        """
        parts = []
        all_templates_used = []

        for technique in config.techniques:
            if technique in self.generators:
                generator = self.generators[technique]
                part = generator.generate(topic, config.intensity)
                parts.append(part)
                all_templates_used.extend(generator.templates_used)

        generated = " ".join(parts)

        # Now enhance the generated content for final polish
        # Create a new config for enhancement (without duplicating techniques)
        enhance_config = GenerationConfig(
            techniques=[],  # Don't re-apply techniques
            intensity=config.intensity,
            synergy_mode=config.synergy_mode,
            llm_enhance=config.llm_enhance,
            verify_output=config.verify_output,
        )

        # Calculate synergy for original techniques
        synergy_result = SynergyResult(
            techniques=config.techniques,
            base_multiplier=1.0,
            count_modifier=1.0,
            final_multiplier=1.0,
            active_synergies=[],
            suggestions=[]
        )
        if config.synergy_mode:
            synergy_result = self.synergy.calculate_synergy(config.techniques)

        # Verify with auditor
        verification_score = 0
        intensity_achieved = "UNKNOWN"
        verification_details = {}

        if config.verify_output:
            audit_result = self.auditor.audit(generated)
            if hasattr(audit_result, 'composite_scores'):
                verification_score = int(audit_result.composite_scores.get("overall", 0))
                intensity_achieved = audit_result.classification
                verification_details = {
                    "composite_scores": audit_result.composite_scores,
                    "classification": audit_result.classification,
                }

        return GenerationResult(
            original_text=f"[Generated from topic: {topic}]",
            enhanced_text=generated,
            techniques_applied=config.techniques,
            templates_used=all_templates_used,
            synergy_multiplier=synergy_result.final_multiplier,
            intensity_achieved=intensity_achieved,
            verification_score=verification_score,
            verification_details=verification_details,
            llm_enhanced=isinstance(self.llm, (OpenAIInterface, AnthropicInterface)),
        )

    def suggest_techniques(self, goal: str) -> Dict[str, Any]:
        """Suggest technique combinations based on goal.

        Args:
            goal: The persuasion goal (urgency, credibility, connection, action, memory)

        Returns:
            Dictionary with recommended techniques and synergy info
        """
        goal_mappings = {
            "urgency": ["SCARCITY", "EMOTIONAL", "FRAMING"],
            "credibility": ["AUTHORITY", "SOCIAL_PROOF", "UNITY"],
            "connection": ["LIKING", "UNITY", "PERSONAL"],
            "action": ["COMMITMENT", "RECIPROCITY", "SCARCITY"],
            "memory": ["MEMORABLE", "RHETORICAL_DEVICES", "EMOTIONAL"],
            "trust": ["AUTHORITY", "SOCIAL_PROOF", "LIKING"],
            "exclusivity": ["PERSONAL", "SCARCITY", "CONTRASTABLE"],
            "authenticity": ["TANGIBLE", "VISUAL", "EMOTIONAL"],
        }

        recommended = goal_mappings.get(goal.lower(), ["AUTHORITY", "SCARCITY"])
        synergy_info = self.synergy.get_synergy_info(recommended)

        return {
            "goal": goal,
            "techniques": recommended,
            "synergy_multiplier": synergy_info["final_multiplier"],
            "active_synergies": synergy_info["active_synergies"],
            "suggestions": synergy_info["suggestions"],
            "rationale": f"These techniques synergize well for {goal} goals",
        }

    def list_techniques(self) -> Dict[str, List[str]]:
        """List all available techniques by category."""
        return TECHNIQUE_CATEGORIES.copy()

    def get_technique_info(self, technique: str) -> Dict[str, Any]:
        """Get detailed information about a specific technique.

        Args:
            technique: Technique name (e.g., "SCARCITY")

        Returns:
            Dictionary with technique details
        """
        if technique not in self.generators:
            return {"error": f"Unknown technique: {technique}"}

        generator = self.generators[technique]
        templates = generator._get_templates()

        # Count templates per intensity
        template_counts = {}
        for subtype, intensity_dict in templates.items():
            for intensity, template_list in intensity_dict.items():
                if intensity not in template_counts:
                    template_counts[intensity] = 0
                template_counts[intensity] += len(template_list)

        # Find synergies involving this technique
        synergies = []
        for combo, (mult, mech, src) in SynergyCalculator.SYNERGY_MULTIPLIERS.items():
            if technique in combo:
                synergies.append({
                    "techniques": list(combo),
                    "multiplier": mult,
                    "mechanism": mech,
                })

        return {
            "technique": technique,
            "category": generator.category,
            "subtypes": list(templates.keys()),
            "template_counts": template_counts,
            "total_templates": sum(template_counts.values()),
            "synergies": synergies,
        }


# =============================================================================
# SECTION 11: CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for the generator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate influence content for research purposes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance text with specific techniques
  python UNIFIED_GENERATOR.py enhance "Try our product today" -t SCARCITY AUTHORITY

  # Generate content from scratch
  python UNIFIED_GENERATOR.py generate "productivity software" -t EMOTIONAL SCARCITY

  # Get technique suggestions
  python UNIFIED_GENERATOR.py suggest urgency

  # List all techniques
  python UNIFIED_GENERATOR.py list

  # Get technique info
  python UNIFIED_GENERATOR.py info SCARCITY
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Enhance command
    enhance_parser = subparsers.add_parser("enhance", help="Enhance existing text")
    enhance_parser.add_argument("text", help="Text to enhance")
    enhance_parser.add_argument("-t", "--techniques", nargs="+", required=True,
                               help="Techniques to apply")
    enhance_parser.add_argument("-i", "--intensity", default="MODERATE",
                               choices=INTENSITY_LEVELS,
                               help="Intensity level")
    enhance_parser.add_argument("--no-synergy", action="store_true",
                               help="Disable synergy calculations")
    enhance_parser.add_argument("--no-verify", action="store_true",
                               help="Skip auditor verification")
    enhance_parser.add_argument("--llm", choices=["openai", "anthropic"],
                               help="Use LLM for enhanced generation")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate new content")
    gen_parser.add_argument("topic", help="Topic to generate about")
    gen_parser.add_argument("-t", "--techniques", nargs="+", required=True,
                           help="Techniques to apply")
    gen_parser.add_argument("-i", "--intensity", default="MODERATE",
                           choices=INTENSITY_LEVELS,
                           help="Intensity level")
    gen_parser.add_argument("--no-synergy", action="store_true",
                           help="Disable synergy calculations")
    gen_parser.add_argument("--no-verify", action="store_true",
                           help="Skip auditor verification")
    gen_parser.add_argument("--llm", choices=["openai", "anthropic"],
                           help="Use LLM for enhanced generation")

    # List command
    list_parser = subparsers.add_parser("list", help="List available techniques")

    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Suggest techniques for a goal")
    suggest_parser.add_argument("goal", help="Goal: urgency, credibility, connection, action, memory, trust, exclusivity, authenticity")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get info about a technique")
    info_parser.add_argument("technique", help="Technique name")

    # Synergy command
    synergy_parser = subparsers.add_parser("synergy", help="Calculate synergy for techniques")
    synergy_parser.add_argument("techniques", nargs="+", help="Techniques to analyze")

    args = parser.parse_args()

    # Initialize LLM if requested
    llm = None
    if hasattr(args, 'llm') and args.llm:
        if args.llm == "openai":
            llm = OpenAIInterface()
        elif args.llm == "anthropic":
            llm = AnthropicInterface()

    generator = UnifiedInfluenceGenerator(llm=llm)

    if args.command == "enhance":
        config = GenerationConfig(
            techniques=[t.upper() for t in args.techniques],
            intensity=args.intensity,
            synergy_mode=not args.no_synergy,
            verify_output=not args.no_verify,
        )
        result = generator.enhance(args.text, config)
        output = {
            "original": result.original_text,
            "enhanced": result.enhanced_text,
            "techniques": result.techniques_applied,
            "templates_used": result.templates_used,
            "synergy_multiplier": result.synergy_multiplier,
            "verification_score": result.verification_score,
            "intensity_achieved": result.intensity_achieved,
        }
        print(json.dumps(output, indent=2))

    elif args.command == "generate":
        config = GenerationConfig(
            techniques=[t.upper() for t in args.techniques],
            intensity=args.intensity,
            synergy_mode=not args.no_synergy,
            verify_output=not args.no_verify,
        )
        result = generator.generate(args.topic, config)
        output = {
            "topic": args.topic,
            "generated": result.enhanced_text,
            "techniques": result.techniques_applied,
            "templates_used": result.templates_used,
            "synergy_multiplier": result.synergy_multiplier,
            "verification_score": result.verification_score,
            "intensity_achieved": result.intensity_achieved,
        }
        print(json.dumps(output, indent=2))

    elif args.command == "list":
        print(json.dumps(generator.list_techniques(), indent=2))

    elif args.command == "suggest":
        print(json.dumps(generator.suggest_techniques(args.goal), indent=2))

    elif args.command == "info":
        print(json.dumps(generator.get_technique_info(args.technique.upper()), indent=2))

    elif args.command == "synergy":
        techniques = [t.upper() for t in args.techniques]
        print(json.dumps(SynergyCalculator.get_synergy_info(techniques), indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
