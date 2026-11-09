#!/usr/bin/env python3
"""Build the preserved device projects and package the six supported platforms."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
PLATFORMS={'emery':'time2','flint':'core2duo','gabbro':'round2','basalt':'time-pebble2','diorite':'time-pebble2','chalk':'timeround'}

def merge(inputs,output):
    """Merge one selected native platform from each input, validating shared files."""
    opened={path:zipfile.ZipFile(path) for path in set(inputs.values())}
    try:
        sources={p:opened[path] for p,path in inputs.items()}
        infos={p:json.loads(z.read('appinfo.json')) for p,z in sources.items()}
        base=infos['chalk'];cfg=json.loads((ROOT/'release.json').read_text());shared=['pebble-js-app.js','pebble-js-app.js.map','phone/config.html']
        for p,z in sources.items():
            if infos[p]['versionLabel']!=cfg['version'] or infos[p]['companyName']!=cfg['developer']:
                raise ValueError(f'Stale metadata in {p}; rebuild before packaging')
            if z.testzip() is not None:raise ValueError(f'Invalid ZIP CRC: {inputs[p]}')
            if p not in infos[p]['targetPlatforms']:raise ValueError(f'{inputs[p]} does not include {p}')
            for field in ['uuid','sdkVersion','messageKeys','appKeys','capabilities','usesPermissions','configPage','enableMultiJS','versionLabel','companyName']:
                if infos[p][field]!=base[field]:raise ValueError(f'Incompatible {field} in {p}')
            for name in shared:
                if z.read(name)!=sources['chalk'].read(name):raise ValueError(f'Incompatible shared {name} in {p}; build all projects with the same SDK')
        info=copy.deepcopy(base);info['versionLabel']=json.loads((ROOT/'release.json').read_text())['version'];info['targetPlatforms']=list(inputs);media=[]
        for p in inputs:
            for original in infos[p]['resources']['media']:
                if 'targetPlatforms' in original and p not in original['targetPlatforms']:continue
                item=copy.deepcopy(original)
                if item.get('menuIcon'):
                    if not any(x.get('menuIcon') for x in media):
                        item.pop('targetPlatforms',None);media.append(item)
                else:item['targetPlatforms']=[p];media.append(item)
        info['resources']['media']=media
        output.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('appinfo.json',json.dumps(info,ensure_ascii=False,indent=2)+'\n')
            for name in shared:z.writestr(name,sources['chalk'].read(name))
            for p,source in sources.items():
                names=[name for name in source.namelist() if name.startswith(p+'/')]
                for required in ['pebble-app.bin','app_resources.pbpack','manifest.json']:
                    if p+'/'+required not in names:raise ValueError(f'Missing {p}/{required}')
                for name in names:z.writestr(name,source.read(name))
        with zipfile.ZipFile(output) as z:
            if z.testzip() is not None:raise ValueError('Output CRC mismatch')
            for p,source in sources.items():
                for name in source.namelist():
                    if name.startswith(p+'/') and z.read(name)!=source.read(name):raise ValueError(f'Changed platform payload: {name}')
        Path(str(output)+'.sha256').write_text(hashlib.sha256(output.read_bytes()).hexdigest()+'  '+output.name+'\n')
    finally:
        for z in opened.values():z.close()
    return output

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pebble',default='pebble',help='Pebble CLI executable')
    parser.add_argument('--skip-build',action='store_true',help='Use existing project build/*.pbw outputs')
    parser.add_argument('--output',type=Path,help='Write a test PBW to this path instead of release/')
    args=parser.parse_args();inputs={}
    subprocess.run([__import__('sys').executable,str(ROOT/'tools/sync_release.py')],check=True)
    for folder in dict.fromkeys(PLATFORMS.values()):
        project=ROOT/'projects'/folder
        if not args.skip_build:
            subprocess.run([args.pebble,'clean'],cwd=project,check=True)
            subprocess.run([args.pebble,'build'],cwd=project,check=True)
        candidates=[p for p in (project/'build').glob('*.pbw') if p.name!='fahrschul-planer-multi.pbw']
        if len(candidates)!=1:raise SystemExit(f'Expected one native project PBW in {project}/build, got {len(candidates)}')
        for platform,target in PLATFORMS.items():
            if target==folder:inputs[platform]=candidates[0]
    output=ROOT/'release'/('Fahrschul-Planer-v'+json.loads((ROOT/'release.json').read_text())['version']+'.pbw')
    if args.output:output=args.output.resolve()
    merge({p:inputs[p] for p in PLATFORMS},output);print(output)

if __name__=='__main__':main()
