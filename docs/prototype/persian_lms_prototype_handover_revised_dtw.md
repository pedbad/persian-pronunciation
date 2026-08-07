# Persian LMS — Pronunciation Prototype Handover

> **📌 Decision update — 7 July 2026 (see `/DECISIONS.md`, D2):** aeneas is dropped, before implementation — unmaintained since 2017, AGPL-licensed (blocks the commercial engine-licensing path), and character-through-espeak alignment was judged too fragile. The alignment layer is the **Montreal Forced Aligner (MFA)**. For the developer, concretely: skip `step6_aeneas_align.py` and the espeak/numpy/Python-3.10 setup entirely — they are replaced by an MFA wrapper, `align_mfa.py` (see `FABLE_REVIEW.md` Step 8). **Rules 1–4, the scorer design, the vowel_map schema, and the API output contract below all survive**, with two changes: the target vowel is located by matching its `phoneme` field in the MFA output (real speech sounds, not characters), while `position` is retained as the lesson-data validation check (Rules 2–3 still mandatory); and per **D9 (7 Aug 2026)** the scorer runs against *both* native references and keeps the better result, so the output payload additionally carries the winning `reference_id` and native segment times. Score weighting is fixed at 60/40 (D4).

## What are we actually building? (plain English)

Imagine you are learning Persian and you try to say the word **سلام** (*salâm* — hello).

You record yourself saying it. The app then:

1. Listens to your recording.
2. Compares it, sound by sound, against a native Persian speaker saying the same word.
3. Highlights exactly **which vowel sounds you got right** (green), nearly right (amber), or wrong (red).
4. Shows the relevant sound regions visually so the learner can connect the score to the audio.

The difficult part is step 2.

Persian has **hidden vowels**: short vowel sounds that native speakers know instinctively but that are usually not written in the script. A learner looking at Persian text often cannot tell which vowel sound belongs between the consonants.

This prototype proves that we can locate and score those hidden vowels in learner speech.

We are **not** building the full LMS yet. We are proving the critical pronunciation-scoring pipeline before wrapping it in Django, React, user accounts, lesson flows, or analytics.

---

## What does success look like?

By the end of this prototype, the developer should have a small Python pipeline that:

- Takes a short Persian learner audio clip.
- Takes a native reference recording of the same word or phrase.
- Takes a lesson JSON file containing the transliteration and target hidden-vowel map.
- Aligns both recordings to the same transliteration.
- Scores each target vowel using:
  - proportional timing comparison, and
  - acoustic similarity using MFCC features plus Dynamic Time Warping (DTW).
- Returns a JSON blob showing which vowel sounds matched, their learner-side timestamps, and their scores.

The timing is assessed **proportionally**, not by fixed milliseconds. A learner should not be punished simply because they spoke the whole word more slowly or more quickly than the native speaker.

The final JSON output is the same shape the Django API will later serve to the frontend.

---

## Critical architectural rules

These rules are not optional. They prevent the legacy bugs that existed in earlier versions of the handover.

### Rule 1 — Do not use static `expected_ms`

Older notes used fields such as:

```json
{ "position": 3, "vowel": "â", "phoneme": "/ɑː/", "expected_ms": 320 }
```

Do **not** implement this.

Fixed millisecond targets break as soon as a learner speaks slower or faster than the native speaker. The scorer should calculate timing from the native reference recording and compare the learner's vowel as a **proportion** of the whole aligned utterance.

The lesson JSON should identify **which sound to score**, not prescribe a fixed duration.

### Rule 2 — `position` is a zero-indexed transliteration character index

The `position` field refers to Python's zero-indexed index in the **transliteration string**, not the Persian script string.

For example:

```text
transliteration = "salâm"

[0] = s
[1] = a
[2] = l
[3] = â
[4] = m
```

Therefore, the long vowel **â** is at position `3`, not position `2`.

This matters because the scorer uses the same index to pick the native and learner audio fragments. A wrong index can silently score a consonant while labelling it as a vowel.

### Rule 3 — Validate that the mapped character is actually the target vowel

Every validation script must include this check:

```python
assert transliteration[position] == entry["vowel"]
```

Without this check, the system can pass while scoring the wrong sounds.

### Rule 4 — The scorer must use acoustic comparison, not duration alone

A duration-only scorer is not enough. A learner could produce the wrong vowel for the right length of time and receive a false high score.

The scoring function must combine:

- **Acoustic score**: MFCC feature similarity using DTW.
- **Timing score**: relative vowel duration compared with the native reference.

The current prototype weighting is:

```text
final_score = 60% acoustic score + 40% proportional timing score
```

This weighting can later be tuned after native-speaker validation.

---

## Pipeline overview

```text
[Native WAV]   ┐
               ├── [1. Whisper word timing] ── [2. aeneas character alignment]
[Learner WAV]  ┘                                      │
                                                      ▼
                                  [3. Proportional + DTW vowel scorer]
                                                      │
                                                      ▼
                                      [4. waveform_annotations JSON]
```

---

## Step 1 — Set up the Python environment

Use Python 3.10. This avoids common compatibility issues with `aeneas`.

```bash
mkdir persian-pronunciation-prototype
cd persian-pronunciation-prototype

python3.10 -m venv venv
source venv/bin/activate
# Windows:
# venv\Scripts\activate

python --version
```

Expected result:

```text
Python 3.10.x
```

---

## Step 2 — Install dependencies

### System dependencies

macOS:

```bash
brew install ffmpeg espeak
```

Ubuntu / Debian:

```bash
sudo apt-get install ffmpeg espeak libespeak-dev
```

If Persian voice support is missing later, install `espeak-ng` as well.

### Python packages

```bash
pip install openai-whisper
pip install numpy==1.23.5
pip install aeneas
pip install librosa soundfile scipy
```

Test imports:

```bash
python -c "import whisper; print('Whisper OK')"
python -c "import aeneas; print('aeneas OK')"
python -c "import librosa; print('librosa OK')"
python -c "import scipy; print('scipy OK')"
```

---

## Step 3 — Collect A1 test audio

Use short, controlled clips.

Each phrase needs:

- one native speaker WAV file,
- one learner WAV file,
- the same transliteration in the lesson JSON.

Recording requirements:

- WAV format
- 16,000 Hz sample rate
- mono channel
- ideally under 10 seconds

Suggested test files:

```text
audio/
  salaam_native.wav
  salaam_learner.wav
  mamnun_native.wav
  mamnun_learner.wav
```

Check an audio file:

```bash
python -c "
import soundfile as sf
data, sr = sf.read('audio/salaam_native.wav')
print(f'Sample rate: {sr}, Duration: {len(data)/sr:.2f}s, Channels: {data.ndim}')
"
```

Expected:

```text
Sample rate: 16000
Channels: 1
```

If the source audio is MP3 or M4A, convert it:

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

---

## Step 4 — Define the lesson JSON files

The lesson JSON contains the text, transliteration, translation, and vowel map.

The vowel map identifies which transliteration character positions should be scored. It does **not** include static millisecond durations.

### `lessons/salaam.json`

```json
{
  "script_rtl": "سلام",
  "transliteration": "salâm",
  "translation_en": "Hello",
  "vowel_map": [
    { "position": 1, "vowel": "a",  "phoneme": "/æ/"  },
    { "position": 3, "vowel": "â",  "phoneme": "/ɑː/" }
  ]
}
```

Index check:

```text
salâm
0 s
1 a
2 l
3 â
4 m
```

### `lessons/mamnun.json`

```json
{
  "script_rtl": "ممنون",
  "transliteration": "mamnun",
  "translation_en": "Thank you",
  "vowel_map": [
    { "position": 1, "vowel": "a",  "phoneme": "/æ/"  },
    { "position": 4, "vowel": "u",  "phoneme": "/uː/" }
  ]
}
```

Index check:

```text
mamnun
0 m
1 a
2 m
3 n
4 u
5 n
```

### JSON schema

Save as `vowel_map_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VowelMap",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["position", "vowel", "phoneme"],
    "additionalProperties": false,
    "properties": {
      "position": {
        "type": "integer",
        "description": "Zero-indexed character index in the transliteration string"
      },
      "vowel": {
        "type": "string",
        "description": "Romanised vowel character at that transliteration index"
      },
      "phoneme": {
        "type": "string",
        "description": "IPA symbol, e.g. /ɑː/, /æ/, /uː/"
      }
    }
  }
}
```

Validation command:

```bash
pip install jsonschema

python -c "
import json, jsonschema
schema = json.load(open('vowel_map_schema.json'))
lesson = json.load(open('lessons/salaam.json'))
jsonschema.validate(lesson['vowel_map'], schema)
transliteration = lesson['transliteration']
for entry in lesson['vowel_map']:
    position = entry['position']
    assert 0 <= position < len(transliteration)
    assert transliteration[position] == entry['vowel']
print('vowel_map schema and indices: VALID')
"
```

---

## Step 5 — Run Whisper for word-level timing

Whisper is used here for **timing**, not as the final pronunciation judge.

Save as `step5_whisper_align.py`:

```python
import json
import sys
import whisper

def transcribe_with_timestamps(audio_path: str) -> dict:
    """
    Transcribe Persian audio and return word-level timestamps.

    Whisper is used for coarse timing. The lesson already defines the expected
    phrase, so the scorer should not depend on open-ended transcription.
    """
    model = whisper.load_model("medium")

    result = model.transcribe(
        audio_path,
        language="fa",
        word_timestamps=True,
        initial_prompt="متن فارسی",
        verbose=False,
    )

    words = []
    for segment in result["segments"]:
        for word in segment.get("words", []):
            words.append({
                "word": word["word"].strip(),
                "start": round(word["start"], 3),
                "end": round(word["end"], 3),
            })

    return {
        "text": result["text"].strip(),
        "language": result["language"],
        "words": words,
    }

if __name__ == "__main__":
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "audio/salaam_native.wav"
    output = transcribe_with_timestamps(audio_file)
    print(json.dumps(output, ensure_ascii=False, indent=2))
```

Run:

```bash
python step5_whisper_align.py audio/salaam_native.wav
```

Expected shape:

```json
{
  "text": "سلام",
  "language": "fa",
  "words": [
    { "word": "سلام", "start": 0.0, "end": 0.62 }
  ]
}
```

---

## Step 6 — Run aeneas for character-level alignment

Save as `step6_aeneas_align.py`:

```python
import json
import os
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

def align_phonemes(audio_path: str, transliteration: str, output_path: str) -> list[dict]:
    """
    Force-align each transliteration character against the audio.

    Returns:
        [
          {"char": "s", "start": 0.00, "end": 0.12},
          {"char": "a", "start": 0.12, "end": 0.22},
          ...
        ]
    """
    text_path = "/tmp/proto_text.txt"

    with open(text_path, "w", encoding="utf-8") as f:
        for char in transliteration.replace(" ", ""):
            f.write(char + "\n")

    config_string = (
        "task_language=fa|"
        "is_text_type=plain|"
        "os_task_file_format=json"
    )

    task = Task(config_string=config_string)
    task.audio_file_path_absolute = os.path.abspath(audio_path)
    task.text_file_path_absolute = os.path.abspath(text_path)
    task.sync_map_file_path_absolute = os.path.abspath(output_path)

    ExecuteTask(task).execute()
    task.output_sync_map_file()

    with open(output_path, "r", encoding="utf-8") as f:
        sync_map = json.load(f)

    fragments = []
    for frag in sync_map.get("fragments", []):
        fragments.append({
            "char": frag["lines"][0] if frag["lines"] else "",
            "start": float(frag["begin"]),
            "end": float(frag["end"]),
        })

    return fragments

if __name__ == "__main__":
    lesson = json.load(open("lessons/salaam.json"))
    fragments = align_phonemes(
        audio_path="audio/salaam_native.wav",
        transliteration=lesson["transliteration"],
        output_path="/tmp/salaam_sync.json",
    )
    print(json.dumps(fragments, ensure_ascii=False, indent=2))
```

Run:

```bash
python step6_aeneas_align.py
```

Expected shape:

```json
[
  { "char": "s", "start": 0.0,  "end": 0.12 },
  { "char": "a", "start": 0.12, "end": 0.22 },
  { "char": "l", "start": 0.22, "end": 0.31 },
  { "char": "â", "start": 0.31, "end": 0.62 },
  { "char": "m", "start": 0.62, "end": 0.74 }
]
```

---

## Step 7 — Score pronunciation using proportional timing and DTW

Save as `step7_score.py`:

```python
import json

import librosa
import numpy as np
from scipy.spatial.distance import cdist

from step6_aeneas_align import align_phonemes

ACOUSTIC_WEIGHT = 0.60
TIMING_WEIGHT = 0.40

def colour_from_score(score: int) -> str:
    if score >= 85:
        return "#1D9E75"
    if score >= 65:
        return "#EF9F27"
    return "#E24B4A"

def timing_score(native_ratio: float, learner_ratio: float) -> int:
    """
    Score relative vowel duration.
    """
    if native_ratio <= 0:
        return 100

    ratio = learner_ratio / native_ratio

    if 0.8 <= ratio <= 1.2:
        return 100

    deviation = abs(ratio - 1.0)
    return max(0, int(100 - (deviation - 0.2) * 200))

def load_audio_segment(audio_path: str, start: float, end: float, sr: int = 16000):
    duration = max(0.0, end - start)
    if duration <= 0:
        return np.array([]), sr

    y, actual_sr = librosa.load(
        audio_path,
        sr=sr,
        offset=max(0.0, start),
        duration=duration,
        mono=True,
    )
    return y, actual_sr

def normalise_mfcc(mfcc: np.ndarray) -> np.ndarray:
    return (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (
        np.std(mfcc, axis=1, keepdims=True) + 1e-6
    )

def acoustic_dtw_score(
    native_audio: str,
    learner_audio: str,
    native_segment: list[float],
    learner_segment: list[float],
) -> int:
    """
    Compare native and learner vowel segments using MFCC features and DTW.

    Returns an approximate 0-100 acoustic similarity score.
    """
    try:
        y_native, sr_native = load_audio_segment(
            native_audio,
            native_segment[0],
            native_segment[1],
        )
        y_learner, sr_learner = load_audio_segment(
            learner_audio,
            learner_segment[0],
            learner_segment[1],
        )

        if len(y_native) < 64 or len(y_learner) < 64:
            return 50

        shortest = min(len(y_native), len(y_learner))
        n_fft = 512 if shortest >= 512 else 256 if shortest >= 256 else 128
        hop_length = max(32, n_fft // 4)

        mfcc_native = librosa.feature.mfcc(
            y=y_native,
            sr=sr_native,
            n_mfcc=13,
            n_fft=n_fft,
            hop_length=hop_length,
        )
        mfcc_learner = librosa.feature.mfcc(
            y=y_learner,
            sr=sr_learner,
            n_mfcc=13,
            n_fft=n_fft,
            hop_length=hop_length,
        )

        if mfcc_native.shape[1] == 0 or mfcc_learner.shape[1] == 0:
            return 50

        mfcc_native = normalise_mfcc(mfcc_native)
        mfcc_learner = normalise_mfcc(mfcc_learner)

        distance_matrix = cdist(mfcc_native.T, mfcc_learner.T, metric="cosine")

        D, path = librosa.sequence.dtw(
            C=distance_matrix,
            step_sizes_sigma=np.array([[1, 1], [1, 2], [2, 1]]),
        )

        normalised_distance = D[-1, -1] / max(1, len(path))

        # Initial calibration constant. Tune with native/native and native/learner clips.
        score = int((1.0 - (normalised_distance / 0.25)) * 100)

        return max(0, min(100, score))

    except Exception:
        # Conservative fallback: do not silently award high marks.
        return 50

def build_position_lookup(fragments: list[dict]) -> dict[int, dict]:
    return {index: fragment for index, fragment in enumerate(fragments)}

def utterance_duration(fragments: list[dict]) -> float:
    if not fragments:
        return 0.0
    return max(0.0, fragments[-1]["end"] - fragments[0]["start"])

def validate_vowel_map(lesson: dict) -> None:
    transliteration = lesson["transliteration"]

    for entry in lesson["vowel_map"]:
        position = entry["position"]

        assert isinstance(position, int), f"position must be int: {entry}"
        assert 0 <= position < len(transliteration), f"position out of range: {entry}"
        assert transliteration[position] == entry["vowel"], (
            f"vowel_map mismatch: position {position} in {transliteration!r} "
            f"is {transliteration[position]!r}, not {entry['vowel']!r}"
        )

def score_pronunciation(
    lesson_path: str,
    native_audio: str,
    learner_audio: str,
) -> dict:
    lesson = json.load(open(lesson_path, encoding="utf-8"))
    validate_vowel_map(lesson)

    transliteration = lesson["transliteration"]
    vowel_map = lesson["vowel_map"]

    native_fragments = align_phonemes(
        audio_path=native_audio,
        transliteration=transliteration,
        output_path="/tmp/native_sync.json",
    )
    learner_fragments = align_phonemes(
        audio_path=learner_audio,
        transliteration=transliteration,
        output_path="/tmp/learner_sync.json",
    )

    native_lookup = build_position_lookup(native_fragments)
    learner_lookup = build_position_lookup(learner_fragments)

    native_total = utterance_duration(native_fragments)
    learner_total = utterance_duration(learner_fragments)

    vowel_accuracy = []
    waveform_annotations = []

    for entry in vowel_map:
        position = entry["position"]

        native_fragment = native_lookup.get(position)
        learner_fragment = learner_lookup.get(position)

        if not native_fragment or not learner_fragment:
            continue

        native_segment = [native_fragment["start"], native_fragment["end"]]
        learner_segment = [learner_fragment["start"], learner_fragment["end"]]

        native_vowel_duration = native_fragment["end"] - native_fragment["start"]
        learner_vowel_duration = learner_fragment["end"] - learner_fragment["start"]

        native_ratio = native_vowel_duration / native_total if native_total > 0 else 0
        learner_ratio = learner_vowel_duration / learner_total if learner_total > 0 else 0

        rhythm_score = timing_score(native_ratio, learner_ratio)
        sound_score = acoustic_dtw_score(
            native_audio=native_audio,
            learner_audio=learner_audio,
            native_segment=native_segment,
            learner_segment=learner_segment,
        )

        final_score = int((sound_score * ACOUSTIC_WEIGHT) + (rhythm_score * TIMING_WEIGHT))

        vowel_accuracy.append({
            "position": position,
            "vowel": entry["vowel"],
            "phoneme": entry["phoneme"],
            "native_ratio": round(native_ratio, 4),
            "learner_ratio": round(learner_ratio, 4),
            "timing_score": rhythm_score,
            "acoustic_score": sound_score,
            "score": final_score,
            "segment": [
                round(learner_segment[0], 3),
                round(learner_segment[1], 3),
            ],
        })

        waveform_annotations.append({
            "time_start": round(learner_segment[0], 3),
            "time_end": round(learner_segment[1], 3),
            "label": entry["vowel"],
            "accuracy": final_score,
            "color_hex": colour_from_score(final_score),
        })

    scores = [entry["score"] for entry in vowel_accuracy]
    overall_score = int(np.mean(scores)) if scores else 0

    return {
        "overall_score": overall_score,
        "vowel_accuracy": vowel_accuracy,
        "waveform_annotations": waveform_annotations,
    }

if __name__ == "__main__":
    result = score_pronunciation(
        lesson_path="lessons/salaam.json",
        native_audio="audio/salaam_native.wav",
        learner_audio="audio/salaam_learner.wav",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

Run:

```bash
python step7_score.py
```

Expected output shape:

```json
{
  "overall_score": 84,
  "vowel_accuracy": [
    {
      "position": 3,
      "vowel": "â",
      "phoneme": "/ɑː/",
      "native_ratio": 0.4189,
      "learner_ratio": 0.4012,
      "timing_score": 100,
      "acoustic_score": 76,
      "score": 85,
      "segment": [0.31, 0.62]
    }
  ],
  "waveform_annotations": [
    {
      "time_start": 0.31,
      "time_end": 0.62,
      "label": "â",
      "accuracy": 85,
      "color_hex": "#1D9E75"
    }
  ]
}
```

---

## Step 8 — Validate everything end to end

Save as `step8_validate_all.py`:

```python
import json
import os

from step7_score import score_pronunciation, validate_vowel_map

LESSONS = [
    ("lessons/salaam.json", "audio/salaam_native.wav", "audio/salaam_learner.wav"),
    ("lessons/mamnun.json", "audio/mamnun_native.wav", "audio/mamnun_learner.wav"),
]

passed = 0
failed = 0

for lesson_path, native_audio, learner_audio in LESSONS:
    lesson_name = os.path.basename(lesson_path)
    print(f"\n--- Testing {lesson_name} ---")

    try:
        lesson = json.load(open(lesson_path, encoding="utf-8"))

        assert "vowel_map" in lesson, "missing vowel_map"
        assert "transliteration" in lesson, "missing transliteration"

        for entry in lesson["vowel_map"]:
            assert "position" in entry, f"missing position in {entry}"
            assert "vowel" in entry, f"missing vowel in {entry}"
            assert "phoneme" in entry, f"missing phoneme in {entry}"
            assert "expected_ms" not in entry, f"legacy expected_ms must be removed from {entry}"

        validate_vowel_map(lesson)

        print(f"  Schema: PASSED ({len(lesson['vowel_map'])} target vowels)")

        result = score_pronunciation(
            lesson_path=lesson_path,
            native_audio=native_audio,
            learner_audio=learner_audio,
        )

        assert 0 <= result["overall_score"] <= 100
        assert len(result["waveform_annotations"]) > 0

        print(f"  Scoring: PASSED (overall score: {result['overall_score']})")
        print(f"  Annotations: {len(result['waveform_annotations'])} vowel regions returned")

        passed += 1

    except Exception as exc:
        print(f"  FAILED: {exc}")
        failed += 1

print(f"\n=== Results: {passed} passed, {failed} failed ===")

if failed == 0:
    print("Prototype is ready for Django integration.")
else:
    print("Fix the failures above before proceeding.")
```

Run:

```bash
python step8_validate_all.py
```

---

## Passing criteria

The prototype is ready for Django integration only when all of the following are true:

- [ ] `step8_validate_all.py` prints `0 failed`.
- [ ] The `vowel_map` contains no `expected_ms` fields.
- [ ] Every `position` points to the matching `vowel` in the transliteration string.
- [ ] The scorer aligns both native and learner recordings.
- [ ] The scorer returns `waveform_annotations`.
- [ ] A native or near-native attempt scores high.
- [ ] A clearly wrong vowel scores lower even if its duration is similar.
- [ ] aeneas successfully identifies the long `â` vowel in `salâm`.

---

## Troubleshooting

### aeneas fails to install

Install `ffmpeg` and `espeak` before installing `aeneas`.

If needed:

```bash
pip install numpy==1.23.5
pip install aeneas --no-binary aeneas
```

### Whisper detects Arabic instead of Persian

Use:

```python
initial_prompt="متن فارسی"
```

inside the Whisper `transcribe()` call.

### aeneas returns all-zero timestamps

Check whether Persian voice support exists:

```bash
espeak --voices | grep fa
```

If empty, install `espeak-ng`.

macOS:

```bash
brew install espeak-ng
```

Ubuntu:

```bash
sudo apt-get install espeak-ng espeak-ng-data
```

### Audio file errors

Convert to 16kHz mono WAV:

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

### DTW scores feel too harsh or too generous

The calibration constant in this line is provisional:

```python
score = int((1.0 - (normalised_distance / 0.25)) * 100)
```

Tune it using:

- native speaker against native speaker,
- native speaker against careful learner,
- native speaker against deliberately wrong vowel,
- same learner speaking fast and slow.

Do not tune the threshold using only one clip.

---

## What happens next after prototype validation

Once this prototype passes validation, wrap the code into the Django/React architecture:

1. `step5_whisper_align.py` → `services/whisper_service.py`
2. `step6_aeneas_align.py` → `services/alignment_service.py`
3. `step7_score.py` → `services/pronunciation_scorer.py`
4. Store the lesson vowel map as JSONB on the relevant Persian text/lesson model.
5. Run pronunciation scoring in a Celery task so the HTTP response does not block.
6. Store the scoring output for review, replay, and analytics.
7. Send `waveform_annotations` directly to the React `WaveformViewer`.

---

## Suggested Django service boundary

The Django layer should not contain raw audio-analysis logic.

Recommended service structure:

```text
services/
  whisper_service.py
  alignment_service.py
  pronunciation_scorer.py
  pronunciation_pipeline.py
```

Suggested orchestration function:

```python
def score_attempt(
    lesson_id: int,
    learner_audio_path: str,
    native_audio_path: str,
) -> dict:
    ...
```

The API view should call the Celery task, not run the scorer inline.

---

## API output contract

The React frontend should be able to rely on this shape:

```json
{
  "overall_score": 84,
  "vowel_accuracy": [
    {
      "position": 3,
      "vowel": "â",
      "phoneme": "/ɑː/",
      "native_ratio": 0.4189,
      "learner_ratio": 0.4012,
      "timing_score": 100,
      "acoustic_score": 76,
      "score": 85,
      "segment": [0.31, 0.62]
    }
  ],
  "waveform_annotations": [
    {
      "time_start": 0.31,
      "time_end": 0.62,
      "label": "â",
      "accuracy": 85,
      "color_hex": "#1D9E75"
    }
  ]
}
```

---

## Prototype scope

This handover covers only:

- A1 Persian pronunciation scoring.
- Short phrase audio.
- Known-prompt learner attempts.
- Native-reference comparison.
- Hidden-vowel scoring.

It does not yet cover:

- live streaming feedback,
- free speech,
- classroom analytics,
- user accounts,
- long-form audio,
- tone scoring for tonal languages,
- production-grade calibration.

---

## Final developer note

The most dangerous failure mode is not a crash. It is a silent pass where the system scores the wrong character.

That is why `position` validation is mandatory.

The second most dangerous failure mode is an attractive but shallow duration-only scorer. That is why the scorer must include acoustic DTW over MFCC features.

If those two constraints are preserved, this prototype is aligned with the current Persian pronunciation architecture and ready to become the Django service layer.
