# BUILD_PLAN — From an Empty Mac to a Working App, One Checked Step at a Time

**Date:** 7 July 2026 · **Updated:** 7 August 2026 (D3 amendment, D9, tolerance and latency checks)
**For:** Pedram (macOS — Apple Silicon or Intel)
**Companion documents:** `FABLE_REVIEW.md` (the strategy), `DECISIONS.md` (the rules), `prototype/` (the design docs)
**Scaffold:** [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) — your Django 5 + Tailwind v4 + ShadCN-Django starter, which already provides the app's authentication, git hooks, tests, and UI components.

## How to use this document

Work strictly top to bottom. Every step has four parts: **Goal** (why this step exists), **Do** (the exact commands or clicks), **✅ Check** (proof it worked — *never* continue past a failed check), and **If it fails** (first aid). Commands go in Terminal (Applications → Utilities → Terminal). Lines starting with `#` are comments — don't type them. When a command shows expected output, yours should look similar; version numbers may be newer.

Two authentications are built and verified along the way: **GitHub** (SSH keys, so you can push code — Part B) and **the app's learner login** (the scaffold's invite-email system — Part C).

---

## Master checklist

**Part A — Your Mac**
- [x] 1. Terminal works and you know where you are
- [x] 2. Xcode Command Line Tools (gives you git)
- [x] 3. Homebrew
- [x] 4. Python 3.13
- [x] 5. Node + npm
- [x] 6. Docker Desktop
- [x] 7. ffmpeg
- [x] 8. Praat + pre-commit

**Part B — Git, GitHub authentication, the repo**
- [x] 9. Git knows who you are
- [x] 10. SSH key created and GitHub accepts it
- [x] 11. Project created from the langcen_base scaffold
- [x] 12. New public GitHub repo, first push
- [x] 13. Project docs moved into the repo (folder-swap variant done: repo root is `~/Sites/persian`)

**Part C — Scaffold running + app login proven**
- [ ] 14. Python env, npm install, database, dev server
- [ ] 15. Scaffold's tests and git hooks pass
- [ ] 16. Admin login works (superuser)
- [ ] 17. Learner invite flow works end to end
- [ ] 18. CSV student seeding works (pilot onboarding path)

**Part D — Audio kit and ground truth**
- [ ] 19. 12 test recordings, correct format
- [ ] 20. Hand-labelled vowel boundaries (Praat → ground_truth.json)

**Part E — The scoring engine, in Docker**
- [ ] 21. Engine image builds (MFA + Whisper)
- [ ] 22. Persian MFA models downloaded
- [ ] 23. First alignment produces a TextGrid
- [ ] 24. `align_mfa.py` wrapper returns fragments
- [ ] 25. Boundaries measured against your hand labels
- [ ] 26. Scorer runs; score matrix behaves
- [ ] 27. Gates work (silence + wrong word rejected); versions stamped
- [ ] 28. Engine tests green in the container; pushed

**Part F — Wiring the engine into the web app**
- [ ] 29. Postgres + Redis + worker running via docker compose
- [ ] 30. Pronunciation models migrated; bad data rejected
- [ ] 31. Two lessons seeded
- [ ] 32. End-to-end scoring via Celery (command line)
- [ ] 33. Upload + polling endpoints work logged in
- [ ] 34. Practice page: full loop in the browser
- [ ] 35. The final exam: fresh-clone test from the README

---

# Part A — Your Mac (checking and installing the tools)

### Step 1 — Terminal works and you know where you are
**Goal:** Confirm the basics before trusting anything else.
**Do:**
```bash
whoami
pwd
```
**✅ Check:** First prints your username (`ped`), second prints your current folder (probably `/Users/ped`).
**If it fails:** If Terminal itself won't open, restart the Mac. This step cannot meaningfully fail beyond that.

### Step 2 — Xcode Command Line Tools (this is what gives you git)
**Goal:** Apple's developer basics — git and compilers — needed by everything below.
**Do:**
```bash
xcode-select -p
```
If that prints a path, you already have it. If it errors:
```bash
xcode-select --install
```
…and click through the install dialog (takes a few minutes).
**✅ Check:**
```bash
git --version
```
Expected: `git version 2.x.x` (any 2.x is fine).
**If it fails:** Re-run `xcode-select --install`; if macOS says "can't install the software", update macOS first (System Settings → General → Software Update).

### Step 3 — Homebrew (the installer for everything else)
**Goal:** Homebrew installs and updates developer tools cleanly.
**Do:**
```bash
brew --version
```
If "command not found":
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
On Apple Silicon, the installer ends by telling you to run two lines beginning `echo 'eval "$(/opt/homebrew/bin/brew shellenv)"'` — run them exactly as shown, then **close and reopen Terminal**.
**✅ Check:**
```bash
brew --version
brew doctor
```
Expected: a version number, then `Your system is ready to brew.`
**If it fails:** `brew doctor` warnings (not errors) are usually fine to ignore at this stage; actual errors — paste them into a search, they're always common ones.

### Step 4 — Python 3.13 (what the scaffold expects)
**Goal:** `langcen_base` pins Python 3.13 (its `.python-version` file). Note: this Python is for the *web app only* — the audio engine's Python lives inside Docker (Decision D1) and never touches your Mac.
**Do:**
```bash
brew install python@3.13
```
**✅ Check:**
```bash
python3.13 --version
```
Expected: `Python 3.13.x`
**If it fails:** `brew link python@3.13` then retry; or close/reopen Terminal.

### Step 5 — Node and npm (for Tailwind v4)
**Goal:** The scaffold compiles its CSS with Tailwind v4 via npm.
**Do:**
```bash
brew install node
```
**✅ Check:**
```bash
node --version
npm --version
```
Expected: `v22.x` (or newer) and `10.x` (or newer).
**If it fails:** Close/reopen Terminal; `brew doctor`.

### Step 6 — Docker Desktop (home of the scoring engine)
**Goal:** The MFA/Whisper engine, Postgres, Redis, and the worker all run in containers.
**Do:**
```bash
brew install --cask docker
open -a Docker
```
Wait until the whale icon in the menu bar stops animating (first launch asks for your Mac password and a licence agreement — the free Personal tier is fine).
**✅ Check:**
```bash
docker --version
docker compose version
docker run --rm hello-world
```
Expected: two version lines, then a message containing `Hello from Docker!`
**If it fails:** Docker Desktop must be *running* (whale in menu bar) for the third command — `open -a Docker` and wait a minute. On first run it may need System Settings → Privacy & Security approval.

### Step 7 — ffmpeg (audio conversion on your Mac)
**Goal:** Convert phone/browser recordings into the 16 kHz mono WAV the engine needs.
**Do:**
```bash
brew install ffmpeg
```
**✅ Check:**
```bash
ffmpeg -version | head -1
ffprobe -version | head -1
```
Expected: two lines starting `ffmpeg version` / `ffprobe version`.

### Step 8 — Praat and pre-commit
**Goal:** Praat is the free phonetics tool for hand-labelling vowels (Part D). pre-commit runs the scaffold's git hooks (Black + Ruff) before every commit.
**Do:**
```bash
brew install --cask praat
brew install pre-commit
```
**✅ Check:**
```bash
open -a Praat
pre-commit --version
```
Expected: Praat opens (two windows: *Objects* and *Picture* — close them), and a `pre-commit 4.x` version line.
**If it fails:** If macOS blocks Praat ("unidentified developer"): System Settings → Privacy & Security → Open Anyway.

> **Part A complete.** Your Mac has every tool the whole project needs. Nothing below installs anything new on the Mac itself — from here it's accounts, code, and containers.

---

# Part B — Git, GitHub authentication, and the repo

### Step 9 — Tell git who you are
**Goal:** Every commit is signed with a name and email; set them once, globally.
**Do:**
```bash
git config --global user.name "Pedram"
git config --global user.email "pb357@cam.ac.uk"
git config --global init.defaultBranch main
```
**✅ Check:**
```bash
git config --global --list
```
Expected: your three settings listed.

### Step 10 — SSH key: authentication #1 (GitHub)
**Goal:** An SSH key is how your Mac proves to GitHub it's you — no passwords on every push.
**Do:**
```bash
ssh-keygen -t ed25519 -C "pb357@cam.ac.uk"
```
Press Enter at every prompt (default location; empty passphrase is acceptable, or set one). Then:
```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
pbcopy < ~/.ssh/id_ed25519.pub
```
Your *public* key is now on the clipboard. In the browser: **github.com → Settings → SSH and GPG keys → New SSH key** → title "Pedram MacBook" → paste → Add. (Signed in as **pedbad**; enable two-factor authentication under Settings → Password and authentication if you haven't.)
**✅ Check:**
```bash
ssh -T git@github.com
```
First time it asks "Are you sure you want to continue connecting?" — type `yes`. Expected: `Hi pedbad! You've successfully authenticated, but GitHub does not provide shell access.` That sentence *is* success.
**If it fails:** "Permission denied (publickey)" → the key wasn't added on the website, or `ssh-add` step was skipped. Redo both.

### Step 11 — Create the project *from* your scaffold
**Goal:** The new app starts as a copy of `langcen_base`, keeping its full history, and keeps a live connection to the scaffold so future scaffold improvements can be pulled in.
**Do:**
```bash
cd ~/Sites
git clone git@github.com:pedbad/langcen_base.git persian-pronunciation
cd persian-pronunciation
git remote rename origin scaffold
```
**✅ Check:**
```bash
git remote -v
git log --oneline | head -3
```
Expected: two `scaffold` lines pointing at langcen_base, and recent scaffold commits listed.
**If it fails:** Clone errors are authentication errors — Step 10's check must pass first.

### Step 12 — New public GitHub repo and first push
**Goal:** The project gets its own public home; `scaffold` remains a second remote for updates.
**Do:** In the browser: **github.com → + → New repository** → name `persian-pronunciation`, **Public**, and **leave every initialisation checkbox unticked** (no README, no licence — the scaffold brings its own). Then:
```bash
git remote add origin git@github.com:pedbad/persian-pronunciation.git
git push -u origin main
```
**✅ Check:** Terminal ends with `branch 'main' set up to track 'origin/main'`. Refresh the repo page — the scaffold's files and README are there.
**If it fails:** "Repository not found" → name mismatch between the web repo and the URL; `git remote -v` to inspect, `git remote set-url origin <correct-url>` to fix.

### Step 13 — Move the project documents into the repo
**Goal:** The plans, decisions, and design docs live *with* the code from day one — in `docs/`, so the repo root keeps the scaffold's clean layout. Two READMEs would collide, so the scaffold's README is preserved under docs/ and the project README takes the root.
**Do:**
```bash
mkdir -p docs
cp /Users/ped/Sites/persian/DECISIONS.md /Users/ped/Sites/persian/FABLE_REVIEW.md /Users/ped/Sites/persian/BUILD_PLAN.md /Users/ped/Sites/persian/HANDOVER.md docs/
cp -R /Users/ped/Sites/persian/prototype docs/prototype
cp -R /Users/ped/Sites/persian/memory memory
# note: emails/ deliberately NOT copied — draft correspondence stays out of the public repo
git mv README.md docs/scaffold-readme.md
cp /Users/ped/Sites/persian/README.md README.md
git add -A
git commit -m "Project docs in docs/; scaffold README preserved as docs/scaffold-readme.md"
git push
```
(The scaffold's pre-commit hooks run automatically on that commit — Black and Ruff pass, these are markdown files. DECISIONS, FABLE_REVIEW, BUILD_PLAN, and prototype/ stay together in one folder so their cross-references by bare filename keep working. `memory/` sits at the repo root — it's the cross-machine session journal and research log, appended at the end of every working session and synced by push/pull. Also save a copy of HANDOVER.md as `CLAUDE.md` in the repo root so Claude Code loads the working protocol automatically in every future session.)
**✅ Check:** `git status` clean; on GitHub the root shows the *project* README and `docs/` contains the four planning docs plus `prototype/` and `scaffold-readme.md`.
**If it fails:** If the hooks block the commit with a Python formatting complaint, something other than docs was staged — `git status` will show what.

> **Folder-swap variant — if you want `~/Sites/persian` as the project root.** Do this *now*, immediately after Step 13 and strictly **before Part C** (a venv breaks if its folder is renamed after creation):
> ```bash
> cd ~/Sites
> mv persian persian-docs-backup
> mv persian-pronunciation persian
> cd persian && git remote -v   # remotes are unaffected by the rename
> ```
> From here on, wherever this document says `~/Sites/persian-pronunciation`, read `~/Sites/persian`. Keep `persian-docs-backup` until Step 13's push is verified on GitHub, then delete it — the repo (plus GitHub) is now the single source of truth. Only the local folder name changes; the GitHub repo stays `persian-pronunciation`.
>
> **Before deleting the backup — rescue what git cannot hold.** `emails/` is deliberately never copied into the public repo, so the backup folder is its *only* copy and deleting it destroys the drafts. Move it somewhere outside the repo first, and take a frozen zip of the whole pre-swap folder as insurance against a mistyped copy:
> ```bash
> mkdir -p ~/Sites/persian-private/archive
> cp -R ~/Sites/persian-docs-backup/emails ~/Sites/persian-private/emails
> cd ~/Sites && zip -r -q persian-private/archive/docs-preswap-$(date +%F).zip persian-docs-backup -x '*.DS_Store'
> ```
> A zip rather than a live folder is deliberate: a second *editable* copy of `DECISIONS.md` or `BUILD_PLAN.md` sitting in `~/Sites` is how two machines silently end up working from different versions. Verify the copies (`diff -rq`) before removing anything.

> **Part B complete — authentication #1 done.** You own a public repo, pushed over SSH, seeded from your own scaffold, docs included.

---

# Part C — Scaffold running + app login proven

### Step 14 — Bring the scaffold to life
**Goal:** Python env, JS deps, environment file, database, dev server — the scaffold's own setup, each part checked.
**Do (from your project root — `~/Sites/persian-pronunciation`, or `~/Sites/persian` if you did the Step 13 folder swap):**
```bash
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
npm install
cp .env.example .env
```
Open `.env` in a text editor and set the dev email path (per the scaffold README):
```
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/Users/ped/Sites/persian-pronunciation/tmp_emails   # adjust if your root is ~/Sites/persian
DEFAULT_FROM_EMAIL=no-reply@langcen_base.com
SITE_DOMAIN=127.0.0.1:8000
SITE_USE_HTTPS=False
```
Then run the scaffold's own environment checker, migrate, and start everything:
```bash
python check_env.py
python src/manage.py migrate
npm run dev
```
**✅ Check (three things):** `check_env.py` reports a healthy environment; `migrate` prints a list of `Applying ... OK` lines; and `npm run dev` starts both the Tailwind watcher and Django — open **http://127.0.0.1:8000** and you should see the scaffold's styled landing page with working light/dark theme toggle. Leave the server running; open a second Terminal tab (⌘T) for the next steps (remember `cd ~/Sites/persian-pronunciation && source venv/bin/activate` in new tabs).
**If it fails:** `(venv)` must show in your prompt before any `pip`/`python` command. If the page is unstyled, the Tailwind watcher isn't running — use `npm run dev`, not plain `runserver`.

### Step 15 — Prove the scaffold's tests and hooks
**Goal:** A known-good baseline: if these pass now, any future failure is something *we* changed.
**Do:**
```bash
pytest -q
pre-commit install
pre-commit run --all-files
```
**✅ Check:** pytest reports **17 passed** (the scaffold's shipped suite: auth flows, password reset, seeding, role redirects); `pre-commit install` says hooks installed; the all-files run shows every hook `Passed`.
**If it fails:** A failing scaffold test on a fresh clone is environment, not code — almost always a missing `.env` value from Step 14.

### Step 16 — Admin login (superuser)
**Goal:** Your own admin account in the scaffold's Unfold admin.
**Do:**
```bash
python src/manage.py createsuperuser
```
(email `pb357@cam.ac.uk`, choose a strong password — this account can do anything.)
**✅ Check:** Visit **http://127.0.0.1:8000/admin/** and log in. You should see the styled admin with a Users section.
**If it fails:** Wrong URL or server not running — the `npm run dev` tab must still be alive.

### Step 17 — The learner invite flow: authentication #2, end to end
**Goal:** Prove how pilot learners will actually get accounts: an admin creates a user → the scaffold automatically emails them a set-password link → they set a password → they log in. In development, "emails" are files in `tmp_emails/`, so the whole loop is testable offline.
**Do:**
1. In the admin, add a user: email `teststudent@example.com`, role student, *not* staff.
2. In Terminal: `ls -t tmp_emails/ | head -1` — then `open tmp_emails/<that-file>`.
3. In the email text, copy the `/users/reset/<uid>/<token>/` link, paste it into the browser, set a password.
4. Log out of admin (or use a private window) and log in at **http://127.0.0.1:8000/users/login/** as the student.
**✅ Check (four):** the invite email file exists; the link opens a set-password page; the password saves; the student login succeeds and redirects to the student view. Logout works too (it's a POST button, not a link — by design in Django 5).
**If it fails:** No email file → `EMAIL_FILE_PATH` in `.env` is wrong or the folder can't be created; check for typos and that the invite signal only fires for non-staff users (it does — creating a superuser sends nothing).

### Step 18 — CSV seeding: the pilot onboarding path
**Goal:** Next term you'll onboard a whole CULP cohort at once. The scaffold ships exactly this. Prove it now with its sample file.
**Do:**
```bash
python src/manage.py seed_students data/sample_students.csv --default-password=ChangeMe123! --dry-run
python src/manage.py seed_students data/sample_students.csv --default-password=ChangeMe123!
```
**✅ Check:** Dry-run lists what *would* be created without touching the database; the real run creates the users — confirm they appear in the admin Users list (and invite emails appeared in `tmp_emails/`).
**If it fails:** CSV format errors are printed row by row; the sample file should pass as-is.

> **Part C complete — authentication #2 done.** The web app runs, both logins are proven, hooks and tests are green. Commit anything you changed (`git add -A && git commit -m "Configure dev environment" && git push`). Everything so far was the scaffold doing its job — now we build what's new.

# Part D — Audio kit and ground truth (FABLE_REVIEW Phase 1)

### Step 19 — Build the 12-clip test kit
**Goal:** Real recordings to test everything against — including the deliberately wrong ones that catch a lying scorer.
**Do:** For each word (**salâm**, **mamnun**) collect six clips: `native_a` (primary reference — Forvo or a native speaker's voice memo), `native_b` (a *different* native speaker, ideally different sex), `learner_good` (you, careful), `wrong_vowel` (you, deliberately wrong: "sa-LOM", "mam-NON"), `fast`, `slow`. Convert everything:
```bash
mkdir -p audio
ffmpeg -i ~/Downloads/salaam_recording.m4a -ar 16000 -ac 1 audio/salaam_native_a.wav
# …repeat per clip, naming: audio/<word>_<type>.wav
```
**✅ Check (every file):**
```bash
for f in audio/*.wav; do echo "$f:"; ffprobe -v error -show_entries stream=sample_rate,channels -of default=nw=1 "$f"; done
```
Expected for each: `sample_rate=16000` and `channels=1`. Play a couple (`afplay audio/salaam_native_a.wav`) — they should sound clean, 0.3–3 seconds.
**If it fails:** Wrong numbers mean the ffmpeg flags were missed — reconvert with `-ar 16000 -ac 1`.

### Step 20 — Hand-label the vowels in Praat → ground_truth.json
**Goal:** The single most important new artefact in the project: the *true* vowel boundaries, marked by you, that every aligner must be measured against. (Why a human? Because "the aligner returned timestamps" can be true while the timestamps are nonsense.)
**Do:** Open Praat → Open → Read from file → `audio/salaam_native_a.wav` → select it → **View & Edit**. The lower panel is the spectrogram; vowels are the stretches with strong dark horizontal bands (formants). Click-drag to select the â vowel — the window shows the selection's start/end times. Record them. Repeat for each target vowel in `native_a`, `native_b`, and `learner_good` for both words. Create `ground_truth.json`:
```json
{
  "salaam_native_a.wav":   { "a": [0.09, 0.16], "â": [0.31, 0.60] },
  "salaam_native_b.wav":   { "a": [0.11, 0.17], "â": [0.35, 0.66] },
  "salaam_learner_good.wav": { "a": [0.11, 0.19], "â": [0.36, 0.70] },
  "mamnun_native_a.wav":   { "a": [0.08, 0.15], "u": [0.42, 0.61] }
}
```
(with *your* measured numbers, all files).
**✅ Check:**
```bash
python3 -c "import json; d=json.load(open('ground_truth.json')); print(len(d), 'files labelled OK')"
```
Expected: `6 files labelled OK` (or more). Then commit: `git add audio ground_truth.json && git commit -m "Test audio kit and hand-labelled ground truth" && git push`.
**If it fails:** JSON errors are almost always a trailing comma — the error message gives the line number.

> **Part D complete.** You now own the ruler. Budget: one weekend, and the Praat hour teaches you more about speech than anything else in this plan.

---

# Part E — The scoring engine, in Docker (FABLE_REVIEW Phases 2 + 4)

The engine's fragile audio stack never touches your Mac (Decision D1): it lives in an image. All engine code goes in an `engine/` folder in the repo.

### Step 21 — Build the engine image
**Goal:** One file that pins the whole audio environment: MFA (Decision D2) + Whisper (D3) + analysis libraries.
**Do:** Create `Dockerfile.engine` in the repo root:
```dockerfile
FROM condaforge/miniforge3:latest

# Alignment layer (Decision D2): Montreal Forced Aligner — MIT licence, maintained
RUN mamba install -y -c conda-forge montreal-forced-aligner && mamba clean -a -y

# Whisper (gatekeeper, D3) + audio analysis + TextGrid parsing
RUN pip install --no-cache-dir openai-whisper librosa soundfile scipy praatio pytest

WORKDIR /app
```
Build and smoke-test:
```bash
docker build -f Dockerfile.engine -t persian-mfa .
docker run --rm persian-mfa mfa version
docker run --rm persian-mfa python -c "import whisper, librosa, praatio; print('all OK')"
```
**✅ Check:** an MFA version prints; `all OK` prints. **Then update README.md's "How to build and run" with exactly these commands (the D1 rule) and commit.**
**If it fails:** First build downloads ~2 GB — be patient. Network hiccups: just re-run the build (Docker resumes from cache).

### Step 22 — Download the Persian MFA models
**Goal:** MFA needs a Persian *acoustic model* (how Persian sounds) and *dictionary* (word → phonemes). Keep them in a project folder so they survive container restarts.
**Do:**
```bash
mkdir -p mfa_models
docker run --rm -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa mfa model download acoustic
docker run --rm -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa mfa model download dictionary
```
The first form lists what's available — find the Farsi/Persian entries (browsable at mfa-models.readthedocs.io), then re-run each command with the exact model name appended.
**✅ Check:**
```bash
docker run --rm -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa mfa model list acoustic
```
Expected: the Persian model in the list (and the dictionary under `mfa model list dictionary`).
**If it fails / no Persian model exists:** This is the Phase 3 contingency trigger in FABLE_REVIEW — stop here and we switch the aligner (wav2vec2). Don't improvise past this check.

### Step 23 — First alignment
**Goal:** Produce your first TextGrid and *look* at it.
**Do:** MFA processes a folder of audio+transcript pairs:
```bash
mkdir -p corpus aligned
cp audio/salaam_native_a.wav corpus/
printf 'سلام' > corpus/salaam_native_a.txt
docker run --rm -v "$(pwd):/app" -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa \
  mfa align /app/corpus <persian_dictionary_name> <persian_acoustic_model_name> /app/aligned
```
**✅ Check:** `ls aligned/` shows `salaam_native_a.TextGrid`. Open it in Praat (Open → Read from file, then select both the TextGrid and the WAV → View & Edit together): you'll see word and phone tiers with boundaries on the timeline. Eyeball the â phone against your Step 20 label — they should be visibly close.
**If it fails:** MFA's error messages are verbose but honest — most common is a mismatch between dictionary name and what `mfa model list` shows.

### Step 24 — The alignment wrapper: `engine/align_mfa.py`
**Goal:** The bridge between MFA's TextGrids and the scorer from the handover doc — the only genuinely new engine code D2 costs us.
**Do:** Write `engine/align_mfa.py` exposing `align_phonemes(audio_path, lesson) -> list[dict]`: it copies audio + transcript into a temp corpus, runs `mfa align`, parses the phone tier with `praatio`, and returns `[{"phone": "...", "start": 0.12, "end": 0.31}, ...]`. Target vowels are located by **matching the `phoneme` field of the lesson's vowel_map** (first /æ/, the /ɑː/…), not by character position — keep `position` purely as lesson-data validation (handover Rules 2–3 unchanged). Include a small MFA-symbol → lesson-IPA mapping dict (e.g. `ɒː` ↔ `ɑː`). Also add the two lesson files (`lessons/salaam.json`, `lessons/mamnun.json`) from the handover doc.
**✅ Check:**
```bash
docker run --rm -v "$(pwd):/app" -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa \
  python engine/align_mfa.py audio/salaam_native_a.wav lessons/salaam.json
```
Expected: a JSON list of phones with plausible, increasing start/end times, in which the target vowels are found.
**If it fails:** Print the raw TextGrid tier names first — a one-line change in the parser usually fixes it.

### Step 25 — Measure MFA against your hand labels
**Goal:** The honesty test. MFA must *earn* its place.
**Do:** Write `engine/compare_boundaries.py` (~30 lines): for each file in `ground_truth.json`, run `align_phonemes()` and print the millisecond difference between MFA's vowel boundaries and yours, as a table. Run it in the container.
**✅ Check:** You have the full table. **Interpretation: within ±50 ms *and* within ~30% of the vowel's own duration → pass. Outside either bound → shaky (try MFA beam options, cleaner audio — isolated sub-second words are any forced aligner's hardest case, so exhaust the config fixes first). >100 ms or vowels on consonants → stop: Phase 3 contingency (wav2vec2).** The relative bound exists because a Persian short vowel may last only 60–100 ms — ±50 ms alone could "pass" while measuring the wrong slice of audio. Record the numbers in `DECISIONS.md` under D2 either way.

### Step 26 — The scorer and the score matrix
**Goal:** Port the handover's scorer (60/40 weighting — D4) onto the MFA wrapper, then check it *behaves*.
**Do:** Create `engine/scorer.py` from the handover doc's `step7_score.py`, importing `align_phonemes` from `align_mfa`, weights `ACOUSTIC_WEIGHT = 0.60, TIMING_WEIGHT = 0.40`. Score every learner-side clip against `native_a` for both words and fill `docs/results/score_matrix.md` *(against `native_a` alone, deliberately — the native_b row must stay a fair test; production scoring is best-of-both per D9, under which a clip is never scored against itself)*:

| Clip vs native_a | Expected | salâm | mamnun |
|---|---|---|---|
| native_b | high (≥80) | | |
| learner_good | fairly high | | |
| wrong_vowel | clearly lower than learner_good | | |
| fast / slow | ≈ learner_good | | |

**✅ Check:** The ordering holds. **The native_b row is the killer test** — if a second native speaker isn't green, the scorer is measuring *voice*, not *pronunciation*: apply FABLE_REVIEW Step 15's fixes (drop MFCC c0 + deltas; confirm D9's best-of-both scoring is actually in effect) and re-run before continuing.

### Step 27 — Gates and version stamping
**Goal:** The scorer must refuse garbage (D3) and sign its work.
**Do:** `engine/gates.py` with two functions: `check_audio(path)` (reject <0.3 s, >10 s, near-silence by RMS, clipping) and `check_expected_word(path, expected_text)` (Whisper transcribe `language="fa"`, normalised comparison, friendly failure message). Add to every scorer result: `"engine": {"scorer_version": "0.1.0", "aligner": "mfa", "weights": {"acoustic": 0.6, "timing": 0.4}}`.
**✅ Check (three negative tests, run in the container):** a generated silent WAV (`ffmpeg -f lavfi -i anullsrc=r=16000:cl=mono -t 1 audio/silence.wav`) is rejected by `check_audio`; a recording of you saying a *different* word is rejected by `check_expected_word` with the friendly message; your `wrong_vowel` clip **passes** the gate (one wrong vowel is the scorer's job, not the gate's) but scores low. **Plus one positive test (D3 amendment, 7 Aug 2026): every correct-word clip in the kit — learner_good, fast, slow, native_a, native_b, both words — passes `check_expected_word`: zero false rejections.** Whisper is flakiest on sub-second single-word clips; a gate that wrongly rejects a good attempt drives learners away as surely as scoring a wrong word.

### Step 28 — Engine tests, then push
**Goal:** Freeze correctness before the web work starts.
**Do:** Write `engine/tests/` covering the pure functions (timing score, colour mapping, vowel_map validation, gates) — around ten small pytest tests. Run:
```bash
docker run --rm -v "$(pwd):/app" persian-mfa pytest engine/tests -q
git add -A && git commit -m "Scoring engine: MFA alignment, DTW scorer, gates, tests" && git push
```
**✅ Check:** pytest green in the container; push clean; README updated with the engine test command. *(Optional extra credit: a GitHub Actions workflow that builds `Dockerfile.engine` and runs these tests on every push — the Actions tab then shows a green tick.)*

> **Part E complete.** A trustworthy command-line scorer in a container. This is FABLE_REVIEW Checkpoints 2 and 3 in the bag — genuinely demo-able to a phonetician.

# Part F — Wiring the engine into the web app (FABLE_REVIEW Phase 5)

Dev topology (recorded as an amendment to D1 in DECISIONS.md): Django runs natively on your Mac exactly as the scaffold intends (`npm run dev`, browser reload, fast feedback), while **Postgres, Redis, and the scoring worker run in Docker** via compose. The heavy, fragile stack stays containerised; the pleasant dev loop stays pleasant. Steps 29–34 are the ones to do *with your developer* — your job is running every check yourself.

### Step 29 — Postgres, Redis, and the worker via docker compose
**Goal:** The services the app needs, one command up, health-checked.
**Design note (7 Aug 2026):** the worker should call MFA via its `align_one`/server mode, not a fresh `mfa align` per attempt — MFA's per-run startup (corpus validation, model loading) can push a cold alignment to 15–30+ seconds.
**Do:** Create `Dockerfile.worker` (the engine image plus the web app's Python deps, so Celery can import Django):
```dockerfile
FROM persian-mfa
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt celery redis psycopg[binary]
WORKDIR /app/src
CMD ["celery", "-A", "config", "worker", "--loglevel=info", "--concurrency=2"]
```
…and `docker-compose.yml` with services `db` (postgres:16, env from `.env`, volume), `redis` (redis:7), `worker` (build: Dockerfile.worker, mounts the repo, env from `.env`, depends_on db+redis). Add to `.env`: `POSTGRES_DB=persian`, `POSTGRES_USER=persian`, `POSTGRES_PASSWORD=<generate one>`, `DATABASE_URL=postgres://persian:<password>@127.0.0.1:5432/persian`, `CELERY_BROKER_URL=redis://127.0.0.1:6379/0`. Point Django's settings at `DATABASE_URL`/`CELERY_BROKER_URL` (with the scaffold's sqlite as fallback when unset), add `src/config/celery.py` (standard Celery-Django boilerplate), then:
```bash
docker compose up -d db redis
python src/manage.py migrate
docker compose up -d --build worker
```
**✅ Check (three):** `docker compose ps` shows db and redis `running`; `migrate` applies cleanly against Postgres; `docker compose logs worker | tail -5` ends with `celery@… ready.`
**If it fails:** Port 5432 already in use → another Postgres is running (`brew services list`). Worker import errors → `Dockerfile.worker` didn't install requirements.txt.

### Step 30 — The pronunciation models
**Goal:** The database schema from the Phase 2 architecture doc — hardened exactly as reviewed.
**Do:** Create a `pronunciation` Django app. Copy the models from `docs/prototype/phase_2_transitioning_to_server_architecture.md` §5–8 (`LanguageProfile`, `Lesson`, `UtteranceAttempt`, the `validate_vowel_map` validator) with the three agreed changes: replace `espeak_voice_code` with `mfa_dictionary` + `mfa_acoustic_model`; add the engine-version block to `assessment_payload` handling; and (D9, 7 Aug 2026) replace `Lesson.native_reference_audio` with a `NativeReference` model — lesson FK (PROTECT), audio file, speaker sex, optional dialect/register note, `is_active`, and a JSON field for cached per-vowel segment times. Register in admin. `makemigrations`, `migrate`.
**✅ Check (two):** the admin shows all four models (including NativeReference); and the validator bites — try saving a Lesson whose vowel_map points at a consonant (position 2 of `salâm`), expect a clean validation error naming the mismatch. Run `pytest -q` — scaffold's 17 still green.

### Step 31 — Seed the two lessons
**Goal:** salâm and mamnun in the database, with native audio attached.
**Do:** A fixture or small management command creating the Persian `LanguageProfile` and both `Lesson` rows (vowel maps from `lessons/*.json`), each with **two `NativeReference` rows** — your `native_a` and `native_b` WAVs with speaker metadata (D9).
**✅ Check:** Both lessons listed in admin; opening one shows the vowel_map JSON and two native references; both audio files play from the admin file links.

### Step 32 — End-to-end scoring through Celery (no browser yet)
**Goal:** Prove web-app → queue → worker → engine → database before any UI exists.
**Do:** A Celery task `score_attempt(attempt_id)` that runs gates → align → score and writes `assessment_payload`, `overall_score`, status transitions (QUEUED → PROCESSING → SUCCESS/FAILED with timestamps, per the Phase 2 doc's lifecycle). Plus a management command for testing:
```bash
python src/manage.py score_file salaam audio/salaam_learner_good.wav
```
…which creates an `UtteranceAttempt`, dispatches the task, waits, and prints the result.
**✅ Check (three):** the JSON result prints with `overall_score`, `waveform_annotations`, the winning `reference_id` (D9), and the `engine` version block; the attempt row in admin shows SUCCESS with timestamps; feeding it `audio/silence.wav` produces FAILED with the friendly gate message stored in `error_message` — not a crash. Also record the wall-clock time from dispatch to SUCCESS — that measured number (not the 3–8 s guess) is what Step 34's "analysing…" wording must be honest about; if it's slow, switch the wrapper to MFA's `align_one`/server mode (Step 29 design note) before building the page.

### Step 33 — Upload and polling endpoints
**Goal:** The two API routes the page needs, auth-protected.
**Do:** `POST /api/v1/lessons/<slug>/attempts/` (login required): validate size/MIME → save upload → **convert with ffmpeg to 16 kHz mono WAV** (browsers send 48 kHz WebM/Opus) → run `check_audio` → create attempt → dispatch task → return `{"attempt_id": …}`. `GET /api/v1/attempts/<id>/`: status + payload when ready, owner-only.
**✅ Check:** Logged in as your test student in the browser, use the browser console to POST one of your WAVs with `fetch` (your developer will show you the two-liner) — then poll the GET URL in a new tab until `status: "SUCCESS"` with the payload. A logged-*out* request gets a 403/redirect, and one student cannot fetch another's attempt.

### Step 34 — The practice page
**Goal:** The full learner loop, on one page, built from the scaffold's cotton components (`<c-card>`, `<c-button>`, `<c-progress>`…): see prompt → play native → record → honest "analysing…" wait → colour-coded vowels → tap a vowel to hear native vs you → hint text under anything amber/red.
**Do (developer builds, you verify):** `/practice/<slug>/` using MediaRecorder for the mic, the Step 33 endpoints, and the accessibility rules from the gap review baked in: every vowel region gets **colour + icon + text label** (never colour alone), the record control works by keyboard, per-vowel playback buttons carry the native *and* learner segment times (both are in the payload) — the native side plays the *winning* reference from D9 (the payload's `reference_id`), so the learner imitates the voice their score was measured against — and the vowel_map's optional `hint` field is displayed for weak vowels.
**✅ Check (the big one — you, not the developer):** the complete loop works for both lessons with your real voice; saying **the wrong word** on purpose shows the friendly gate message (D3 live in production code!); the loop is completable using only the keyboard; and squinting test — could you tell pass from fail if the colours vanished? Commit, push.

### Step 35 — The final exam: fresh-clone test
**Goal:** Prove the D1 promise end to end: the README alone rebuilds everything.
**Do:**
```bash
cd /tmp
git clone git@github.com:pedbad/persian-pronunciation.git test-clone
cd test-clone
```
…then follow **only** README.md, as if you were the September developer: venv, npm, `.env`, compose, migrate, seed, engine image, one scored attempt.
**✅ Check:** You reach a scored attempt without once consulting your memory or this document. Every gap you hit = a missing line in the README — fix it, commit, and re-run until clean. Then delete `/tmp/test-clone`, tick the last box, and open FABLE_REVIEW.md Phase 6: the pilot.

---

## What this document deliberately leaves out

Consent screens, privacy notice, retention job, teacher calibration, WCAG audit, and pilot logistics are **Phase 6** of FABLE_REVIEW.md — process work with the Language Centre, not build work. The wav2vec2 contingency lives in FABLE_REVIEW Phase 3 and only activates if Step 22 or 25 fails.

## Rough budget

Parts A–B: one evening. Part C: one evening. Part D: one weekend. Part E: two weeks of evenings (Step 24 is the big one). Part F: three to four weeks with your developer, checks run by you. The demo for the tutor meeting exists at the end of Part F.
