# Copy-paste starter prompt for Claude Code

*(Two versions below: one for a machine that already has the project, one for a machine starting from nothing. `CLAUDE.md` in the repository root loads the working protocol automatically, so the prompt mainly sets the session's ground rules and points at the journal.)*

**Where to run it:** Claude desktop app → Code tab → environment **Local** → folder `~/Sites/persian` → permission mode **Manual** → paste the prompt as the first message.

**Model choice** (the dropdown next to the send button, changeable mid-session): Sonnet is enough for the mechanical parts (BUILD_PLAN Parts A–D: installs, git, scaffold, audio kit — a recipe with checks). Switch to Opus for the engine code (Part E, especially Step 24 `align_mfa.py`, and Part F wiring). Save Fable for genuinely hard thinking.

**One Claude session at a time**, across all seats and machines. Every session starts with a pull and ends with a push.

---

## A — Machine that already has the project

```
Read CLAUDE.md in this folder now, in full, and follow it exactly — it defines who I am, the authoritative documents, and the non-negotiable baby-step protocol. Then read docs/DECISIONS.md, docs/BUILD_PLAN.md, and the LATEST entry in memory/JOURNAL.md, which says where we left off and the exact next step. Run git pull first.

Ground rules, repeated so there is no doubt:

1. Baby steps. One command at a time. Before each command: tell me in plain terms what it does and why. After each command: run its ✅ Check from BUILD_PLAN.md, show me the output, then STOP and wait for my explicit "ok" before doing anything else. Never batch commands unless I say the word "batch".
2. Never continue past a failed check. Stop, explain the failure simply, propose one fix, and wait for my agreement.
3. I work on multiple machines, one session at a time. Pull at the start of every session, push at the end. memory/JOURNAL.md is our shared memory: read its last entry to know where we are, and at the end of every session append a dated entry (what was done, checks passed/failed, exact next step), then commit and push it.
4. memory/RESEARCH_LOG.md collects material for a future paper for language-teaching venues. When we produce anything publication-worthy — a design rationale, an evaluation number, an honest failure — append a dated note in the same commit.
5. memory/SETUP_LOG.md is the plain-English record of what is installed and why. Append a section whenever a BUILD_PLAN Part completes.
6. The repo is public: no secrets, no personal data, ever. Commit messages carry no Co-Authored-By trailer. Run git status as its own command before any commit — never chain it into the commit — and tell me what is about to be staged.
7. Some material lives OUTSIDE the repo and does not sync between machines: ~/Sites/persian-private/ holds draft correspondence (emails/) and the native-speaker recording materials, including speaker identities and consent records. It exists only on the MacBook "neo". Never copy it into the repository, and never assume it is present.

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
3. Then read the documents named above, plus memory/SETUP_LOG.md, which lists every developer tool the project needs and the exact versions verified on my other Mac.
4. Check which of those tools this machine is missing, tell me the list before installing anything, and install them one at a time with BUILD_PLAN Part A's checks. Docker Desktop needs my admin password — you cannot install it yourself, so hand me that command to run.

Ground rules, repeated so there is no doubt:

1. Baby steps. One command at a time. Before each command: tell me in plain terms what it does and why. After each command: run its ✅ Check from BUILD_PLAN.md, show me the output, then STOP and wait for my explicit "ok" before doing anything else. Never batch commands unless I say the word "batch".
2. Never continue past a failed check. Stop, explain the failure simply, propose one fix, and wait for my agreement.
3. I work on multiple machines, one session at a time. Pull at the start of every session, push at the end. memory/JOURNAL.md is our shared memory: read its last entry to know where we are, and at the end of every session append a dated entry (what was done, checks passed/failed, exact next step), then commit and push it.
4. memory/RESEARCH_LOG.md collects material for a future paper for language-teaching venues. When we produce anything publication-worthy — a design rationale, an evaluation number, an honest failure — append a dated note in the same commit.
5. memory/SETUP_LOG.md is the plain-English record of what is installed and why. Append a section whenever a BUILD_PLAN Part completes.
6. The repo is public: no secrets, no personal data, ever. Commit messages carry no Co-Authored-By trailer. Run git status as its own command before any commit — never chain it into the commit — and tell me what is about to be staged.
7. Some material lives OUTSIDE the repo and does not sync between machines: ~/Sites/persian-private/ holds draft correspondence (emails/) and the native-speaker recording materials, including speaker identities and consent records. It exists only on the MacBook "neo". Never copy it into the repository, and never assume it is present.

When you've read everything, tell me in two or three sentences where the project stands and what BUILD_PLAN step we start at — then begin that step, one baby step at a time.
```

---

## What a second machine will and will not have

**Arrives with the clone:** all code, `docs/` (decisions, build plan, strategy, prototype history), `memory/` (journal, research log, setup log), and `CLAUDE.md`.

**Does not arrive, and must be created locally:** the Python virtual environment (`venv/` is git-ignored and is tied to its own absolute path — never copy one between machines), `node_modules/`, the `.env` file (copy `.env.example` and set the values; `EMAIL_FILE_PATH` must point at that machine's own path), the database, and the Docker images.

**Never syncs at all:** `~/Sites/persian-private/` — draft correspondence, native-speaker recording materials, speaker identities and consent records. That folder exists on one machine deliberately. If it is ever needed elsewhere, move it by hand, and never through the repository.

**Tooling:** `memory/SETUP_LOG.md` lists every tool, why the project needs it, and the versions verified on the first machine. Work through BUILD_PLAN Part A on the new machine and check each one; most may already be present. Docker Desktop's installer requires an administrator password and must be run by hand in a terminal.
