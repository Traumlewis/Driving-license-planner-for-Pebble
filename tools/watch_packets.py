"""Language-independent LP5 packets. Codec training is frozen, never language registration."""
from pathlib import Path
import json,re,struct,zlib,hashlib
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1];MAX_BYTES=2560;FORMAT='LP5/shared-bpe-v1'
def normalize(text):return re.sub(r'(?i)((?:fahrschul planer|driving planner|version)\s+)\d+\.\d+\.\d+',lambda m:m.group(1)+'{version}',text)
def signature(text):
    tokens=re.findall(r'%(?:[-+# 0]*\d*(?:\.\d+)?)?[a-zA-Z%]',text)
    if text.count('%')!=sum(t.count('%') for t in tokens):raise ValueError('Unrecognized percent sequence: '+text)
    h=2166136261
    for b in ''.join(tokens).encode():h=((h^b)*16777619)&0xffffffff
    return h&65535

@lru_cache(maxsize=1)
def codec():
    source=json.loads((ROOT/'tools/watch-codec-v7.json').read_text());dictionary=source['dictionary'];books=[{int(k):v for k,v in book['codes'].items()} for book in source['books']];tree=[];roots=[]
    def node(current):
        if 'token' in current:return -current['token']-1
        i=len(tree);tree.append(None);tree[i]=(node(current[0]),node(current[1]));return i
    for codes in books:
        trie={}
        for token,bits in codes.items():
            current=trie
            for bit in bits:current=current.setdefault(bit,{})
            current['token']=token
        roots.append(node(trie))
    if len(tree)>=32768 or not 1<=len(books)<=64:raise ValueError('Codec exceeds native bounds')
    raw=b''.join(struct.pack('<HH',*pair) for pair in dictionary)+b''.join(struct.pack('<hh',*pair) for pair in tree)+b''.join(struct.pack('<HH',root,0) for root in roots)
    return dictionary,books,raw,len(tree)

def schema_id(schema):return zlib.crc32(json.dumps([(r['de'],r['maxBytes'],r['signature']) for r in schema],ensure_ascii=False,separators=(',',':')).encode())
def compatibility():
    schema=json.loads((ROOT/'tools/watch-schema.json').read_text());_,_,raw,_=codec();sid=schema_id(schema);cid=zlib.crc32(raw)
    return dict(format=FORMAT,schemaId=sid,codecId=cid,tag=f'{sid:08x}-{cid:08x}',maxBytes=MAX_BYTES,codebooks=len(codec()[1]))

def apply_merges(sequences,dictionary):
    # Track the strings containing each pair instead of revisiting every string
    # for every merge. This preserves the frozen merge order and output bytes.
    positions={}
    for k,sequence in enumerate(sequences):
        for pair in set(zip(sequence,sequence[1:])):positions.setdefault(pair,set()).add(k)
    for i,pair in enumerate(dictionary):
        pair=tuple(pair)
        for k in tuple(positions.pop(pair,())):
            old=sequences[k];before=set(zip(old,old[1:]));out=[];j=0
            while j<len(old):
                if j+1<len(old) and old[j]==pair[0] and old[j+1]==pair[1]:out.append(256+i);j+=2
                else:out.append(old[j]);j+=1
            after=set(zip(out,out[1:]));sequences[k]=out
            for removed in before-after:
                members=positions.get(removed)
                if members is not None:
                    members.discard(k)
                    if not members:del positions[removed]
            for added in after-before:positions.setdefault(added,set()).add(k)
    return sequences

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
    sequences=apply_merges(sequences,dictionary)
    # Each book covers all bytes. Unknown intermediate merge tokens expand to
    # coded children, so future translations need data only, never new tables.
    candidates=[]
    for book,codeset in enumerate(codes):
        @lru_cache(maxsize=None)
        def token_bits(token):
            if token in codeset:return tuple(codeset[token])
            a,b=dictionary[token-256];return token_bits(a)+token_bits(b)
        lengths=[sum(len(token_bits(t)) for t in sequence) for sequence in sequences]
        directory=sum(1 if n<128 else 2 if n<16384 else 3 for n in lengths)
        candidates.append((24+len(name.encode())+directory+(sum(lengths)+7)//8,book,lengths))
    _,book,lengths=min(candidates);codeset=codes[book]
    @lru_cache(maxsize=None)
    def selected_bits(token):
        if token in codeset:return tuple(codeset[token])
        a,b=dictionary[token-256];return selected_bits(a)+selected_bits(b)
    bits=[];index=bytearray()
    for sequence,n in zip(sequences,lengths):
        bits.extend(b for t in sequence for b in selected_bits(t))
        while n>=128:index.append((n&127)|128);n>>=7
        index.append(n)
    payload=bytes(sum((bits[i+j] if i+j<len(bits) else 0)<<(7-j) for j in range(8)) for i in range(0,len(bits),8))
    body=name.encode()+index+payload;size=24+len(body)
    if size>MAX_BYTES:raise ValueError(f'Packet needs {size} bytes; limit {MAX_BYTES}. Shorten translations.')
    header=struct.pack('<4sIIIHBBI',b'LP5'+bytes([book]),compat['schemaId'],compat['codecId'],0,size,language,len(name.encode()),zlib.crc32(body))
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
