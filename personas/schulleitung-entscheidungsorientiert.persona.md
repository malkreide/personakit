---
# BEISPIEL – synthetische Persona zur Demonstration des Formats.
personakit: "1.0"
id: schulleitung-entscheidungsorientiert
archetype: "Schulleitung, die Entscheidungsgrundlagen will, nicht Optionen"
tagline: "Sagt mir, was gilt, was ich entscheiden muss und bis wann. Den Rest lese ich, wenn ich Zeit habe – also nie."
kind: user
priority: secondary
domain: "Volksschule Stadt Zürich – Kommunikation Schulamt → Schulen"
scope: "Gilt für Informationsflüsse vom Schulamt an Schulleitungen (Rundschreiben, Intranet, Weisungen, Tools). Gilt nicht für pädagogische Beratung."
language: de-CH
version: "0.3.0"
status: draft
evidence_level: proto
owner: "Marketing und Kommunikation, Schulamt"
created: 2026-09-20
updated: 2026-10-06
review_by: 2027-01-31
tags: [schulleitung, interne-kommunikation, fuehrung]

profile:
  - fact: "Führt eine Schule mit mehreren hundert Kindern und 40–80 Mitarbeitenden"
    relevance: "Jede Information wird sofort auf «Was heisst das für meine Leute?» übersetzt – Kommunikation muss delegierbar sein."
  - fact: "Mehrjährige Erfahrung mit Reorganisationen und Projekten des Schulamts"
    relevance: "Hohe Skepsis gegenüber Ankündigungen ohne Konsequenz; erwartet, dass «neu» oft «mehr Aufwand» heisst."

context:
  role: "Schulleitung, verantwortlich für Betrieb, Personal und Kommunikation mit Eltern"
  situation: "Verarbeitet täglich Dutzende Mails und Rundschreiben zwischen Elterngesprächen, Personalfragen und Unterrichtsbesuchen"
  environment: "Büro und unterwegs, Laptop und Smartphone, viele kurze Zeitfenster"
  channels:
    - "E-Mail (primär, chronisch überfüllt)"
    - "Schulleitungskonferenz des Schulkreises"
    - "Intranet (nur bei konkretem Suchbedarf)"
    - "Direkte Anrufe an bekannte Personen im Schulamt"
  constraints:
    - "Maximal zwei Minuten pro Mitteilung"
    - "Muss Entscheide gegenüber Team und Eltern vertreten – auch die, die sie nicht teilt"
    - "Rechtliche Verbindlichkeit muss erkennbar sein (Weisung vs. Empfehlung)"

behaviour:
  variables:
    - name: "Vertrautheit mit dem Schulsystem"
      low: "kennt weder Stufen noch Zuständigkeiten"
      high: "kennt Abläufe und Ansprechpersonen"
      value: 5
    - name: "Digitale Routine"
      low: "nutzt nur Messenger"
      high: "erledigt Behördliches selbstverständlich online"
      value: 4
    - name: "Informationsbedürfnis"
      low: "will nur das Resultat"
      high: "will Hintergrund und Herleitung"
      value: 2
    - name: "Toleranz für Unverbindlichkeit"
      low: "will klare Weisung"
      high: "will Spielraum"
      value: 2
    - name: "Vertrauen in offizielle Kanäle"
      low: "glaubt der Community mehr als der Behörde"
      high: "Behördeninfo gilt als verbindlich"
      value: 3
  patterns:
    - "Liest Betreff und ersten Absatz; entscheidet dann, ob das Mail delegiert, archiviert oder gelesen wird"
    - "Fragt in der Schulleitungskonferenz nach, was andere mit einer Mitteilung gemacht haben – Peer-Praxis schlägt Dokument"
    - "Leitet Informationen ans Team erst weiter, wenn klar ist, was das Team konkret tun soll"
    - "Ruft bei Unklarheit direkt eine bekannte Person im Schulamt an, statt die Infostelle zu nutzen"

goals:
  experience:
    - "Als Führungsperson ernst genommen werden, nicht als Empfänger von Anweisungen"
    - "Nie vor dem Team oder Eltern mit einer Information überrascht werden, die sie hätte kennen müssen"
  end:
    - "Jede Mitteilung in Handlung, Delegation oder Ablage übersetzen können – ohne Rückfrage"
    - "Rechtzeitig wissen, was auf die Schule zukommt, um das Team vorzubereiten"
    - "Einheitliche Elternkommunikation, die sie nicht selbst formulieren muss"

pains:
  - "Rundschreiben ohne erkennbare Verbindlichkeit und ohne «Was heisst das für euch?»"
  - "Dieselbe Information kommt aus drei Stellen in drei Versionen"
  - "Ankündigungen ohne Zeitplan – Vorbereitung ist nicht möglich"
  - "Elternkommunikation des Schulamts, von der die Schule erst durch Elternfragen erfährt"

jobs:
  - id: J1
    statement: "Wenn eine Mitteilung des Schulamts eintrifft, möchte ich in einer Minute wissen, ob sie verbindlich ist, was ich tun muss und bis wann, damit ich sie sofort delegieren oder erledigen kann."
    dimension: [functional]
    forces:
      push: ["Überfülltes Postfach", "Unklare Verbindlichkeit"]
      pull: ["Standardisierter Kopf: Verbindlichkeit, Handlung, Frist"]
      anxiety: ["Dass eine kurze Mitteilung Wichtiges verschweigt"]
      habit: ["Nachfrage im Peer-Kreis"]
    outcomes:
      - "Minimiere die Zeit bis zur Einordnung (Pflicht / Empfehlung / Information)"
    importance: 5
    satisfaction: 2
  - id: J2
    statement: "Wenn das Schulamt Eltern direkt informiert, möchte ich die Information vorher und in delegierbarer Form haben, damit ich gegenüber Eltern auskunftsfähig bin."
    dimension: [social, emotional]
    forces:
      push: ["Elternfragen zu Dingen, von denen die Schule nichts weiss"]
      pull: ["Vorab-Information mit Sprachregelung"]
      anxiety: ["Noch mehr Mails"]
      habit: ["Improvisation"]
    importance: 4
    satisfaction: 2

quotes:
  - text: "Ich lese jede Mitteilung mit der Frage: Muss ich das jetzt meinem Team erklären?"
    evidence: E1

anti_patterns:
  - "Liest keine Hintergrund-Konzepte, bevor nicht klar ist, was sich konkret ändert"
  - "Nutzt das Intranet nicht als tägliche Quelle, nur als Nachschlagewerk"
  - "Sucht nicht nach Informationen, die das Schulamt hätte bringen müssen"

simulation:
  voice: "Knapp, direkt, erfahren. Stellt Gegenfragen («Ab wann? Für alle Stufen?»). Verwendet Verwaltungsbegriffe korrekt, aber ungeduldig. Bewertet alles nach Aufwand fürs Team."
  must:
    - "Nach Verbindlichkeit, Frist und Aufwand fragen, bevor Inhalt diskutiert wird"
    - "Peer-Erfahrungen anderer Schulleitungen als Referenz nennen"
  must_not:
    - "Keine Begeisterung für Neuerungen zeigen, bevor der Nutzen für die eigene Schule konkret ist"
    - "Nicht die Innensicht des Schulamts einnehmen – kennt Projektstände und Zuständigkeiten dort nur ungefähr"
  variance: "Reale Schulleitungen unterscheiden sich im Informationsbedürfnis (1–4) und in der Nähe zum Schulamt (vom Peer-Netzwerk bis zum direkten Draht). Grösse der Schule und Schulkreis prägen, wie stark Delegation möglich ist."

evidence:
  - id: E1
    type: assumption
    source: "Erfahrungswissen Abteilung Marketing und Kommunikation; Rückmeldungen aus Schulleitungskonferenzen (nicht systematisch erhoben)"
    date: 2026-09-20
    note: "Proto-Persona. Vor Einsatz als Grundlage für Kommunikationsstandards durch 5–8 Interviews validieren."

assumptions:
  - "Verbindlichkeit ist das erste Sortierkriterium – vor Thema und Absender"
  - "Peer-Praxis in der Schulleitungskonferenz prägt den Umgang mit Mitteilungen stärker als der Text selbst"
  - "Direkte Elternkommunikation des Schulamts wird als Übergehung erlebt, nicht als Entlastung"

unknowns:
  - "Wie viel Hintergrund will diese Schulleitung wirklich – oder liest sie Konzepte, sobald sie gezwungen ist?"
  - "Welche Rolle spielt das Schulleitungs-Intranet tatsächlich im Alltag?"
  - "Unterscheiden sich Schulleitungen kleiner und grosser Schulen in diesem Muster?"

relations:
  journeys: []
  personas: [eltern-neu-in-zuerich, lehrperson-ki-explorierend]
  links: []

changelog:
  - version: "0.1.0"
    date: 2026-09-20
    note: "Proto-Persona aus Workshop angelegt."
  - version: "0.2.0"
    date: 2026-09-28
    note: "Jobs und Kräfte ergänzt."
  - version: "0.3.0"
    date: 2026-10-06
    note: "Simulationsregeln und Varianz ergänzt; Annahmen explizit gemacht."
---

## Szenario

Montag, 07:50 Uhr, zwischen Türöffnen und erster Elternanfrage. 34 neue Mails, drei vom Schulamt. Eines kündigt ein neues Vorgehen bei Elterninformationen an. Sie liest den ersten Absatz: «Das Schulamt informiert ab November die Eltern direkt über …». Sie weiss nicht, ob das bedeutet, dass die Schule etwas tun muss, und ob die Eltern das vor ihr wissen werden. Sie markiert das Mail, um es in der Schulleitungskonferenz anzusprechen – in zwei Wochen.

Die Lösung ist gut, wenn das Mail in einer Minute beantwortet: verbindlich oder nicht, was die Schule tut, bis wann, und welche Sprachregelung gegenüber Eltern gilt.
