#include "store.h"
Config cfg={-1,0};
Entry entries[MAX_ENTRIES];
uint16_t counts[16][6];
uint32_t topics[16],revision=1,last_request;
uint8_t profiles[16];
bool storage_error;
uint8_t language;
PracticeProgress practice[16];
bool store_language(uint8_t value) {if(value>63)return false;if(persist_write_int(26,value)<0){storage_error=true;return false;}language=value;return true;}
static uint32_t sequence;
static bool put(int key,const void *p,size_t n) {bool ok=persist_write_data(key,p,n)==(int)n;if(!ok)storage_error=true;return ok;}
static bool get_record(int key,void *p,size_t n) {return persist_get_size(key)==(int)n&&persist_read_data(key,p,n)==(int)n;}
bool store_revision(void) {revision++;return put(REVISION_KEY,&revision,sizeof(revision));}
bool store_request(uint32_t request) {last_request=request;return put(REQUEST_KEY,&last_request,sizeof(last_request));}
bool store_entry(int i) {return put(200+i,&entries[i],sizeof(Entry));}
bool store_config(void) {profiles[cfg.cls]=cfg.profile;return put(CONFIG_KEY,&cfg,sizeof(cfg))&&put(PROFILES_KEY,profiles,sizeof(profiles));}
bool store_progress(int c) {return put(100+c,counts[c],sizeof(counts[c]))&&put(150+c,&topics[c],sizeof(topics[c]))&&put(170+c,&practice[c],sizeof(practice[c]));}
uint32_t allocate_id(void) {sequence++;if(!put(SEQUENCE_KEY,&sequence,sizeof(sequence)))return 0;return sequence;}
static bool recover_booking(void) {
 Booking b={0};if(!get_record(BOOKING_KEY,&b,sizeof(b))){if(!get_record(BOOKING_KEY,&b,16))return true; if(b.cls<16){b.remainder=practice[b.cls].remainder[b.counter<4?b.counter:4];b.exercise_units=practice[b.cls].exercise_units;}}
 if(b.cls>=16||b.counter>6){storage_error=true;return false;}
 if(b.counter<6)counts[b.cls][b.counter]=b.counter_value;
 topics[b.cls]=b.topic_mask;
 if(b.counter<4)practice[b.cls].remainder[b.counter]=b.remainder;
 if(b.counter==6)practice[b.cls].remainder[4]=b.remainder;
 practice[b.cls].exercise_units=b.exercise_units;
 if(!store_progress(b.cls))return false;
 int i=find_id(entries,b.id);
 if(i>=0){entries[i].active=0;if(!store_entry(i))return false;}
 if(b.token&&!store_request(b.token))return false;
 if(!store_revision())return false;
 if(persist_delete(BOOKING_KEY)<0){storage_error=true;return false;}
 return true;
}
unsigned topic_units(int cls,int counter) {
 if(cls<0||cls>=16||(counter!=4&&counter!=5))return 0;
 unsigned result=0;for(int t=counter==4?0:12;t<(counter==4?12:MAX_TOPICS);t++)if(topics[cls]&(1u<<t))result++;
 return result;
}
unsigned extra_minutes_limit(int cls,int counter){
 if(cls<0||cls>=16||counter<0||counter>6||counter==4||counter==5)return 0;
 unsigned current=counter<4?counts[cls][counter]:practice[cls].exercise_units;
 unsigned limit=current<999?(999-current)*45+40:40;return limit<540?limit:540;
}
bool set_extra_minutes(int cls,int counter,unsigned minutes){
 if(cls<0||cls>=16||counter<0||counter>6||counter==4||counter==5||minutes>extra_minutes_limit(cls,counter)||minutes%5||storage_error)return false;
 unsigned units=minutes/45;
 Booking b={.counter_value=counter<4?counts[cls][counter]+units:0,.cls=cls,.counter=counter,.topic_mask=topics[cls],.remainder=minutes%45,.exercise_units=practice[cls].exercise_units+(counter==6?units:0)};
 if(!put(BOOKING_KEY,&b,sizeof(b)))return false;
 return recover_booking();
}

bool set_progress_count(int cls,int counter,unsigned value) {
 if(cls<0||cls>=16||counter<0||counter>=6||value>999||value<topic_units(cls,counter)||storage_error)return false;
 // Checkbox credit is protected. A manual correction only changes the excess above it.
 Booking b={.counter_value=value,.cls=cls,.counter=counter,.topic_mask=topics[cls],.remainder=counter<4?practice[cls].remainder[counter]:0,.exercise_units=practice[cls].exercise_units};
 if(!put(BOOKING_KEY,&b,sizeof(b)))return false;
 return recover_booking();
}
bool toggle_topic(int cls,int topic) {
 if(cls<0||cls>=16||topic<0||topic>=MAX_TOPICS||storage_error)return false;
 int counter=topic<12?4:5;uint32_t bit=1u<<topic;bool checked=(topics[cls]&bit)!=0;
 if(!checked&&counts[cls][counter]>=999)return false;
 unsigned count=counts[cls][counter];count=checked?(count?count-1:0):(count<999?count+1:999);
 Booking b={.id=0,.counter_value=count,.cls=cls,.counter=counter,.topic_mask=topics[cls]^bit,.exercise_units=practice[cls].exercise_units};
 // Reuse the write-ahead record so the checkbox and counter commit together after a restart.
 if(!put(BOOKING_KEY,&b,sizeof(b)))return false;
 return recover_booking();
}
bool book_entry(int i) {
 if(i<0||i>=MAX_ENTRIES||!entries[i].active||end_time(&entries[i])>time(NULL))return false;
 Entry *e=&entries[i];int k=kind_counter(e->kind);int slot=k>=0?k:4;
 unsigned extra=e->kind<5?practice[e->cls].remainder[slot]+e->extra_minutes:0;
 unsigned units=e->units+extra/45;
 // A checked topic already contributes one unit, whether checked manually or by a lesson.
 if(e->kind>=5&&e->topic!=NO_TOPIC&&(topics[e->cls]&(1u<<e->topic))&&units)units--;
 unsigned total=k>=0?counts[e->cls][k]+units:0;
 unsigned exercise=practice[e->cls].exercise_units+(k<0?units:0);
 Booking b={.id=e->id,.token=0,.counter_value=total>999?999:total,.cls=e->cls,.counter=k>=0?k:6,.topic_mask=topics[e->cls],.remainder=extra%45,.exercise_units=exercise>999?999:exercise};
 if(e->topic!=NO_TOPIC)b.topic_mask|=1u<<e->topic;
 // Write-ahead record makes a crash between count and appointment writes idempotent.
 if(!put(BOOKING_KEY,&b,sizeof(b)))return false;
 return recover_booking();
}
bool store_load(void) {
 int32_t stored_language=persist_read_int(26);language=stored_language>=0&&stored_language<=63?(uint8_t)stored_language:0;
 get_record(CONFIG_KEY,&cfg,sizeof(cfg));if(cfg.cls<0||cfg.cls>=16){cfg.cls=-1;cfg.profile=0;}
 for(int c=0;c<16;c++){get_record(100+c,counts[c],sizeof(counts[c]));get_record(150+c,&topics[c],sizeof(topics[c]));get_record(170+c,&practice[c],sizeof(practice[c]));}
 get_record(PROFILES_KEY,profiles,sizeof(profiles));get_record(SEQUENCE_KEY,&sequence,sizeof(sequence));get_record(REVISION_KEY,&revision,sizeof(revision));get_record(REQUEST_KEY,&last_request,sizeof(last_request));
 if(persist_read_int(VERSION_KEY)==MODEL_VERSION){
  for(int i=0;i<MAX_ENTRIES;i++){get_record(200+i,&entries[i],sizeof(Entry));if(entries[i].active&&!entry_valid(&entries[i])){storage_error=true;entries[i].active=0;}}
 }else{
  typedef struct {int32_t when;uint16_t lead,units;uint8_t kind,active,notified,pad;} Old;
  Old old={0};get_record(2,&old,sizeof(old));
  if(cfg.cls>=0)profiles[cfg.cls]=cfg.profile;
  if(old.active&&cfg.cls>=0){entries[0]=(Entry){.id=allocate_id(),.when=old.when,.lead={old.lead,0},.cls=cfg.cls,.kind=old.kind,.units=old.units,.topic=NO_TOPIC,.flags=old.notified?REM1:0,.active=1};if(!entry_valid(&entries[0]))entries[0].active=0;}
  // Complete every new record before marking migration complete; old values remain untouched.
  for(int i=0;i<MAX_ENTRIES;i++)if(!store_entry(i))return false;
  if(cfg.cls>=0&&!store_config())return false;
  if(persist_write_int(VERSION_KEY,MODEL_VERSION)<0){storage_error=true;return false;}
  wakeup_cancel_all();persist_delete(WAKE_KEY);
 }
 if(!recover_booking())return false;
 // Retire the 3.5 global mute by copying Off into existing appointments, once.
 if(persist_get_size(29)==4&&persist_read_int(29)==0){
  bool changed=false;for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active&&entries[i].lead[1]){entries[i].lead[1]=0;if(!store_entry(i))return false;changed=true;}
  if(changed&&!store_revision())return false;
  if(persist_write_int(29,1)<0){storage_error=true;return false;}
 }

 if(persist_read_int(27)!=1){
  bool changed=false;
  for(int c=0;c<16;c++){
   unsigned gs=0,zs=0;for(int t=0;t<MAX_TOPICS;t++)if(topics[c]&(1u<<t)){if(t<12)gs++;else zs++;}
   bool update=false;if(counts[c][4]<gs){counts[c][4]=gs;update=true;}if(counts[c][5]<zs){counts[c][5]=zs;update=true;}
   if(update){if(!store_progress(c))return false;changed=true;}
  }
  if(changed&&!store_revision())return false;
  if(persist_write_int(27,1)<0){storage_error=true;return false;}
 }
 // Repair old manual corrections without erasing the user's checkmarks.
 for(int c=0;c<16;c++)for(int k=4;k<6;k++){
  unsigned checked=topic_units(c,k);
  if(checked>counts[c][k]&&!set_progress_count(c,k,checked))return false;
 }
 return true;
}
