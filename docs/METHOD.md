# Methodik: Warum personakit so gebaut ist

Dieses Dokument fasst die Analyse zu Personas und Jobs-to-be-Done (JTBD) zusammen und leitet daraus die Entscheide für das Format, die Lint-Regeln und den Prompt-Export ab. Jede Designentscheidung ist auf einen Befund zurückführbar.

## 1. Befunde

### 1.1 Personas sind Ziel- und Verhaltensmodelle, keine Steckbriefe

Cooper hat Personas 1999 als Instrument des Goal-Directed Design eingeführt: Sie repräsentieren nicht Nutzer, sondern **Nutzerziele**, und sie beenden den «elastischen Nutzer», der sich jeder Designentscheidung nachträglich anpasst. Cooper unterscheidet Erlebnisziele (wie man sich fühlen will – nie verletzen), Endziele (was man erreichen will) und Lebensziele. Verhaltensvariablen schneiden quer durch demografische Schichten: Ob jemand 25 oder 55 ist, sagt weniger über die Interaktion als ob er Gelegenheits- oder Power-User ist.

Die meiste Kritik an Personas – auch die aus dem JTBD-Lager – trifft **Marketing-Personas**, die Demografie an die Stelle von Verhalten setzen. NN/g und Praktiker wie Gothelf oder Elezea argumentieren übereinstimmend: Design-Personas, die auf Verhalten, Zielen und Kontext beruhen, sind nicht das Ziel dieser Kritik.

→ **Entscheid:** Das Format stellt `behaviour.variables` (Skalen 1–5 mit Ankern), `goals` (experience/end/life) und `context` ins Zentrum. `archetype` ist Pflicht und muss verhaltensbasiert sein; `name` ist optional. Demografische Angaben gibt es nur als `profile[].fact` **mit** `relevance` – Tschechows Gewehr als Lint-Regel (C001).

### 1.2 JTBD und Personas beantworten verschiedene Fragen

JTBD (Christensen, Ulwick, Moesta) erklärt, **warum** jemand eine Lösung «einstellt»: Situation, gewünschter Fortschritt, Wechselkräfte (Push, Pull, Angst, Gewohnheit). Es ist stark für Strategie, Innovationslücken und Priorisierung (ODI-Opportunity-Score), aber es liefert kein kognitives Profil für Interface-Entscheide und keine Empathie im Team. Personas liefern **wer** und **wie**; JTBD liefert **was** und **warum**. Der Milkshake-Fall zeigt beides: dieselbe Person, zwei Jobs – nur die Situation unterscheidet sie.

→ **Entscheid:** Jede Persona trägt einen `jobs[]`-Block mit Job Stories («Wenn [Situation], möchte ich [Motivation], damit [Ergebnis]»), den vier Kräften, ODI-Ergebnisaussagen sowie Wichtigkeit/Zufriedenheit. `render matrix` berechnet daraus den Opportunity-Score. Die Job Story ist bewusst situationsbezogen formuliert, nicht rollenbezogen – das verhindert, dass der JTBD-Block zur verkappten User Story wird.

### 1.3 Evidenzniveau muss sichtbar sein

NN/g unterscheidet Proto-Personas (Annahmen, 2–4 h Workshop), qualitative Personas (5–30 Interviews bis zur Sättigung) und statistische Personas (Mixed Methods, Clusteranalyse, n > 100). Personas scheitern vor allem, wenn ihre Datenbasis nicht vertrauenswürdig oder nicht sichtbar ist («Story Time») oder wenn sie aus unvereinbaren Quellen zusammengestückelt werden («Frankenstein-Persona»).

→ **Entscheid:** `evidence_level` ist Pflicht. `evidence[]` listet Quellen mit Typ, Datum und n; Zitate und Variablen verweisen auf Evidenz-IDs. Proto-Personas **müssen** `assumptions` offenlegen (E001); qualitative/statistische Personas **müssen** Evidenz jenseits von Annahmen haben (E003). `unknowns` ist Pflicht-nah (E008): Eine Persona ohne offene Fragen ist verdächtig.

### 1.4 Personas haben eine Halbwertszeit und brauchen einen Lebenszyklus

Pruitt/Adlin beschreiben den Persona Lifecycle von der «Familienplanung» bis zum «Ruhestand». Die häufigsten Antipatterns sind Wandkunst (nie wieder referenziert), fehlendes Buy-in und Veralterung.

→ **Entscheid:** `status` (draft/active/retired), `version` (SemVer), `review_by`, `changelog`, `owner`. `bump` und `retire` pflegen das maschinell; Lint warnt bei überfälligem Review (L002). Das Dateiformat ist Git-freundlich (keine Zeilenumbrüche in Strings, keine Anker), damit Änderungen reviewbar sind und die Persona dort lebt, wo gearbeitet wird – nicht als Poster.

### 1.5 Fokus: eine primäre Persona, 3–5 insgesamt, negative Personas explizit

Cooper: Ein Produkt, das für alle funktionieren will, funktioniert für niemanden. Genau eine primäre Persona muss zwingend zufrieden sein; sekundäre dürfen nicht frustriert werden. Negative Personas sparen Ressourcen, indem sie sagen, für wen nicht gebaut wird – und sie schützen vor selbstreferenziellem Design.

Die Priorität ist keine Eigenschaft der Person, sondern ihrer Beziehung zu einer Lösung: Dieselbe Lehrperson ist für KI-Leitplanken primär, für die Elternkommunikation höchstens ergänzend. Wer die Priorität global festschreibt, muss für jede weitere Lösung eine Kopie der Persona anlegen – und Kopien laufen auseinander.

→ **Entscheid:** `priority` (primary/secondary/supplemental/negative), `scope` (wofür die Persona gilt und wofür nicht). Ein **Set** (`personas/<set-id>/set.yml`) fasst die Personas einer Lösung zusammen und vergibt die Priorität pro Lösung; `priority` in der Persona-Datei ist der Default. Set-Lint prüft pro Set genau eine primäre Persona (X002/X003) und warnt ab sechs aktiven (X004). IDs und Relationen werden repo-weit geprüft (X001/X005), weil sie zur Persona gehören, nicht zur Lösung. Die Beispiel-Persona `verwaltungs-insider` zeigt die negative Persona als Gegenprobe – in zwei Sets, ohne Kopie.

### 1.6 Synthetische Nutzer: nützlich, aber systematisch verzerrt

Die HCI-Forschung 2025/26 ist eindeutig: LLM-basierte Personas leiden unter **Persona Collapse** – viele verschieden spezifizierte Personas konvergieren auf dieselben Verhaltenspunkte, Varianz kollabiert, Antworten sind zu positiv und zu rational, Trainingsdaten sind WEIRD-verzerrt. Grounding mit realen Daten reduziert den Fehler stark, beseitigt ihn aber nicht (Fidelity Gap). «Thinking»-Modi helfen nicht. Dennoch ist der Einsatz als schnelle Gegenprobe, als Interview-Übung oder als Zielpublikum-Voreinstellung für Content wertvoll – solange die Persona als Hypothese behandelt und mit realen Daten geerdet wird.

→ **Entscheid:** Der `simulation`-Block ist Teil des Formats: `voice`, `must`, `must_not`, `variance`. Der Prompt-Export (`render --format prompt`) trägt die Guardrails mit: Einzelperson statt Durchschnitt, keine erfundenen Fakten, `unknowns` bleiben offen, Proto-Status wird als Hypothese markiert, keine Innensicht der anbietenden Organisation, keine Überfreundlichkeit. `variance` zwingt zur Festlegung einer konkreten Ausprägung statt des Mittelwerts. Lint verlangt `must_not` und `variance` bei aktiven Personas (S001/S002).

### 1.7 Stereotypisierung

Stockfotos und demografische Marker lösen Stereotype aus und führen zu exkludierendem Design. Mehrere Frameworks empfehlen rein verhaltensbasierte Archetypen ohne erfundene Biografie.

→ **Entscheid:** Kein Foto-Feld. `name` optional. `archetype` beschreibt Verhalten. Das Beispiel `eltern-neu-in-zuerich` kommt ohne Namen und ohne Herkunftsangabe aus – `variance` hält explizit fest, dass Herkunftsland und Beruf für die Gestaltung irrelevant sind.

## 2. Was das Format bewusst nicht enthält

| Weggelassen | Grund |
|---|---|
| Foto, Alter, Familienstand als eigene Felder | Stereotypisierung; keine Gestaltungsrelevanz ohne Begründung |
| Marketing-Felder (Kaufkraft, Markenaffinität) | B2C-Marketing-Persona ist ein anderes Werkzeug |
| Freitext-«Biografie» als Pflichtfeld | Lädt zu erfundenen Details ein; `## Narrativ` im Body ist optional und darf keine neuen Fakten einführen |
| Fertige Journey-Map | Gehört in journeykit; `relations.journeys` verlinkt |

## 3. Wie Personas als Input für andere Lösungen dienen

| Einsatz | Export | Hinweis |
|---|---|---|
| Content-Generierung für ein Zielpublikum (Elternbrief, Website-Text, FAQ) | `render -f prompt -m audience` | Erlebnisziele als Veto-Kriterium; Register der Persona, nicht der Verwaltung |
| Synthetische Gegenprobe (Entwurf «vorlesen», Interview üben) | `render -f prompt -m simulate` | Hypothese, nicht Evidenz; Ergebnisse nie als Nutzerforschung ausgeben |
| User Journeys (journeykit) | `render -f json` oder `bundle` | Persona-ID als Akteur; Jobs als Journey-Treiber |
| Priorisierung von Features/Massnahmen | `render -f matrix` | Opportunity-Score pro Job; primäre Persona entscheidet bei Konflikt |
| Dokumentation (Notion, Confluence, Wiki) | `render -f md` / `card` | Card für Übersichten, md für Detailseiten |
| Team-Kommunikation | `render -f html` | Galerie als Single-File, offline, gruppiert nach Set, Filter nach Set/Priorität/Status |

## 4. Arbeitsrhythmus

1. **Anlegen** als `proto` mit expliziten `assumptions` – 2–4 h Workshop reichen.
2. **Erden** durch 5–8 Interviews oder Support-Logs; `evidence` nachtragen, Variablen mit Evidenz-IDs versehen, `bump --evidence-level qualitative --status active`.
3. **Einsetzen** über Exporte; jede Entscheidung, die eine Persona referenziert, bleibt nachvollziehbar (ID + Version).
4. **Review** vor `review_by`: Was hat sich bestätigt, was nicht? `bump` mit Changelog; bei Verhaltensänderung major, bei Ergänzung minor.
5. **Ruhestand**, wenn Markt, Technologie oder Verhalten sich geändert haben – nie stillschweigend löschen.

## 5. Quellen

Die Analyse stützt sich auf den Forschungsbericht «Personas: Definition und Analyse» (Cooper, Nielsen, Pruitt/Adlin, NN/g, Christensen/Ulwick/Moesta, Salminen/Jansen) sowie auf folgende aktuelle Arbeiten zu synthetischen Nutzern:

- Xiao et al. (2026): *The Chameleon's Limit: Investigating Persona Collapse and Homogenization in LLMs* – arXiv 2604.24698
- Özkan (2026): *Distribution-First Population Simulation: Collapse, Calibration, and Recall in Non-WEIRD LLM Persona Modeling* – arXiv 2607.18310
- *When Can You Trust Your Synthetic Users? Diagnostics and Corrections for LLM Consumer Panels* (2026) – arXiv 2609.13148
- *The Persona Fidelity Gap: Behaviorally Grounded LLM Personas Still Compress Real-User Preference Diversity* – ICML 2026
- Salminen, Nielsen, Farooq, Jansen (2026): *AI-generated personas: Representing user needs with generative AI models* – Int. J. Human-Computer Studies 209
- *How Is Generative AI Used for Persona Development? A Systematic Review of 52 Research Articles* (2025) – arXiv 2504.04927
- NN/g: *Personas vs. Jobs-to-Be-Done*; *3 Persona Types*; *Why Personas Fail*
