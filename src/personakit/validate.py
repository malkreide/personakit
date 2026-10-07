"""JSON-Schema validation of persona frontmatter and set files."""

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
