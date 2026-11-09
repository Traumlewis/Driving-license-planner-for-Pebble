"""Language-independent LP4 packets. Codec training is frozen, never language registration."""
from pathlib import Path
import json,re,struct,zlib,hashlib
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1];MAX_BYTES=2560;FORMAT='LP4/shared-bpe-v1'
def normalize(text):return re.sub(r'(?i)((?:fahrschul planer|driving planner|version)\s+)\d+\.\d+\.\d+',lambda m:m.group(1)+'{version}',text)
def signature(text):
    tokens=re.findall(r'%(?:[-+# 0]*\d*(?:\.\d+)?)?[a-zA-Z%]',text)
    if text.count('%')!=sum(t.count('%') for t in tokens):raise ValueError('Unrecognized percent sequence: '+text)
    h=2166136261
    for b in ''.join(tokens).encode():h=((h^b)*16777619)&0xffffffff
    return h&65535

@lru_cache(maxsize=1)
def codec():
    source=json.loads((ROOT/'tools/watch-codec-v3.json').read_text());dictionary=source['dictionary'];codes={int(k):v for k,v in source['codes'].items()};tree=[]
    trie={}
    for token,bits in codes.items():
        current=trie
        for bit in bits:current=current.setdefault(bit,{})
        current['token']=token
    def node(current):
        if 'token' in current:return -current['token']-1
        i=len(tree);tree.append(None);tree[i]=(node(current[0]),node(current[1]));return i
    node(trie)
    raw=b''.join(struct.pack('<HH',*pair) for pair in dictionary)+b''.join(struct.pack('<hh',*pair) for pair in tree)
    return dictionary,codes,raw,len(tree)

def schema_id(schema):return zlib.crc32(json.dumps([(r['de'],r['maxBytes'],r['signature']) for r in schema],ensure_ascii=False,separators=(',',':')).encode())
def compatibility():
    schema=json.loads((ROOT/'tools/watch-schema.json').read_text());_,_,raw,_=codec();sid=schema_id(schema);cid=zlib.crc32(raw)
    return dict(format=FORMAT,schemaId=sid,codecId=cid,tag=f'{sid:08x}-{cid:08x}',maxBytes=MAX_BYTES)

def encode(source):
    schema=json.loads((ROOT/'tools/watch-schema.json').read_text());dictionary,codes,raw,trees=codec();compat=compatibility()
    if source.get('format')!='watch-source-v1' or not isinstance(source.get('strings'),dict):raise ValueError('Unsupported watch source format')
    locale=source['locale'];name=source['name'];language=source['language'];strings=source['strings']
    if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,2}',locale) or not isinstance(language,int) or isinstance(language,bool) or not 0<=language<=63 or not 1<=len(name.encode())<=23:raise ValueError('Invalid language metadata')
    if language<2 and locale!=['de','en'][language]:raise ValueError('Language numbers 0 and 1 are reserved for de/en')
    sequences=[]
    for row in schema:
        value=strings.get(row['de'])
        if not isinstance(value,str) or not value or '\x00' in value or len(value.encode())>row['maxBytes'] or signature(value)!=row['signature']:raise ValueError('Missing/invalid translation: '+row['en'])
        sequences.append(list(value.encode()))
    for i,pair in enumerate(dictionary):
        for k,s in enumerate(sequences):
            out=[];j=0
            while j<len(s):
                if j+1<len(s) and tuple(s[j:j+2])==tuple(pair):out.append(256+i);j+=2
                else:out.append(s[j]);j+=1
            sequences[k]=out
    bits=[];index=bytearray()
    for sequence in sequences:
        encoded=[b for t in sequence for b in codes[t]];n=len(encoded)
        while n>=128:index.append((n&127)|128);n>>=7
        index.append(n);bits.extend(encoded)
    payload=bytes(sum((bits[i+j] if i+j<len(bits) else 0)<<(7-j) for j in range(8)) for i in range(0,len(bits),8))
    body=name.encode()+index+payload;size=24+len(body)
    if size>MAX_BYTES:raise ValueError(f'Packet needs {size} bytes; limit {MAX_BYTES}. Shorten translations.')
    header=struct.pack('<4sIIIHBBI',b'LP4\x01',compat['schemaId'],compat['codecId'],0,size,language,len(name.encode()),zlib.crc32(body))
    identity=zlib.crc32(header[:12]+header[16:]+body)
    if not identity:raise ValueError('Reserved zero packet identity')
    header=header[:12]+struct.pack('<I',identity)+header[16:];packet=header+body
    return dict(format=FORMAT,schemaId=compat['schemaId'],codecId=compat['codecId'],locale=locale,name=name,language=language,id=identity,crc=zlib.crc32(packet),size=size,chunks=[packet[i:i+128].hex() for i in range(0,size,128)])

def register(source,base=None):
    base=Path(base) if base else ROOT/'Packs/App/Languages';compat=compatibility();packet=encode(source);folder=base/'watch'/compat['tag'];folder.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(packet,ensure_ascii=False,indent=2)+'\n').encode();path=folder/(source['locale']+'.json');path.write_bytes(raw)
    index_path=base/'index.json';index=json.loads(index_path.read_text());variants=index.setdefault('watchPacks',{});variant=variants.setdefault(compat['tag'],dict(compat,languages=[]));entry={k:packet[k] for k in ['locale','name','language','id','crc','size']};entry.update(file=path.relative_to(base).as_posix(),sha256=hashlib.sha256(raw).hexdigest())
    if not any(d['locale']==source['locale'] for d in index['settings']['languages']):raise ValueError('Register phone settings locale first')
    if any(d['language']==entry['language'] and d['locale']!=entry['locale'] for d in variant['languages']):raise ValueError('Duplicate watch language number')
    variant['languages']=[d for d in variant['languages'] if d['locale']!=entry['locale']]+[entry];variant['languages'].sort(key=lambda d:d['language']);index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');return packet
