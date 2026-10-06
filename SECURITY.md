# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | yes |

## Reporting a vulnerability

personakit is a local command-line tool without network access. Relevant findings are therefore mostly about parsing untrusted persona files (YAML, Markdown) and rendered HTML.

Please report vulnerabilities privately via [GitHub Security Advisories](https://github.com/malkreide/personakit/security/advisories/new) rather than as public issues. Include the affected version, steps to reproduce and, if possible, a minimal persona file. You will receive an acknowledgement within 7 days.

## Scope notes

- Persona files are user-authored data. The HTML export escapes all persona content; if you find an injection path, that is in scope.
- Example personas in this repository are synthetic and contain no personal data. Please keep it that way in contributions.
