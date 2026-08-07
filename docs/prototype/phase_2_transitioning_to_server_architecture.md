# Phase 2: Transitioning to Server Architecture

## Django Database Model Design Review and Recommendations

> **📌 Decision update — 7 July 2026 (see `/DECISIONS.md`, D2):** The alignment layer is now the **Montreal Forced Aligner (MFA)**, not aeneas (unmaintained, AGPL-licensed, fragile at character level — dropped before implementation). Model impact: `LanguageProfile.espeak_voice_code` should become aligner model references instead — e.g. `mfa_dictionary` and `mfa_acoustic_model` fields, or keys inside `profile_config`. Additionally, per **D9 (7 Aug 2026)**, `Lesson.native_reference_audio` is replaced by a `NativeReference` model (lesson → many references, each with audio, speaker sex, optional dialect/register note, `is_active`, cached per-vowel segment times), and the `assessment_payload` records the winning `reference_id`. Everything else in this document stands, and per D2 the `assessment_payload` should additionally record the engine version block (`scorer_version`, aligner name/version, weights — see `FABLE_REVIEW.md` Step 16).

This document records the Phase 2 architectural review for moving the Persian pronunciation prototype from standalone Python scripts into a Django server architecture.

The proposed model design is directionally strong. The three core concepts are correct:

```text
LanguageProfile 1 ─── * Lesson 1 ─── * UtteranceAttempt
```

This is the right foundation for a multilingual pronunciation platform. However, the first-pass model design is still too prototype-shaped for production. It stores the right objects, but it does not yet enforce enough correctness around JSON schemas, audio lifecycle, async task state, content versioning, and learner-attempt retention.

The key principle for Phase 2 is:

> Treat JSON fields as versioned contracts, not convenient dumping grounds.

---

## 1. Overall Assessment

The original design has the correct core entities:

- `LanguageProfile`
- `Lesson`
- `UtteranceAttempt`

The relationship between them is also correct:

```text
LanguageProfile
  └── Lesson
        └── UtteranceAttempt
```

The design correctly recognises that the system needs multilingual configuration, lesson-level reference audio, hidden-vowel maps, learner audio attempts, async task state, and a stored scoring payload for frontend replay.

Using PostgreSQL `JSONField` / JSONB is also sensible for `vowel_map`, `assessment_payload`, and future multilingual profile configuration.

However, the current schema should not be frozen yet. It needs hardening before it becomes the basis for migrations, admin tooling, API serializers, Celery tasks, or frontend contracts.

---

## 2. What Is Strong in the Proposed Design

### 2.1 `LanguageProfile` is the right abstraction

A multilingual pronunciation platform needs a language-level configuration object. This fits the “One Engine, Every Language” architecture and prevents Persian-specific logic from being hardcoded into the application.

Good existing fields:

```python
id
display_name
whisper_language_code
espeak_voice_code
is_active
```

### 2.2 `Lesson` is the right place for target prompt data

A lesson needs to hold native script, transliteration, English translation, native reference audio, and vowel-map data. The lesson represents the known prompt against which the learner’s speech is assessed.

### 2.3 `UtteranceAttempt` is the right ledger object

A learner pronunciation attempt should be a separate record from the lesson itself. It needs to store the user, lesson, learner audio, processing status, final score, assessment payload, and error state.

### 2.4 `models.PROTECT` from `Lesson` to `LanguageProfile` is correct

A language profile should not be deletable while lessons depend on it.

### 2.5 UUIDs are reasonable for public-facing IDs

UUIDs are useful for non-sequential API paths and external references. They are not a substitute for permissions, but they are still a sensible default for lessons and attempts.

---

## 3. Key Problems in the First-Pass Model Design

### 3.1 `celery_task_id` should not be a `UUIDField`

Celery task IDs often look UUID-like, but they are not guaranteed to be valid UUID values in every configuration.

Use:

```python
celery_task_id = models.CharField(
    max_length=255,
    null=True,
    blank=True,
    db_index=True,
)
```

### 3.2 `UtteranceAttempt.lesson` should not cascade-delete attempts

The original design uses:

```python
lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
```

This means deleting a lesson deletes all learner attempt records. For a production learning platform, that is usually wrong.

Recommended MVP choice:

```python
lesson = models.ForeignKey(
    Lesson,
    on_delete=models.PROTECT,
    related_name="attempts",
)
```

### 3.3 `Lesson` says “immutable” but includes `updated_at`

If attempts are scored against a lesson’s `vowel_map`, then changing that `vowel_map` later can make old attempts unreproducible.

At minimum, add:

```python
version = models.PositiveIntegerField(default=1)
is_published = models.BooleanField(default=False)
is_active = models.BooleanField(default=True)
```

Longer-term, consider a separate `LessonVersion` model.

### 3.4 `vowel_map` needs model-level validation

The most dangerous failure mode is not a crash. It is a silent pass where the system scores the wrong character.

The model must enforce:

```text
position is int
0 <= position < len(transliteration)
transliteration[position] == vowel
expected_ms is not present
phoneme exists
```

This prevents the old “silent consonant bug”, where the system accidentally scores `l` or `n` while labelling the result as a vowel.

### 3.5 `LanguageProfile` needs more future-facing configuration

For a global platform, `LanguageProfile` needs more than Whisper and espeak codes.

Recommended additional fields:

```python
script_direction
feature_focus
profile_config
```

These support language-specific differences such as right-to-left script, tone scoring, pitch accent, stress placement, and additional acoustic extraction settings.

### 3.6 Audio storage needs lifecycle metadata

Learner recordings are sensitive and storage-heavy. The attempt model should store basic audio metadata:

```python
audio_duration_ms
audio_sample_rate
audio_mime_type
delete_after
```

### 3.7 Async processing needs timestamps

`created_at` alone is insufficient for diagnosing worker behaviour.

Add:

```python
processing_started_at
processing_finished_at
updated_at
```

### 3.8 Add database-level score constraints

Application code should not be the only thing preventing invalid scores.

Add a `CheckConstraint` to enforce:

```text
overall_score is null OR 0 <= overall_score <= 100
```

### 3.9 JSONB indexing must be explicit

Using JSONB is sensible, but “deep querying” only works well if the correct indexes are added.

For JSONB fields that may be queried, add PostgreSQL GIN indexes:

```python
GinIndex(fields=["vowel_map"], name="lesson_vowel_map_gin")
GinIndex(fields=["assessment_payload"], name="attempt_payload_gin")
```

If these fields are only stored and retrieved as whole blobs, indexing may not be needed immediately.

---

## 4. Recommended Revised Models

The following model direction keeps the original architecture but hardens it for multilingual expansion, JSON validation, attempt retention, async tracking, and future profile configuration.

---

## 5. `LanguageProfile`

```python
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.postgres.indexes import GinIndex


class LanguageProfile(models.Model):
    class ScriptDirection(models.TextChoices):
        LTR = "ltr", "Left to right"
        RTL = "rtl", "Right to left"

    id = models.SlugField(
        max_length=20,
        primary_key=True,
        help_text="e.g. persian, swahili, cantonese",
    )

    display_name = models.CharField(max_length=100, unique=True)

    whisper_language_code = models.CharField(
        max_length=10,
        help_text="Whisper language code, e.g. fa, sw, zh, yue",
    )

    espeak_voice_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="System speech synthesis voice code, e.g. fa, sw",
    )

    script_direction = models.CharField(
        max_length=3,
        choices=ScriptDirection.choices,
        default=ScriptDirection.LTR,
    )

    feature_focus = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. vowel_duration, tone, pitch_accent, stress",
    )

    profile_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Language-specific scoring and alignment configuration.",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return f"{self.display_name} ({self.id})"
```

---

## 6. `vowel_map` Validator

This should live somewhere reusable, for example:

```text
lessons/validators.py
```

```python
from django.core.exceptions import ValidationError


def validate_vowel_map(transliteration: str, vowel_map: list[dict]) -> None:
    if not isinstance(vowel_map, list):
        raise ValidationError("vowel_map must be a list.")

    for entry in vowel_map:
        if not isinstance(entry, dict):
            raise ValidationError("Each vowel_map entry must be an object.")

        required = {"position", "vowel", "phoneme"}
        missing = required - set(entry.keys())

        if missing:
            raise ValidationError(f"Missing vowel_map keys: {missing}")

        if "expected_ms" in entry:
            raise ValidationError("expected_ms is deprecated and must not be used.")

        position = entry["position"]
        vowel = entry["vowel"]

        if not isinstance(position, int):
            raise ValidationError("vowel_map.position must be an integer.")

        if position < 0 or position >= len(transliteration):
            raise ValidationError(f"vowel_map position out of range: {position}")

        if transliteration[position] != vowel:
            raise ValidationError(
                f"vowel_map mismatch: transliteration[{position}] is "
                f"{transliteration[position]!r}, not {vowel!r}."
            )
```

This validator is essential. Without it, the old data bug can re-enter through Django admin, fixtures, management commands, API serializers, or direct imports.

---

## 7. `Lesson`

```python
class Lesson(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    language = models.ForeignKey(
        LanguageProfile,
        on_delete=models.PROTECT,
        related_name="lessons",
    )

    slug = models.SlugField(max_length=120)

    title = models.CharField(max_length=255, blank=True)

    script_rtl = models.CharField(
        max_length=255,
        help_text="Native text script representation, e.g. سلام",
    )

    transliteration = models.CharField(
        max_length=255,
        help_text="Target alignment string, e.g. salâm",
    )

    translation_en = models.CharField(max_length=255)

    native_reference_audio = models.FileField(
        upload_to="audio/native/",
        help_text="Master native gold-standard WAV file.",
    )

    vowel_map = models.JSONField(
        help_text="Zero-indexed transliteration vowel targets. No expected_ms.",
    )

    version = models.PositiveIntegerField(default=1)

    is_published = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        validate_vowel_map(self.transliteration, self.vowel_map)

    class Meta:
        ordering = ["language", "transliteration"]
        constraints = [
            models.UniqueConstraint(
                fields=["language", "slug", "version"],
                name="unique_lesson_language_slug_version",
            )
        ]
        indexes = [
            GinIndex(fields=["vowel_map"], name="lesson_vowel_map_gin"),
        ]

    def __str__(self):
        return f"{self.language_id.upper()} | {self.transliteration}"
```

---

## 8. `UtteranceAttempt`

```python
class UtteranceAttempt(models.Model):
    class ProcessStatus(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pronunciation_attempts",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.PROTECT,
        related_name="attempts",
    )

    learner_audio_recording = models.FileField(
        upload_to="audio/attempts/",
        help_text="Uploaded user attempt recording.",
    )

    status = models.CharField(
        max_length=20,
        choices=ProcessStatus.choices,
        default=ProcessStatus.QUEUED,
        db_index=True,
    )

    celery_task_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    overall_score = models.PositiveSmallIntegerField(null=True, blank=True)

    assessment_payload = models.JSONField(null=True, blank=True)

    audio_duration_ms = models.PositiveIntegerField(null=True, blank=True)

    audio_sample_rate = models.PositiveIntegerField(null=True, blank=True)

    audio_mime_type = models.CharField(max_length=100, blank=True)

    delete_after = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    processing_started_at = models.DateTimeField(null=True, blank=True)

    processing_finished_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["lesson", "-created_at"]),
            GinIndex(fields=["assessment_payload"], name="attempt_payload_gin"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(overall_score__isnull=True)
                    | (Q(overall_score__gte=0) & Q(overall_score__lte=100))
                ),
                name="attempt_overall_score_0_100",
            )
        ]

    def __str__(self):
        return f"Attempt {self.id} | User {self.user_id} | {self.status}"
```

---

## 9. Recommended Minimal Content Hierarchy

The three-model design can work for the prototype. However, for an LMS, `Lesson` will quickly become overloaded unless there is at least one parent content object.

Recommended near-term hierarchy:

```text
LanguageProfile
  └── Course or Module
        └── Lesson
              └── UtteranceAttempt
```

A minimal `Module` model could include:

```python
class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    language = models.ForeignKey(
        LanguageProfile,
        on_delete=models.PROTECT,
        related_name="modules",
    )

    slug = models.SlugField(max_length=120)

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["language", "order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["language", "slug"],
                name="unique_module_language_slug",
            )
        ]

    def __str__(self):
        return f"{self.language_id.upper()} | {self.title}"
```

Then `Lesson` can include:

```python
module = models.ForeignKey(
    Module,
    on_delete=models.PROTECT,
    related_name="lessons",
    null=True,
    blank=True,
)
```

For Phase 2, this can be optional. But it is better to introduce the idea early than to retrofit it after lessons have multiplied.

---

## 10. Admin and Serializer Safeguards

Model-level validation is necessary but not sufficient.

Add the same validation to:

- Django admin forms
- DRF serializers
- seed-data import commands
- fixtures
- bulk upload scripts

The `vowel_map` must not be treated as arbitrary JSON.

Every path that creates or updates a `Lesson` should call:

```python
validate_vowel_map(transliteration, vowel_map)
```

The most important rule remains:

```python
assert transliteration[position] == entry["vowel"]
```

---

## 11. Attempt Lifecycle Recommendation

A typical attempt lifecycle should be:

```text
QUEUED
  → PROCESSING
      → SUCCESS
      → FAILED
```

Recommended behaviour:

### On upload

- Create `UtteranceAttempt`
- Store learner audio
- Set `status = QUEUED`
- Dispatch Celery task
- Store `celery_task_id`

### On worker start

- Set `status = PROCESSING`
- Set `processing_started_at`

### On scoring success

- Store `overall_score`
- Store `assessment_payload`
- Set `status = SUCCESS`
- Set `processing_finished_at`

### On scoring failure

- Set `status = FAILED`
- Store safe `error_message`
- Set `processing_finished_at`

The API should never run Whisper, aeneas, or DTW inline inside a request/response cycle.

---

## 12. API Output Contract

The frontend should be able to rely on this output shape:

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

This should be treated as an output contract between:

```text
pronunciation_scorer.py
UtteranceAttempt.assessment_payload
Django REST API
React WaveformViewer
```

---

## 13. Implementation Order for Phase 2

Recommended sequence:

1. Add hardened Django models.
2. Add `validate_vowel_map`.
3. Add admin support with validation.
4. Add seed fixtures for Persian `salâm` and `mamnun`.
5. Add `UtteranceAttempt` creation endpoint.
6. Add Celery task shell.
7. Add pronunciation service wrapper.
8. Store `assessment_payload`.
9. Add polling endpoint for attempt status.
10. Wire `waveform_annotations` to the frontend.

---

## 14. Final Recommendation

The original Phase 2 model design is a strong starting point, but it should not be frozen as-is.

The corrected production-oriented version should:

- keep `LanguageProfile`, `Lesson`, and `UtteranceAttempt`;
- add model-level `vowel_map` validation;
- remove all traces of `expected_ms`;
- enforce correct zero-index transliteration positions;
- use `CharField` for Celery task IDs;
- protect attempts from accidental lesson deletion;
- track async processing timestamps;
- add score constraints;
- add audio metadata and retention fields;
- consider a minimal `Module` layer before lesson volume grows.

The central architectural truth is:

> The database must protect the pronunciation pipeline from silent data bugs.

If the database allows invalid `vowel_map` entries, the scorer may still run successfully while scoring the wrong sound. Phase 2 should prevent that class of bug before any API or frontend code depends on the schema.
