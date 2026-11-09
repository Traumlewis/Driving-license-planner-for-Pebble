#pragma once
#include <stdint.h>
#include <stdbool.h>
extern uint8_t language;
const char *translate(const char *text);
void language_pack_init(void);
bool language_pack_ready(void);
uint32_t language_pack_id(void);
unsigned language_pack_size(void);
unsigned language_pack_received(void);
int language_pack_receive(uint32_t identity,unsigned part,unsigned total,const char *hex);
#define T(text) translate(text)
