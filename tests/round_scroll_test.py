"""Exercise actual Round menu geometry, limits and legacy separator callbacks."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def function(source,marker):
 a=source.index(marker);b=source.index('{',a)+1;depth=1
 while depth:depth+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
for project,diameter,head in [('round2',260,78),('timeround',180,58)]:
 source=(ROOT/'projects'/project/'src/c/main.c').read_text()
 assert 'menu_layer_pad_bottom_enable(menu,true)' in source
 prefix=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
typedef int MenuLayer;typedef int ScrollLayer;
typedef struct {int section,row;} MenuIndex;
#define MenuIndex(s,r) ((MenuIndex){s,r})
typedef struct {int x,y;} GPoint;
#define GPointZero ((GPoint){0,0})
typedef struct {int w,h;} GSize;
typedef struct {GPoint origin;GSize size;} GRect;
enum {HOME,PROGRESS,TOPICS,TOPIC_PICK,SETTINGS,MenuRowAlignNone=10,MenuRowAlignCenter};
static int page=SETTINGS,menu_value,viewport=122,frame_y,offset=-90,selected=2,changes,resets,last_align;
static MenuLayer *menu=&menu_value;
static int rows(MenuLayer *m,int s,void *ctx){(void)m;(void)s;(void)ctx;return 7;}
static int row_height(MenuLayer *m,MenuIndex *i,void *ctx){(void)m;(void)i;(void)ctx;return 48;}
static int menu_layer_get_layer(MenuLayer *m){(void)m;return 0;}
static GRect layer_get_frame(int l){(void)l;return (GRect){{0,frame_y},{180,viewport}};}
static MenuIndex menu_layer_get_selected_index(MenuLayer *m){(void)m;return MenuIndex(0,selected);}
static ScrollLayer *menu_layer_get_scroll_layer(MenuLayer *m){return m;}
static GPoint scroll_layer_get_content_offset(ScrollLayer *s){(void)s;return (GPoint){0,offset};}
static void menu_layer_set_selected_next(MenuLayer *m,bool up,int align,bool animated){(void)m;assert(animated);selected+=up?-1:1;changes++;last_align=align;}
static void scroll_layer_set_content_offset(ScrollLayer *s,GPoint p,bool animated){(void)s;assert(animated&&p.x==0);offset=p.y;resets++;}
'''
 funcs='\n'.join(function(source,m) for m in ['static int page_header_height(void){','static int16_t header_height(MenuLayer *m,uint16_t section,void *ctx){','static int16_t separator_height(MenuLayer *m,MenuIndex *i,void *ctx){','static int row_screen_top(int row){','static void move_menu(bool up){'])
 suffix='\nint main(void){frame_y='+str(head)+r''';
 MenuIndex first=MenuIndex(0,0),last=MenuIndex(0,6);
 assert(separator_height(menu,NULL,NULL)==0);assert(separator_height(NULL,&last,NULL)==0);
 assert(separator_height(menu,&first,NULL)==0);assert(separator_height(menu,&last,NULL)==0);
 viewport=30;assert(separator_height(menu,&last,NULL)==0);
 assert(header_height(menu,0,NULL)==0);assert(row_screen_top(2)==frame_y-90+96);
 selected=0;move_menu(true);assert(changes==0&&resets==0);
 selected=6;move_menu(false);assert(changes==0&&resets==0);
 selected=1;move_menu(true);assert(selected==0&&offset==0&&resets==1&&last_align==MenuRowAlignNone);
 move_menu(false);assert(selected==1&&last_align==MenuRowAlignCenter&&resets==1);
 page=HOME;assert(header_height(menu,0,NULL)>0);
 puts("PASS Round scroll: fixed header frame, native bottom padding, null callbacks, hard selection limits and complete return to first row");
}
'''
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp);(p/'scroll.c').write_text(prefix+funcs+suffix)
  subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'scroll.c'),'-o',str(p/'scroll')],check=True)
  subprocess.run([str(p/'scroll')],check=True)
