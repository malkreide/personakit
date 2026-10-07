---
name: persona-kit
description: Erstellt, prüft, aktualisiert und exportiert evidenzbasierte Personas im personakit-Format (*.persona.md mit YAML-Frontmatter, JTBD-Block, Evidenz, Simulationsregeln). Verwenden, wenn der User (1) eine Persona aus Interviews, Support-Logs, Umfragen, Workshops oder Annahmen ableiten will, (2) bestehende Personas anpassen, versionieren, reviewen oder in den Ruhestand versetzen will, (3) Personas als Markdown, JSON, YAML, Prompt-Block, Karte, Matrix oder HTML-Galerie exportieren will, (4) eine Persona als Voreinstellung für Content, Chat-Assistenten, User Journeys (journeykit) oder synthetische Gegenproben braucht, oder (5) Begriffe wie «Persona», «Archetyp», «Zielgruppe», «Jobs-to-be-Done», «Job Story», «synthetischer Nutzer» im Kontext einer Lösung verwendet.
---

# persona-kit

Personas sind hier **verhaltensbasierte Ziel- und Kontextmodelle mit sichtbarer Evidenz**, keine Steckbriefe. Jede Zeile in einer Persona muss eine Gestaltungsentscheidung beeinflussen können; sonst wird sie gestrichen. Hintergrund: `docs/METHOD.md`, Feldreferenz: `docs/FORMAT.md`.

## Werkzeug

```bash
pip install -e .                      # einmalig im Repo
personakit new <id> -a "<Archetyp>"   # Vorlage mit Kommentaren anlegen
personakit lint personas              # Schema + Methodik-Regeln (Exit 1 bei Fehlern)
personakit render <datei> -f md|card|json|yaml|prompt [-m simulate|audience]
personakit render personas -f matrix|html|bundle   # nach Set gruppiert
personakit list personas                            # Übersicht pro Set
personakit bump <datei> -p minor -m "…" [--status active --evidence-level qualitative --review-days 180]
personakit retire <datei> -m "…"
```

Ohne installiertes Paket: `python -m personakit.cli …` mit `PYTHONPATH=src`.

## Ablauf: Persona aus Material ableiten

1. **Material sichten, Factoids extrahieren.** Aus Interviews, Support-Logs, Umfragen, Analytics oder Workshop-Notizen einzelne beobachtbare Aussagen ziehen («bricht Formular ab, wenn Feld unklar»). Jedes Factoid bekommt eine Quelle. Keine Interpretation in diesem Schritt.
2. **Verhaltensvariablen bilden.** 3–7 Skalen, auf denen sich die Befragten unterscheiden (z. B. digitale Routine, Fehlervermeidung vs. Ausprobieren, Vertrautheit mit dem System). Befragte auf den Skalen verorten. Wo sich Häufungen bilden, entsteht eine Persona – nicht wo Demografie sich ähnelt.
3. **Skelett füllen.** `personakit new` ausführen, dann Frontmatter füllen: `archetype` verhaltensbasiert, `context`, `behaviour.variables` mit Ankern, `goals` (experience/end), `pains`, `jobs` als Job Stories mit Kräften, `quotes` mit Evidenz-ID, `anti_patterns`. Jedes `profile[].fact` braucht `relevance`.
4. **Evidenz und Lücken dokumentieren.** `evidence[]` mit Typ, Datum, n. `evidence_level` ehrlich setzen: Ohne Primärforschung ist es `proto`, dann sind `assumptions` Pflicht. `unknowns` immer füllen.
5. **Simulationsregeln schreiben.** `simulation.voice`, `must`, `must_not`, `variance`. `must_not` beschreibt, was ein LLM typischerweise falsch macht (zu kompetent, zu freundlich, Innensicht der Organisation, Fachbegriffe). `variance` benennt, worin reale Personen dieses Typs streuen.
6. **Szenario schreiben** (`## Szenario` im Body): eine konkrete Situation mit Zeit, Ort, Gerät, Auslöser und dem Satz «Die Lösung ist gut, wenn …».
7. **Set zuordnen.** Jede Lösung hat ein Set `personas/<set-id>/set.yml`; die neue Persona dort mit ihrer Priorität für diese Lösung eintragen. Gilt sie für eine weitere Lösung, nicht kopieren, sondern im anderen Set über die `id` aufführen – mit der Priorität, die sie dort hat.
8. **Lint laufen lassen** und alle ERROR beheben; WARN begründet stehen lassen oder beheben. Dann `list` bzw. `matrix` prüfen: genau eine primäre Persona pro Set.

Beim Ableiten aus Material: Zitate wörtlich übernehmen, nicht glätten. Werte auf Skalen nur setzen, wenn das Material sie trägt; sonst mittig lassen und in `unknowns` notieren.

## Ablauf: Persona anpassen

- Inhalt in der `.persona.md` ändern, danach `personakit bump` mit Changelog-Note. `major`, wenn Verhaltensmuster oder Jobs sich ändern; `minor` bei Ergänzungen; `patch` bei Korrekturen.
- Wechsel von `proto` zu `qualitative`: Evidenz-Einträge mit n nachtragen, Variablen und Zitate auf Evidenz-IDs verweisen, dann `bump --evidence-level qualitative --status active`.
- Review (vor `review_by`): Was hat sich bestätigt, was nicht? Nicht Bestätigtes nach `assumptions` oder `unknowns` verschieben, nicht löschen.
- Nie zwei Personas zusammenlegen, deren Verhaltensvariablen sich widersprechen (Frankenstein-Persona). Lieber eine in den Ruhestand (`retire`) und eine neue anlegen.

## Ablauf: Persona als Input einsetzen

| Zweck | Befehl | Regel |
|---|---|---|
| Content für ein Zielpublikum erzeugen | `render -f prompt -m audience` | Prompt-Block als System-Kontext vorschalten; Erlebnisziele sind Veto-Kriterien |
| Entwurf gegen eine Persona testen, Interview üben | `render -f prompt -m simulate` | Ergebnis ist Hypothese, nie Nutzerforschung; Persona-ID und Version im Output nennen |
| journeykit-Journey schreiben | `render -f json` | Persona-ID als Akteur; Jobs als Journey-Treiber; `relations.journeys` nachtragen |
| Massnahmen priorisieren | `render -f matrix` | Opportunity-Score pro Job; bei Konflikt entscheidet die primäre Persona |
| Notion/Wiki-Seite | `render -f md` oder `-f card` | Karte für Übersichten, md für Detailseiten |
| Team-Galerie | `render personas -f html -o personas.html` | Single-File, offline |

Wenn mehrere Personas als Voreinstellung gleichzeitig nötig sind, immer die primäre zuerst und die negative als Gegenprobe («Würde der Verwaltungs-Insider das durchwinken? Dann nochmals gegen die primäre Persona prüfen»).

## Grenzen, die der Skill einhält

- Keine Persona ohne `evidence_level`; keine `qualitative`-Persona ohne Evidenz-Einträge. Wenn der User nur Annahmen liefert, wird `proto` gesetzt und gesagt, was zur Validierung fehlt (5–8 Interviews, Support-Logs, Kurzumfrage).
- Keine demografischen Fakten ohne `relevance`; keine Fotos; Namen nur, wenn der User sie will.
- Synthetische Antworten (simulate-Modus) werden als solche gekennzeichnet und nicht als Befund in `evidence` eingetragen – ausser als `type: assumption` mit entsprechender Note.
- Beispiel-Personas im Repo sind synthetisch; sie beschreiben keine realen Erhebungen.

## Referenzen

- `references/elicitation.md` – Interviewleitfaden und Workshop-Ablauf für Proto-Personas
- `docs/FORMAT.md` – Felder, Enums, Lint-Codes
- `docs/METHOD.md` – Befunde und Designentscheide (Cooper, NN/g, JTBD, synthetische Nutzer)
