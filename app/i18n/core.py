"""
Internationalization (i18n) module - Disney-style flat key lookup.

Uses dot-notation keys like lodash's `_.get()` to resolve nested translation
values. Example: t("error.not_found") -> "Resource not found"
"""

import json
from contextvars import ContextVar
from pathlib import Path

import pydash

from app.config import settings

_current_locale: ContextVar[str] = ContextVar("current_locale", default=settings.DEFAULT_LOCALE)

_translations: dict[str, dict] = {}

LOCALES_DIR = Path(__file__).parent / "locales"


def _load_translations() -> None:
    """Load all locale JSON files into memory."""
    for locale_dir in LOCALES_DIR.iterdir():
        if not locale_dir.is_dir():
            continue
        locale = locale_dir.name
        _translations[locale] = {}
        for json_file in locale_dir.glob("*.json"):
            namespace = json_file.stem
            with open(json_file, encoding="utf-8") as f:
                _translations[locale][namespace] = json.load(f)


def get_locale() -> str:
    return _current_locale.get()


def set_locale(locale: str) -> None:
    if locale in settings.SUPPORTED_LOCALES:
        _current_locale.set(locale)
    else:
        _current_locale.set(settings.DEFAULT_LOCALE)


def t(key: str, default: str | None = None, **kwargs: str) -> str:
    """
    Translate a key using dot-notation (lodash-style deep get).

    Usage:
        t("error.not_found")           -> "Resource not found"
        t("user.created")              -> "User created successfully"
        t("common.welcome")            -> "Welcome"

    Keys are resolved as: <namespace>.<path> where namespace defaults to "common".
    Supports interpolation: t("greeting", name="John") with "{name}" placeholders.
    """
    if not _translations:
        _load_translations()

    locale = get_locale()
    parts = key.split(".", 1)

    if len(parts) == 2 and parts[0] in _translations.get(locale, {}):
        namespace, path = parts
    else:
        namespace = "common"
        path = key

    locale_data = _translations.get(locale, {})
    ns_data = locale_data.get(namespace, {})

    # Use pydash.get for lodash-style deep path access
    value = pydash.get(ns_data, path, default)

    if value is None:
        # Fallback to default locale
        fallback_data = _translations.get(settings.DEFAULT_LOCALE, {})
        fallback_ns = fallback_data.get(namespace, {})
        value = pydash.get(fallback_ns, path, default or key)

    if isinstance(value, str) and kwargs:
        for k, v in kwargs.items():
            value = value.replace(f"{{{k}}}", v)

    return value if isinstance(value, str) else key
