# Persian Pronunciation Project

A tool that listens to a learner say a Persian word, compares it vowel-by-vowel against a native speaker, and shows exactly which of Persian's *hidden vowels* were pronounced well — starting as a prototype, aimed at a pilot with Cambridge Language Centre CULP Persian learners.

## Where to look

- **`docs/DECISIONS.md`** — the authoritative decision log. Where any other document conflicts with it, DECISIONS.md wins.
- **`docs/FABLE_REVIEW.md`** — the strategy: every step in order, with "done when" criteria.
- **`docs/BUILD_PLAN.md`** — the hands-on build manual: from empty Mac to working app, every command paired with a check. Start here when you sit down to build.
- **`docs/prototype/`** — the original brainstorming documents (tutorial, platform vision, handover, Phase 2 architecture) and the gap review. Note the decision banners at the top of each: the aeneas-based sections are historical.
- **`memory/`** — the project's working memory, synced across machines by this repo: `JOURNAL.md` (append-only session log — read the latest entry before starting work), `RESEARCH_LOG.md` (material for a future paper), and `SETUP_LOG.md` (a plain-English explanation of every tool the project installs, and why).
- **`CLAUDE.md`** — the working protocol, loaded automatically by Claude Code at the start of every session. A copy of `docs/HANDOVER.md`.
- **Scaffold** — this repository was created from [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) (Decision D7), which remains connected as a git remote named `scaffold` so future scaffold improvements can be merged in. Its own README is preserved at `docs/scaffold-readme.md`.

## How to build and run

*(Rule from Decision D1: this section must always work — anyone should be able to rebuild the project from the README alone. It gets updated at every phase.)*

**Current status:** BUILD_PLAN **Part A complete** (developer tooling installed and verified — see `memory/SETUP_LOG.md` for what and why); **Part B** in progress (this repository, created from the scaffold). No project code written yet — everything here is the scaffold plus the planning documents. When the engine image lands (BUILD_PLAN **Step 21**), this section will contain, verbatim:

```bash
docker build -f Dockerfile.engine -t persian-mfa .
docker run --rm persian-mfa mfa version
```

## Requirements

- Docker Desktop for the audio engine and services (the fragile stack needs only Docker, by design — D1), plus the scaffold's dev tools: Python 3.13 and Node/npm. BUILD_PLAN Part A checks and installs all of them.
