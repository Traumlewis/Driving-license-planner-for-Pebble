"""Production info-card contract: shared design, full body and persistent reading window."""
from pathlib import Path
import subprocess,tempfile,re
source=(Path(__file__).resolve().parents[1]/'src/c/main.c').read_text()
def function(start):
 a=source.index(start);b=source.index('{',a)+1;depth=1
 while depth:depth+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
typedef int Window;typedef int Layer;typedef int ScrollLayer;typedef int TextLayer;
typedef struct {int x,y,w,h;} GRect;
#define GRect(x,y,w,h) ((GRect){x,y,w,h})
#define T(s) (s)
enum {GColorWhite,GColorOxfordBlue,FONT_KEY_GOTHIC_24};
static bool ui_ready=true,contains,header_hidden=true;static int dismissals,pushes,layouts,updates;
static int window_value,header_value,scroll_value,text_value;
static Window *msg_window=&window_value;static Layer *info_header=&header_value;
static ScrollLayer *msg_scroll=&scroll_value;static TextLayer *msg_text=&text_value;
static char info_title[64],msg_buf[2048];static int info_symbol;
static void dismiss_status(void){dismissals++;}
static void window_set_background_color(Window *w,int c){assert(w==msg_window&&c==GColorWhite);}
static void text_layer_set_text_color(TextLayer *l,int c){assert(l==msg_text&&c==GColorOxfordBlue);}
static int fonts_get_system_font(int f){assert(f==FONT_KEY_GOTHIC_24);return f;}
static void text_layer_set_font(TextLayer *l,int f){assert(l==msg_text&&f==FONT_KEY_GOTHIC_24);}
static void text_layer_set_text(TextLayer *l,const char *s){assert(l==msg_text&&s==msg_buf);}
static void layout_message(void){layouts++;}
static void scroll_layer_set_frame(ScrollLayer *s,GRect r){assert(s==msg_scroll&&r.y==48&&r.w==200&&r.h==180);}
static Layer *scroll_layer_get_layer(ScrollLayer *s){assert(s==msg_scroll);return &scroll_value;}
static void layer_set_bounds(Layer *l,GRect r){assert(l==&scroll_value&&r.y==0&&r.h==180);}
static void layer_set_hidden(Layer *l,bool hidden){assert(l==info_header);header_hidden=hidden;}
static void layer_mark_dirty(Layer *l){assert(l==info_header);updates++;}
static bool window_stack_contains_window(Window *w){assert(w==msg_window);return contains;}
static void window_stack_push(Window *w,bool animated){assert(w==msg_window&&animated);contains=true;pushes++;}
'''+function('static void show_notice(')+function('void show_message(')+function('static void show_info(')+r'''
int main(void){
 const char *details="KLASSE B\nPraxis | Nachtfahrt\n09.11.2026\n\n45 Minuten\nErinnerung 1: 01:00";
 show_notice("Termindetails",6,details);assert(!strcmp(msg_buf,details)&&!strcmp(info_title,"Termindetails")&&info_symbol==6&&!header_hidden&&pushes==1);
 show_notice("Speicherfehler",4,"Erster Absatz\n\nWichtiger zweiter Absatz");assert(!strcmp(msg_buf,"Erster Absatz\n\nWichtiger zweiter Absatz")&&info_symbol==4&&pushes==1);
 show_message("Bitte Datum prüfen.");assert(!strcmp(info_title,"Hinweis")&&!strcmp(msg_buf,"Bitte Datum prüfen."));
 show_info("Handy-Eingabe",2,"HANDY-EINGABE\n\nVollständiger Erklärungstext");assert(!strcmp(msg_buf,"Vollständiger Erklärungstext")&&info_symbol==2);
 assert(layouts==4&&updates==4&&dismissals==4&&contains);
 ui_ready=false;show_notice("Ignorieren",4,"Keine UI");assert(layouts==4&&dismissals==4);
 puts("PASS info cards: shared white/navy/cyan layout, large text, fixed header and scroll area; complete details and paragraphs preserved; explanation legacy heading removed only explicitly; no automatic dismissal");
}
'''
# There is no remaining call site using the former unstyled route.
assert len(re.findall(r'\bshow_message\s*\(',source))==1
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'info.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'info.c'),'-o',str(p/'info')],check=True)
 subprocess.run([str(p/'info')],check=True)
