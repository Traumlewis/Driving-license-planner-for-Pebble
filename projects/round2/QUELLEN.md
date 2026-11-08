# Gesetzliche Vorgaben

Recherchiert am 06.11.2026 anhand der folgenden amtlichen Online-Fassungen:

- [FahrschAusbO § 4](https://www.gesetze-im-internet.de/fahrschausbo_2012/__4.html): Grundstoff mindestens 12 Doppelstunden, bei vorhandener Fahrerlaubnis 6; eine Doppelstunde dauert 90 Minuten.
- [Anlage 2.8](https://www.gesetze-im-internet.de/fahrschausbo_2012/anlage_2_8.html): klassenspezifischer Zusatzstoff und Reduktionen nach Vorbesitz.
- [Anlage 4](https://www.gesetze-im-internet.de/fahrschausbo_2012/anlage_4.html): besondere Ausbildungsfahrten für Motorrad-, Pkw- und Lkw-Klassen, jeweils 45 Minuten.
- [Anlage 5](https://www.gesetze-im-internet.de/fahrschausbo_2012/anlage_5.html): praktische Mindeststunden für Busklassen nach Vorbesitz und dessen Dauer.
- [FeV § 15](https://www.gesetze-im-internet.de/fev_2010/__15.html) und [FahrschAusbO § 7](https://www.gesetze-im-internet.de/fahrschausbo_2012/__7.html): Ausbildungs-/Prüfungsausnahmen beim Stufenaufstieg und Anhängerklassen.

## Praktische Fahrten

Werte in der Reihenfolge **LA / AU / NA**, jeweils 45 Minuten:

| Profil | LA | AU | NA |
|---|---:|---:|---:|
| A1, A2, A direkt; B | 5 | 4 | 3 |
| A1 auf A2 vor zwei Jahren; A1 auf A; A2 auf A vor zwei Jahren | 3 | 2 | 1 |
| B auf BE; B auf C1; C1 auf C; C1 auf C1E | 3 | 1 | 1 |
| B auf C; C auf CE | 5 | 2 | 3 |
| C1 + C1E gemeinsam, gesamt | 4 | 2 | 2 |
| C + CE gemeinsam, gesamt | 8 | 3 | 3 |

Bei den gemeinsamen Ausbildungen gibt die App die Gesamtwerte an; die erforderliche Aufteilung auf Solo und Zug bleibt zu beachten. Der vereinfachte Gesamtzähler bildet diese Aufteilung nicht ab.

Busprofile werden unmittelbar aus Anlage 5 übernommen, einschließlich der festen Grundausbildung [GA]. Für D1 gibt es gesonderte C1-Profile, da die Theorie bei C1-Vorbesitz reduziert ist. B und C1 werden bei D1 und D getrennt angeboten.

## Theorie

Zusatzstoff in Doppelstunden à 90 Minuten: AM 2; A1/A2/A 4; B 2; C1 6 (mit D1/D: 2); C 10 (mit C1/D1: 4, mit D: 2); CE 4; D1 10 (mit C1/C: 4); D 18 (mit C: 8, mit C1: 12, mit D1: 8); L 2; T 6.

BE, C1E, D1E und DE erfordern beim entsprechenden reinen Anhänger-Erweiterungsprofil keinen zusätzlichen Theorieunterricht. Der prüfungsbasierte Stufenaufstieg nach mindestens zwei Jahren wird nur für A1 → A2 und A2 → A angeboten. A1 → A ist davon nicht umfasst. Bei gemeinsamem C/CE-Erwerb zeigt die App 10 + 4 Zusatzstoff-Doppelstunden.

## Bedeutung der Zähler und Grenzen

- LA = Landstraße/Überland, AU = Autobahn, NA = Dämmerung/Dunkelheit.
- GA = feste praktische Grundausbildung für Busprofile.
- UE = normale Übungsfahrt ohne festen gesetzlichen Mindestzähler.
- GS = theoretischer Grundstoff, ZS = theoretischer Zusatzstoff.
- Praxis wird in 45-Minuten-Einheiten gezählt; Theorie in 90-Minuten-Doppelstunden. Zwei einzelne Theoriestunden à 45 Minuten entsprechen einer angezeigten Einheit und können zusammen manuell eingetragen werden.
- Null bedeutet keine feste Mindestzahl in diesem Profil, nicht „keine Ausbildung erforderlich“. AM und T haben praktische Ausbildung, aber keine festen LA/AU/NA-Mindestzahlen; L hat keine praktische Prüfung.
- Die Auswahl umfasst die 16 regulären Klassen AM, A1, A2, A, B, BE, C1, C1E, C, CE, D1, D1E, D, DE, L und T. B96, B196 und B197 sind Schlüsselzahlen, keine separaten Fahrerlaubnisklassen; deren gesonderte Schulungen sind nicht enthalten.
- Für außergewöhnliche Kombinationen des Vorbesitzes, Umschreibungen, Ausnahmen und gleichzeitig erworbene Klassen können weitere Erleichterungen gelten. Die App bietet die genannten Profile und stellt keinen individuellen Ausbildungsnachweis aus. Die Fahrschule legt den konkreten Ausbildungsbedarf und die zulässige Anrechnung fest.
- Zusätzliche Vorgaben wie die Länge zusammenhängender Fahrten und die Art der befahrenen Straßen werden vom einfachen Stundenkonto nicht geprüft.

## Ergänzung Version 2: Theorie-Themen

- [Anlage 1: Rahmenplan Grundstoff](https://www.gesetze-im-internet.de/fahrschausbo_2012/anlage_1.html) bildet die Grundlage für die 12 verkürzt bezeichneten Grundstoff-Themen.
- [Anlage 2.2: Rahmenplan Klasse B](https://www.gesetze-im-internet.de/fahrschausbo_2012/anlage_2_2.html) bildet die Grundlage für die beiden zusammengefassten B-Zusatzstoff-Themen „Technik und Beladung“ und „Pkw und Anhänger“.
- Eine Themenliste ersetzt weder Unterrichtszeiten noch den Ausbildungsnachweis. Die konkrete Aufteilung in Lektionen richtet sich nach dem Ausbildungsplan der Fahrschule.
- Bei den übrigen Klassen zeigt Version 2 nummerierte Zusatzstoff-Einträge entsprechend der für das gespeicherte Profil vorgesehenen Doppelstunden. Sie beansprucht keine amtliche Themenbenennung pro Doppelstunde.

## Technische Quellen: lokale Timeline (Version 3.4)

- [Lokale Pins](https://developer.repebble.com/guides/pebble-timeline/timeline-local-pins/): direkte lokale API für sideloaded Apps, stabile IDs und Löschungen.
- [PebbleKit JS API](https://developer.repebble.com/docs/pebblekit-js/Pebble/): `insertTimelinePin` / `deleteTimelinePin`.
- [Kalender-Pin-Format](https://developer.repebble.com/guides/pebble-timeline/pin-structure/): `calendarPin`, UTC-Startzeit und Dauer in Minuten.
- [Manifest-Berechtigungen](https://developer.repebble.com/guides/plugins/preview/): `Timeline` in `usesPermissions`.

Abgerufen am 06.11.2026.
