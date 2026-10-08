# Entscheidungsnotiz: Kopplung personakit ↔ journeykit (P6)

Stand 2026-10-08 · Grundlage: journeykit `main` @ `5166e5e` (Schema `1.0`, Beispiele `kindergarteneintritt`, `baubewilligung`)

**Empfehlung in einem Satz:** Die Werkzeuge koppeln sich über IDs, nicht über geteilte Inhalte. personakit prüft die Verweise (`lint --journeys`), keines der beiden Schemas ändert sich, und für die Evidenz genügt vorerst eine Namenskonvention.

## 1. Wo eine Journey Akteure nennt

| Journey-Feld | Bedeutung | Persona-ID? |
|---|---|---|
| `persona.id` (Pflicht, genau eine pro Journey) | Persona der Journey | **ja: hier steht die personakit-`id`** |
| `evidence[].persona_hint` | Zuordnungshinweis beim Extrahieren (`zugezogen`, `fremdsprachig`) | nein, bleibt Arbeitshilfe |
| `step.performed_by.role` | helfende oder handelnde Dritte (ADR-0005), bewusst ohne Persona | nein |
| `step.counterpart`, `meta.owner.role`, `sources[].participants` | Verwaltungsrollen, Erhobene | nein |

Konvention: Journey-`persona.id` = personakit-`id`; Gegenrichtung `relations.journeys` = Journey-`meta.id`. Der übrige `persona`-Block der Journey (name, role, goals, frustrations) bleibt eine Momentaufnahme, damit `journey.json` allein teilbar bleibt und der Viewer offline läuft; Quelle der Wahrheit ist die Persona-Datei (`render -f json`). Mehrere Dateien mit derselben `meta.id` (Hypothese, Synthese) gelten als eine Journey. Ein neues Feld `persona.ref` wäre überflüssig, weil `persona.id` die Bedeutung schon trägt, und kostete in journeykit ein ADR (`additionalProperties: false`). Die ID-Muster passen: personakit `^[a-z0-9]+(-[a-z0-9]+)*$` ist in journeykit gültig, solange die ID mit einem Buchstaben beginnt und höchstens 64 Zeichen hat.

**Befund:** `eltern-neu-in-zuerich` verweist auf `kindergarteneintritt-eltern`, die Journey führt aber `persona.id: eltern-zugezogen`. Die Kopplung besteht heute nur einseitig. Die Korrektur gehört nach journeykit (`persona.id` umbenennen, `persona_hint` bleibt).

## 2. Wer den Cross-Lint besitzt: personakit

- Nur personakit hat ein Feld, das ausdrücklich auf das andere Werkzeug zeigt (`relations.journeys`). journeykit kennt personakit nicht und soll es nicht kennen müssen (eine Laufzeitabhängigkeit, neue nur mit ADR).
- personakit liest von einer Journey nur `meta.id` und `persona.id`: kein Import von journeykit, keine Validierung der Journey. Gültigkeit prüft `journeykit lint`.
- personakit-mcp und CI erhalten die Regel über `personakit.api.lint_workspace(paths, journeys=…)` ohne eigenen Code.
- Wer `--journeys` übergibt, erklärt diese Journeys zum Persona-Bestand gehörig. Deshalb gilt dort jede `persona.id` als Verweis.

| Code | Stufe | Regel |
|---|---|---|
| K000 | ERROR | Journey-Datei nicht lesbar, oder `meta.id` bzw. `persona.id` fehlt |
| K001 | WARN | `relations.journeys` nennt eine Journey, die unter `--journeys` nicht vorkommt |
| K002 | WARN | Journey nennt eine Persona, die es nicht gibt |
| K003 | WARN | Persona verweist auf eine Journey, die eine andere Persona führt |
| K004 | INFO | Journey führt die Persona, `relations.journeys` fehlt |

Die Stufen folgen X005: Ein toter Verweis macht die Persona nicht unbrauchbar. Ohne `--journeys` läuft keine K-Regel, und `personakit lint` bleibt unverändert.

## 3. Evidenz: Namenskonvention statt gemeinsamer Datei

Journey-Atome und Factoids sind beinahe dasselbe (kleinste belegte Aussage mit Quelle und Fundstelle), aber unterschiedlich codiert: Atome nach Phase, Kanal, Emotion und Signal, Factoids nach Verhaltensvariable und Wert. Eine gemeinsame Datei würde `journey.json` die Eigenständigkeit nehmen (geteilte Datei, Offline-Viewer). Weil reale Factoid-Ordner per `.gitignore` ausgeschlossen sind, zeigte eine geteilte Journey ausserdem auf etwas, das die Empfängerin nie erhält. Und zwei Schemas müssten sich auf eine Codierung einigen, die heute niemand braucht.

**Konvention:** Der Schlüssel ist (Erhebung, Teilnehmer-Code). Eine Erhebungsserie trägt in beiden Werkzeugen denselben Slug (Factoid-`source_id` = Journey-`sources[].id` bei Sammelquellen). Teilnehmer-Codes sind identisch (Factoid-`participant` = Code in Journey-Quelle und Atom-ID, z. B. `e1` ↔ `int-e1`, `e1-03`). Persona-`evidence[].ref` und Journey-`sources[].location` zeigen auf dieselbe Ablage. So lässt sich eine Aussage in beiden Werkzeugen bis zur Quelle zurückverfolgen, ohne dass eine Datei geteilt wird. **Erneut prüfen**, sobald eine reale Studie für Persona und Journey codiert wurde. Dann wäre ein Generator (Factoids → Atom-Entwürfe) besser als eine geteilte Datei, und erst danach lohnt sich ein Evidenz-Cross-Lint.

**Offen:** journeykit-Beispiel angleichen, `--journeys` im MCP-Server, Statusabgleich (Journey `validated` auf Persona `proto`).
