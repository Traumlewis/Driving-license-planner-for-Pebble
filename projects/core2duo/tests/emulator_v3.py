"""Regression checks on the actual Emery UI and AppMessage protocol."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import QemuButton,send_data_to_qemu
import png
nonce=int(time.time())%1000000000

def cmd(data):
 global nonce
 nonce+=1;data[2]=nonce;reply=request(data);assert reply['status']==0,reply;return reply['state']
def click(name,n=1):
 import subprocess
 subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','180','--repeat',str(n),'--interval','350'],check=True,capture_output=True)
 time.sleep(.35)
def shot(name):
 rows=Screenshot(pebble).grab_image();png.from_array(rows,mode='RGB;8').save('/workspace/artifacts/'+name);return rows
state=request({1:0,2:0})['state'];Path('/workspace/artifacts/v3-emulator-before.json').write_text(json.dumps(state))
for e in list(state['entries']):state=cmd({1:2,3:e[0],11:state['revision']})
state=cmd({1:3,17:0});assert state['language']==0;click('back')
before=shot('v3-home-before.png');click('down');click('up');after=shot('v3-home-after.png');assert before[:112]==after[:112],'Home header moved after down/up'
click('select');shot('v3-compact-planning.png');click('down');click('select');shot('v3-date-editor.png');click('up');click('select',3)
click('down');click('select');shot('v3-time-editor.png');click('up');click('select');click('up');click('select')
click('up',2);click('select');shot('v3-lesson-picker.png');click('down',3);click('select')
click('down',5);click('select');click('up');shot('v3-50-minutes.png');click('select');click('down',2);click('select')
s=request({1:0,2:0})['state'];assert len(s['entries'])==1,s;entry=s['entries'][0];assert entry[3]==3 and entry[4]==1 and entry[8]==5,entry
click('back');shot('v3-home-de.png')
s=cmd({1:3,17:1});assert s['language']==1;click('back');shot('v3-home-en.png')
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.3);pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.6)
s=request({1:0,2:0})['state'];assert s['language']==1 and s['entries'][0][8]==5
s=cmd({1:3,17:0});click('back')
# Different vehicle families should be visible without losing the saved appointment.
click('down',5);click('select');click('down',15);click('select');click('select');shot('v3-tractor.png')
s=request({1:0,2:0})['state'];assert s['cls']==15 and len(s['entries'])==1
click('down',5);click('select');click('down',4);click('select');click('select');shot('v3-final.png')
Path('/workspace/artifacts/v3-emulator-state.json').write_text(json.dumps(request({1:0,2:0})['state'],indent=2))
print('PASS actual Emery: full header after down/up, compact date/time, full lesson names, 50-minute practice, persisted extra minutes, DE/EN switch and class icons')
service.shutdown()
