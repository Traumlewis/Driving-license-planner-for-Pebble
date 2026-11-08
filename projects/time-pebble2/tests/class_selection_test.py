"""Production class selection: first setup versus later settings changes."""
from pathlib import Path
import subprocess,tempfile
s=(Path(__file__).resolve().parents[1]/'src/c/main.c').read_text()
a=s.index('static void choose_class(int cls){');b=s.index('\nstatic void select_row(MenuLayer *m,MenuIndex *idx',a)
helper=s[a:b]
code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
enum {SETTINGS,PROFILES};
static struct {int cls,profile;} cfg;
static int profiles[16],rules_loaded,config_saved,revision_saved,destination=-1,pushes,returns;
static void load_rules(void){rules_loaded++;assert(cfg.profile==profiles[cfg.cls]);}
static void store_config(void){config_saved++;}
static void store_revision(void){revision_saved++;}
static void show_page(int page){destination=page;pushes++;}
static void return_to(int page){destination=page;returns++;}
'''+helper+r'''
int main(void){
 profiles[4]=1;profiles[8]=3;cfg.cls=-1;choose_class(4);
 assert(cfg.cls==4&&cfg.profile==1&&destination==PROFILES&&pushes==1&&returns==0);
 choose_class(4);assert(cfg.cls==4&&cfg.profile==1&&destination==SETTINGS&&pushes==1&&returns==1);
 choose_class(8);assert(cfg.cls==8&&cfg.profile==3&&destination==SETTINGS&&pushes==1&&returns==2);
 choose_class(4);assert(cfg.cls==4&&cfg.profile==1&&destination==SETTINGS&&pushes==1&&returns==3);
 assert(rules_loaded==4&&config_saved==4&&revision_saved==4);
 puts("PASS classes: first setup opens previous licence; later choices return to settings and retain each saved profile");
}
'''
# Native MenuLayer tap recognition must not activate alongside the raw touch handler.
callbacks=s[s.index('menu_layer_set_callbacks(menu,'):s.index('layer_add_child(window_get_root_layer(window),menu_layer_get_layer(menu))')]
assert '.select_click=select_row' not in callbacks
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'classes.c').write_text(code)
 subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'classes.c'),'-o',str(p/'classes')],check=True)
 subprocess.run([str(p/'classes')],check=True)
