# Fahrplan und Prompts für Claude Code

Jeder Prompt ist für eine frische Session geschrieben: Claude Code liest `CLAUDE.md` automatisch, der Prompt liefert Ziel, Grenzen und Abnahmekriterien. Reihenfolge ist eine Empfehlung; P1–P3 sind Grundlage für den Rest, P4–P8 sind weitgehend unabhängig voneinander.

| # | Thema | Ergebnis |
|---|---|---|
| P0 | Einstieg | Verständnis + Schwachstellenliste, keine Änderung |
| P1 | Nachpflege Publikation | Topics, Secret Scanning, Skill-Fix, Release v0.1.0 |
| P2 | Robustheit | CRLF/BOM, `new`-UX, `--json`-Lint, Tests |
| P3 | Sets pro Lösung | `personas/<set>/set.yml`, Set-Lint, gruppierte Exporte |
| P4 | Factoid-Pipeline | Material → Factoids → Skelett, Skill-Erweiterung |
| P5 | MCP-Server | `personakit-mcp`: Personas als Voreinstellung in jeder Session |
| P6 | journeykit-Kopplung | Cross-Lint Persona ↔ Journey, gemeinsame Evidenz-IDs |
| P7 | Notion-Export | `render -f notion`, DB «Personas» |
| P8 | Collapse-Probe | Prüft, ob simulierte Personas unterscheidbar bleiben |
| A | Anwendung | Vorlage für echte Personas zu einer Lösung |

---

## P0 – Einstieg

```
Lies CLAUDE.md, README.md, docs/METHOD.md und docs/FORMAT.md. Installiere das Paket und das gepinnte ruff, führe alle Gates aus CLAUDE.md aus und bestätige, dass sie grün sind. Rendere die Beispiele einmal in jedem Format (md, card, json, yaml, prompt in beiden Modi, matrix, html, bundle) nach einem temporären Ordner und sieh dir die Ausgaben an.

Fasse mir danach in höchstens zehn Zeilen zusammen, wie Format, Linter und Renderer zusammenhängen. Nenne drei Stellen, die du für schwach oder brüchig hältst (Code, Methodik oder Doku), je mit einem Satz Begründung. Ändere in dieser Session nichts.
```

## P1 – Nachpflege Publikation

```
Erledige die offenen Punkte aus .github/repo-meta.yml mit der github-repo-Skill: Topics setzen, Secret Scanning und Push Protection aktivieren (lokal mit gh, Backend A), danach die Einträge unter «offen» entfernen und confirmed auf true setzen, nachdem du mir Titel, Description und Topics einmal zur Bestätigung gezeigt hast.

Dann Release v0.1.0 nach Schritt 12 der Skill: CHANGELOG-Abschnitt prüfen, Tag auf dem aktuellen main-Commit, Gegenprobe des Tag-Ziels, GitHub-Release nur mit dem Abschnitt dieser Version, Badges in beiden READMEs prüfen. Kein PyPI.

Zusätzlich: scripts/validate_repo.py enthält eine lokale Anpassung an Regel A1 (mcp-name-Marker nur bei MCP-Servern verlangen). Übertrage dieselbe Korrektur in die Skill-Quelle unter ~/github-repo-skill, mit Test in scripts/test_c1.py oder einem neuen Test, und zeige mir den Diff, bevor du dort committest.
```

## P2 – Robustheit und Windows

```
Härte personakit für den Alltag unter Windows und in CI. Schreibe zuerst Tests, die heute fehlschlagen, dann die Fixes:

1. Persona-Dateien mit CRLF-Zeilenenden und mit UTF-8-BOM werden geladen, der Round-Trip erhält die ursprünglichen Zeilenenden.
2. `personakit new` ohne --archetype erzeugt heute eine Datei, die das Schema verletzt (minLength). Entweder --archetype verpflichtend machen oder interaktiv nachfragen; die Fehlermeldung muss sagen, was fehlt.
3. `personakit lint --json` gibt die Findings als JSON (Liste mit level, code, persona, message) für CI und andere Werkzeuge aus; Exit-Codes bleiben wie bisher.
4. Pfade mit Umlauten und Leerzeichen funktionieren in allen Befehlen.
5. `render` mit mehreren Dateien und --output auf eine bestehende Datei statt einen Ordner bricht mit klarer Meldung ab.

Halte dich an die Konventionen in CLAUDE.md, führe alle Gates aus und trage die Änderungen in CHANGELOG.md unter [Unreleased] ein.
```

## P3 – Sets pro Lösung

```
Heute gilt die Set-Regel «genau eine primäre Persona» für den ganzen Ordner personas/. Ich will Personas für mehrere Lösungen im selben Repo pflegen, und dieselbe Persona darf in mehreren Lösungen eine Rolle spielen.

Entwirf und implementiere «Sets»: Ein Set ist ein Unterordner personas/<set-id>/ mit einer set.yml (id, title, solution, scope, status, personas: Liste von {id, priority}). Die Priorität einer Persona gilt pro Set, nicht global – entsprechend wird priority in der Persona-Datei zum Default, den set.yml überschreiben kann. Die X-Regeln des Linters (eine primäre Persona, maximal fünf aktive, Referenzen) laufen pro Set; Personas ohne Set werden weiterhin als loses Set behandelt. list, matrix und html gruppieren nach Set; render -f bundle enthält die Set-Struktur.

Schema-Änderung an der Persona nur, wenn unvermeidbar; wenn ja, Format-Version 1.1 und Migrationshinweis in FORMAT.md. Verschiebe die vier Beispiele in ein Set «elternkommunikation-schuleintritt» und zeige mir zuerst den Entwurf von set.yml und der Lint-Logik als kurze Notiz, bevor du Code schreibst.
```

## P4 – Factoid-Pipeline

```
Die Skill skills/persona-kit beschreibt den Weg Material → Factoids → Verhaltensvariablen → Persona nur in Prosa. Baue den deterministischen Teil als Werkzeug, der interpretierende Teil bleibt beim Modell:

1. Ein Factoid-Format: factoids/<quelle>.factoids.md mit Frontmatter (source-id, type, date, n, consent-note) und einer Tabelle pro Zeile: id, participant, observation (wörtlich oder beobachtet), variable (optional), value 1–5 (optional), quote (bool).
2. `personakit factoids <ordner>`: validiert die Dateien, zeigt pro Teilnehmer die Verortung auf den Variablen als Matrix, meldet Variablen mit zu wenig Belegung und Teilnehmer, die auf mindestens zwei Variablen um ≥ 2 Punkte von allen anderen abweichen (Kandidaten für eine eigene Persona oder für variance).
3. `personakit skeleton <ordner> --participants p1,p3,p7 --id <persona-id>`: erzeugt aus den gewählten Teilnehmern eine Persona-Datei, in der behaviour.variables mit Median-Werten, evidence mit den Quellen und quotes mit den als quote markierten Factoids vorbefüllt sind; alles andere bleibt leer, evidence_level wird nach Anzahl Interviews gesetzt.
4. Erweitere SKILL.md so, dass die Skill diese Befehle nutzt und die Interpretation (Archetyp, Ziele, Jobs, Simulationsregeln) selbst leistet, mit Verweis auf Factoid-IDs.

Datenschutz: Factoid-Dateien enthalten nur Teilnehmer-Codes, nie Namen. Ergänze .gitignore um ein Muster für reale Factoid-Ordner und lege ein synthetisches Beispiel unter factoids/beispiel/ an. Tests und FORMAT.md nachführen.
```

## P5 – MCP-Server

```
Ich will Personas in jeder Claude-Session als Voreinstellung laden können, ohne Dateien zu kopieren. Entwirf dafür einen MCP-Server «personakit-mcp» als eigenes Repo (Namenskonvention meiner github-repo-Skill), zuerst nur als Design-Notiz, dann als Implementierung nach mcp-builder und mcp-data-fidelity.

Tools: list_sets, list_personas(set?, status?, priority?), get_persona(id, format: md|card|json|prompt, mode?), persona_prompt(id, mode) als Convenience, lint(id?) read-only. Der Server liest ein konfiguriertes Personas-Verzeichnis (Umgebungsvariable), schreibt nie, und liefert bei leerem Ergebnis eine explizite Meldung statt nichts. Tool-Descriptions müssen sagen, was proto bedeutet und dass simulate-Ausgaben Hypothesen sind. Nutze personakit als Bibliothek (Abhängigkeit), dupliziere keine Render-Logik.

Zielstand ist die MCP-Spec, die meine github-repo-Skill unter references/mcp-spec.md vorgibt; prüfe das vor dem ersten Commit. Zeige mir das Design, bevor du das Repo anlegst.
```

## P6 – journeykit-Kopplung

```
Lies das Schema und die Beispiel-Journey in ../journeykit (oder dem Pfad, den ich dir nenne). Entwirf die kleinste sinnvolle Kopplung zwischen journeykit und personakit, ohne eines der beiden Formate zu verbiegen:

1. Welche Journey-Felder referenzieren heute Akteure, und wie würde eine Persona-ID dort stehen?
2. Cross-Lint: `personakit lint --journeys <pfad>` prüft, dass relations.journeys auf existierende Journey-IDs zeigt und dass Journeys, die eine Persona-ID nennen, auf existierende Personas zeigen. Welche Seite soll die Regel besitzen?
3. Evidenz: Beide Werkzeuge haben Evidenz-Konzepte. Lohnt sich eine gemeinsame Evidenz-Datei (Factoids aus P4), auf die beide verweisen, oder reicht eine Namenskonvention der IDs?

Liefere zuerst eine Entscheidungsnotiz mit Empfehlung (max. eine Seite). Implementiere danach nur den Cross-Lint, mit Test gegen die Beispiele beider Repos.
```

## P7 – Notion-Export

```
Baue `personakit render -f notion`: Ausgabe ist JSON, das direkt an die Notion-API passt – pro Persona ein Objekt mit properties für eine Datenbank «Personas» (Name, ID, Archetyp, Set, Priorität, Status, Evidenz, Version, Review bis, Tags) und children als Notion-Blöcke (Überschriften, Aufzählungen, Zitate, Tabelle für Verhaltensvariablen, Toggle für Evidenz und Annahmen). Keine Netzwerkaufrufe im Renderer.

Dokumentiere in docs/FORMAT.md, wie die Datenbank angelegt sein muss (Property-Typen), und ergänze in skills/persona-kit/SKILL.md einen Schritt «nach Notion publizieren», der die Ausgabe über die Notion-MCP-Tools in die Datenbank schreibt und bei bestehender Seite (gleiche ID) aktualisiert statt dupliziert. Tests für die Block-Struktur, inklusive Escaping von Sonderzeichen.
```

## P8 – Collapse-Probe für synthetische Nutzer

```
docs/METHOD.md Abschnitt 1.6 beschreibt Persona Collapse. Ich will messen, ob meine Personas im simulate-Modus unterscheidbar bleiben. Baue `personakit probe` in zwei Schritten:

1. `probe build <set oder dateien> -o probe.json`: erzeugt aus jeder Persona 6–10 Prüffragen aus Szenario, Jobs und Schmerzpunkten (deterministisch, ohne Modell) plus die simulate-Prompts, als Plan, den ich gegen ein Modell meiner Wahl laufen lasse.
2. `probe evaluate probe.json answers.json`: answers enthält pro Persona und Frage die Modellantwort. Berechne ohne externe Modelle (stdlib, TF-IDF-Kosinus oder ähnlich) die paarweise Ähnlichkeit der Antworten zwischen Personas auf dieselbe Frage, melde Paare mit hoher Ähnlichkeit als Collapse-Verdacht, prüfe Verstösse gegen simulation.must_not über konfigurierbare Schlüsselwörter und prüfe, ob unknowns als offen behandelt wurden. Ausgabe als Markdown-Bericht mit Ampel pro Persona-Paar.

Entwirf zuerst das answers.json-Format und die Metriken als Notiz, dann implementieren. Beziehe die Grenzen der Methode in den Bericht ein (lexikalische Ähnlichkeit ist ein grober Proxy). Tests mit synthetischen Antworten, die einen Collapse enthalten.
```

## A – Anwendung: Personas für eine echte Lösung

```
Nutze die Skill persona-kit. Lösung: <Name und Zweck der Lösung, z. B. Chat-Assistent zur Elternkommunikation beim Schuleintritt>. Material: <Pfad zu Interview-Notizen, Support-Logs, Umfrage-Export – nur anonymisiert, Teilnehmer-Codes statt Namen>.

Leite daraus ein Set mit höchstens vier Personas ab, davon genau eine primäre und eine negative. Arbeite nach dem Ablauf in SKILL.md: Factoids mit Quellen extrahieren, Verhaltensvariablen bilden, Teilnehmer verorten, erst dann Personas schreiben. Setze evidence_level ehrlich; was nicht aus dem Material stammt, kommt in assumptions oder unknowns. Zitate wörtlich. Simulationsregeln mit konkretem must_not und variance.

Lint muss ohne Fehler durchlaufen. Zeige mir vor dem Schreiben der Dateien die Verhaltensvariablen mit Ankern und die Verortung der Teilnehmer als Matrix, damit ich die Gruppierung bestätigen kann.
```
