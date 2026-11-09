/* Appended to a temporary copy of the original store_test.c by the experiment. */
#ifdef COMPACT
#include "compact_storage.h"
static uint32_t random_state=71;
static uint32_t random32(void){random_state^=random_state<<13;random_state^=random_state>>17;random_state^=random_state<<5;return random_state;}
#endif
static void fresh(void){
 memset(disk,0,sizeof(disk));memset(sizes,0,sizeof(sizes));fail_key=-1;mutation_limit=-1;mutations=0;external_bytes=0;revision=1;last_request=0;
 persist_write_int(SEQUENCE_KEY,1);persist_write_int(REVISION_KEY,1);persist_write_int(REQUEST_KEY,0);reboot();cfg=(Config){4,0};assert(store_config());assert(store_language(0));
 persist_write_int(WAKE_KEY,7);persist_write_int(28,1900000600);persist_write_int(29,1);
}
static void scenario(int mode){
 fresh();
 if(mode==1){counts[4][0]=2;counts[4][1]=1;counts[4][4]=5;counts[4][5]=1;topics[4]=3;practice[4].exercise_units=3;practice[4].remainder[0]=10;assert(store_progress(4));}
 if(mode>=2){
  for(int c=0;c<16;c++){for(int k=0;k<6;k++)counts[c][k]=999;topics[c]=0x3fffffffu;practice[c].exercise_units=999;for(int k=0;k<5;k++)practice[c].remainder[k]=40;profiles[c]=c%4;assert(store_progress(c));}
  cfg.profile=1;assert(store_config());
 }
 int n=mode==0?0:mode==1?3:24;
 for(int i=0;i<n;i++){
  int cls=mode==1?4:i%16,kind=cls==14?5:i%7;
  Entry e={.id=allocate_id(),.token=0xf0000000u-i,.when=1900000000+i*7200,.lead={2880,2865},.cls=cls,.kind=kind,.units=kind>=5?12:11,.topic=kind==5?0:kind==6?12:NO_TOPIC,.flags=mode==3?255:0,.active=1,.extra_minutes=kind<5?40:0};
  if(mode==3){e.snooze=e.when+100;e.review=e.when+200;}
  assert(entry_valid(&e));entries[i]=e;assert(store_entry(i));
 }
 assert(store_request(87));assert(store_revision());reboot();
}

typedef struct {Config config;Entry appointments[24];uint16_t totals[16][6];uint32_t checked[16];PracticeProgress extra[16];uint8_t owners[16],lang;uint32_t rev,request;} State;
static State state(void){State s={.config=cfg,.lang=language,.rev=revision,.request=last_request};memcpy(s.appointments,entries,sizeof(entries));for(int i=0;i<24;i++)if(!s.appointments[i].active)memset(&s.appointments[i],0,sizeof(Entry));memcpy(s.totals,counts,sizeof(counts));memcpy(s.checked,topics,sizeof(topics));memcpy(s.extra,practice,sizeof(practice));memcpy(s.owners,profiles,sizeof(profiles));return s;}
static void same_state(const State *a){State b=state();assert(!memcmp(&a->config,&b.config,sizeof(Config)));assert(!memcmp(a->appointments,b.appointments,sizeof(entries)));assert(!memcmp(a->totals,b.totals,sizeof(counts)));assert(!memcmp(a->checked,b.checked,sizeof(topics)));assert(!memcmp(a->extra,b.extra,sizeof(practice)));assert(!memcmp(a->owners,b.owners,sizeof(profiles)));assert(a->lang==b.lang&&a->rev==b.rev&&a->request==b.request);}
static unsigned char saved_disk[300][256];static int saved_sizes[300];
static void save_disk(void){memcpy(saved_disk,disk,sizeof(disk));memcpy(saved_sizes,sizes,sizeof(sizes));}
static void restore_disk(void){memcpy(disk,saved_disk,sizeof(disk));memcpy(sizes,saved_sizes,sizeof(sizes));fail_key=-1;mutation_limit=-1;mutations=0;}

static unsigned booking_faults(void){
 fresh();counts[4][0]=7;topics[4]=1;practice[4].exercise_units=2;practice[4].remainder[0]=25;assert(store_progress(4));
 entries[0]=past(1);entries[0].units=1;entries[0].extra_minutes=20;assert(store_entry(0));save_disk();
 external_bytes=2567;mutations=0;assert(book_entry(0));int operations=mutations;
 for(int cut=0;cut<=operations;cut++){
  restore_disk();reboot();mutations=0;mutation_limit=cut;bool success=book_entry(0);mutation_limit=-1;bool pending=persist_get_size(BOOKING_KEY)>=0;
  reboot();if(pending||success){assert(counts[4][0]==9&&practice[4].remainder[0]==0&&!entries[0].active);}else{assert(counts[4][0]==7&&practice[4].remainder[0]==25&&entries[0].active);}
  uint16_t total=counts[4][0];reboot();assert(counts[4][0]==total);
 }
 return operations+1;
}

#ifdef COMPACT
static unsigned migration_faults(bool pending_booking){
 scenario(3);
 /* Simulate an existing installation with the original raw record layout. */
 assert(persist_write_data(CONFIG_KEY,&cfg,sizeof(cfg))==sizeof(cfg));assert(persist_write_data(PROFILES_KEY,profiles,sizeof(profiles))==sizeof(profiles));
 for(int i=0;i<24;i++)assert(persist_write_data(200+i,&entries[i],sizeof(Entry))==sizeof(Entry));
 for(int c=0;c<16;c++){assert(persist_write_data(100+c,counts[c],12)==12);assert(persist_write_data(150+c,&topics[c],4)==4);assert(persist_write_data(170+c,&practice[c],8)==8);}
 reboot();external_bytes=2567;
 if(pending_booking){entries[0].when=time(NULL)-100000;assert(persist_write_data(200,&entries[0],sizeof(Entry))==sizeof(Entry));fail_key=200;assert(!book_entry(0));fail_key=-1;assert(persist_get_size(BOOKING_KEY)==sizeof(Booking));}
 save_disk();reboot();State expected=state();restore_disk();mutations=0;assert(compact_migrate_existing());int operations=mutations;
 for(int cut=0;cut<=operations;cut++){
  restore_disk();mutations=0;mutation_limit=cut;compact_migrate_existing();mutation_limit=-1;reboot();same_state(&expected);
  assert(compact_migrate_existing());reboot();same_state(&expected);
 }
 return operations+1;
}

static void roundtrips(void){
 fresh();
 for(unsigned test=0;test<12000;test++){
  unsigned cls=random32()%16,kind=cls==14?5:random32()%7;Entry e={.id=random32(),.token=test%3?random32():0,.when=1000000000+(int32_t)(random32()%1000000000),.lead={15*(1+random32()%192),15*(random32()%193)},.cls=cls,.kind=kind,.units=1+random32()%11,.topic=kind==5?(random32()%2?NO_TOPIC:random32()%12):kind==6?(random32()%2?NO_TOPIC:12+random32()%18):NO_TOPIC,.flags=random32()&255,.active=1,.extra_minutes=kind<5?5*(random32()%9):0};
  if(test%2)e.snooze=(int32_t)random32();
  if(test%5)e.review=(int32_t)random32();
  assert(entry_valid(&e));Entry decoded={0};
  assert(compact_write_data(200,&e,sizeof(e))==sizeof(e));assert(sizes[200]>=15&&sizes[200]<=27);assert(compact_read_data(200,&decoded,sizeof(decoded))==sizeof(decoded));assert(!memcmp(&decoded,&e,sizeof(e)));
  uint16_t c[6],got[6];for(int i=0;i<6;i++)c[i]=random32()%1000;assert(compact_write_data(100,c,12)==12);assert(compact_read_data(100,got,12)==12);assert(!memcmp(c,got,12));
  PracticeProgress p={.exercise_units=random32()%1000},q={0};for(int i=0;i<5;i++)p.remainder[i]=5*(random32()%9);assert(compact_write_data(170,&p,8)==8);assert(compact_read_data(170,&q,8)==8);assert(!memcmp(&p,&q,8));
 }
 /* Historical values outside current UI ranges must remain raw and lossless. */
 uint16_t old[6]={65535,2000,4,0,0,0},got[6];assert(compact_write_data(100,old,12)==12&&sizes[100]==12);assert(compact_read_data(100,got,12)==12&&!memcmp(old,got,12));
 PracticeProgress p={.exercise_units=1001,.remainder={1,2,3,4,5},.pad=7},q;assert(compact_write_data(170,&p,8)==8&&sizes[170]==8);assert(compact_read_data(170,&q,8)==8&&!memcmp(&p,&q,8));
}
#endif

int main(void){
 assert(original_regression_suite()==0);
 unsigned faults=booking_faults(),migration=0;
 #ifdef COMPACT
 roundtrips();migration=migration_faults(false)+migration_faults(true);
 #endif
 printf("RESULT:{\"bookingFailureBoundaries\":%u,\"migrationFailureBoundaries\":%u,\"scenarios\":[",faults,migration);
 for(int mode=0;mode<4;mode++){
  scenario(mode);int steady=used();int peak=steady+(int)sizeof(Booking);State expected=state();reboot();same_state(&expected);
  /* Full current Spanish LP4 packet including its manifest occupies 2567 B. */
  external_bytes=2567;assert(used()+external_bytes<=4096);assert(store_request(91));assert(store_revision());external_bytes=0;
  printf("%s{\"mode\":%d,\"appBytes\":%d,\"bookingPeakBytes\":%d,\"languageBudgetWithManifest\":%d}",mode?",":"",mode,steady,peak,4096-peak);
 }
 puts("]}");return 0;
}
