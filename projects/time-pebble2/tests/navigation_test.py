"""Execute production nearest-edge navigation against recording menu/scroll APIs."""
from pathlib import Path
import tempfile,subprocess
s=(Path(__file__).resolve().parents[1]/'src/c/main.c').read_text()
a=s.index('static void menu_up(');b=s.index('\nstatic void menu_select(',a);handler=s[a:b]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
typedef void *ClickRecognizerRef;typedef int ScrollLayer;
typedef struct {int section,row;} MenuIndex;
#define MenuIndex(s,r) ((MenuIndex){s,r})
typedef struct {int x,y;} GPoint;typedef struct {int w,h;} GSize;typedef struct {GPoint origin;GSize size;} GRect;
enum {HOME,PROGRESS,TOPICS,LIST,CLASSES};
typedef enum {MenuRowAlignCenter,MenuRowAlignBottom,MenuRowAlignTop,MenuRowAlignNone} MenuRowAlign;
static int page=HOME,menu,calls,alignment,offset,viewport=228;static MenuIndex selected={0,0};
static MenuIndex menu_layer_get_selected_index(int value){(void)value;return selected;}
static int rows(int m,int section,void *ctx){(void)m;(void)section;(void)ctx;return 12;}
static ScrollLayer *menu_layer_get_scroll_layer(int m){(void)m;return &menu;}
static GPoint scroll_layer_get_content_offset(ScrollLayer *l){(void)l;return (GPoint){0,offset};}
static int scroll_layer_get_layer(ScrollLayer *l){(void)l;return 0;}
static GRect layer_get_bounds(int l){(void)l;return (GRect){{0,0},{200,viewport}};}
static int header_height(int m,int section,void *ctx){(void)m;(void)section;(void)ctx;return page==HOME?160:(page==PROGRESS||page==TOPICS)?54:36;}
static int row_height(int m,MenuIndex *index,void *ctx){(void)m;(void)index;(void)ctx;return page==HOME?34:page==PROGRESS?56:48;}
static void menu_layer_set_selected_next(int value,bool up,MenuRowAlign align,bool animated){(void)value;assert(animated);calls++;alignment=align;selected.row+=up?-1:1;}
static void move_menu(bool up);
'''+handler+r'''
int main(void){
 for(int i=0;i<30;i++){menu_up(NULL,NULL);}assert(calls==0);
 menu_down(NULL,NULL);assert(selected.row==1&&alignment==MenuRowAlignNone); // both home choices already visible
 menu_down(NULL,NULL);assert(selected.row==2&&alignment==MenuRowAlignBottom);
 selected.row=1;menu_up(NULL,NULL);assert(selected.row==0&&alignment==MenuRowAlignBottom);
 int old=calls;for(int i=0;i<30;i++){menu_up(NULL,NULL);}assert(calls==old);
 page=PROGRESS;selected.row=0;menu_down(NULL,NULL);assert(alignment==MenuRowAlignNone);
 menu_down(NULL,NULL);assert(selected.row==2&&alignment==MenuRowAlignNone);
 menu_down(NULL,NULL);assert(selected.row==3&&alignment==MenuRowAlignBottom);
 offset=-190;menu_up(NULL,NULL);assert(selected.row==2&&alignment==MenuRowAlignTop);
 page=TOPICS;viewport=206;offset=0;selected.row=1;menu_down(NULL,NULL);assert(selected.row==2&&alignment==MenuRowAlignNone);
 menu_down(NULL,NULL);assert(selected.row==3&&alignment==MenuRowAlignBottom);
 selected.row=11;old=calls;menu_down(NULL,NULL);assert(calls==old);
 puts("PASS navigation: no transition at either boundary, visible choices retain their viewport, minimal native scroll at edges, header restored at first row, footer viewport respected");
}
'''
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'navigation.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'navigation.c'),'-o',str(p/'navigation')],check=True)
 subprocess.run([str(p/'navigation')],check=True)
