# One Engine, Every Language
## How a Persian Pronunciation Scorer Becomes a Global Language Learning Platform

> **📌 Decision update — 7 July 2026 (see `/DECISIONS.md`, D2):** The alignment layer described in this document as aeneas is now the **Montreal Forced Aligner (MFA)** — decided before implementation because aeneas is unmaintained (last release 2017), AGPL-licensed (incompatible with licensing the engine commercially, a core proposition of this document), and linguistically fragile at character level. This *strengthens* the pitch: the "aeneas and Persian" risk in the Honest Assessment section is resolved — MFA, one of the two named alternatives, is the plan of record, and MFA's MIT licence keeps the commercial path clean. In the Pronunciation Profile, `espeak_voice` becomes MFA model references (dictionary + acoustic model per language). Whisper's role is confirmed as gatekeeping/timing, never the pronunciation judge (D3).

### A Document for Partners and Funders

---

## The Idea in One Paragraph

We are building a pronunciation scoring engine that listens to a language learner speak, compares their voice to a native speaker sound by sound, and tells them exactly which sounds they got right and which need work — with a colour-coded visual score. We are starting with Persian, one of the hardest languages in the world to learn from text alone. But the technical foundation we are building does not care what language it is processing. The same engine — with only a small configuration file changed — can score pronunciation in Swahili, Cantonese, Arabic, Latvian, or any of the 99 languages supported by OpenAI's Whisper speech recognition system. This document explains both the vision and the technical reality of how that works.

---

## Why Pronunciation Is the Unsolved Problem in Language Learning

Every major language learning app today — Duolingo, Babbel, Rosetta Stone — focuses on vocabulary, grammar, and reading. Pronunciation is either ignored entirely or handled by a simple "did you say the right word?" check. Neither approach works for serious learners.

The real problem is that pronunciation operates at a level below words. It operates at the level of individual sounds — phonemes — and the subtle properties of those sounds: how long they are held, what pitch contour they follow, whether the tongue is in the right position. A learner can know every word in the dictionary and still be completely unintelligible to a native speaker because their phonemes are wrong.

This is especially acute in certain language families:

**Tonal languages** like Mandarin, Cantonese, and Vietnamese use pitch to distinguish meaning. The Mandarin syllable "ma" means mother, hemp, horse, or scold depending entirely on the tone. No existing consumer app scores tone accuracy at the phoneme level.

**Script-hidden languages** like Persian and Arabic do not write short vowels. A learner reading Persian text has no idea which vowel sounds to insert between consonants. They must either know from experience or guess.

**Phoneme-rich languages** like Arabic (with sounds that do not exist in European languages), Georgian, and many Bantu languages including Swahili have consonants and vowel structures that require precision feedback to learn correctly.

**Pitch-accent languages** like Japanese, Swedish, and Latvian use stress and pitch in ways that are almost invisible to learners from other language backgrounds.

Our engine addresses all of these categories — not by building four separate systems, but by building one configurable system with a language-specific pronunciation profile for each.

---

## The Technical Foundation: What Whisper Is and Why It Matters

Whisper is an open-source speech recognition model released by OpenAI in 2022. It was trained on 680,000 hours of audio in its original version, expanding to over 5 million hours in the current large-v3 release. It supports 99 languages and is available free of charge under the MIT licence, meaning it can be used in commercial products without royalty fees.

What makes Whisper uniquely suited to our platform is not just its language coverage — it is its ability to return **word-level timestamps**. When Whisper transcribes audio, it does not just say "the person said سلام." It says "the word سلام started at 0.0 seconds and ended at 0.62 seconds." This timestamp data is the foundation of our pronunciation scoring pipeline.

### Whisper's 99 supported languages include:

| Region | Languages |
|---|---|
| Middle East & Central Asia | Arabic, Persian (Farsi), Hebrew, Turkish, Azerbaijani, Kazakh, Uzbek |
| East & Southeast Asia | Mandarin Chinese, Cantonese, Japanese, Korean, Vietnamese, Thai, Indonesian, Malay, Tagalog |
| Sub-Saharan Africa | Swahili, Yoruba, Hausa, Amharic, Somali |
| South Asia | Hindi, Urdu, Bengali, Tamil, Telugu, Kannada, Gujarati, Marathi, Nepali |
| Europe (Western) | French, Spanish, German, Italian, Portuguese, Dutch, Polish, Romanian |
| Europe (Northern & Eastern) | Latvian, Lithuanian, Estonian, Finnish, Swedish, Norwegian, Danish, Ukrainian, Russian, Czech, Slovak, Hungarian |
| Other | Welsh, Maori, Basque, Icelandic, Georgian, Armenian |

Whisper's accuracy varies by language. For well-resourced languages (those with large amounts of training data available on the internet), word error rates are typically below 15% on real-world audio. For lower-resource languages, accuracy is lower — but still sufficient for our use case, because we are not relying on Whisper alone to transcribe what was said. We already *know* what was said. We are using Whisper primarily to find *when* each word occurred.

This distinction matters for partners and funders. We are not asking Whisper to act as the pronunciation teacher. We are using it as a timing tool at the coarse word level, then using forced alignment, acoustic feature extraction, and language-specific pronunciation profiles to do the actual pronunciation scoring.

---

## The Key Insight: We Are Using Whisper for Timing, Not Meaning

Traditional speech recognition has a hard job: listen to audio and figure out what words were spoken. That is transcription: converting unknown speech into text.

Our system has an easier and more controlled job. In a language-learning exercise, we already know the expected phrase before the learner speaks. The lesson tells us the text, the transliteration, the target phonemes, and the native reference recording. The learner is not speaking freely; they are attempting a known prompt.

That changes the technical problem. We are not asking, "What did the learner say?" We are asking, "Where in the learner's audio did the expected sounds occur, and how closely do those sounds match the native model?"

This technique is called **forced alignment**. We force the known text and the audio to align in time, producing a map of which sound happened at which millisecond. Whisper handles the coarse level by giving us word timestamps. A second tool, **aeneas**, handles the fine level by aligning individual sounds or transliterated fragments.

This is a lower-risk use of Whisper than open-ended transcription. If Whisper makes a small text-recognition mistake, the system can still use the known lesson prompt, the native reference audio, and the fine alignment layer to recover the timing. The core pronunciation judgement comes from acoustic comparison and the Pronunciation Profile, not from trusting Whisper's text output as a final answer.

### How to explain this in a pitch

A non-technical audience may hear "Whisper" and assume the product depends on general-purpose AI transcription accuracy. That is not the right framing.

The clearer framing is:

> We are not building a chatbot that guesses what the learner said. We are building a pronunciation alignment engine. Whisper gives us rough timing; our own language profiles and acoustic scoring decide whether the pronunciation was accurate.

This matters commercially because timing is a narrower, more testable dependency than full speech understanding. It can be validated phrase by phrase, language by language, against native reference recordings before a profile is released.

---

## What Changes Per Language (Very Little)

This is the most important thing to understand about our architecture. The core pipeline — record audio, align to text, compare durations and patterns, score, produce a visual annotation — is identical for every language. What changes is a single configuration object we call the **Pronunciation Profile**.

Here is what a Pronunciation Profile contains, and how it differs across four example languages:

---

### Persian (Farsi) — the prototype language

**The core challenge:** Hidden short vowels. Persian script omits the short vowels a, e, o entirely. A learner reading the word سلام sees only consonants; the vowels sâ-lâ-m must be inferred. When a learner tries to speak, they often omit or distort these invisible sounds.

**What the profile tracks:** Vowel duration (how long each vowel is held), vowel presence (did the learner include the vowel at all), and register distinction (formal literary Persian versus informal colloquial Persian have significantly different vowel patterns).

**Whisper language code:** `fa`

**Sample vowel map entry:**
```json
{ "position": 3, "vowel": "â", "phoneme": "/ɑː/" }
```

The profile identifies the target vowel and its position in the transliteration. It does not store a fixed expected duration in milliseconds. Timing is calculated dynamically by comparing the learner's vowel segment with the native reference recording, so learners are not penalised simply for speaking faster or slower.


---

### Mandarin Chinese — the tonal challenge

**The core challenge:** Tones. Mandarin has four tones plus a neutral tone. The syllable "ma" (妈/麻/马/骂) changes meaning entirely based on pitch. Whisper transcribes Mandarin characters but cannot alone score tone accuracy — we need to add pitch contour analysis.

**What the profile tracks:** Pitch contour (the shape of the pitch curve across the syllable), tone category accuracy (did the learner produce a rising tone or a falling tone?), and aspiration (Mandarin distinguishes b/p, d/t, g/k by whether air is expelled — English speakers consistently get this wrong).

**Whisper language code:** `zh`

**Technical addition needed:** The Pronunciation Profile for tonal languages includes a `pitch_map` field alongside the standard `phoneme_map`. The pipeline adds a pitch extraction step using the `librosa.yin()` function, which measures fundamental frequency (F0) over time and classifies the contour as one of the four Mandarin tone shapes.

**Sample tone map entry:**
```json
{ "syllable": "mā", "tone": 1, "contour": "high_flat", "f0_range_hz": [180, 220] }
```

---

### Swahili — the accessible entry point

**The core challenge:** Swahili is phonetically regular and relatively forgiving — what you see is almost always what you say. However, the language has a rich system of noun class prefixes that change the pronunciation of entire phrases, and vowel length is phonemically significant (long vowels change meaning).

**What the profile tracks:** Vowel length distinction (short versus long vowels), stress placement (Swahili stress always falls on the penultimate syllable — learners from English backgrounds consistently get this wrong), and the click-adjacent consonants in some loanwords from Bantu neighbours.

**Whisper language code:** `sw`

**Why Swahili is a strategic language for this platform:** Swahili is the most widely spoken African language by number of speakers (estimated 200 million total speakers across East Africa), it is an official language of the African Union, and it is dramatically underserved by existing language learning technology. There is no serious Duolingo-equivalent for Swahili pronunciation. This represents a significant market gap.

**Sample profile entry:**
```json
{ "position": 3, "vowel": "a", "phoneme": "/aː/", "long": true }
```

Here too, the profile marks the linguistic target rather than a fixed duration. The engine learns the expected timing from the native reference clip and scores the learner proportionally.


---

### Cantonese — the complexity ceiling

**The core challenge:** Cantonese has six tones (compared to Mandarin's four), a unique set of final consonants that do not exist in most other Chinese varieties, and a writing system that is partially shared with Mandarin but pronounced completely differently. Whisper large-v3 added Cantonese as a newly supported language, making this possible now when it was not feasible two years ago.

**What the profile tracks:** Six-tone pitch contours, final stop consonants (-p, -t, -k which are "unreleased" — the mouth closes but no air is expelled), and vowel length which is phonemically meaningful.

**Whisper language code:** `yue`

**Technical addition needed:** Six-tone classification requires a more sophisticated pitch classifier than Mandarin's four-tone version. The profile specifies tone contour templates: high level, high rising, mid level, low falling, low rising, low level.

**Why this matters:** Cantonese has approximately 85 million native speakers, is the dominant language of Hong Kong and the global Cantonese diaspora, and is entirely absent from serious language learning technology beyond basic vocabulary apps. A pronunciation scorer for Cantonese would be genuinely novel.

---

### Latvian — the European edge case

**The core challenge:** Latvian is a pitch-accent language, one of only two surviving Baltic languages. It has three intonation patterns (level, falling, broken) that change word meaning, three vowel lengths, and a palatalization system where consonants shift based on adjacent sounds. Almost no language learning technology addresses Latvian specifically.

**What the profile tracks:** Vowel length (Latvian has strict short/long vowel distinctions marked in writing with a macron: a versus ā), pitch accent on stressed syllables, and palatalized consonants (ķ, ģ, ļ, ņ, ŗ) that are unique to Latvian.

**Whisper language code:** `lv`

**Why Latvian matters for a funder:** Latvia is a member of the European Union. EU institutions have obligations to support all official EU languages. Language technology for Latvian is dramatically underdeveloped compared to major EU languages. This opens doors to EU research funding (Horizon Europe), Latvian government partnerships, and collaboration with the University of Latvia's Institute of Mathematics and Computer Science, which is the primary research body for Latvian language technology.

---

## The Architecture: One Engine, Swappable Profiles

Here is the technical architecture that makes this work across all 99 languages. The key design decision is that the language-specific knowledge lives entirely in the Pronunciation Profile configuration — not in the code.

```
┌─────────────────────────────────────────────────────┐
│                    Core Pipeline                     │
│  (identical for every language)                      │
│                                                      │
│  1. Receive learner audio (WAV, 16kHz mono)          │
│  2. Receive lesson reference data                    │
│  3. Run Whisper forced alignment → word timestamps   │
│  4. Run aeneas fine alignment → phoneme timestamps   │
│  5. Extract features (duration, pitch if needed)     │
│  6. Score against Pronunciation Profile              │
│  7. Return waveform_annotations JSON                 │
└──────────────────────┬──────────────────────────────┘
                       │ reads
┌──────────────────────▼──────────────────────────────┐
│              Pronunciation Profile                   │
│  (one per language — this is all that changes)       │
│                                                      │
│  language_code: "fa" | "zh" | "sw" | "yue" | "lv"  │
│  script_direction: "rtl" | "ltr"                    │
│  feature_focus: "vowel_duration" | "tone" |          │
│                 "stress" | "pitch_accent"            │
│  phoneme_map: [ ... language-specific entries ... ]  │
│  pitch_map: [ ... tonal languages only ... ]         │
│  espeak_voice: "fa" | "zh" | "sw" | ...             │
│  whisper_language: "fa" | "zh" | "sw" | "yue" | "lv"│
└─────────────────────────────────────────────────────┘
```

Adding a new language to the platform means:
1. Writing a Pronunciation Profile JSON file for that language (linguistic work, not engineering work)
2. Collecting native speaker audio samples for the A1 lesson set (content work)
3. Running the validation suite to confirm the alignment pipeline works for that language's phonemes

The engineering work is done once. Every new language is a content and linguistics task.

---

## The Linguistic Work: What a Pronunciation Profile Requires

To be honest with funders and partners: the engineering is the easy part. The hard, valuable, and irreplaceable work is creating accurate Pronunciation Profiles for each language. This requires:

**A linguistic consultant** who is a native speaker of the target language and has formal training in phonetics. They must be able to identify which phonemes are genuinely difficult for learners, specify expected duration ranges for vowels, describe tone contours precisely, and validate that the profile produces intuitive scores.

**Native speaker recordings** of the A1 lesson set — a minimum of 50–100 short phrases per language, recorded at 16kHz in a quiet environment by a clear speaker. These become the reference models against which all learner audio is compared.

**Transliteration standards** — particularly important for languages like Arabic, Persian, Cantonese, and Swahili that have multiple competing romanisation systems. The platform must commit to one standard per language and document it clearly.

This linguistic work is where the genuine expertise and intellectual property of the platform lives. The profiles, once created and validated, are the asset. The code is infrastructure.

---

## The Market Opportunity

The global language learning market was valued at approximately $61 billion in 2023 and is projected to reach $115 billion by 2032. Pronunciation learning — the most technically underserved segment — represents a significant fraction of that value.

The platform's multilingual architecture creates several distinct market opportunities:

**Consumer language learning:** A standalone app targeting serious adult learners of Persian, Arabic, Swahili, and Cantonese — languages that are either geographically strategic (Swahili across East Africa, Arabic across 22 countries) or have large diasporas motivated to maintain heritage languages (Persian, Cantonese).

**Integration with existing LMS platforms:** The pronunciation scoring API can be licenced to existing language learning platforms as a premium pronunciation module. They handle the learner interface; we provide the scoring engine.

**Government and institutional language training:** Diplomatic services, international NGOs, and militaries train staff in strategically important languages. Persian, Arabic, Swahili, and Mandarin are all on that list. Institutional buyers pay premium prices for measurable outcomes.

**Endangered and under-resourced language preservation:** Languages like Welsh, Maori, and many minority European languages have active governmental and community support for language learning technology. EU Horizon funding, Welsh Government grants, and Māori language revitalisation funding are all accessible markets.

**Academic research partnerships:** The forced alignment and pronunciation scoring pipeline produces data that is genuinely useful to phonetics researchers. University partnerships can fund development of profiles for lower-resource languages in exchange for data access.

---

## What We Are Building First and Why

We are starting with Persian for three reasons.

First, Persian is technically the hardest case. The hidden vowel problem, the right-to-left script, the formal/colloquial register split, and the relative scarcity of Persian-language AI training data make it the most demanding test of our pipeline. If the engine works for Persian, it works for everything easier.

Second, the Persian diaspora is large, educated, and motivated. There are approximately 110 million Persian speakers worldwide, with significant diaspora communities in the United States, United Kingdom, Germany, and Sweden. Diaspora communities learning or maintaining their heritage language are highly motivated learners willing to pay for quality tools.

Third, no serious competitor exists. Persian is absent from the pronunciation scoring features of every major language learning platform. This is a clear gap.

The Persian prototype validates the core engine. The first commercial release will add Arabic (structurally similar — right-to-left, hidden vowels, shared infrastructure) and Swahili (the largest African language market, phonetically simpler, easier to validate). Mandarin and Cantonese follow, then a sweep across the remaining Whisper-supported languages using the validated pipeline.

---

## Honest Assessment: Limitations and Risks

A document for serious funders must acknowledge what is hard and what could go wrong.

**Whisper accuracy varies by language.** For well-resourced languages, the coarse timing is usually reliable. For lower-resource languages — some African languages, many Central Asian languages — Whisper's word error rate is higher, and its timestamps may be less precise. The mitigation is that we use Whisper for timing rather than final transcription: the lesson already supplies the expected text, and every new language profile is manually validated against native reference recordings before release.

**Cantonese is newly supported.** Whisper large-v3 added Cantonese support relatively recently. The accuracy on Cantonese is good but not yet at the level of Mandarin or European languages. We treat Cantonese as a later release, not a launch language.

**The linguistic work is slow.** Creating a validated Pronunciation Profile for a new language is a weeks-long collaboration with a phonetics specialist. It cannot be automated. Scaling to 99 languages requires a sustained programme of linguistic partnerships — this is a resource and time constraint, not a technical one.

**aeneas and Persian.** The forced alignment tool we use (aeneas) was built primarily for European languages. Our prototype work is specifically testing whether it handles Persian phonemes reliably. If it does not, we have identified two alternatives: the Montreal Forced Aligner (MFA) and a custom alignment layer built on top of Whisper's internal attention weights. The prototype is designed to surface this risk early, before any large engineering investment.

**Not a real-time system yet.** The current pipeline takes 3–8 seconds to process a short audio clip. This is acceptable for a post-attempt scoring tool ("here is how you did") but not for real-time feedback during speech. Real-time scoring is a future feature requiring hardware optimisation.

---

## Summary: The Proposition for Partners and Funders

We are building a technically novel pronunciation scoring engine, starting with Persian and designed from day one to scale to 99 languages.

The technology foundation — Whisper word-level timing, forced alignment, acoustic comparison, and phoneme-level scoring — is proven and open source. The engineering challenge (which we are solving) is the Persian-specific alignment pipeline and the multilingual configuration architecture. The linguistic challenge (which we are solving through expert partnerships) is creating accurate Pronunciation Profiles for each target language.

The important technical distinction is that we are not relying on Whisper's general transcription intelligence as the product. We are using its timing signal as one layer in a controlled pronunciation-alignment pipeline.

The result is a platform that addresses the most underserved problem in language learning, for the most underserved languages, at a moment when the underlying AI technology has finally made it possible.

The Persian prototype is the proof of concept. The multilingual engine is the product.

---

## Appendix: Whisper's 99 Supported Languages (Full List)

Afrikaans · Albanian · Amharic · Arabic · Armenian · Assamese · Azerbaijani · Bashkir · Basque · Belarusian · Bengali · Bosnian · Breton · Bulgarian · Burmese · Cantonese · Castilian · Catalan · Chinese · Croatian · Czech · Danish · Dutch · English · Estonian · Faroese · Finnish · Flemish · French · Galician · Georgian · German · Greek · Gujarati · Haitian Creole · Hausa · Hawaiian · Hebrew · Hindi · Hungarian · Icelandic · Indonesian · Italian · Japanese · Javanese · Kannada · Kazakh · Khmer · Korean · Lao · Latvian · Letzeburgesch · Lingala · Lithuanian · Luxembourgish · Macedonian · Malagasy · Malay · Malayalam · Maltese · Maori · Marathi · Moldavian · Mongolian · Myanmar · Nepali · Norwegian · Nynorsk · Occitan · Panjabi · Pashto · Persian · Polish · Portuguese · Punjabi · Romanian · Russian · Sanskrit · Serbian · Shona · Sindhi · Sinhala · Slovak · Slovenian · Somali · Spanish · Sundanese · Swahili · Swati · Swedish · Tagalog · Tajik · Tamil · Tatar · Telugu · Thai · Tibetan · Turkish · Turkmen · Ukrainian · Urdu · Uzbek · Valencian · Vietnamese · Welsh · Yiddish · Yoruba

*Note: Whisper's published accuracy benchmarks cover the languages where word error rate is below 60% on standard test sets. For lower-resource languages further down this list, the platform will use a combination of Whisper alignment and manual validation by linguistic consultants before those language profiles are released.*

---

*Document version 1.2 — revised to align profile examples with dynamic native-reference timing*
*Technical prototype: Persian A1 pronunciation scoring*
*Next milestone: Validated vowel_map schema and aeneas alignment confirmation*
