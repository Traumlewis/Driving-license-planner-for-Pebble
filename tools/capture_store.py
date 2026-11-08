"""Capture authentic English native screenshots and verify release credits; restore watch data."""
exec(open('tools/protocol.py').read())
import png,datetime
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
SIZES={'emery':(200,228),'flint':(144,168),'gabbro':(260,260),'basalt':(144,168),'diorite':(144,168),'chalk':(180,180)}
ROOT=Path.cwd();folder=ROOT/'store/screenshots/platforms'/test_platform;folder.mkdir(parents=True,exist_ok=True)
verify=ROOT/'docs/verification'/test_platform;verify.mkdir(parents=True,exist_ok=True)
def click(name,n=1,duration=.1,pause=.4):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(duration);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(pause)
 time.sleep(.3)
def home():
 pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
 pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.9)
def snapshot():return request({1:0,2:0})['state']
def shot(name,path=folder):
 time.sleep(.5);data=Screenshot(pebble).grab_image();size=SIZES[test_platform]
 assert len(data)==size[1] and len(data[0])==size[0]*3
 png.from_array(data,mode='RGB;8').save(str(path/(name+'.png')))
home();before=snapshot();assert before['cls']>=0,'Complete first-run licence selection before capturing'
nonce=int(time.time())%1000000000;created=None;topic_toggled=False
Path('/tmp/release382-'+test_platform+'-before.json').write_text(json.dumps(before))
try:
 r=request({1:3,2:nonce,17:1});assert r['status']==0;time.sleep(2.3)
 state=snapshot();now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
 r=request({1:1,2:nonce+1,3:0,4:before['cls'],5:1,6:now+10800,7:60,8:30,9:1,10:255,11:state['revision'],16:5});assert r['status']==0
 created=r['state']['savedId'];Path('/tmp/release382-'+test_platform+'-fixture.json').write_text(json.dumps({'id':created,'before':before}))
 time.sleep(2.3);home();shot('01-home')
 home();click('select');shot('02-plan-appointment')
 home();click('down',3);click('select');shot('03-required-lessons')
 home();click('down',4);click('select')
 if not before['topics'][before['cls']]&1:
  click('select');topic_toggled=True
 shot('04-theory-topics')
 if topic_toggled:click('select');topic_toggled=False
 assert snapshot()['topics']==before['topics']
 home();click('down',5);click('select');shot('05-settings')
 for language,label in [(1,'en'),(0,'de')]:
  r=request({1:3,2:nonce+2+language,17:language});assert r['status']==0;time.sleep(2.3);home()
  click('down',6);click('select');click('down');click('select');shot('guide-'+label+'-top',verify)
  click('down',60,duration=.05,pause=.12);shot('credits-'+label,verify)
 print('PASS',test_platform,'five native store screenshots and DE/EN guide/credits views captured',flush=True)
finally:
 home()
 if topic_toggled:
  click('down',4);click('select');click('select');home()
 state=snapshot()
 if created is not None and any(e[0]==created for e in state['entries']):
  r=request({1:2,2:nonce+10,3:created,11:state['revision']});assert r['status']==0;time.sleep(2.3)
 r=request({1:3,2:nonce+11,17:before['language']});assert r['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['alarmOk'] and after['storageOk']
 Path('/tmp/release382-'+test_platform+'-fixture.json').unlink(missing_ok=True)
 print('PASS',test_platform,'all original watch data restored, alarm/storage healthy',flush=True)
 service.shutdown()
