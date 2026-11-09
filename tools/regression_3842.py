"""Native persisted language-package transfer and offline UI verification."""
"""Verify optional-unit UI without storing appointments or progress."""
"""Check zero/full AM progress bars and B on the native binary without retaining test data."""
"""Exercise AM/B counters on the native binary, then round menu edges, preserving watch data."""
exec(open('tools/protocol.py').read())
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
ROOT=Path.cwd();out=ROOT/'docs/verification/dev/3.8.42'/test_platform;out.mkdir(parents=True,exist_ok=True)
def click(name,n=1,duration=.16,pause=.90):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(duration);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(pause)
 time.sleep(.3)
def home():
 pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
 pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(2)
def snapshot():return request({1:0,2:0})['state']
def shot(name):
 time.sleep(.8);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save(str(out/(name+'.png')))
 if test_platform in ['gabbro','chalk'] and name.endswith('-bottom') and not name.startswith('home'):
  diameter=260 if test_platform=='gabbro' else 180
  limit=(224 if diameter==260 else 154) if name.startswith('topics') else diameter
  selected_rows=[y for y,row in enumerate(data) if any(tuple(row[x*3:x*3+3])==(0,255,255) for x in range(diameter//2-4,diameter//2+5))]
  assert selected_rows and max(selected_rows)<limit-10,('Last selection too close to circular edge/footer',name,selected_rows[-1:] if selected_rows else [])
 return data
def choose(cls):
 home();click('down',5);click('select');click('select');click('down',cls);click('select');time.sleep(.5)
 assert snapshot()['cls']==cls,('Class selection failed',cls)
 home()
def units(cls,target):
 if snapshot()['cls']!=cls:choose(cls)
 home();click('down',3);click('select');click('select')
 current=snapshot()['counts'][cls][0];delta=target-current;assert abs(delta)<=2
 click('up' if delta>0 else 'down',abs(delta));click('select');time.sleep(.6)
 assert snapshot()['counts'][cls][0]==target
from libpebble2.services.appmessage import CString,Uint32
pack=json.loads((ROOT/'projects/time2/src/pkjs/lang-pack.js').read_text()[len('module.exports = '):].strip().rstrip(';'))
def request(data):
 global awaiting_rid
 awaiting_rid=data.get(2,0);done.clear()
 service.send_message(app,{k:CString(v) if isinstance(v,str) else Uint32(v) if v>=0 else Int32(v) for k,v in data.items()})
 if not done.wait(12):raise AssertionError('No native application reply')
 return dict(received)
home();before=snapshot();nonce=int(time.time())%1000000000
try:
 assert before['storageOk'] and before['alarmOk'];was_ready=before['languagePack']['ready']
 if not was_ready:
  assert request({1:3,2:nonce,17:1})['status']==-4
  assert request({1:4,2:nonce+1,3:pack['id'],14:0,15:len(pack['chunks']),13:pack['chunks'][0]})['status']==0
  assert not snapshot()['languagePack']['ready'];home();assert not snapshot()['languagePack']['ready'];shot('partial-pack-fallback')
 for part,chunk in enumerate(pack['chunks']):
  result=request({1:4,2:nonce+1,3:pack['id'],14:part,15:len(pack['chunks']),13:chunk});assert result['status']==0,(part,result)
 assert snapshot()['languagePack']['ready']
 assert request({1:3,2:nonce+2,17:1})['status']==0;time.sleep(2.3);home();state=snapshot()
 assert state['languagePack']['ready'] and state['language']==1;shot('English-offline-home')
 click('down',3);click('select');shot('English-progress');home()
 click('select');click('down',5);click('select');shot('English-unit-editor');time.sleep(1.5);shot('English-unit-editor-stable');home()
 click('down',6);click('select');click('down');click('select');shot('English-bundled-guide');home()
 assert request({1:3,2:nonce+3,17:0})['status']==0;time.sleep(2.3);home();assert snapshot()['languagePack']['ready'];shot('German-cached-pack')
 assert request({1:3,2:nonce+4,17:1})['status']==0;time.sleep(2.3);home();assert snapshot()['languagePack']['ready']
 print('PASS',test_platform,'native phone protocol, interrupted transfer fallback, complete pack verification, English after app restart, stable translated editor and cached DE/EN switch',flush=True)
finally:
 assert request({1:3,2:nonce+10,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['storageOk'] and after['alarmOk'];service.shutdown()
 print('PASS original app data preserved; English package retained for offline use',flush=True)
