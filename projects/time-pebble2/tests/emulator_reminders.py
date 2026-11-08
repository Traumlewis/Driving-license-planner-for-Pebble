"""Check both real persistent wakeups, snooze, and post-lesson confirmation."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
from libpebble2.protocol.system import TimeMessage,GetTimeRequest,SetUTC
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from libpebble2.services.screenshot import Screenshot
from pebble_tool.commands.emucontrol import QemuButton,send_data_to_qemu
import png
from datetime import datetime,timezone

def get_time():return pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
def start():pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.5)
def stop():pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.3)
def set_time(at):pebble.send_packet(TimeMessage(message=SetUTC(unix_time=at,utc_offset=0,tz_name='UTC')));time.sleep(.3)
def shot(name):
 # Same service used by the CLI; save directly without opening a desktop viewer.
 image=Screenshot(pebble).grab_image();png.from_array(image,mode='RGB;8').save('/workspace/artifacts/'+name)
state=request({1:0,2:0})['state']
for e in list(state['entries']):
 if e[3]==5 and e[7]==1:state=request({1:2,2:int(time.time())%1000000000+e[0],3:e[0],11:state['revision']})['state']
now=get_time();when=now+3700
nonce=int(time.time())%1000000000
base={1:1,2:nonce,3:0,4:4,5:5,6:when,7:30,8:15,9:1,10:1,11:state['revision']}
a=request(base);assert a['status']==0,a;entry=max(a['state']['entries'],key=lambda e:e[0]);entry_id=entry[0]
stop();set_time(when-1800-5);start();stop();time.sleep(7);shot('v2-erinnerung1.png')
print('Captured first reminder after closed app')
# Restart does not re-deliver consumed reminder. Second warning stays scheduled.
stop();set_time(when-900-5);start();stop();time.sleep(7);shot('v2-erinnerung2.png')
print('Captured second reminder after closed app')
def click(name):
 send_data_to_qemu(pebble.transport,QemuButton(state={'down':QemuButton.Button.Down,'select':QemuButton.Button.Select,'back':QemuButton.Button.Back}[name]));time.sleep(.1);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.3)
click('down');click('select');click('back')
snooze_at=get_time()+600
stop();set_time(snooze_at-5);start();stop();time.sleep(8);shot('v2-schlummern.png')
print('Captured ten-minute snooze')
# Restart past lesson time must ask for confirmation, never auto-book.
stop();set_time(when+5400-5);start();stop();time.sleep(7);shot('v2-abschlussfrage.png')
s=request({1:0,2:0})['state'];assert any(e[0]==entry_id for e in s['entries']);assert s['counts'][4][4]==a['state']['counts'][4][4]
Path('/workspace/artifacts/v2-reminder-state.json').write_text(json.dumps({'testId':entry_id,'when':when,'state':s},indent=2))
click('select');time.sleep(.5)
booked=request({1:0,2:0})['state'];assert not any(e[0]==entry_id for e in booked['entries']);assert booked['counts'][4][4]==s['counts'][4][4]+1;assert booked['topics'][4]&(1<<1)
shot('v2-stunden-gebucht.png')
print('PASS native wakeup flow: two reminders, ten-minute snooze, completion question, no automatic booking, confirmed count and topic update')
service.shutdown()
