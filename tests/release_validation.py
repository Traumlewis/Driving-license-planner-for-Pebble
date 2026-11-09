"""Validate the release version/credits, native package and required store assets."""
from pathlib import Path
import hashlib,json,re,struct,zipfile,sys
ROOT=Path(__file__).resolve().parents[1];cfg=json.loads((ROOT/'release.json').read_text());version=cfg['version'];credit=cfg['credits']
assert (ROOT/'VERSION').read_text().strip()==version
projects={'time2':['emery'],'core2duo':['flint'],'round2':['gabbro'],'time-pebble2':['basalt','diorite'],'timeround':['chalk']}
for name,platforms in projects.items():
 folder=ROOT/'projects'/name;pkg=json.loads((folder/'package.json').read_text())
 assert pkg['version']==version and pkg['author']==cfg['developer'] and pkg['pebble']['targetPlatforms']==platforms
 for path in [folder/'src/c/main.c',folder/'src/c/i18n.c']:
  source=path.read_text();assert '(DEV)' not in source and credit in source
  for m in re.finditer(r'"(?:\\.|[^"\\])*"',source):
   value=json.loads(m.group())
   if value.startswith(('FAHRSCHUL PLANER ','DRIVING PLANNER ')) and '\n\n' in value:
    assert value.endswith('\n\nVersion '+version+'\n'+credit)
    assert value.count(credit)==1
 for p in json.loads((folder/'tools/translations.json').read_text()).items():
  for s in p:assert len(s.encode())<1024
pbw=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'release'/('Fahrschul-Planer-v'+version+'.pbw')
with zipfile.ZipFile(pbw) as z:
 assert z.testzip() is None
 info=json.loads(z.read('appinfo.json'));assert info['versionLabel']==version and info['companyName']==cfg['developer']
 assert set(info['targetPlatforms'])=={'emery','flint','gabbro','basalt','diorite','chalk'}
 assert info['uuid']=='7a1cd9f4-32ba-485c-ae41-605cc3d148eb'
 for platform in info['targetPlatforms']:
  assert json.loads(z.read(platform+'/manifest.json'))['application']['size']==len(z.read(platform+'/pebble-app.bin'))
 assert z.read('phone/config.html')==(ROOT/'projects/time2/phone/config.html').read_bytes()
h,filename=Path(str(pbw)+'.sha256').read_text().strip().split(maxsplit=1);assert hashlib.sha256(pbw.read_bytes()).hexdigest()==h and filename==pbw.name
sizes={'emery':(200,228),'flint':(144,168),'gabbro':(260,260),'basalt':(144,168),'diorite':(144,168),'chalk':(180,180)}
scenes={'01-home.png','02-plan-appointment.png','03-required-lessons.png','04-theory-topics.png','05-settings.png'}
for platform,size in sizes.items():
 folder=ROOT/'store/screenshots/platforms'/platform;assert {p.name for p in folder.glob('*.png')}==scenes
 for p in folder.glob('*.png'):
  data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==size
manifest=json.loads((ROOT/'store/screenshot-manifest.json').read_text());assert len(manifest['models'])==8
for model in manifest['models']:
 assert model['count']==5 and len(model['files'])==5
 for entry in model['files']:assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
data=(ROOT/'store/banner.png').read_bytes();w,h=struct.unpack('>II',data[16:24]);assert (w,h)==(720,320)
print('PASS release metadata/version/credits, six-platform PBW/CRC/SHA, native resolutions, 40 model screenshots and exact 720x320 banner')
