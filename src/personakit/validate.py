"""JSON-Schema validation of persona frontmatter."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .model import Persona


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    with resources.files("personakit").joinpath("schema/persona.schema.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema(), format_checker=FormatChecker())


def validate(persona: Persona) -> list[str]:
    """Return a list of human-readable schema violations (empty = valid)."""
    errors = []
    for err in sorted(_validator().iter_errors(persona.plain()), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    return errors
