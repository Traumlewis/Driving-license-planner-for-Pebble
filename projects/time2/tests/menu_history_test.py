"""Execute production menu history and Back with recording menu/scroll APIs."""
from pathlib import Path
import tempfile,subprocess
s=(Path(__file__).resolve().parents[1]/'src/c/main.c').read_text()
enum=s[s.index('typedef enum {HOME'):s.index(' Page;')+6]
declarations=s[s.index('#define NAVIGATION_LIMIT'):s.index('static int navigation_depth;')+len('static int navigation_depth;')]
helpers=s[s.index('static MenuView capture_view('):s.index('\nstatic void surface_alerts(void) {')]
back=s[s.index('static void back(ClickRecognizerRef r,void *ctx){'):s.index('\nstatic void menu_up(')]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef void *ClickRecognizerRef;
typedef struct {int16_t x,y;} GPoint;
typedef struct {int16_t w,h;} GSize;
typedef struct {GPoint origin;GSize size;} GRect;
typedef struct {uint16_t section,row;} MenuIndex;
#define MenuIndex(s,r) ((MenuIndex){s,r})
#define GPointZero ((GPoint){0,0})
enum {MenuRowAlignTop,MenuRowAlignNone};
typedef int ScrollLayer;
'''+enum+'\n'+declarations+r'''
static Page page;static int menu,selected=-1,list_count,list_map[4],pops,forced_height;
static int completion_count;static struct {int cls;} cfg={4};
static struct {uint32_t id;bool active;} entries[4];
static MenuIndex current;static GPoint offset;static bool reversed;
static bool selected_valid(void){return selected>=0&&selected<4&&entries[selected].active;}
static int find_id(const void *unused,uint32_t id){(void)unused;for(int i=0;i<4;i++)if(entries[i].active&&entries[i].id==id)return i;return -1;}
static MenuIndex menu_layer_get_selected_index(int m){(void)m;return current;}
static ScrollLayer *menu_layer_get_scroll_layer(int m){(void)m;return &menu;}
static GPoint scroll_layer_get_content_offset(ScrollLayer *l){(void)l;return offset;}
static void menu_layer_set_selected_index(int m,MenuIndex i,int align,bool animated){(void)m;assert(!animated&&(align==MenuRowAlignTop||align==MenuRowAlignNone));current=i;}
static int scroll_layer_get_layer(ScrollLayer *l){(void)l;return 0;}
static GRect layer_get_bounds(int layer){(void)layer;return (GRect){{0,0},{200,228}};}
static GSize scroll_layer_get_content_size(ScrollLayer *l){(void)l;return (GSize){200,forced_height?forced_height:700};}
static void scroll_layer_set_content_offset(ScrollLayer *l,GPoint p,bool animated){(void)l;assert(!animated);offset=p;}
static int rows(int m,int section,void *ctx){(void)m;(void)section;(void)ctx;return page==LIST?list_count+1:page==PENDING?(list_count?list_count:1):12;}
static void refresh(void){list_count=0;for(int j=0;j<4;j++){int i=reversed?3-j:j;if(entries[i].active)list_map[list_count++]=i;}}
static void window_stack_pop(bool animated){assert(animated);pops++;}
static void clear_alerts(void){}
static void clear_completion(int i){(void)i;completion_count=0;}
static void surface_alerts(void);
'''+helpers+r'''
static void surface_alerts(void){show_event_page(COMPLETE_CONFIRM);}
'''+back+r'''
static void choose(int row,int scroll){current=MenuIndex(0,row);offset=(GPoint){0,scroll};}
int main(void){
 for(int i=0;i<4;i++){entries[i].id=100+i;entries[i].active=true;}
 reset_navigation(HOME);choose(1,-64);show_page(LIST);choose(3,-82);selected=2;show_page(ACTIONS);choose(4,-50);show_page(DELETE_CONFIRM);
 return_page();assert(page==ACTIONS&&current.row==4&&offset.y==-50&&selected==2);
 return_page();assert(page==LIST&&current.row==3&&offset.y==-82);
 return_page();assert(page==HOME&&current.row==1&&offset.y==-64&&navigation_depth==0);
 back(NULL,NULL);assert(page==HOME&&current.row==0&&offset.y==0&&pops==0);back(NULL,NULL);assert(pops==1);
 reset_navigation(HOME);choose(1,-70);show_page(LIST);choose(0,0);show_page(EDIT);choose(6,-120);show_page(TOPIC_PICK);
 back(NULL,NULL);assert(page==EDIT&&current.row==6&&offset.y==-120);
 back(NULL,NULL);assert(page==LIST&&current.row==0);back(NULL,NULL);assert(page==HOME&&current.row==1);
 // New settings/help tabs preserve their own selection and the home entry.
 reset_navigation(HOME);choose(5,-170);show_page(SETTINGS);choose(1,0);show_page(PROFILES);return_to(SETTINGS);assert(page==SETTINGS&&current.row==1&&navigation_depth==1);
 back(NULL,NULL);assert(page==HOME&&current.row==5&&offset.y==-170);
 reset_navigation(HOME);choose(6,-170);show_page(EXPLANATIONS);choose(2,0);show_page(LIST);return_page();assert(page==EXPLANATIONS&&current.row==2);return_page();assert(page==HOME&&current.row==6);
 // Reordering a list retains the same appointment ID, not merely its previous row number.
 reset_navigation(HOME);show_page(LIST);choose(2,-55);selected=1;show_page(ACTIONS);reversed=true;return_page();assert(page==LIST&&current.row==3);
 // If an ancestor appointment disappears, skip its stale actions page safely.
 selected=1;show_page(ACTIONS);show_page(EDIT);entries[1].active=false;return_page();assert(page==LIST&&current.row<=list_count);
 // A shorter list clamps the saved offset and selection to valid bounds.
 choose(3,-450);show_page(EDIT);entries[0].active=entries[2].active=entries[3].active=false;forced_height=100;return_page();assert(page==LIST&&current.row==0&&offset.y==0);forced_height=0;
 for(int i=0;i<4;i++)entries[i].active=true;
 reset_navigation(HOME);choose(3,-160);show_page(PROGRESS);choose(4,-140);show_page(PROGRESS_ACTIONS);choose(1,-30);show_page(PROGRESS_RESET);return_to(PROGRESS);assert(page==PROGRESS&&current.row==4&&offset.y==-140&&navigation_depth==1);
 return_page();assert(page==HOME&&current.row==3&&offset.y==-160);
 reset_navigation(HOME);show_page(EDIT);choose(6,-120);show_event_page(ALERT);int depth=navigation_depth;show_event_page(COMPLETE_CONFIRM);assert(navigation_depth==depth);return_page();assert(page==EDIT&&current.row==6&&offset.y==-120);
 reset_navigation(HOME);for(int i=0;i<40;i++)show_page(page==HOME?LIST:HOME);assert(navigation_depth==NAVIGATION_LIMIT);for(int i=0;i<NAVIGATION_LIMIT;i++)return_page();assert(navigation_depth==0);
 puts("PASS menu history: nested Back, selected row and scroll restoration, home anchor before exit, stable appointment identity, changed/deleted lists, extras, alert replacement and bounded history");
}
'''
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'history.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'history.c'),'-o',str(p/'history')],check=True)
 subprocess.run([str(p/'history')],check=True)
