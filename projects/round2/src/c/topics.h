#pragma once
static const char *const ground_topics[12]={
 "Persönliche Voraussetzungen","Risikofaktor Mensch","Rechtliche Grundlagen","Straßenverkehrssystem","Vorfahrt und Regelungen","Zeichen und Bahnübergänge","Andere Verkehrsteilnehmer","Tempo, Abstand, Umwelt","Fahrmanöver und Beobachtung","Halten und Parken","Besondere Situationen","Lebenslanges Lernen"
};
static const char *topic_label(int cls,int topic) {
 if(topic<12)return ground_topics[topic];
 if(cls==4&&topic==12)return "B: Technik und Beladung";
 if(cls==4&&topic==13)return "B: Pkw und Anhänger";
 return "Klassenspezifischer Stoff";
}
