#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include "i18n.h"
#include "language_pack_fixture.h"
uint8_t language;
int resource_get_handle(int id){assert(id==1);return 1;}
size_t resource_load_byte_range(int h,size_t offset,uint8_t *buffer,size_t n){assert(h==1&&offset+n<=sizeof(fixture_codec));memcpy(buffer,fixture_codec+offset,n);return n;}

static uint8_t records[20][256];static int sizes[20];static int available=4096-1500,used,writes,fail_write;
static int index_of(int key){assert(key==9000||(key>=9100&&key<9119));return key==9000?19:key-9100;}
int persist_get_size(int key){return sizes[index_of(key)]?sizes[index_of(key)]:-1;}
int persist_read_data(int key,void *p,size_t n){int i=index_of(key);if(!sizes[i])return -1;if(n>(size_t)sizes[i])n=sizes[i];memcpy(p,records[i],n);return n;}
int persist_delete(int key){int i=index_of(key);used-=sizes[i];sizes[i]=0;return 0;}
int persist_write_data(int key,const void *p,size_t n){int i=index_of(key);assert(n<=256);if(fail_write||used-sizes[i]+(int)n>available)return -1;used+=n-sizes[i];sizes[i]=n;memcpy(records[i],p,n);writes++;return n;}
static unsigned parts(void){return sizeof(fixture_chunks)/sizeof(fixture_chunks[0]);}
static void install(void){for(unsigned p=0;p<parts();p++)assert(language_pack_receive(fixture_id,p,parts(),fixture_chunks[p])==0);assert(language_pack_ready());}
int main(void){
 language_pack_init();assert(!language_pack_ready());language=0;assert(!strcmp(T("Übungsfahrten"),"Übungsfahrten"));language=1;assert(!strcmp(T("Übungsfahrten"),"Übungsfahrten"));
 assert(language_pack_receive(fixture_id+1,0,parts(),fixture_chunks[0])==-1);assert(language_pack_receive(fixture_id,0,parts(),"zz")==-1);
 assert(language_pack_receive(fixture_id,1,parts(),fixture_chunks[1])==-1);
 assert(language_pack_receive(fixture_id,0,parts(),fixture_chunks[0])==0);assert(!language_pack_ready());language_pack_init();assert(!language_pack_ready());
 fail_write=1;assert(language_pack_receive(fixture_id,0,parts(),fixture_chunks[0])==-3);fail_write=0;install();assert(used<=available);
 int before=writes;install();assert(before==writes);
 for(unsigned i=0;i<sizeof(fixture_pairs)/sizeof(fixture_pairs[0]);i++){const char *actual=T(fixture_pairs[i][0]);if(strcmp(actual,fixture_pairs[i][1])){fprintf(stderr,"Translation mismatch: %s => %s != %s\n",fixture_pairs[i][0],actual,fixture_pairs[i][1]);assert(0);}}
 language_pack_init();assert(language_pack_ready());assert(!strcmp(T("Datum"),"Date"));language=0;assert(!strcmp(T("Datum"),"Datum"));language=1;
 records[0][0]^=1;language_pack_init();assert(!language_pack_ready());assert(!strcmp(T("Datum"),"Datum"));install();assert(!strcmp(T("Datum"),"Date"));
 assert(!strcmp(T("Praxis | Nachtfahrt"),"Practice | Night driving"));assert(!strcmp(T("Deine Klasse"),"Licence class"));
 printf("PASS language pack: %u bytes plus %d reserved app bytes within 4KB; complete EN coverage, offline reboot, interrupted/corrupt/failed transfers and cache reuse\n",language_pack_size(),1500);
}
