#pragma once
#include "language_keys.h"
static const char *const ground_topics[12]={
 LK_Personliche_Voraussetzungen_ba63c1cf,LK_Risikofaktor_Mensch_5f79355b,LK_Rechtliche_Grundlagen_cdf355ad,LK_Strassenverkehrssystem_c69b75b4,LK_Vorfahrt_und_Regelungen_f76846be,LK_Zeichen_und_Bahnubergange_4d5047a3,LK_Andere_Verkehrsteilnehmer_1854e01a,LK_Tempo_Abstand_Umwelt_4f62ecbd,LK_Fahrmanover_und_Beobachtung_a590799b,LK_Halten_und_Parken_92074942,LK_Besondere_Situationen_62d9421e,LK_Lebenslanges_Lernen_1c3e3866
};
static const char *topic_label(int cls,int topic) {
 if(topic<12)return ground_topics[topic];
 if(cls==4&&topic==12)return LK_B_Technik_und_Beladung_ed4fa74a;
 if(cls==4&&topic==13)return LK_B_Pkw_und_Anhanger_1875e877;
 return LK_Klassenspezifischer_Stoff_1a0a257a;
}
