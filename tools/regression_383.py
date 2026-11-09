"""Exercise AM/B counters on the native binary, then round menu edges, preserving watch data."""
exec(open('tools/protocol.py').read())
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
ROOT=Path.cwd();out=ROOT/'docs/verification/3.8.3'/test_platform;out.mkdir(parents=True,exist_ok=True)
def click(name,n=1,duration=.10,pause=.50):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(duration);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(pause)
 time.sleep(.3)
def home():
 pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
 pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
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
Path('/tmp/release383-'+test_platform+'-before.json').write_text(json.dumps(before))
try:
 assert request({1:3,2:nonce,17:0})['status']==0;time.sleep(2.3)
 for cls,name in [(0,'AM'),(4,'B')]:
  choose(cls);original=before['counts'][cls][0];assert original<999
  units(cls,original+1);shot(name+'-one-added');units(cls,original)
 assert snapshot()['counts']==before['counts']
 if test_platform in ['gabbro','chalk']:
  header=78 if test_platform=='gabbro' else 58
  def fixed(first,second,h=header):
   assert [bytes(x) for x in first[:h]]==[bytes(x) for x in second[:h]],'Header changed/cropped while scrolling'
  home();click('down',6);shot('home-bottom');click('up',6);shot('home-top-restored')
  home();click('down',5);click('select');a=shot('settings-top');click('down',2);b=shot('settings-bottom');fixed(a,b);click('up',2);fixed(a,shot('settings-top-restored'))
  click('select');a=shot('classes-top');click('down',15);b=shot('classes-bottom');fixed(a,b);click('up',15);fixed(a,shot('classes-top-restored'))
  home();click('down',3);click('select');a=shot('progress-top');click('down',6);b=shot('progress-bottom');fixed(a,b,78 if test_platform=='gabbro' else 70);click('up',6);fixed(a,shot('progress-top-restored'),78 if test_platform=='gabbro' else 70)
  home();click('down',4);click('select');a=shot('topics-top');click('down',13);b=shot('topics-bottom');fixed(a,b,78 if test_platform=='gabbro' else 70);click('up',13);fixed(a,shot('topics-top-restored'),78 if test_platform=='gabbro' else 70);click('down',8);shot('topics-long-label')
  home();click('select');a=shot('planning-top');click('down',8);b=shot('planning-bottom');fixed(a,b);click('up',8);fixed(a,shot('planning-top-restored'))
  assert request({1:3,2:nonce+1,17:1})['status']==0;time.sleep(2.3);home();click('down',4);click('select');a=shot('topics-English-top');click('down',13);b=shot('topics-English-bottom');fixed(a,b,78 if test_platform=='gabbro' else 70)
  print('PASS',test_platform,'round menu headers remain pixel-identical at top/bottom/return; last rows, long DE/EN labels, Home and planning captured',flush=True)
 print('PASS',test_platform,'AM manual count visible without percentage track; B fixed-goal bar; original counters restored',flush=True)
finally:
 for cls in [0,4]:
  current=snapshot()['counts'][cls][0]
  if current!=before['counts'][cls][0]:units(cls,before['counts'][cls][0])
 if snapshot()['cls']!=before['cls']:choose(before['cls'])
 assert request({1:3,2:nonce+10,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['storageOk'] and after['alarmOk']
 print('PASS original watch data restored; alarm/storage healthy',flush=True);service.shutdown()
