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
