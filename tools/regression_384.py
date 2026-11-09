"""Check zero/full AM progress bars and B on the native binary without retaining test data."""
"""Exercise AM/B counters on the native binary, then round menu edges, preserving watch data."""
exec(open('tools/protocol.py').read())
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
ROOT=Path.cwd();out=ROOT/'docs/verification/3.8.4'/test_platform;out.mkdir(parents=True,exist_ok=True)
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
home();before=snapshot();nonce=int(time.time())%1000000000
Path('/tmp/release384-'+test_platform+'-before.json').write_text(json.dumps(before))
try:
 assert request({1:3,2:nonce,17:0})['status']==0;time.sleep(2.3)
 choose(0);original=before['counts'][0][0];assert original<=2
 for value in [0,1,2,0]:
  units(0,value);shot('AM-'+str(value)+'-units')
 assert snapshot()['counts'][0][0]==0
 units(0,original)
 choose(4);original=before['counts'][4][0];units(4,original+1);shot('B-one-added');units(4,original)
 print('PASS',test_platform,'AM zero/one/two units captured; B defined goal captured',flush=True)
finally:
 for cls in [0,4]:
  current=snapshot()['counts'][cls][0]
  if current!=before['counts'][cls][0]:units(cls,before['counts'][cls][0])
 if snapshot()['cls']!=before['cls']:choose(before['cls'])
 assert request({1:3,2:nonce+10,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['storageOk'] and after['alarmOk']
 print('PASS original watch data restored; alarm/storage healthy',flush=True);service.shutdown()
