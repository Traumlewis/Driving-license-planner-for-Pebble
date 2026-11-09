/* One bounded additional language pack; German is the permanent fallback. */
#define PACK_CHUNK_SIZE 128
#define PACK_META_KEY 9000
#define PACK_DATA_KEY 9100
typedef struct {uint32_t id,crc,size;} PackMeta;
static bool pack_ready;
static uint32_t received_parts;
static int cached_page=-1;
static uint8_t pack_page[PACK_CHUNK_SIZE];
static char translated[16][64];
static unsigned translated_slot;
static uint32_t pack_crc(void){
 uint32_t crc=0xffffffffu;uint8_t data[PACK_CHUNK_SIZE];
 for(unsigned part=0;part<PACK_PARTS;part++){
  unsigned n=PACK_SIZE-part*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;
  if(persist_get_size(PACK_DATA_KEY+part)!=(int)n||persist_read_data(PACK_DATA_KEY+part,data,n)!=(int)n)return 0;
  for(unsigned j=0;j<n;j++){crc^=data[j];for(int bit=0;bit<8;bit++)crc=(crc>>1)^((crc&1)?0xedb88320u:0);}
 }
 return crc^0xffffffffu;
}
void language_pack_init(void){
 PackMeta meta={0};received_parts=0;cached_page=-1;
 pack_ready=persist_get_size(PACK_META_KEY)==(int)sizeof(meta)&&persist_read_data(PACK_META_KEY,&meta,sizeof(meta))==(int)sizeof(meta)&&meta.id==PACK_ID&&meta.crc==PACK_CRC&&meta.size==PACK_SIZE&&pack_crc()==PACK_CRC;
}
bool language_pack_ready(void){return pack_ready;}
uint32_t language_pack_id(void){return PACK_ID;}
unsigned language_pack_size(void){return PACK_SIZE;}
unsigned language_pack_received(void){return pack_ready?(1u<<PACK_PARTS)-1:received_parts;}
static int hex_value(char c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}
int language_pack_receive(uint32_t identity,unsigned part,unsigned total,const char *hex){
 if(identity!=PACK_ID||total!=PACK_PARTS||part>=PACK_PARTS||!hex)return -1;
 unsigned n=PACK_SIZE-part*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;
 if(strlen(hex)!=n*2)return -1;
 uint8_t data[PACK_CHUNK_SIZE];for(unsigned i=0;i<n;i++){int a=hex_value(hex[i*2]),b=hex_value(hex[i*2+1]);if(a<0||b<0)return -1;data[i]=(a<<4)|b;}
 if(pack_ready)return 0;
 if(!part&&!received_parts){
  if(persist_get_size(PACK_META_KEY)>=0&&persist_delete(PACK_META_KEY)<0)return -3;
  cached_page=-1;
 }
 if(part&&!received_parts)return -1;
 if(persist_write_data(PACK_DATA_KEY+part,data,n)!=(int)n)return -3;
 received_parts|=1u<<part;cached_page=-1;
 if(received_parts==(1u<<PACK_PARTS)-1){
  if(pack_crc()!=PACK_CRC){received_parts=0;return -1;}
  PackMeta meta={PACK_ID,PACK_CRC,PACK_SIZE};
  if(persist_write_data(PACK_META_KEY,&meta,sizeof(meta))!=(int)sizeof(meta))return -3;
  pack_ready=true;
 }
 return 0;
}
/* Decoder tables are read-only resources; the small cache avoids retaining them in RAM. */
static uint16_t codec_cache[16][3];
static ResHandle codec_resource;
static bool codec_pair(unsigned index,uint16_t *a,uint16_t *b){
 if(index>=TOKEN_COUNT+TREE_COUNT)return false;
 uint16_t *entry=codec_cache[index%16];
 if(entry[0]!=index+1){
  uint8_t bytes[4];if(!codec_resource)codec_resource=resource_get_handle(RESOURCE_ID_LANGUAGE_CODEC);
  if(resource_load_byte_range(codec_resource,index*4,bytes,4)!=4)return false;
  entry[0]=index+1;entry[1]=bytes[0]|bytes[1]<<8;entry[2]=bytes[2]|bytes[3]<<8;
 }
 *a=entry[1];*b=entry[2];return true;
}
static int packed_bit(unsigned bit){
 unsigned byte=bit/8;if(byte>=PACK_SIZE)return -1;
 int page=byte/PACK_CHUNK_SIZE;
 if(cached_page!=page){unsigned n=PACK_SIZE-page*PACK_CHUNK_SIZE;if(n>PACK_CHUNK_SIZE)n=PACK_CHUNK_SIZE;if(persist_read_data(PACK_DATA_KEY+page,pack_page,n)!=(int)n)return -1;cached_page=page;}
 return (pack_page[byte%PACK_CHUNK_SIZE]>>(7-bit%8))&1;
}
static bool expand_token(unsigned token,char *out,unsigned *length,unsigned depth){
 if(depth>64)return false;
 if(token<256){if(!token||*length>=60)return false;out[(*length)++]=(char)token;return true;}
 unsigned index=token-256;uint16_t a,b;if(index>=TOKEN_COUNT||!codec_pair(index,&a,&b))return false;
 return expand_token(a,out,length,depth+1)&&expand_token(b,out,length,depth+1);
}
static const char *unpack_text(unsigned bit,const char *fallback){
 char *out=translated[translated_slot++%16];unsigned length=0;
 for(unsigned tokens=0;tokens<64;tokens++){
  int node=0;
  for(unsigned depth=0;node>=0&&depth<32;depth++){
   uint16_t a,b;if((unsigned)node>=TREE_COUNT||!codec_pair(TOKEN_COUNT+node,&a,&b))return fallback;
   int next=packed_bit(bit++);if(next<0){pack_ready=false;return fallback;}node=(int16_t)(next?b:a);
  }
  if(node>=0)return fallback;
  unsigned token=-node-1;if(!token){out[length]=0;return out;}
  if(!expand_token(token,out,&length,0))return fallback;
 }
 return fallback;
}
const char *translate(const char *text){
 if(!language||!text)return text;
 /* Until all chunks pass verification, the entire UI remains in German. */
 if(!pack_ready)return text;
 for(unsigned i=0;i<sizeof(packed_texts)/sizeof(packed_texts[0]);i++)if(strcmp(text,packed_texts[i].de)==0)return unpack_text(packed_texts[i].bit,text);
 for(unsigned i=0;i<sizeof(long_texts)/sizeof(long_texts[0]);i++)if(strcmp(text,long_texts[i].de)==0)return long_texts[i].en;
 return text;
}
