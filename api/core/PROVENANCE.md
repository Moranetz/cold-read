# Engine provenance

`engine/core/` is vendored **unmodified** from the Persuasion-Max research engine:
https://github.com/Moranetz/Persuasion-Max

Cold Read does not fork or alter the engine. It calls the engine's offline,
deterministic path (heuristic extraction → limbic cascade → circuit prediction
→ reframing) through a single adapter, `api/engine_adapter.py`, which is the
only translation layer between the research vocabulary and the outbound-sales
surface.

Nothing here requires an API key or network access. To update the engine,
re-vendor `core/` from the upstream repo; do not edit files in place.

## What the numbers mean (honesty note)

Predicted reply / follow-up / annoyance figures are **model-internal
appraisal-to-circuit scores**, not measured human response rates. They are
directional — useful for comparing how one message lands across buyer
archetypes, and for finding the highest-leverage edit — not a forecast of a
real campaign's reply rate. Upstream calibration (within-corpus AUC 0.63–0.67,
5-fold CV; 302 provenance-labeled weights; 126K-sample, 2-corpus evaluation)
is documented in the Persuasion-Max repo.
