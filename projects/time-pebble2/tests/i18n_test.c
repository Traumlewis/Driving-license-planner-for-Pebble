#include <assert.h>
#include <string.h>
#include <stdio.h>
#include "i18n.h"
uint8_t language;
int main(void){language=0;assert(!strcmp(T("Übungsfahrten"),"Übungsfahrten"));language=1;assert(!strcmp(T("Übungsfahrten"),"General driving"));assert(!strcmp(T("Datum"),"Date"));assert(!strcmp(T("Praxis | Nachtfahrt"),"Practice | Night driving"));assert(!strcmp(T("Deine Klasse"),"Licence class"));puts("PASS translations: German umlauts and English UI");}
