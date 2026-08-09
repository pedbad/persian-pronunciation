# BUILD_PLAN — From an Empty Mac to a Working App, One Checked Step at a Time

**Date:** 7 July 2026 · **Updated:** 9 August 2026 (D10 pass: Steps 14, 15, 21, 29, 30, 32, 35 rewritten for uv; Step 18 corrected; Step 18b measured)
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
- [x] 8b. uv — the Python toolchain (D10)

**Part B — Git, GitHub authentication, the repo**
- [x] 9. Git knows who you are
- [x] 10. SSH key created and GitHub accepts it
- [x] 11. Project created from the langcen_base scaffold
- [x] 12. New public GitHub repo, first push
- [x] 13. Project docs moved into the repo (folder-swap variant done: repo root is `~/Sites/persian`)

**Part C — Scaffold running + app login proven**
- [x] 14. Python env (uv), npm install, database, dev server
- [x] 15. Scaffold's tests and git hooks pass
- [x] 16. Admin login works (superuser)
- [x] 17. Learner invite flow works end to end
- [x] 18. CSV student seeding works (pilot onboarding path)
- [x] 18b. `pwa-asset-generator` removed; `npm audit` quiet (D12)

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

### Step 8b — uv, the Python toolchain (Decision D10, 8 August 2026)
**Goal:** One tool that creates the virtual environment, installs the packages, records exactly what it installed (`uv.lock`), and provisions the pinned Python interpreter itself. It replaces `venv` + `pip` everywhere in this project. See D10 in `DECISIONS.md` for why, and `memory/SETUP_LOG.md` for the plain-English version.
**Do:**
```bash
brew install uv
```
**✅ Check:**
```bash
uv --version
```
Expected: a version line such as `uv 0.11.x`.
**If it fails:** `brew update && brew install uv`; reopen Terminal so the new command is found.

> **A note on Step 4.** Homebrew's Python is still worth having on the Mac for odd one-off scripts, but the project no longer depends on it: uv reads `.python-version` (3.13.3) and downloads that exact interpreter itself. This is why the two machines' differing Pythons (abacus 3.13.3, neo 3.13.15) stopped mattering.

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
**Goal:** Python environment, JS build tools, environment file, database, dev server — each part checked.

> **Rewritten 9 August 2026 for Decision D10.** This step used to create a `venv` and run `pip install -r requirements.txt -r requirements-dev.txt`. Those files were deleted when uv was adopted; that version of the step cannot be followed. `pyproject.toml` plus the committed `uv.lock` are now the source of truth, and one command builds the environment.

**Do (from your project root — `~/Sites/persian`):**
```bash
uv sync
```
That is the whole Python setup. It creates `.venv`, installs exactly the versions recorded in `uv.lock`, and provisions the interpreter pinned by `.python-version` — adopting a matching one already on the machine, or downloading a standalone build (about 15 MB) if there isn't one. **Do not create a virtual environment by hand, do not activate anything, and never copy a `.venv` between machines** — it records its own absolute path.

Then the environment file:
```bash
cp .env.example .env
```
Open `.env` and set four values:

| Key | Value |
|---|---|
| `SECRET_KEY` | **generate a fresh one for this machine** — never reuse another machine's: `uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `EMAIL_FILE_PATH` | absolute path inside your checkout: `/Users/ped/Sites/persian/tmp_emails` |
| `DEFAULT_FROM_EMAIL` | `no-reply@persian-pronunciation.local` |
| `SITE_NAME` | `Persian Pronunciation` — drives the nav wordmark, page titles and the invite email |

`.env.example` already sets `EMAIL_BACKEND` to Django's filebased backend, so development email is written to files. Leave `SITE_DOMAIN=127.0.0.1:8000` and `SITE_USE_HTTPS=False` as they are.

If you edit `.env` with a script rather than by hand, **do not use `sed`** for `SECRET_KEY`: Django's key alphabet includes `&`, which `sed` expands to the whole match and corrupts the key silently.

Then check, migrate, and start:
```bash
uv run python check_env.py
uv run python src/manage.py migrate
npm install
npm run dev
```
Note the `uv run` prefix on every Python command. It finds `.venv` without activation — the old "`(venv)` must show in your prompt" trap is gone.

**✅ Check (four):** `check_env.py` reports `ENV: dev` and the `EMAIL_FILE_PATH` you set; `migrate` prints a run of `Applying … OK` lines; `npm install` completes; and `npm run dev` starts both the Tailwind watcher and Django — open **http://127.0.0.1:8000** and you should see a styled landing page titled **Persian Pronunciation** (not "LangCen Base") with a working light/dark theme toggle. Leave the server running and open a second Terminal tab (⌘T) for the next steps — nothing to activate in the new tab, just `cd ~/Sites/persian`.

**Expected noise, neither of which is a failure:**
- `npm install` reports advisories. Until Step 18b removes `pwa-asset-generator` that is 15; afterwards it is a handful traceable to the Tailwind CLI and `concurrently` (D11 handles those, one at a time).
- On **npm 11 and newer** you also get `npm warn allow-scripts` for `@tailwindcss/oxide` and `@parcel/watcher`. Expected; ignore it. Both ship prebuilt binaries as platform-specific optional dependencies, so the build works with the scripts unapproved — verify with `npm run tw:build`, which should finish in well under a second. **Do not run `npm approve-scripts`** to silence the warning; that grants precisely the permission npm supply-chain attacks depend on.

**If it fails:** An unstyled page means the Tailwind watcher isn't running — use `npm run dev`, not plain `runserver`. `uv sync` failing on the interpreter means `.python-version` names a build uv can't fetch; `uv python list` shows what's available. If a Python command reports missing packages, you almost certainly typed `python …` instead of `uv run python …`.

### Step 15 — Prove the scaffold's tests and hooks
**Goal:** A known-good baseline: if these pass now, any future failure is something *we* changed.
**Do:**
```bash
uv run pytest -q
pre-commit install
pre-commit run --all-files
```
**✅ Check:** pytest reports **17 passed** (the scaffold's shipped suite: auth flows, password reset, seeding, role redirects); `pre-commit install` says hooks installed; the all-files run shows every hook `Passed` (eight of them).

**`pre-commit install` must be run on every machine.** Hooks live in `.git/hooks/`, which is per-clone and does not travel with a `git clone` or a `git pull`. Abacus learned this by committing twice unchecked before anyone noticed.

`pre-commit run --all-files` **can modify files** — it fixes trailing whitespace and end-of-file newlines in place. Run `git status` afterwards and look at what it touched before committing.
**If it fails:** A failing scaffold test on a fresh clone is environment, not code — almost always a missing `.env` value from Step 14. Note that on this suite `pytest -q` without the `uv run` prefix either fails outright or, worse, runs against some other Python that happens to be on the PATH.

### Step 16 — Admin login (superuser)
**Goal:** Your own admin account in the scaffold's Unfold admin.
**Do:**
```bash
uv run python src/manage.py createsuperuser
```
(email `pb357@cam.ac.uk`, choose a strong password — this account can do anything.)
Run this yourself in a second terminal: it prompts for a password interactively, and the
dev server must keep running in the first tab.
**✅ Check:** Visit **http://127.0.0.1:8000/admin/** and log in. You should see the styled admin with a Users section.
**If it fails:** Wrong URL or server not running — the `npm run dev` tab must still be alive.

### Step 17 — The learner invite flow: authentication #2, end to end
**Goal:** Prove how pilot learners will actually get accounts: an admin creates a user → the scaffold automatically emails them a set-password link → they set a password → they log in. In development, "emails" are files in `tmp_emails/`, so the whole loop is testable offline.
**Do:**
1. Logged in as an admin, go to **http://127.0.0.1:8000/users/register/** and add a user: email `teststudent@example.com`, role student.

   The form asks for an email and a role, and **no password** — which is the point: `RegisterView.form_valid()` calls `set_unusable_password()`, and the invite is what lets the learner choose their own.

   **Not** Django admin's *Add user* page. The scaffold has two deliberate creation paths, and only one invites (`src/users/signals.py`, `send_invite_on_create`): the signal skips any new user who already has a usable password. Django admin's `AdminUserAddForm` *requires* password1/password2, so it sets one and suppresses the invite; `/users/register/` uses `RegisterForm` and calls `set_unusable_password()`, so the invite fires. Use the admin page and no email will ever appear, with nothing to indicate why.

   Keep to `@example.com` — RFC 2606 reserves it, so a stray development email can never reach a real person. Never use a real address here; if `EMAIL_BACKEND` is later switched to SMTP, any such row becomes a live email.
2. In Terminal: `ls -t tmp_emails/ | head -1` — then `open tmp_emails/<that-file>`.
3. In the email text, copy the `/users/reset/<uid>/<token>/` link, paste it into the browser, set a password.
4. Log out of admin (or use a private window) and log in at **http://127.0.0.1:8000/users/login/** as the student.
**✅ Check (four):** the invite email file exists; the link opens a set-password page; the password saves; the student login succeeds and redirects to the student view. Logout works too (it's a POST button, not a link — by design in Django 5).
**Fixed 9 August 2026 — recorded because the shape of the bug recurs.** Until this date `/users/register/` demanded a password and a confirmation, then threw both away. `RegisterForm` narrowed `Meta.fields` to `("email",)`, but Django declares `password1`/`password2` on the `UserCreationForm` **class**, so `Meta.fields` never touched them. Harmless for one test user; wrong for onboarding a CULP cohort, who would each be handed a credential the system discards.

The fix sets `password1 = None` and `password2 = None` on `RegisterForm` — Django's documented way to opt out of an inherited declared field — plus a `save()` override, because `UserCreationForm.save()` reads `cleaned_data["password1"]` and would otherwise raise `KeyError`. The template needed no change: it already guards every field with `{% if form.password1 %}`.

**The test lesson is the part worth keeping.** `test_register.py` posted `password1`/`password2`, and Django silently ignores unrecognised POST keys — so after the fix that test still passed while proving nothing. It now posts no password *and* asserts the fields are absent from `RegisterForm().fields`. When you remove a form field, assert on the form, not on the request.

Still worth offering back to `langcen_base` through the `scaffold` remote (D7).

**If it fails:** No email file, and `tmp_emails/` does not exist at all → nothing was ever sent. Django's filebased backend creates that folder on its first send, so a missing folder is the symptom, not the cause. In order of likelihood: (a) the user was created through Django admin's *Add user* page rather than `/users/register/`, so it has a usable password and the invite was skipped — check with `has_usable_password()`; (b) `EMAIL_FILE_PATH` in `.env` is wrong; (c) the user is a superuser or staff, which the signal also skips.

### Step 18 — CSV seeding: the pilot onboarding path
**Goal:** Next term you'll onboard a whole CULP cohort at once. The scaffold ships exactly this. Prove it now with its sample file.
**Do:**
```bash
uv run python src/manage.py seed_students data/sample_students.csv --dry-run
uv run python src/manage.py seed_students data/sample_students.csv
```

**No `--default-password` — corrected 9 August 2026, and the reason matters.** This step previously passed `--default-password=ChangeMe123!`, which is the one flag that makes its own check unsatisfiable. `seed_students` chooses a create-time password as *CSV column > `--default-password` > unusable*, so that flag gives every seeded student a **usable** password — and `send_invite_on_create` (`src/users/signals.py`) skips any new user who already has one. The result is six accounts and zero invite emails, with nothing to indicate why. This is the same trap as Step 17, reached through a different command.

Omitting the flag makes the create-time password `None`, the manager marks it unusable, and the invite fires for every row — which is D8's actual pilot path: learners receive a **set-password link**, never a shared credential.

`seed_students` does have its own separate email path — `--send-welcome`, which requires `--site-domain` — but it mails the temporary password **in plain text** beside the reset link. Deliberately not used here: D8 specifies invite links, and a plaintext credential sent to a CULP cohort is the wrong artefact to own in a pilot with a DPIA attached.

**✅ Check (four):** the dry run lists six `would create` rows and writes nothing; the real run creates them; `ls tmp_emails/ | wc -l` shows **one invite file per seeded student** (the folder will not exist until the first send — Django's filebased backend creates it); and the users appear in the admin Users list with role `student`. Confirm the invites are real by opening one — `Subject: Set your password`, a `/users/reset/<uid>/<token>/` link, and a `From:` address matching `DEFAULT_FROM_EMAIL` in your `.env`.

Verify the password state directly rather than trusting the absence of an error:
```bash
uv run python src/manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
for u in U.objects.filter(email__endswith='@example.com').order_by('email'):
    print(u.email, u.role, 'usable_pw=', u.has_usable_password())
"
```
Every row must read `usable_pw= False`. A `True` anywhere means a password was set and that learner will never receive an invite.

**If it fails:** CSV format errors are printed row by row; the sample file should pass as-is. Users created but `tmp_emails/` missing entirely → a password was set after all (check the command line for `--default-password`, or a `password` column in the CSV, which outranks everything). Note the sample CSV lowercases addresses on the way in (`Ed@` → `ed@`), so re-running is a no-op rather than a duplicate.

### Step 18b — Remove `pwa-asset-generator` (Decision D12, 8 August 2026)
**Goal:** A quiet `npm audit`. A fresh `npm install` reports 15 advisories, 11 high and 4 critical — and 12 of them, including every critical one, come through this one package, which bundles a headless Chrome (`puppeteer-core`) and its proxy stack. It is a one-shot icon generator that no npm script ever runs. The point is not the vulnerabilities themselves (all dev-only, none reaching a browser) but keeping `npm audit` output worth reading. Full reasoning: D12 in `DECISIONS.md`.
**Do:**
```bash
npm uninstall pwa-asset-generator
npm install
npm audit
```
The fourteen icon files in `src/core/static/core/favicon/` are committed static assets and are **not** affected — nothing about the app's appearance changes. When branding is next redone, regenerate them with a one-off `npx pwa-asset-generator …` (see README) rather than reinstalling the dependency.
**✅ Check (three, all must hold):**

1. **`pwa-asset-generator` is gone from `package.json`'s `devDependencies`, and the advisory count falls sharply** — measured on neo, 9 August 2026: **15 → 6**. Judge this by *what remains*, not by the number. Every surviving advisory must trace to a package the project genuinely uses; run `npm ls <package>` on each to prove it. On 9 August the residue was `tar` ← `@tailwindcss/cli` → `@tailwindcss/oxide` (the criticals), `shell-quote` ← `concurrently`, plus `nanoid` ← `postcss` and `picomatch` ← `@parcel/watcher`.

   **Do not treat a specific number as the pass condition — it rots.** D12 was written on 8 August predicting a residue of "roughly 3"; one day later it was 6, because `@tailwindcss/oxide 4.1.13` pins `tar 7.5.1` and a batch of node-tar advisories covering `<=7.5.20` was published in between. Nothing about this project changed. That is D12's own argument arriving as evidence: an advisory list is only worth reading if it stays short enough to read.

   Whatever remains belongs to **D11's one-at-a-time, test-gated policy** — bumping `@tailwindcss/cli` or `concurrently` is its own step — and **never** to `npm audit fix`, which rewrites the lockfile wholesale.
2. `uv run pytest -q` still reports **17 passed**.
3. `npm run dev` still serves the styled landing page with a working theme toggle. Confirm the stylesheet is genuinely being served rather than 404ing behind a page that merely loads: `curl -s -o /dev/null -w '%{http_code} %{size_download}\n' http://127.0.0.1:8000/static/core/css/output.css` — expect `200` and a size in the tens of kilobytes (85,715 bytes on 9 Aug 2026). Also confirm `ls src/core/static/core/favicon/ | wc -l` still shows **14** — the icons are committed assets and must survive untouched.

**Then add the regeneration command to README.md (the D1 rule) and commit.**
**If it fails:** Revert with `git checkout package.json package-lock.json && npm install` — the lockfile is in git, so this is fully reversible. Do **not** reach for `npm audit fix`: it rewrites the lockfile wholesale, which is exactly what D11 forbids.

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

> **Read this before writing the Dockerfile — D10 applies here more than anywhere else (noted 9 August 2026).** The sketch below was written before uv was adopted and **pins nothing**: a `:latest` base image, an unpinned `mamba install`, and a `pip install` of six packages at whatever versions exist on the day. D1 promises this project rebuilds at any point in its history, and D10's second stated reason is precisely this file — **the engine is where reproducibility matters most, because the boundary table (Step 25) and the score matrix (Step 26) are numbers the paper will report.** An engine that silently rebuilds with a different librosa is an engine whose published numbers cannot be reproduced.
>
> **The mechanism is a decision, not an improvisation.** Two layers need pinning and they use different tooling — MFA arrives through conda, everything else through pip. Settle *how* before writing the file (an `environment.yml` with explicit versions, or conda-lock, for the conda layer; a lockfile-backed pip layer for the rest), **record it as a dated DECISIONS.md entry, then build.** This was flagged on 7 August and formally covered by D10 on 8 August; it is owed at this step and nowhere else.
>
> Whatever is chosen, three properties must hold: the base image is pinned (a tag *and* a digest, never `:latest`); every installed package has an exact version recorded in a committed file; and a rebuild months later either reproduces the environment or fails loudly rather than quietly drifting.

**Do:** Create `Dockerfile.engine` in the repo root. The structure below is the *shape* — the pins are what Step 21's decision supplies:
```dockerfile
# Pin the base image by tag AND digest — never :latest
FROM condaforge/miniforge3:<tag>@sha256:<digest>

# Alignment layer (Decision D2): Montreal Forced Aligner — MIT licence, maintained.
# Exact version, from the pinned conda environment file.
RUN mamba install -y -c conda-forge montreal-forced-aligner=<version> && mamba clean -a -y

# Whisper (gatekeeper, D3) + audio analysis + TextGrid parsing — from a committed,
# fully pinned requirements/lock file, never a bare package list.
COPY engine/requirements.lock /tmp/
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock

WORKDIR /app
```
Build and smoke-test:
```bash
docker build -f Dockerfile.engine -t persian-mfa .
docker run --rm persian-mfa mfa version
docker run --rm persian-mfa python -c "import whisper, librosa, praatio; print('all OK')"
```
**✅ Check (three):** an MFA version prints; `all OK` prints; and **the Dockerfile contains no `:latest` and no unpinned package name** — read it back and confirm, because this is the check that is easiest to skip and most expensive to discover later. **Then update README.md's "How to build and run" with exactly these commands (the D1 rule) and commit.**
**If it fails:** First build downloads ~2 GB — be patient. Network hiccups: just re-run the build (Docker resumes from cache). A digest mismatch on the base image means the tag was re-pushed upstream — that is the pin doing its job; look at what changed before updating it.

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
**Do — first, add the three new dependencies to the project properly** (D10: nothing is installed that the lockfile does not record):
```bash
uv add celery redis "psycopg[binary]"
```
That updates `pyproject.toml` and `uv.lock` together. Do **not** install them inside the Dockerfile instead — that is exactly the unpinned hole D10 closed.

Then create `Dockerfile.worker` (the engine image plus the web app's Python dependencies, so Celery can import Django):
```dockerfile
FROM persian-mfa

# uv, version-pinned — nothing in this project installs "whatever is newest today"
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /usr/local/bin/uv

# Build the environment OUTSIDE /app. compose bind-mounts the repository over
# /app, which would otherwise hide the image's .venv behind the Mac's own —
# a macOS venv that cannot run in a Linux container. See "If it fails" below.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./

# --frozen: fail loudly if uv.lock is out of date, rather than quietly
#           re-resolving and building an environment nobody recorded.
# --no-dev: the worker needs runtime dependencies only.
RUN uv sync --frozen --no-dev

WORKDIR /app/src
CMD ["uv", "run", "--frozen", "celery", "-A", "config", "worker", "--loglevel=info", "--concurrency=2"]
```
Also add `.venv/` and `node_modules/` to `.dockerignore` if they are not already there, so the Mac's environment is never copied into an image.
…and `docker-compose.yml` with services `db` (postgres:16, env from `.env`, volume), `redis` (redis:7), `worker` (build: Dockerfile.worker, mounts the repo, env from `.env`, depends_on db+redis). Add to `.env`: `POSTGRES_DB=persian`, `POSTGRES_USER=persian`, `POSTGRES_PASSWORD=<generate one>`, `DATABASE_URL=postgres://persian:<password>@127.0.0.1:5432/persian`, `CELERY_BROKER_URL=redis://127.0.0.1:6379/0`. Point Django's settings at `DATABASE_URL`/`CELERY_BROKER_URL` (with the scaffold's sqlite as fallback when unset), add `src/config/celery.py` (standard Celery-Django boilerplate), then:
```bash
docker compose up -d db redis
uv run python src/manage.py migrate
docker compose up -d --build worker
```
**✅ Check (three):** `docker compose ps` shows db and redis `running`; `migrate` applies cleanly against Postgres; `docker compose logs worker | tail -5` ends with `celery@… ready.`
**If it fails:** Port 5432 already in use → another Postgres is running (`brew services list`). Worker import errors → the three dependencies were never added with `uv add`, so they are not in `uv.lock`; check `uv.lock` mentions celery before rebuilding. `uv sync --frozen` failing during the build → `uv.lock` is stale; run `uv lock` on the Mac, commit it, rebuild. Worker starts but cannot find its packages → the bind mount is shadowing the environment; confirm `UV_PROJECT_ENVIRONMENT=/opt/venv` is set and that `.venv/` is in `.dockerignore`.

### Step 30 — The pronunciation models
**Goal:** The database schema from the Phase 2 architecture doc — hardened exactly as reviewed.
**Do:** Create a `pronunciation` Django app. Copy the models from `docs/prototype/phase_2_transitioning_to_server_architecture.md` §5–8 (`LanguageProfile`, `Lesson`, `UtteranceAttempt`, the `validate_vowel_map` validator) with the three agreed changes: replace `espeak_voice_code` with `mfa_dictionary` + `mfa_acoustic_model`; add the engine-version block to `assessment_payload` handling; and (D9, 7 Aug 2026) replace `Lesson.native_reference_audio` with a `NativeReference` model — lesson FK (PROTECT), audio file, speaker sex, optional dialect/register note, `is_active`, and a JSON field for cached per-vowel segment times. Register in admin. `makemigrations`, `migrate`.
**✅ Check (two):** the admin shows all four models (including NativeReference); and the validator bites — try saving a Lesson whose vowel_map points at a consonant (position 2 of `salâm`), expect a clean validation error naming the mismatch. Run `uv run pytest -q` — scaffold's 17 still green.

### Step 31 — Seed the two lessons
**Goal:** salâm and mamnun in the database, with native audio attached.
**Do:** A fixture or small management command creating the Persian `LanguageProfile` and both `Lesson` rows (vowel maps from `lessons/*.json`), each with **two `NativeReference` rows** — your `native_a` and `native_b` WAVs with speaker metadata (D9).
**✅ Check:** Both lessons listed in admin; opening one shows the vowel_map JSON and two native references; both audio files play from the admin file links.

### Step 32 — End-to-end scoring through Celery (no browser yet)
**Goal:** Prove web-app → queue → worker → engine → database before any UI exists.
**Do:** A Celery task `score_attempt(attempt_id)` that runs gates → align → score and writes `assessment_payload`, `overall_score`, status transitions (QUEUED → PROCESSING → SUCCESS/FAILED with timestamps, per the Phase 2 doc's lifecycle). Plus a management command for testing:
```bash
uv run python src/manage.py score_file salaam audio/salaam_learner_good.wav
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
…then follow **only** README.md, as if you were the September developer: `uv sync`, `.env`, `npm install`, compose, migrate, seed, engine image, one scored attempt.

**Two things this test is specifically designed to catch, both learned the hard way:**

- **Everything per-machine must be in the README.** A clone brings the code and the documents and nothing else — not `.venv`, not `node_modules/`, not `.env`, not the database, not `passwords.txt`, not the Docker images. Each one that the README fails to mention is a gap the September developer falls into.
- **Run it from a genuinely different directory** (`/tmp/test-clone`, as above) and never rename that directory afterwards. `.venv` records its own absolute path, so a rename breaks it — the same rule that forced the folder swap to happen before Part C.

**✅ Check:** You reach a scored attempt without once consulting your memory or this document. Every gap you hit = a missing line in the README — fix it, commit, and re-run until clean. Then delete `/tmp/test-clone`, tick the last box, and open FABLE_REVIEW.md Phase 6: the pilot.

---

## What this document deliberately leaves out

Consent screens, privacy notice, retention job, teacher calibration, WCAG audit, and pilot logistics are **Phase 6** of FABLE_REVIEW.md — process work with the Language Centre, not build work. The wav2vec2 contingency lives in FABLE_REVIEW Phase 3 and only activates if Step 22 or 25 fails.

## Rough budget

Parts A–B: one evening. Part C: one evening. Part D: one weekend. Part E: two weeks of evenings (Step 24 is the big one). Part F: three to four weeks with your developer, checks run by you. The demo for the tutor meeting exists at the end of Part F.
