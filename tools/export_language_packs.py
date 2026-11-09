#!/usr/bin/env python3
"""Export version-bound menu packets for the German training ruleset."""
from pathlib import Path
import hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[1]
PROJECTS=['time2','core2duo','time-pebble2','round2','timeround']
LOCALES={0:('de','Deutsch'),1:('en','English')}
def export():
    version=json.loads((ROOT/'release.json').read_text())['version'];catalogue=None
    for name in PROJECTS:
        folder=ROOT/'projects'/name
        if json.loads((folder/'package.json').read_text())['version']!=version:
            raise ValueError('Synchronize project versions before exporting language packets')
        data=json.loads((folder/'tools/language-packets.json').read_text())
        if catalogue is None:catalogue=data
        elif data!=catalogue:raise ValueError('Device projects contain different language packets')
    base=ROOT/'Packs/Germany/Languages';target=base/version;target.mkdir(parents=True,exist_ok=True)
    languages=[];seen=set()
    for packet in catalogue['packs']:
        code,label=LOCALES[packet['language']]
        if code in seen:raise ValueError('Duplicate packet locale')
        seen.add(code);chunks=[bytes.fromhex(c) for c in packet['chunks']]
        if not chunks or any(len(c)!=128 for c in chunks[:-1]) or not 0<len(chunks[-1])<=128:raise ValueError('Invalid packet chunk sizes')
        payload=b''.join(chunks)
        if len(payload)!=packet['size'] or zlib.crc32(payload)!=packet['crc']:raise ValueError('Packet length/CRC mismatch')
        content=(json.dumps(packet,ensure_ascii=False,indent=2)+'\n').encode()
        filename=code+'.json';(target/filename).write_bytes(content)
        languages.append(dict(locale=code,name=label,file=filename,language=packet['language'],packId=packet['id'],payloadBytes=len(payload),crc32=packet['crc'],sha256=hashlib.sha256(content).hexdigest()))
    manifest=dict(schemaVersion=1,trainingCountry='DE',rulesetDirectory='Germany',appVersion=version,format='LP3/swap128',scope='menu',languages=languages)
    (target/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    versions={}
    for path in sorted(base.glob('*/manifest.json')):
        entry=json.loads(path.read_text())
        if entry['appVersion']!=path.parent.name:raise ValueError('Version folder/manifest mismatch')
        versions[path.parent.name]=path.relative_to(base).as_posix()
    (base/'index.json').write_text(json.dumps(dict(schemaVersion=1,trainingCountry='DE',versions=versions),indent=2)+'\n')
    return target
if __name__=='__main__':print(export())
