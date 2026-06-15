# Cold Read

A scoring instrument for cold outbound. Paste a message; it returns how five
buyer archetypes are predicted to react, which persuasion mechanics the copy
actually fires, and the single change that moves the most replies.

It runs on the [Persuasion-Max](https://github.com/Moranetz/Persuasion-Max)
engine — offline, deterministic, no API key.

## The premise

Most outbound tooling personalizes the merge fields: the name, the company,
the recent funding round. It treats persuasion as a delivery problem.

Cold Read starts somewhere else. The same sentence does not land the same way
on a procurement lead and an internal champion — not because of the merge
fields, but because each reads it through a different appraisal profile:
novelty, relevance, coping potential, agency, certainty, urgency. The engine
scores a message against those profiles and shows you where they diverge.

Where the bars diverge is where targeting beats volume.

## What it separates

Three things most "AI email graders" collapse into one number, kept apart on
purpose:

- **Recipient fit** — predicted reply, follow-up receptiveness, and annoyance
  risk for each of five buyer archetypes (champion, evaluator, economic buyer,
  incumbent user, consensus buyer).
- **Mechanics** — which persuasion techniques the copy is firing, at what
  intensity, across tactical, psychological, and linguistic layers.
- **Leverage** — the one appraisal dimension whose change is predicted to move
  reply the most, and by how much.

## What the numbers are — and are not

The figures are **model-internal**: the engine maps a message to each
archetype's appraisal profile and predicts a behavioral response. They are
directional — built for comparing how one message lands across buyers and for
finding the highest-leverage edit. They are **not** measured reply rates and
not a forecast of a real campaign.

The engine's calibration is documented upstream: within-corpus AUC 0.63–0.67
(5-fold CV), 302 provenance-labeled weights, a 126K-sample evaluation across
two corpora.

## Run it

```bash
python serve.py        # http://localhost:8000  — needs only numpy
```

No keys, no network. The engine's heuristic path is regex + numpy; the
adapter in `api/engine_adapter.py` is the only translation layer between the
research vocabulary and the sales surface. The engine itself is vendored
unmodified under `engine/core` — see `engine/PROVENANCE.md`.

---

Built by Marion Moranetz · San Francisco
