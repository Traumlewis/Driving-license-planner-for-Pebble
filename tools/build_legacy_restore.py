#!/usr/bin/env python3
"""Build a DEV helper that restores legacy persistence, then restore normal build outputs."""
import argparse,concurrent.futures,json,subprocess
from pathlib import Path
from build_all import ROOT,PLATFORMS,merge

def build_projects(pebble):
    def build(project):
        result=subprocess.run([pebble,'build'],cwd=ROOT/'projects'/project,text=True,capture_output=True)
        if result.returncode:raise RuntimeError(project+'\n'+result.stdout+result.stderr)
        print('Built',project,flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(build,dict.fromkeys(PLATFORMS.values())))

def main(pebble,output):
    headers={p:p.read_text() for p in (ROOT/'projects').glob('*/src/c/compact_storage.h')}
    if len(headers)!=5 or any('#define COMPACT_WRITE_DEFAULT 1' not in text for text in headers.values()):raise ValueError('Expected normal compact storage defaults in all five projects')
    try:
        for p,text in headers.items():p.write_text(text.replace('#define COMPACT_WRITE_DEFAULT 1','#define COMPACT_WRITE_DEFAULT 0'))
        build_projects(pebble)
        merge({platform:ROOT/'projects'/project/'build'/(project+'.pbw') for platform,project in PLATFORMS.items()},output.resolve())
        print(output.resolve(),flush=True)
    finally:
        for p,text in headers.items():p.write_text(text)
        # Avoid leaving helper binaries in the normal project build directories.
        build_projects(pebble)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pebble',default='pebble');parser.add_argument('--output',type=Path)
    args=parser.parse_args();version=json.loads((ROOT/'release.json').read_text())['version']
    output=args.output or ROOT.parent/'artifacts'/('Fahrschul-Planer-v'+version+'-Legacy-Restore(DEV).pbw')
    main(args.pebble,output)
