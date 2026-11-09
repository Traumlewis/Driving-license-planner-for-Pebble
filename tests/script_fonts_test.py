"""Exercise production font selection, bounded caching and retained-pointer lifetime."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
names=['GOTHIC_14','GOTHIC_14_BOLD','GOTHIC_18','GOTHIC_18_BOLD','GOTHIC_24','GOTHIC_24_BOLD','GOTHIC_28_BOLD']
projects=['time2','core2duo','time-pebble2','round2','timeround']
for name in projects:
 for filename in ['script_fonts.c','script_fonts.h']:
  assert (ROOT/'projects'/name/'src/c'/filename).read_bytes()==(ROOT/'projects/time2/src/c'/filename).read_bytes()
with tempfile.TemporaryDirectory() as directory:
 p=Path(directory)
 header='#pragma once\n#include <stdint.h>\n#include <stdbool.h>\ntypedef void *GFont;typedef uint32_t ResHandle;\nGFont fonts_get_system_font(const char *);GFont fonts_load_custom_font(ResHandle);ResHandle resource_get_handle(uint32_t);\n'
 for i,name in enumerate(names):header+=f'#define FONT_KEY_{name} "{name}"\n#define RESOURCE_ID_SCRIPT_{name[7:]} {i+1}\n'
 (p/'pebble.h').write_text(header)
 source='''#include <assert.h>
#include <string.h>
#include "script_fonts.h"
static const char *name="Deutsch";static unsigned loads;static int glyphs[7],system_font;
const char *language_pack_name(void){return name;}
GFont fonts_get_system_font(const char *key){(void)key;return &system_font;}
ResHandle resource_get_handle(uint32_t id){return id;}
GFont fonts_load_custom_font(ResHandle id){assert(id>=1&&id<=7);loads++;return &glyphs[id-1];}
int main(void){
 assert(script_font(FONT_KEY_GOTHIC_14)==&system_font&&loads==0);
 name="Ελληνικά";GFont retained=script_font(FONT_KEY_GOTHIC_14);assert(retained==&glyphs[0]&&loads==1);
 assert(script_font(FONT_KEY_GOTHIC_14)==retained&&loads==1);
 name="Български";assert(script_font(FONT_KEY_GOTHIC_14)==retained&&loads==1);
 name="Latviešu";assert(script_font(FONT_KEY_GOTHIC_14)==&system_font&&loads==1);
 name="Gaeilge";assert(script_font(FONT_KEY_GOTHIC_14)==&system_font&&loads==1);
 name="Ελληνικά";assert(script_font("BITHAM_42_BOLD")==&system_font&&loads==1);
'''
 for name in names:source+=f' assert(script_font(FONT_KEY_{name})!=&system_font);\n'
 source+='assert(loads==7);name="Español";assert(script_font(FONT_KEY_GOTHIC_14)==&system_font);name="Български";assert(script_font(FONT_KEY_GOTHIC_14)==retained&&loads==7);return 0;}\n'
 (p/'test.c').write_text(source)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-I',str(p),'-I',str(ROOT/'projects/time2/src/c'),str(p/'test.c'),str(ROOT/'projects/time2/src/c/script_fonts.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS font selection: Latin originals, Greek/Cyrillic resources, unchanged numeric fonts, seven cached descriptors and retained-pointer lifetime across language swaps')
