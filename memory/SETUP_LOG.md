# SETUP_LOG — What Is Installed, and Why (plain-English appendix)

**What this is:** a non-programmer's explanation of every tool this project installs on a machine, what it is for, and how it was verified. Three purposes: (1) a reference when setting up a second machine, (2) a record of which versions were actually used, (3) raw material for the methods appendix of the paper or poster.

**How this differs from BUILD_PLAN.md:** the build plan says *what to type*. This file says *what the thing is and why it exists in this project*. Read this one first if the build plan feels like magic incantations.

**Sync:** lives in `memory/`, which is copied into the repo at BUILD_PLAN Step 13 and synced across machines by push/pull from then on.

---

## Part A — Your Mac (completed 7 August 2026, Pedram's Mac, macOS 25.5 / Apple Silicon)

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
