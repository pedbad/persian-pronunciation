# Persian Pronunciation Project

A tool that listens to a learner say a Persian word, compares it vowel-by-vowel against a native speaker, and shows exactly which of Persian's *hidden vowels* were pronounced well — starting as a prototype, aimed at a pilot with Cambridge Language Centre CULP Persian learners.

## Where to look

- **`docs/DECISIONS.md`** — the authoritative decision log. Where any other document conflicts with it, DECISIONS.md wins.
- **`docs/FABLE_REVIEW.md`** — the strategy: every step in order, with "done when" criteria.
- **`docs/BUILD_PLAN.md`** — the hands-on build manual: from empty Mac to working app, every command paired with a check. Start here when you sit down to build.
- **`docs/prototype/`** — the original brainstorming documents (tutorial, platform vision, handover, Phase 2 architecture) and the gap review. Note the decision banners at the top of each: the aeneas-based sections are historical.
- **`memory/`** — the project's working memory, synced across machines by this repo: `JOURNAL.md` (append-only session log — read the latest entry before starting work), `RESEARCH_LOG.md` (material for a future paper), and `SETUP_LOG.md` (a plain-English explanation of every tool the project installs, and why).
- **`CLAUDE.md`** — the working protocol, loaded automatically by Claude Code at the start of every session. **This is the single source**; `docs/HANDOVER.md` is the superseded original, reduced to a pointer.
- **Scaffold** — this repository was created from [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) (Decision D7), which remains connected as a git remote named `scaffold` so future scaffold improvements can be merged in. Its own README is preserved at `docs/scaffold-readme.md`.

## How to build and run

*(Rule from Decision D1: this section must always work — anyone should be able to rebuild the project from the README alone. It gets updated at every phase.)*

**Current status:** BUILD_PLAN **Parts A, B and C complete** — developer tooling, the repository, and the web application running with both logins proven. The scoring engine (Parts D–F) is not built yet, so there is nothing to score with; what follows brings up the web application.

### Requirements

Install these once per machine — BUILD_PLAN Part A walks through each with a check, and `memory/SETUP_LOG.md` explains what every one of them is for:

| Tool | Why |
|---|---|
| **uv** | the Python toolchain (Decision D10) — creates the environment, installs the locked dependencies, and provisions the pinned interpreter itself. `brew install uv` |
| **Node + npm** | compiles the Tailwind stylesheet. Nothing else; no JavaScript ships to the browser |
| **Docker Desktop** | the audio engine and services, from Part E onwards. Not needed to run the web app |
| **ffmpeg** | converts all audio to 16 kHz mono WAV. Not needed to run the web app |

You do **not** need to install Python yourself. uv reads `.python-version` and provisions that exact interpreter — adopting a matching one if the machine already has it, downloading a standalone build if not.

### Bring the web application up

```bash
git clone git@github.com:pedbad/persian-pronunciation.git ~/Sites/persian
cd ~/Sites/persian
uv sync
cp .env.example .env
```

Then edit `.env` and set four values:

| Key | Value |
|---|---|
| `SECRET_KEY` | generate a fresh one **per machine** — never copy another machine's: `uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `EMAIL_FILE_PATH` | absolute path to `tmp_emails` inside your checkout, e.g. `/Users/ped/Sites/persian/tmp_emails` |
| `DEFAULT_FROM_EMAIL` | `no-reply@persian-pronunciation.local` |
| `SITE_NAME` | `Persian Pronunciation` |

In development, email is written to files rather than sent — `EMAIL_BACKEND` is already Django's filebased backend in `.env.example`, and `tmp_emails/` is created by the first send.

```bash
uv run python check_env.py
uv run python src/manage.py migrate
npm install
npm run dev
```

The app is at **http://127.0.0.1:8000**. `npm run dev` runs the Tailwind watcher and Django together — use it rather than `runserver` alone, or the page loads unstyled.

**On npm 11 and newer**, `npm install` warns that install scripts for `@tailwindcss/oxide` and `@parcel/watcher` are not approved. This is expected and needs no action: both ship prebuilt binaries as platform-specific optional dependencies, so the build works with the scripts left unapproved. Do **not** run `npm approve-scripts` to silence it — that grants exactly the permission npm supply-chain attacks rely on.

### Accounts

```bash
uv run python src/manage.py createsuperuser
```

For a whole cohort, seed from a CSV — this is the pilot onboarding path (Decision D8). Each learner is created **without** a password and receives a set-password invite:

```bash
uv run python src/manage.py seed_students data/sample_students.csv --dry-run
uv run python src/manage.py seed_students data/sample_students.csv
```

Do not pass `--default-password`: it gives each user a usable password, which suppresses every invite. See BUILD_PLAN Step 18.

Local demo fixtures (`admin@`, `teacher@`, `student@persian.local`) come from an idempotent command that refuses to run when `DEBUG=False`:

```bash
uv run python src/manage.py seed_demo_users --password='<choose one>'
```

### Tests and hooks

```bash
uv run pytest -q          # 17 tests, the scaffold's suite
pre-commit install        # per-clone: hooks live in .git/hooks and never travel
pre-commit run --all-files
```

### Regenerating the PWA icons

`pwa-asset-generator` is deliberately **not** a dependency (Decision D12) — it bundles a headless Chrome to support an operation performed perhaps twice in the project's life. The fourteen icons in `src/core/static/core/favicon/` are committed assets. When branding is next redone, run it once without installing it:

```bash
npx pwa-asset-generator <source-image> src/core/static/core/favicon/
```

### The scoring engine

Not built yet. When the engine image lands (BUILD_PLAN **Step 21**), this section will contain, verbatim:

```bash
docker build -f Dockerfile.engine -t persian-mfa .
docker run --rm persian-mfa mfa version
```
