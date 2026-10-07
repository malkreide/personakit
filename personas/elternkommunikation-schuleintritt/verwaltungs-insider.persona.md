---
# BEISPIEL – negative Persona. Beschreibt, für wen NICHT gebaut wird:
# die eigene Organisation. Schutz vor selbstreferenziellem Design (Cooper).
personakit: "1.0"
id: verwaltungs-insider
archetype: "Verwaltungs-Insider, der die Abläufe kennt und deshalb nicht merkt, was andere nicht wissen"
tagline: "Das steht doch alles auf der Website."
kind: operator
priority: negative
domain: "Volksschule Stadt Zürich – alle Lösungen mit externen Nutzenden"
scope: "Gilt als Kontrast-Persona für jede Lösung, die sich an Eltern, Lehrpersonen oder Schulleitungen richtet. Nicht für interne Werkzeuge der Schulamts-Mitarbeitenden."
language: de-CH
version: "1.0.0"
status: active
evidence_level: proto
owner: "Marketing und Kommunikation, Schulamt"
created: 2026-10-06
updated: 2026-10-06
review_by: 2027-10-06
tags: [negativ, selbstreferenz, intern]

profile:
  - fact: "Arbeitet seit Jahren im Schulamt oder einer Kreisschulbehörde"
    relevance: "Begriffe, Zuständigkeiten und Fristen sind Alltagswissen – die Vorstellung, dass jemand sie nicht kennt, fehlt im Reflex."

context:
  role: "Mitarbeitende des Schulamts, der Kreisschulbehörden oder der Schulverwaltung"
  situation: "Formuliert, prüft oder bewilligt Kommunikation und Werkzeuge für Externe"
  environment: "Büro, Desktop, Intranet, interne Dokumente im Zugriff"
  channels:
    - "Intranet und interne Ablage"
    - "Fachstellen, kurze Dienstwege"
  constraints:
    - "Rechtliche Korrektheit hat Vorrang vor Verständlichkeit"
    - "Absicherung gegenüber Beschwerden prägt die Formulierung"

behaviour:
  variables:
    - name: "Vertrautheit mit dem Schulsystem"
      low: "kennt weder Stufen noch Zuständigkeiten"
      high: "kennt Abläufe und Ansprechpersonen"
      value: 5
    - name: "Deutsch (Behördensprache)"
      low: "übersetzt jeden Satz"
      high: "liest Amtsbriefe flüssig"
      value: 5
    - name: "Vertrauen in offizielle Kanäle"
      low: "glaubt der Community mehr als der Behörde"
      high: "Behördeninfo gilt als verbindlich"
      value: 5
  patterns:
    - "Beurteilt Texte nach Vollständigkeit und juristischer Absicherung, nicht nach der Frage, ob eine Person in Eile die Handlung erkennt"
    - "Verweist auf bestehende Dokumente («steht im Merkblatt»), statt die Antwort zu geben"
    - "Hält Fachbegriffe für neutral, weil sie intern eindeutig sind"

goals:
  experience:
    - "Keine Beschwerde, kein Fehler, keine Nachfrage von oben"
  end:
    - "Korrekte, vollständige, rechtlich abgesicherte Information"

pains:
  - "Externe stellen Fragen, die «eigentlich» beantwortet sind"

jobs: []

anti_patterns:
  - "Lösungen dürfen nicht voraussetzen, dass Nutzende Zuständigkeiten (Schulamt, Kreisschulbehörde, Schule) kennen"
  - "Lösungen dürfen Vollständigkeit nicht über Handlungsklarheit stellen"
  - "Lösungen dürfen nicht auf Dokumente verweisen, wo eine Antwort möglich ist"
  - "Lösungen dürfen interne Begriffe nicht unerklärt verwenden"
  - "Lösungen werden nicht mit Mitarbeitenden des Schulamts als Testpersonen abgenommen"

simulation:
  voice: "Präzise, vollständig, verwaltungssprachlich. Verweist auf Grundlagen und Zuständigkeiten."
  must:
    - "Als Gegenprobe einsetzen: Würde diese Persona den Entwurf gutheissen? Dann prüfen, ob er für die primäre Persona noch funktioniert."
  must_not:
    - "Nie als Zielpublikum einer externen Lösung verwenden"
  variance: "Irrelevant – diese Persona beschreibt einen Blickwinkel, keine Zielgruppe."

evidence: []

assumptions:
  - "Der Fluch des Wissens (curse of knowledge) ist der häufigste Grund für unverständliche Elternkommunikation"

unknowns:
  - "In welchen Prozessschritten entsteht der Insider-Bias am stärksten – beim Schreiben, beim Prüfen oder bei der Freigabe?"

relations:
  journeys: []
  personas: [eltern-neu-in-zuerich]
  links: []

changelog:
  - version: "1.0.0"
    date: 2026-10-06
    note: "Negative Persona angelegt."
---

## Szenario

Ein Entwurf für den Elternbrief zum Kindergarteneintritt geht in die interne Prüfung. Der Insider ergänzt die Rechtsgrundlage, den Hinweis auf die Zuständigkeit der Kreisschulbehörde und den Link zum Merkblatt. Der Brief ist jetzt korrekt und vollständig – und für die primäre Persona um einen Absatz unverständlicher.

Die Gegenprobe: Jeder Entwurf, den diese Persona ohne Einwand durchwinkt, wird noch einmal gegen `eltern-neu-in-zuerich` getestet.
