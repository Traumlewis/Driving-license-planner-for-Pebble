#pragma once
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
 case 0: ADD("Ersterwerb",0,0,0,0,12,2); ADD("Mit Fahrerlaubnis",0,0,0,0,6,2); break;
 case 1: case 2: case 3:
 ADD("Direkt / Ersterwerb",5,4,3,0,12,4); ADD("Direkt / Erweiterung",5,4,3,0,6,4);
 if(c>=2) { ADD("Aufstieg vor 2 Jahren",3,2,1,0,6,4); r[n++]=(Rule){c==2?"A1 auf A2 ab 2 J.":"A2 auf A ab 2 J.",{0,0,0,0,0,0}}; } break;
 case 4: ADD("Ersterwerb",5,4,3,0,12,2); ADD("Mit Fahrerlaubnis",5,4,3,0,6,2); break;
 case 5: ADD("B auf BE",3,1,1,0,0,0); break;
 case 6: ADD("B auf C1",3,1,1,0,6,6); ADD("Vorbesitz D1 / D",3,1,1,0,6,2); break;
 case 7: ADD("C1 auf C1E",3,1,1,0,0,0); ADD("C1+C1E gemeinsam",4,2,2,0,6,6); break;
 case 8: ADD("B auf C",5,2,3,0,6,10); ADD("C1 auf C",3,1,1,0,6,4); ADD("Vorbesitz D1",5,2,3,0,6,4); ADD("Vorbesitz D",5,2,3,0,6,2); break;
 case 9: ADD("C auf CE",5,2,3,0,6,4); ADD("C+CE gemeinsam",8,3,3,0,6,14); break;
 case 10:
 ADD("B bis 2 Jahre",19,12,7,41,6,10); ADD("B über 2 Jahre",8,4,4,16,6,10);
 ADD("C bis 2 Jahre",8,4,4,8,6,4); ADD("C über 2 Jahre",4,2,2,6,6,4);
 ADD("C1 bis 2 Jahre",19,12,7,41,6,4); ADD("C1 über 2 Jahre",8,4,4,16,6,4); break;
 case 11: ADD("D1 auf D1E",3,1,1,4,0,0); break;
 case 12:
 ADD("B bis 2 Jahre",22,14,8,45,6,18); ADD("B über 2 Jahre",12,8,5,33,6,18);
 ADD("C bis 2 Jahre",16,8,6,14,6,8); ADD("C über 2 Jahre",8,4,3,7,6,8);
 ADD("D1 auf D",5,5,5,20,6,8); ADD("C1 bis 2 Jahre",22,14,8,45,6,12); ADD("C1 über 2 Jahre",12,8,5,33,6,12); break;
 case 13: ADD("D auf DE",3,1,1,4,0,0); break;
 case 14: ADD("Ersterwerb",0,0,0,0,12,2); ADD("Mit Fahrerlaubnis",0,0,0,0,6,2); break;
 case 15: ADD("Ersterwerb",0,0,0,0,12,6); ADD("Mit Fahrerlaubnis",0,0,0,0,6,6); break;
 }
 #undef ADD
 return n;
}
