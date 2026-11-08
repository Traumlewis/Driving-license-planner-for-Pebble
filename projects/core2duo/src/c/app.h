#pragma once
#include "store.h"
extern bool alarm_ok;
int profile_extra(int cls);
void state_changed(void);
void show_message(const char *text);
void show_status(const char *title,const char *detail);
void phone_init(void);
void phone_push(uint32_t request,int status,const char *error);
void phone_deinit(void);
