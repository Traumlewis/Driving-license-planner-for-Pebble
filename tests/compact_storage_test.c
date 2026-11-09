/* Native store logic, simulated SDK persistence: migration, restart and rollback. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "store.h"
#include "compact_storage.h"
static unsigned char disk[300][256],saved[300][256];
static int sizes[300],saved_sizes[300],fail_after=-1,mutations;
static unsigned used(void){unsigned n=0;for(int i=0;i<300;i++)n+=sizes[i];return n;}
static bool blocked(void){int at=mutations++;return fail_after>=0&&at>=fail_after;}
int persist_get_size(int k){assert(k>=0&&k<300);return sizes[k]?sizes[k]:-1;}
int persist_read_data(int k,void *p,size_t n){assert(k>=0&&k<300);if(sizes[k]!=(int)n)return -1;memcpy(p,disk[k],n);return n;}
int persist_write_data(int k,const void *p,size_t n){assert(k>=0&&k<300&&n<=256);if(blocked()||used()-sizes[k]+n+2567>4096)return -1;memcpy(disk[k],p,n);sizes[k]=n;return n;}
int persist_delete(int k){assert(k>=0&&k<300);if(blocked()||!sizes[k])return -1;sizes[k]=0;return 0;}
int persist_write_int(int k,int32_t v){return persist_write_data(k,&v,4);}
int32_t persist_read_int(int k){int32_t v=0;persist_read_data(k,&v,4);return v;}
void wakeup_cancel_all(void){}
static bool boot(void){memset(entries,0,sizeof(entries));memset(counts,0,sizeof(counts));memset(topics,0,sizeof(topics));memset(profiles,0,sizeof(profiles));memset(practice,0,sizeof(practice));cfg=(Config){-1,0};language=0;revision=1;last_request=0;storage_error=false;return store_load();}
typedef struct {Config config;Entry items[24];uint16_t totals[16][6];uint32_t checked[16];PracticeProgress extra[16];uint8_t owner[16],lang;uint32_t rev,request;} State;
static State state(void){State s={0};s.config=cfg;memcpy(s.items,entries,sizeof(entries));for(int i=0;i<24;i++)if(!s.items[i].active)memset(s.items+i,0,sizeof(Entry));memcpy(s.totals,counts,sizeof(counts));memcpy(s.checked,topics,sizeof(topics));memcpy(s.extra,practice,sizeof(practice));memcpy(s.owner,profiles,sizeof(profiles));s.lang=language;s.rev=revision;s.request=last_request;return s;}
static void same(const State *a,bool replay){State b=state();assert(!memcmp(&a->config,&b.config,sizeof(Config)));assert(!memcmp(a->items,b.items,sizeof(entries)));assert(!memcmp(a->totals,b.totals,sizeof(counts)));assert(!memcmp(a->checked,b.checked,sizeof(topics)));assert(!memcmp(a->extra,b.extra,sizeof(practice)));assert(!memcmp(a->owner,b.owner,sizeof(profiles)));assert(a->lang==b.lang&&(replay?b.rev>=a->rev:a->rev==b.rev)&&a->request==b.request);}
static void save(void){memcpy(saved,disk,sizeof(disk));memcpy(saved_sizes,sizes,sizeof(sizes));}
static void restore(void){memcpy(disk,saved,sizeof(disk));memcpy(sizes,saved_sizes,sizeof(sizes));fail_after=-1;mutations=0;}
static void seed(bool pending){
 memset(disk,0,sizeof(disk));memset(sizes,0,sizeof(sizes));fail_after=-1;mutations=0;
 cfg=(Config){4,1};for(int c=0;c<16;c++){profiles[c]=c%4;for(int k=0;k<6;k++)counts[c][k]=999;topics[c]=0x3fffffff;practice[c]=(PracticeProgress){.exercise_units=999,.remainder={40,40,40,40,40}};}
 profiles[4]=1;
 for(int i=0;i<24;i++){int cls=i%16,kind=cls==14?5:i%7;entries[i]=(Entry){.id=100+i,.token=0xf0000000u-i,.when=1900000000+i*7200,.snooze=1900000100+i*7200,.review=1900000200+i*7200,.lead={2880,2865},.cls=cls,.kind=kind,.units=kind>=5?12:11,.topic=kind==5?0:kind==6?12:NO_TOPIC,.flags=255,.active=1,.extra_minutes=kind<5?40:0};assert(entry_valid(entries+i));assert(persist_write_data(200+i,entries+i,sizeof(Entry))==sizeof(Entry));}
 for(int c=0;c<16;c++){assert(persist_write_data(100+c,counts[c],12)==12);assert(persist_write_data(150+c,topics+c,4)==4);assert(persist_write_data(170+c,practice+c,8)==8);}
 assert(persist_write_data(CONFIG_KEY,&cfg,sizeof(cfg))==sizeof(cfg));assert(persist_write_data(PROFILES_KEY,profiles,16)==16);
 assert(persist_write_int(VERSION_KEY,MODEL_VERSION)==4);assert(persist_write_int(SEQUENCE_KEY,200)==4);assert(persist_write_int(REVISION_KEY,5)==4);assert(persist_write_int(REQUEST_KEY,17)==4);assert(persist_write_int(26,3)==4);assert(persist_write_int(27,1)==4);assert(persist_write_int(29,1)==4);language=3;revision=5;last_request=17;
 if(pending){Booking b={.id=entries[0].id,.token=44,.counter_value=999,.cls=0,.counter=0,.topic_mask=topics[0],.remainder=35,.exercise_units=999};assert(persist_write_data(BOOKING_KEY,&b,sizeof(b))==sizeof(b));}
}
static unsigned migration_cuts(bool pending){
 seed(pending);save();mutations=0;assert(boot());State expected=state();unsigned steps=mutations;
 for(unsigned cut=0;cut<=steps;cut++){restore();mutations=0;fail_after=cut;bool completed=boot();fail_after=-1;if(!completed)assert(storage_error);assert(boot());same(&expected,pending);mutations=0;assert(boot());same(&expected,pending);assert(!mutations);}
 return steps+1;
}
static unsigned restore_cuts(void){
 seed(false);assert(boot());State expected=state();save();mutations=0;assert(compact_restore_legacy());unsigned steps=mutations;
 for(unsigned cut=0;cut<=steps;cut++){restore();fail_after=cut;compact_restore_legacy();fail_after=-1;assert(boot());same(&expected,false);assert(compact_restore_legacy());assert(store_compact_records()==0);Config raw;assert(persist_read_data(CONFIG_KEY,&raw,sizeof(raw))==sizeof(raw)&&!memcmp(&raw,&expected.config,sizeof(raw)));for(int i=0;i<24;i++){Entry e;assert(persist_read_data(200+i,&e,sizeof(e))==sizeof(e));assert(!memcmp(&e,expected.items+i,sizeof(e)));}assert(boot());same(&expected,false);}
 return steps+1;
}
static void corrupt_records(void){
 seed(false);assert(boot());save();
 for(int kind=0;kind<4;kind++){restore();if(kind==0)disk[200][0]^=1;if(kind==1)sizes[200]=18;if(kind==2)disk[100][7]^=0x10;if(kind==3){memset(disk[BOOKING_KEY],0,19);sizes[BOOKING_KEY]=19;}unsigned old=used();unsigned char previous[256];memcpy(previous,disk[200],sizeof(previous));mutations=0;assert(!boot()&&storage_error);assert(!mutations&&used()==old&&!memcmp(previous,disk[200],sizeof(previous)));assert(!store_entry(0));assert(!store_config());assert(!mutations);}
 restore();assert(boot());
}
static uint32_t random_state=71;
static uint32_t random32(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return random_state;}
static void roundtrips(void){
 seed(false);assert(boot());
 for(unsigned t=0;t<12000;t++){
  unsigned cls=random32()%16,kind=cls==14?5:random32()%7;Entry e={.id=random32(),.token=t%3?random32():0,.when=1000000000+(int32_t)(random32()%1000000000),.lead={15*(1+random32()%192),15*(random32()%193)},.cls=cls,.kind=kind,.units=1+random32()%11,.topic=kind==5?random32()%12:kind==6?12+random32()%18:NO_TOPIC,.flags=random32()&255,.active=1,.extra_minutes=kind<5?5*(random32()%9):0};
  if(t%2)e.snooze=(int32_t)random32();
  if(t%5)e.review=(int32_t)random32();
  assert(entry_valid(&e));Entry got;assert(compact_write_data(200,&e,sizeof(e))==sizeof(e));assert(compact_read_data(200,&got,sizeof(got))==sizeof(got)&&!memcmp(&e,&got,sizeof(e)));
  uint16_t c[6],read[6];for(int i=0;i<6;i++)c[i]=random32()%1000;assert(compact_write_data(100,c,12)==12);assert(compact_read_data(100,read,12)==12&&!memcmp(c,read,12));
 }
 uint16_t legacy[6]={65535,2000,4,0,0,0},got[6];assert(compact_write_data(100,legacy,12)==12&&sizes[100]==12);assert(compact_read_data(100,got,12)==12&&!memcmp(legacy,got,12));
 PracticeProgress p={.exercise_units=1001,.remainder={1,2,3,4,5},.pad=7},q;assert(compact_write_data(170,&p,8)==8&&sizes[170]==8);assert(compact_read_data(170,&q,8)==8&&!memcmp(&p,&q,8));
}
int main(void){
 unsigned migration=migration_cuts(false)+migration_cuts(true),rollback=restore_cuts();corrupt_records();roundtrips();seed(false);unsigned old=used();assert(boot());unsigned current=used();assert(current<old&&store_bytes_used()==current&&store_quota_bytes()==4096&&store_uses_compact());
 seed(false);for(int i=0;i<24;i++){entries[i].snooze=entries[i].review=0;entries[i].flags=0;assert(persist_write_data(200+i,entries+i,sizeof(Entry))==sizeof(Entry));}unsigned normal_old=used();assert(boot());unsigned normal=used();assert(normal_old-normal==450&&old-current==258);
 printf("PASS production compact store: %u migration interruption boundaries, %u rollback boundaries, 12000 entry/counter roundtrips, read-only corruption failure, no repeated startup writes; %u -> %u persisted app bytes\n",migration,rollback,old,current);printf("PASS full regular appointments: %u -> %u persisted app bytes (%u saved)\n",normal_old,normal,normal_old-normal);return 0;
}
