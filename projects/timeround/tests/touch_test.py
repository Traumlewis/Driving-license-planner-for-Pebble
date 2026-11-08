"""Compile the production touch handler with small UI doubles and replay raw contacts."""
from pathlib import Path
import tempfile,subprocess
root=Path(__file__).resolve().parents[1];source=(root/'src/c/main.c').read_text();start=source.index('static void touch_handler(const TouchEvent *event,void *context) {');brace=source.index('{',start);end=brace+1;depth=1
while depth:
 depth+=(source[end]=='{')-(source[end]=='}');end+=1
handler=source[start:end]
prefix=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
typedef struct {int id;} Window;
typedef struct {int16_t x,y;} GPoint;
typedef struct {int16_t w,h;} GSize;
typedef struct {GPoint origin;GSize size;} GRect;
typedef struct {int type;bool non_navigational;int16_t x,y;} TouchEvent;
enum {TouchEvent_Touchdown,TouchEvent_Liftoff,TouchEvent_PositionUpdate};
static Window n={1},d={2},m={3},other={4},w={5};
typedef int ScrollLayer;
typedef struct {int section,row;} MenuIndex;
#define MenuIndex(s,r) ((MenuIndex){s,r})
enum {MenuRowAlignNone};
static ScrollLayer msg_value,menu_value;
static ScrollLayer *msg_scroll=&msg_value;static int menu,menu_offset,menu_activated,back_count;
static MenuIndex menu_selected;
static Window *window=&w;
static Window *num_window=&n,*date_window=&d,*msg_window=&m,*top=&n;
static int num_layer,date_layer,date_mode,date_field,viewport_height=228,row_count=3;
typedef int Page;static Page page;
static bool progress_hold_fired;static int hold_started;
static void cancel_progress_touch(void){}
static void start_progress_touch(int y){(void)y;hold_started++;}
static int up,down,selected,popped,date_delta,date_selected,dirty,offset;
static Window *window_stack_get_top_window(void){return top;}
static void window_stack_pop(bool animate){assert(animate);popped++;}
static ScrollLayer *menu_layer_get_scroll_layer(int value){(void)value;return &menu_value;}
static MenuIndex menu_layer_get_selected_index(int value){(void)value;return menu_selected;}
static void menu_layer_set_selected_index(int value,MenuIndex index,int align,bool animated){(void)value;assert(align==MenuRowAlignNone&&!animated);menu_selected=index;}
static int rows(int menu,int section,void *ctx){(void)menu;(void)section;(void)ctx;return row_count;}
static int header_height(int menu,int section,void *ctx){(void)menu;(void)section;(void)ctx;return 34;}
static int row_height(int menu,MenuIndex *i,void *ctx){(void)menu;(void)i;(void)ctx;return 48;}
static void select_row(int menu,MenuIndex *i,void *ctx){(void)menu;(void)i;(void)ctx;menu_activated++;}
static void back(void *r,void *ctx){(void)r;(void)ctx;back_count++;}
static GPoint scroll_layer_get_content_offset(ScrollLayer *scroll){return (GPoint){0,scroll==&menu_value?menu_offset:offset};}
static GPoint point(int x,int y){return (GPoint){x,y};}
#define GPoint(x,y) point(x,y)
static int scroll_layer_get_layer(ScrollLayer *scroll){(void)scroll;return 0;}
static GRect layer_get_bounds(int layer){(void)layer;return (GRect){{0,0},{200,viewport_height}};}
static GSize scroll_layer_get_content_size(ScrollLayer *scroll){(void)scroll;return (GSize){200,500};}
static void scroll_layer_set_content_offset(ScrollLayer *scroll,GPoint point,bool animate){assert(!animate);assert(point.y<=0&&point.y>=-272);if(scroll==&menu_value)menu_offset=point.y;else offset=point.y;}
static void num_up(void *r,void *c){(void)r;(void)c;up++;}
static void num_down(void *r,void *c){(void)r;(void)c;down++;}
static void num_select(void *r,void *c){(void)r;(void)c;selected++;}
static void date_adjust(int delta){date_delta+=delta;}
static void date_select(void *r,void *c){(void)r;(void)c;date_selected++;}
static void layer_mark_dirty(int layer){(void)layer;dirty++;}
'''
suffix=r'''
static void touch(int type,int x,int y,bool inert){TouchEvent e={type,inert,x,y};touch_handler(&e,NULL);}
static void tap(int x,int y){touch(TouchEvent_Touchdown,x,y,false);touch(TouchEvent_Liftoff,0,0,false);}
int main(void){
 (void)num_layer;
 tap(166,180);assert(up==1);tap(30,180);assert(down==1);tap(100,180);assert(selected==1);
 touch(TouchEvent_Touchdown,160,180,true);touch(TouchEvent_Liftoff,0,0,true);assert(up==1);
 touch(TouchEvent_Touchdown,70,100,false);touch(TouchEvent_PositionUpdate,150,105,false);touch(TouchEvent_Liftoff,0,0,false);assert(popped==1);
 top=&d;tap(120,100);assert(date_field==2&&dirty==1);tap(100,180);assert(date_selected==1);
 touch(TouchEvent_Touchdown,100,110,false);touch(TouchEvent_PositionUpdate,100,50,false);touch(TouchEvent_Liftoff,0,0,false);assert(date_delta==1);
 top=&m;touch(TouchEvent_Touchdown,100,200,false);touch(TouchEvent_PositionUpdate,100,80,false);touch(TouchEvent_Liftoff,0,0,false);assert(offset==-120);
 touch(TouchEvent_Touchdown,100,200,false);touch(TouchEvent_PositionUpdate,100,-200,false);touch(TouchEvent_Liftoff,0,0,false);assert(offset==-272);
 top=&w;touch(TouchEvent_Touchdown,100,100,false);touch(TouchEvent_PositionUpdate,100,200,false);assert(menu_offset==0);
 touch(TouchEvent_PositionUpdate,100,180,false);assert(menu_offset==-20);touch(TouchEvent_PositionUpdate,100,-500,false);assert(menu_offset==-272);
 touch(TouchEvent_PositionUpdate,100,-480,false);assert(menu_offset==-252);touch(TouchEvent_Liftoff,0,0,false);assert(menu_activated==0);
 menu_offset=0;tap(100,100);assert(menu_selected.row==1&&menu_activated==0);tap(100,100);assert(menu_activated==1);
 touch(TouchEvent_Touchdown,50,100,false);touch(TouchEvent_PositionUpdate,140,100,false);touch(TouchEvent_Liftoff,0,0,false);assert(back_count==1);
 top=&other;tap(160,180);assert(up==1);
 top=&w;int previous_activations=menu_activated;touch(TouchEvent_Touchdown,40,60,false);assert(hold_started>0);progress_hold_fired=true;touch(TouchEvent_Liftoff,0,0,false);assert(menu_activated==previous_activations);
 top=&w;viewport_height=206;row_count=5;previous_activations=menu_activated;int previous_row=menu_selected.row;tap(100,214);assert(menu_activated==previous_activations&&menu_selected.row==previous_row);menu_selected.row=3;touch(TouchEvent_Touchdown,100,204,false);touch(TouchEvent_PositionUpdate,100,210,false);touch(TouchEvent_Liftoff,0,0,false);assert(menu_activated==previous_activations);viewport_height=228;row_count=3;
 // A contact begun on the previous menu must not act on the next page.
 top=&w;menu_offset=0;previous_activations=menu_activated;touch(TouchEvent_Touchdown,100,100,false);page++;touch(TouchEvent_Liftoff,0,0,false);assert(menu_activated==previous_activations);
 puts("PASS touch: +/-/OK, date-field selection, swipes, text dragging, scroll bounds, inert contacts and zero-coordinate liftoff, hard menu edges and immediate reversal without rubberband");
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);(p/'touch.c').write_text(prefix+handler+suffix)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'touch.c'),'-o',str(p/'touch')],check=True);subprocess.run([str(p/'touch')],check=True)
