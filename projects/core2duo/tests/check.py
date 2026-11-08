from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    for name,extra in [('model_test',[]),('store_test',[str(root/'src/c/store.c')]),('i18n_test',[str(root/'src/c/i18n.c')])]:
        target=Path(tmp)/name
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-I',str(root/'tests/fake'),'-I',str(root/'src/c'),str(root/'tests'/f'{name}.c'),*extra,'-o',str(target)],check=True)
        subprocess.run([str(target)],check=True)

# A delayed callback for a previously consumed minute must not discard the next alarm.
import re
handler=re.search(r"static void wake_handler[^\n]+",(root/'src/c/main.c').read_text()).group(0)
code="""#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
typedef int WakeupId;
#define WAKE_KEY 4
static int wake_id=8,deleted=0,processed=0;
static void persist_delete(int key){assert(key==WAKE_KEY);deleted++;}
static void process_events(bool show){assert(show);processed++;}
"""+handler+"""
int main(void){wake_handler(7,321);assert(wake_id==8&&deleted==0);wake_handler(8,321);assert(wake_id==-1&&deleted==1&&processed==2);}
"""
with tempfile.TemporaryDirectory() as tmp:
    source=Path(tmp)/'race.c';target=Path(tmp)/'race';source.write_text(code)
    subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(source),'-o',str(target)],check=True)
    subprocess.run([str(target)],check=True)
print('PASS wakeup race: delayed old callback preserves the next scheduled alarm')
