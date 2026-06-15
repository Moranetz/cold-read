from __future__ import annotations
"""
Somatic Marker Store — Damasio's Hypothesis as Computable Layer
================================================================
Implements the somatic marker hypothesis (Damasio, 1994) as a persistent
key-value store that biases future decisions based on past emotional outcomes.

The vmPFC retrieves body-state associations from similar past experiences
and uses them to bias approach/avoidance before conscious deliberation.

Two pathways modeled:
    - Body loop: actual physiological change (stronger, slower)
    - As-if body loop: simulated body-state (weaker, faster)

Based on:
    - Damasio (1994) Descartes' Error
    - Bechara et al. (1997) Iowa Gambling Task
    - Nader et al. (2000) Memory reconsolidation
"""

import json
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class SomaticMarker:
    """A stored body-state association for a stimulus context."""
    context_key: str
    valence: float          # -1.0 (strongly aversive) to 1.0 (strongly rewarding)
    intensity: float        # 0.0 (barely perceptible) to 1.0 (overwhelming)
    source: str             # "direct" (body loop) or "vicarious" (as-if / social proof)
    timestamp: float        # unix timestamp of encoding
    reinforcement_count: int = 1  # how many times this marker has been reactivated

    @property
    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600

    @property
    def effective_strength(self) -> float:
        """Strength after temporal decay and reinforcement.

        Decay: markers weaken over time (half-life ~30 days).
        Reinforcement: each reactivation strengthens the marker.
        Source: direct experience markers are 2x stronger than vicarious.
        """
        half_life_hours = 720  # ~30 days
        decay = 0.5 ** (self.age_hours / half_life_hours)
        source_weight = 1.0 if self.source == "direct" else 0.5
        reinforcement_bonus = min(2.0, 1.0 + 0.15 * (self.reinforcement_count - 1))
        return round(self.intensity * decay * source_weight * reinforcement_bonus, 4)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["effective_strength"] = self.effective_strength
        d["age_hours"] = round(self.age_hours, 1)
        return d


class SomaticMarkerStore:
    """Persistent store of somatic markers.

    Maps context keys (brand, pattern type, stimulus hash) to emotional outcomes.
    The vmPFC retrieves these during Stage 5 of the limbic cascade to bias
    the current decision toward approach or avoidance.
    """

    def __init__(self, store_path: Optional[str] = None):
        if store_path:
            self.path = Path(store_path)
        else:
            self.path = Path.home() / ".persuasion-max" / "somatic_markers.json"
        self.markers: dict[str, SomaticMarker] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            for key, data in raw.items():
                self.markers[key] = SomaticMarker(**data)

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = {k: asdict(v) for k, v in self.markers.items()}
        self.path.write_text(json.dumps(raw, indent=2))

    @staticmethod
    def make_key(context: str) -> str:
        """Generate a stable key from context string."""
        return hashlib.sha256(context.lower().strip().encode()).hexdigest()[:16]

    def encode(
        self,
        context: str,
        valence: float,
        intensity: float = 0.5,
        source: str = "direct",
    ) -> SomaticMarker:
        """Encode a new somatic marker or reinforce an existing one.

        This is what happens when a user has an experience:
        the vmPFC stores the body-state for future retrieval.
        """
        key = self.make_key(context)

        if key in self.markers:
            existing = self.markers[key]
            # Reconsolidation: reactivated markers can be modified
            # Weighted average biased toward new experience
            existing.valence = round(0.6 * valence + 0.4 * existing.valence, 4)
            existing.intensity = round(max(existing.intensity, intensity), 4)
            existing.reinforcement_count += 1
            existing.timestamp = time.time()
            self._save()
            return existing

        marker = SomaticMarker(
            context_key=key,
            valence=valence,
            intensity=intensity,
            source=source,
            timestamp=time.time(),
        )
        self.markers[key] = marker
        self._save()
        return marker

    def retrieve(self, context: str) -> Optional[SomaticMarker]:
        """Retrieve the somatic marker for a context.

        This is Stage 5 of the limbic cascade: the vmPFC checks
        whether a body-state association exists for this stimulus.
        """
        key = self.make_key(context)
        marker = self.markers.get(key)
        if marker and marker.effective_strength < 0.01:
            return None  # marker has decayed below threshold
        return marker

    def congruence_score(self, context: str) -> float:
        """Return somatic marker congruence for circuit prediction.

        Maps stored marker to 0-1 scale for the approach formula:
            0.0 = strongly aversive marker
            0.5 = no marker (neutral)
            1.0 = strongly rewarding marker
        """
        marker = self.retrieve(context)
        if marker is None:
            return 0.5  # no prior — neutral
        # Scale: valence (-1 to 1) * strength (0 to ~2) mapped to 0-1
        biased = 0.5 + 0.5 * marker.valence * marker.effective_strength
        return round(min(1.0, max(0.0, biased)), 4)

    def disgust_signal(self, context: str) -> float:
        """Return insula disgust signal for the avoidance formula.

        High when a strong negative marker exists — the insula detects
        that this stimulus pattern has previously been associated with
        agency violation or authenticity failure.
        """
        marker = self.retrieve(context)
        if marker is None or marker.valence >= 0:
            return 0.0
        return round(abs(marker.valence) * marker.effective_strength, 4)

    def prune_expired(self, min_strength: float = 0.01) -> int:
        """Remove markers that have decayed below threshold."""
        before = len(self.markers)
        self.markers = {
            k: v for k, v in self.markers.items()
            if v.effective_strength >= min_strength
        }
        pruned = before - len(self.markers)
        if pruned:
            self._save()
        return pruned

    def list_markers(self, limit: int = 20) -> list[dict]:
        """List strongest active markers."""
        sorted_markers = sorted(
            self.markers.values(),
            key=lambda m: m.effective_strength,
            reverse=True,
        )
        return [m.to_dict() for m in sorted_markers[:limit]]
