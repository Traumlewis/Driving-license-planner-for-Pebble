#pragma once
#include "language_keys.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
// Counters: LA AU NA Grundausbildung Theorie-Grundstoff Theorie-Zusatzstoff.
// Practical units 45 min, theory units 90 min. Sources in QUELLEN.md.
typedef struct { const char *label; uint16_t target[6]; } Rule;
static const char *const classes[] = {"AM","A1","A2","A","B","BE","C1","C1E","C","CE","D1","D1E","D","DE","L","T"};
static int rules_for(int c, Rule *r) {
 int n=0;
 #define ADD(label,a,b,d,g,t,z) r[n++]=(Rule){label,{a,b,d,g,t,z}}
 switch(c) {
 case 0: ADD(LK_Ersterwerb_5979ec4e,0,0,0,0,12,2); ADD(LK_Mit_Fahrerlaubnis_5ceea0d9,0,0,0,0,6,2); break;
 case 1: case 2: case 3:
 ADD(LK_Direkt_Ersterwerb_666bb6c8,5,4,3,0,12,4); ADD(LK_Direkt_Erweiterung_a4ad776c,5,4,3,0,6,4);
 if(c>=2) { ADD(LK_Aufstieg_vor_2_Jahren_9a40d208,3,2,1,0,6,4); r[n++]=(Rule){c==2?LK_A1_auf_A2_ab_2_J_3ddd4dd0:LK_A2_auf_A_ab_2_J_051ae8ee,{0,0,0,0,0,0}}; } break;
 case 4: ADD(LK_Ersterwerb_5979ec4e,5,4,3,0,12,2); ADD(LK_Mit_Fahrerlaubnis_5ceea0d9,5,4,3,0,6,2); break;
 case 5: ADD(LK_B_auf_BE_5a4b92b1,3,1,1,0,0,0); break;
 case 6: ADD(LK_B_auf_C1_b071801e,3,1,1,0,6,6); ADD(LK_Vorbesitz_D1_D_43f27f8f,3,1,1,0,6,2); break;
 case 7: ADD(LK_C1_auf_C1E_0d573b8b,3,1,1,0,0,0); ADD(LK_C1_C1E_gemeinsam_c266ee4b,4,2,2,0,6,6); break;
 case 8: ADD(LK_B_auf_C_a3e98960,5,2,3,0,6,10); ADD(LK_C1_auf_C_335f1ecd,3,1,1,0,6,4); ADD(LK_Vorbesitz_D1_6b45fe64,5,2,3,0,6,4); ADD(LK_Vorbesitz_D_954c576c,5,2,3,0,6,2); break;
 case 9: ADD(LK_C_auf_CE_0eb4c2dd,5,2,3,0,6,4); ADD(LK_C_CE_gemeinsam_d665b6a1,8,3,3,0,6,14); break;
 case 10:
 ADD(LK_B_bis_2_Jahre_97b09a33,19,12,7,41,6,10); ADD(LK_B_uber_2_Jahre_b46ef68a,8,4,4,16,6,10);
 ADD(LK_C_bis_2_Jahre_5ba75a10,8,4,4,8,6,4); ADD(LK_C_uber_2_Jahre_0e517216,4,2,2,6,6,4);
 ADD(LK_C1_bis_2_Jahre_ebe66511,19,12,7,41,6,4); ADD(LK_C1_uber_2_Jahre_0cc7cf51,8,4,4,16,6,4); break;
 case 11: ADD(LK_D1_auf_D1E_97e05e32,3,1,1,4,0,0); break;
 case 12:
 ADD(LK_B_bis_2_Jahre_97b09a33,22,14,8,45,6,18); ADD(LK_B_uber_2_Jahre_b46ef68a,12,8,5,33,6,18);
 ADD(LK_C_bis_2_Jahre_5ba75a10,16,8,6,14,6,8); ADD(LK_C_uber_2_Jahre_0e517216,8,4,3,7,6,8);
 ADD(LK_D1_auf_D_3d9ec802,5,5,5,20,6,8); ADD(LK_C1_bis_2_Jahre_ebe66511,22,14,8,45,6,12); ADD(LK_C1_uber_2_Jahre_0cc7cf51,12,8,5,33,6,12); break;
 case 13: ADD(LK_D_auf_DE_8fd80a3e,3,1,1,4,0,0); break;
 case 14: ADD(LK_Ersterwerb_5979ec4e,0,0,0,0,12,2); ADD(LK_Mit_Fahrerlaubnis_5ceea0d9,0,0,0,0,6,2); break;
 case 15: ADD(LK_Ersterwerb_5979ec4e,0,0,0,0,12,6); ADD(LK_Mit_Fahrerlaubnis_5ceea0d9,0,0,0,0,6,6); break;
 }
 #undef ADD
 return n;
}
