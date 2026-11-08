"""Replay physical Round 2 coordinates through the production touch handler."""
from pathlib import Path
import ast,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'src/c/main.c').read_text();a=s.index('static void __attribute__((unused)) touch_handler(const TouchEvent *event,void *context) {');b=s.index('{',a)+1;depth=1
while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
handler=s[a:b]
tree=ast.parse((root/'tests/touch_test.py').read_text());prefix=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets))
prefix=prefix.replace('viewport_height=228','viewport_height=184').replace('point.y>=-272','point.y>=viewport_height-500').replace('return 34;','return 36;')
prefix+='\n#define UI_WIDTH 184\n#define UI_HEIGHT 184\n#define UI_LEFT 38\n#define UI_TOP 38\n'
suffix=r'''
static void raw(int type,int x,int y){TouchEvent e={type,false,x,y};touch_handler(&e,NULL);}
static void local(int type,int x,int y){raw(type,x+38,y+38);}
static void tap(int x,int y){local(TouchEvent_Touchdown,x,y);raw(TouchEvent_Liftoff,0,0);}
int main(void){
 (void)num_layer;(void)other;
 tap(154,161);assert(up==1);tap(30,161);assert(down==1);tap(92,161);assert(selected==1);
 raw(TouchEvent_Touchdown,10,199);raw(TouchEvent_Liftoff,0,0);assert(down==1); // outer round rim cannot press minus
 top=&d;tap(150,80);assert(date_field==2&&dirty==1);
 top=&w;menu_selected.row=0;tap(90,60);assert(menu_activated==1);
 raw(TouchEvent_Touchdown,10,98);raw(TouchEvent_Liftoff,0,0);assert(menu_activated==1);
 local(TouchEvent_Touchdown,90,140);local(TouchEvent_PositionUpdate,90,70);raw(TouchEvent_Liftoff,0,0);assert(menu_offset==-70&&menu_activated==1);
 local(TouchEvent_Touchdown,90,100);local(TouchEvent_PositionUpdate,90,200);assert(menu_offset==0);local(TouchEvent_PositionUpdate,90,180);assert(menu_offset==-20);raw(TouchEvent_Liftoff,0,0);
 local(TouchEvent_Touchdown,20,80);local(TouchEvent_PositionUpdate,100,80);raw(TouchEvent_Liftoff,0,0);assert(back_count==1);
 viewport_height=164;row_count=5;int activations=menu_activated;tap(90,174);assert(menu_activated==activations);
 viewport_height=184;local(TouchEvent_Touchdown,90,60);page++;raw(TouchEvent_Liftoff,0,0);assert(menu_activated==activations);
 puts("PASS Round 2 touch: physical 38px insets, +/-/OK, date fields, menu taps, inert outer rim and footer, hard scroll limits, Back swipe and page-change cancellation");
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'round.c').write_text(prefix+handler+suffix);subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'round.c'),'-o',str(p/'round')],check=True);subprocess.run([str(p/'round')],check=True)
