# SETUP_LOG — What Is Installed, and Why (plain-English appendix)

**What this is:** a non-programmer's explanation of every tool this project installs on a machine, what it is for, and how it was verified. Three purposes: (1) a reference when setting up a second machine, (2) a record of which versions were actually used, (3) raw material for the methods appendix of the paper or poster.

**How this differs from BUILD_PLAN.md:** the build plan says *what to type*. This file says *what the thing is and why it exists in this project*. Read this one first if the build plan feels like magic incantations.

**Sync:** lives in `memory/`, which is copied into the repo at BUILD_PLAN Step 13 and synced across machines by push/pull from then on.

---

## Part A — Your Mac (completed 7 August 2026, MacBook "neo", macOS 25.5 / Apple Silicon)

Part A installs nothing project-specific. It stocks the machine with general tools. Nothing after Part A installs anything onto macOS itself — from Part B onwards it is accounts, code, and containers.

### Step 1 — Terminal orientation

**Commands:** `whoami`, `pwd`
**Result:** `ped`, `/Users/ped/Sites/persian`

The Terminal is a text interface to the computer. `whoami` prints the user account; `pwd` ("print working directory") prints the folder the Terminal is currently sitting in. Every later command is interpreted relative to that folder, so running the right command in the wrong folder is the commonest beginner error. Confirming both before anything else is cheap insurance.

### Step 2 — Xcode Command Line Tools

**Verified:** `git version 2.50.1 (Apple Git-155)` (already installed)

Apple's basic developer kit: compilers, build tools, and — the part this project needs — **git**. Git is a version-control system: it records every change made to the project as a numbered, dated, reversible snapshot, and it is what lets the same project exist on several machines without the copies drifting apart. GitHub (Part B) is simply a website that hosts git snapshots.

### Step 3 — Homebrew

**Verified:** `Homebrew 6.0.15`, `brew doctor` → `Your system is ready to brew.` (already installed)

Homebrew is a package manager: an app store for developer tools, driven from the Terminal. Instead of finding an installer on a website, `brew install X` downloads, installs, and later updates X, keeping everything in one predictable place (`/opt/homebrew` on Apple Silicon). Every tool below arrived through it.

`brew doctor` is Homebrew's self-diagnosis — it reports anything about the machine likely to break future installs.

### Step 4 — Python 3.13

**Installed:** `Python 3.13.15` (via `brew install python@3.13`)

Python is the language the web application is written in. The version matters: the `langcen_base` scaffold pins Python 3.13 in its `.python-version` file, and mixing versions is a reliable source of confusing failures.

**Important distinction, and the whole point of Decision D1:** this Python runs the *website* only. The audio engine's Python — with the Montreal Forced Aligner, Whisper, and their fragile dependencies — lives inside Docker and never touches macOS. Two separate Pythons, deliberately, so the fragile one cannot break the machine and the machine cannot break the fragile one.

### Step 5 — Node and npm

**Verified:** `node v24.19.0`, `npm 11.17.0` (already installed; plan required v22+/10+)

Node is a second language runtime, used here purely as a build tool. The scaffold styles its pages with Tailwind CSS v4, which is a Node program: it reads the HTML templates, works out which style rules are actually used, and compiles a stylesheet. No Node code runs as part of the finished application — it only builds the CSS.

### Step 6 — Docker Desktop

**Installed:** `Docker 29.6.2`, `Docker Compose v5.3.1`; `docker run --rm hello-world` succeeded
**Note:** the Homebrew cask install needed an administrator password (it creates `/usr/local/bin`), so it was run by hand in an interactive Terminal rather than by the assistant.

Docker runs software inside sealed boxes called **containers**. A container carries its own copy of an operating system's libraries, so the software inside it sees exactly the same environment on every machine, regardless of what the host machine has installed.

This is the foundation of Decision D1. The speech stack — Montreal Forced Aligner, Whisper, and the numerical libraries beneath them — depends on a tangle of specific pinned versions that is painful to reproduce by hand and rots over time as the host machine is updated. Written into a `Dockerfile`, that environment is frozen as a text file: it rebuilds identically on this Mac in August, on a collaborator's machine in September, and on a university server next year.

`hello-world` is a tiny image whose only job is to prove the whole chain works: the Docker client reached the Docker engine, the engine downloaded an image from the internet, created a container from it, ran it, and streamed the output back.

### Step 7 — ffmpeg

**Installed:** `ffmpeg 8.1.2`, `ffprobe 8.1.2`

ffmpeg is the universal audio and video converter; `ffprobe` is its companion that inspects a file and reports what is actually inside it.

Every recording in this project is converted to **16 kHz mono WAV**: 16,000 samples per second, a single channel, uncompressed. This is not arbitrary. Speech recognition and forced alignment models are trained on 16 kHz audio; higher sample rates carry no additional speech information (the frequencies that distinguish speech sounds sit well below 8 kHz) and merely make files larger. Mono because there is one speaker. Uncompressed because compression artefacts are exactly the kind of small spectral distortion that a vowel-comparison algorithm might mistake for a pronunciation difference.

Recordings arrive in the wrong format by default — phones produce `.m4a`, browsers produce 48 kHz WebM/Opus — so this conversion happens at every entry point to the system, including inside the upload endpoint (Step 33).

### Step 8a — pre-commit

**Installed:** `pre-commit 4.6.1`
**Side note:** installing it also pulled in Homebrew's `python@3.14` as its own private runtime. This is unrelated to the project's Python 3.13 and does not affect the virtual environment created in Step 14.

pre-commit is a gatekeeper attached to git. Before git accepts a commit, pre-commit runs a configured list of checks over the changed files — in this project, the code formatters **Black** and **Ruff**, which come with the scaffold. Badly formatted code is reformatted or rejected before it can enter the repository's history. Since the repository is public, this keeps it presentable without anyone having to remember to be tidy.

### Step 8b — Praat

**Installed:** `Praat 7.0`

Praat is free phonetics software from the University of Amsterdam (Paul Boersma and David Weenink), and has been the standard analysis tool in academic speech research for decades. It displays a recording two ways simultaneously: the **waveform** (loudness over time) and beneath it the **spectrogram** (which frequencies are present at each instant, drawn as a smear of light and dark).

The spectrogram is the reason it is in this project. Vowels appear as **strong dark horizontal bands** — *formants*, the resonant frequencies of the vocal tract. Where those bands sit is what distinguishes one vowel from another; the difference is visible on screen. Consonants look quite different: a fricative like /s/ is a high, diffuse grey hiss, a stop like /b/ is a moment of silence followed by a burst. A reader can therefore see, and measure, where a vowel begins and ends.

**Praat has two jobs here.**

*First, and most important: it makes the ruler.* At BUILD_PLAN Step 20, the vowel boundaries in the test recordings are marked by hand in Praat and written into `ground_truth.json`. This is the single most important artefact created before any pipeline code exists, and the reason is methodological: a forced aligner always returns timestamps. It returns them for the wrong word, for silence, for nonsense. "The aligner produced output" can be entirely true while the output is meaningless. Only a human-made reference measurement can catch that. At Step 25 the Montreal Forced Aligner is measured against those hand labels and must land within ±50 ms *and* within 30% of the vowel's own duration — the relative bound exists because a Persian short vowel may last only 60–100 ms, so ±50 ms alone could "pass" while pointing at the wrong slice of audio. Failing worse than 100 ms, or placing vowels on consonants, stops the project and triggers the wav2vec2 contingency.

*Second: it reads the aligner's output.* The Montreal Forced Aligner writes its results as **TextGrid** files, which is Praat's own annotation format. Opening a WAV and its TextGrid together in Praat (Step 23) shows the aligner's proposed boundaries drawn directly on the spectrogram, which makes an obviously-wrong alignment obvious at a glance.

---

### Part A summary table

| Tool | Version installed | Role in this project |
|---|---|---|
| Xcode Command Line Tools | git 2.50.1 | version control, compilers |
| Homebrew | 6.0.15 | installs and updates everything below |
| Python | 3.13.15 | the web application's language (website only) |
| Node / npm | 24.19.0 / 11.17.0 | compiles the Tailwind stylesheet |
| Docker Desktop | 29.6.2 (Compose 5.3.1) | sealed environment for the audio engine (D1) |
| ffmpeg / ffprobe | 8.1.2 | converts all audio to 16 kHz mono WAV |
| pre-commit | 4.6.1 | runs Black + Ruff before every commit |
| Praat | 7.0 | hand-labelling vowel boundaries; reading TextGrids |

**One thing that did not go to plan:** the Docker Desktop cask install failed when run non-interactively, because creating `/usr/local/bin` requires an administrator password and there was no terminal available to type it into. It was re-run by hand and succeeded. Worth knowing when setting up a second machine: Docker is the one Part A install that needs a password.

---

## Part B — Git, GitHub, and where this repository came from (completed 7 August 2026, MacBook "neo")

Part B installs nothing. It establishes an identity, an authentication, and a repository. If you are reading this on a second machine, the practical content is Steps 9 and 10 — the repository itself already exists and you only need to clone it.

### Step 9 — Git identity

Every commit carries a name and an email, set once and used by every project on the machine:

```bash
git config --global user.name "Pedram Badakhchani"
git config --global user.email "pb357@cam.ac.uk"
git config --global init.defaultBranch main
```

The third line tells git to call the first branch of a new repository `main` rather than the older default `master`, which is what GitHub now expects.

**Note for a second machine:** the first two may already be set from other work — check with `git config --global --list` before overwriting. Since this repository is public, the name and email in these settings appear permanently and publicly in every commit. That was a deliberate choice (research credibility), not an oversight.

### Step 10 — SSH key: how the machine proves it is you

GitHub needs to recognise the machine before it will accept a push. An SSH key is a matched pair of files: a **private** key that never leaves the machine, and a **public** key that is pasted into your GitHub account. GitHub then recognises anything signed by the private half.

On this machine an `ed25519` key already existed and was reused. **One key per machine is the right arrangement** — a second key on the same machine adds nothing and gives you two things to manage.

A machine with no key needs one created:

```bash
ssh-keygen -t ed25519 -C "pb357@cam.ac.uk"
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
pbcopy < ~/.ssh/id_ed25519.pub
```

The public half is then on the clipboard; paste it at **github.com → Settings → SSH and GPG keys → New SSH key**, titled after the machine.

Verification:

```bash
ssh -T git@github.com
```

Success looks like `Hi pedbad! You've successfully authenticated, but GitHub does not provide shell access.` **That sentence is the pass, even though the command exits with a non-zero code** — GitHub deliberately refuses shell access, so the connection always closes with an error status. Judge it by the greeting, not the exit code.

### Steps 11–12 — Why this repository is a clone of another one

The project was not started from an empty folder. It was created by cloning [`pedbad/langcen_base`](https://github.com/pedbad/langcen_base) — Pedram's own Django 5 + Tailwind v4 + ShadCN-Django starter — which already provides, tested: a custom user model with student, teacher and admin roles; complete authentication flows; automatic invite emails when an account is created; CSV seeding of a whole cohort; pre-commit hooks running Black and Ruff; a seventeen-test pytest suite; the Unfold admin theme; and the component UI. That is several weeks of work that did not need doing twice (Decision D7).

The clone keeps the scaffold's full history, and the scaffold stays connected as a **second git remote** so improvements to it can be merged in later:

```bash
git clone git@github.com:pedbad/langcen_base.git persian-pronunciation
cd persian-pronunciation
git remote rename origin scaffold                                    # free up the name "origin"
git remote add origin git@github.com:pedbad/persian-pronunciation.git
git push -u origin main
```

The result is two remotes, and the distinction matters:

| Remote | Points at | Used for |
|---|---|---|
| `origin` | `persian-pronunciation` | normal work — `git pull`, `git push` |
| `scaffold` | `langcen_base` | pulling in future scaffold improvements: `git fetch scaffold && git merge scaffold/main` |

The public GitHub repository was created through the website with **every initialisation checkbox left unticked** — no README, no licence, no `.gitignore`. A pre-filled repository creates a commit that has nothing in common with the scaffold's history, and the first push then fails.

### Step 13 — Layout, and the folder-name swap

The planning documents moved into `docs/`, so the repository root keeps the scaffold's clean layout. `memory/` sits at the root because it is the project's working memory rather than documentation. The scaffold's own README was preserved as `docs/scaffold-readme.md` and the project README took the root — two files cannot both be `README.md`. `HANDOVER.md` was duplicated as `CLAUDE.md` in the root, because Claude Code loads that filename automatically and the working protocol should not depend on remembering to paste it.

The local folder was then renamed so that the project lives at `~/Sites/persian` while the GitHub repository remains `persian-pronunciation`. **The order of that rename is not cosmetic:** it must happen before Part C, because a Python virtual environment records its own absolute path internally and breaks if its parent folder is renamed afterwards. The same reason explains why a `venv/` must never be copied between machines — always create a fresh one.

Two things were deliberately kept out of the repository, and remain out of it permanently: draft correspondence, and all native-speaker recording material including speaker identities and consent records. They live in `~/Sites/persian-private/`, which does not sync between machines. A frozen zip of the pre-swap documentation folder was archived there as well — deliberately a zip rather than a live folder, because a second *editable* copy of `DECISIONS.md` or `BUILD_PLAN.md` is how two machines silently end up working from different versions.

### Conventions adopted during Part B

- **No `Co-Authored-By` trailers** in commit messages. This is a public research repository and the history should read as the author's own.
- **`.claude/` and `emails/` are git-ignored.** The first is per-machine tooling state that a plugin recreated inside the project root; the second is a safety net for correspondence that should never be committed.
- **`git status` is run as its own command before any commit**, never chained into the commit itself. A stray file was committed and pushed once during Part B precisely because the status output arrived too late to act on.

### What a second machine needs from Part B

Only Steps 9 and 10 — identity and an SSH key. Then:

```bash
git clone git@github.com:pedbad/persian-pronunciation.git ~/Sites/persian
```

Nothing else in Part B is repeated. The full session-opening prompt for a fresh machine is in `docs/START_PROMPT.md`, version B.
