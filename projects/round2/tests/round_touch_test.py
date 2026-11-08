"""Replay physical Round 2 coordinates through the production touch handler."""
from pathlib import Path
import ast,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'src/c/main.c').read_text();a=s.index('static void __attribute__((unused)) touch_handler(const TouchEvent *event,void *context) {');b=s.index('{',a)+1;depth=1
while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
handler=s[a:b]
tree=ast.parse((root/'tests/touch_test.py').read_text());prefix=next(n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets))
prefix=prefix.replace('viewport_height=228','viewport_height=260').replace('point.y>=-272','point.y>=viewport_height-500').replace('return 34;','return 78;')
prefix+='\n#define UI_WIDTH 260\n#define UI_HEIGHT 260\n#define UI_LEFT 0\n#define UI_TOP 0\n'
suffix=r'''
static void raw(int type,int x,int y){TouchEvent e={type,false,x,y};touch_handler(&e,NULL);}
static void local(int type,int x,int y){raw(type,x,y);}
static void tap(int x,int y){raw(TouchEvent_Touchdown,x,y);raw(TouchEvent_Liftoff,0,0);}
int main(void){
 (void)num_layer;(void)other;
 tap(184,217);assert(up==1);tap(76,217);assert(down==1);tap(130,217);assert(selected==1);
 tap(10,10);tap(35,217);tap(103,217);assert(up==1&&down==1&&selected==1);
 tap(130,245);assert(popped==1);
 top=&d;tap(180,115);assert(date_field==2&&dirty==1);tap(105,115);assert(date_field==1);tap(60,115);assert(date_field==0);
 date_mode=1;tap(180,115);assert(date_field==1);tap(105,115);assert(date_field==0);
 top=&w;menu_selected.row=0;tap(130,102);assert(menu_activated==1);
 tap(10,10);assert(menu_activated==1);
 local(TouchEvent_Touchdown,130,180);local(TouchEvent_PositionUpdate,130,110);raw(TouchEvent_Liftoff,0,0);assert(menu_offset==-70&&menu_activated==1);
 local(TouchEvent_Touchdown,130,100);local(TouchEvent_PositionUpdate,130,200);assert(menu_offset==0);local(TouchEvent_PositionUpdate,130,180);assert(menu_offset==-20);raw(TouchEvent_Liftoff,0,0);
 local(TouchEvent_Touchdown,30,130);local(TouchEvent_PositionUpdate,110,130);raw(TouchEvent_Liftoff,0,0);assert(back_count==1);
 viewport_height=224;row_count=5;int activations=menu_activated;tap(130,240);assert(menu_activated==activations);
 viewport_height=260;local(TouchEvent_Touchdown,130,102);page++;raw(TouchEvent_Liftoff,0,0);assert(menu_activated==activations);
 puts("PASS Round 2 touch: full circular 260px coordinates, +/-/OK/Back, date fields, menu taps, inert corners/gaps/footer, hard scroll limits, Back swipe and page-change cancellation");
}
'''

with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'round.c').write_text(prefix+handler+suffix);subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'round.c'),'-o',str(p/'round')],check=True);subprocess.run([str(p/'round')],check=True)
