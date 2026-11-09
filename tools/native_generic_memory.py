"""Measure real staged language memory and accept a language created after the build."""
exec(open('tools/native_phone_bridge.py').read().split('home();before=')[0])
import sys,png
from libpebble2.services.screenshot import Screenshot
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
sys.path.insert(0,str(Path.cwd()/'tools'))
from watch_packets import encode
version=json.loads(Path('release.json').read_text())['version'];out=Path('docs/verification/dev')/version/test_platform;out.mkdir(parents=True,exist_ok=True)
packs=json.loads(Path('projects/time2/tools/language-packets.json').read_text())['packs'];rows=[];nonce=int(time.time())%1000000000
home();before=raw_request({1:0,2:0})['state'];late_verified=False
def install(pack):
 global nonce
 home();rest=raw_request({1:0,2:0})['state']['languagePack'];nonce+=1;first=None
 for part,chunk in enumerate(pack['chunks']):
  nonce+=1
  response=raw_request({1:4,2:nonce,3:pack['id'],14:part,15:len(pack['chunks']),13:chunk});assert response['status']==0,(part,response)
  if part==0:first=response['state']['languagePack']
 nonce+=1;assert raw_request({1:3,2:nonce,17:pack['language']})['status']==0;home();state=raw_request({1:0,2:0})['state'];assert state['languagePack']['id']==pack['id'] and state['language']==pack['language'] and state['languagePack']['ready']
 rows.append(dict(locale=pack['locale'],language=pack['language'],payloadBytes=pack['size'],storedBytes=state['languagePack']['storedBytes'],heapBefore=rest['heapFree'],heapDuring=first['heapFree'],stagedBytes=first['stagedBytes'],heapAfter=state['languagePack']['heapFree']))
 return state
try:
 for pack in packs:
  install(pack)
  png.from_array(Screenshot(pebble).grab_image(),mode='RGB;8').save(str(out/(pack['locale']+'-home.png')))
  if pack['language']>=17:
   for section in ['middle','bottom']:
    for _ in range(3):
     send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP['down']));time.sleep(.1);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.3)
    png.from_array(Screenshot(pebble).grab_image(),mode='RGB;8').save(str(out/(pack['locale']+'-main-'+section+'.png')))
   home()
 # Codec and binary are already built. Only new data is generated here.
 late=json.loads(Path('Packs/App/Languages/es/watch-source.json').read_text());late.update(locale='es-XX',name='Prueba',language=42);late['strings']['Hinweis']='Información de prueba';install(encode(late));home();assert raw_request({1:0,2:0})['state']['language']==42;late_verified=True
 print('PASS native language 42 added after build, offline restart, all supported languages, memory samples',json.dumps(rows),flush=True)
finally:
 install(next(p for p in packs if p['language']==before['language']));after=raw_request({1:0,2:0})['state']
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 (out/'generic-memory.json').write_text(json.dumps(dict(platform=test_platform,version=version,measurements=rows,appDataPreserved=True,newLanguageWithoutBuild=late_verified),indent=2)+'\n');service.shutdown()
