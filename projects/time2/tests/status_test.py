"""Run production status lifecycle functions against recording window/timer APIs."""
from pathlib import Path
import subprocess,tempfile
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
typedef int Window;typedef int Layer;typedef int AppTimer;
static Window status_value,*status_window=&status_value;static Layer layer_value,*status_layer=&layer_value;
static AppTimer timer_value,*status_timer;static bool ui_ready=true,contains,foreign_top;
static char status_title[96],status_detail[96];static int registrations,cancellations,pushes,removes;
#define T(s) (s)
static void app_timer_cancel(AppTimer *t){assert(t);cancellations++;}
static bool window_stack_contains_window(Window *w){assert(w==status_window);return contains;}
static void window_stack_remove(Window *w,bool animated){assert(w==status_window&&!animated);contains=false;removes++;}
static void layer_mark_dirty(Layer *l){assert(l==status_layer);}
static void window_stack_push(Window *w,bool animated){assert(w==status_window&&!animated);contains=true;pushes++;}
static AppTimer *app_timer_register(int ms,void (*callback)(void *),void *ctx){assert(ms==2000&&callback&&ctx==NULL);registrations++;return &timer_value;}
'''+function('static void dismiss_status(')+function('static void status_timeout(')+function('void show_status(')+r'''
int main(void){
 show_status("Termin gespeichert","Handy-Eingabe");assert(registrations==1&&pushes==1&&contains);assert(!strcmp(status_title,"Termin gespeichert"));
 show_status("Termin gelöscht","Handy-Eingabe");assert(cancellations==1&&pushes==1&&registrations==2);assert(!strcmp(status_title,"Termin gelöscht"));
 foreign_top=true;status_timeout(NULL);assert(foreign_top&&!contains&&!status_timer&&removes==1); // never pop another window
 show_status("Gespeichert","Info");dismiss_status();assert(!contains&&!status_timer&&cancellations==2);
 status_timeout(NULL);assert(removes==2&&foreign_top);
 ui_ready=false;show_status("Ignored","Info");assert(registrations==3);
 puts("PASS status: exactly 2000ms, repeated updates restart timer, only owned window closes, early dismissal and shutdown-safe cancellation");
}
'''
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'status.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'status.c'),'-o',str(p/'status')],check=True)
 subprocess.run([str(p/'status')],check=True)
