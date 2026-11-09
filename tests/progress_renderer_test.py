"""Run the actual five progress renderers against every class/profile/counter."""
from pathlib import Path
import subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[1]
def body(source,marker):
 a=source.index(marker);b=source.index('{',a)+1;start=b;depth=1
 while depth:depth+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[start:b-1]
for project in ['time2','core2duo','time-pebble2','round2','timeround']:
 folder=ROOT/'projects'/project;s=(folder/'src/c/main.c').read_text();round_device=project in ['round2','timeround']
 code=body(s,'else if(page==PROGRESS){') if round_device else body(s,'static void progress_row(')
 if round_device:code='int r=row,left=8,width=164,h=56;bool selected=false;(void)h;'+code
 prefix=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
'''+ '#include '+json.dumps(str(folder/'src/c/rules.h'))+r'''
typedef int GContext;typedef int Layer;typedef int GFont;
typedef struct {int w,h;} GSize;
typedef struct {int x,y,w,h;} GRect;
#define GRect(x,y,w,h) ((GRect){x,y,w,h})
#define T(x) (x)
#define UI_WIDTH 144
#define UI_SELECTION_TEXT 0
#define GColorWhite 1
#define GColorBlack 0
#define GColorOxfordBlue 0
#define GColorCyan 2
#define GCornerNone 0
#define FONT_KEY_GOTHIC_14 14
#define FONT_KEY_GOTHIC_14_BOLD 15
#define FONT_KEY_GOTHIC_18_BOLD 18
#define FONT_KEY_GOTHIC_24_BOLD 24
#define GTextOverflowModeTrailingEllipsis 0
#define GTextOverflowModeWordWrap 1
#define GTextAlignmentLeft 0
#define GTextAlignmentRight 1
static struct {int cls,profile;} cfg;
static uint16_t counts[16][6];
static struct {unsigned exercise_units,remainder[5];} practice[16];
static Rule rules[10];static int outlines,no_minimum;static char rendered_count[32];
static const uint16_t *targets(void){return rules[cfg.profile].target;}
static GFont fonts_get_system_font(int font){return font;}
static bool menu_cell_layer_is_highlighted(const Layer *l){(void)l;return false;}
static bool cell_selected(const Layer *l){(void)l;return false;}
static GSize graphics_text_layout_get_content_size(const char *s,GFont f,GRect r,int o,int a){(void)f;(void)r;(void)o;(void)a;return (GSize){(int)strlen(s)*8,18};}
static void graphics_draw_text(GContext *c,const char *s,GFont f,GRect r,int o,int a,void *attrs){(void)c;(void)f;(void)r;(void)o;(void)a;(void)attrs;if(!strcmp(s,"Kein festes Minimum"))no_minimum++;if(s[0]&&strspn(s,"0123456789/")==strlen(s))snprintf(rendered_count,sizeof(rendered_count),"%s",s);}
static void graphics_context_set_fill_color(GContext *c,int color){(void)c;(void)color;}
static void graphics_context_set_text_color(GContext *c,int color){(void)c;(void)color;}
static void graphics_context_set_stroke_color(GContext *c,int color){(void)c;(void)color;}
static void graphics_context_set_stroke_width(GContext *c,int width){(void)c;(void)width;}
static void graphics_fill_rect(GContext *c,GRect r,int radius,int corners){(void)c;(void)r;(void)radius;(void)corners;}
static void graphics_draw_rect(GContext *c,GRect r){(void)c;(void)r;outlines++;}
static void render(GContext *ctx,const Layer *layer,int row){(void)layer;
'''
 suffix=r'''
}
int main(void){
 int cases=0,profiles=0,zero=0;
 for(int cls=0;cls<16;cls++){
  int n=rules_for(cls,rules);assert(n>0);cfg.cls=cls;
  for(int profile=0;profile<n;profile++){
   cfg.profile=profile;profiles++;
   for(int row=0;row<7;row++){
    unsigned goal=row<6?targets()[row]:0;counts[cls][row<6?row:0]=1;practice[cls].exercise_units=1;
    outlines=no_minimum=0;rendered_count[0]=0;render(NULL,NULL,row);cases++;
    if(goal){char expected[32];snprintf(expected,sizeof(expected),"1/%u",goal);assert(!strcmp(rendered_count,expected));assert(outlines==1&&no_minimum==0);}
    else {assert(!strcmp(rendered_count,"1"));assert(outlines==0&&no_minimum==1);zero++;}
   }
  }
 }
 printf("PASS actual renderer: 16 classes, %d profiles, %d counters; %d undefined goals show count/no minimum without empty percentage track\n",profiles,cases,zero);
}
'''
 with tempfile.TemporaryDirectory() as d:
  p=Path(d);(p/'render.c').write_text(prefix+code+suffix)
  subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function',str(p/'render.c'),'-o',str(p/'render')],check=True)
  subprocess.run([str(p/'render')],check=True)
 print('Project:',project)
