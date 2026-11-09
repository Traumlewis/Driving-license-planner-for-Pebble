"""Exercise production unit/minute selection and duration application for every profile."""
from pathlib import Path
import json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def function(s,marker):
 a=s.index(marker);b=s.index('{',a)+1;depth=1
 while depth:depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]
for project in ['time2','core2duo','time-pebble2','round2','timeround']:
 folder=ROOT/'projects'/project;s=(folder/'src/c/main.c').read_text()
 prefix=r'''
#include <assert.h>
#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
'''+ '#include '+json.dumps(str(folder/'src/c/model.h'))+'\n#include '+json.dumps(str(folder/'src/c/rules.h'))+r'''
#define T(x) (x)
static Config cfg;static Entry draft;static Rule rules[10];static uint8_t profiles[16];
static PracticeProgress practice[16];
static int number_field,number_value,progress_counter,writes,edit_field,edit_value,edit_min,edit_max;
static const char *edit_title;static struct tm draft_tm;
static const uint16_t *targets(void){return rules[cfg.profile].target;}
static int topic_units(int c,int k){(void)c;(void)k;return 0;}
static void store_progress(int c){(void)c;writes++;}
static void store_revision(void){writes++;}
static void set_extra_minutes(int c,int k,int v){(void)c;(void)k;(void)v;writes++;}
static void set_progress_count(int c,int k,int v){(void)c;(void)k;(void)v;writes++;}
static void refresh(void){}
static void edit_number(int f,const char *title,int v,int min,int max){edit_field=f;edit_title=title;edit_value=v;edit_min=min;edit_max=max;}
'''
 code='\n'.join(function(s,m) for m in ['static bool draft_uses_minutes(void){','static bool progress_has_minutes(int counter){','static bool progress_can_hold(int counter){','static void apply_number('])
 a=s.index('case 5:if(draft_uses_minutes())edit_number');b=s.index('break;',a)+6
 code+='\nstatic void open_duration(void){switch(5){'+s[a:b]+'}}\n'
 suffix=r'''
int main(void){int cases=0;
 for(int cls=0;cls<16;cls++){
  int n=rules_for(cls,rules);cfg.cls=cls;
  for(int profile=0;profile<n;profile++){
   cfg.profile=profile;profiles[cls]=profile;
   for(int counter=0;counter<7;counter++){
    bool minutes=counter<4&&rules[profile].target[counter]>0;
    assert(progress_has_minutes(counter)==minutes);
    assert(progress_can_hold(counter)==(counter==4||counter==5||minutes));
    progress_counter=counter;number_field=17;number_value=8;writes=0;apply_number();assert((writes>0)==minutes);
   }
   for(int kind=0;kind<7;kind++){
    if(cls==14&&kind<5)continue;
    bool minutes=kind>0&&kind<5&&rules[profile].target[kind-1]>0;
    draft=(Entry){.cls=cls,.kind=kind,.units=2,.extra_minutes=5};
    assert(draft_uses_minutes()==minutes);
    cfg.cls=-1;assert(draft_uses_minutes()==minutes);cfg.cls=cls;
    open_duration();assert(edit_field==7&&edit_title);
    assert(edit_value==(minutes?19:2));assert(edit_min==(minutes?9:1));assert(edit_max==(minutes?108:12));
    number_field=7;number_value=minutes?10:2;apply_number();
    assert(draft.units==(minutes?1:2)&&draft.extra_minutes==(minutes?5:0));
    assert(duration_minutes(&draft)==(minutes?50:kind>=5?180:90));cases++;
   }
  }
 }
 printf("PASS %d class/profile/kind combinations: units/minutes editor, other-class profiles, duration application and protected extra-minute entry\n",cases);
}
'''
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp);(p/'policy.c').write_text(prefix+code+suffix)
  subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'policy.c'),'-o',str(p/'policy')],check=True)
  subprocess.run([str(p/'policy')],check=True)
