"""Capture native Round 2 info cards, lesson selection and timed status; restore language."""
exec(open('tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import png
from libpebble2.services.screenshot import Screenshot
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton

def click(name,n=1):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(.1);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.25)
 time.sleep(.15)
def shot(name):
 data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-gabbro-v3.8.11-(DEV)-'+name+'.png');return data
state=request({1:0,2:0})['state'];lang=state['language'];nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:lang});time.sleep(.3);status=shot('Status');time.sleep(2.1);home=shot('Startseite');assert status!=home
click('select');click('select');shot('Unterrichtsart');click('back');click('back')
click('down',6);click('select');click('down');click('select');shot('Kuerzel');click('back');click('down');click('select');shot('Handy-Eingabe');click('back');click('back');click('back')
click('down',5);click('select');click('down',2);click('select');shot('Alarmtest');click('back');click('back');click('back')
after=request({1:0,2:0})['state']
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert state[key]==after[key],key
print('PASS Round 2 native info/card layouts, lesson selection, status dismissal and original data preserved')
service.shutdown()
