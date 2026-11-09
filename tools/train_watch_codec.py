#!/usr/bin/env python3
"""Explicit codec migration tool. Ordinary language registration never trains a codec."""
from pathlib import Path
import argparse, collections, heapq, itertools, json

ROOT = Path(__file__).resolve().parents[1]

def train(limit=8192, frequency_scale=1024, weights=None, locales=None, groups=None):
    if not 1<=limit<=16384 or not 1<=frequency_scale<=1024: raise ValueError("Invalid codec training limits")
    sources = [json.loads(p.read_text()) for p in sorted((ROOT/'Packs/App/Languages').glob('*/watch-source.json'))]
    if locales is not None:
        chosen=set(locales)
        if not chosen or chosen-{s['locale'] for s in sources}: raise ValueError('Missing training locale')
        sources=[s for s in sources if s['locale'] in chosen]
    sequences = [list(text.encode()) for source in sources for text in source['strings'].values()]
    dictionary = []
    for i in range(limit):
        freq = collections.Counter(pair for s in sequences for pair in zip(s, s[1:]))
        if not freq: break
        pair, count = min(freq.items(), key=lambda item: (-item[1], item[0]))
        if count < 2: break
        dictionary.append(pair)
        for k, s in enumerate(sequences):
            out = []; j = 0
            while j < len(s):
                if j+1 < len(s) and (s[j], s[j+1]) == pair:
                    out.append(256+i); j += 2
                else:
                    out.append(s[j]); j += 1
            sequences[k] = out
    if groups is not None:
        chosen={s['locale']:i for i,s in enumerate(sources)}
        flat=[locale for group in groups for locale in group]
        if not 1<=len(groups)<=64 or any(not group for group in groups) or len(set(flat))!=len(flat) or set(flat)!=set(chosen):raise ValueError('Groups must partition the training locales')
        weights=weights or {}
        if any(not isinstance(w,(int,float)) or not 0<w<=100 for w in weights.values()):raise ValueError('Invalid language weights')
        offsets=[];offset=0
        for source in sources:offsets.append(offset);offset+=len(source['strings'])
        books=[]
        for group in groups:
            frequency=collections.Counter()
            for locale in group:
                i=chosen[locale];weight=weights.get(locale,1.0)
                for sequence in sequences[offsets[i]:offsets[i]+len(sources[i]['strings'])]:
                    for token in sequence:frequency[token]+=weight
            serial=itertools.count();heap=[(max(1,round(frequency[token]*frequency_scale)),next(serial),token) for token in sorted(set(frequency)|set(range(256)))];heapq.heapify(heap)
            while len(heap)>1:
                a=heapq.heappop(heap);b=heapq.heappop(heap);heapq.heappush(heap,(a[0]+b[0],next(serial),(a[2],b[2])))
            codes={}
            def visit_group(node,code):
                if isinstance(node,int):codes[node]=code;return
                visit_group(node[0],code+[0]);visit_group(node[1],code+[1])
            visit_group(heap[0][2],[]);books.append(dict(codes=codes))
        return dict(dictionary=dictionary,books=books)
    weights = weights or {}
    sequence_weights = [weights.get(source['locale'],1.0) for source in sources for _ in source['strings']]
    if any(not isinstance(w,(int,float)) or not 0<w<=100 for w in sequence_weights): raise ValueError('Invalid language weights')
    freq = collections.Counter()
    for weight,sequence in zip(sequence_weights,sequences):
        for token in sequence: freq[token] += weight
    for token in range(256+len(dictionary)): freq[token] = max(1,round(freq[token]*frequency_scale))
    serial = itertools.count()
    heap = [(n, next(serial), token) for token, n in sorted(freq.items())]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap); b = heapq.heappop(heap)
        heapq.heappush(heap, (a[0]+b[0], next(serial), (a[2], b[2])))
    codes = {}
    def visit(node, code):
        if isinstance(node, int): codes[node] = code; return
        visit(node[0], code+[0]); visit(node[1], code+[1])
    visit(heap[0][2], [])
    return dict(dictionary=dictionary, codes=codes)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='A NEW codec filename; never overwrite a published codec')
    parser.add_argument('--limit',type=int,default=8192,help='Maximum merge count, at most 16384')
    parser.add_argument('--frequency-scale',type=int,default=1024,help='Weight actual tokens relative to unused fallback tokens')
    parser.add_argument('--weights',type=Path,help='Optional locale weights for a deliberately balanced shared book')
    parser.add_argument('--locales',help='Comma-separated frozen training locales for reproducibility')
    parser.add_argument('--groups',type=Path,help='Explicit LP5 training groups; no language IDs are stored in the decoder')
    args = parser.parse_args()
    if args.output.exists(): parser.error('Output exists; published codecs must remain frozen')
    codec = train(args.limit,args.frequency_scale,json.loads(args.weights.read_text()) if args.weights else None,args.locales.split(',') if args.locales else None,json.loads(args.groups.read_text()) if args.groups else None)
    args.output.write_text(json.dumps(codec, separators=(',', ':'))+'\n')
    print(len(codec['dictionary']), 'shared tokens; rebuild and publish a new compatibility variant')
