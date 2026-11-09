#pragma once
#include <pebble.h>
#include "model.h"
#define CONFIG_KEY 1
#define WAKE_KEY 4
#define VERSION_KEY 20
#define SEQUENCE_KEY 21
#define REVISION_KEY 22
#define BOOKING_KEY 23
#define PROFILES_KEY 24
#define REQUEST_KEY 25
extern Config cfg;
extern Entry entries[MAX_ENTRIES];
extern uint16_t counts[16][6];
extern uint32_t topics[16],revision,last_request;
extern uint8_t profiles[16];
extern uint8_t language;
unsigned extra_minutes_limit(int cls,int counter);
bool set_extra_minutes(int cls,int counter,unsigned minutes);
extern PracticeProgress practice[16];
bool store_language(uint8_t value);
extern bool storage_error;
bool store_load(void);
bool store_entry(int i);
bool store_config(void);
bool store_progress(int c);
bool store_revision(void);
bool store_request(uint32_t request);
bool book_entry(int i);
bool toggle_topic(int cls,int topic);
bool set_progress_count(int cls,int counter,unsigned value);
unsigned topic_units(int cls,int counter);
uint32_t allocate_id(void);

unsigned store_bytes_used(void);
unsigned store_compact_records(void);
unsigned store_quota_bytes(void);
bool store_uses_compact(void);
