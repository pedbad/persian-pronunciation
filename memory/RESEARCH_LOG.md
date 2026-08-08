# RESEARCH_LOG — Material for the Paper / Poster (append-only)

**What this is:** the raw material for a short paper or poster on this project for language-teaching venues — kept as it happens, because reconstructing it later is how publications die. Whenever something publication-worthy happens, it gets a dated entry here: a design decision with pedagogical rationale, an evaluation number, an honest failure, a pilot observation.

**Likely venues (to refine with the Language Centre / tutor):** ReCALL (EUROCALL's journal), CALICO Journal, Language Learning & Technology, System; or a poster at EUROCALL / BAAL / a CALL SIG. The Cambridge angle (ALTA Institute, Phonetics Lab) may suggest a co-author later.

**The likely story arc of the paper:**
1. *Problem:* Persian's hidden vowels are the A1 pain point; per-phoneme pronunciation feedback for Persian exists in no mainstream tool.
2. *Method:* forced alignment (MFA) + dual-native-reference DTW scoring, with an honesty-first evaluation design (hand-labelled ground truth before any pipeline claim).
3. *Evaluation:* boundary accuracy vs hand labels; the six-clip score matrix incl. the native-B fairness test; teacher-calibration correlation.
4. *Pilot:* one CULP cohort, one term — usage, outcomes, learner confidence.
5. *Honest limitations:* what didn't work, and what that means for low-resource pronunciation CALL.

**Publication-relevant process note:** anything using learner data in a publication depends on the research-consent tick-box (FABLE_REVIEW Step 24) and the DPIA/ethics answer (Step 3b). Log the dates those happen.

**Entry format:** `## YYYY-MM-DD — tag (design / evaluation / pilot / limitation / process) — note`

---

## 2026-08-07 — design — evaluation-first methodology locked in before any code

The project's central methodological claim, decided before implementation: no pipeline component is trusted until measured against human ground truth. Hand-labelled vowel boundaries in Praat (BUILD_PLAN Step 20) come before the aligner runs; the aligner must beat ±50 ms *and* ≤30%-of-vowel-duration bounds (Step 25); the scorer must rank a six-clip test kit sensibly, including a second-native-speaker fairness test (Step 26). This "catch the pipeline lying" design is itself worth a section in the paper — most CALL prototypes report only that their tool ran, not that it measured the right thing.

## 2026-08-07 — design — dual native references to separate voice identity from pronunciation quality (D9)

MFCC+DTW against a single reference voice conflates *who is speaking* with *how well they pronounce* (vocal-tract length shifts formants). Decision D9: every lesson ships two native references (different speakers, ideally different sexes); attempts are scored against both, keeping the better result; the learner hears the winning voice. Testable prediction for the evaluation section: native-B scored against native-A alone should be green *before* this mitigation is credited with anything.

## 2026-08-07 — process — plain-English setup appendix started (`memory/SETUP_LOG.md`)

Part A of the build (developer tooling on macOS) is now documented for a non-specialist reader in `memory/SETUP_LOG.md`: what each tool is, why this project needs it, the exact version installed, and how it was verified. Intended as methods-appendix material — CALL papers routinely state that a system "was implemented in Python" without recording the reproducibility measures, and this project's Docker-first, ground-truth-first commitments are only credible if the environment behind them is written down. Also the practical reference for setting up Pedram's second machine. Continue appending a section per completed Part.

## 2026-08-07 — design — Whisper as gatekeeper, not judge (D3 + amendment)

Forced alignment scores *something* even when the learner says the wrong word or nothing — the worst failure of a learning tool is confident feedback on speech that never happened. Whisper's only role is the wrong-word gate. The 7 Aug amendment adds the symmetric requirement: the gate's false-rejection rate on correct attempts must be zero on the test kit, because wrongly rejecting a good attempt is equally damaging pedagogically. Both directions belong in the evaluation table.

## 2026-08-07 — design — reference-corpus design under a single, non-repeatable collection opportunity

The native reference recordings are being collected during one trip to Iran in August 2026. There is no second opportunity, and the corpus cannot be extended later by the same speakers. That constraint drove a deliberate redesign of the recording script, and the design principle is worth stating in the methods section because it generalises: *when reference data collection is a one-shot event, record what is impossible to reconstruct first, not what the current prototype happens to need.*

Four categories were added on that basis, in priority order ahead of most vocabulary:

1. **Sustained isolated vowels** — each of the six Persian vowels held for roughly three seconds, twice per speaker. This yields a clean per-speaker measurement of vowel-space position, free of coarticulation and speaking-rate effects. It converts D9's dual-reference argument from a design rationale into something measurable: the acoustic distance between the two reference speakers' vowel spaces can be quantified and reported, rather than assumed to be large enough to matter. Extracting equivalent measurements from running speech is substantially noisier and may be infeasible for short single-word clips.
2. **Controlled consonant frames** — real Persian words holding consonants constant while varying only the vowel (the *d—r* and *s—r* frames; the latter potentially yields all six vowels in one environment from one voice). Cross-word vowel comparisons confound the vowel with its neighbours; within-frame comparisons do not.
3. **Homographs** — written forms with two or three valid readings distinguished only by unwritten short vowels (گل *gol*/*gel*, مرد *mard*/*mord*, کرد *kard*/*kord*, ملک *melk*/*malek*/*molk*). These are the clearest available demonstration of the pedagogical problem the system addresses, recorded in the same voice under identical conditions, and are the strongest candidate for a worked example in the paper.
4. **Room tone at both ends of every session** — ten seconds of silence. Establishes the noise floor required to interpret any acoustic measurement from that speaker, and supplies the silence-rejection gate with authentic rather than synthesised silence for testing.

Also captured: carrier-phrase versions of the pilot words (isolated citation forms differ systematically from the same word in connected speech), ezâfe constructions (an unwritten linking vowel learners routinely omit — the same class of problem as the hidden short vowels, one level up), and native slow-versus-fast productions of the pilot words. That last item addresses a specific confound: with a 40% timing weight in the score (D4), it must be possible to say how much score variation is attributable to speaking rate alone in *native* speech before interpreting a learner's timing penalty.

A secondary observation from building the minimal-pair set, relevant to lesson design generally: **Persian's contrast density is highly uneven.** The /æ/–/ɑː/ and /o/–/uː/ oppositions generate minimal pairs freely; clean /e/–/iː/ pairs barely exist. Syllabus design that mechanically covers every vowel pair therefore either invents unnatural items or drills contrasts that carry little functional load. Following the language's actual contrast density is the better principle, and the asymmetry itself is worth reporting for other low-resource pronunciation work.

## 2026-08-07 — limitation — speaker recruitment and recording conditions must be reported honestly, not glossed

The reference speakers are recruited opportunistically during a personal trip, recorded in domestic rooms on a laptop microphone. This is a **convenience sample under field conditions**, not a controlled corpus, and the paper must say so plainly. Overstating it would be both dishonest and easy for a reviewer to detect.

What the methods section has to state, and what is therefore being logged per speaker at collection time in a private file (`SPEAKER_LOG.md`, outside the repository, the only place identities exist):

- **Recruitment** — opportunistic, personal contacts, during a single visit; number of speakers; no compensation.
- **Speaker characteristics** — sex, age range, region grown up in, region currently resident, other languages spoken. Regional origin matters because Tehrani is the teaching standard for the CULP course; a strongly regional reference speaker is usable but must be labelled, not silently averaged into the reference set.
- **Sex composition, and why it is not incidental** — D9 exists because MFCC/DTW comparison against a single voice conflates vocal-tract identity with pronunciation quality, and vocal-tract length is the dominant axis of that confound. Two references of the same sex would substantially weaken the mitigation, so the target is at least one female and one male speaker per lesson, and the achieved composition must be reported rather than the intended one.
- **Recording conditions** — domestic rooms with soft furnishings, no sound booth, laptop microphone, lossless capture, measured noise floor per session, no post-processing of any kind beyond trimming (no noise reduction, normalisation, EQ or fades — these alter exactly the acoustics being measured).
- **Consent procedure** — verbal consent recorded on tape at the head of each session, tracked as **two separate permissions**: use within the application, and inclusion of the audio file in a public repository. A speaker may grant the first and decline the second; recordings so marked never enter the repository but can still drive the engine locally. Withdrawal procedure documented, including removal from git history.
- **Items rejected by speakers** — words the script proposed that a native speaker judged unnatural or archaic were skipped and logged. Native judgement outranked the script. This is worth reporting: it is a small but real source of variation between speakers' item sets.

**Limitations that follow, to be stated rather than defended:** a two-to-four speaker reference set cannot represent Persian, and no claim of that kind is made — the references are teaching models for one pilot, not a phonetic corpus. Field recording conditions raise the noise floor relative to laboratory corpora, which bounds the precision of any boundary or distance measurement reported. And because speakers were recruited through personal contacts, they are not independent of one another in region or social background.

**The one methodological consolation, worth arguing rather than merely conceding:** learners in the pilot will record themselves on their own laptops and phones, in their own rooms. Reference audio captured under comparable domestic conditions is arguably *better* matched to the learner audio it will be compared against than studio recordings would be — a channel and environment mismatch between reference and attempt is itself a documented source of error in acoustic comparison. The honest framing is that field conditions cost precision and buy ecological validity, and that the trade was made deliberately.

Note also that this consent process is **separate from, and additional to**, the learner-data consent that the DPIA/ethics question (FABLE_REVIEW Step 3b) covers. Two distinct groups of people, two distinct permissions, two dates to record.

## 2026-08-08 — method — computational reproducibility is a claim, and it has to be built in rather than asserted

Setting up the second machine exposed a gap between what this project *promised* about reproducibility and what it could actually deliver. Decision D1 has said since July that anyone should be able to rebuild the project at any point in its history. The mechanism was a `requirements.txt` — and a requirements file cannot deliver that. It lists some direct dependencies, often loosely; it says nothing about transitive dependencies, which are most of what gets installed; and in this project the development requirements were entirely unpinned. Two installs a year apart produce different software and nothing anywhere records the difference.

This matters for the paper specifically, not merely as hygiene. The measurements this project will report — forced-alignment boundary error against hand labels, the six-clip score matrix, teacher-calibration correlations — are outputs of a software stack. "We used the Montreal Forced Aligner and Whisper" is the level of detail most CALL papers give, and it is not enough for anyone, including the authors a year later, to reproduce a number. The correction adopted (Decision D10) is a committed lockfile recording every package, direct and transitive, at an exact version with a file hash, plus a pinned interpreter provisioned by the same tool. The methods section can then state the environment as a fact rather than a gesture, and an appendix can point at a file rather than a paragraph.

**Two observations worth carrying into the write-up.**

*The same defect had already been spotted in the engine and treated as a separate problem.* A note from the previous session flagged that `Dockerfile.engine` pins nothing — `pip install openai-whisper librosa …` takes whatever is newest that day — and proposed fixing it when Step 21 arrived. It is the same defect in a different file, and the engine is where it matters most, because the engine produces the numbers. Worth reporting as a small general finding: **in a research artefact, the unpinned dependency is not a tidiness issue but a measurement-validity issue**, and it tends to appear in several places at once because it comes from a habit rather than an oversight.

*The platform moved during setup.* Django 6.1 was released on 5 August 2026 — three days before this decision — while the scaffold this project is built on pins the 5.2 LTS line. The choice made (D11) was to stay on 5.2 LTS through the Michaelmas 2026 pilot, because its security support runs to April 2028, because 6.1's own support would expire during or just after the pilot, and because two small third-party dependencies the interface depends on (`django-cotton`, `django-unfold`) had had three days to be tested against a new major release. This is a mundane engineering decision with a methodological edge: **for a study running over a term, the stability of the environment is worth more than the features forgone**, and the decision should be stated in the paper rather than left implicit, since a reader may otherwise wonder why a 2026 pilot ran on a 2025 framework release. The honest answer is that it was chosen deliberately and dated.
