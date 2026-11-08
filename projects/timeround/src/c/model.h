#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#define MAX_ENTRIES 24
#define REM1 1
#define REM2 2
#define ASKED 4
#define NO_TOPIC 255
#define MODEL_VERSION 2
#define MAX_TOPICS 30
// All persistence records fit in Pebble's 256-byte value limit.
typedef struct {
 uint32_t id, token;
 int32_t when, snooze, review;
 uint16_t lead[2];
 uint8_t cls, kind, units, topic, flags, active;
 uint16_t extra_minutes;
} Entry;
typedef struct { int16_t cls,profile; } Config;
typedef struct { uint32_t id,token; uint16_t counter_value; uint8_t cls,counter; uint32_t topic_mask; uint16_t remainder,exercise_units; } Booking;
typedef struct { uint16_t exercise_units; uint8_t remainder[5]; uint8_t pad; } PracticeProgress;
static inline int unit_minutes(const Entry *e) {return e->kind>=5?90:45;}
static inline int duration_minutes(const Entry *e) {return e->units*unit_minutes(e)+e->extra_minutes;}
static inline int32_t end_time(const Entry *e) {return e->when+(int32_t)duration_minutes(e)*60;}
static inline int kind_counter(int kind) {return kind-1;}
static inline bool entry_valid(const Entry *e) {
 return (e->kind>=5?e->extra_minutes==0:(e->extra_minutes<45 && e->extra_minutes%5==0 && duration_minutes(e)<=540)) && e->active<=1 && e->cls<16 && e->kind<7 && !(e->cls==14&&e->kind<5) && e->units>=1 && e->units<=12 && e->when>0 && e->when<=2147400000-12*90*60 && e->lead[0]>=15 && e->lead[0]<=2880 && e->lead[0]%15==0 && e->lead[1]<=2880 && e->lead[1]%15==0 && (e->topic==NO_TOPIC || (e->kind==5&&e->topic<12) || (e->kind==6&&e->topic>=12&&e->topic<MAX_TOPICS));
}
static inline bool valid_date(struct tm *t,time_t *result) {
 struct tm copy=*t;copy.tm_isdst=-1;time_t value=mktime(&copy);
 if(value==(time_t)-1||copy.tm_year!=t->tm_year||copy.tm_mon!=t->tm_mon||copy.tm_mday!=t->tm_mday||copy.tm_hour!=t->tm_hour||copy.tm_min!=t->tm_min)return false;
 *result=value;return true;
}
static inline int free_slot(const Entry *e) {for(int i=0;i<MAX_ENTRIES;i++)if(!e[i].active)return i;return -1;}
static inline int find_id(const Entry *e,uint32_t id) {for(int i=0;i<MAX_ENTRIES;i++)if(e[i].active&&e[i].id==id)return i;return -1;}
static inline int32_t entry_next_with_reminder2(const Entry *e,bool second) {
 if(!e->active)return 0;
 int32_t next=0,v;
 #define EARLIEST(t) do {v=(t);if(v>0&&(!next||v<next))next=v;}while(0)
 for(int k=0;k<(second?2:1);k++)if(e->lead[k]&&!(e->flags&(1<<k)))EARLIEST(e->when-(int32_t)e->lead[k]*60);
 if(!(e->flags&ASKED))EARLIEST(end_time(e));
 EARLIEST(e->snooze);EARLIEST(e->review);
 #undef EARLIEST
 return next;
}
static inline int32_t entry_next(const Entry *e){return entry_next_with_reminder2(e,true);}
static inline int32_t queue_next_with_reminder2(const Entry *entries,bool second) {
 int32_t next=0;for(int i=0;i<MAX_ENTRIES;i++){int32_t t=entry_next_with_reminder2(&entries[i],second);if(t&&(!next||t<next))next=t;}return next;
}
static inline int32_t queue_next(const Entry *entries){return queue_next_with_reminder2(entries,true);}
// Consume ALL due events before scheduling again: reminders at the same time share one wakeup.
// Returns bit 1 reminder, bit 2 lesson-completion question. No automatic booking.
static inline int consume_due_with_reminder2(Entry *e,int32_t now,bool second) {
 if(!e->active)return 0;
 int event=0;
 for(int k=0;k<2;k++)if(e->lead[k]&&!(e->flags&(1<<k))&&e->when-(int32_t)e->lead[k]*60<=now){e->flags|=1<<k;if((k==0||second)&&now<e->when)event|=1;}
 if(e->snooze&&e->snooze<=now){e->snooze=0;event|=1;}
 if((!(e->flags&ASKED)&&end_time(e)<=now)||(e->review&&e->review<=now)){e->flags|=ASKED;e->review=0;event|=2;}
 return event;
}
static inline int consume_due(Entry *e,int32_t now){return consume_due_with_reminder2(e,now,true);}
