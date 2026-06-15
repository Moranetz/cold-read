from __future__ import annotations
"""
Preset Personas — 10 Recipient Archetypes
==========================================
Pre-configured RecipientProfiles for common analysis scenarios.
5 e-commerce personas + 5 politics/PR personas.

Each persona represents a cluster of traits that co-occur in real
populations. The specific values are UNCALIBRATED — they represent
plausible configurations, not empirical measurements of actual
population segments.
"""

from core.recipient_profile import RecipientProfile


# ═══════════════════════════════════════════════════════════════════════════════
# E-COMMERCE PERSONAS
# ═══════════════════════════════════════════════════════════════════════════════

IMPULSE_BUYER = RecipientProfile(
    # High extraversion, low conscientiousness, low EL, high neuroticism
    # Responds to urgency, social proof, emotional appeals
    openness=0.5,
    conscientiousness=0.2,
    extraversion=0.8,
    agreeableness=0.6,
    neuroticism=0.75,
    care_harm=0.5,
    fairness_cheating=0.4,
    loyalty_betrayal=0.5,
    authority_subversion=0.4,
    sanctity_degradation=0.3,
    liberty_oppression=0.3,
    economic_ideology=0.0,
    social_ideology=0.0,
    prior_belief=0.5,
    involvement=0.6,
    elaboration_likelihood=0.2,
)

PRICE_HUNTER = RecipientProfile(
    # High conscientiousness, high EL, low agreeableness, prevention focus
    # Responds to evidence, logical appeals, comparison data
    openness=0.5,
    conscientiousness=0.85,
    extraversion=0.3,
    agreeableness=0.3,
    neuroticism=0.4,
    care_harm=0.4,
    fairness_cheating=0.7,
    loyalty_betrayal=0.3,
    authority_subversion=0.3,
    sanctity_degradation=0.3,
    liberty_oppression=0.6,
    economic_ideology=0.0,
    social_ideology=0.0,
    prior_belief=0.3,
    involvement=0.8,
    elaboration_likelihood=0.85,
)

BRAND_LOYALIST = RecipientProfile(
    # High loyalty, high conscientiousness, high prior belief
    # Responds to brand authority, consistency, community
    openness=0.3,
    conscientiousness=0.7,
    extraversion=0.5,
    agreeableness=0.7,
    neuroticism=0.3,
    care_harm=0.5,
    fairness_cheating=0.5,
    loyalty_betrayal=0.85,
    authority_subversion=0.7,
    sanctity_degradation=0.5,
    liberty_oppression=0.3,
    economic_ideology=0.0,
    social_ideology=0.0,
    prior_belief=0.85,
    involvement=0.7,
    elaboration_likelihood=0.5,
)

SOCIAL_SHOPPER = RecipientProfile(
    # High extraversion, high care/harm, high social proof sensitivity
    # Responds to social proof, community, emotional storytelling
    openness=0.6,
    conscientiousness=0.4,
    extraversion=0.85,
    agreeableness=0.8,
    neuroticism=0.5,
    care_harm=0.8,
    fairness_cheating=0.6,
    loyalty_betrayal=0.6,
    authority_subversion=0.4,
    sanctity_degradation=0.4,
    liberty_oppression=0.4,
    economic_ideology=-0.1,
    social_ideology=-0.1,
    prior_belief=0.5,
    involvement=0.6,
    elaboration_likelihood=0.35,
)

SKEPTICAL_RESEARCHER = RecipientProfile(
    # High openness, high EL, low agreeableness, high agency sensitivity
    # Responds to evidence, resists emotional appeals and pressure tactics
    openness=0.85,
    conscientiousness=0.7,
    extraversion=0.4,
    agreeableness=0.3,
    neuroticism=0.3,
    care_harm=0.5,
    fairness_cheating=0.7,
    loyalty_betrayal=0.3,
    authority_subversion=0.3,
    sanctity_degradation=0.3,
    liberty_oppression=0.85,
    economic_ideology=0.0,
    social_ideology=-0.3,
    prior_belief=0.3,
    involvement=0.8,
    elaboration_likelihood=0.9,
)


# ═══════════════════════════════════════════════════════════════════════════════
# POLITICS/PR PERSONAS
# ═══════════════════════════════════════════════════════════════════════════════

LIBERAL_BASE = RecipientProfile(
    # High care/fairness, low loyalty/authority/sanctity, economic left
    openness=0.8,
    conscientiousness=0.5,
    extraversion=0.5,
    agreeableness=0.7,
    neuroticism=0.5,
    care_harm=0.9,
    fairness_cheating=0.85,
    loyalty_betrayal=0.3,
    authority_subversion=0.2,
    sanctity_degradation=0.2,
    liberty_oppression=0.7,
    economic_ideology=-0.7,
    social_ideology=-0.6,
    prior_belief=0.7,
    involvement=0.7,
    elaboration_likelihood=0.6,
)

CONSERVATIVE_BASE = RecipientProfile(
    # Balanced MFT, high loyalty/authority/sanctity, economic right
    openness=0.3,
    conscientiousness=0.7,
    extraversion=0.5,
    agreeableness=0.5,
    neuroticism=0.5,
    care_harm=0.5,
    fairness_cheating=0.5,
    loyalty_betrayal=0.8,
    authority_subversion=0.8,
    sanctity_degradation=0.8,
    liberty_oppression=0.5,
    economic_ideology=0.7,
    social_ideology=0.6,
    prior_belief=0.7,
    involvement=0.7,
    elaboration_likelihood=0.5,
)

PERSUADABLE_MODERATE = RecipientProfile(
    # Moderate everything, high involvement, medium EL
    openness=0.5,
    conscientiousness=0.5,
    extraversion=0.5,
    agreeableness=0.5,
    neuroticism=0.5,
    care_harm=0.5,
    fairness_cheating=0.5,
    loyalty_betrayal=0.5,
    authority_subversion=0.5,
    sanctity_degradation=0.5,
    liberty_oppression=0.5,
    economic_ideology=0.0,
    social_ideology=0.0,
    prior_belief=0.5,
    involvement=0.75,
    elaboration_likelihood=0.5,
)

DISENGAGED_VOTER = RecipientProfile(
    # Low involvement, low EL, low prior belief, peripheral processing
    openness=0.4,
    conscientiousness=0.3,
    extraversion=0.4,
    agreeableness=0.5,
    neuroticism=0.4,
    care_harm=0.4,
    fairness_cheating=0.4,
    loyalty_betrayal=0.4,
    authority_subversion=0.4,
    sanctity_degradation=0.4,
    liberty_oppression=0.4,
    economic_ideology=0.0,
    social_ideology=0.0,
    prior_belief=0.2,
    involvement=0.15,
    elaboration_likelihood=0.2,
)

ISSUE_ACTIVIST = RecipientProfile(
    # Very high involvement, very high moral conviction, high EL, high prior belief
    openness=0.7,
    conscientiousness=0.7,
    extraversion=0.7,
    agreeableness=0.4,
    neuroticism=0.6,
    care_harm=0.9,
    fairness_cheating=0.9,
    loyalty_betrayal=0.7,
    authority_subversion=0.5,
    sanctity_degradation=0.6,
    liberty_oppression=0.9,
    economic_ideology=-0.3,
    social_ideology=-0.4,
    prior_belief=0.9,
    involvement=0.95,
    elaboration_likelihood=0.85,
)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY — All presets accessible by name
# ═══════════════════════════════════════════════════════════════════════════════

PRESET_PERSONAS = {
    "impulse_buyer": IMPULSE_BUYER,
    "price_hunter": PRICE_HUNTER,
    "brand_loyalist": BRAND_LOYALIST,
    "social_shopper": SOCIAL_SHOPPER,
    "skeptical_researcher": SKEPTICAL_RESEARCHER,
    "liberal_base": LIBERAL_BASE,
    "conservative_base": CONSERVATIVE_BASE,
    "persuadable_moderate": PERSUADABLE_MODERATE,
    "disengaged_voter": DISENGAGED_VOTER,
    "issue_activist": ISSUE_ACTIVIST,
}


def get_persona(name: str) -> RecipientProfile:
    """Get a preset persona by name. Raises KeyError if not found."""
    return PRESET_PERSONAS[name]


def list_personas() -> list:
    """List all available preset persona names."""
    return list(PRESET_PERSONAS.keys())
