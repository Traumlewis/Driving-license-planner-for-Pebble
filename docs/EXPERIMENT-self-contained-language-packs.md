# Versuch: Sprache und Wörterbuch gemeinsam laden

Ergebnis: Der selbstständige Desktop-Prototyp funktioniert, überschreitet aber bei allen vier vorhandenen Sprachen das Speicherbudget der älteren unterstützten Pebbles. Deshalb wurde die App nicht umgestellt und keine neue PBW erzeugt. Die funktionierende 3.8.49 bleibt unverändert.

## Gemessene Paketgrößen

Jedes Versuchspaket enthält alle 296 Texte, ein nur für diese Sprache erzeugtes BPE-Wörterbuch, eine kanonische Huffman-Codetabelle, das Textverzeichnis, den Sprachnamen und einen Header mit Integritätsprüfung. Der Decoder braucht keine Sprachdateien und kein gemeinsames Wörterbuch aus dem Build.

| Sprache | Paket vollständig | Mit 16 Byte Verwaltung und 1.500 Byte App-Reserve |
| --- | ---: | ---: |
| Deutsch | 4.606 B | 6.122 B |
| English | 4.374 B | 5.890 B |
| Español | 4.783 B | 6.299 B |
| Français | 4.719 B | 6.235 B |

Vergleich: Die bisherige App begrenzt Sprachpakete auf 2.560 Byte. Pebble Time/Time Steel (basalt), Pebble 2/2 SE (diorite) und die alte Time Round (chalk) haben laut SDK einen festen Gesamtgrenzwert von 4.096 Byte für die persistenten Werte einer App. Das ist ein Speicherlimit für gespeicherte Daten, kein RAM-Limit. Selbst ohne App-Reserve ist keines dieser BPE-Versuchspakete klein genug.

Die App-Reserve ist keine frei verfügbare Sprachreserve: Die 24 Termin-Datensätze brauchen bereits 768 Byte. Vollständiger Fortschritt aller 16 Klassen braucht weitere 384 Byte. Hinzu kommen Profil, Einstellungen, Versions-/Migrationsschlüssel, Erinnerungsdaten und der Buchungsdatensatz für unterbrechungssichere Änderungen. Diese Funktionen und vorhandene Nutzerdaten wurden nicht reduziert.

## Vergleich mit allgemeiner Kompression

Raw-DEFLATE komprimiert die vollständigen Texte je nach Sprache mit großem Fenster auf 3.113–3.432 Byte. Diese Zahlen enthalten noch keinen Paketheader und keine App-Daten. Mit der bisherigen App-Reserve passen auch diese Varianten nicht in 4.096 Byte. Große DEFLATE-Fenster brauchen außerdem Arbeitsspeicher. Bei nur 512 Byte Fenster liegen die Textdaten bereits bei 3.752–4.275 Byte. Bzip2 lag bei 3.042–3.308 Byte; seine Decoder-RAM-Anforderungen wurden nicht für Pebble implementiert oder gemessen.

Das ist kein Beweis, dass jede denkbare zukünftige Codierung unmöglich ist. Es ist ein belastbares negatives Ergebnis für die getesteten Varianten unter den heutigen Offline- und Speicheranforderungen. Größere Laufzeitquoten neuer Geräte wurden in diesem Versuch nicht gemessen; eine Umstellung für alle unterstützten Uhren scheitert bereits an den älteren Geräten.

## Prüfung und Grenzen

Der Versuch prüft mehrere Wörterbuchgrößen pro Sprache. Jede geprüfte Variante wird vollständig und bytegenau zurückübersetzt. Beschädigte und abgeschnittene Pakete werden abgewiesen. Zusätzliche Tests prüfen unbekannte UTF-8-Texte ohne externe Dateien, ungültige Wörterbuchverweise, zu große Textausgaben und ungültige Huffman-Codetabellen.

Es wurde kein nativer LP5P-Empfänger gebaut oder auf einer Uhr installiert: Die Speicherprüfung scheitert vorher. Die Dateien mit Endung experimental-lp5p sind Entwicklungsartefakte und können nicht mit der App installiert werden. Der laufende App-Code, die Live-Sprachliste, alle bestehenden Kompressionswörterbücher, die Versionsnummer und die fertige 3.8.49-PBW wurden per SHA-256 auf unveränderten Inhalt geprüft.

Reproduzieren:

```
python tools/prototypes/self_contained_languages.py --output /tmp/language-dictionary-prototype
python tools/prototypes/test_self_contained_languages.py
```

Maschinenlesbare Größen: self-contained-language-pack-results.json. Die 4-KB-Grenze ist im SDK für basalt/diorite/chalk als persist_get_max_size(...) (4096) definiert. Die neuen SDK-Plattformen bieten dafür eine Laufzeitabfrage; deren mögliche größere Quoten sind keine zugesicherte Eigenschaft dieses Versuchs.

Quellcode-/Dokumentationsupdate; kein GitHub Release und kein neuer App-Build.
