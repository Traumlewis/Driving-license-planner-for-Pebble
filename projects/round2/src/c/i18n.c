/* Generated generic decoder. (Idee by Traumlewis | Code by Codex) */
#include "i18n.h"
#include <pebble.h>
#include <string.h>
#include <stdlib.h>
#define APP_VERSION "3.8.49"
#define TEXT_COUNT 296
#define WATCH_SCHEMA_ID 935079838u
#define WATCH_CODEC_ID 4102950692u
#define CODEC_TOKENS 2841
#define CODEC_TREES 3096
static const char *emergency_text(unsigned id){switch(id){
case 1:return "%02d:%02d vorher";
case 2:return "%d Min. | Klasse %s";
case 3:return "%d Minuten";
case 4:return "%d Minuten | Klasse %s";
case 6:return "%d Termin(e)";
case 9:return "%d.%m. · %H:%M";
case 10:return "%s | Klasse %s";
case 34:return "Alarmfehler! Erneut aktivieren";
case 35:return "Alarmstatus";
case 43:return "Alle in 10 Min. erinnern";
case 50:return "Aus";
case 87:return "Dein Termin";
case 95:return "Details & Erinnerungen";
case 96:return "Di";
case 99:return "Do";
case 109:return "Erinnerung schließen";
case 114:return "Erneute Erinnerung";
case 119:return "Sprache / Language";
case 124:return "Fr";
case 145:return "In 10 Minuten";
case 146:return "In 10 Minuten erinnern";
case 173:return "Mi";
case 178:return "Mo";
case 196:return "Praxis | Autobahn";
case 197:return "Praxis | Grundausbildung";
case 198:return "Praxis | Landstraße";
case 199:return "Praxis | Nachtfahrt";
case 200:return "Praxis | Übungsfahrt";
case 207:return "Sa";
case 210:return "So";
case 211:return "Speicherfehler";
case 219:return "Sprachpaket fehlt. Bitte Handy verbinden.";
case 245:return "Termin-Erinnerung";
case 257:return "Theorie | Grundstoff";
case 258:return "Theorie | Zusatzstoff";
case 265:return "Ungültige Anfrage";
case 282:return "Zurück";
default:return "...";}}
/* LP4: one self-describing language packet; shared byte codec and bounded decoding. */
#define PACK_CHUNK_SIZE 128
#define PACK_META_KEY 9000
#define PACK_DATA_KEY 9100
#define MAX_PACK_PARTS 20
#define MAX_PACK_BYTES 2560
#define PACK_HEADER_BYTES 24
/* A failed flash commit may require repair, but never writes application-data keys. */
typedef struct {uint32_t id,crc,size,language;} PackMeta;
typedef struct {uint32_t id,body_crc;uint16_t size,data_start;uint8_t language,name_len;char name[24];} Packet;
static Packet active,incoming_header;
static bool pack_ready;
static uint8_t *incoming;
static uint32_t received_parts;
static uint16_t text_offsets[TEXT_COUNT+1];
static int cached_page=-1;
static uint8_t pack_page[PACK_CHUNK_SIZE];
static char translated[16][96],long_text[2048];
static unsigned translated_slot;
static uint8_t codec_pages[8][64];
static uint16_t codec_page_keys[8];
static uint32_t codec_page_ages[8],codec_age;
static ResHandle codec_resource;
static uint16_t read16(const uint8_t *p){return (uint16_t)p[0]|(uint16_t)p[1]<<8;}
static uint32_t read32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static unsigned pack_parts(unsigned size){return (size+127)/128;}
static uint32_t crc_update(uint32_t crc,const uint8_t *p,unsigned n){for(unsigned i=0;i<n;i++){crc^=p[i];for(int b=0;b<8;b++)crc=crc>>1^((crc&1)?0xedb88320u:0);}return crc;}
static void clear_incoming(void){free(incoming);incoming=NULL;memset(&incoming_header,0,sizeof(incoming_header));received_parts=0;}
static int stored_byte(unsigned offset){unsigned page=offset/128;if(cached_page!=(int)page){int size=persist_get_size(PACK_DATA_KEY+page);if(size<=0||size>128||persist_read_data(PACK_DATA_KEY+page,pack_page,size)!=size)return -1;cached_page=page;}return pack_page[offset%128];}
static int source_byte(const uint8_t *source,unsigned offset,unsigned size){if(offset>=size)return -1;return source?source[offset]:stored_byte(offset);}
static bool header(const uint8_t *data,Packet *p){
 static const uint8_t magic[4]={76,80,52,1};
 if(memcmp(data,magic,4)||read32(data+4)!=WATCH_SCHEMA_ID||read32(data+8)!=WATCH_CODEC_ID)return false;
 memset(p,0,sizeof(*p));p->id=read32(data+12);p->size=read16(data+16);p->language=data[18];p->name_len=data[19];p->body_crc=read32(data+20);
 return p->id&&p->size>24+TEXT_COUNT&&p->size<=MAX_PACK_BYTES&&p->language<=63&&p->name_len>0&&p->name_len<24;
}
static bool codec_pair(unsigned index,uint16_t *a,uint16_t *b){
 unsigned count=CODEC_TOKENS+CODEC_TREES+TEXT_COUNT;if(index>=count)return false;
 unsigned page=index/16,slot=8;uint32_t oldest=0xffffffffu;
 for(unsigned i=0;i<8;i++)if(codec_page_keys[i]==page+1){slot=i;break;}
 if(slot==8){for(unsigned i=0;i<8;i++){if(!codec_page_keys[i]){slot=i;break;}if(codec_page_ages[i]<oldest){oldest=codec_page_ages[i];slot=i;}}
  unsigned offset=page*64,n=count*4-offset;if(n>64)n=64;if(!codec_resource)codec_resource=resource_get_handle(RESOURCE_ID_LANGUAGE_CODEC);
  if(resource_load_byte_range(codec_resource,offset,codec_pages[slot],n)!=n)return false;
  codec_page_keys[slot]=page+1;
 }
 codec_page_ages[slot]=++codec_age;unsigned at=(index%16)*4;*a=read16(codec_pages[slot]+at);*b=read16(codec_pages[slot]+at+2);return true;
}
static bool text_parameters(unsigned id,uint16_t *limit,uint16_t *format){return id&&id<=TEXT_COUNT&&codec_pair(CODEC_TOKENS+CODEC_TREES+id-1,limit,format);}
static bool expand_token(unsigned token,char *out,unsigned *length,unsigned limit){
 uint16_t pending[32];unsigned count=0;pending[count++]=(uint16_t)token;
 while(count){token=pending[--count];if(token<256){if(!token||*length>=limit)return false;out[(*length)++]=(char)token;continue;}
  unsigned index=token-256;uint16_t a,b;if(index>=CODEC_TOKENS||!codec_pair(index,&a,&b)||a>=token||b>=token||count+2>32)return false;pending[count++]=b;pending[count++]=a;
 }
 return true;
}
static bool valid_utf8(const char *text){const uint8_t *p=(const uint8_t *)text;while(*p){uint32_t cp;unsigned n;uint8_t first=*p++;if(first<128)continue;if(first>=0xc2&&first<=0xdf){cp=first&31;n=1;}else if(first>=0xe0&&first<=0xef){cp=first&15;n=2;}else if(first>=0xf0&&first<=0xf4){cp=first&7;n=3;}else return false;unsigned count=n;while(n--){if((*p&0xc0)!=0x80)return false;cp=cp<<6|(*p++&63);}if(cp>0x10ffff||(cp>=0xd800&&cp<=0xdfff)||(count==2&&cp<0x800)||(count==3&&cp<0x10000))return false;}return true;}
static uint16_t format_signature(const char *text,bool *ok){uint32_t hash=2166136261u;*ok=true;while(*text){if(*text++!='%')continue;hash=(hash^'%')*16777619u;while(*text&&strchr("-+# 0123456789.",*text)){hash=(hash^(uint8_t)*text++)*16777619u;}if(!*text||*text=='n'||*text=='p'||!strchr("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%",*text)){*ok=false;return 0;}hash=(hash^(uint8_t)*text++)*16777619u;}return (uint16_t)hash;}
static bool decode_text(const Packet *p,unsigned start,unsigned end,unsigned id,const uint8_t *source,char *out,unsigned capacity){
 if(!id||id>TEXT_COUNT)return false;
 uint16_t allowed,expected;if(!text_parameters(id,&allowed,&expected))return false;
 unsigned bit=start,length=0,limit=allowed;if(limit>=capacity)limit=capacity-1;
 while(bit<end){int node=0;for(unsigned depth=0;node>=0&&depth<32;depth++){uint16_t a,b;if((unsigned)node>=CODEC_TREES||!codec_pair(CODEC_TOKENS+node,&a,&b)||bit>=end)return false;int value=source_byte(source,p->data_start+bit/8,p->size);if(value<0)return false;int next=(value>>(7-bit%8))&1;bit++;node=(int16_t)(next?b:a);}if(node>=0||!expand_token((unsigned)(-node-1),out,&length,limit))return false;}
 out[length]=0;bool ok;if(!valid_utf8(out)||format_signature(out,&ok)!=expected||!ok)return false;return true;
}
static bool read_layout(const uint8_t *source,Packet *p,uint16_t *offsets,bool check_text){
 unsigned cursor=24;for(unsigned i=0;i<p->name_len;i++){int b=source_byte(source,cursor++,p->size);if(b<=0)return false;p->name[i]=(char)b;}p->name[p->name_len]=0;if(!valid_utf8(p->name))return false;
 unsigned bits=0;if(offsets)offsets[0]=0;for(unsigned id=0;id<TEXT_COUNT;id++){unsigned n=0,shift=0;int b;do{b=source_byte(source,cursor++,p->size);if(b<0||shift>14)return false;n|=(unsigned)(b&127)<<shift;shift+=7;}while(b&128);if(!n||bits+n>MAX_PACK_BYTES*8)return false;bits+=n;if(offsets)offsets[id+1]=(uint16_t)bits;}
 p->data_start=cursor;if(cursor+(bits+7)/8!=p->size)return false;
 if(check_text){cursor=24+p->name_len;unsigned start=0;for(unsigned id=1;id<=TEXT_COUNT;id++){unsigned n=0,shift=0;int b;do{b=source_byte(source,cursor++,p->size);if(b<0||shift>14)return false;n|=(unsigned)(b&127)<<shift;shift+=7;}while(b&128);if(!decode_text(p,start,start+n,id,source,long_text,sizeof(long_text)))return false;start+=n;}}
 return true;
}
static bool verify_packet(const uint8_t *source,Packet *p,uint16_t *offsets,bool check_text){
 uint8_t bytes[24];for(unsigned i=0;i<24;i++){int b=source_byte(source,i,p->size);if(b<0)return false;bytes[i]=(uint8_t)b;}
 uint32_t body=0xffffffffu,identity=crc_update(0xffffffffu,bytes,12);identity=crc_update(identity,bytes+16,8);
 for(unsigned i=24;i<p->size;i++){int b=source_byte(source,i,p->size);if(b<0)return false;uint8_t byte=(uint8_t)b;body=crc_update(body,&byte,1);identity=crc_update(identity,&byte,1);}
 return (body^0xffffffffu)==p->body_crc&&(identity^0xffffffffu)==p->id&&read_layout(source,p,offsets,check_text);
}
__attribute__((noinline)) void language_pack_init(void){
 clear_incoming();pack_ready=false;cached_page=-1;memset(codec_page_keys,0,sizeof(codec_page_keys));PackMeta meta;
 if(persist_get_size(PACK_META_KEY)!=(int)sizeof(meta)||persist_read_data(PACK_META_KEY,&meta,sizeof(meta))!=(int)sizeof(meta)||persist_read_data(PACK_DATA_KEY,pack_page,sizeof(pack_page))!=128||!header(pack_page,&active)||meta.id!=active.id||meta.size!=active.size||meta.language!=active.language)return;
 uint32_t crc=0xffffffffu;for(unsigned i=0;i<pack_parts(active.size);i++){unsigned n=active.size-i*128;if(n>128)n=128;if(persist_get_size(PACK_DATA_KEY+i)!=(int)n||persist_read_data(PACK_DATA_KEY+i,pack_page,n)!=(int)n)return;crc=crc_update(crc,pack_page,n);}
 if((crc^0xffffffffu)!=meta.crc||!verify_packet(NULL,&active,text_offsets,false))return;
 language=active.language;pack_ready=true;
}
bool language_pack_ready(void){return pack_ready;}
int language_pack_language(void){return pack_ready?active.language:-1;}
uint32_t language_pack_id(void){return pack_ready?active.id:0;}
unsigned language_pack_size(void){return pack_ready?active.size:0;}
unsigned language_pack_staged(void){return incoming?incoming_header.size:0;}
unsigned language_pack_received(void){return incoming?received_parts:pack_ready?(1u<<pack_parts(active.size))-1:0;}
unsigned language_pack_stored(void){unsigned n=0;int size=persist_get_size(PACK_META_KEY);if(size>0)n+=size;for(int i=0;i<MAX_PACK_PARTS;i++){size=persist_get_size(PACK_DATA_KEY+i);if(size>0)n+=size;}return n;}
uint32_t language_pack_schema(void){return WATCH_SCHEMA_ID;}
uint32_t language_pack_codec(void){return WATCH_CODEC_ID;}
const char *language_pack_name(void){return pack_ready?active.name:"";}
static int hex_value(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}
__attribute__((noinline)) int language_pack_receive(uint32_t identity,unsigned part,unsigned total,const char *hex){
 if(!hex||!total||total>MAX_PACK_PARTS||part>=total)return -1;
 size_t len=strlen(hex);if(!len||len>256||(len&1))return -1;unsigned n=len/2;uint8_t bytes[128];for(unsigned i=0;i<n;i++){int a=hex_value(hex[2*i]),b=hex_value(hex[2*i+1]);if(a<0||b<0)return -1;bytes[i]=(uint8_t)(a*16+b);}
 if(pack_ready&&active.id==identity)return 0;
 if(!incoming||incoming_header.id!=identity){if(part||n!=128)return -1;Packet p;if(!header(bytes,&p)||p.id!=identity||pack_parts(p.size)!=total)return -1;clear_incoming();incoming=malloc(p.size);if(!incoming)return -3;incoming_header=p;}
 if(total!=pack_parts(incoming_header.size)||n!=(part+1==total?incoming_header.size-part*128:128))return -1;
 memcpy(incoming+part*128,bytes,n);received_parts|=1u<<part;if(received_parts!=(1u<<total)-1)return 0;
 Packet next=incoming_header;if(!verify_packet(incoming,&next,NULL,true)){clear_incoming();return -1;}
 uint32_t crc=crc_update(0xffffffffu,incoming,next.size)^0xffffffffu;
 if(persist_get_size(PACK_META_KEY)>=0&&persist_delete(PACK_META_KEY)<0){clear_incoming();return -3;}pack_ready=false;cached_page=-1;
 for(unsigned i=0;i<total;i++){unsigned count=next.size-i*128;if(count>128)count=128;if(persist_write_data(PACK_DATA_KEY+i,incoming+i*128,count)!=(int)count){clear_incoming();return -3;}}
 for(unsigned i=total;i<MAX_PACK_PARTS;i++)if(persist_get_size(PACK_DATA_KEY+i)>=0&&persist_delete(PACK_DATA_KEY+i)<0){clear_incoming();return -3;}
 PackMeta meta={next.id,crc,next.size,next.language};if(persist_write_data(PACK_META_KEY,&meta,sizeof(meta))!=(int)sizeof(meta)){clear_incoming();return -3;}
 if(!read_layout(incoming,&next,text_offsets,false)){clear_incoming();return -1;}active=next;language=active.language;pack_ready=true;clear_incoming();return 0;
}
static void insert_version(char *text,unsigned capacity){char *at;while((at=strstr(text,"{version}"))){size_t n=strlen(APP_VERSION),tail=strlen(at+9);if((size_t)(at-text)+n+tail>=capacity)return;memmove(at+n,at+9,tail+1);memcpy(at,APP_VERSION,n);}}
const char *translate(const char *text){
 if(!text||text[0]!='~'||strlen(text)!=5)return text;
 unsigned id=0;for(unsigned i=1;i<5;i++){int n=hex_value(text[i]);if(n<0)return text;id=id*16+n;}if(!id||id>TEXT_COUNT)return text;
 if(!pack_ready)return emergency_text(id);
 uint16_t limit,format;if(!text_parameters(id,&limit,&format))return emergency_text(id);
 char *out=limit<96?translated[translated_slot++%16]:long_text;unsigned capacity=limit<96?96:sizeof(long_text);
 if(!decode_text(&active,text_offsets[id-1],text_offsets[id],id,NULL,out,capacity)){pack_ready=false;return emergency_text(id);}insert_version(out,capacity);return out;
}

