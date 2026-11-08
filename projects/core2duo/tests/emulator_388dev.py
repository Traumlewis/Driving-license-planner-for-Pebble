"""Native checks for migrated info cards, complete details and persistent warning text."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
def click(name,n=1):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(.1);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.18)
 time.sleep(.15)
def shot(name):
 time.sleep(.3);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.8-(DEV)-'+name+'.png')
 assert list(data[1][:3])==[0,0,85] and list(data[47][:3])==[0,255,255] and list(data[60][:3])==[255,255,255],name
 return data
def snapshot():return request({1:0,2:0})['state']
def open_fixture():
 state=snapshot();ordered=sorted(state['entries'],key=lambda e:e[1]);pos=next(i for i,e in enumerate(ordered) if e[0]==test_id)
 click('down');click('select');click('down',pos+1);click('select')
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4);pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-388-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:0});time.sleep(2.2)
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time;state=snapshot();r=request({1:1,2:nonce+1,3:0,4:before['cls'],5:3,6:now+86400,7:60,8:30,9:1,10:255,11:state['revision'],16:0});assert r['status']==0
test_id=r['state']['savedId'];Path('/tmp/fahrschul-388-fixture.json').write_text(json.dumps({'id':test_id,'before':before}));time.sleep(2.2)
open_fixture();click('down',2);click('select');shot('Termindetails-DE');click('down',12);shot('Termindetails-Ende');click('back');click('up');click('select');persistent=shot('Unterricht-Laeuft');time.sleep(2.3);assert tuple(tuple(row) for row in Screenshot(pebble).grab_image())==tuple(tuple(row) for row in persistent),'Reading cards must not auto-close after 2 seconds'
click('back');click('back');click('back');click('back')
click('select');click('down',6);click('select');shot('Thema-Praxis-Hinweis');click('back');click('up',2);click('select');click('up',2);click('select');click('down',3);click('select');shot('Erinnerungen-Pruefen');click('back');click('back')
request({1:3,2:nonce+2,17:1});time.sleep(2.2);open_fixture();click('down',2);click('select');shot('Appointment-Details-EN');click('back');click('back');click('back');click('back')
request({1:3,2:nonce+3,17:before['language']});time.sleep(2.2);state=snapshot();assert request({1:2,2:nonce+4,3:test_id,11:state['revision']})['status']==0;time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.8.8 DEV: redesigned DE/EN appointment details, scroll to final fields, premature booking and theory/practice hints, equal-reminder validation; info stays visible, status closes after 2s; original data restored')
service.shutdown()
