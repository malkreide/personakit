---
# personakit – Persona-Datei. Frontmatter = strukturierte Daten, Body = Narrativ.
# Leitprinzip: Jedes Feld muss eine Gestaltungsentscheidung beeinflussen können.
# Was keine Entscheidung beeinflusst, wird gestrichen (Tschechows Gewehr).
personakit: "1.0"
id: {{id}}
archetype: "{{archetype}}"          # verhaltensbasiert, nicht demografisch
# name: ""                           # optional – Vorname für narrative Ansprache
tagline: ""                          # ein Satz in den Worten der Persona
kind: user                           # user | buyer | stakeholder | partner | operator
priority: secondary                  # primary | secondary | supplemental | negative
domain: ""                           # z. B. «Volksschule Stadt Zürich – Elternkommunikation»
scope: ""                            # gilt für … / gilt nicht für …
language: de-CH
version: "0.1.0"
status: draft                        # draft | active | retired
evidence_level: proto                # proto | qualitative | statistical
owner: ""
created: {{today}}
updated: {{today}}
review_by: {{review_by}}
tags: []

# Biografische Fakten NUR mit Relevanz-Begründung.
profile:
  - fact: ""
    relevance: ""

context:
  role: ""
  situation: ""
  environment: ""
  channels: []
  constraints: []

# 3–7 Verhaltensvariablen als Skalen 1–5 mit Ankern.
behaviour:
  variables:
    - name: ""
      low: ""
      high: ""
      value: 3
  patterns: []

goals:
  experience: []                     # wie will sie sich fühlen (nie verletzen)
  end: []                            # was will sie erreichen
  life: []                           # langfristig (optional)

pains: []

# Jobs-to-be-Done als Job Story: «Wenn [Situation], möchte ich [Motivation], damit [Ergebnis].»
jobs:
  - id: J1
    statement: ""
    dimension: [functional]
    forces:
      push: []
      pull: []
      anxiety: []
      habit: []
    outcomes: []
    importance: 3
    satisfaction: 3

quotes: []

anti_patterns: []

# Regeln für den Einsatz als Prompt-Voreinstellung.
simulation:
  voice: ""
  must: []
  must_not: []
  variance: ""

evidence: []
assumptions: []
unknowns: []

relations:
  journeys: []
  personas: []
  links: []

changelog:
  - version: "0.1.0"
    date: {{today}}
    note: "Angelegt"
---

## Szenario

<!-- Eine konkrete Situation, in der die Persona mit der Lösung interagiert.
     Erst mit Szenario wird die Persona zum Testinstrument. -->

## Narrativ

<!-- Optional: kurze Erzählung (max. 10 Sätze), die die Daten oben lebendig macht,
     ohne neue Fakten einzuführen. -->
