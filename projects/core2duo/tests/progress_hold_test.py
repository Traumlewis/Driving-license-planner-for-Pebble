"""Production hold mapping must follow actual row heights after the progress redesign."""
from pathlib import Path
import tempfile,subprocess
source=(Path(__file__).resolve().parents[1]/'src/c/main.c').read_text()
def function(start):
 a=source.index(start);b=source.index('{',a)+1;depth=1
 while depth:depth+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
typedef int AppTimer;typedef int Window;
typedef struct {int x,y;} GPoint;
typedef struct {int section,row;} MenuIndex;
#define MenuIndex(s,r) ((MenuIndex){s,r})
enum {HOME,PROGRESS,PROGRESS_ACTIONS,MenuRowAlignNone};
static int blocked_row=-1;
static bool progress_can_hold(int row){return row!=blocked_row;}
static int page=PROGRESS,menu,progress_counter,progress_touch_row,selected,offset,registered,cancelled;
static AppTimer value,*progress_hold_timer;static bool progress_hold_fired;
static Window root,other,*window=&root,*top=&root;
static void (*callback)(void *);
static void app_timer_cancel(AppTimer *t){assert(t==&value);cancelled++;}
static AppTimer *app_timer_register(int ms,void (*cb)(void *),void *ctx){assert(ms==650&&ctx==NULL);registered++;callback=cb;return &value;}
static Window *window_stack_get_top_window(void){return top;}
static void menu_layer_set_selected_index(int m,MenuIndex index,int align,bool animated){(void)m;assert(align==MenuRowAlignNone&&!animated);selected=index.row;}
static void show_page(int p){page=p;}
static int menu_layer_get_scroll_layer(int m){return m;}
static GPoint scroll_layer_get_content_offset(int m){(void)m;return (GPoint){0,offset};}
static int header_height(int m,int section,void *ctx){(void)m;(void)section;(void)ctx;return 54;}
static int row_height(int m,MenuIndex *index,void *ctx){(void)m;(void)index;(void)ctx;return 56;}
'''+function('static void cancel_progress_touch(void){')+function('static void progress_touch_timeout(void *context){')+function('static void start_progress_touch(int y){')+r'''
int main(void){
 for(int row=0;row<7;row++){page=PROGRESS;top=&root;offset=-row*56;progress_hold_fired=false;start_progress_touch(80);assert(progress_touch_row==row);callback(NULL);assert(page==PROGRESS_ACTIONS&&progress_counter==row&&selected==row&&progress_hold_fired);}
 page=PROGRESS;offset=0;int old=registered;start_progress_touch(20);start_progress_touch(54+7*56);assert(registered==old);
 start_progress_touch(80);cancel_progress_touch();assert(cancelled==1&&!progress_hold_timer);
 page=HOME;start_progress_touch(80);assert(registered==old+1);
 page=PROGRESS;start_progress_touch(80);top=&other;callback(NULL);assert(page==PROGRESS);
 blocked_row=0;page=PROGRESS;top=&root;offset=0;int previous=registered;start_progress_touch(80);assert(registered==previous);progress_touch_row=0;callback(NULL);assert(page==PROGRESS);
 puts("PASS progress hold: all seven 56px rows including scrolled offsets, header/end rejection, cancellation and changed top window");
}
'''
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'hold.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'hold.c'),'-o',str(p/'hold')],check=True)
 subprocess.run([str(p/'hold')],check=True)
