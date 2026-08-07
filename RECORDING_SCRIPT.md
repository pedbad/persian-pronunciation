# Native-Speaker Recording Script — Iran trip
*(Companion to BUILD_PLAN Step 19. Bring this on your phone or printed.)*

## What we need

- **Per word: at least 2 different native speakers** — ideally one male, one female (Decision D9: the app scores each learner against both voices and keeps the better match, so voice variety directly improves fairness).
- **3 takes per word per speaker** — pick the cleanest later.
- More speakers = better. If you can get 3–4 people, do.

## Consent — do this first, every speaker

Explain before recording: the clips become reference audio in a university language-learning app, and may be stored in a **public code repository**. Get a clear verbal "yes" **on the recording itself** at the start of the session (or written). No names in filenames — speakers are logged as `spk1_f`, `spk2_m`, etc.

## How to record

1. Quiet room — no fan, AC, street noise. Phone in airplane mode (no call interruptions).
2. Phone voice memo app is fine. Hold ~20 cm from mouth.
3. One word per take: say it **once, clearly, natural pace** — careful but not exaggerated or syllable-by-syllable.
4. Pause ~1 second of silence before and after the word.
5. Any format (m4a is fine) — we convert to 16 kHz mono WAV later with ffmpeg.

## Speaker log (fill per person)

| ID | Sex | Age range | City / dialect | Consent on tape? |
|----|-----|-----------|----------------|------------------|
| spk1 | | | | |
| spk2 | | | | |

## PART 1 — Required (the two pilot lessons)

| Persian | Transliteration | Meaning | Target vowels |
|---------|-----------------|---------|---------------|
| سلام | salâm | hello | a (short), â (long) |
| ممنون | mamnun | thank you | a (short), u (long) |

## PART 2 — Optional word bank (future lessons — record if time allows)

Everyday CULP-level words covering all six vowels (short a/e/o, long â/i/u):

| Persian | Transliteration | Meaning |
|---------|-----------------|---------|
| بله | bale | yes |
| نه | na | no |
| آب | âb | water |
| نان | nân | bread |
| کتاب | ketâb | book |
| خانه | khâne | house |
| مدرسه | madrese | school |
| دوست | dust | friend |
| خوب | khub | good |
| چطور | chetor | how |
| لطفاً | lotfan | please |
| ببخشید | bebakhshid | excuse me |
| خداحافظ | khodâhâfez | goodbye |

## PART 3 — Minimal-pair gold (optional, high value)

Same written consonants, different hidden short vowels — the exact problem the app teaches. Say each member of the set:

| Written | Readings |
|---------|----------|
| گل | **gol** (flower) · **gel** (mud) |
| شکر | **shekar** (sugar) · **shokr** (gratitude) |
| کرم | **karam** (generosity) · **kerm** (worm) · **krem** (cream) |

## PART 4 — Short phrases (optional — future lessons + connected speech)

2–6 words, natural conversational pace. One phrase per take, 2 takes per speaker enough:

| Persian | Transliteration | Meaning |
|---------|-----------------|---------|
| سلام، خوبی؟ | salâm, khubi? | hi, how are you? |
| خیلی ممنون | kheyli mamnun | thanks a lot |
| حالت چطوره؟ | hâlet chetore? | how are you? |
| خواهش می‌کنم | khâhesh mikonam | you're welcome |
| صبح بخیر | sobh bekheir | good morning |
| شب بخیر | shab bekheir | good night |
| من فارسی یاد می‌گیرم | man fârsi yâd migiram | I'm learning Persian |
| چای می‌خوری؟ | chây mikhori? | do you want tea? |
| خیلی خوشمزه است | kheyli khoshmaze ast | it's delicious |
| ببخشید، متوجه نشدم | bebakhshid, motavajjeh nashodam | sorry, I didn't understand |

Why phrases too: future lessons need connected speech (ezâfe, liaison), and aligners handle phrases better than isolated words — good comparison data.

## Bringing it home

Keep originals untouched. Back at the Mac we convert and name per BUILD_PLAN Step 19: `audio/<word>_native_a.wav`, `audio/<word>_native_b.wav`.
