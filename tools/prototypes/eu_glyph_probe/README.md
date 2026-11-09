# Isolated EU glyph probe

A separate app UUID tests the existing system fonts without writing planner storage. It draws Czech Čč Ďď Ěě Ňň Řř Šš Ťť Ůů Žž and Hungarian/Romanian/Finnish Őő Űű Ăă Șș Țț Ää Öö Åå. Down cycles GOTHIC 14/14 bold/18/18 bold/24/24 bold/28 bold. Select switches between character groups. Back exits. No data is persisted.

Build with Pebble SDK 4.44 from this directory. Never install it using the planner UUID. Native screenshots for all six targets and seven font variants were captured under docs/verification/dev/eu-glyph-probe, excluded from source publication. The planner was reopened afterwards; its original data is compared separately before/after the language upgrade.
