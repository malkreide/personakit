---
name: persona-kit
description: Erstellt, prüft, aktualisiert und exportiert evidenzbasierte Personas im personakit-Format (*.persona.md mit YAML-Frontmatter, JTBD-Block, Evidenz, Simulationsregeln). Verwenden, wenn der User (1) eine Persona aus Interviews, Support-Logs, Umfragen, Workshops oder Annahmen ableiten will – auch Factoids extrahieren, Teilnehmende auf Verhaltensvariablen verorten oder ein Persona-Skelett aus Factoids erzeugen –, (2) bestehende Personas anpassen, versionieren, reviewen oder in den Ruhestand versetzen will, (3) Personas als Markdown, JSON, YAML, Prompt-Block, Karte, Matrix oder HTML-Galerie exportieren oder in eine Notion-Datenbank publizieren will, (4) eine Persona als Voreinstellung für Content, Chat-Assistenten, User Journeys (journeykit) oder synthetische Gegenproben braucht, oder (5) Begriffe wie «Persona», «Archetyp», «Zielgruppe», «Jobs-to-be-Done», «Job Story», «Factoid», «Verhaltensvariable», «synthetischer Nutzer» im Kontext einer Lösung verwendet.
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
personakit render personas -f notion --target mcp  # Seiten für die Notion-Datenbank «Personas»
personakit list personas                            # Übersicht pro Set
personakit bump <datei> -p minor -m "…" [--status active --evidence-level qualitative --review-days 180]
personakit retire <datei> -m "…"
personakit factoids factoids/<studie> [--json]      # Verortung, dünne Variablen, Ausreisser
personakit skeleton factoids/<studie> -p p1,p3,p7 --id <id> -a "<Archetyp>" [-d personas/<set>]
```

Ohne installiertes Paket: `python -m personakit.cli …` mit `PYTHONPATH=src`.

## Ablauf: Persona aus Material ableiten

Arbeitsteilung: **Zählen macht das Werkzeug, Deuten macht die Skill.** `factoids` und `skeleton` sind deterministisch – sie verorten, rechnen Mediane und übernehmen Zitate. Welche Teilnehmenden eine Persona bilden, wie sie heisst, was sie will und wie sie spricht, entscheidet die Skill, und zwar nur mit Verweis auf Factoid-IDs. Format: `docs/FORMAT.md` → Factoids; Beispiel: `factoids/beispiel/`.

1. **Factoids extrahieren.** Pro Quelle eine Datei `factoids/<studie>/<source_id>.factoids.md`: Frontmatter (`source_id`, `type`, `date`, `n`, `consent_note`, optional `title`) und eine Tabelle `id | participant | observation | variable | value | quote`. Eine beobachtbare Aussage pro Zeile, wörtliche Aussagen mit `quote: ja`, nichts glätten, nichts deuten. Teilnehmende **nur als Codes** (`p1`, `p2` …), nie Namen; identifizierende Details (Beruf, Strasse, seltene Umstände) weglassen. `value` nur setzen, wenn das Factoid die Stufe trägt.
2. **Variablen festlegen.** 3–7 Skalen in `factoids/<studie>/variables.yml` mit Ankern für 1 und 5 – Dimensionen, auf denen sich die Teilnehmenden unterscheiden, nicht Demografie. Neue Variablen, die beim Extrahieren auftauchen, dort ergänzen.
3. **Prüfen und lesen:** `personakit factoids factoids/<studie>`. Alle ERROR beheben (F006 heisst: ein Name statt eines Codes – sofort ersetzen). Dann deuten:
   - **Verteilung** lesen: Teilnehmende, die auf mehreren Variablen gemeinsam liegen, sind ein Persona-Kandidat. Eine Persona entsteht aus einer Häufung im Verhalten, nicht aus ähnlicher Demografie.
   - **F010** (dünne Variable): nachkodieren, Material ergänzen oder die Variable streichen – nicht auf ihr clustern.
   - **F011** (Ausreisser): eigene Persona, wenn Jobs oder Ziele ebenfalls abweichen; sonst als Ausprägung in `simulation.variance` der nächstgelegenen Persona. Die Entscheidung mit Factoid-IDs begründen.
   - Dem User die vorgeschlagenen Häufungen mit Teilnehmer-Codes und den tragenden Factoid-IDs zeigen, bevor Dateien entstehen.
4. **Skelett erzeugen:** `personakit skeleton factoids/<studie> -p <codes> --id <id> -a "<Archetyp>" -d personas/<set>`. Der Archetyp ist die erste Deutung: verhaltensbasiert, aus den Factoids der Häufung. Hinweise auf stderr ernst nehmen – «Frankenstein-Gefahr» heisst, die Auswahl mischt zwei Personas. Das Skelett enthält Variablen (Median), Evidenz, Zitate, `evidence_level` und den Abschnitt `## Herleitung`; Werte und Zitate nicht nachträglich «verbessern».
5. **Deuten und belegen.** Im Skelett füllen: `context`, `behaviour.patterns`, `goals` (experience/end), `pains`, `jobs` als Job Stories mit Kräften, `anti_patterns`, `profile[]` nur mit `relevance`. Jede Aussage stützt sich auf Factoids der gewählten Teilnehmenden; die IDs gehören in `## Herleitung` als Zeilen wie `- Archetyp ← I02, I05`, `- J1 ← I09, B01`, `- pains[0] ← I03, I22`. Was kein Factoid trägt, gehört nach `assumptions` oder `unknowns`, nicht in die Persona.
6. **Evidenz und Lücken prüfen.** `evidence_level` aus dem Skelett nicht hochstufen: Bei `proto` (weniger als 5 Interviews/Beobachtungen) `assumptions` füllen. `unknowns` immer füllen; vom Skelett gesetzte Einträge (unbelegte Variablen) stehen lassen.
7. **Simulationsregeln schreiben.** `simulation.voice` aus den Zitaten ableiten, `must`, `must_not`, `variance`. `must_not` beschreibt, was ein LLM typischerweise falsch macht (zu kompetent, zu freundlich, Innensicht der Organisation, Fachbegriffe). `variance` aus der Spanne in `## Herleitung` und aus F011-Fällen: worin streuen reale Personen dieses Typs?
8. **Szenario schreiben** (`## Szenario` im Body): eine konkrete Situation mit Zeit, Ort, Gerät, Auslöser und dem Satz «Die Lösung ist gut, wenn …» – gebaut aus Factoids, nicht erfunden.
9. **Set zuordnen.** Jede Lösung hat ein Set `personas/<set-id>/set.yml`; die neue Persona dort mit ihrer Priorität für diese Lösung eintragen. Gilt sie für eine weitere Lösung, nicht kopieren, sondern im anderen Set über die `id` aufführen – mit der Priorität, die sie dort hat.
10. **Lint laufen lassen** und alle ERROR beheben; WARN begründet stehen lassen oder beheben. Dann `list` bzw. `matrix` prüfen: genau eine primäre Persona pro Set.

Ohne Material (nur Annahmen) entfallen Schritte 1–4: `personakit new` anlegen, `evidence_level: proto`, `assumptions` füllen, dann weiter bei 5. Zitate immer wörtlich übernehmen, nicht glätten. Werte auf Skalen nur setzen, wenn das Material sie trägt; sonst mittig lassen und in `unknowns` notieren.

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
| journeykit-Journey schreiben | `render -f json` | Persona-ID als Journey-`persona.id`; Jobs als Journey-Treiber; `relations.journeys` nachtragen, dann `lint personas --journeys <ordner>` |
| Massnahmen priorisieren | `render -f matrix` | Opportunity-Score pro Job; bei Konflikt entscheidet die primäre Persona |
| Notion-Datenbank «Personas» | `render -f notion --target mcp` | Ablauf «Nach Notion publizieren» unten |
| Wiki-Seite | `render -f md` oder `-f card` | Karte für Übersichten, md für Detailseiten |
| Team-Galerie | `render personas -f html -o personas.html` | Single-File, offline |

Wenn mehrere Personas als Voreinstellung gleichzeitig nötig sind, immer die primäre zuerst und die negative als Gegenprobe («Würde der Verwaltungs-Insider das durchwinken? Dann nochmals gegen die primäre Persona prüfen»).

## Ablauf: Nach Notion publizieren

Notion ist eine Lesekopie: Die `.persona.md` bleibt die Quelle, jede Seite wird beim nächsten Export überschrieben. Datenbank, Property-Typen und Exportformat: `docs/FORMAT.md` → Notion-Export. Geschrieben wird über die Notion-MCP-Tools; der Export selbst macht keine Netzwerkaufrufe.

1. **Prüfen und exportieren.** `personakit lint <pfade>` muss ohne ERROR durchlaufen, sonst nicht publizieren. Dann `personakit render <pfade> -f notion --target mcp -o notion-personas.json` – `<pfade>` ist ein Set-Ordner oder `personas`. Jede Persona ergibt genau einen Eintrag in `pages[]` mit `properties` und `content`.
2. **Datenschutz klären.** Zitate, Evidenz-Quellen und Notizen gehen mit nach Notion. Vor der ersten Publikation aus realem Material klären, ob die Einwilligung (`consent_note` der Factoid-Quellen) und die Vorgaben der Organisation das abdecken; sonst nicht publizieren.
3. **Datenbank finden.** Die Datenbank nennt der User; sonst `notion-search` nach «Personas» und den Treffer bestätigen lassen. Mit `notion-fetch` die Datenbank und danach ihre Datenquelle (`collection://…`) laden und die Properties mit der Tabelle in `docs/FORMAT.md` vergleichen. Fehlen Properties oder haben sie einen anderen Typ: dem User zeigen und erst nach Zustimmung ändern. Gibt es keine Datenbank: nach Zustimmung und mit der Elternseite, die der User nennt, `notion-create-database` mit `database.schema` aus dem Export aufrufen.
   **Optionen abgleichen.** Die MCP-Tools lehnen eine Seite ab, wenn ein Wert von `Set`, `Tags` oder einem Select in der Datenquelle noch keine Option ist. Deshalb `database.options` aus dem Export mit den Optionen der Datenquelle vergleichen und fehlende mit `notion-update-data-source` ergänzen, z. B. `ALTER COLUMN "Tags" SET MULTI_SELECT('bestehend':default, 'neu':default)`. `SET` ersetzt die ganze Optionsliste: alle bestehenden Optionen mit ihren Farben mitgeben, nie nur die neuen.
4. **Bestehende Seiten suchen (Schlüssel `ID`).** Für jede Persona `notion-query-data-sources` im Modus `rows` auf die Datenquelle, Filter `{"type": "property", "property": "ID", "propertyType": "text", "operator": "string_is", "value": {"type": "exact", "value": "<id>"}}`. Die `id` steht in `properties["userDefined:ID"]`.
   - kein Treffer → neu anlegen
   - ein Treffer → aktualisieren
   - mehrere Treffer → nichts schreiben, die Seiten-URLs dem User zeigen und fragen, welche bleibt. Nie raten.
5. **Plan bestätigen lassen.** Dem User die Liste zeigen: anlegen (ID, Name), aktualisieren (ID, Seiten-URL), übersprungen (mit Grund). Erst nach Zustimmung schreiben.
6. **Schreiben.**
   - Neu: `notion-create-pages` mit `parent: {"data_source_id": "<collection-id>"}` und den betroffenen Einträgen aus `pages[]` unverändert (`properties`, `content`; höchstens 100 pro Aufruf).
   - Bestehend: `notion-update-page` mit `command: "update_properties"` und `properties` aus dem Export, danach `command: "replace_content"` mit `new_str` = `content`. Meldet das Tool, dass Unterseiten oder Datenbanken gelöscht würden, die Liste zeigen und nachfragen; `allow_deleting_content` nie ohne Zustimmung setzen.
   - `properties` und `content` nicht von Hand umformulieren, kürzen oder «verbessern»: Das Escaping im Export ist Absicht.
7. **Abgleich melden.** Angelegte und aktualisierte Seiten mit URL nennen. Seiten in der Datenbank, deren `ID` im Export fehlt (Persona umbenannt oder entfernt), nur melden – nicht löschen oder archivieren, ausser der User verlangt es.

Für Skripte ohne MCP gibt `--target api` (Default) dieselben Seiten als Bodies für `POST /v1/pages` aus; Details in `docs/FORMAT.md`.

## Grenzen, die der Skill einhält

- Keine Persona ohne `evidence_level`; keine `qualitative`-Persona ohne Evidenz-Einträge. Wenn der User nur Annahmen liefert, wird `proto` gesetzt und gesagt, was zur Validierung fehlt (5–8 Interviews, Support-Logs, Kurzumfrage).
- Keine demografischen Fakten ohne `relevance`; keine Fotos; Namen nur, wenn der User sie will.
- Synthetische Antworten (simulate-Modus) werden als solche gekennzeichnet und nicht als Befund in `evidence` eingetragen – ausser als `type: assumption` mit entsprechender Note.
- Beispiel-Personas im Repo sind synthetisch; sie beschreiben keine realen Erhebungen.
- Factoid-Dateien enthalten nur Teilnehmer-Codes, nie Namen oder Kontaktdaten; `consent_note` ist gefüllt. Reale Studienordner bleiben ausserhalb von Git (`.gitignore`: `factoids/*` ausser `factoids/beispiel/`); Rohmaterial (Transkripte, Audio) wird nie ins Repo kopiert.
- Keine Aussage in einer aus Factoids abgeleiteten Persona ohne Factoid-ID in `## Herleitung` – sonst ist sie eine Annahme und gehört nach `assumptions`.

## Referenzen

- `references/elicitation.md` – Interviewleitfaden und Workshop-Ablauf für Proto-Personas
- `factoids/beispiel/` – synthetische Studie: zwei Quellen, `variables.yml`, eine Häufung, ein Ausreisser
- `docs/FORMAT.md` – Felder, Enums, Lint-Codes
- `docs/METHOD.md` – Befunde und Designentscheide (Cooper, NN/g, JTBD, synthetische Nutzer)
