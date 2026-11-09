/* Desktop experiment only. No watch build includes this file. */
#pragma once
#include "store.h"
int compact_write_data(int key,const void *data,size_t n);
int compact_read_data(int key,void *data,size_t n);
int compact_get_size(int key);
bool compact_migrate_existing(void);
