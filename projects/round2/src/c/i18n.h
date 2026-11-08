#pragma once
#include <stdint.h>
extern uint8_t language;
const char *translate(const char *text);
#define T(text) translate(text)
