"""Exercise production JSON serialization at maximum field widths and all 24 slots."""
from pathlib import Path
import re,subprocess,tempfile,json
s=(Path(__file__).resolve().parents[1]/'src/c/bridge.c').read_text();a=s.index('#define add(');b=s.index('static void send_part(',a);body=s[a:b]
code=r'''
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>
#define MAX_ENTRIES 24
static char snapshot[3072],error_text[120];static size_t length;static uint32_t revision=UINT32_MAX,request_id=UINT32_MAX;
static uint8_t language=1;static bool alarm_ok=false,storage_error=true;
static struct {int cls,profile;} cfg={15,9};
static uint16_t counts[16][6];static uint32_t topics[16];
static struct {uint8_t remainder[5];} practice[16];
typedef struct {bool active;uint32_t id,token;int32_t when;uint8_t cls,kind,units,topic,extra_minutes;uint16_t lead[2];} Entry;
static Entry entries[24];static int profile_extra(int cls){(void)cls;return 18;}
'''+body+r'''
int main(void){
 memset(counts,255,sizeof(counts));memset(topics,255,sizeof(topics));memset(practice,255,sizeof(practice));memset(error_text,'x',119);
 for(int i=0;i<24;i++)entries[i]=(Entry){true,UINT32_MAX,UINT32_MAX,INT32_MIN,255,255,255,255,255,{UINT16_MAX,UINT16_MAX}};
 build_snapshot();if(length>=sizeof(snapshot)-1)return 1;puts(snapshot);return 0;
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'capacity.c').write_text(code);subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',str(p/'capacity.c'),'-o',str(p/'capacity')],check=True);data=subprocess.check_output([str(p/'capacity')]).decode();state=json.loads(data);assert len(state['entries'])==24 and state['error']=='x'*119
 print('PASS snapshot capacity:',len(data.strip()),'bytes with every numeric field at storage limits; 3072-byte buffer complete')
