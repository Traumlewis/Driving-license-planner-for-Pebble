# Isolated EU glyph probe

A separate app UUID tests the existing system fonts without writing planner storage. It draws Czech Čč Ďď Ěě Ňň Řř Šš Ťť Ůů Žž and Hungarian/Romanian/Finnish Őő Űű Ăă Șș Țț Ää Öö Åå. Down cycles GOTHIC 14/14 bold/18/18 bold/24/24 bold/28 bold. Select switches between character groups. Back exits. No data is persisted.

Build with Pebble SDK 4.44 from this directory. Never install it using the planner UUID. Native screenshots for all six targets and seven font variants were captured under docs/verification/dev/eu-glyph-probe, excluded from source publication. The planner was reopened afterwards; its original data is compared separately before/after the language upgrade.

The next EU-language campaign uses Ĺĺ Ľľ Ŕŕ Čč Ćć Đđ Šš Žž Ôô and Õõ Ää Öö Üü Ďď Ťť Ňň. Its 84 screenshots are stored separately under docs/verification/dev/eu-glyph-probe-18. The previous glyph campaign remains in Git history and its original local screenshots.

The SK/HR/SL/ET campaign uses Ĺĺ Ľľ Ŕŕ Čč Ćć Đđ Šš Žž Ôô and Õõ Ää Öö Üü Ďď Ťť Ňň. Capture output is stored under docs/verification/dev/eu-glyph-probe-18, again seven font variants on six platforms. All planner data remains separate.

For the final six EU languages, Up toggles system/custom Open Sans Condensed fonts, Down cycles seven sizes, Select toggles LV/LT/MT and Greek/Cyrillic groups. The isolated app logs font-descriptor heap use. Source fonts and redistribution license are bundled. Current test UUID remains separate from the planner. System-font coverage and custom-font coverage are stored separately under eu-glyph-probe-24 and eu-glyph-probe-24-custom.
