# FABLE_REVIEW — The Proposal, in Baby Steps

**Date:** 7 July 2026 · **Updated:** 7 August 2026 (D3 amendment, D9, revised timeline, Step 3b)
**Builds on:** `prototype/project_review_gaps_docker_usefulness.md` (the gap analysis) and your four brainstorming docs.
**Executable companion:** `BUILD_PLAN.md` (7 Jul 2026) turns Phases 0–5 into checked, command-by-command build steps on the `pedbad/langcen_base` scaffold (see DECISIONS.md D7/D8). This document remains the strategy and the "why".
**How to read this:** It's a single ordered path. Every step is small enough to finish in one sitting where possible, says *why* it exists, and has a "done when" so you always know whether you can move on. Nothing in a later phase starts until the checkpoint before it passes.

---

## The proposal in one paragraph

Prove the scorer honestly before building anything around it. First create a small kit of real recordings and hand-label the "true" vowel boundaries so you have a ruler to measure against (Phase 1). Then build the pipeline on the Montreal Forced Aligner *inside Docker from day one* — Docker satisfies development's requirement immediately, and skipping aeneas entirely (Decision D2) means never depending on an abandoned, AGPL-licensed library (Phase 2). A neural-aligner fallback stands ready only if MFA's Persian coverage disappoints (Phase 3). Add the safety gates and versioning that stop the scorer lying (Phase 4). Only then build the thinnest possible web app — one page, one lesson, record → score → coloured result (Phase 5). Finally, prepare a small supervised pilot with a CULP Persian cohort, which produces the evidence everything else (Arabic, funding, ALTA collaboration) depends on (Phase 6). React, the 99-language story, and the funder pitch all wait for pilot data.

---

## Decision log — D1–D8 agreed 7 July 2026, D9 added 7 August 2026

| # | Question | Decision | Status |
|---|---|---|---|
| D1 | Docker? | Yes — from the very first build, **and the README documents how to build and run from the very first build too** (Pedram's amendment) | ✅ Agreed |
| D2 | aeneas? | **Skipped entirely — Montreal Forced Aligner from day one** (stronger than originally proposed); wav2vec2 held as contingency | ✅ Agreed |
| D3 | Whisper's job? | Gatekeeper: checks the learner said the right word before anything is scored | ✅ Agreed |
| D4 | Score weights? | One constant: 60% acoustic / 40% timing, frozen until Phase 6 teacher calibration | ✅ Agreed |
| D5 | Frontend? | Server-rendered Django templates — now concretely the scaffold's Tailwind v4 + cotton components (see D5 amendment); React only after the pilot validates the design | ✅ Agreed |
| D6 | Where does it run? | Pedram's laptop until pilot prep — engine/services via `docker compose`, Django natively in dev (see D1 amendment) | ✅ Agreed |
| D7 | Repo? | Public GitHub (`pedbad/persian-pronunciation`), created from the `langcen_base` scaffold, kept as a second remote | ✅ Agreed |
| D8 | Learner accounts? | The scaffold's invite-email flow — admin-created / CSV-seeded, no open signup (replaces the invite-code idea) | ✅ Agreed |
| D9 | Second native reference? | Two per lesson, stored as `NativeReference` rows: score against both, keep the better result (never a clip against itself); the practice page plays the winning voice | ✅ Agreed 7 Aug 2026 |

The authoritative copy, with full plain-English rationale and consequences, lives in `DECISIONS.md`. When any document contradicts another, DECISIONS.md wins.

---

## How the phases fit together

```
Phase 0        Phase 1         Phase 2          Phase 3          Phase 4        Phase 5         Phase 6
housekeeping → real audio  →  MFA pipeline →  contingency:  →  make scorer →  thin web    →  Language Centre
& one email    + hand labels   in Docker        wav2vec2, only   trustworthy    slice demo      pilot
(1 evening)    (1 weekend)     (1–2 wks eves)   if MFA fails     (1 wk eves)    (3–4 weeks)     (next term)
```

---

## Phase 0 — Housekeeping (one evening)

### Step 1 — Put everything in git *(superseded in detail by BUILD_PLAN.md Part B)*
**Why:** Four markdown docs and future code with no version control is how good decisions get lost.
**Do:** Per D7 (7 Jul 2026) this is no longer a `git init` in this folder: the repo is created by **cloning the `pedbad/langcen_base` scaffold** into `~/Sites/persian-pronunciation`, re-pointing remotes, and copying these documents into its `docs/` folder — follow BUILD_PLAN.md Steps 11–13 exactly. The README rule from your D1 amendment stands: a "How to build and run" section updated at *every* phase, so anyone can rebuild the project from the README alone.
**Done when:** BUILD_PLAN Steps 11–13 checks pass (repo public on GitHub, docs pushed).
**Time:** 30 minutes.

### Step 2 — Create DECISIONS.md
**Why:** Your tutorial says 65/35 weighting, your handover says 60/40. Small today; a silent bug generator once a developer joins.
**Do:** Copy the decision-log table above into `DECISIONS.md`. Add a line to each older doc's top: "Where this conflicts with DECISIONS.md, DECISIONS.md wins."
**Done when:** Committed. *(Done — `DECISIONS.md` was created on 7 July 2026 with D1–D8 agreed and explained in plain terms; D9 added 7 August 2026.)*
**Time:** 15 minutes.

### Step 3 — Send one email to the Language Centre
**Why:** Everything in Phase 6 needs a Persian tutor as ally, and academic lead times are long. Booking the conversation costs nothing now and would cost you a term later.
**Do:** Two short paragraphs to the CULP coordinator (langculp@langcen.cam.ac.uk): you're building a tool that gives Persian learners per-vowel pronunciation feedback on the hidden-vowel problem; could you have 30 minutes with a Persian tutor this term or early next, to show a demo and ask what phrases an A1 learner most needs. Don't oversell — you're asking for advice, which people give more readily than endorsement.
**Done when:** Sent. (The meeting itself is Step 25 — a demo will exist by then.)
**Time:** 20 minutes.

### Step 3b — Send one more email: who owns the DPIA / ethics approval? *(added 7 Aug 2026)*
**Why:** Recording students' voices is personal-data processing, and University ethics and data-protection sign-off can take longer than the entire build. Phase 6 (Step 24) is too late to *start* that conversation — this is the one item that could sink the pilot date even if all the code works.
**Do:** One short email — in the same thread as Step 3, or to your departmental research-ethics contact — asking two things: for a term-long pilot where CULP Persian students record short phrases, who handles the DPIA? And is ethics review needed if it runs as a Language Centre activity versus as your own research project (open question 3)? You're asking about process and lead time, not requesting approval yet.
**Done when:** Sent; when the answer arrives, note the owner and expected lead time as a dated entry in DECISIONS.md.
**Time:** 20 minutes.

---

## Phase 1 — Real audio and ground truth (one weekend)

### Step 4 — Build the test kit
**Why:** Every claim in Phases 2–4 is tested against these clips. Recording them all now, once, means every later comparison is fair.
**Do:** For each of your two words (salâm, mamnun), collect **six** recordings:

1. **native-A** — primary native reference (Forvo, or a native speaker on a phone voice memo)
2. **native-B** — a *different* native speaker, ideally different sex to native-A
3. **learner-good** — you, saying it as carefully as you can
4. **learner-wrong-vowel** — you, deliberately wrong: "sa-LOM" instead of "sa-LÂM", "mam-NON" instead of "mam-NUN"
5. **learner-fast** — your careful version, but quick
6. **learner-slow** — your careful version, drawn out

Convert everything: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`. Name them consistently: `audio/salaam_native_a.wav`, `audio/salaam_wrong_vowel.wav`, etc.
**Done when:** 12 WAV files, 16kHz mono, each 0.3–3 seconds, listed in a little `audio/README.md` table.
**Time:** 2–3 hours (finding a second native speaker is the slow part — a colleague, or a second Forvo contributor for the same word, is fine).

### Step 5 — Hand-label the vowel boundaries in Praat
**Why:** This is the single most important new step in the whole plan. The original docs' success test was "the aligner returned non-zero timestamps" — which can pass while the boundaries are badly wrong. You need the *true* answer to measure against, and only a human can provide it — MFA (Decision D2) gets judged against these labels in Step 9. Bonus: an hour in Praat teaches you more about your own pipeline than a week of coding.
**Do:** Download Praat (free, praat.org). Open `salaam_native_a.wav` → View & Edit. You'll see the waveform and below it a spectrogram. Vowels are the regions with strong dark horizontal bands (formants). Click-drag to select the â vowel; Praat shows the selection's start and end times. Write them down. Repeat for each target vowel in native-A, native-B, and learner-good for both words. Save as `ground_truth.json`:

```json
{
  "salaam_native_a.wav": { "a": [0.09, 0.16], "â": [0.31, 0.60] },
  "salaam_learner_good.wav": { "a": [0.11, 0.19], "â": [0.36, 0.70] }
}
```
**Done when:** `ground_truth.json` has entries for at least 6 of the 12 files, and you can explain to someone else how you found a vowel in a spectrogram.
**Time:** 2–3 hours including learning Praat.

> **Checkpoint 1:** You have real audio and a ruler. Nothing has been "built", but you can now catch the pipeline lying — which no document so far could.

---

## Phase 2 — The MFA pipeline, in Docker, tested honestly (1–2 weeks of evenings)

Decision D2 means aeneas is never installed. A pleasant side effect: the Python 3.10 pin, the numpy pin, espeak, and most of the tutorial's troubleshooting table existed *only* to keep aeneas alive — they all vanish. MFA works differently from a Python library: it's a command-line tool that processes a *folder* of audio + text pairs. This phase is about learning that way of working on your two words.

### Step 6 — Build the container (and start the README rule)
**Why:** Decision D1 — the environment lives in a file, not in a machine, from the very first build.
**Do:** Create `Dockerfile.engine` in the repo:

```dockerfile
FROM condaforge/miniforge3:latest

# Alignment layer (Decision D2): Montreal Forced Aligner — MIT licence, maintained
RUN mamba install -y -c conda-forge montreal-forced-aligner && mamba clean -a -y

# Whisper (gatekeeper, Decision D3) + audio analysis for the scorer + TextGrid parsing
RUN pip install --no-cache-dir openai-whisper librosa soundfile scipy praatio

WORKDIR /app
```

Then:

```bash
docker build -f Dockerfile.engine -t persian-mfa .
docker run --rm persian-mfa mfa version
docker run --rm persian-mfa python -c "import whisper, librosa, praatio; print('all OK')"
```

Put exactly these commands into README.md's "How to build and run" section — the D1 rule: anyone with Docker can rebuild the project from the README alone, at every phase from now on.
**Done when:** `mfa version` prints a version, the import check prints `all OK`, and the README says how.
**Time:** 1–2 hours.

### Step 7 — Download the Persian models and align your first file
**Why:** MFA needs two downloads per language: an *acoustic model* (how Persian sounds) and a *pronunciation dictionary* (word → phonemes). This step confirms Persian coverage is real, and produces your first alignment.
**Do:** List what's available and fetch the Farsi/Persian entries (also browsable at mfa-models.readthedocs.io):

```bash
docker run --rm -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa mfa model download acoustic
docker run --rm -v "$(pwd)/mfa_models:/root/Documents/MFA" persian-mfa mfa model download dictionary
```

Then prepare a corpus folder — MFA's convention is audio and transcript side by side: `corpus/salaam_native_a.wav` next to `corpus/salaam_native_a.txt` containing سلام. Align with `mfa align corpus/ <persian_dictionary> <persian_acoustic_model> aligned/`. Open `aligned/salaam_native_a.TextGrid` in Praat — pleasingly, Praat displays it as labelled tiers on the timeline, so you can eyeball MFA's phone boundaries directly against your own Step 5 labels.
**Done when:** A TextGrid exists for salaam_native_a with visible word and phone boundaries.
**Time:** An evening, downloads included. *If the Persian model or dictionary turns out to be missing or poor, jump to Phase 3 — that's exactly what it's for.*

### Step 8 — Write the alignment wrapper
**Why:** The scorer from the handover expects a Python function returning `[{sound, start, end}, ...]`. MFA speaks TextGrid files. This wrapper is the bridge — the only genuinely new code Decision D2 costs us.
**Do:** Write `align_mfa.py` with a function `align_phonemes(audio_path, lesson)` that: copies the audio and its transcript into a temporary corpus folder, runs `mfa align`, parses the TextGrid's phone tier with `praatio`, and returns the fragments list. One conceptual upgrade over the aeneas design: MFA returns *phones* (real speech sounds such as /ɑː/), not transliteration characters — so each target vowel is located by **matching the `phoneme` field of your vowel_map** (the first /æ/, the /ɑː/, and so on), not by character position. Keep the `position` field: it still validates lesson data exactly as the handover's Rules 2–3 demand. Practical note: MFA's phone symbols may differ slightly from the IPA in your lesson JSON (e.g. `ɒː` vs `ɑː`), so include a small symbol-mapping dictionary — that mapping later becomes part of each language's Pronunciation Profile. Finally, point `step7_score.py` at this module (the scorer itself needs no other change), and type up the scorer and validator scripts from the handover doc, skipping `step6_aeneas_align.py`.
**Done when:** `align_phonemes()` returns sensible fragments for all four native and learner-good clips.
**Time:** 2–3 evenings — the priciest step in this phase, and worth every minute.

### Step 9 — Measure MFA against your hand labels
**Why:** The honesty test. MFA must earn its place with numbers, exactly as aeneas would have had to.
**Do:** Write a ~30-line `compare_boundaries.py`: for each file in `ground_truth.json`, run `align_phonemes()`, and for each target vowel print the difference (in milliseconds) between MFA's start/end and yours. Produce a small table.
**Done when:** You have the table. **Interpretation:** errors within ±50 ms *and* within ~30% of the vowel's own duration → MFA passes; outside either bound → shaky, try the fixes in MFA's docs (beam settings, a cleaner recording) before judging; >100 ms or vowels landing on consonants → go to Phase 3. *(The relative bound matters because a Persian short vowel may last only 60–100 ms — a "passing" ±50 ms error on a 70 ms vowel means mostly measuring the wrong slice of audio. And set expectations: isolated sub-second words are the hardest case for any forced aligner, which earns its accuracy from context — so exhaust the config fixes before declaring Phase 3.)*
**Time:** An evening.

### Step 10 — Run the score matrix
**Why:** A scorer you can trust must rank your six clip types sensibly. This is calibration on a budget, and it directly tests the two dangerous failure modes named in the handover.
**Do:** Score every learner-side clip against native-A, for both words, and fill in this table (add it to the repo as `results/score_matrix.md`). *(Against native-A alone, deliberately — the native-B row must stay a fair test. Production scoring is best-of-both-references per D9, under which a clip is never scored against itself.)*

| Clip vs native-A | Expected | salâm actual | mamnun actual |
|---|---|---|---|
| native-B | high (≥80) | | |
| learner-good | fairly high | | |
| learner-wrong-vowel | clearly lower than learner-good | | |
| learner-fast | ≈ learner-good | | |
| learner-slow | ≈ learner-good | | |

Optional extra column, cheap and potentially decisive *(added 7 Aug 2026)*: MFA is built on Kaldi, so a per-phone alignment-confidence score (a crude goodness-of-pronunciation measure) can be pulled from the same alignment run DTW already needs. Record it alongside the DTW score. If it ranks the six clip types better than DTW does, that's worth knowing *before* Phase 5 — and it naturally sidesteps speaker mismatch, because it compares the learner against the acoustic model rather than against one speaker's voice.

**Done when:** Table complete, plus three written sentences on whether the ordering holds. The **native-B row is the killer test**: if a second native speaker doesn't score green, the scorer is measuring *voice identity* (who is speaking), not *pronunciation* — that's the speaker-mismatch problem from the gap review, and Step 15 exists to fix it.
**Time:** An evening.

> **Checkpoint 2:** You know, with numbers, whether the design works — and you have a Docker image plus a README that rebuilds it, so anyone (including the future developer) can reproduce your results with one command. This checkpoint is genuinely publishable progress.

---

## Phase 3 — Contingency: wav2vec2 alignment (only if MFA fails Step 9)

Skip this phase entirely if MFA passed the boundary test. It exists so a disappointing Persian MFA model can't stall the project.

### Step 11 — Try wav2vec2 forced alignment
**Why:** Modern neural aligners handle lower-resource languages well. Persian wav2vec2 models exist on Hugging Face (e.g. `m3hrdadfi/wav2vec2-large-xlsr-persian-v3`), and torchaudio has a built-in forced-alignment API. One licence caution, in the spirit of D2: Meta's multilingual MMS aligner weights are non-commercial (CC-BY-NC) — prefer an Apache/MIT-licensed Persian model.
**Do:** Write a second implementation of the Step 8 wrapper interface (`align_phonemes()`), then rerun `compare_boundaries.py` and the score matrix against it.
**Done when:** Same clips aligned, boundary table produced.
**Time:** A weekend.

### Step 12 — Record the outcome in DECISIONS.md
**Do:** Whichever aligner passes the boundary test becomes the production aligner — add a dated entry under D2 with the numbers. If both pass, MFA wins (simpler, and the phonetics-research standard).
**Done when:** DECISIONS.md names the aligner, with evidence.
**Time:** Half an hour.

---

## Phase 4 — Make the scorer trustworthy (a week of evenings)

### Step 13 — Add the audio sanity gate
**Why:** Today, silence or a cough gets force-aligned and scored. Garbage in, confident-looking garbage out.
**Do:** One function, `check_audio(path)`, returning OK or a *human-friendly* reason: too short (<0.3 s), too long (>10 s), too quiet (RMS energy below threshold), clipped (many samples at maximum). Run it before any alignment.
**Done when:** A silent WAV and a deliberately clipped WAV both get rejected with sensible messages; your 12 real clips all pass.
**Time:** An evening.

### Step 14 — Give Whisper its real job: the wrong-word gate
**Why:** Decision D3. If the learner says a different word, the scorer must say "we heard something else", not produce a meaningless score.
**Do:** Transcribe the learner clip with Whisper (`language="fa"`), normalise both strings (strip punctuation, diacritics, whitespace), and check the expected word appears in the transcript (or use a similarity ratio ≥ ~0.6 via `difflib.SequenceMatcher`). On failure return: *"It sounds like you said something different — listen to the native recording and try again."*
**Done when:** Recording yourself saying a completely different word gets caught, **and** every correct-word clip in the test kit — learner-good, fast, slow, native-A, native-B, both words — passes the gate: zero false rejections *(D3 amendment, 7 Aug 2026)*. Whisper is at its flakiest on sub-second single-word clips, and a gate that wrongly tells a learner "you said something different" is as damaging as scoring a wrong word. (Your learner-wrong-vowel clips *should still pass* this gate — one wrong vowel is exactly what the scorer, not the gate, is for.)
**Time:** An evening.

### Step 15 — Fix the speaker-mismatch problem (if Step 10's native-B row failed)
**Why:** A learner must never score worse because their voice differs from the reference speaker's.
**Do, in escalating order, retesting the score matrix after each:** (a) drop the first MFCC coefficient (it mostly encodes loudness) and add delta features; (b) score against *both* native-A and native-B and take the better result — *the default from day one since D9 (7 Aug 2026), so here just verify it's actually in effect*; (c) if still failing, park raw DTW and note "goodness-of-pronunciation scoring" as the Phase 6+ research question — this is precisely where an ALTA/phonetics collaboration earns its place.
**Done when:** native-B scores ≥80 against native-A on both words, or the limitation is documented honestly in DECISIONS.md.
**Time:** One to three evenings.

### Step 16 — Stamp versions into every result
**Why:** The moment you tune anything, all previous scores become incomparable — unless every payload says what produced it.
**Do:** Add to the output JSON: `"engine": { "scorer_version": "0.2.0", "aligner": "mfa-3.x", "weights": {"acoustic": 0.6, "timing": 0.4} }`. Bump `scorer_version` whenever behaviour changes.
**Done when:** Present in every scorer output; the Phase 2 doc's `assessment_payload` inherits it for free.
**Time:** 30 minutes.

### Step 17 — Tests and a one-job CI
**Why:** The pure functions (`timing_score`, `colour_from_score`, `validate_vowel_map`, `check_audio`) are cheap to test and are where silent regressions hide.
**Do:** `pip install pytest`, write ~10 small tests, run them inside the container. Optional but worth it: a GitHub Actions workflow that builds the image and runs pytest on every push.
**Done when:** `docker run --rm -v "$(pwd):/app" persian-mfa pytest` is green.
**Time:** An evening (+1 for CI).

> **Checkpoint 3:** A command-line scorer that refuses bad input, catches wrong words, treats different voices fairly (or says it can't yet), stamps its own version, and runs identically anywhere Docker runs. *This* is what gets wrapped in Django — not the raw prototype.

---

## Phase 5 — The thinnest possible web slice (3–4 weeks, with your developer)

The goal is **one page**: choose a word → hear the native → record → wait honestly → see the coloured result → tap a vowel to hear native vs you. No course structure, no dashboards.

> **Updated 7 Jul 2026:** this phase is built on the `langcen_base` scaffold (D7), which already ships accounts, login, and the learner invite-email flow (D8) — BUILD_PLAN.md Parts C and F are the executable version of this phase. Django runs natively in dev; Postgres, Redis, and the worker run in compose (D1 amendment).

### Step 18 — Compose skeleton
**Do (developer):** `docker-compose.yml` with three services — `worker` (Celery, built on the engine image: MFA + Whisper + the scorer), `redis`, `postgres` — sharing a volume for audio; Django itself runs natively in dev (D1 amendment; BUILD_PLAN Step 29). The worker loads models once at startup, not per task. One design note with teeth *(added 7 Aug 2026)*: call MFA through its `align_one`/server mode rather than a fresh `mfa align` per attempt — MFA's per-run startup (corpus validation, model loading) can push a cold alignment to 15–30+ seconds. Measure the real dispatch-to-result latency here: the 3–8 s figure quoted elsewhere is a guess, and Step 21's "analysing…" wording must be honest about the number you actually measure.
**Done when:** `docker compose up` starts all three; natively-run Django connects and the admin loads.

### Step 19 — Models and seed data
**Do (developer):** Implement the *hardened* models from `phase_2_transitioning_to_server_architecture.md` (they're good — use them as written, including `validate_vowel_map`), plus the engine-version field from Step 16. Seed the two lessons.
**Done when:** Both lessons visible and editable in Django admin, and admin refuses a lesson whose vowel_map points at a consonant.

### Step 20 — Upload endpoint and attempt lifecycle
**Why this needs a step of its own:** Browsers don't record 16 kHz WAV. MediaRecorder produces 48 kHz WebM/Opus, so the server must convert.
**Do (developer):** `POST /api/v1/lessons/{slug}/attempts/` — validate size/MIME → convert with ffmpeg → `check_audio` gate → create `UtteranceAttempt` (QUEUED) → dispatch Celery → return attempt id. Plus `GET /api/v1/attempts/{id}/` for polling. The Celery task runs gate → align → score → stores payload, following the lifecycle in the Phase 2 doc.
**Done when:** `curl` an audio file in, poll, get the scored JSON back.

### Step 21 — The practice page
**Do (developer, with you on wording):** One Django template built from the scaffold's cotton components (`<c-card>`, `<c-button>`…) plus a small amount of plain JavaScript for MediaRecorder — still no React (D5 amendment). Build in the things the gap review flagged, from the start rather than retrofitted: every coloured region also carries an **icon and text label** (never colour alone); the record button works by keyboard; the 3–8 s wait shows an honest "Analysing your vowels…" state; each vowel region is a button that plays the native segment then your segment. (That playback needs the *native* segment times in the payload — currently computed and thrown away; add them — plus, per D9, the id of the winning reference, so the page plays the native voice the score was actually measured against.)
**Done when:** You — not the developer — can do the full loop on your laptop, and so can someone who can't distinguish red from green.

### Step 22 — Hints, not verdicts
**Do (you, with the tutor when available):** Add an optional `"hint"` per vowel_map entry — *"the long â as in British 'father': open wider, hold it longer"* — displayed under any amber/red vowel.
**Done when:** A failed â shows advice, not just a number.

> **Checkpoint 4:** `docker compose up` + `npm run dev` → record → coloured, clickable, explained result. This is the demo for the tutor meeting, and it is worth pausing here to show people before building further.

---

## Phase 6 — Language Centre pilot preparation (next term)

### Step 23 — The tutor meeting (booked in Step 3)
Show the demo. Ask three questions: would you point your students at this between classes? Which 15–20 phrases should the A1 set contain? What should the feedback wording say? Their answers *are* the product spec for this phase.

### Step 24 — Consent, privacy, retention
Add a consent screen before first recording (with a separate optional tick for "my recordings may be used anonymised for research/calibration"), a plain-English privacy notice, a concrete retention period wired to `delete_after` plus a cleanup job, and ask the Centre/department who handles the DPIA. Accounts come from the scaffold's invite-email flow (D8) — onboard the cohort with `seed_students` from a class-list CSV; Raven/SSO can wait.

### Step 25 — Author the real A1 lesson set
15–20 phrases chosen by the tutor; native reference recordings from **two speakers (one male, one female)**; vowel maps written and validated; hints written by the tutor.

### Step 26 — Teacher calibration (the step that makes the scores mean something)
Collect ~50 attempts (pilot volunteers plus your deliberate-error kit). Two Persian teachers independently rate each on the same scale. Check the raters roughly agree with each other; then tune the DTW calibration and weights until machine scores correlate with teacher scores; report the correlation in DECISIONS.md and bump `scorer_version`. This dataset is also the seed of the research asset — the natural thing to bring to an ALTA/phonetics conversation.

### Step 27 — Five-learner think-aloud + accessibility pass
Watch five learners use it, saying their thoughts aloud. Fix the top confusions only. Run a basic WCAG check (colour contrast, keyboard-only walkthrough, screen-reader pass over the results list).

### Step 28 — The pilot itself
One CULP Persian cohort, one term, tutor on side. Decide the success measures *before* it starts — e.g. weekly active use by half the cohort, pre/post pronunciation improvement rated blind by a teacher, learner confidence survey. Write the results up honestly.

> **Checkpoint 5:** You have evidence. Every ambition in the multilingual platform document — Arabic next, funding, research collaboration, the commercial engine — now stands on data instead of hope.

---

## What NOT to build yet (and what unlocks each)

**React app** — unlocked by the pilot settling the design. **Arabic** — unlocked by pilot evidence plus a second linguistic consultant. **Tonal languages / pitch tracking** — new signal-processing code, not configuration; unlocked by revenue or research funding. **Real-time feedback** — a different architecture; park it. **Teacher dashboards** — after the pilot proves learners come back. **The funder pitch deck** — after Checkpoint 5, when the "one engine" story has a validated language behind it (the aligner licence problem is already solved — D2 chose MIT-licensed MFA).

---

## Rough timeline

> **Revised 7 Aug 2026:** building had not started by early August, so the original mid-July dates shift by roughly a month. The critical path is no longer code: it is (a) the September developer's availability (open question 2) and (b) the DPIA/ethics lead time (Step 3b). If either slips, the pilot moves to Lent term 2027 — an honest Lent pilot beats a rushed Michaelmas one.

| Phase | Effort | Calendar guess (revised 7 Aug 2026) |
|---|---|---|
| 0–1: housekeeping, audio, ground truth | 1 evening + 1 weekend | mid-August 2026 |
| 2: Docker prototype, honest test | 1–2 weeks of evenings | end of August |
| 3: contingency — only if MFA fails the boundary test | 0–1 weekend | early September |
| 4: harden the scorer | 1 week of evenings | mid-September |
| 5: thin web slice | 3–4 weeks (developer) | October |
| 6: pilot prep → pilot | prep in October/November | late Michaelmas (Nov–Dec 2026) or Lent 2027 |

---

## Open questions for you (answer as you go, no rush)

1. Who is your second native speaker (Step 4)? This is the earliest hard dependency — and since D9, native-B is load-bearing: it ships in every lesson as a scoring reference, not just a test clip.
2. Does the Django developer exist yet, and roughly how many hours can they give in September?
3. Should the pilot run as a Language Centre activity or as your own research project with Centre cooperation? It changes who owns the DPIA and the data.
4. When the tutor meeting happens, do you want an Arabic tutor in the room too? It costs nothing and warms up language number two.
