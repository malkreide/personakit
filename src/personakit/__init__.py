"""personakit – evidence-based, behaviour-first personas as versioned Markdown files.

Source of truth is a ``<id>.persona.md`` file: YAML frontmatter (structured data,
validated against ``schema/persona.schema.json``) plus a Markdown body (scenario,
narrative). Everything else – JSON, YAML, prompt blocks, cards, HTML – is rendered.
"""

__version__ = "0.2.0"
FORMAT_VERSION = "1.0"
