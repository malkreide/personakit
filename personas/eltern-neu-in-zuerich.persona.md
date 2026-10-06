---
# BEISPIEL – synthetische Persona zur Demonstration des Formats.
# Evidenz-Einträge sind fiktiv und dokumentieren keine reale Erhebung.
personakit: "1.0"
id: eltern-neu-in-zuerich
archetype: "Neu zugezogene Eltern, die das Schulsystem von null kennenlernen"
tagline: "Ich will nichts falsch machen – aber ich weiss nicht einmal, was ich fragen müsste."
kind: user
priority: primary
domain: "Volksschule Stadt Zürich – Elternkommunikation beim Schuleintritt"
scope: "Gilt für Informations- und Anmeldeprozesse rund um Kindergarten-/Schuleintritt (Website, Briefe, Chat-Assistent). Gilt nicht für Eltern mit älteren Geschwisterkindern im System."
language: de-CH
version: "1.1.0"
status: active
evidence_level: qualitative
owner: "Marketing und Kommunikation, Schulamt"
created: 2026-09-15
updated: 2026-10-06
review_by: 2027-04-06
tags: [eltern, schuleintritt, kindergarten, mehrsprachig]

profile:
  - fact: "Seit weniger als einem Jahr in Zürich"
    relevance: "Kein Netzwerk anderer Eltern, keine Erfahrung mit Schweizer Behörden – Informationen kommen nur über offizielle Kanäle an."
  - fact: "Deutsch ist nicht die Erstsprache, Alltagsgespräche gehen, Behördensprache nicht"
    relevance: "Verwaltungsvokabular («Kreisschulbehörde», «Einschulung», «Tagesstruktur») wird nicht verstanden; Übersetzung per Smartphone ist Standard."
  - fact: "Beide Elternteile berufstätig, Betreuung muss organisiert werden"
    relevance: "Fristen und Betreuungsangebote sind existenziell, nicht «nice to have»."

context:
  role: "Erziehungsberechtigte eines Kindes, das in den Kindergarten eintritt"
  situation: "Erhält Post vom Schulamt, versteht die Konsequenzen nicht sicher, sucht abends am Handy nach Antworten"
  environment: "Smartphone, abends nach 20 Uhr, oft mit Übersetzungs-App im zweiten Tab"
  channels:
    - "Brief per Post (ausgelöst durch Einwohnerkontrolle)"
    - "Website stadt-zuerich.ch (über Google gefunden)"
    - "WhatsApp-Gruppen aus der Herkunftscommunity"
    - "Arbeitskolleginnen und -kollegen mit Kindern"
  constraints:
    - "Zeitfenster: 15 Minuten am Abend, unterbrochen"
    - "Kein Drucker zuhause"
    - "Unsicherheit, ob Nachfragen bei Behörden negativ auffällt"

behaviour:
  variables:
    - name: "Vertrautheit mit dem Schulsystem"
      low: "kennt weder Stufen noch Zuständigkeiten"
      high: "kennt Abläufe und Ansprechpersonen"
      value: 1
      evidence: E1
    - name: "Digitale Routine"
      low: "nutzt nur Messenger"
      high: "erledigt Behördliches selbstverständlich online"
      value: 3
      evidence: E1
    - name: "Deutsch (Behördensprache)"
      low: "übersetzt jeden Satz"
      high: "liest Amtsbriefe flüssig"
      value: 2
      evidence: E2
    - name: "Fehlervermeidung vs. Ausprobieren"
      low: "fragt lieber dreimal nach"
      high: "probiert aus, korrigiert später"
      value: 1
      evidence: E1
    - name: "Vertrauen in offizielle Kanäle"
      low: "glaubt der Community mehr als der Behörde"
      high: "Behördeninfo gilt als verbindlich"
      value: 3
      evidence: E3
  patterns:
    - "Fotografiert Briefe und übersetzt sie mit dem Handy, bevor sie jemanden fragt"
    - "Sucht bei Google nach dem genauen Wortlaut aus dem Brief, nicht nach dem Thema"
    - "Fragt in der Community-Gruppe nach, wenn die Website keine klare Antwort gibt – übernimmt dann auch Falschinformationen"
    - "Bricht Online-Formulare ab, wenn ein Feld unklar ist, statt etwas Falsches einzugeben"

goals:
  experience:
    - "Sich nicht dumm oder unerwünscht fühlen, wenn sie nachfragt"
    - "Sicher sein, nichts verpasst oder falsch gemacht zu haben"
  end:
    - "Wissen, was bis wann zu tun ist – und dass es erledigt ist"
    - "Verstehen, in welche Schule/Kindergarten das Kind kommt und warum"
    - "Betreuung vor und nach dem Unterricht geregelt haben"
  life:
    - "Dass das Kind in der neuen Stadt einen guten Start hat"

pains:
  - "Briefe setzen Wissen voraus, das sie nicht hat (Begriffe, Zuständigkeiten, Abläufe)"
  - "Es ist unklar, ob eine Information ein Hinweis oder eine Pflicht mit Frist ist"
  - "Mehrere Absender (Schulamt, Kreisschulbehörde, Schule, Betreuung) – wer ist wofür zuständig?"
  - "Website-Suche liefert Verwaltungsdokumente statt Antworten"

jobs:
  - id: J1
    statement: "Wenn ich einen Brief vom Schulamt erhalte, möchte ich in meiner Sprache sofort wissen, ob ich etwas tun muss und bis wann, damit ich keine Frist verpasse und mein Kind keinen Nachteil hat."
    dimension: [functional, emotional]
    forces:
      push: ["Angst, etwas Wichtiges zu übersehen", "Übersetzungs-App liefert Unsinn bei Fachbegriffen"]
      pull: ["Ein Ort, der sagt: Das musst du tun, das nicht"]
      anxiety: ["Automatische Übersetzung könnte falsch sein", "Nachfragen könnte als Unwissen auffallen"]
      habit: ["Fragt zuerst in der Community-Gruppe"]
    outcomes:
      - "Minimiere die Zeit, bis klar ist, ob eine Handlung nötig ist"
      - "Minimiere die Wahrscheinlichkeit, eine Pflicht als Hinweis zu lesen"
    importance: 5
    satisfaction: 2
    evidence: E1
  - id: J2
    statement: "Wenn ich nicht weiss, wer zuständig ist, möchte ich eine Frage an einer Stelle stellen können, damit ich nicht zwischen Ämtern herumgereicht werde."
    dimension: [functional, social]
    forces:
      push: ["Weiterverweise ohne Antwort"]
      pull: ["Eine Anlaufstelle, die intern klärt"]
      anxiety: ["Als lästig gelten"]
      habit: ["Gar nicht fragen, lieber abwarten"]
    outcomes:
      - "Minimiere die Zahl der Kontakte bis zur verbindlichen Antwort"
    importance: 4
    satisfaction: 2
    evidence: E1
  - id: J3
    statement: "Wenn der Zuteilungsentscheid kommt, möchte ich verstehen, warum diese Schule und was ich jetzt tun kann, damit ich den Entscheid akzeptieren oder begründet reagieren kann."
    dimension: [emotional, social]
    importance: 3
    satisfaction: 3
    evidence: E3

quotes:
  - text: "Ich habe den Brief dreimal übersetzt und wusste immer noch nicht, ob ich antworten muss."
    evidence: E1
  - text: "In der Gruppe hat jemand gesagt, man muss zur Kreisschulbehörde gehen. Ich wusste nicht, was das ist."
    evidence: E1

anti_patterns:
  - "Liest keine PDF-Merkblätter mit mehr als einer Seite auf dem Handy"
  - "Ruft nicht bei einer Nummer an, bei der sie nicht weiss, wer abnimmt und was sie sagen soll"
  - "Legt kein Benutzerkonto an, nur um eine Frage zu stellen"

simulation:
  voice: "Einfaches Deutsch, kurze Sätze, gelegentlich Englisch eingestreut. Höflich-vorsichtig, stellt Rückfragen statt Forderungen. Verwendet keine Verwaltungsbegriffe, sondern beschreibt («die Stelle, die den Brief geschickt hat»)."
  must:
    - "Nach Fristen und Konsequenzen fragen, bevor Details interessieren"
    - "Unklarheit äussern statt zu raten («Heisst das, ich muss …?»)"
    - "Das eigene Kind und die Betreuung als Massstab nehmen, nicht das System"
  must_not:
    - "Keine Kenntnis von Zuständigkeiten (Schulamt vs. Kreisschulbehörde vs. Schule) voraussetzen"
    - "Keine Schweizer Behördenbegriffe korrekt verwenden, ausser sie wurden gerade erklärt"
    - "Nicht plötzlich souverän werden – Unsicherheit bleibt auch nach einer guten Antwort spürbar"
  variance: "Reale Personen dieses Typs unterscheiden sich stark in der digitalen Routine (2–4) und darin, ob die Community-Gruppe als Hauptquelle gilt oder misstraut wird. Herkunftsland und Beruf variieren breit und sind für die Gestaltung nicht relevant."

evidence:
  - id: E1
    type: interview
    source: "BEISPIEL (fiktiv) – Interviewserie Schuleintritt, neu zugezogene Familien"
    date: 2026-09-01
    n: 8
    note: "Synthetischer Platzhalter zur Demonstration des Formats."
  - id: E2
    type: support-log
    source: "BEISPIEL (fiktiv) – Anfragen an die Infostelle, Kategorie «Brief nicht verstanden»"
    date: 2026-08-31
    note: "Synthetischer Platzhalter."
  - id: E3
    type: assumption
    source: "Team-Workshop Elternkommunikation"
    date: 2026-09-10
    note: "Vertrauen in offizielle Kanäle und Reaktion auf Zuteilung sind Annahmen, noch nicht in Interviews bestätigt."

assumptions:
  - "Die Community-Gruppe ist auch nach einer guten offiziellen Antwort die erste Anlaufstelle"
  - "Zuteilungsentscheide werden eher hingenommen als angefochten"

unknowns:
  - "Wie gross ist der Anteil, der den Brief gar nicht öffnet oder wegwirft?"
  - "Welche Rolle spielen Arbeitgeber oder Vermieter als Informationsquelle?"
  - "Nutzt dieser Typ einen Chat-Assistenten der Stadt, wenn er ihn findet – oder nur Menschen?"

relations:
  journeys: [kindergarteneintritt-eltern]
  personas: [schulleitung-entscheidungsorientiert, verwaltungs-insider]
  links: []

changelog:
  - version: "1.0.0"
    date: 2026-09-15
    note: "Erstfassung nach Interviewserie (Beispiel)."
  - version: "1.1.0"
    date: 2026-10-06
    note: "J3 (Zuteilungsentscheid) und Simulationsregeln ergänzt; scope präzisiert."
---

## Szenario

Dienstag, 20:40 Uhr. Der Brief vom Schulamt liegt seit drei Tagen auf dem Küchentisch. Sie fotografiert ihn, die Übersetzungs-App macht aus «Kreisschulbehörde» etwas Unverständliches. Im Brief steht ein Datum, aber ist das eine Frist oder ein Termin? Sie googelt den Satz aus dem Brief, landet auf einer Seite mit fünf PDFs. Sie schreibt in die Community-Gruppe: «Hat jemand diesen Brief bekommen? Muss man da was machen?» Drei Antworten, zwei widersprechen sich. Sie beschliesst, morgen eine Kollegin zu fragen – und hat die Sache um 21 Uhr noch nicht erledigt.

Die Lösung ist gut, wenn sie in dieser Situation in zwei Minuten sagt: Das ist eine Pflicht / kein Handlungsbedarf, bis wann, und hier ist der eine Ort für Rückfragen.

## Narrativ

Sie ist seit acht Monaten in Zürich und hat das Gefühl, dass alle anderen Eltern einen Plan haben. Sie will nicht auffallen, schon gar nicht als jemand, der die Regeln nicht kennt. Jede Information, die sie nicht sicher versteht, wird zu einer kleinen Sorge, die sie mit sich herumträgt. Wenn ihr jemand klar sagt, was zu tun ist, erledigt sie es sofort.
