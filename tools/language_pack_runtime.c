/* One persisted menu pack. Incoming data is staged in RAM until its checksum passes. */
#define PACK_CHUNK_SIZE 128
#define PACK_META_KEY 9000
#define PACK_DATA_KEY 9100
#define MAX_PACK_PARTS 19
typedef struct {uint32_t id,crc,size,language;} PackMeta;
static bool pack_ready;
static int active_language=-1,incoming_language=-1;
static uint32_t received_parts;
static uint8_t *incoming;
static int cached_page=-1;
static uint8_t pack_page[PACK_CHUNK_SIZE];
static char translated[16][96];
static unsigned translated_slot;
static uint16_t codec_cache[16][3];
static ResHandle codec_resource;
static unsigned pack_parts(const PackDef *p){return (p->size+PACK_CHUNK_SIZE-1)/PACK_CHUNK_SIZE;}
static uint32_t crc_update(uint32_t crc,const uint8_t *data,unsigned n){
 for(unsigned j=0;j<n;j++){crc^=data[j];for(int bit=0;bit<8;bit++)crc=(crc>>1)^((crc&1)?0xedb88320u:0);}
 return crc;
}
static uint32_t persisted_crc(const PackDef *p){
 uint32_t crc=0xffffffffu;uint8_t data[PACK_CHUNK_SIZE];
 for(unsigned part=0;part<pack_parts(p);part++){
  unsigned n=p->size-part*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;
  if(persist_get_size(PACK_DATA_KEY+part)!=(int)n||persist_read_data(PACK_DATA_KEY+part,data,n)!=(int)n)return 0;
  crc=crc_update(crc,data,n);
 }
 return crc^0xffffffffu;
}
static void clear_incoming(void){free(incoming);incoming=NULL;incoming_language=-1;received_parts=0;}
void language_pack_init(void){
 clear_incoming();PackMeta meta={0};cached_page=-1;memset(codec_cache,0,sizeof(codec_cache));pack_ready=false;active_language=-1;
 if(persist_get_size(PACK_META_KEY)!=(int)sizeof(meta)||persist_read_data(PACK_META_KEY,&meta,sizeof(meta))!=(int)sizeof(meta)||meta.language>1)return;
 const PackDef *p=&packet_defs[meta.language];
 if(meta.id!=p->id||meta.crc!=p->crc||meta.size!=p->size||persisted_crc(p)!=p->crc)return;
 active_language=meta.language;language=meta.language;pack_ready=true;
}
bool language_pack_ready(void){return pack_ready;}
int language_pack_language(void){return pack_ready?active_language:-1;}
uint32_t language_pack_id(void){return pack_ready?packet_defs[active_language].id:0;}
unsigned language_pack_size(void){return pack_ready?packet_defs[active_language].size:0;}
unsigned language_pack_staged(void){return incoming?packet_defs[incoming_language].size:0;}
unsigned language_pack_received(void){return incoming?received_parts:pack_ready?(1u<<pack_parts(&packet_defs[active_language]))-1:0;}
unsigned language_pack_stored(void){unsigned size=0;int n=persist_get_size(PACK_META_KEY);if(n>0)size+=n;for(int key=PACK_DATA_KEY;key<PACK_DATA_KEY+MAX_PACK_PARTS;key++){n=persist_get_size(key);if(n>0)size+=n;}return size;}
static int hex_value(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}
int language_pack_receive(uint32_t identity,unsigned part,unsigned total,const char *hex){
 int wanted=-1;for(int lang=0;lang<2;lang++)if(identity==packet_defs[lang].id)wanted=lang;
 if(wanted<0||!hex)return -1;
 const PackDef *p=&packet_defs[wanted];
 if(total!=pack_parts(p)||part>=total)return -1;
 unsigned n=p->size-part*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;
 if(strlen(hex)!=n*2)return -1;
 uint8_t data[PACK_CHUNK_SIZE];for(unsigned i=0;i<n;i++){int a=hex_value(hex[i*2]),b=hex_value(hex[i*2+1]);if(a<0||b<0)return -1;data[i]=(a<<4)|b;}
 if(pack_ready&&active_language==wanted)return 0;
 if(incoming_language!=wanted){
  if(part)return -1;
  clear_incoming();incoming=malloc(p->size);if(!incoming)return -3;incoming_language=wanted;
 }
 memcpy(incoming+part*PACK_CHUNK_SIZE,data,n);received_parts|=1u<<part;
 if(received_parts!=(1u<<total)-1)return 0;
 if((crc_update(0xffffffffu,incoming,p->size)^0xffffffffu)!=p->crc){clear_incoming();return -1;}
 /* The previous packet survives interrupted downloads. Commit has a recovery fallback. */
 if(persist_get_size(PACK_META_KEY)>=0&&persist_delete(PACK_META_KEY)<0){clear_incoming();return -3;}
 pack_ready=false;active_language=-1;cached_page=-1;
 for(unsigned i=0;i<total;i++){
  unsigned bytes=p->size-i*PACK_CHUNK_SIZE;if(bytes>PACK_CHUNK_SIZE)bytes=PACK_CHUNK_SIZE;
  if(persist_write_data(PACK_DATA_KEY+i,incoming+i*PACK_CHUNK_SIZE,bytes)!=(int)bytes){clear_incoming();return -3;}
 }
 for(unsigned i=total;i<MAX_PACK_PARTS;i++)if(persist_get_size(PACK_DATA_KEY+i)>=0&&persist_delete(PACK_DATA_KEY+i)<0){clear_incoming();return -3;}
 PackMeta meta={p->id,p->crc,p->size,(unsigned)wanted};
 if(persist_write_data(PACK_META_KEY,&meta,sizeof(meta))!=(int)sizeof(meta)){clear_incoming();return -3;}
 active_language=wanted;language=wanted;pack_ready=true;memset(codec_cache,0,sizeof(codec_cache));clear_incoming();return 0;
}
static bool codec_pair(unsigned index,uint16_t *a,uint16_t *b){
 const PackDef *p=&packet_defs[active_language];if(index>=p->tokens+p->trees)return false;
 uint16_t *entry=codec_cache[index%16];
 if(entry[0]!=index+1){
  uint8_t bytes[4];if(!codec_resource)codec_resource=resource_get_handle(RESOURCE_ID_LANGUAGE_CODEC);
  if(resource_load_byte_range(codec_resource,p->codec_base+index*4,bytes,4)!=4)return false;
  entry[0]=index+1;entry[1]=bytes[0]|bytes[1]<<8;entry[2]=bytes[2]|bytes[3]<<8;
 }
 *a=entry[1];*b=entry[2];return true;
}
static int packed_bit(unsigned bit){
 const PackDef *p=&packet_defs[active_language];unsigned byte=bit/8;if(byte>=p->size)return -1;int page=byte/PACK_CHUNK_SIZE;
 if(cached_page!=page){unsigned n=p->size-page*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;if(persist_read_data(PACK_DATA_KEY+page,pack_page,n)!=(int)n)return -1;cached_page=page;}
 return (pack_page[byte%PACK_CHUNK_SIZE]>>(7-bit%8))&1;
}
static bool expand_token(unsigned token,char *out,unsigned *length,unsigned depth){
 if(depth>64)return false;
 if(token<256){if(!token||*length>=95)return false;out[(*length)++]=(char)token;return true;}
 unsigned index=token-256;uint16_t a,b;const PackDef *p=&packet_defs[active_language];if(index>=p->tokens||!codec_pair(index,&a,&b))return false;
 return expand_token(a,out,length,depth+1)&&expand_token(b,out,length,depth+1);
}
static const char *unpack_text(unsigned id){
 unsigned bit=text_bits[id-1][active_language];char *out=translated[translated_slot++%16];unsigned length=0;const PackDef *p=&packet_defs[active_language];
 for(unsigned tokens=0;tokens<96;tokens++){
  int node=0;
  for(unsigned depth=0;node>=0&&depth<32;depth++){
   uint16_t a,b;if((unsigned)node>=p->trees||!codec_pair(p->tokens+node,&a,&b))return emergency_text(id);
   int next=packed_bit(bit++);if(next<0){pack_ready=false;return emergency_text(id);}node=(int16_t)(next?b:a);
  }
  if(node>=0)return emergency_text(id);
  unsigned token=-node-1;if(!token){out[length]=0;return out;}
  if(!expand_token(token,out,&length,0))return emergency_text(id);
 }
 return emergency_text(id);
}
const char *translate(const char *text){
 if(!text)return text;
 if(text[0]=='~'&&strlen(text)==5){unsigned id=0;for(int i=1;i<5;i++){int nibble=hex_value(text[i]);if(nibble<0)return text;id=id*16+nibble;}if(id>0&&id<=sizeof(text_bits)/sizeof(text_bits[0]))return pack_ready?unpack_text(id):emergency_text(id);}
 if(pack_ready&&active_language==1)for(unsigned i=0;i<sizeof(long_texts)/sizeof(long_texts[0]);i++)if(strcmp(text,long_texts[i].de)==0)return long_texts[i].en;
 return text;
}
