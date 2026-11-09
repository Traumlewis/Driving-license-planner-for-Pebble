#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include "i18n.h"
#include "language_pack_fixture.h"
uint8_t language;
int resource_get_handle(int id){assert(id==1);return 1;}
size_t resource_load_byte_range(int h,size_t offset,uint8_t *buffer,size_t n){assert(h==1&&offset+n<=sizeof(fixture_codec));memcpy(buffer,fixture_codec+offset,n);return n;}
static uint8_t records[20][256];static int sizes[20];static int available=4096-1500,used,writes,fail_after=-1;
static int index_of(int key){assert(key==9000||(key>=9100&&key<9119));return key==9000?19:key-9100;}
int persist_get_size(int key){return sizes[index_of(key)]?sizes[index_of(key)]:-1;}
int persist_read_data(int key,void *p,size_t n){int i=index_of(key);if(!sizes[i])return -1;if(n>(size_t)sizes[i])n=sizes[i];memcpy(p,records[i],n);return n;}
int persist_delete(int key){int i=index_of(key);used-=sizes[i];sizes[i]=0;return 0;}
int persist_write_data(int key,const void *p,size_t n){int i=index_of(key);assert(n<=256);if(fail_after==0||used-sizes[i]+(int)n>available)return -1;if(fail_after>0)fail_after--;used+=n-sizes[i];sizes[i]=n;memcpy(records[i],p,n);writes++;return n;}
static unsigned parts(int lang){unsigned n=0;while(fixture_chunks[lang][n])n++;return n;}
static void install(int lang){for(unsigned p=0;p<parts(lang);p++)assert(language_pack_receive(fixture_ids[lang],p,parts(lang),fixture_chunks[lang][p])==0);assert(language_pack_ready()&&language_pack_language()==lang);assert(used==(int)fixture_sizes[lang]+16);assert(used<=available);}
static void verify(int lang){assert(language==lang);for(unsigned i=0;i<sizeof(fixture_pairs)/sizeof(fixture_pairs[0]);i++){const char *actual=T(fixture_pairs[i][0]);if(strcmp(actual,fixture_pairs[i][lang+1])){fprintf(stderr,"Translation mismatch: %s => %s != %s\n",fixture_pairs[i][1],actual,fixture_pairs[i][lang+1]);assert(0);}}}
int main(void){
 language_pack_init();assert(!language_pack_ready());assert(language_pack_language()==-1);assert(!language_pack_staged());
 for(unsigned i=0;i<sizeof(fixture_pairs)/sizeof(fixture_pairs[0]);i++)if(!strcmp(fixture_pairs[i][1],"%d.%m. · %H:%M")||!strcmp(fixture_pairs[i][1],"%s | Klasse %s"))assert(!strcmp(T(fixture_pairs[i][0]),fixture_pairs[i][1]));
 assert(language_pack_receive(fixture_ids[0]+1,0,parts(0),fixture_chunks[0][0])==-1);
 assert(language_pack_receive(fixture_ids[0],0,parts(0),"zz")==-1);assert(language_pack_receive(fixture_ids[0],1,parts(0),fixture_chunks[0][1])==-1);
 install(0);verify(0);language_pack_init();verify(0);
 int old_used=used,before=writes;
 assert(language_pack_receive(fixture_ids[1],0,parts(1),fixture_chunks[1][0])==0);assert(language_pack_staged()==fixture_sizes[1]);assert(language_pack_language()==0&&used==old_used&&writes==before);verify(0);
 language_pack_init();assert(!language_pack_staged());verify(0);assert(used==old_used);
 /* Invalid fully received data leaves the previous language intact. */
 for(unsigned p=0;p<parts(1);p++){
  char chunk[257];snprintf(chunk,sizeof(chunk),"%s",fixture_chunks[1][p]);if(p==parts(1)-1)chunk[0]=chunk[0]=='0'?'1':'0';
  assert(language_pack_receive(fixture_ids[1],p,parts(1),chunk)==(p==parts(1)-1?-1:0));
 }
 verify(0);assert(used==old_used);install(1);verify(1);assert(!language_pack_staged());language_pack_init();verify(1);
 before=writes;install(1);assert(before==writes);
 install(0);verify(0);install(1);verify(1);
 /* Power/storage failure during the flash commit requires repair but never changes app keys. */
 fail_after=2;int result=0;for(unsigned p=0;p<parts(0);p++)result=language_pack_receive(fixture_ids[0],p,parts(0),fixture_chunks[0][p]);assert(result==-3);assert(!language_pack_ready()&&!language_pack_staged());
 language_pack_init();assert(!language_pack_ready());fail_after=-1;install(0);verify(0);
 records[0][0]^=1;language_pack_init();assert(!language_pack_ready());install(1);verify(1);
 printf("PASS language swap: one DE/EN pack, %u/%u bytes, interrupted/corrupt transfer preserves old language, commit recovery and 4KB quota with 1500 app bytes\n",fixture_sizes[0]+16,fixture_sizes[1]+16);
}
