#include "app.h"
#include "i18n.h"
#include <stdarg.h>
#include <stdio.h>
// Numeric protocol keys also declared in package.json and src/pkjs/index.js.
enum {OP=1,RID,ID,CLS,KIND,WHEN,LEAD1,LEAD2,UNITS,TOPIC,REV,STATUS,PAYLOAD,PART,TOTAL,EXTRA,LANGUAGE,REMINDER2};
static char snapshot[3072],error_text[120];
static size_t length,offset,chunk_ends[16];
static int chunk_count;
static uint32_t request_id,pending_request;
static int pending_status;
static char pending_error[120];
static int response_status,part;
static bool sending,again;
#define add(...) do {if(length<sizeof(snapshot)-1){int written=snprintf(snapshot+length,sizeof(snapshot)-length,__VA_ARGS__);if(written>0)length+=(size_t)written<sizeof(snapshot)-length?(size_t)written:sizeof(snapshot)-length-1;}} while(0)
static void build_snapshot(void) {
 length=0;add("{\"version\":2,\"language\":%u,\"revision\":%lu,\"cls\":%d,\"profile\":%d,\"alarmOk\":%s,\"storageOk\":%s,\"counts\":[",language,(unsigned long)revision,cfg.cls,cfg.profile,alarm_ok?"true":"false",storage_error?"false":"true");
 for(int c=0;c<16;c++)add("%s[%u,%u,%u,%u,%u,%u]",c?",":"",counts[c][0],counts[c][1],counts[c][2],counts[c][3],counts[c][4],counts[c][5]);
 add("],\"remainders\":[");for(int c=0;c<16;c++)add("%s[%u,%u,%u,%u,%u]",c?",":"",practice[c].remainder[0],practice[c].remainder[1],practice[c].remainder[2],practice[c].remainder[3],practice[c].remainder[4]);
 add("],\"extras\":[");for(int c=0;c<16;c++)add("%s%d",c?",":"",profile_extra(c));
 add("],\"topics\":[");for(int c=0;c<16;c++)add("%s%lu",c?",":"",(unsigned long)topics[c]);
 add("],\"entries\":[");bool first=true;
 for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active){Entry *e=&entries[i];add("%s[%lu,%d,%u,%u,%u,%u,%u,%u,%u]",first?"":",",(unsigned long)e->id,(int)e->when,e->cls,e->kind,e->units,e->lead[0],e->lead[1],e->topic,e->extra_minutes);first=false;}
 uint32_t saved_id=0;for(int i=0;i<MAX_ENTRIES;i++)if(request_id&&entries[i].active&&entries[i].token==request_id){saved_id=entries[i].id;break;}
 add("],\"savedId\":%lu,\"error\":\"%s\",",(unsigned long)saved_id,error_text);
 add("\"languagePack\":{\"id\":%lu,\"bytes\":%u,\"ready\":%s,\"received\":%u}}",(unsigned long)language_pack_id(),language_pack_size(),language_pack_ready()?"true":"false",language_pack_received());
}
static void send_part(void) {
 DictionaryIterator *d;if(app_message_outbox_begin(&d)!=APP_MSG_OK){sending=false;return;}
 static char chunk[651];size_t n=chunk_ends[part]-offset;memcpy(chunk,snapshot+offset,n);chunk[n]=0;
 dict_write_uint32(d,RID,request_id);dict_write_int32(d,STATUS,response_status);dict_write_uint8(d,PART,part);dict_write_uint8(d,TOTAL,chunk_count);dict_write_cstring(d,PAYLOAD,chunk);
 if(app_message_outbox_send()!=APP_MSG_OK){sending=false;return;}offset+=n;part++;
}
void phone_push(uint32_t request,int status,const char *error) {
 if(sending){pending_request=request;pending_status=status;snprintf(pending_error,sizeof(pending_error),"%s",error?T(error):"");again=true;return;}
 request_id=request;response_status=status;snprintf(error_text,sizeof(error_text),"%s",error?T(error):"");
 build_snapshot();chunk_count=0;size_t cursor=0;while(cursor<length){size_t end=cursor+650;if(end>length)end=length;while(end<length&&((unsigned char)snapshot[end]&0xc0)==0x80)end--;chunk_ends[chunk_count++]=end;cursor=end;}offset=0;part=0;sending=true;send_part();
}
static void sent(DictionaryIterator *d,void *ctx) {(void)d;(void)ctx;if(offset<length){send_part();return;}sending=false;if(again){again=false;phone_push(pending_request,pending_status,pending_error);}}
static void failed(DictionaryIterator *d,AppMessageResult why,void *ctx) {(void)d;(void)why;(void)ctx;sending=false;again=false;}
static bool integer(DictionaryIterator *d,int key,int32_t *value) {
 Tuple *t=dict_find(d,key);if(!t||(t->type!=TUPLE_UINT&&t->type!=TUPLE_INT))return false;
 if(t->length==4)*value=t->value->int32;
 else if(t->length==2)*value=t->type==TUPLE_INT?t->value->int16:t->value->uint16;
 else if(t->length==1)*value=t->type==TUPLE_INT?t->value->int8:t->value->uint8;
 else return false;
 return true;
}
static void inbox(DictionaryIterator *d,void *ctx) {
 (void)ctx;int32_t op=0,rid=0,id=0,rev=0;
 if(!integer(d,OP,&op))return;
 integer(d,RID,&rid);
 if(op==0){phone_push(rid,0,NULL);return;}
 if(!rid){phone_push(0,-1,"Ungültige Anfrage");return;}
 if(op==4){
  int32_t identity=0,p=0,total=0;Tuple *payload=dict_find(d,PAYLOAD);
  if(!integer(d,ID,&identity)||!integer(d,PART,&p)||!integer(d,TOTAL,&total)||!payload||payload->type!=TUPLE_CSTRING||!payload->length||payload->length>513||payload->value->cstring[payload->length-1]){phone_push(rid,-1,"Ungültige Anfrage");return;}
  int status=language_pack_receive((uint32_t)identity,(unsigned)p,(unsigned)total,payload->value->cstring);
  phone_push(rid,status,status?"Sprachpaket fehlt. Bitte Handy verbinden.":NULL);return;
 }
 if(last_request==(uint32_t)rid){phone_push(rid,0,NULL);return;}
 for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active&&entries[i].token==(uint32_t)rid){phone_push(rid,0,NULL);return;}
 if(op==3){int32_t value;if(!integer(d,LANGUAGE,&value)||value<0||value>1){phone_push(rid,-1,"Ungültige Sprache");return;}if(value==1&&!language_pack_ready()){phone_push(rid,-4,"Sprachpaket fehlt. Bitte Handy verbinden.");return;}if(!store_language(value)){phone_push(rid,-3,"Sprache nicht gespeichert");return;}store_request(rid);store_revision();state_changed();phone_push(rid,0,NULL);show_status("Sprache gespeichert", "Einstellungen");return;}
 if(!integer(d,REV,&rev)||(uint32_t)rev!=revision){phone_push(rid,-2,"Daten geändert. Bitte neu laden.");return;}
 if(storage_error){phone_push(rid,-3,"Speicherfehler. Bitte Uhr-App neu starten.");return;}
 if(!integer(d,ID,&id)){phone_push(rid,-1,"Termin-ID fehlt");return;}
 int i=id?find_id(entries,id):free_slot(entries);
 if(i<0){phone_push(rid,-1,id?"Termin nicht mehr vorhanden":"Alle 24 Terminplätze belegt");return;}
 if(op==2){
  if(!id){phone_push(rid,-1,"Termin-ID fehlt");return;}Entry old=entries[i];entries[i].active=0;
  if(!store_entry(i)){entries[i]=old;phone_push(rid,-3,"Löschen nicht gespeichert");return;}
 }else if(op==1){
  int32_t c,k,w,l1,l2,u,t,extra=0;integer(d,EXTRA,&extra);
  if(!integer(d,CLS,&c)||!integer(d,KIND,&k)||!integer(d,WHEN,&w)||!integer(d,LEAD1,&l1)||!integer(d,LEAD2,&l2)||!integer(d,UNITS,&u)||!integer(d,TOPIC,&t)||c<0||c>15||k<0||k>6||u<1||u>12||l1<15||l1>2880||l2<0||l2>2880||t<0||t>255||extra<0||extra>40){phone_push(rid,-1,"Ungültige Termindaten");return;}
  Entry next={.id=id?(uint32_t)id:allocate_id(),.token=rid,.when=w,.lead={l1,l2},.cls=c,.kind=k,.units=u,.topic=t,.active=1,.extra_minutes=extra};
  if(!next.id||!entry_valid(&next)||w<=time(NULL)||(l2&&l1==l2)){phone_push(rid,-1,"Termin oder Erinnerungen ungültig");return;}
  // Reminders whose lead has already passed are skipped; the later reminder remains active.
  for(int n=0;n<2;n++)if(next.lead[n]&&w-(int32_t)next.lead[n]*60<=time(NULL))next.flags|=1<<n;
  Entry old=entries[i];entries[i]=next;if(!store_entry(i)){entries[i]=old;phone_push(rid,-3,"Termin nicht gespeichert");return;}
 }else{phone_push(rid,-1,"Unbekannte Aktion");return;}
 store_request(rid);store_revision();state_changed();phone_push(rid,storage_error?-3:0,storage_error?"Speicherfehler: Stand auf Uhr prüfen":NULL);
 show_status(op==2?"Termin gelöscht":"Termin gespeichert","Handy-Eingabe");
}
void phone_init(void) {app_message_register_inbox_received(inbox);app_message_register_outbox_sent(sent);app_message_register_outbox_failed(failed);app_message_open(512,1024);}
void phone_deinit(void) {app_message_deregister_callbacks();}
