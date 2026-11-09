/* (Idee by Traumlewis | Code by Codex) */
#include <pebble.h>
#include <string.h>
#include "i18n.h"
#include "script_fonts.h"
/* Pebble keeps resource-backed glyph data in flash. Each loaded font is a small
 * descriptor; at most seven live descriptors, reused until application exit. */
static GFont loaded[7];
static bool extended_script(void){
 const unsigned char *p=(const unsigned char *)language_pack_name();
 /* Greek/Cyrillic autonyms identify the script without hard-coded language IDs.
  * Additional compatible packets can therefore be registered without a build. */
 while(*p){if(*p>=0xce&&*p<=0xd4)return true;p++;}return false;
}
GFont script_font(const char *key){
 static const char *const keys[]={FONT_KEY_GOTHIC_14,FONT_KEY_GOTHIC_14_BOLD,FONT_KEY_GOTHIC_18,FONT_KEY_GOTHIC_18_BOLD,FONT_KEY_GOTHIC_24,FONT_KEY_GOTHIC_24_BOLD,FONT_KEY_GOTHIC_28_BOLD};
 static const uint32_t ids[]={RESOURCE_ID_SCRIPT_14,RESOURCE_ID_SCRIPT_14_BOLD,RESOURCE_ID_SCRIPT_18,RESOURCE_ID_SCRIPT_18_BOLD,RESOURCE_ID_SCRIPT_24,RESOURCE_ID_SCRIPT_24_BOLD,RESOURCE_ID_SCRIPT_28_BOLD};
 if(extended_script())for(unsigned i=0;i<7;i++)if(!strcmp(key,keys[i])){if(!loaded[i])loaded[i]=fonts_load_custom_font(resource_get_handle(ids[i]));return loaded[i];}
 return fonts_get_system_font(key);
}
