# Copy-paste starter prompt for Claude Code

*(Two versions below: one for a machine that already has the project, one for a machine starting from nothing. `CLAUDE.md` in the repository root loads the working protocol automatically, so the prompt mainly sets the session's ground rules and points at the journal.)*

**Where to run it:** Claude desktop app → Code tab → environment **Local** → folder `~/Sites/persian` → permission mode **Manual** → paste the prompt as the first message.

**Model choice** (the dropdown next to the send button, changeable mid-session): Sonnet is enough for the mechanical parts (BUILD_PLAN Parts A–D: installs, git, scaffold, audio kit — a recipe with checks). Switch to Opus for the engine code (Part E, especially Step 24 `align_mfa.py`, and Part F wiring). Save Fable for genuinely hard thinking.

**One Claude session at a time**, across all seats and machines. Every session starts with a pull and ends with a push.

---

## Where the project stands — updated 9 August 2026

Keep this section current; it is what makes the prompt below specific rather than generic. The journal remains the authority.

- **BUILD_PLAN Parts A, B and C are complete**, on both machines. The web application runs, both logins are proven, the scaffold's 17 tests and eight pre-commit hooks are green, and the app is branded as this project rather than the scaffold.
- **Both machines are set up**: MacBook "neo" and MacBook "abacus". Neo additionally holds `~/Sites/persian-private/`, which never syncs.
- **The next step is Step 19 (Part D)** — the 12-clip test kit — followed by Step 20, hand-labelling vowel boundaries in Praat. Part D produces the project's *ruler*: nothing in Part E can be measured without it.
- **Part D is the first step that is not mechanical.** It needs real recordings, and `native_b` depends on the second native speaker (open since the start, load-bearing under D9). Those recordings are planned for a trip to Iran in mid-August 2026; the protocol, read sheets and speaker log live in `~/Sites/persian-private/native-recordings/`.
- **One question must be settled before any audio is committed.** BUILD_PLAN Steps 19–20 say to commit `audio/` to the repository, and the repository is **public**. The consent design records two separate permissions — use inside the application, and inclusion of the audio file in the public repo — and a speaker may grant the first while refusing the second. The plan does not yet encode that. This needs a dated `DECISIONS.md` entry (where non-public clips live, how the loader finds them, how the two are kept apart) **before** any recording is added to git, not after.

---

## A — Machine that already has the project

```
Read CLAUDE.md in this folder now, in full, and follow it exactly — it defines who I am, the authoritative documents, and the non-negotiable baby-step protocol. Then read docs/DECISIONS.md, docs/BUILD_PLAN.md, and the LATEST entry in memory/JOURNAL.md, which says where we left off and the exact next step. Run git pull first.

Ground rules, repeated so there is no doubt:

1. Baby steps. One command at a time. Before each command: tell me in plain terms what it does and why. After each command: run its ✅ Check from BUILD_PLAN.md, show me the output, then STOP and wait for my explicit "ok" before doing anything else. Never batch commands unless I say the word "batch".
2. Never continue past a failed check. Stop, explain the failure simply, propose one fix, and wait for my agreement.
3. I work on multiple machines, one session at a time. Pull at the start of every session, push at the end. memory/JOURNAL.md is our shared memory: read its last entry to know where we are, and at the end of every session append a dated entry (what was done, checks passed/failed, exact next step), then commit and push it.
4. memory/RESEARCH_LOG.md collects material for a future paper for language-teaching venues. When we produce anything publication-worthy — a design rationale, an evaluation number, an honest failure — append a dated note in the same commit.
5. memory/SETUP_LOG.md is the plain-English record of what is installed and why. Append a section whenever a BUILD_PLAN Part completes, and record anything that differs between my two machines.
6. The repo is public: no secrets, no personal data, ever. Commit messages carry no Co-Authored-By trailer. Run git status as its own command before any commit — never chain it into the commit — and tell me what is about to be staged.
7. Some material lives OUTSIDE the repo and does not sync between machines: ~/Sites/persian-private/ holds draft correspondence (emails/) and the native-speaker recording materials, including speaker identities and consent records. It exists only on the MacBook "neo". Never copy it into the repository, and never assume it is present.
8. The Python toolchain is uv (Decision D10). Every Python command takes a "uv run" prefix — uv run python src/manage.py …, uv run pytest -q. There is nothing to activate. Never create a venv by hand, never edit uv.lock, and add dependencies only with uv add. Under D11, dependency bumps happen one at a time, each gated on the 17-test suite, and never bundled into another change — that includes npm audit fix, which is forbidden.
9. If a documented ✅ Check does not pass, consider that the step itself may be wrong before assuming the machine is. That has now happened twice — Steps 17 and 18 both told me to do something that silently suppressed the thing they then asked me to verify. Fixing the document is part of the work.

When you've read everything, tell me in two or three sentences where the project stands and what BUILD_PLAN step we start at — then begin that step, one baby step at a time.
```

---

## B — Fresh machine, nothing installed

Open Claude Code with the folder set to `~/Sites` (the project folder does not exist yet), and paste:

```
Read CLAUDE.md in this folder now, in full, and follow it exactly — it defines who I am, the authoritative documents, and the non-negotiable baby-step protocol. Then read docs/DECISIONS.md, docs/BUILD_PLAN.md, and the LATEST entry in memory/JOURNAL.md, which says where we left off and the exact next step.

If this folder does not contain the project yet, this is a fresh machine. Do this first, one step at a time, checking each:

1. Confirm SSH access to GitHub: ssh -T git@github.com — expect "Hi pedbad!". If it fails, stop and walk me through BUILD_PLAN Part B Step 10 (SSH key) before anything else.
2. Clone into ~/Sites/persian (note: the local folder is "persian", the GitHub repo is "persian-pronunciation"):
   git clone git@github.com:pedbad/persian-pronunciation.git ~/Sites/persian
3. Check the remotes immediately: git remote -v. "origin" must be SSH (git@github.com:pedbad/persian-pronunciation.git), not HTTPS, and a second remote "scaffold" must point at git@github.com:pedbad/langcen_base.git. A clone taken from the web page gets neither right. Fix with git remote set-url / git remote add before doing anything else.
4. Then read the documents named above, plus memory/SETUP_LOG.md, which lists every developer tool the project needs and the exact versions verified on my other Macs.
5. Audit before installing: check which tools this machine is actually missing with a single read-only sweep of version strings, tell me the list before installing anything, then install them one at a time with BUILD_PLAN Part A's checks. Most are usually already present. Docker Desktop needs my admin password — you cannot install it yourself, so hand me that command to run.
6. Then follow BUILD_PLAN Step 14 to bring the app up: uv sync, cp .env.example .env (with a SECRET_KEY generated fresh for THIS machine — never copied from another), migrate, npm install, npm run dev.

Ground rules, repeated so there is no doubt:

1. Baby steps. One command at a time. Before each command: tell me in plain terms what it does and why. After each command: run its ✅ Check from BUILD_PLAN.md, show me the output, then STOP and wait for my explicit "ok" before doing anything else. Never batch commands unless I say the word "batch".
2. Never continue past a failed check. Stop, explain the failure simply, propose one fix, and wait for my agreement.
3. I work on multiple machines, one session at a time. Pull at the start of every session, push at the end. memory/JOURNAL.md is our shared memory: read its last entry to know where we are, and at the end of every session append a dated entry (what was done, checks passed/failed, exact next step), then commit and push it.
4. memory/RESEARCH_LOG.md collects material for a future paper for language-teaching venues. When we produce anything publication-worthy — a design rationale, an evaluation number, an honest failure — append a dated note in the same commit.
5. memory/SETUP_LOG.md is the plain-English record of what is installed and why. Append a section whenever a BUILD_PLAN Part completes, and record anything that differs between my machines.
6. The repo is public: no secrets, no personal data, ever. Commit messages carry no Co-Authored-By trailer. Run git status as its own command before any commit — never chain it into the commit — and tell me what is about to be staged.
7. Some material lives OUTSIDE the repo and does not sync between machines: ~/Sites/persian-private/ holds draft correspondence (emails/) and the native-speaker recording materials, including speaker identities and consent records. It exists only on the MacBook "neo". Never copy it into the repository, and never assume it is present.
8. The Python toolchain is uv (Decision D10). Every Python command takes a "uv run" prefix. There is nothing to activate. Never create a venv by hand, never edit uv.lock, and add dependencies only with uv add.

When you've read everything, tell me in two or three sentences where the project stands and what BUILD_PLAN step we start at — then begin that step, one baby step at a time.
```

---

## What a second machine will and will not have

**Arrives with the clone:** all code, `docs/` (decisions, build plan, strategy, prototype history), `memory/` (journal, research log, setup log), `CLAUDE.md`, `pyproject.toml` and `uv.lock`.

**Does not arrive, and must be created locally:**

| Thing | How |
|---|---|
| `.venv/` | `uv sync`. **Never copy one between machines** — it records its own absolute path, which is also why `~/Sites/persian` must never be renamed |
| `node_modules/` | `npm install` |
| `.env` | `cp .env.example .env`, then set `SECRET_KEY` (**generated fresh for that machine**), `EMAIL_FILE_PATH` (that machine's own absolute path), `DEFAULT_FROM_EMAIL`, `SITE_NAME` |
| the database | `uv run python src/manage.py migrate` |
| `passwords.txt` | git-ignored by design; recreate by hand, and confirm with `git check-ignore -v passwords.txt` first |
| a superuser | `uv run python src/manage.py createsuperuser` — interactive, so Pedram types it, never the assistant |
| Docker images | rebuilt per machine |

**Never syncs at all:** `~/Sites/persian-private/` — draft correspondence, native-speaker recording materials, speaker identities and consent records. That folder exists on one machine deliberately. If it is ever needed elsewhere, move it by hand, and never through the repository.

**Tooling:** `memory/SETUP_LOG.md` lists every tool, why the project needs it, and the versions verified per machine. Audit before installing — on abacus a single read-only sweep showed six of eight tools were already present. Docker Desktop's installer requires an administrator password and must be run by hand.

**Known machine differences**, recorded rather than pinned: neo runs node 24.19.0 / npm 11.17.0 and uv 0.12.2; abacus runs node 22.19.0 / npm 10.9.3 and uv 0.11.26. On npm 11 and newer, `npm install` warns that install scripts for `@tailwindcss/oxide` and `@parcel/watcher` are unapproved — expected, harmless, and **not** to be silenced with `npm approve-scripts`.
