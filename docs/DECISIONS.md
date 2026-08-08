# DECISIONS.md — Project Decision Log

**Rule: where any other document in this project conflicts with this file, this file wins.**

How to change a decision: add a new dated entry underneath the old one — never rewrite history. If a change alters how attempts are scored, bump `scorer_version` (FABLE_REVIEW.md, Step 16) so old and new results stay distinguishable.

| # | Decision | Status |
|---|---|---|
| D1 | Docker **and a maintained README** from the very first build | ✅ Agreed 7 Jul 2026 |
| D2 | Skip aeneas entirely — Montreal Forced Aligner (MFA) from day one | ✅ Agreed 7 Jul 2026 |
| D3 | Whisper's only job is the gatekeeper (wrong-word check) | ✅ Agreed 7 Jul 2026 |
| D4 | Final score = 60% acoustic + 40% timing — one constant, defined once | ✅ Agreed 7 Jul 2026 |
| D5 | First interface is server-rendered Django templates — scaffold + cotton components, no React (see amendment) | ✅ Agreed 7 Jul 2026 |
| D6 | Runs on Pedram's laptop via `docker compose` until pilot prep | ✅ Agreed 7 Jul 2026 |
| D7 | Public GitHub repo, built from the `pedbad/langcen_base` scaffold (kept as a second remote) | ✅ Agreed 7 Jul 2026 |
| D8 | Learner accounts via the scaffold's invite-email flow (admin-created / CSV-seeded; no open signup) | ✅ Agreed 7 Jul 2026 |
| D9 | Two native references per lesson: score against both, keep the better result; `NativeReference` table; playback uses the winning voice | ✅ Agreed 7 Aug 2026 |
| D10 | uv is the Python toolchain: `pyproject.toml` + `uv.lock` are the source of truth, `.venv`, `requirements*.txt` retired | ✅ Agreed 8 Aug 2026 |
| D11 | Dependency version policy: track the Django 5.2 LTS line through the pilot; LTS→LTS to 6.2 afterwards; third-party bumps one at a time, gated on the test suite | ✅ Agreed 8 Aug 2026 |

---

## D1 — Docker and a README from the very first build

**What:** Every build of this project, starting with the very first one, happens inside Docker, and the README.md always contains working build-and-run instructions. The standing rule: anyone with Docker installed can rebuild the whole project from the README alone, at any point in its history.

**Why:** The pipeline depends on system tools and pinned versions that are painful to reproduce by hand. Docker freezes the working environment into a file. The README amendment (Pedram, 7 Jul 2026) closes the remaining gap: an image nobody knows how to build or run is as useless as no image.

**Consequences:** Slightly slower first setup (write the Dockerfile before running any code); in exchange, no "works on my machine" problems, a one-command handover to the Django developer, and a smooth path to university or cloud hosting later. Updating the README is part of "done" for every phase.

> **Amendment — 7 Jul 2026 (after adopting the langcen_base scaffold, D7):** The fragile parts — scoring engine, worker, Postgres, Redis — always run in Docker. The Django app itself runs *natively* during development (the scaffold's `npm run dev` flow: venv + Tailwind watcher + browser reload), because that is the workflow the scaffold is built and tested for. The D1 promise is kept by the fresh-clone test (BUILD_PLAN.md Step 35): the README alone must rebuild the entire stack on any machine. Full containerisation of the web app happens at deployment prep (Phase 6).

---

## D2 — Skip aeneas entirely: Montreal Forced Aligner from day one

**What:** aeneas — the alignment tool all four original brainstorming documents were written around — will never be installed. The alignment layer (the tool that finds *where* each sound sits in a recording) is the Montreal Forced Aligner from the first line of pipeline code. A neural fallback (wav2vec2 forced alignment) is held in reserve if MFA's Persian coverage disappoints (FABLE_REVIEW.md, Phase 3).

**Why — three independent reasons, any one of which would justify the switch:**

1. **Licence.** aeneas is AGPL-3. In plain terms: if the platform ever sells access to the scoring engine — the exact business model in the multilingual platform document — AGPL legally requires publishing all of our source code. MFA is MIT-licensed: free for any use, commercial included.
2. **Abandonment.** aeneas's last release was March 2017. The Python 3.10 pin, the numpy 1.23.5 pin, and the espeak installation battles in the tutorial existed *only* to keep it alive, and get worse every year. MFA is actively maintained. Dropping aeneas deletes all of those workarounds.
3. **Linguistic soundness.** aeneas would have aligned single romanised characters ("s", "l", "â") using a speech synthesiser — a fragile trick. MFA aligns real *phonemes* using a trained Persian acoustic model and pronunciation dictionary, which is the standard method in phonetics research.

**Consequences:** We write one new bridge script, `align_mfa.py` (2–3 evenings), and lose the ready-made aeneas scripts in the tutorial and handover docs — their alignment sections are now historical reading only. Everything else survives: the scorer, the vowel_map rules, the JSON output contract. One design improvement falls out for free: target vowels are located by matching their `phoneme` (a real sound) instead of a character position, with `position` retained as a lesson-data validation check. Boundary accuracy against the hand-labelled ground truth (FABLE_REVIEW.md, Step 9) remains the acceptance test — MFA must earn its place with numbers, same as anything else.

---

## D3 — Whisper is the gatekeeper, nothing else

**What:** Before any attempt is scored, Whisper transcribes what the learner actually said. If it doesn't match the expected word, the attempt is rejected with a friendly "It sounds like you said something different — listen to the native recording and try again", and **nothing is scored**. Whisper's output is used for nothing else.

**Why:** Forced alignment *forces* the expected word onto whatever audio arrives — say "merci" instead of "salâm", or record silence, and the original pipeline would still return a confident colour-coded score for a word never spoken. That's the worst failure a learning tool can have: it teaches something false. The review also found the original design's scoring script never used Whisper's output at all — this decision converts dead weight into insurance. Division of labour: Whisper judges **what** was said; the aligner and scorer judge **how well**. A single wrong vowel still passes the gate — catching that is the scorer's job.

**Consequences:** ~1–3 seconds extra per attempt (hidden inside the background worker's "analysing…" state) and a ~1.5 GB model in the worker Docker image. Accepted as cheap insurance.

> **Amendment — 7 Aug 2026:** The gate's acceptance test cuts both ways. It must catch wrong words **and** must not reject correct attempts: Whisper is at its least reliable on sub-second single-word clips (hallucination, Arabic-flavoured spellings, orthographic variants), and a gate that wrongly tells a learner "you said something different" is as damaging as scoring the wrong word. The done-checks (FABLE_REVIEW Step 14 / BUILD_PLAN Step 27) therefore include a false-rejection test: every correct-word clip in the test kit must pass the gate.

---

## D4 — Score weighting: 60% acoustic, 40% timing

**What:** `final_score = 0.60 × acoustic_score + 0.40 × timing_score`. This constant is defined in exactly one place in the code, stamped into every result via `scorer_version`, and does not change until real Persian teachers rate real attempts in the Phase 6 calibration study.

**Why:** The tutorial said 65/35, the handover said 60/40. The exact split matters far less than there being one number in one place — two documents with two values is how a developer and a founder end up silently running different scorers. 60/40 (the handover's value) reflects that how the vowel *sounds* matters more than its rhythm, while timing still counts.

**Consequences:** Any future tuning is a deliberate, versioned, evidence-based change rather than a copy-paste accident.

---

## D5 — First interface: one plain HTML + JavaScript page

**What:** Version one of the learner interface is a single page served by Django — no React, no build tooling. React is reconsidered only after the pilot validates the design.

**Why:** Weeks faster to a working demo; Pedram can read and tweak every line; design mistakes cost an afternoon, not a sprint. The interaction loop (listen → record → wait → coloured result → tap a vowel to compare) is unvalidated — validating it cheaply comes first.

**Consequences:** If the pilot succeeds, some frontend code is rewritten in React later — from a design that is by then known to work. That rewrite is the good outcome.

> **Amendment — 7 Jul 2026:** "Plain page" is now concretely the langcen_base scaffold's stack: Django templates + Tailwind v4 + ShadCN-Django components (rendered by django-cotton, with Alpine.js). Still server-rendered, still no React — the spirit of D5 is unchanged, the page just looks professional from day one.

---

## D6 — Runs on the laptop until pilot prep

**What:** The whole stack runs locally via `docker compose up`. No hosting, no server, nothing exposed to the internet, until Phase 6 pilot preparation — at which point hosting is discussed with the Language Centre.

**Why:** There is nothing worth hosting, securing, or paying for until there's a working demo — and because of D1, moving later is trivial: same containers, different machine.

**Consequences:** Demos run from Pedram's laptop. The university IT / hosting conversation is deferred to when a demo exists to justify it.

---

## D7 — Public GitHub repo, built from the langcen_base scaffold

**What:** The project lives at `github.com/pedbad/persian-pronunciation` (public), created by cloning [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) — Pedram's own Django 5 + Tailwind v4 + ShadCN-Django starter — and keeping it connected as a second git remote named `scaffold`.

**Why:** The scaffold already provides, tested, what the plan would otherwise build by hand: custom user model with student/teacher/admin roles, full auth flows, invite-on-create emails, CSV student seeding, pre-commit hooks (Black + Ruff), a 17-test pytest suite, Unfold admin, and the component UI. Public because it costs nothing, backs the work off the laptop, adds research credibility, and both the scaffold and this project are MIT anyway. The `scaffold` remote means future scaffold improvements can be merged in (`git fetch scaffold && git merge scaffold/main`).

**Consequences:** GitHub SSH authentication becomes a build prerequisite (BUILD_PLAN Part B). Anything secret must live in `.env` (git-ignored) from the first commit — the public repo makes secret hygiene non-negotiable. Learner audio and personal data never enter the repo.

---

## D8 — Learner accounts via the scaffold's invite-email flow

**What:** No open self-registration. Accounts are created by an admin (individually, or a whole cohort at once via the scaffold's `seed_students` CSV command); the scaffold then automatically emails each new learner a set-password link. This replaces the earlier "invite code + password" idea.

**Why:** Same pilot control (only people Pedram admits get in) with zero new code — the flow ships with the scaffold, is covered by its test suite, and CSV seeding maps exactly onto onboarding a CULP cohort from a class list. In development, emails are files in `tmp_emails/`, so the whole flow is testable offline (BUILD_PLAN Step 17).

**Consequences:** Pilot onboarding is: get class list → CSV → one command → learners receive set-password emails. Production needs a real SMTP backend (the scaffold README documents the `.env` switch). Raven/SSO remains deferred to Phase 6+ discussions.

---

## D9 — Dual native references: score against both, keep the better result

**What:** Every lesson carries at least two native reference recordings, modelled as `NativeReference` rows (lesson → many; each row holds the audio file, speaker sex, an optional dialect/register note, and cached per-vowel segment times) instead of a single file field on `Lesson`. The scorer scores each attempt against every active reference and keeps the **best** result; the payload records which reference won, and the practice page plays that winning voice for the listen button and the per-vowel comparison. In force from the first scorer version — `scorer_version` 0.1.0 is dual-reference from birth, so no retrofit bump is ever needed.

**Why:** MFCC+DTW against a single voice conflates pronunciation quality with voice identity (gap review §2.2) — a learner must never score worse because their vocal tract differs from the reference speaker's. Scoring against both natives and keeping the better result is the cheapest honest mitigation, and the data is already free: the test kit records native-A and native-B anyway (BUILD_PLAN Step 19). Best-of beats averaging, because averaging drags a good match to one voice down by the mismatch to the other — punishing exactly the case dual references exist to protect. Playing back the winning reference means the learner imitates the voice their score was actually measured against, which is also the voice closest to their own range.

**Consequences:** Roughly double the alignment/DTW compute per attempt (two single-word alignments — cheap; Step 32's latency measurement captures the real cost). The Phase 2 models change: `Lesson.native_reference_audio` becomes the `NativeReference` table (BUILD_PLAN Step 30); seeding attaches both recordings (Step 31); the payload gains the winning reference id and its segment times (Steps 32–34). FABLE_REVIEW Step 15's escalation (b) is now the default rather than a repair. Two guard rails: a clip used as test input is **never** scored against itself (when native-B is the input, native-B leaves the reference set), and Step 10's score matrix deliberately scores against native-A alone so the native-B killer test stays fair.

---

## D10 — uv as the Python toolchain (8 August 2026)

**What:** Python dependencies and the Python interpreter itself are managed by **uv** (Astral). Concretely:

- `pyproject.toml` — which already exists in this repository for Black and Ruff configuration — gains a `[project]` section holding the runtime dependencies and a `[dependency-groups] dev` group for the development tools.
- **`uv.lock` is committed to the repository** and is the authoritative record of exactly which packages, at which versions, with which file hashes, get installed. It includes transitive dependencies, which no `requirements.txt` in this project ever recorded.
- The virtual environment is **`.venv`** — uv's convention. `.gitignore` already covers both `.venv/` and `venv/`, so nothing needs changing there.
- `requirements.txt` and `requirements-dev.txt` are **deleted**, but only after the scaffold's test suite passes against the migrated environment (see Consequences).
- The interpreter is pinned by the existing `.python-version` (3.13.3) and provisioned by uv, so every machine and every container runs the same Python.
- `package.json`'s `dev` script changes from `python src/manage.py runserver` to `uv run python src/manage.py runserver`.
- Setting up any machine becomes one command: **`uv sync`**.

**Why — four reasons, in order of importance to this project:**

1. **It makes D1 true rather than aspirational.** D1 promises that anyone can rebuild this project at any point in its history. `pip install -r requirements.txt` cannot deliver that here: the development requirements were entirely unpinned, transitive dependencies were unrecorded, and the same file installs different software each year. A lockfile records every package, direct and transitive, at an exact version with a hash — so a rebuild either reproduces the environment precisely or fails loudly. For a project whose output is a paper, "here is the exact environment that produced these numbers" is a methods asset, not a convenience.
2. **It closes a gap already flagged in the journal.** `Dockerfile.engine` (BUILD_PLAN Step 21) pins nothing — `pip install openai-whisper librosa …` installs whatever is newest on the day. The same lock discipline applies inside the engine image, and the engine is precisely where reproducibility matters most, because the boundary and score numbers reported in the paper come out of it.
3. **It enforces an interpreter pin that was previously decorative.** `.python-version` says 3.13.3 and nothing enforced it; the two machines had already drifted (abacus 3.13.3, neo 3.13.15). uv reads that file and provisions the exact interpreter everywhere, including in containers.
4. **It consolidates on tooling already in use.** Ruff — from the same authors — already runs in this repository's pre-commit hooks.

**Consequences:**

- **A deliberate divergence from the scaffold.** `langcen_base` (D7) stays pip-based. Code merges from the `scaffold` remote continue to work normally; *dependency files* will conflict and must be reconciled by hand. This is accepted: the scaffold has served its purpose and this application is expected to evolve away from it. The `scaffold` remote stays connected regardless — it costs nothing.
- **One rule, never broken:** `uv.lock` is generated, never hand-edited. Dependencies change through `uv add` / `uv remove`, which update `pyproject.toml` and the lock together.
- **The migration has an acceptance test.** The scaffold's 17-test pytest suite (BUILD_PLAN Step 15) is run immediately after the switch. Green means the translation from requirements files into `pyproject.toml` was faithful. Only then are `requirements.txt` and `requirements-dev.txt` deleted, so there is never a period in which two sources of truth coexist unnoticed.
- **`npm run dev` gains a failure mode fewer.** Because the script now calls `uv run`, it finds `.venv` without activation. The old "`(venv)` must show in your prompt" trap disappears.
- **Documents updated in the same commit:** BUILD_PLAN (a new Part A step installing uv; Step 14 rewritten; Steps 21 and 35 adjusted), `memory/SETUP_LOG.md`, `README.md`, `CLAUDE.md`. Superseded wording in the D1 amendment and in older JOURNAL entries is **left as written** — this log never rewrites history, and D10 supersedes it.
- **No `scorer_version` impact.** This changes how the environment is built, not how attempts are scored.
- **The second machine needs no cleanup.** Part C had not been run on any machine when this was decided, so no virtual environment or installed packages existed anywhere to migrate. MacBook "neo" picks this up by pulling the repository and following the rewritten Step 14.

---

## D11 — Dependency version policy: the Django 5.2 LTS line through the pilot (8 August 2026)

**What:** The project tracks **Django's 5.2 LTS line** through the Michaelmas 2026 pilot and the calibration study that follows it. `pyproject.toml` states the intent as `>=5.2,<5.3`; `uv.lock` records the exact patch release actually used. Security patches within the line are adopted deliberately, by an explicit `uv lock --upgrade-package django`, not silently at install time. The next planned Django move is **LTS to LTS — 5.2 to 6.2** — after the pilot, when 6.2 is released (expected April 2027). Third-party dependencies are bumped **one at a time**, each bump gated on the scaffold's pytest suite passing, and never in the same change as a toolchain or framework migration.

Versions observed on PyPI on 8 August 2026, when this decision was taken:

| Package | Pinned here | Latest available |
|---|---|---|
| Django | 5.2.17 (via the 5.2 LTS line) | 6.1, released 5 Aug 2026 |
| django-cotton | 2.1.3 | 2.7.2 |
| django-unfold | 0.67.0 | 0.103.0 |
| django-import-export | 4.3.10 | 4.4.1 |
| python-dotenv | 1.1.1 | 1.2.2 |

**Why:**

1. **5.2 is LTS, with security support until April 2028** — comfortably past the pilot, the calibration study, and writing up.
2. **Django 6.1 was three days old when this was decided, and is a feature release.** Its mainstream support ends when 6.2 arrives (~April 2027), so adopting it would force an upgrade *during or immediately after* the pilot term. Django's designed upgrade path is LTS to LTS; 6.1 as a stepping stone buys nothing and costs a migration.
3. **Third-party compatibility is unproven, not proven.** `django-cotton` and `django-unfold` are small projects, and the scaffold's UI sits directly on both. Three days after a Django major release, "works with 6.1" means untested. The worst possible time to discover otherwise is week three of term.
4. **A research artefact benefits from a stated, stable environment.** The environment is something the paper reports; changing it mid-study costs more than the features gained.

**Consequences:**

- **This repository knowingly runs a Django that is not the newest.** That is deliberate and now recorded, so nobody — including a future developer or a reviewer — reads it as neglect.
- **Every Django security-release day requires a decision, not a reflex.** One reviewable command inside the 5.2 line; cheap, and visible in the lockfile diff.
- **`django-unfold` 0.67 → 0.103 is its own future step.** Unfold moves quickly and has changed admin templates between minor versions, and the scaffold's admin theming depends on it directly.
- **The 6.2 upgrade belongs to Phase 6 planning or later**, after the pilot has produced its evidence.
- **No `scorer_version` impact.** No scoring behaviour changes here.
