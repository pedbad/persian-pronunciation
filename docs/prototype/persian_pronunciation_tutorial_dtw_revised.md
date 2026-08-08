# How to Build a Pronunciation Scorer for Language Learning
## A Beginner-Friendly Tutorial for NotebookLM

> **📌 Decision update — 7 July 2026 (see `/DECISIONS.md`, D2):** This tutorial was written around **aeneas** as the alignment layer. That plan was dropped before any code was written, for three reasons: aeneas has been unmaintained since 2017; its AGPL-3 licence would legally require publishing all our source code if we ever sell access to the engine; and aligning single romanised characters through the espeak synthesiser was judged too fragile for accurate vowel boundaries. The project goes **straight to the Montreal Forced Aligner (MFA)** — MIT-licensed, actively maintained, and aligning real phonemes via a trained Persian model. Concretely: Steps 2–3 (espeak/aeneas installation, and with them the Python 3.10 and numpy pins) and Step 7 (aeneas alignment) are superseded by `FABLE_REVIEW.md` Phase 2. The concepts taught here — phonemes, forced alignment, DTW, the vowel map — remain fully valid, and Whisper's role is now the wrong-word gatekeeper (D3). The 65% acoustic / 35% timing weighting in Step 8 is likewise superseded: D4 fixes the constant at **60% acoustic / 40% timing**. For the current hands-on build, follow `BUILD_PLAN.md`.

---

## Who this tutorial is for

This tutorial is for someone who has written a few Python scripts before — maybe to rename files, scrape a webpage, or automate something small — but has never worked with audio, speech recognition, or AI APIs. Every concept is explained before the code that uses it. Nothing is assumed except that you know what a function and a variable are.

By the end, you will have built something genuinely impressive: a script that listens to two people saying the same Persian word, and tells you — vowel by vowel — how closely the learner matched the native speaker.

---

## What problem are we actually solving?

Persian (Farsi) has a beautiful but tricky quirk: **short vowels are almost never written in the script.** When a Persian speaker reads the word سلام, they know from experience that it is pronounced "sa-LÂAM" — but a learner looking at those letters has no idea. The vowels are invisible.

This is called the **hidden vowel problem**, and it is the number one reason Persian is hard to learn from text alone.

Our prototype solves one specific part of this: **did the learner actually pronounce those hidden vowels correctly when they spoke?** Not "did they say the right word" — but "did they hold the â sound long enough? Did they hit the right pitch?"

That is a much harder and more interesting question than simple speech-to-text. It requires us to look inside the audio at the level of individual sounds, not just words.

---

## The big picture: what our script will do

Before we write a single line of code, let us understand the full journey of the audio through our system. Think of it like a factory assembly line with five stations:

**Station 1 — Record**
Two audio files arrive: one from a native Persian speaker, one from a learner. Both are saying the same word or phrase.

**Station 2 — Transcribe**
We feed both audio files to Whisper, OpenAI's speech recognition model. Whisper reads the audio and tells us not just *what* was said, but *when* each word started and ended. This is called a transcript with timestamps.

**Station 3 — Align**
Whisper gives us word-level timing. But we need to go deeper — we need to know when each individual *sound* (phoneme) happened. We use a tool called aeneas to do this finer alignment. Think of it as zooming in from "the word started at 0.3 seconds" to "the â vowel inside that word started at 0.41 seconds and ended at 0.68 seconds."

**Station 4 — Compare**
Now we have timing data for both recordings. We compare them vowel by vowel. Did the learner hold the â sound for roughly as long as the native speaker? We use a mathematical technique called DTW (Dynamic Time Warping) to make this comparison fair even if the learner spoke slightly faster or slower overall.

**Station 5 — Score and annotate**
Each vowel gets a score from 0 to 100. We assign a colour — green for good, amber for close, red for needs work — and package everything into a JSON file. That JSON is the final product of this prototype.

---

## Key concepts you need to understand first

### What is a phoneme?

A phoneme is the smallest unit of sound in a language that changes meaning. In English, the difference between "bit" and "beat" is one phoneme — the vowel sound in the middle. In Persian, the difference between سَر (sar, meaning head) and سیر (sir, meaning full) is also one phoneme.

When we talk about scoring pronunciation, we are scoring phonemes — not letters, not words, but individual sounds.

### What is forced alignment?

Imagine you have a recording of someone reading a poem, and you have the text of the poem. Forced alignment is the process of automatically figuring out which word in the text corresponds to which moment in the audio. "Forced" means we are not asking the computer to figure out what was said — we already know the text — we are forcing the text and audio to line up in time.

In our case, we already know the transliteration (the romanised spelling of the Persian word). We force it to align with the audio so we can find exactly when each sound occurs.

### What is Dynamic Time Warping (DTW)?

Suppose the native speaker says "salâm" in 0.7 seconds, and the learner says it in 0.9 seconds. A simple comparison would say everything is wrong because all the timings are different. DTW is smarter — it stretches or compresses one sequence to match the other before comparing. It finds the best possible alignment between two sequences regardless of overall speed differences.

Think of it like comparing two pieces of music played at different tempos. DTW finds which notes correspond to each other, then compares the notes themselves rather than their absolute positions in time.

### What is a vowel map?

This is a concept specific to our app. For each Persian lesson, we store a small lookup table called a vowel_map. It says: "in this word, at this character position, there is a hidden vowel with this phoneme sound." The scorer then uses the native recording to calculate the expected timing pattern, rather than relying on fixed millisecond values in the lesson data.

Example for the word سلام (salâm):

```
Position 2 → vowel "â" → phoneme /ɑː/
```

The vowel map is what connects the abstract lesson content (what sound should be here) to the audio analysis (did the learner make that sound). Without it, the scorer has no idea what to look for.

### What is JSON?

JSON (JavaScript Object Notation) is a simple way of structuring data as text so that any programming language can read it. It uses curly braces for objects and square brackets for lists. Our prototype produces a JSON file as its final output — this is what the Django backend will eventually send to the React frontend to draw the coloured waveform.

Example of JSON output from our scorer:

```json
{
  "overall_score": 78,
  "waveform_annotations": [
    {
      "time_start": 0.41,
      "time_end": 0.68,
      "label": "â",
      "accuracy": 72,
      "color_hex": "#EF9F27"
    }
  ]
}
```

---

## The tools we will use

### Python
You already know this one. We are using Python 3.10 specifically because one of our libraries (aeneas) has compatibility issues with newer versions. This is common in audio/ML work — library versions matter more than in general scripting.

### Whisper
Whisper is a speech recognition model built by OpenAI and released as open source. Unlike older speech recognition systems that struggled with accents and non-English languages, Whisper was trained on a huge and diverse dataset. It supports approximately 100 languages including Persian (language code: "fa") and Mandarin ("zh").

We use Whisper in a specific mode called word_timestamps=True, which makes it return not just what was said but when each word started and ended. This is the foundation of our alignment pipeline.

Whisper runs locally on your machine. You do not need an internet connection or API key for the prototype.

### aeneas
aeneas is a Python library originally built to help create audiobooks with synchronised text — think of the Kindle feature where the highlighted word follows the narrator. It uses a speech synthesiser (espeak) to generate a reference version of the text, then uses audio comparison algorithms to figure out where each fragment of text appears in the real recording.

For our purposes, we feed it a transliteration of a Persian phrase and the actual audio recording, and it tells us when each character sound occurs.

aeneas is the trickiest tool in this stack to install because it depends on system-level audio tools (ffmpeg and espeak) being present before the Python package is installed. The tutorial covers this carefully.

### librosa
librosa is the standard Python library for audio analysis. It can read audio files, convert them to numerical arrays, measure signal properties, and — crucially for us — run Dynamic Time Warping comparisons between two audio sequences.

Think of librosa as the measuring tape of our pipeline. Whisper and aeneas tell us *where* the sounds are. librosa tells us *how* they compare.

### soundfile
A simple library for reading and writing audio files in formats like WAV. We use it to check that our audio files are valid and in the right format before feeding them to the other tools.

---

## Understanding the file structure we will build

Before writing code, it helps to picture what our project folder will look like when it is complete:

```
persian-pronunciation-prototype/
│
├── venv/                          ← your isolated Python environment
│
├── audio/
│   ├── salaam_native.wav          ← native speaker recording
│   ├── salaam_learner.wav         ← learner recording
│   ├── mamnun_native.wav
│   └── mamnun_learner.wav
│
├── lessons/
│   ├── salaam.json                ← lesson data including vowel_map
│   └── mamnun.json
│
├── step5_whisper_align.py         ← one script per pipeline stage
├── step6_aeneas_align.py
├── step7_score.py
└── step8_validate_all.py
```

Each script does one job. This is intentional — when something goes wrong (and it will, at least once), you can run each stage in isolation and see exactly where the problem is.

---

## Why we use a virtual environment

When you install Python packages with pip, they normally go into a global location on your machine. This causes problems when two projects need different versions of the same library. A virtual environment (venv) is an isolated folder that contains its own Python and its own packages, completely separate from everything else.

Think of it like a clean workbench for this project. Whatever mess we make with library versions, it cannot affect your other projects — and vice versa.

You create it once, and then every time you come back to work on this project you "activate" it before doing anything else.

---

## Step 1 — Setting up your environment

**What you are doing:** Creating a clean, isolated workspace for the project.

**Why this step matters:** aeneas in particular has known conflicts with recent versions of numpy. By isolating everything in a venv on Python 3.10, we sidestep those issues before they happen.

```bash
# Create the project folder
mkdir persian-pronunciation-prototype
cd persian-pronunciation-prototype

# Create a virtual environment using Python 3.10
python3.10 -m venv venv

# Activate it
source venv/bin/activate
# On Windows the command is: venv\Scripts\activate

# You should now see (venv) at the start of your terminal prompt
# Confirm the Python version
python --version
```

**What success looks like:** Your terminal prompt shows `(venv)` and `python --version` prints `Python 3.10.x`.

**Common problem:** If `python3.10` is not found, you may need to install it. On macOS: `brew install python@3.10`. On Ubuntu: `sudo apt install python3.10 python3.10-venv`.

---

## Step 2 — Installing system dependencies

**What you are doing:** Installing two tools that must exist at the operating system level before any Python packages can use them. This is different from pip — these are not Python libraries, they are programs.

**ffmpeg** is a powerful audio and video processing tool used by almost every audio library in the Python ecosystem. It handles reading and converting audio files.

**espeak** is a text-to-speech synthesiser. aeneas uses it to generate a synthetic version of your text so it can compare it against the real audio for alignment purposes. It supports Persian out of the box.

```bash
# macOS (using Homebrew)
brew install ffmpeg espeak

# Ubuntu / Debian Linux
sudo apt-get install ffmpeg espeak libespeak-dev

# Verify both installed correctly
ffmpeg -version | head -1
espeak --version
```

**What success looks like:** Both commands print version information without errors.

**Common problem:** On some Ubuntu versions espeak-ng is installed instead of espeak. If aeneas later complains about espeak, try: `sudo apt-get install espeak-ng` and then in your aeneas config replace `espeak` with `espeak-ng`.

---

## Step 3 — Installing Python packages

**What you are doing:** Installing the four Python libraries the prototype needs. Make sure your venv is active (you see `(venv)` in your terminal) before running these.

```bash
# Speech recognition with timestamps
pip install openai-whisper

# Phoneme-level forced alignment
pip install numpy==1.23.5   # pin this version — aeneas has issues with numpy 2.x
pip install aeneas

# Audio analysis and DTW comparison
pip install librosa soundfile scipy
```

**Test each one:**

```bash
python -c "import whisper; print('Whisper: OK')"
python -c "import aeneas; print('aeneas: OK')"
python -c "import librosa; print('librosa: OK')"
python -c "import soundfile; print('soundfile: OK')"
python -c "import scipy; print('scipy: OK')"
```

**What success looks like:** All four lines print OK.

**Common problem with aeneas:** If it fails to import, the most likely cause is that espeak was not found during installation. Try reinstalling with: `pip install aeneas --no-binary aeneas` which forces it to compile from source and find espeak at compile time.

---

## Step 4 — Creating your lesson files

**What you are doing:** Writing the vowel_map JSON files for your two test phrases. This is not code — it is data. You are describing the hidden vowel structure of each word so the scorer knows what to look for.

**Why you write these by hand for the prototype:** In the full app, these will be authored by a Persian linguist and stored in the Django database. For the prototype, we create them manually for three words so we can test the pipeline end-to-end.

Create a folder called `lessons/` and add these two files:

**lessons/salaam.json**
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

**lessons/mamnun.json**
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

**Understanding the fields:**
- `position` — the exact zero-indexed character position in the transliteration string. For example, in `salâm`, `a` is position 1 and `â` is position 3.
- `vowel` — the romanised symbol for this vowel sound
- `phoneme` — the International Phonetic Alphabet symbol, which is the universal scientific notation for speech sounds
- The expected timing is not stored here. It is calculated from the native recording during scoring, so the lesson file only describes the target vowels.
- The validator later checks that `transliteration[position] == vowel`, because a wrong index can silently score a consonant while labelling it as a vowel.

**What success looks like:** Both files are valid JSON. Test with:
```bash
python -c "import json; json.load(open('lessons/salaam.json')); print('salaam.json: valid')"
python -c "import json; json.load(open('lessons/mamnun.json')); print('mamnun.json: valid')"
```

---

## Step 5 — Collecting your audio files

**What you are doing:** Getting two recordings for each test phrase — one native speaker, one learner — in the correct audio format.

**The format requirements:**
- File type: WAV (not MP3, not M4A)
- Sample rate: 16,000 Hz (16kHz)
- Channels: Mono (one channel, not stereo)

These requirements come from Whisper and aeneas, both of which expect 16kHz mono WAV as their standard input. Using other formats will either cause errors or reduce accuracy.

**Where to get native speaker audio:**
- Forvo.com has free human recordings of individual words in almost every language including Persian
- The Wikimedia Commons audio files for Persian words
- Ask a native speaker to record on their phone's voice memo app, then convert

**How to convert any audio file to the right format:**
```bash
ffmpeg -i input_file.mp3 -ar 16000 -ac 1 output_file.wav
```
The `-ar 16000` sets the sample rate to 16kHz. The `-ac 1` converts to mono.

**For the learner recording during the prototype:** You can record yourself attempting the word, or you can take the native recording and use ffmpeg to slightly alter the pitch to simulate a learner error:
```bash
# Shift pitch slightly to simulate a learner mispronunciation
ffmpeg -i salaam_native.wav -af "asetrate=16000*0.95,aresample=16000" salaam_learner.wav
```

**Verify your audio files:**
```bash
python -c "
import soundfile as sf
data, sr = sf.read('audio/salaam_native.wav')
duration = len(data) / sr
print(f'Sample rate: {sr}Hz  Duration: {duration:.2f}s  Channels: {data.ndim}')
"
```

**What success looks like:** Sample rate is 16000, duration is between 0.3 and 3 seconds, channels is 1.

---

## Step 6 — Running Whisper to get word timestamps

**What you are doing:** Using Whisper to transcribe your native audio file and get back not just the words but the exact time each word starts and ends.

**Why this is impressive:** Traditional speech recognition just returns text. Getting timestamps requires a technique called forced alignment internally — Whisper does this for us automatically when we set `word_timestamps=True`.

Save this as `step5_whisper_align.py` (we keep the step numbering from the handover document):

```python
import whisper
import json
import sys

def transcribe_with_timestamps(audio_path):
    """
    Transcribe a Persian audio file and return word-level timestamps.

    whisper.load_model("medium") loads a 769MB model that balances
    speed and accuracy. For production use "large-v3" (2.9GB) for
    better Persian accuracy. For quick testing use "small" (244MB).
    """

    # Load the model — this downloads it on first run, then caches locally
    model = whisper.load_model("medium")

    result = model.transcribe(
        audio_path,
        language="fa",           # fa = Farsi / Persian
        word_timestamps=True,    # this is what gives us timing data
        verbose=False            # set to True to see progress during transcription
    )

    # Extract word-level timing from the nested segment structure
    words = []
    for segment in result["segments"]:
        for word in segment.get("words", []):
            words.append({
                "word":  word["word"].strip(),
                "start": round(word["start"], 3),  # seconds, 3 decimal places
                "end":   round(word["end"],   3)
            })

    return {
        "text":     result["text"].strip(),
        "language": result["language"],
        "words":    words
    }

# Run when called directly from the command line
if __name__ == "__main__":
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "audio/salaam_native.wav"
    output = transcribe_with_timestamps(audio_file)
    print(json.dumps(output, ensure_ascii=False, indent=2))
```

**Run it:**
```bash
python step5_whisper_align.py audio/salaam_native.wav
```

**What success looks like:**
```json
{
  "text": "سلام",
  "language": "fa",
  "words": [
    { "word": "سلام", "start": 0.0, "end": 0.62 }
  ]
}
```

**What to check:**
- `language` must be `"fa"` not `"ar"` (Arabic). If it says Arabic, add `initial_prompt="متن فارسی"` to the transcribe() call to nudge Whisper toward Persian
- `words` must not be empty
- The `start` and `end` times should be shorter than the total audio duration

**Note on first run:** Whisper will download the model file (~769MB for "medium") on the first run. This is a one-time download. Subsequent runs are instant.

---

## Step 7 — Running aeneas for phoneme-level alignment

**What you are doing:** Going deeper than word-level timing. While Whisper told us "the word سلام happened between 0.0s and 0.62s", aeneas will tell us "the â vowel inside that word happened between 0.31s and 0.62s."

**The concept of text fragments:** aeneas works by splitting your text into fragments and aligning each fragment to the audio. For our purposes, each character in the transliteration is one fragment. This gives us the finest possible granularity.

Save as `step6_aeneas_align.py`:

```python
import json
import os
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

def align_phonemes(audio_path, transliteration, output_path):
    """
    Use aeneas to find the timestamp of each character in a transliteration.

    How it works:
    1. Write each character to a text file, one per line (these are the "fragments")
    2. Configure aeneas with the language and file paths
    3. aeneas synthesises speech from the text using espeak
    4. It then finds where each synthesised fragment appears in the real audio
    5. The result is a sync map: fragment → time range
    """

    # Write each character as a separate fragment for aeneas
    text_path = "/tmp/proto_text.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        for char in transliteration.replace(" ", ""):
            f.write(char + "\n")

    # aeneas configuration string — pipe-separated key=value pairs
    config_string = (
        "task_language=fa|"       # fa = Farsi/Persian
        "is_text_type=plain|"     # plain text, one fragment per line
        "os_task_file_format=json" # output as JSON
    )

    task = Task(config_string=config_string)
    task.audio_file_path_absolute = os.path.abspath(audio_path)
    task.text_file_path_absolute  = os.path.abspath(text_path)
    task.sync_map_file_path_absolute = os.path.abspath(output_path)

    # Execute the alignment
    ExecuteTask(task).execute()
    task.output_sync_map_file()

    # Read and parse the result
    with open(output_path, "r", encoding="utf-8") as f:
        sync_map = json.load(f)

    # Convert to a simple list of {char, start, end}
    fragments = []
    for frag in sync_map.get("fragments", []):
        char = frag["lines"][0] if frag["lines"] else ""
        fragments.append({
            "char":  char,
            "start": float(frag["begin"]),
            "end":   float(frag["end"])
        })

    return fragments

if __name__ == "__main__":
    lesson = json.load(open("lessons/salaam.json"))
    fragments = align_phonemes(
        audio_path="audio/salaam_native.wav",
        transliteration=lesson["transliteration"],
        output_path="/tmp/salaam_sync.json"
    )
    print(json.dumps(fragments, ensure_ascii=False, indent=2))
```

**Run it:**
```bash
python step6_aeneas_align.py
```

**What success looks like:**
```json
[
  { "char": "s", "start": 0.0,  "end": 0.12 },
  { "char": "a", "start": 0.12, "end": 0.22 },
  { "char": "l", "start": 0.22, "end": 0.31 },
  { "char": "â", "start": 0.31, "end": 0.62 },
  { "char": "m", "start": 0.62, "end": 0.74 }
]
```

**The critical thing to check:** The `â` character must appear with a non-zero start and end time. This is the key vowel we are scoring. If it appears with `"start": 0.0, "end": 0.0`, aeneas could not align it — check that espeak's Persian voice is installed.

---

## Step 8 — Scoring the learner against the native with DTW

**What you are doing:** Running alignment on both the native and learner audio, extracting the vowel regions, then comparing those vowel regions in two ways:

1. **Relative timing** — did the learner give the vowel a similar proportion of the word/phrase?
2. **Acoustic similarity using DTW** — does the learner's vowel sound mathematically similar to the native speaker's vowel after allowing for speed differences?

This fixes two weaknesses in a simple duration-only scorer:

- It does not punish a learner just because they spoke the whole word slowly or quickly.
- It actually uses `librosa.sequence.dtw`, so the DTW explanation earlier in the tutorial now matches the code.

### Why relative duration matters

A raw duration such as 320 ms is fragile. A careful learner may say the whole word slowly, and a confident native speaker may say the same word quickly. The better question is not:

```text
Did the vowel last exactly 320 ms?
```

The better question is:

```text
Did the vowel occupy a similar share of the whole word?
```

For example, if the native speaker's â vowel takes 45% of the word and the learner's â vowel takes 48%, that is probably close, even if the learner's absolute recording is slower.

### Why DTW matters

Relative duration still only measures timing. It does not know whether the learner produced the right vowel quality. To get closer to pronunciation scoring, we compare the *sound shape* of the native and learner vowel regions.

We do this by:

1. Cutting out the matching vowel region from the native audio.
2. Cutting out the matching vowel region from the learner audio.
3. Converting each region into MFCC features.
4. Running DTW over the two MFCC sequences.
5. Turning the DTW distance into a 0–100 acoustic similarity score.

MFCCs are compact numerical summaries of speech sound. They are commonly used in speech processing because they capture the broad spectral shape of a sound — roughly, the information that helps distinguish one vowel from another.

Save as `step7_score.py`:

```python
import json
import os
import numpy as np
import librosa
from librosa.sequence import dtw
from scipy.spatial.distance import cdist
from step6_aeneas_align import align_phonemes


def colour_from_score(score):
    """Map a score to a hex colour for the waveform visualiser."""
    if score >= 85:
        return "#1D9E75"   # teal green — good pronunciation
    elif score >= 65:
        return "#EF9F27"   # amber — close but needs work
    else:
        return "#E24B4A"   # red — significant difference


def safe_duration(start, end):
    """Return a non-negative segment duration in seconds."""
    return max(0.0, float(end) - float(start))


def build_position_lookup(fragments):
    """
    Convert aeneas character fragments into a position-indexed lookup.

    Why this matters:
    The earlier prototype used {character: timing}. That breaks when the same
    vowel appears more than once, as in 'mamnun'. A position lookup is safer.
    """
    return {index: fragment for index, fragment in enumerate(fragments)}


def duration_ratio_score(expected_ratio, actual_ratio):
    """
    Score vowel timing using relative duration rather than raw milliseconds.

    A 20% tolerance band receives a perfect timing score. Outside that band,
    the score falls gradually.
    """
    if expected_ratio is None or expected_ratio <= 0:
        return 100

    ratio = actual_ratio / expected_ratio

    if 0.8 <= ratio <= 1.2:
        return 100

    deviation = abs(ratio - 1.0)
    return max(0, int(100 - (deviation - 0.2) * 200))


def load_audio_segment(audio_path, start, end, sr=16000):
    """
    Load a short region from an audio file.

    librosa.load accepts offset and duration in seconds, so we do not need
    to load the entire file just to compare one vowel.
    """
    duration = safe_duration(start, end)
    if duration <= 0:
        return np.array([], dtype=np.float32), sr

    y, sr = librosa.load(
        audio_path,
        sr=sr,
        mono=True,
        offset=max(0.0, float(start)),
        duration=duration
    )
    return y, sr


def mfcc_features(y, sr):
    """
    Convert a vowel audio segment into MFCC features.

    Returns a matrix shaped as frames x features.
    """
    if len(y) < 400:
        return None

    # Use a conservative FFT size for very short vowel clips.
    n_fft = min(1024, max(256, 2 ** int(np.floor(np.log2(len(y))))))
    hop_length = max(64, n_fft // 4)

    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13,
        n_fft=n_fft,
        hop_length=hop_length
    )

    # Normalise each coefficient so loudness differences matter less.
    mfcc = (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (
        np.std(mfcc, axis=1, keepdims=True) + 1e-8
    )

    return mfcc.T


def dtw_acoustic_score(native_audio, learner_audio, native_fragment, learner_fragment):
    """
    Compare native and learner vowel regions using MFCC + DTW.

    Returns:
    - score: 0–100, where higher means more acoustically similar
    - average_cost: the normalised DTW distance
    """
    native_y, sr = load_audio_segment(
        native_audio,
        native_fragment["start"],
        native_fragment["end"]
    )
    learner_y, _ = load_audio_segment(
        learner_audio,
        learner_fragment["start"],
        learner_fragment["end"],
        sr=sr
    )

    native_mfcc = mfcc_features(native_y, sr)
    learner_mfcc = mfcc_features(learner_y, sr)

    if native_mfcc is None or learner_mfcc is None:
        return 0, None

    # Build a frame-by-frame cost matrix, then let DTW find the best path.
    cost_matrix = cdist(native_mfcc, learner_mfcc, metric="cosine")
    accumulated_cost, warping_path = dtw(C=cost_matrix)

    average_cost = float(accumulated_cost[-1, -1] / len(warping_path))

    # Convert cost into a score. This calibration is deliberately simple;
    # production systems should tune it against labelled learner data.
    score = int(round(100 * np.exp(-3.0 * average_cost)))
    score = max(0, min(100, score))

    return score, average_cost


def score_pronunciation(lesson_path, native_audio, learner_audio):
    """
    Full pipeline:
    1. Load lesson metadata.
    2. Align native and learner audio character by character.
    3. Score each target vowel using relative duration and DTW.
    4. Return JSON for the Django API and waveform visualiser.
    """
    lesson = json.load(open(lesson_path, encoding="utf-8"))
    vowel_map = lesson["vowel_map"]
    transliteration = lesson["transliteration"]

    native_fragments = align_phonemes(
        audio_path=native_audio,
        transliteration=transliteration,
        output_path="/tmp/native_sync.json"
    )

    learner_fragments = align_phonemes(
        audio_path=learner_audio,
        transliteration=transliteration,
        output_path="/tmp/learner_sync.json"
    )

    native_by_position = build_position_lookup(native_fragments)
    learner_by_position = build_position_lookup(learner_fragments)

    native_total_duration = safe_duration(
        native_fragments[0]["start"],
        native_fragments[-1]["end"]
    ) if native_fragments else 0

    learner_total_duration = safe_duration(
        learner_fragments[0]["start"],
        learner_fragments[-1]["end"]
    ) if learner_fragments else 0

    vowel_accuracy = []
    waveform_annotations = []

    for entry in vowel_map:
        position = entry["position"]
        vowel_char = entry["vowel"]

        native_fragment = native_by_position.get(position)
        learner_fragment = learner_by_position.get(position)

        if not native_fragment or not learner_fragment:
            continue

        native_vowel_duration = safe_duration(
            native_fragment["start"],
            native_fragment["end"]
        )
        learner_vowel_duration = safe_duration(
            learner_fragment["start"],
            learner_fragment["end"]
        )

        native_ratio = (
            native_vowel_duration / native_total_duration
            if native_total_duration > 0 else None
        )
        learner_ratio = (
            learner_vowel_duration / learner_total_duration
            if learner_total_duration > 0 else None
        )

        # Use the native clip as the timing reference.
        expected_ratio = native_ratio
        timing_score = duration_ratio_score(expected_ratio, learner_ratio)

        acoustic_score, dtw_cost = dtw_acoustic_score(
            native_audio=native_audio,
            learner_audio=learner_audio,
            native_fragment=native_fragment,
            learner_fragment=learner_fragment
        )

        # Acoustic similarity matters more than timing, but timing still helps.
        final_score = int(round((0.35 * timing_score) + (0.65 * acoustic_score)))
        colour = colour_from_score(final_score)

        vowel_accuracy.append({
            "position": position,
            "vowel": vowel_char,
            "phoneme": entry["phoneme"],
            "native_ratio": round(native_ratio, 3) if native_ratio else None,
            "learner_ratio": round(learner_ratio, 3) if learner_ratio else None,
            "timing_score": timing_score,
            "acoustic_score": acoustic_score,
            "dtw_average_cost": round(dtw_cost, 4) if dtw_cost is not None else None,
            "score": final_score,
            "segment": [
                round(learner_fragment["start"], 3),
                round(learner_fragment["end"], 3)
            ]
        })

        waveform_annotations.append({
            "time_start": round(learner_fragment["start"], 3),
            "time_end": round(learner_fragment["end"], 3),
            "label": vowel_char,
            "accuracy": final_score,
            "color_hex": colour
        })

    scores = [v["score"] for v in vowel_accuracy]
    overall_score = int(np.mean(scores)) if scores else 0

    return {
        "overall_score": overall_score,
        "vowel_accuracy": vowel_accuracy,
        "waveform_annotations": waveform_annotations
    }


if __name__ == "__main__":
    result = score_pronunciation(
        lesson_path="lessons/salaam.json",
        native_audio="audio/salaam_native.wav",
        learner_audio="audio/salaam_learner.wav"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

**Run it:**

```bash
python step7_score.py
```

**What success looks like:**

```json
{
  "overall_score": 82,
  "vowel_accuracy": [
    {
      "position": 3,
      "vowel": "â",
      "phoneme": "/ɑː/",
      "native_ratio": 0.42,
      "learner_ratio": 0.46,
      "timing_score": 100,
      "acoustic_score": 73,
      "dtw_average_cost": 0.1045,
      "score": 82,
      "segment": [0.34, 0.71]
    }
  ],
  "waveform_annotations": [
    {
      "time_start": 0.34,
      "time_end": 0.71,
      "label": "â",
      "accuracy": 82,
      "color_hex": "#EF9F27"
    }
  ]
}
```

### Important calibration warning

The line below is a deliberately simple prototype calibration:

```python
score = int(round(100 * np.exp(-3.0 * average_cost)))
```

This turns a DTW distance into a human-readable score. It is useful for a prototype, but it is not scientifically validated. In a production app, you would tune this conversion against labelled learner recordings judged by Persian teachers.

### What this version now scores

This revised scorer is no longer just checking whether a learner held a vowel for the right number of milliseconds. It now combines:

- **Timing similarity** — did the vowel occupy the right proportion of the word?
- **Acoustic similarity** — did the vowel sound similar to the native version after DTW alignment?

This is still not a complete pronunciation assessment system, but it is a much stronger architecture than a raw duration scorer.

## Step 9 — Validating everything end to end

**What you are doing:** Running one final script that tests both lesson files automatically and tells you whether the prototype is ready. This is your green-light check before handing the pipeline to the Django developer.

Save as `step8_validate_all.py`:

```python
import json
import os
from step7_score import score_pronunciation

lessons = [
    ("lessons/salaam.json", "audio/salaam_native.wav", "audio/salaam_learner.wav"),
    ("lessons/mamnun.json", "audio/mamnun_native.wav", "audio/mamnun_learner.wav"),
]

passed = 0
failed = 0

for lesson_path, native_audio_path, learner_audio_path in lessons:
    name = os.path.basename(lesson_path)
    print(f"\n--- Testing {name} ---")

    try:
        # Check schema completeness
        lesson = json.load(open(lesson_path))
        assert "vowel_map"       in lesson
        assert "transliteration" in lesson
        transliteration = lesson["transliteration"]
        for entry in lesson["vowel_map"]:
            assert "position"    in entry
            assert "vowel"       in entry
            assert "phoneme"     in entry
            position = entry["position"]
            assert 0 <= position < len(transliteration)
            assert transliteration[position] == entry["vowel"]
        print(f"  Schema:  PASSED — {len(lesson['vowel_map'])} vowels defined")

        # Run the full scoring pipeline
        result = score_pronunciation(lesson_path, native_audio_path, learner_audio_path)
        assert 0 <= result["overall_score"] <= 100
        assert len(result["waveform_annotations"]) > 0

        print(f"  Scoring: PASSED — overall score {result['overall_score']}")
        print(f"  Output:  {len(result['waveform_annotations'])} vowel regions annotated")
        passed += 1

    except AssertionError as e:
        print(f"  FAILED — assertion error: {e}")
        failed += 1
    except Exception as e:
        print(f"  FAILED — {e}")
        failed += 1

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if failed == 0:
    print("Prototype is ready for Django integration.")
else:
    print("Fix the failures above before proceeding.")
```

**Run it:**
```bash
python step8_validate_all.py
```

**What success looks like:**
```
--- Testing salaam.json ---
  Schema:  PASSED — 3 vowels defined
  Scoring: PASSED — overall score 84
  Output:  3 vowel regions annotated

--- Testing mamnun.json ---
  Schema:  PASSED — 3 vowels defined
  Scoring: PASSED — overall score 71
  Output:  3 vowel regions annotated

========================================
Results: 2 passed, 0 failed
Prototype is ready for Django integration.
```

---

## What the prototype does NOT do

It is important to be clear about scope. This prototype does not:

- Have a user interface of any kind — it is command-line only
- Connect to a database
- Handle multiple users
- Work in real time — processing takes several seconds per clip
- Handle very long audio (keep clips under 10 seconds for the prototype)
- Fully judge pronunciation quality — this version combines relative vowel timing and MFCC/DTW acoustic similarity, but pitch, stress, rhythm, and teacher-calibrated scoring are future features

All of those things come later. The prototype's only job is to prove that the alignment pipeline works for Persian vowels and that the vowel_map schema is correct.

---

## What comes next

Once all tests pass, these scripts get handed to the Django developer who will:

1. Wrap `step5_whisper_align.py` into a service class
2. Wrap `step6_aeneas_align.py` into a service class
3. Wrap `step7_score.py` into a service class
4. Create a Django view at `POST /api/v1/lessons/{slug}/pronunciation/` that calls all three in sequence
5. Run the processing in a Celery background task so the API responds quickly
6. Store the `waveform_annotations` result in the database

The React frontend then calls that API endpoint and passes the `waveform_annotations` array to the WaveformViewer component, which draws the coloured overlay on the audio waveform.

The vowel_map JSON schema you validated in Step 4 becomes the exact structure stored in the `PersianTextLayer.vowel_map` database column — no changes needed.

---

## Troubleshooting reference

| Problem | Most likely cause | Fix |
|---|---|---|
| `python3.10` not found | Python 3.10 not installed | `brew install python@3.10` or `sudo apt install python3.10` |
| `aeneas` fails to import | espeak not found | Install espeak before pip installing aeneas |
| Whisper detects Arabic | Audio quality or accent | Add `initial_prompt="متن فارسی"` to transcribe() call |
| aeneas returns all-zero timestamps | espeak Persian voice missing | `espeak --voices \| grep fa` — if empty, reinstall espeak-ng |
| Audio file errors | Wrong format | Convert with `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav` |
| numpy conflicts | Wrong numpy version | `pip install numpy==1.23.5` before installing aeneas |

---

*Tutorial scope: A1 Persian, colloquial register, two phrases minimum.*
*Estimated time to complete all steps: 3–4 hours including audio collection.*
*Next document: Django integration guide (written after prototype validation).*
