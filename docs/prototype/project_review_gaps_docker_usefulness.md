# Project Review — Gaps, Docker Decision, and Usefulness Assessment

> **📌 Status update — 7 July 2026:** All six decisions arising from this review were agreed and recorded in `/DECISIONS.md`. §2.1's recommendation was adopted and *strengthened*: aeneas is skipped entirely, not merely replaced for production — MFA from day one (D2). Docker was accepted with a README-first amendment (D1), Whisper became the gatekeeper (D3), weights fixed at 60/40 (D4), plain-HTML-first frontend (D5), laptop hosting until pilot prep (D6). The current plan is `/FABLE_REVIEW.md`, executed via `/BUILD_PLAN.md`. Note the Docker sketch in §5 (python:3.10 base + aeneas) is superseded by BUILD_PLAN Step 21 (conda + MFA engine image) and the D1 amendment (Django runs natively in dev on the `langcen_base` scaffold; engine, worker, Postgres, and Redis run in compose).

**Date:** 7 July 2026
**Reviewed documents:** pronunciation tutorial (DTW revised), multilingual platform doc, LMS prototype handover, Phase 2 server architecture
**Purpose:** Identify what the brainstorming so far has missed, record the Docker deployment decision, and honestly assess how useful this would be for the Cambridge Language Centre and beyond.

---

## 1. What the documents already get right

Before the gaps, credit where due. The four documents are unusually coherent for a brainstorming set. The move from static `expected_ms` to proportional timing calculated from the native reference is the correct call and is enforced consistently across all four documents. The `position` validation rule (`transliteration[position] == vowel`) closes a genuinely dangerous silent-failure mode. The Phase 2 model review is production-minded in the right ways: PROTECT over CASCADE for attempts, versioned lessons, async task timestamps, retention metadata (`delete_after`), and check constraints. The funder document is honest about Whisper being a timing tool rather than the judge, and about the linguistic work being the real asset. That framing is correct and rare.

The gaps below are things *none* of the four documents address, or address only in passing.

---

## 2. Technical gaps

### 2.1 aeneas is a bigger risk than the docs acknowledge — including a licensing problem

The handover treats aeneas as the workhorse with MFA as a fallback. Three issues deserve to be promoted from footnote to front page:

**Maintenance.** aeneas last had a release (1.7.3) in March 2017. The Python 3.10 and numpy 1.23.5 pins in your setup instructions are symptoms of building on an abandoned library. Every year this gets harder, not easier.

**Licence.** aeneas is AGPL v3. For the Language Centre pilot this is fine. But the multilingual platform document pitches a commercial SaaS and a licensable scoring API — and AGPL's network copyleft means any service built on aeneas must offer its full source to users, which is incompatible with the "licence the engine to LMS platforms" business model. Montreal Forced Aligner is MIT-licensed. If the commercial vision is real, the alignment layer should be MFA (or a Whisper/wav2vec2-based aligner such as WhisperX or torchaudio's forced alignment API) from the start, not as a fallback.

**Linguistic soundness of character-level fragments.** Feeding aeneas one romanised character per line means espeak synthesises isolated letters ("s", "l", "m") as reference audio. That is not how those sounds appear in connected speech, and boundary accuracy for a vowel inside a word will be rough. The prototype's success criterion — "the â fragment has non-zero timestamps" — can pass while the boundaries are badly wrong. Add a validation checkpoint: hand-label the vowel boundaries for salâm and mamnun in Praat, and require aeneas boundaries within ±40–60 ms before declaring the pipeline proven. A phone-level aligner with a Persian grapheme-to-phoneme layer is the more defensible medium-term architecture.

### 2.2 Speaker mismatch will corrupt the acoustic score

MFCC + DTW against a single native reference conflates *pronunciation quality* with *voice identity*. A female learner compared against a male native speaker will score worse for reasons that have nothing to do with her vowels (different vocal tract length shifts all formants). The docs never mention this. Mitigations, in increasing order of effort: drop the first MFCC coefficient and add delta features; compare vowel formant ratios (F1/F2) rather than raw spectra for vowel quality; record multiple native references (at minimum one male, one female) and score against the closest; longer-term, replace raw DTW with a goodness-of-pronunciation (GOP) score from a phoneme recogniser. The calibration warning in the tutorial hints at this problem but does not name it.

### 2.3 There is no "did they even say the word?" gate

If a learner says the wrong word, mumbles, or submits silence, the current pipeline will still force-align and score *something* — the exact class of silent-wrong-answer bug the handover warns about, at the utterance level. Before scoring: run a voice-activity check (reject silence/too-short clips), compare Whisper's transcript against the expected text with a normalised edit-distance threshold, and reject clipped or extremely noisy audio with an actionable message ("we couldn't hear you clearly — try again closer to the microphone").

### 2.4 Whisper is currently decorative

Notably, `step7_score.py` never consumes the output of `step5_whisper_align.py`. For single-word A1 prompts, aeneas aligns both clips directly and Whisper contributes nothing to the score. Either give Whisper a real job (the wrong-word gate above; trimming leading/trailing silence; windowing aeneas for multi-word phrases) or remove it from the critical path and the deployment footprint until phrases get longer. This also cuts the biggest model download from the prototype.

### 2.5 No calibration or evaluation dataset plan

The docs correctly say the DTW-to-score conversion is uncalibrated, but no document plans the fix. Before any learner sees a number, you need a small labelled set: ~50–100 recorded attempts (real learners plus deliberate error recordings), each rated by two Persian teachers on the same 0–100 or band scale, with inter-rater agreement checked. Tune the calibration constants against that set and report the correlation. This is a week of work that turns "plausible demo" into "defensible tool", and it is exactly the evidence the Language Centre would ask for.

### 2.6 Engine versioning is missing from the data model

Phase 2 versions lessons but not the scorer. `assessment_payload` should record `scorer_version`, `profile_version`, and model identifiers (Whisper model name, aligner version). Otherwise every calibration tune silently makes historical attempts incomparable — fatal for progress-over-time charts and for any research use of the data.

### 2.7 Small inconsistencies to reconcile

The tutorial weights the final score 65% acoustic / 35% timing; the handover says 60/40. Pick one, define it once in the Pronunciation Profile (it will likely differ per language anyway). Also, the browser reality is unaddressed: MediaRecorder produces 48 kHz WebM/Opus, not 16 kHz mono WAV, so the upload endpoint needs an ffmpeg conversion step, file-size limits, and MIME validation — the Phase 2 metadata fields imply this but no document specifies it.

---

## 3. Product and design gaps

### 3.1 The frontend is a name, not a design

"React WaveformViewer" appears in all four documents and is specified in none. The core learner loop needs actual design work: see prompt → hear native audio → record (mic-permission UX, level meter, re-record) → wait (3–8 s of processing needs a designed, honest waiting state) → results → **tap a coloured region to hear the native vowel and your own attempt side by side**. That last interaction is where the learning happens; without it the colours are just a verdict. A one-page wireframe of this loop should exist before any Django work starts, because it will change the API (e.g., you need per-segment audio playback, which means the API must expose segment offsets for both recordings — the native segment timings are currently computed and thrown away).

### 3.2 Scores are not feedback

A red "â — 42" tells a learner they failed, not what to do. Each phoneme in the Pronunciation Profile should carry authored remediation copy ("this is the long 'â' as in British *father* — open wider and hold it longer") written by the linguistic consultant. This is cheap to add to the schema now (`vowel_map` entry gains an optional `hint` field, or hints live per-phoneme in `profile_config`) and expensive to retrofit. It also strengthens the funder story: the profiles become richer IP.

### 3.3 Accessibility — currently a compliance failure waiting to happen

Green/amber/red as the *only* encoding of correctness violates WCAG 1.4.1 (use of colour) and fails the ~8% of men with red-green colour vision deficiency. UK public sector bodies — including universities — are legally required to meet WCAG 2.2 AA for web services. Fixes are easy at this stage: pair colour with icons or patterns and always show the numeric/band label; specify keyboard operation for the record control; define what a screen reader announces for a waveform (a per-vowel results list is the accessible equivalent). Mixed-direction text (RTL Persian script alongside LTR transliteration) also needs deliberate handling in the UI spec.

### 3.4 Motivation design

Per-vowel percentages invite discouragement at exactly the moment (A1) when learners quit. Consider showing bands ("good / close / keep working") with the number available on tap, and lead with *improvement since last attempt* rather than absolute score. Store-everything (which Phase 2 already does) makes a "your â has improved 3 attempts in a row" narrative possible — that is the retention feature.

### 3.5 No user research loop

All four documents assume phoneme-level visual feedback is what learners want. That is plausible but untested. Before Phase 2 hardening, run the prototype output past 5–8 real learners (CULP Persian students are right there) in a think-aloud session, and past the Persian tutors who would recommend it. Also missing: any teacher-facing view. Even a minimal "class heat-map of weak phonemes" turns this from a self-study toy into something a course coordinator will champion.

---

## 4. Governance gaps

**Data protection.** Learner voice recordings are personal data under UK GDPR, and the platform docs propose keeping them for calibration and research. Missing: a consent step in the recording flow (with a separate, optional consent for research/calibration use), a stated retention period backing the `delete_after` field, a privacy notice, and — for a University deployment — a DPIA and clarity on storage location. None of this is hard, but it must exist before real students record anything.

**Authentication.** For Language Centre use, plan on Raven/SSO rather than standalone accounts; for the general platform, that slot should be pluggable.

**Licensing inventory.** Whisper (MIT), librosa (ISC), MFA (MIT) are all commercially safe; aeneas (AGPL v3) is not — see §2.1. Worth keeping a one-page licence inventory as dependencies grow.

---

## 5. The Docker decision (requested note from development)

**Status:** Accepted — development's recommendation is correct, and this stack is close to a best-case argument for containerisation.

### Context

The pipeline depends on a pinned interpreter (Python 3.10), a pinned numpy (1.23.5), an abandoned C-extension library (aeneas) that must find espeak at build time, and two system binaries (ffmpeg, espeak/espeak-ng) whose packaging differs across macOS and Ubuntu. The tutorial's troubleshooting table is essentially a list of environment-reproduction failures. Docker freezes this fragile environment once, and every developer, CI runner, and server then runs the identical image. It also matches how University IT and any future cloud host will want to receive the application.

### Options considered

| Option | Complexity | Reproducibility | Fit for uni IT / cloud | Notes |
|---|---|---|---|---|
| A. Bare VM + venv + setup docs | Low upfront | Poor — the troubleshooting table becomes ops reality | Weak | Every deploy re-fights aeneas/espeak |
| B. Docker Compose: web + worker + redis + postgres | Medium | Strong | Strong — standard handover artefact | **Recommended** |
| C. Managed PaaS (Heroku-like) | Low | Good | Mixed | System deps (espeak) and long tasks fit poorly; costs scale badly with audio workers |

### Decision

Adopt Option B. Build **two images**, not one: a slim `web` image (Django + gunicorn) and a heavy `worker` image (Celery + Whisper + aligner + librosa + ffmpeg + espeak-ng). This keeps web deploys fast, lets workers scale independently (they are the CPU-bound part), and means a broken audio dependency can never take down the API.

Sketch of the worker image:

```dockerfile
FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg espeak-ng libespeak-ng-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-worker.txt .
RUN pip install --no-cache-dir numpy==1.23.5 \
    && pip install --no-cache-dir -r requirements-worker.txt

# Bake the Whisper model into the image for deterministic cold starts,
# or mount a volume at /root/.cache/whisper instead to keep the image small.
RUN python -c "import whisper; whisper.load_model('medium')"

COPY . /app
WORKDIR /app
CMD ["celery", "-A", "config", "worker", "--concurrency=2", "-Q", "scoring"]
```

Compose services: `web`, `worker`, `redis` (broker/result backend), `postgres`, and a shared volume (or S3-compatible bucket) for audio files. Add healthchecks on all services and load the Whisper model once per worker process, not per task.

### Consequences

Easier: onboarding the Django developer (one `docker compose up`), CI (test in the same image you ship), handover to University hosting, later GPU adoption (swap base image, add nvidia runtime). Harder/watch-list: worker image size (~3–4 GB with the medium model baked in — acceptable; use a volume if it hurts), Apple Silicon vs linux/amd64 build targets (use `docker buildx`), and remembering that pinning via Docker *hides* the aeneas fragility rather than fixing it — §2.1 still stands.

### Action items

1. [ ] Add `Dockerfile.web`, `Dockerfile.worker`, `docker-compose.yml`, `.dockerignore` to the repo skeleton before Django work starts.
2. [ ] Decide model-in-image vs volume-mounted model cache.
3. [ ] Add a CI job that builds both images and runs `step8_validate_all.py` inside the worker image — this makes the container the canonical test environment.

---

## 6. How useful would this actually be?

### For the Cambridge Language Centre

The fit is better than a generic ed-tech pitch, for specific reasons:

**There are real cohorts with exactly this problem.** The Language Centre currently teaches Persian through CULP — an "Introduction to Persian (Farsi) Language and Culture" course and "Persian for Academic Purposes", the latter explicitly preparing students for fieldwork with a listening and speaking component. These are weekly, contact-hour-limited courses; pronunciation is precisely what a weekly group class cannot give individual feedback on, and hidden vowels are precisely the A1 pain point your engine targets. A tool that lets a student drill the week's phrases between classes, with per-vowel feedback, plugs the most acute gap in that format. Arabic — structurally the same hidden-vowel problem and your own stated second language — is also taught at the Centre, so a successful Persian pilot has an immediate internal expansion path.

**It fits the Centre's self-study tradition.** The Centre has a long-standing independent-learning offer (adviser-supported self-study, the John Trim Centre's resource collection). A pronunciation tool with stored progress is a natural modern extension of that model, and framing it that way will land better than framing it as replacing anything a tutor does.

**There is a serious research hook in Cambridge.** Automated assessment of learner speech is an active Cambridge research area (the ALTA Institute's work on automated language teaching and assessment, plus the Phonetics Laboratory in Theoretical & Applied Linguistics). A validated Persian phoneme-scoring dataset — teacher-rated learner attempts with alignments — is publishable research material and a credible basis for collaboration or studentship involvement. That is also your cheapest route to the calibration work in §2.5.

**Honest adoption barriers.** Cohorts are small (tens of students per year, not thousands), so the Centre justification is pedagogical value and research, not scale. Expect requirements for Raven login, WCAG 2.2 AA compliance (§3.3), a DPIA (§4), University-approved hosting (where the Docker image earns its keep), and — most binding — tutor time to author and QA lesson content and native recordings. The realistic path is a term-long supervised pilot inside one CULP Persian cohort with the course tutor as co-designer, measuring whether pronunciation outcomes and confidence actually improve. If that produces evidence, everything else (funding, expansion to Arabic, research collaboration) gets easier.

### In general

The funder document's core claims mostly survive scrutiny. Phoneme-level pronunciation feedback for Persian genuinely does not exist in mainstream tools: the serious commercial engines (ELSA, Speechace, Microsoft's Azure Pronunciation Assessment) centre on English, with Azure covering roughly 33 locales and offering full phoneme-level detail reliably only for English variants — Persian is not served. The underserved-languages wedge (Persian, Arabic, Swahili, Cantonese; heritage learners; institutional/diplomatic training) is real and better than competing head-on in English.

Two claims deserve softening before this document goes to anyone sceptical. First, "one engine, 99 languages via config" overstates it — the document itself admits tonal languages need new signal processing (pitch extraction, contour classification), which is code, not configuration; more accurate and still compelling: "one engine, per-language profiles, with feature extractors added per language *family*." Second, the moat needs naming honestly: Whisper, MFA and DTW are available to everyone; the defensible assets are the validated Pronunciation Profiles, the teacher-rated calibration data, and the pedagogical feedback layer (§3.2). The docs gesture at this ("the profiles are the asset") — lean into it harder, because a funder will ask.

Net assessment: as a Language Centre pilot, this is genuinely useful and well-matched to an existing need, with a credible research angle — worth building. As a global platform, the vision is coherent but the near-term claims should rest on the pilot evidence, one language done properly, before the 99-language story leads.

---

## 7. Priority list of the misses (summary)

1. Alignment layer risk: aeneas AGPL licence + abandonment + character-fragment fragility → plan MFA/Whisper-based alignment now, and validate boundaries against hand labels (§2.1).
2. No wrong-word/silence gate before scoring (§2.3) and Whisper currently unused by the scorer (§2.4).
3. Speaker mismatch in MFCC/DTW comparison (§2.2).
4. No calibration dataset or teacher-rating plan (§2.5) and no scorer versioning in the payload (§2.6).
5. Frontend/UX entirely unspecified — recording loop, waiting state, segment playback, feedback copy, accessibility (WCAG 2.2 AA), motivation design (§3).
6. GDPR consent, retention policy, DPIA, Raven/SSO (§4).
7. Docker/CI/deployment previously unmentioned — now decided, see §5.
8. Weighting constants inconsistent across docs; browser audio conversion unspecified (§2.7).
