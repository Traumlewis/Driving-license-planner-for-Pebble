#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "model.h"
#include "rules.h"
int main(void){
 assert(sizeof(Entry)<=256);assert(sizeof(Booking)<=256);
 Entry list[MAX_ENTRIES]={0};int32_t now=1800000000;
 Entry e={.id=1,.when=now+90000,.lead={1440,30},.cls=4,.kind=1,.units=2,.topic=NO_TOPIC,.active=1};
 assert(entry_valid(&e));assert(sizeof(Entry)==32);assert(end_time(&e)==e.when+5400);assert(entry_next(&e)==e.when-86400);
 assert(!consume_due(&e,now));assert(consume_due(&e,e.when-86400)==1);assert(e.flags==REM1);
 assert(consume_due(&e,e.when-86400)==0);assert(entry_next(&e)==e.when-1800);
 assert(consume_due(&e,e.when-1800)==1);assert(e.flags==(REM1|REM2));assert(entry_next(&e)==end_time(&e));
 e.snooze=e.when-600;assert(entry_next(&e)==e.when-600);assert(consume_due(&e,e.when-600)==1);assert(e.snooze==0);
 assert(consume_due(&e,end_time(&e)-1)==0);assert(consume_due(&e,end_time(&e))==2);assert(e.flags&ASKED);assert(!entry_next(&e));
 e.review=end_time(&e)+1800;assert(entry_next(&e)==e.review);assert(consume_due(&e,e.review)==2);assert(!entry_next(&e));
 e.flags=0;assert(consume_due(&e,end_time(&e)+999)==2);assert(!entry_next(&e)); // no stale reminder when lessons are long past
 e.kind=5;e.topic=3;e.flags=0;assert(entry_valid(&e));assert(end_time(&e)==e.when+10800);e.topic=13;assert(!entry_valid(&e));
 e.kind=6;assert(entry_valid(&e));e.cls=14;e.kind=1;assert(!entry_valid(&e));
 e.cls=4;e.kind=1;e.topic=NO_TOPIC;
 for(int i=0;i<MAX_ENTRIES;i++){list[i]=e;list[i].id=i+1;list[i].when+=i*86400;}
 assert(free_slot(list)==-1);assert(queue_next(list)==e.when-86400);assert(find_id(list,24)==23);
 list[5].active=0;assert(free_slot(list)==5);assert(find_id(list,6)==-1);
 list[1].when=list[0].when;int due=0;for(int i=0;i<MAX_ENTRIES;i++)due+=(consume_due(&list[i],e.when-86400)&1)?1:0;assert(due==2);
 for(int i=0;i<MAX_ENTRIES;i++){consume_due(&list[i],2000000000);}
 assert(queue_next(list)==0);
 Entry minutes={.id=55,.when=now+5000,.lead={60,30},.cls=4,.kind=1,.units=1,.extra_minutes=5,.topic=NO_TOPIC,.active=1};
 assert(entry_valid(&minutes)&&duration_minutes(&minutes)==50&&end_time(&minutes)==minutes.when+3000);
 minutes.extra_minutes=40;assert(entry_valid(&minutes)&&duration_minutes(&minutes)==85);
 minutes.extra_minutes=45;assert(!entry_valid(&minutes));minutes.extra_minutes=7;assert(!entry_valid(&minutes));
 minutes.kind=5;minutes.extra_minutes=5;assert(!entry_valid(&minutes));minutes.extra_minutes=0;assert(entry_valid(&minutes)&&duration_minutes(&minutes)==90);
 Rule r[10];for(int c=0;c<16;c++){int n=rules_for(c,r);assert(n>=1&&n<=10);for(int i=0;i<n;i++)assert(r[i].target[5]<=18);}
 rules_for(4,r);assert(r[0].target[0]==5&&r[0].target[1]==4&&r[0].target[2]==3);assert(r[0].target[4]==12&&r[1].target[4]==6);
 setenv("TZ","Europe/Berlin",1);tzset();time_t t;
 struct tm dt={.tm_year=127,.tm_mon=1,.tm_mday=31,.tm_hour=12};assert(!valid_date(&dt,&t));dt.tm_year=128;dt.tm_mday=29;assert(valid_date(&dt,&t));dt.tm_year=127;assert(!valid_date(&dt,&t));
 dt=(struct tm){.tm_year=127,.tm_mon=2,.tm_mday=28,.tm_hour=2,.tm_min=30};assert(!valid_date(&dt,&t));
 dt=(struct tm){.tm_year=127,.tm_mon=9,.tm_mday=31,.tm_hour=2,.tm_min=30};assert(valid_date(&dt,&t));
 assert(kind_counter(0)==-1&&kind_counter(6)==5);
 Entry muted={.when=10000,.units=1,.kind=0,.lead={60,30},.active=1,.flags=REM1};
 assert(entry_next_with_reminder2(&muted,false)==end_time(&muted));assert(entry_next_with_reminder2(&muted,true)==8200);
 assert(consume_due_with_reminder2(&muted,8200,false)==0&&(muted.flags&REM2));assert(consume_due_with_reminder2(&muted,8200,true)==0);
 muted.flags=0;assert(consume_due_with_reminder2(&muted,6400,false)==1&&(muted.flags&REM1));
 muted.flags=REM1;assert(consume_due_with_reminder2(&muted,8200,true)==1);
 puts("PASS model: 24 entries, both reminders, simultaneous alarms, snooze, completion/review, overdue/restart consumption, class rules and DST");
}
