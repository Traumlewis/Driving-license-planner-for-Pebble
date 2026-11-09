/* Lossless record encoding experiment, retaining the live store's journal and keys. */
#include "compact_storage.h"
#include <string.h>

static unsigned read16(const uint8_t *p){return p[0]|(unsigned)p[1]<<8;}
static uint32_t read32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void write16(uint8_t *p,unsigned v){p[0]=v;p[1]=v>>8;}
static void write32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static bool is_entry(int key){return key>=200&&key<224;}
static bool is_counts(int key){return key>=100&&key<116;}
static bool is_topics(int key){return key>=150&&key<166;}
static bool is_practice(int key){return key>=170&&key<186;}
static bool zero(const uint8_t *p,size_t n){for(size_t i=0;i<n;i++)if(p[i])return false;return true;}
static int packed_write(int key,const uint8_t *data,unsigned size,unsigned original){return persist_write_data(key,data,size)==(int)size?(int)original:-1;}
static int remove_record(int key,unsigned original){if(persist_get_size(key)<0)return original;return persist_delete(key)>=0?(int)original:-1;}

int compact_write_data(int key,const void *data,size_t n){
 uint8_t out[32];
 if(is_entry(key)&&n==sizeof(Entry)){
  Entry value;memcpy(&value,data,n);const Entry *e=&value;if(!e->active)return remove_record(key,n);
  if(!entry_valid(e))return persist_write_data(key,data,n);
  unsigned topic=e->topic==NO_TOPIC?31:e->topic;
  uint32_t meta=e->cls|(uint32_t)e->kind<<4|(uint32_t)(e->units-1)<<7|(uint32_t)topic<<11|(uint32_t)e->flags<<16|(uint32_t)(e->extra_minutes/5)<<24;
  if(e->token)meta|=1u<<28;
  if(e->snooze)meta|=1u<<29;
  if(e->review)meta|=1u<<30;
  out[0]=0xd1;write32(out+1,meta);write32(out+5,e->id);write32(out+9,(uint32_t)e->when);out[13]=e->lead[0]/15;out[14]=e->lead[1]/15;
  unsigned size=15;if(e->token){write32(out+size,e->token);size+=4;}if(e->snooze){write32(out+size,(uint32_t)e->snooze);size+=4;}if(e->review){write32(out+size,(uint32_t)e->review);size+=4;}
  return packed_write(key,out,size,n);
 }
 if(is_counts(key)&&n==12){
  if(zero(data,n))return remove_record(key,n);
  uint16_t values[6];memcpy(values,data,n);uint64_t bits=UINT64_C(0xa)<<60;
  for(unsigned i=0;i<6;i++){if(values[i]>999)return persist_write_data(key,data,n);bits|=(uint64_t)values[i]<<(10*i);}
  for(unsigned i=0;i<8;i++)out[i]=bits>>(8*i);
  return packed_write(key,out,8,n);
 }
 if(is_topics(key)&&n==4&&zero(data,n))return remove_record(key,n);
 if(is_practice(key)&&n==sizeof(PracticeProgress)){
  if(zero(data,n))return remove_record(key,n);
  PracticeProgress value;memcpy(&value,data,n);const PracticeProgress *p=&value;if(p->exercise_units>999||p->pad)return persist_write_data(key,data,n);
  uint32_t bits=0x80000000u|p->exercise_units;
  for(unsigned i=0;i<5;i++){if(p->remainder[i]>40||p->remainder[i]%5)return persist_write_data(key,data,n);bits|=(uint32_t)(p->remainder[i]/5)<<(10+4*i);}
  write32(out,bits);return packed_write(key,out,4,n);
 }
 if(key==CONFIG_KEY&&n==sizeof(Config)){
  Config value;memcpy(&value,data,n);const Config *c=&value;if(c->cls < -1||c->cls>15||c->profile<0||c->profile>63)return persist_write_data(key,data,n);
  write16(out,0xa800u|(unsigned)(c->cls+1)|(unsigned)c->profile<<5);return packed_write(key,out,2,n);
 }
 if(key==PROFILES_KEY&&n==16){
  if(zero(data,n))return remove_record(key,n);
  const uint8_t *p=data;memset(out,0,8);for(unsigned i=0;i<16;i++){if(p[i]>15)return persist_write_data(key,data,n);out[i/2]|=p[i]<<((i%2)*4);}
  return packed_write(key,out,8,n);
 }
 return persist_write_data(key,data,n);
}

int compact_get_size(int key){
 int n=persist_get_size(key);
 if(is_entry(key)&&n>=15&&n<=27)return sizeof(Entry);
 if(is_counts(key)&&n==8)return 12;
 if(is_practice(key)&&n==4)return sizeof(PracticeProgress);
 if(key==CONFIG_KEY&&n==2)return sizeof(Config);
 if(key==PROFILES_KEY&&n==8)return 16;
 return n;
}

int compact_read_data(int key,void *data,size_t n){
 int size=persist_get_size(key);uint8_t raw[32];
 if(size==(int)n)return persist_read_data(key,data,n);
 if(size<0||size>32||compact_get_size(key)!=(int)n||persist_read_data(key,raw,size)!=size)return -1;
 if(is_entry(key)&&n==sizeof(Entry)){
  if(raw[0]!=0xd1)return -1;
  uint32_t meta=read32(raw+1);if(meta&0x80000000u)return -1;
  unsigned needed=15+((meta>>28)&1)*4+((meta>>29)&1)*4+((meta>>30)&1)*4;if(needed!=(unsigned)size)return -1;
  unsigned topic=(meta>>11)&31;Entry e={.cls=meta&15,.kind=(meta>>4)&7,.units=((meta>>7)&15)+1,.topic=topic==31?NO_TOPIC:topic,.flags=(meta>>16)&255,.extra_minutes=((meta>>24)&15)*5,.active=1,.id=read32(raw+5),.when=(int32_t)read32(raw+9),.lead={raw[13]*15,raw[14]*15}};
  unsigned cursor=15;if(meta&(1u<<28)){e.token=read32(raw+cursor);cursor+=4;}if(meta&(1u<<29)){e.snooze=(int32_t)read32(raw+cursor);cursor+=4;}if(meta&(1u<<30))e.review=(int32_t)read32(raw+cursor);
  if(!entry_valid(&e))return -1;
  memcpy(data,&e,n);return n;
 }
 if(is_counts(key)&&n==12){
  uint64_t bits=0;for(unsigned i=0;i<8;i++)bits|=(uint64_t)raw[i]<<(8*i);if(bits>>60!=0xa)return -1;
  uint16_t values[6];for(unsigned i=0;i<6;i++){values[i]=(bits>>(10*i))&1023;if(values[i]>999)return -1;}memcpy(data,values,n);return n;
 }
 if(is_practice(key)&&n==sizeof(PracticeProgress)){
  uint32_t bits=read32(raw);if(bits>>30!=2)return -1;PracticeProgress p={.exercise_units=bits&1023};if(p.exercise_units>999)return -1;
  for(unsigned i=0;i<5;i++){unsigned v=(bits>>(10+4*i))&15;if(v>8)return -1;p.remainder[i]=v*5;}memcpy(data,&p,n);return n;
 }
 if(key==CONFIG_KEY&&n==sizeof(Config)){
  unsigned bits=read16(raw);if((bits&0xf800)!=0xa800||(bits&31)>16)return -1;Config c={(int16_t)((int)(bits&31)-1),(int16_t)((bits>>5)&63)};memcpy(data,&c,n);return n;
 }
 if(key==PROFILES_KEY&&n==16){uint8_t values[16];for(unsigned i=0;i<16;i++)values[i]=(raw[i/2]>>((i%2)*4))&15;memcpy(data,values,n);return n;}
 return -1;
}

bool compact_migrate_existing(void){
 uint8_t data[32];
 for(int key=0;key<300;key++){
  unsigned n=key==CONFIG_KEY?sizeof(Config):key==PROFILES_KEY?16:is_entry(key)?sizeof(Entry):is_counts(key)?12:is_topics(key)?4:is_practice(key)?sizeof(PracticeProgress):0;
  if(!n||compact_get_size(key)<0)continue;
  if(compact_read_data(key,data,n)!=(int)n||compact_write_data(key,data,n)!=(int)n)return false;
 }
 return true;
}
