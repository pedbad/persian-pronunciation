# Handover — Persian Pronunciation Project
*(Paste this whole document as the first message of the new session.)*

You are picking up an in-progress project. Read this fully, then open the documents listed below before doing anything else.

## Who you're working with

Pedram (pb357@cam.ac.uk, GitHub: **pedbad**), on macOS. Working style is non-negotiable: **baby steps**. One step at a time, explain what a command does *before* running it, verify every step with its check, show the output, and never continue past a failed check. Ask rather than assume.

## The project

A Persian pronunciation-scoring app: a learner records a word, the engine compares it vowel-by-vowel against a native speaker (Persian script hides its short vowels — the core learning problem), and returns colour-coded per-vowel feedback with hints. Target: a pilot with Cambridge Language Centre CULP Persian learners in Michaelmas term 2026. Engine: Montreal Forced Aligner + Whisper gatekeeper + MFCC/DTW scorer, in Docker. Web app: Django 5 built on Pedram's own scaffold [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) (Tailwind v4, ShadCN-Django cotton components, auth + invite emails + CSV student seeding already built and tested).

## The documents (in the connected folder; later in the repo's `docs/`)

- **`DECISIONS.md`** — AUTHORITATIVE. Nine agreed decisions, D1–D9, with rationale. Where any document conflicts, this wins. New decisions are added as dated entries — never rewrite history.
- **`BUILD_PLAN.md`** — THE EXECUTION DOCUMENT. 35 steps in 6 parts, each with Goal / Do / ✅ Check / If-it-fails, plus a master checklist. All work happens here, starting at Step 1.
- **`FABLE_REVIEW.md`** — the strategy and the "why": phases, checkpoints, contingencies, pilot plan.
- **`README.md`** — must always contain working build/run instructions (the D1 rule).
- **`prototype/`** — historical design docs with decision banners at the top; the aeneas-based sections are superseded — never implement them.
- **`memory/JOURNAL.md`** — THE PROJECT'S MEMORY. Append-only session log, synced across Pedram's machines via the repo. Read the latest entry at every session start; append an entry at every session end.
- **`memory/RESEARCH_LOG.md`** — raw material for a future paper/poster for language-teaching venues. Append dated notes whenever something publication-worthy happens.
- **`emails/`** — draft correspondence (tutor meeting, DPIA/ethics). Local only — do **not** copy into the public repo.

## Decisions in force (summary — full text in DECISIONS.md)

**D1** Docker for the fragile audio stack from the first build; README always rebuilds everything (amended: Django runs natively in dev via the scaffold's `npm run dev`; engine, worker, Postgres, Redis run in compose). **D2** aeneas is NEVER installed — Montreal Forced Aligner from day one; wav2vec2 is the contingency (FABLE_REVIEW Phase 3). **D3** Whisper's only job is the wrong-word gatekeeper. **D4** score = 60% acoustic + 40% timing, one constant, one place, frozen until teacher calibration. **D5** server-rendered Django templates + cotton components — no React. **D6** everything runs on Pedram's laptop until pilot prep. **D7** public repo `github.com/pedbad/persian-pronunciation`, created by cloning the langcen_base scaffold, which stays connected as a `scaffold` remote. **D8** learner accounts via the scaffold's invite-email flow (admin-created / CSV-seeded); no open signup. **D9** (7 Aug 2026) two native references per lesson, stored as `NativeReference` rows — the scorer scores against both and keeps the better result (never scoring a clip against itself); the practice page plays the winning voice.

## Current state

Documentation complete; **zero code written**. Next action: **BUILD_PLAN.md Step 1** (Part A, system checks). The repo folder `~/Sites/persian-pronunciation` does not exist yet — it is created at Step 11 by cloning the scaffold. The old `~/Sites/persian` folder is the docs source and becomes a deletable backup after Step 13's push is verified.

## Skills already installed — use them at the right moments

- **engineering:architecture** — whenever a new design decision comes up (record the outcome as a dated entry in DECISIONS.md)
- **engineering:code-review** — before committing anything substantial (`align_mfa.py`, the scorer, the API endpoints)
- **engineering:debug** — when a ✅ Check fails and the fix isn't obvious
- **engineering:testing-strategy** — Step 28 (engine test suite) and Part F coverage
- **engineering:documentation** — README updates at every phase boundary; runbook later
- **engineering:system-design** — Part F wiring decisions (compose topology, task lifecycle)
- **engineering:deploy-checklist** — Phase 6 / hosting preparation
- **design:accessibility-review** — Step 34, the practice page (never colour alone; keyboard operation; screen-reader results list)
- **design:ux-copy** — gate error messages, vowel hints, consent screen wording
- **design:user-research** and **design:research-synthesis** — the think-aloud sessions and pilot feedback (FABLE_REVIEW Phase 6)
- **design:design-critique** — practice page review before the pilot
- **docx / pptx / xlsx / pdf** — deliverables (tutor-meeting one-pager, score-matrix tables, pilot write-up)
- **schedule** — recurring reminders if Pedram asks for them

## How to work — the baby-step protocol (non-negotiable)

1. **Session start:** read `DECISIONS.md`, `BUILD_PLAN.md`, and the latest entry in `memory/JOURNAL.md` (it says where we left off and what's next). Once the repo exists, `git pull` first — Pedram works on multiple machines and Claude seats, but runs **one session at a time**: every session ends with a push, every session starts with a pull. Model guidance: Sonnet suffices for the recipe-following parts (A–D); Opus for the engine code (Parts E–F); the protocol and checks, not the model, are what keep the build safe.
2. **One command at a time.** Work strictly in BUILD_PLAN order, starting at the step the journal names (Step 1 if no journal entry says otherwise). Within a step: explain in plain terms what the next command does and why → run it → run its ✅ Check → show Pedram the output → **stop and wait for his explicit go-ahead** before the next command. Never run several commands in one go unless Pedram says "batch".
3. **Never continue past a failed check.** Stop, explain what failed in plain terms, propose the fix, get agreement, retry. The BUILD_PLAN's "If it fails" notes are first aid.
4. Tick the master checklist in BUILD_PLAN.md as steps complete; commit documentation updates along with code.
5. Update README.md at every phase boundary — the D1 rule: anyone must be able to rebuild the project from the README alone.
6. Any deviation from the plan → dated entry in DECISIONS.md first, then proceed.
7. **Session end** (or whenever Pedram says "wrap up"): append a dated entry to `memory/JOURNAL.md` — what was done, which checks passed/failed, open threads, and the exact next BUILD_PLAN step — then commit and push (once the repo exists) so his other machines pick it up.
8. **Research log:** whenever something publication-worthy happens — a design rationale, an evaluation number (boundary table, score matrix), a surprising failure, a calibration result — append a dated note to `memory/RESEARCH_LOG.md` in the same commit. Pedram intends to publish this work for language-teaching audiences; the log is the paper's raw material.
9. **Public-repo hygiene:** the repo is public. No secrets, no student data, nothing personal in the journal or anywhere else; secrets live in `.env` (git-ignored); the `emails/` folder stays out of the repo.
