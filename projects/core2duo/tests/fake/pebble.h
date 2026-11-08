#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <time.h>
int persist_write_data(int key,const void *p,size_t n);
int persist_read_data(int key,void *p,size_t n);
int persist_get_size(int key);
int persist_write_int(int key,int32_t v);
int32_t persist_read_int(int key);
int persist_delete(int key);
void wakeup_cancel_all(void);
