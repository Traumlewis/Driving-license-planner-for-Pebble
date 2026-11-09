#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "store.h"
static unsigned char disk[300][256];static int sizes[300];static int fail_key=-1;
int persist_write_data(int key,const void *p,size_t n){assert(key>=0&&key<300&&n<=256);if(key==fail_key)return -1;memcpy(disk[key],p,n);sizes[key]=n;return n;}
int persist_read_data(int key,void *p,size_t n){if(sizes[key]!=(int)n)return -1;memcpy(p,disk[key],n);return n;}
int persist_get_size(int key){return sizes[key]?sizes[key]:-1;}
int persist_write_int(int key,int32_t v){return persist_write_data(key,&v,sizeof(v));}
int32_t persist_read_int(int key){int32_t v=0;persist_read_data(key,&v,sizeof(v));return v;}
int persist_delete(int key){if(key==fail_key)return -1;if(!sizes[key])return -1;sizes[key]=0;return 0;}
void wakeup_cancel_all(void){}
static void reboot(void){memset(entries,0,sizeof(entries));memset(counts,0,sizeof(counts));memset(topics,0,sizeof(topics));memset(profiles,0,sizeof(profiles));memset(practice,0,sizeof(practice));language=0;cfg=(Config){-1,0};storage_error=false;assert(store_load());}
static Entry past(int kind){return(Entry){.id=allocate_id(),.when=time(NULL)-20000,.cls=4,.kind=kind,.units=2,.lead={60,30},.topic=NO_TOPIC,.active=1};}
int main(void){
 Config old_cfg={4,0};persist_write_data(1,&old_cfg,sizeof(old_cfg));
 typedef struct {int32_t when;uint16_t lead,units;uint8_t kind,active,notified,pad;} Old;
 Old old={.when=time(NULL)+86400,.lead=60,.units=1,.kind=1,.active=1};persist_write_data(2,&old,sizeof(old));
 uint16_t previous[6]={2,1,0,0,3,0};persist_write_data(104,previous,sizeof(previous));
 reboot();assert(cfg.cls==4&&counts[4][0]==2&&entries[0].active&&entries[0].lead[0]==60&&entries[0].topic==NO_TOPIC);
 reboot();assert(entries[0].active&&counts[4][0]==2); // migration once, survives restart
 entries[1]=past(1);assert(store_entry(1));assert(book_entry(1));assert(counts[4][0]==4&&!entries[1].active);assert(!book_entry(1));
 reboot();assert(counts[4][0]==4&&!entries[1].active);
 entries[1]=past(5);entries[1].topic=2;assert(store_entry(1));fail_key=201;assert(!book_entry(1));assert(persist_get_size(BOOKING_KEY)==sizeof(Booking)); // interruption after count, before deleting entry
 fail_key=-1;reboot();assert(counts[4][4]==5&&!entries[1].active&&(topics[4]&(1u<<2))); // exactly once
 reboot();assert(counts[4][4]==5);assert(persist_get_size(BOOKING_KEY)<0);
 entries[2]=past(1);assert(store_entry(2));fail_key=104;assert(!book_entry(2));fail_key=-1;reboot();assert(counts[4][0]==6&&!entries[2].active);
 entries[2]=past(0);assert(store_entry(2));assert(book_entry(2));assert(counts[4][0]==6); // UE has no special-hour counter
 entries[2]=past(1);entries[2].units=1;entries[2].extra_minutes=20;assert(store_entry(2));assert(book_entry(2));assert(counts[4][0]==7&&practice[4].remainder[0]==20);
 reboot();assert(practice[4].remainder[0]==20);
 entries[2]=past(1);entries[2].units=1;entries[2].extra_minutes=25;assert(store_entry(2));assert(book_entry(2));assert(counts[4][0]==9&&practice[4].remainder[0]==0);
 entries[2]=past(2);entries[2].units=1;entries[2].extra_minutes=20;assert(store_entry(2));assert(book_entry(2));assert(counts[4][1]==2&&practice[4].remainder[1]==20&&practice[4].remainder[0]==0);
 entries[2]=past(1);entries[2].units=1;entries[2].extra_minutes=40;assert(store_entry(2));assert(book_entry(2));assert(counts[4][0]==10&&practice[4].remainder[0]==40);
 entries[2]=past(1);entries[2].units=1;entries[2].extra_minutes=10;assert(store_entry(2));fail_key=174;assert(!book_entry(2));fail_key=-1;reboot();assert(counts[4][0]==12&&practice[4].remainder[0]==5);reboot();assert(counts[4][0]==12&&practice[4].remainder[0]==5);
 assert(store_language(1));reboot();assert(language==1);assert(store_language(0));reboot();assert(language==0);
 Booking legacy={.id=999,.counter_value=14,.cls=4,.counter=0,.topic_mask=topics[4]};persist_write_data(BOOKING_KEY,&legacy,16);reboot();assert(counts[4][0]==14&&practice[4].remainder[0]==5);
 assert(toggle_topic(0,0));assert(counts[0][4]==1&&(topics[0]&1));assert(counts[0][5]==0);
 assert(toggle_topic(0,12));assert(counts[0][5]==1);assert(toggle_topic(0,0));assert(counts[0][4]==0);reboot();assert(counts[0][5]==1&&(topics[0]&(1u<<12)));
 assert(toggle_topic(1,0));entries[3]=past(5);entries[3].cls=1;entries[3].units=1;entries[3].topic=0;assert(store_entry(3));assert(book_entry(3));assert(counts[1][4]==1);assert(toggle_topic(1,0));assert(counts[1][4]==0);
 entries[3]=past(6);entries[3].cls=1;entries[3].units=1;entries[3].topic=12;assert(store_entry(3));assert(book_entry(3));assert(counts[1][5]==1&&(topics[1]&(1u<<12)));assert(toggle_topic(1,12));assert(counts[1][5]==0);
 fail_key=152;assert(!toggle_topic(2,0));assert(persist_get_size(BOOKING_KEY)==sizeof(Booking));fail_key=-1;reboot();assert(counts[2][4]==1&&(topics[2]&1));reboot();assert(counts[2][4]==1);assert(toggle_topic(2,0));assert(counts[2][4]==0);
 topics[3]=3u|(1u<<12);counts[3][4]=0;counts[3][5]=4;assert(store_progress(3));persist_delete(27);reboot();assert(counts[3][4]==2&&counts[3][5]==4);reboot();assert(counts[3][4]==2&&counts[3][5]==4);
 // Manual corrections only edit units above the checkbox credit; checkmarks are protected.
 assert(topic_units(3,4)==2&&topic_units(3,5)==1);
 assert(set_progress_count(3,4,5));assert(topics[3]==(3u|(1u<<12)));
 assert(set_progress_count(3,4,3));assert(topics[3]==(3u|(1u<<12)));
 assert(!set_progress_count(3,4,1));assert(counts[3][4]==3&&topics[3]==(3u|(1u<<12))&&!storage_error);
 assert(set_progress_count(3,4,2));assert(!set_progress_count(3,4,0));
 assert(toggle_topic(3,0));assert(counts[3][4]==1&&topics[3]==(2u|(1u<<12)));
 assert(toggle_topic(3,1));assert(counts[3][4]==0&&topics[3]==(1u<<12));
 assert(toggle_topic(3,1));assert(counts[3][4]==1);assert(!set_progress_count(3,4,0));
 entries[3]=past(5);entries[3].cls=3;entries[3].units=1;entries[3].topic=1;assert(store_entry(3));assert(book_entry(3));assert(counts[3][4]==1);
 assert(set_progress_count(3,4,4));assert(toggle_topic(3,1));assert(counts[3][4]==3);assert(toggle_topic(3,1));assert(counts[3][4]==4); // manual units preserved
 assert(set_progress_count(3,4,1));assert(toggle_topic(3,13));assert(counts[3][5]==5);
 assert(set_progress_count(3,5,2));assert(!set_progress_count(3,5,1));assert(topics[3]==(2u|(3u<<12)));
 assert(toggle_topic(3,12));assert(counts[3][5]==1&&counts[3][4]==1);reboot();assert(topics[3]==(2u|(1u<<13)));
 assert(set_progress_count(3,4,5));fail_key=103;assert(!set_progress_count(3,4,1));fail_key=-1;reboot();assert(counts[3][4]==1&&(topics[3]&2));reboot();assert(counts[3][4]==1);
 // Repair a contradictory 3.3 manual edit by protecting its checkmarks, never by removing them.
 topics[3]=7u|(1u<<12);counts[3][4]=1;counts[3][5]=0;assert(store_progress(3));reboot();assert(counts[3][4]==3&&counts[3][5]==1&&topics[3]==(7u|(1u<<12)));
 uint8_t rest=practice[4].remainder[0];assert(set_progress_count(4,0,8));assert(practice[4].remainder[0]==rest);
 assert(!set_progress_count(-1,4,0)&&!set_progress_count(3,6,0)&&!set_progress_count(3,4,1000));
 assert(set_progress_count(3,4,999));uint32_t full_mask=topics[3];assert(!toggle_topic(3,4));assert(counts[3][4]==999&&topics[3]==full_mask);
 // Upgrade the retired global mute to per-appointment Off, idempotently.
 entries[5]=past(1);entries[5].when=time(NULL)+86400;entries[5].lead[1]=30;assert(store_entry(5));persist_write_int(29,0);reboot();assert(entries[5].lead[1]==0&&entries[5].lead[0]==60);reboot();assert(entries[5].lead[1]==0);
 entries[6]=past(1);entries[6].lead[1]=30;assert(store_entry(6));reboot();assert(entries[6].lead[1]==30); // new appointments keep their own choice
 uint16_t units=counts[4][0];uint32_t bits=topics[4];assert(set_extra_minutes(4,0,35));assert(practice[4].remainder[0]==35&&counts[4][0]==units&&topics[4]==bits);
 assert(set_extra_minutes(4,0,0));assert(practice[4].remainder[0]==0&&counts[4][0]==units);
 assert(set_extra_minutes(4,6,20));assert(practice[4].remainder[4]==20);reboot();assert(practice[4].remainder[4]==20);
 fail_key=174;assert(!set_extra_minutes(4,6,0));fail_key=-1;reboot();assert(practice[4].remainder[4]==0);
 assert(!set_extra_minutes(4,4,0)&&!set_extra_minutes(4,0,545)&&!set_extra_minutes(4,0,7));
 units=counts[4][0];assert(set_extra_minutes(4,0,45));assert(counts[4][0]==units+1&&practice[4].remainder[0]==0);
 units=counts[4][0];assert(set_extra_minutes(4,0,50));assert(counts[4][0]==units+1&&practice[4].remainder[0]==5);
 units=counts[4][0];fail_key=174;assert(!set_extra_minutes(4,0,540));fail_key=-1;reboot();assert(counts[4][0]==units+12&&practice[4].remainder[0]==0);reboot();assert(counts[4][0]==units+12);
 units=practice[4].exercise_units;assert(set_extra_minutes(4,6,95));assert(practice[4].exercise_units==units+2&&practice[4].remainder[4]==5);
 assert(set_progress_count(4,0,999));assert(extra_minutes_limit(4,0)==40&&!set_extra_minutes(4,0,45));

 puts("PASS storage: v1 migration, persistence, exactly-once booking, interrupted count and appointment writes, topic checkoff, linked GS/ZS toggles, deduplicated lessons and upgrade reconciliation");
}
