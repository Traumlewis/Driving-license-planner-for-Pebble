# Option 2: Speicheroptimierung der App-Daten

Ergebnis: Die kompaktere Ablage spart im getesteten Prototyp 258 bis 786 Byte Nutzdatenspeicher. Bei 24 normalen Handy-Terminen und Fortschritt für alle Klassen sind es 450 Byte. Das ist eine sinnvolle Verbesserung, löst aber die vollständigen selbstständigen Sprachpakete für alle älteren Uhren noch nicht.

Dies ist ein Desktop-Test der tatsächlichen App-Speicherlogik, kein eingebautes Watch-Update. Version 3.8.49, Live-Sprachpakete und fertige PBW bleiben unverändert. Es wurde keine neue PBW und kein GitHub Release erstellt.

## Gemessene Größen

Die Werte bezeichnen die gespeicherten App-Daten ohne Sprachpaket. Alle fünf Geräteprojekte liefern dieselben Werte.

| Szenario | Aktuell | Prototyp | Ersparnis |
| --- | ---: | ---: | ---: |
| Keine Termine, leeres Profil | 824 B | 38 B | 786 B |
| Drei Handy-Termine, Fortschritt einer Klasse | 848 B | 111 B | 737 B |
| 24 Handy-Termine, Fortschritt aller 16 Klassen | 1.208 B | 758 B | 450 B |
| 24 Termine, zusätzlich alle Schlummer-/Nachfragezeiten, alle Klassen | 1.208 B | 950 B | 258 B |

Bei der letzten Zeile sind alle optionalen Zeitfelder sowie große gültige Fortschrittswerte belegt. Die nichtlineare Ersparnis ist beabsichtigt: Leere Felder und Datensätze brauchen im Prototyp kaum Platz. Eine komplett gefüllte App spart weniger.

Der bestehende 20-Byte-Buchungsdatensatz bleibt unverändert. Die modellierten Spitzen während einer Buchung sind damit 778 bzw. 970 Byte in den beiden vollen Szenarien. Im strengeren Szenario bleiben von den 4.096 Byte der älteren Uhren 3.126 Byte für ein Sprachpaket einschließlich seiner Verwaltung übrig.

Diese Werte sind persistente Nutzdatenwerte. Es sind keine Messwerte für freien RAM, den Ressourcenbereich oder den internen Flash-Verwaltungsaufwand. Die RAM-Strukturen der App werden nicht verkleinert. Ein nativer Build mit dieser Codec-Schicht wurde nicht erstellt.

## Was der Prototyp ändert

- Ein leerer oder abgeschlossener Terminplatz wird entfernt. Die bisherige App speichert für jeden der 24 Plätze 32 Byte. Aktive Termine bleiben vollständig erhalten; der neue Datensatz braucht 15–27 Byte. Handy-Übertragungskennungen, Alarmflags, Schlummer- und Nachfragezeiten gehen nicht verloren.
- Erinnerungszeiten werden verlustfrei als Viertelstundenwerte abgelegt, Praxis-Zusatzminuten als Fünfminutenwerte. Die Wertebereiche entsprechen dem bestehenden Modell.
- Sechs Fortschrittszähler brauchen 8 statt 12 Byte, Praxisfortschritt 4 statt 8 Byte. Null-Datensätze werden entfernt.
- Klassenprofil und Profilliste werden kompakter gespeichert. Historische Werte außerhalb der heutigen normalen Bereiche bleiben unverändert im alten Rohformat erhalten.
- Die fachliche Logik aus store.c und das Buchungsjournal werden nicht umgeschrieben. Ein Adapter kodiert einzelne Datensätze an denselben Schlüsseln. Der Leser versteht sowohl alte als auch neue Datensätze, auch mitten in einer unterbrochenen Umstellung.

Inaktive alte Termin-Datensätze enthalten historische Felder, die die App nicht mehr verwendet; diese Datensätze werden nicht behalten. Die aktive Termin-ID/Übertragungskennung und die globale zuletzt bestätigte Anfrage bleiben für die bestehende Duplikaterkennung erhalten.

## Verifikation

Die Tests kompilieren für time2, core2duo, time-pebble2, round2 und timeround jeweils den originalen store.c und dessen bisherige store_test.c. Umgeleitet wird nur die Persistenz-Schnittstelle in einer temporären Quellkopie. Der echte App-Code wird nicht verändert.

Pro Projekt bestanden:

- Die bisherigen Speicherprüfungen einschließlich alter Datenmigration, Theorie-Häkchen, manueller GS/ZS-Korrekturen, Zusatzminuten und genau einmaliger Stundenbuchung.
- 12.000 zufällige, verlustfreie Ein-/Ausgabezyklen für aktive Termine, Zähler und Praxisfortschritt. Alte außerhalb der heutigen Bereiche liegende Werte bleiben im Rohformat lesbar.
- Acht Abbruchgrenzen einer Stundenbuchung; nach Neustart bleibt entweder der alte Zustand oder die Buchung wird genau einmal fertiggestellt.
- 150 Abbruchgrenzen der Datenumstellung, einschließlich eines noch offenen Buchungsjournals. Gemischte alte/neue Datensätze bleiben lesbar, und die Umstellung lässt sich fortsetzen.
- Ein simuliertes SDK-Limit von 4.096 Byte. Bei den Unterbrechungstests sind zusätzlich 2.567 Byte für das vorhandene größte LP4-Sprachpaket einschließlich Verwaltung reserviert.
- AddressSanitizer und UndefinedBehaviorSanitizer. LeakSanitizer ist im getracten Executor deaktiviert; der Codec führt keine neue Heap-Allokation ein.

Das sind Desktop-/Speicherlogiktests. Tests auf tatsächlicher Pebble-Firmware, nativer RAM-/Stackbedarf, ein produktiver Migrationsauslöser und eine sichere Rückkehrstrategie auf ältere App-Builds sind vor einem Einbau noch erforderlich. Ein alter Build kennt das neue Datensatzformat nicht. Die Originaldaten dieses Tests sind synthetische Fixtures; vorhandene Uhren-/Emulatordaten wurden nicht berührt.

## Reicht es für Sprache plus Wörterbuch?

Die bisherigen eigenständigen BPE/Huffman-Versuchspakete brauchen bereits 4.390–4.799 Byte inklusive 16 Byte Verwaltung. Sie passen selbst ohne App-Daten nicht in 4.096 Byte.

Als kompaktere Vergleichsgröße ergaben sich für vollständige Texte mit Raw-DEFLATE und einem großen Fenster die folgenden minimal angesetzten Größen. Header, Sprachname und 16 Byte Verwaltung sind hier berücksichtigt. Ein Pebble-Decoder und dessen RAM-Bedarf sind damit nicht nachgewiesen.

| Sprache | Minimaler DEFLATE-Ansatz mit Verwaltung | Im strengeren App-Szenario verfügbar |
| --- | ---: | ---: |
| Deutsch | 3.381 B | 3.126 B |
| Englisch | 3.168 B | 3.126 B |
| Spanisch | 3.488 B | 3.126 B |
| Französisch | 3.328 B | 3.126 B |

Bei wenigen Terminen könnten kleinere Vergleichsvarianten ins Budget passen. Daraus folgt aber keine zuverlässige Lösung für die vollständige Offline-App mit 24 Terminen und Daten aller Klassen. Die Optimierung ist nützlich; allein reicht die getestete Variante für diesen Sprachpaket-Plan noch nicht. Das ist keine Behauptung, dass jede zukünftige Speicher- oder Kompressionsmethode unmöglich wäre.

## Reproduzieren

```
python tools/prototypes/test_storage_optimization.py --output /tmp/storage-optimization-test
ASAN_OPTIONS=detect_leaks=0 python tools/prototypes/test_storage_optimization.py --output /tmp/storage-optimization-test --sanitize
```

Die Ergebnisse sind in storage-optimization-option2-results.json abgelegt. Die ursprüngliche App bleibt während des Versuchs unverändert; der Test schreibt nur temporäre Kompilate und Ergebnisdateien. Es wurde kein GitHub Release ausgelöst.
