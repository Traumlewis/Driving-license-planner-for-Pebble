#!/usr/bin/env python3
"""Register a translated settings-v1 JSON packet without building a PBW."""
from pathlib import Path
import argparse,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
def register(source,name,base=None):
    base=Path(base) if base else ROOT/'Packs/Germany/Languages'
    packet=json.loads(Path(source).read_text());locale=packet.get('locale')
    if not isinstance(locale,str) or not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,2}',locale):raise ValueError('Invalid locale')
    if locale in {'de','en'}:raise ValueError('Edit tools/settings-translations.json and run tools/export_settings_languages.py for DE/EN')
    if not isinstance(name,str) or not 1<=len(name)<=80:raise ValueError('Invalid language name')
    if packet.get('schemaVersion')!=1 or packet.get('format')!='settings-v1' or packet.get('trainingCountry')!='DE':raise ValueError('Unsupported packet format/country')
    required=json.loads((ROOT/'tools/settings-translations.json').read_text())['en']['strings']
    strings=packet.get('strings')
    if not isinstance(strings,dict) or any(not isinstance(strings.get(k),str) or not 1<=len(strings[k])<=2000 for k in required):raise ValueError('Missing/invalid translation')
    for key,count in [('kinds',7),('grounds',12)]:
        values=packet.get(key)
        if not isinstance(values,list) or len(values)!=count or any(not isinstance(v,str) or not 1<=len(v)<=200 for v in values):raise ValueError('Invalid '+key)
    raw=(json.dumps(packet,ensure_ascii=False,indent=2)+'\n').encode()
    if len(raw)>60000:raise ValueError('Packet exceeds 60KB limit')
    index_path=base/'index.json';index=json.loads(index_path.read_text());settings=index['settings']
    if settings['format']!='settings-v1':raise ValueError('Unsupported catalogue format')
    entries=settings['languages'];entry=dict(locale=locale,name=name,file=locale+'/settings.json',sha256=hashlib.sha256(raw).hexdigest(),watchLanguage=None)
    updated=[d for d in entries if d['locale']!=locale]+[entry]
    if len(updated)>64:raise ValueError('Language catalogue is full')
    folder=base/locale;folder.mkdir(parents=True,exist_ok=True);(folder/'settings.json').write_bytes(raw);settings['languages']=updated;index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');return folder/'settings.json'
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('packet',type=Path);parser.add_argument('--name',required=True);args=parser.parse_args();print(register(args.packet,args.name))
