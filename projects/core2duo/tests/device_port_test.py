"""Native model-specific navigation, editors, reminders and phone protocol smoke test."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
def click(name,n=1,duration=.1):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(duration);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.18)
 time.sleep(.15)
def shot(name):
 time.sleep(.35);data=Screenshot(pebble).grab_image();expected=(144,168) if test_platform=='flint' else (260,260);assert len(data)==expected[1] and len(data[0])==expected[0]*3
 png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-'+test_platform+'-v3.8.9-(DEV)-'+name+'.png');return data
def snapshot():return request({1:0,2:0})['state']
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4);pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.8)
initial=snapshot()
if initial['cls']<0:click('down',4);click('select');click('select')
before=snapshot();nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:0});time.sleep(2.2);shot('Startseite')
click('down',5);click('select');shot('Einstellungen');click('select');click('down',15);shot('Klassen-Ende');click('up',15);click('back');click('back');click('back')
click('select');shot('Terminplanung');click('down');click('select');shot('Datum');click('back');click('down');click('select');shot('Uhrzeit');click('back');click('down',3);click('select');click('up');shot('Dauer-50');click('back');click('back')
click('down',3);click('select');shot('Pflichtstunden');click('select');shot('Zaehler');click('back');click('back');click('back')
click('down',4);click('select');shot('Theorie');click('select');click('select');assert snapshot()['topics']==before['topics'];click('back');click('back')
click('down',6);click('select');click('select');shot('Rechtliche-Vorgaben');click('down',12);shot('Info-Ende');click('back');click('back');click('back')
# A real save/update/delete path through the watch AppMessage protocol.
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time;state=snapshot();r=request({1:1,2:nonce+1,3:0,4:before['cls'],5:3,6:now+86400,7:60,8:0,9:1,10:255,11:state['revision'],16:5});assert r['status']==0
saved=r['state']['savedId'];assert next(e for e in r['state']['entries'] if e[0]==saved)[6]==0;time.sleep(2.2);shot('Termin-Startseite')
click('down');click('select');shot('Termine');ordered=sorted(snapshot()['entries'],key=lambda e:e[1]);index=next(i for i,e in enumerate(ordered) if e[0]==saved);click('down',index+1);click('select');click('down',2);click('select');shot('Termindetails');click('back');click('back');click('back');click('back')
request({1:3,2:nonce+2,17:1});time.sleep(2.2);click('down',5);click('select');shot('Settings-English');click('back');click('back')
request({1:3,2:nonce+3,17:before['language']});time.sleep(2.2);state=snapshot();assert request({1:2,2:nonce+4,3:saved,11:state['revision']})['status']==0;time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS',test_platform,'native: class browsing, menus, date/time/50min editors, counters, theory checkboxes, info scrolling, DE/EN, saved second Off and full phone protocol; original data restored')
service.shutdown()
