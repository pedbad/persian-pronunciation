# src/core/context_processor.py
from django.conf import settings


def site_meta(_request):
    return {
        "SITE_ORIGIN": getattr(settings, "SITE_ORIGIN", ""),
        "SITE_NAME": getattr(settings, "SITE_NAME", "Persian Pronunciation"),
        "SITE_DESCRIPTION": getattr(
            settings,
            "SITE_DESCRIPTION",
            "Vowel-by-vowel pronunciation feedback for Persian learners.",
        ),
    }
