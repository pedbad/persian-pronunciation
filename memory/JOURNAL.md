# JOURNAL — Session Log (append-only)

**What this is:** the project's memory across machines and Claude sessions. Every working session ends with a dated entry here: what was done, which checks passed or failed, open threads, and the exact next step. Every session *starts* by reading the latest entry.

**Sync rule:** once the GitHub repo exists (BUILD_PLAN Step 12), this folder lives in the repo — **pull at session start, commit + push this file at session end**. Until then it exists only on this machine.

**Public-repo rule:** the repo is public. Nothing sensitive goes in here — no passwords, no tokens, no student names or data. Secrets live in `.env` (git-ignored); people-data never enters the repo at all.

**Entry format:**

```
## YYYY-MM-DD — machine — short title
- Done: …
- Checks: passed/failed (which)
- Decisions/observations: … (real decisions go in DECISIONS.md; note the pointer here)
- Next step: BUILD_PLAN Step N
```

---

## 2026-08-07 — Pedram's Mac (Cowork session) — docs review, D9, corrections

- Done: Full review of all planning docs. Correction edits applied (boundary-tolerance rule ±50 ms *and* ≤30% of vowel duration; Whisper-gate false-rejection test; MFA `align_one`/latency notes; GOP optional column in Step 10; new Step 3b ethics/DPIA email; timeline revised). **D9 agreed and written**: two native references per lesson (`NativeReference` table), score against both, keep the better result, playback uses the winning voice, never score a clip against itself. All docs synced (DECISIONS, FABLE_REVIEW, BUILD_PLAN, HANDOVER, prototype banners). Draft emails written in `emails/` (tutor + DPIA/ethics) — **not yet sent**.
- Checks: n/a (documentation phase — zero code exists).
- Decisions: D3 amendment + D9, both dated 7 Aug 2026 in DECISIONS.md.
- Open threads: send the two emails; confirm the September developer (FABLE open question 2); second native speaker still unidentified (open question 1 — now load-bearing per D9).
- Next step: **BUILD_PLAN Step 1** (Part A system checks), in Claude Code on the Mac that will host the build.

## 2026-08-07 — MacBook "neo" (Claude Code) — Parts A and B complete; repo live

- Done: **BUILD_PLAN Steps 1–13, all green.** Part A (developer tooling): verified git 2.50.1, Homebrew 6.0.15, node 24.19.0 / npm 11.17.0 already present; installed Python 3.13.15, Docker Desktop 29.6.2 (Compose 5.3.1), ffmpeg/ffprobe 8.1.2, pre-commit 4.6.1, Praat 7.0. Part B: git identity already set (name kept as "Pedram Badakhchani", fuller than the plan's "Pedram"), `init.defaultBranch=main` added; the existing `id_ed25519` key was reused rather than generating a second one — GitHub accepted it first try. Cloned `langcen_base` to `persian-pronunciation`, renamed its remote to `scaffold`, created the public repo, pushed. Step 13 moved the planning docs into `docs/`, `memory/` to the repo root, `README.md` to the root (with its internal paths corrected for the new layout), and duplicated `HANDOVER.md` as `CLAUDE.md`. Folder-swap variant done: the local project root is now `~/Sites/persian`.
- Checks: every ✅ Check passed. The `hello-world` container ran; `ssh -T git@github.com` returned "Hi pedbad!"; `git push -u origin main` set upstream tracking; post-swap `diff -rq` confirmed every planning doc, `prototype/`, and `memory/` copied byte-identical.
- Failures and fixes: the Docker Desktop cask install failed when run non-interactively — it needs an administrator password to create `/usr/local/bin` — so Pedram ran it by hand. Two git tidy-ups also had to be run by hand: a Claude "GateGuard" hook blocks `git commit --amend` and `rm -rf` from the assistant. Mid-session the assistant's file-edit tool began failing with "Not logged in"; shell writes still worked, so the remaining edits went through the shell.
- Decisions/observations: no new DECISIONS.md entries. Two project conventions adopted: **no `Co-Authored-By` trailers** in commit messages (this is a public research repo), and `.claude/` plus `emails/` are git-ignored. New file `memory/SETUP_LOG.md` — a plain-English explanation of every installed tool and why this project needs it, intended both as methods-appendix material for the paper and as the reference for setting up a second machine; a `process` note recording it was added to RESEARCH_LOG.md. BUILD_PLAN's folder-swap note was amended: it previously told you to delete the backup folder without warning that `emails/` exists nowhere else. The backup is archived as `~/Sites/persian-private/archive/docs-preswap-2026-08-07.zip` — a frozen zip, deliberately not a second live copy of the planning documents — with `emails/` alongside it at `~/Sites/persian-private/emails/`.
- Flagged for later: `Dockerfile.engine` (Step 21) pins no versions — `pip install openai-whisper librosa …` installs whatever is newest on the day, which quietly undercuts D1's promise of a frozen environment. Propose pinned versions, probably an `engine/requirements.txt`, when Step 21 arrives; that is a change to the plan, so it needs a dated DECISIONS.md entry first.
- Open threads (unchanged): send the two draft emails; confirm the September developer; the second native speaker is still unidentified (load-bearing per D9). Repo Topics not yet set on GitHub.
- Next step: **BUILD_PLAN Step 14** (Part C) — venv, `pip install -r requirements.txt -r requirements-dev.txt`, `npm install`, `cp .env.example .env` and set the dev email path, `python check_env.py`, `migrate`, `npm run dev`. Note that `.env`'s `EMAIL_FILE_PATH` must read `/Users/ped/Sites/persian/tmp_emails` after the folder swap.

## 2026-08-07 — MacBook "neo" (Claude Code) — native-reference recording corpus expanded

- Done: **Open question 1 (the second native speaker) now has a plan, not just a hope.** Recordings will be collected during a trip to Iran in mid-August 2026, from at least two and ideally four speakers. A private staging area exists outside the repository (`~/Sites/persian-private/native-recordings/`) holding the recording protocol, technique guide, editor instructions, and the speaker log; identities and consent live only there, never in this repository. The corpus was substantially expanded on the explicit assumption that **there is no second trip** — the recording script now works in priority tiers (essential / high value / bank) so a speaker who gives fifteen minutes still leaves the pilot safe, and four categories were added that cannot be reconstructed afterwards: sustained held vowels for a per-speaker vowel-space reference, controlled consonant frames, an expanded minimal-pair set organised by contrast, and a homograph set (one spelling, two or three pronunciations). Room tone is now recorded at both ends of every session. Two new operational documents separate what the operator does from what the speaker reads.
- Checks: n/a — documentation only. No code, no repository changes beyond `memory/`.
- Decisions/observations: no new DECISIONS.md entry required; nothing here contradicts D9, it implements it. Two things worth knowing outside the private folder. First, **consent is now tracked as two separate permissions** — use inside the application, and inclusion of the audio file in this public repository — because a speaker may reasonably grant the first and decline the second; recordings marked *app only* never enter the repository but can still drive the engine locally. Second, the sustained-vowel recordings are what turn D9 from a design argument into a measurable claim: they allow the acoustic distance between the two reference speakers' vowel spaces to be quantified and reported rather than assumed.
- Publication: two RESEARCH_LOG entries added in the same commit — one on reference-corpus design under a single non-repeatable collection opportunity, one on speaker recruitment and recording conditions as a reportable limitation. The second lists exactly what the paper's methods section must state (recruitment, speaker characteristics, sex composition and why it is not incidental, field recording conditions, the two-tier consent procedure, items speakers rejected as unnatural) and argues the honest framing: field conditions cost precision and buy ecological validity, because learners will also be recording on their own laptops in their own rooms. Also logged an incidental finding from building the minimal-pair set — Persian's contrast density is markedly uneven, with /æ/–/ɑː/ and /o/–/uː/ generating pairs freely while clean /e/–/iː/ pairs barely exist — which argues against syllabus design that mechanically covers every vowel pair.
- Open threads: the two draft emails are still unsent (set aside deliberately for now). The September developer is still unconfirmed — noting the view formed this session that Part F should be treated as an accelerator to hire for, not a dependency to wait on, and that the decision is better taken at the end of Part E when the engine's behaviour is known. Repo Topics still not set on GitHub.
- Next step: unchanged — **BUILD_PLAN Step 14** (Part C).
