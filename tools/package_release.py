#!/usr/bin/env python3
"""Package the checked-in, validated PBW and source/store assets for a GitHub Release."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile,shutil
ROOT=Path(__file__).resolve().parents[1]

def package(output):
    cfg=json.loads((ROOT/'release.json').read_text());version=cfg['version']
    subprocess.run(['python3',str(ROOT/'tests/release_validation.py')],cwd=ROOT,check=True)
    source=ROOT/'release'/f'Fahrschul-Planer-v{version}.pbw'
    output.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,output/source.name)
    shutil.copyfile(Path(str(source)+'.sha256'),output/(source.name+'.sha256'))
    sourcezip=output/f'Fahrschul-Planer-v{version}-Quellcode.zip'
    subprocess.run(['git','archive','--format=zip',f'--prefix=Fahrschul-Planer-v{version}/','--output='+str(sourcezip.resolve()),'HEAD'],cwd=ROOT,check=True)
    storezip=output/f'Fahrschul-Planer-v{version}-Store-Assets.zip'
    with zipfile.ZipFile(storezip,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted((ROOT/'store').rglob('*')):
            if path.is_file():z.write(path,path.relative_to(ROOT).as_posix())
    for path in [sourcezip,storezip]:
        with zipfile.ZipFile(path) as z:
            if z.testzip() is not None:raise ValueError(f'Invalid ZIP CRC: {path}')
    files=sorted(path for path in output.iterdir() if path.is_file() and path.name!='SHA256SUMS.txt')
    (output/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n' for path in files))
    print(f'Packaged release {version}: {len(files)+1} download assets in {output}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'release-assets');args=p.parse_args();package(args.output.resolve())
