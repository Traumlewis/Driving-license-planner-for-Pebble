#pragma once
#include "store.h"
/* Set to 0 only when building the explicit legacy-restore helper. */
#define COMPACT_WRITE_DEFAULT 1
int compact_write_data(int key,const void *data,size_t n);
int compact_read_data(int key,void *data,size_t n);
int compact_get_size(int key);
bool compact_migrate_existing(void);
bool compact_restore_legacy(void);
