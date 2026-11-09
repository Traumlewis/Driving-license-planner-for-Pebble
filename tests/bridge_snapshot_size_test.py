"""Compile the real snapshot renderer with maximum-width fields and prove its bound."""
from pathlib import Path
import json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
for project in (ROOT/'projects').iterdir():
    source=(project/'src/c/bridge.c').read_text()
    declaration=re.search(r'static char snapshot\[\d+\],error_text\[\d+\];',source).group()
    macro=next(line for line in source.splitlines() if line.startswith('#define add('))
    renderer=source[source.index('static __attribute__((noinline)) void build_snapshot(void)'):source.index('void phone_push(')]
    protocol_enum=next(line for line in source.splitlines() if line.startswith('enum {OP='))
    prelude='''#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <assert.h>
static bool allow_storage=true;
#include "model.h"
static Config cfg={15,INT16_MIN};
static uint32_t revision=UINT32_MAX,topics[16];
static uint16_t counts[16][6];
static PracticeProgress practice[16];
static Entry entries[24];
static uint8_t language=UINT8_MAX;
static bool alarm_ok=false,storage_error=true;
static size_t length,offset,chunk_ends[16];static uint32_t request_id=0;
static int part,chunk_count,response_status;static bool sending;
static char assembled[4096];
typedef struct {int dummy;} DictionaryIterator;
#define APP_MSG_OK 0
static int app_message_outbox_begin(DictionaryIterator **d){static DictionaryIterator iterator;*d=&iterator;return APP_MSG_OK;}
static void dict_write_uint32(DictionaryIterator *d,int k,uint32_t v){(void)d;(void)k;(void)v;}
static void dict_write_int32(DictionaryIterator *d,int k,int32_t v){(void)d;(void)k;(void)v;}
static void dict_write_uint8(DictionaryIterator *d,int k,uint8_t v){(void)d;(void)k;(void)v;}
static void dict_write_cstring(DictionaryIterator *d,int k,const char *v){(void)d;(void)k;assert(strlen(v)<=650);strcat(assembled,v);}
static int app_message_outbox_send(void){return APP_MSG_OK;}
static int profile_extra(int cls){(void)cls;return UINT16_MAX;}
static unsigned store_bytes_used(void){assert(allow_storage);return UINT32_MAX;}
static unsigned store_compact_records(void){assert(allow_storage);return UINT32_MAX;}
static unsigned store_quota_bytes(void){assert(allow_storage);return UINT32_MAX;}
static bool store_uses_compact(void){assert(allow_storage);return false;}
static unsigned language_pack_id(void){return UINT32_MAX;}
static int language_pack_language(void){return UINT16_MAX;}
static unsigned language_pack_size(void){return UINT32_MAX;}
static bool language_pack_ready(void){return false;}
static unsigned language_pack_received(void){return UINT32_MAX;}
static unsigned language_pack_stored(void){return UINT32_MAX;}
static unsigned language_pack_staged(void){return UINT32_MAX;}
static unsigned heap_bytes_free(void){return UINT32_MAX;}
static unsigned language_pack_schema(void){return UINT32_MAX;}
static unsigned language_pack_codec(void){return UINT32_MAX;}
'''
    main='''static void emit_snapshot(void){
char original[4096];strcpy(original,snapshot);assembled[0]=0;offset=0;part=0;chunk_count=0;sending=true;size_t cursor=0;
while(cursor<length){size_t end=cursor+650;if(end>length)end=length;while(end<length&&((unsigned char)snapshot[end]&0xc0)==0x80)end--;chunk_ends[chunk_count++]=end;cursor=end;}
while(offset<length)send_part();
assert(!strcmp(snapshot,original)&&!strcmp(assembled,original));puts(assembled);
}
int main(void){
memset(counts,255,sizeof(counts));memset(topics,255,sizeof(topics));memset(practice,255,sizeof(practice));memset(error_text,'x',sizeof(error_text)-1);
for(int i=0;i<24;i++)entries[i]=(Entry){.active=1,.id=UINT32_MAX,.token=UINT32_MAX,.when=2147330000,.cls=15,.kind=3,.units=11,.topic=NO_TOPIC,.lead={2880,2865},.extra_minutes=40};
build_snapshot();emit_snapshot();request_id=UINT32_MAX;allow_storage=false;build_snapshot();emit_snapshot();return 0;}
'''
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'test.c';binary=Path(tmp)/'test';c.write_text(prelude+protocol_enum+'\n'+declaration+'\n'+macro+'\n'+renderer+main)
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-I',str(project/'src/c'),str(c),'-o',str(binary)],check=True)
        replies=subprocess.check_output([str(binary)],text=True).strip().splitlines();assert len(replies)==2
        capacity=int(re.search(r'snapshot\[(\d+)\]',declaration).group(1))
        for index,raw in enumerate(replies):
            data=json.loads(raw);assert len(data['entries'])==24 and len(data['counts'])==16 and 'languagePack' in data;assert ('storage' in data)==(index==0);assert len(raw.encode())+1<=capacity,len(raw.encode())
        print(project.name,max(len(raw.encode()) for raw in replies),'/ '+str(capacity)+' bytes; complete snapshot, ACK does not query persistence')
