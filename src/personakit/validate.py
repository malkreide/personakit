"""JSON-Schema validation of persona frontmatter, set files, factoid files and probe files."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .model import Persona


def _read_schema(name: str) -> dict[str, Any]:
    with resources.files("personakit").joinpath(f"schema/{name}").open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    return _read_schema("persona.schema.json")


@lru_cache(maxsize=1)
def load_set_schema() -> dict[str, Any]:
    return _read_schema("set.schema.json")


@lru_cache(maxsize=8)
def _named_validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(_read_schema(name), format_checker=FormatChecker())


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema(), format_checker=FormatChecker())


@lru_cache(maxsize=1)
def _set_validator() -> Draft202012Validator:
    return Draft202012Validator(load_set_schema(), format_checker=FormatChecker())


def _messages(validator: Draft202012Validator, data: Any) -> list[str]:
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    return errors


def validate(persona: Persona) -> list[str]:
    """Return a list of human-readable schema violations (empty = valid)."""
    return _messages(_validator(), persona.plain())


def validate_set(data: dict[str, Any]) -> list[str]:
    """Schema violations of a plain ``set.yml`` mapping (empty = valid)."""
    return _messages(_set_validator(), data)


def validate_factoids(data: dict[str, Any]) -> list[str]:
    """Schema violations of the frontmatter of a ``*.factoids.md`` file (empty = valid)."""
    return _messages(_named_validator("factoids.schema.json"), data)


def validate_variables(data: dict[str, Any]) -> list[str]:
    """Schema violations of a plain ``variables.yml`` mapping (empty = valid)."""
    return _messages(_named_validator("variables.schema.json"), data)


def validate_probe_plan(data: Any) -> list[str]:
    """Schema violations of a probe plan (``probe build``) (empty = valid)."""
    return _messages(_named_validator("probe.schema.json"), data)


def validate_probe_answers(data: Any) -> list[str]:
    """Schema violations of an answers file for ``probe evaluate`` (empty = valid)."""
    return _messages(_named_validator("probe-answers.schema.json"), data)


def validate_probe_keywords(data: Any) -> list[str]:
    """Schema violations of a keyword file for ``probe evaluate --keywords`` (empty = valid)."""
    return _messages(_named_validator("probe-keywords.schema.json"), data)
