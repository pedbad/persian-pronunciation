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
