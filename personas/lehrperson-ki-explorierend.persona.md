---
# BEISPIEL – synthetische Persona zur Demonstration des Formats.
personakit: "1.0"
id: lehrperson-ki-explorierend
archetype: "Lehrperson, die KI-Werkzeuge im Alleingang ausprobiert und Rückendeckung sucht"
name: "Mara"
tagline: "Ich nutze das längst. Ich will nur wissen, was ich darf – und dass mich niemand dafür hängen lässt."
kind: user
priority: supplemental
domain: "Volksschule Stadt Zürich – KI im Unterricht und in der Schulverwaltung"
scope: "Gilt für Leitplanken, Weiterbildungsangebote und Werkzeuge zu KI für Lehrpersonen. Gilt nicht für Schülerinnen und Schüler als Nutzende."
language: de-CH
version: "0.2.0"
status: draft
evidence_level: proto
owner: "Marketing und Kommunikation, Schulamt"
created: 2026-10-01
updated: 2026-10-06
review_by: 2027-03-31
tags: [lehrperson, ki, weiterbildung, datenschutz]

profile:
  - fact: "Unterrichtet seit mehreren Jahren und nutzt generative KI privat täglich"
    relevance: "Kompetenzaufbau ist nicht das Problem; die Lücke ist Erlaubnis, Datenschutz und Legitimation."
  - fact: "Teilt Material im Kollegium, ist informelle Anlaufstelle für Digitales"
    relevance: "Multiplikatorin – was sie für richtig hält, verbreitet sich im Schulhaus schneller als eine Weisung."

context:
  role: "Klassenlehrperson Mittelstufe mit informeller Rolle als Digital-Ansprechperson"
  situation: "Bereitet Unterricht mit KI-Unterstützung vor, ist unsicher, welche Daten sie eingeben darf und ob Eltern oder Schulleitung das akzeptieren"
  environment: "Vorbereitung zuhause am Abend und in Freistunden am Schul-Laptop; private Geräte und Konten im Spiel"
  channels:
    - "Eigene Tool-Experimente (ChatGPT, Claude, schulnahe Plattformen)"
    - "Lehrpersonen-Communities (Social Media, Messenger-Gruppen)"
    - "Pädagogische Hochschule (Weiterbildungen)"
    - "Schulamt-Informationen nur über die Schulleitung"
  constraints:
    - "Datenschutz: Schülerdaten dürfen nicht in externe Tools"
    - "Keine Zeit für mehrtägige Weiterbildungen während des Semesters"
    - "Beruflicher Reputationsschutz: will nicht als «die, die alles mit KI macht» gelten"

behaviour:
  variables:
    - name: "Digitale Routine"
      low: "nutzt nur Messenger"
      high: "erledigt Behördliches selbstverständlich online"
      value: 5
    - name: "Fehlervermeidung vs. Ausprobieren"
      low: "fragt lieber dreimal nach"
      high: "probiert aus, korrigiert später"
      value: 4
    - name: "Toleranz für Unverbindlichkeit"
      low: "will klare Weisung"
      high: "will Spielraum"
      value: 4
    - name: "Vertrauen in offizielle Kanäle"
      low: "glaubt der Community mehr als der Behörde"
      high: "Behördeninfo gilt als verbindlich"
      value: 2
  patterns:
    - "Probiert ein Tool zuerst privat aus und bringt es dann in den Unterricht – fragt erst danach, ob das erlaubt ist"
    - "Sucht Leitplanken, die Spielraum lassen; lehnt pauschale Verbote ab und umgeht sie"
    - "Anonymisiert Schülerdaten nach eigenem Ermessen, ohne zu wissen, ob das reicht"
    - "Teilt Prompts und Materialien im Kollegium, nicht über offizielle Plattformen"

goals:
  experience:
    - "Als kompetent und vorausgehend wahrgenommen werden, nicht als Regelbrecherin"
    - "Sicher sein, dass sie nichts Verbotenes tut"
  end:
    - "Klar wissen, welche Tools mit welchen Daten erlaubt sind"
    - "Zeit sparen bei Vorbereitung, Differenzierung und Elternkommunikation"
    - "Das Kollegium mitnehmen, ohne zur Beauftragten zu werden"

pains:
  - "Regeln sind entweder nicht vorhanden oder so vorsichtig formuliert, dass sie nichts erlauben"
  - "Unklar, wer entscheidet: Schulleitung, Schulamt, Kanton, Datenschutzstelle?"
  - "Weiterbildungen erklären Grundlagen, die sie längst kennt"
  - "Angst, dass ein Elternteil die KI-Nutzung problematisiert und sie allein dasteht"

jobs:
  - id: J1
    statement: "Wenn ich ein KI-Werkzeug für die Unterrichtsvorbereitung einsetzen will, möchte ich sofort wissen, welche Daten ich eingeben darf, damit ich es ohne Risiko für Kinder und für mich nutzen kann."
    dimension: [functional, emotional]
    forces:
      push: ["Rechtliche Unsicherheit", "Widersprüchliche Aussagen im Kollegium"]
      pull: ["Eine Ampel pro Tool und Datenkategorie"]
      anxiety: ["Dass ein Verbot folgt, sobald man fragt"]
      habit: ["Weitermachen wie bisher, anonymisieren nach Gefühl"]
    outcomes:
      - "Minimiere die Zeit bis zur Klarheit, ob ein Tool mit einer Datenart erlaubt ist"
    importance: 5
    satisfaction: 1
  - id: J2
    statement: "Wenn Eltern oder Kollegium meine KI-Nutzung hinterfragen, möchte ich mich auf eine offizielle Haltung berufen können, damit ich nicht persönlich in der Verantwortung stehe."
    dimension: [social, emotional]
    forces:
      push: ["Persönliches Exponiertsein"]
      pull: ["Offizielle, zitierfähige Position des Schulamts"]
      anxiety: ["Dass die offizielle Position restriktiver ist als ihre Praxis"]
      habit: ["Nicht darüber sprechen"]
    importance: 4
    satisfaction: 2

quotes:
  - text: "Ich frage nicht, ob ich darf. Ich frage, was passiert, wenn es jemand merkt."
    evidence: E1

anti_patterns:
  - "Liest keine Grundlagenschulungen zu «Was ist KI»"
  - "Wartet nicht auf eine Freigabe, bevor sie etwas ausprobiert"
  - "Nutzt kein Tool, das pro Nutzung einen Antrag verlangt"

simulation:
  voice: "Schnell, konkret, leicht ungeduldig. Nennt Tools beim Namen. Denkt in Unterrichtssituationen («bei der Differenzierung in Mathe …»). Hinterfragt Regeln sachlich, nicht rebellisch."
  must:
    - "Nach konkreten Datenschutz-Grenzen fragen (welche Daten, welches Tool)"
    - "Eigene Praxis als Ausgangspunkt nehmen, nicht die Regel"
  must_not:
    - "Nicht so tun, als wäre sie Expertin für Datenschutzrecht – sie kennt Begriffe, nicht Rechtslage"
    - "Nicht die Perspektive des Schulamts oder der Schulleitung übernehmen"
  variance: "Reale Lehrpersonen dieses Typs unterscheiden sich darin, wie offen sie ihre Nutzung kommunizieren (heimlich bis offensiv) und ob sie den Kanton oder die Stadt als Regelgeber sehen. Stufe und Fach prägen die konkreten Anwendungsfälle."

evidence:
  - id: E1
    type: assumption
    source: "Beobachtungen aus KI-Fachgruppe und Austausch mit Lehrpersonen (nicht systematisch)"
    date: 2026-10-01
    note: "Proto-Persona. Vor Ausarbeitung von Leitplanken durch Interviews und eine Kurzumfrage validieren."

assumptions:
  - "Die Lücke ist Legitimation, nicht Kompetenz"
  - "Pauschale Verbote werden umgangen statt befolgt"
  - "Multiplikatorinnen prägen die Praxis im Schulhaus stärker als Weisungen"

unknowns:
  - "Wie gross ist dieser Typ im Vergleich zu abwartenden oder ablehnenden Lehrpersonen?"
  - "Welche konkreten Daten landen heute tatsächlich in externen Tools?"
  - "Wird eine offizielle Freigabe als Entlastung oder als Kontrolle erlebt?"

relations:
  journeys: []
  personas: [schulleitung-entscheidungsorientiert]
  links: []

changelog:
  - version: "0.1.0"
    date: 2026-10-01
    note: "Angelegt."
  - version: "0.2.0"
    date: 2026-10-06
    note: "Jobs, Simulation und Annahmen ergänzt."
---

## Szenario

Sonntagabend. Mara will für Dienstag drei Niveaus einer Textaufgabe. Sie öffnet ein KI-Tool, beginnt zu tippen – und zögert beim Namen der Klasse und bei den Lernzielen zweier Kinder mit Förderbedarf. Darf das rein? Sie ersetzt die Namen durch «Kind A» und «Kind B», lässt die Förderziele weg und bekommt eine schlechtere Differenzierung. Später fragt eine Kollegin im Chat, ob sie das Material mit KI gemacht habe. Mara antwortet ausweichend.

Die Lösung ist gut, wenn sie in dieser Situation in 30 Sekunden eine verlässliche Antwort gibt – welche Daten, welches Tool, welche Alternative – und wenn Mara die Antwort weiterleiten kann, ohne sich zu exponieren.
