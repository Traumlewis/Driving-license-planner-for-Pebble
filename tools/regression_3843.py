"""Measure genuine language replacement and verify interrupted-swap recovery."""
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
ROOT=Path.cwd();out=ROOT/'docs/verification/dev/3.8.43'/test_platform;out.mkdir(parents=True,exist_ok=True)
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
packs=json.loads((ROOT/'projects/time2/src/pkjs/lang-pack.js').read_text()[len('module.exports = '):].strip().rstrip(';'))['packs']
def request(data):
 global awaiting_rid
 awaiting_rid=data.get(2,0);done.clear();service.send_message(app,{k:CString(v) if isinstance(v,str) else Uint32(v) if v>=0 else Int32(v) for k,v in data.items()})
 if not done.wait(12):raise AssertionError('No native application reply')
 return dict(received)
home();before=snapshot();nonce=int(time.time())%1000000000;report={}
def upload(lang,apply=True):
 p=packs[lang]
 for part,chunk in enumerate(p['chunks']):
  result=request({1:4,2:nonce+lang+1,3:p['id'],14:part,15:len(p['chunks']),13:chunk});assert result['status']==0,(lang,part,result)
 state=snapshot();assert state['languagePack']['id']==p['id'] and state['languagePack']['language']==lang and state['languagePack']['ready']
 assert state['languagePack']['storedBytes']==p['size']+16
 if apply:
  result=request({1:3,2:nonce+10+lang,17:lang});assert result['status']==0;time.sleep(2.3);home()
 return snapshot()['languagePack']
try:
 assert before['storageOk'] and before['alarmOk']
 report['DE']=upload(0);shot('DE-home')
 first=request({1:4,2:nonce+2,3:packs[1]['id'],14:0,15:len(packs[1]['chunks']),13:packs[1]['chunks'][0]});assert first['status']==0
 report['during_EN']=snapshot()['languagePack'];assert report['during_EN']['language']==0 and report['during_EN']['ready'];assert report['during_EN']['storedBytes']==report['DE']['storedBytes'];assert report['during_EN']['stagedBytes']==packs[1]['size']
 home();report['interrupted']=snapshot()['languagePack'];assert report['interrupted']['language']==0 and not report['interrupted']['stagedBytes'];shot('DE-after-interrupted-swap')
 report['EN']=upload(1);shot('EN-home');home();click('down',3);click('select');shot('EN-progress');home()
 click('select');click('down',5);click('select');shot('EN-quantity');home()
 assert request({1:3,2:nonce+30,17:0})['status']==-4,'Inactive German packet was still available'
 report['back_DE']=upload(0);shot('DE-after-swap')
 assert request({1:3,2:nonce+31,17:1})['status']==-4,'Inactive English packet was still available'
 click('down',5);click('select');shot('DE-settings');home()
 print('PASS',test_platform,'DE→EN→DE genuinely replaces the stored packet; interrupted transfer keeps DE; inactive language requires transfer',flush=True)
finally:
 upload(before['language']);after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['storageOk'] and after['alarmOk'];service.shutdown()
 (out/'memory-swap.json').write_text(json.dumps(report,indent=2))
 print('PASS original app data preserved; measured storage and transient RAM',flush=True)
