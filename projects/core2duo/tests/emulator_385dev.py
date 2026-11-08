"""Measure visible title bounds in native DE/EN screenshots, preserving all data."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
measurements=[]
def click(name,n=1):
 for _ in range(n):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(.1)
  send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(.18)
 time.sleep(.15)
def shot(name,height=36):
 time.sleep(.3);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.5-(DEV)-'+name+'.png')
 points=[(x,y) for y,row in enumerate(data[:height]) for x in range(42,198) if list(row[x*3:x*3+3])==[255,255,255]]
 assert points,name+' missing header'
 x0=min(x for x,y in points);x1=max(x for x,y in points);y0=min(y for x,y in points);y1=max(y for x,y in points)
 dx=abs((x0+x1)/2-118.5);dy=abs((y0+y1)/2-(height-1)/2)
 measurements.append(dict(page=name,bounds=[x0,y0,x1,y1],horizontalError=dx,verticalError=dy))
 print(name,'ink bounds',x0,y0,x1,y1,'center deviation',dx,dy,flush=True)
 assert dx<=2 and dy<=2.5,(name,dx,dy)
def snapshot():return request({1:0,2:0})['state']
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-385-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
for lang,prefix in [(0,'DE'),(1,'EN')]:
 request({1:3,2:nonce+lang,17:lang});time.sleep(2.2)
 click('down',5);click('select');shot(prefix+'-Einstellungen');click('select');shot(prefix+'-Klasse');click('back');click('down');click('select');shot(prefix+'-Vorbesitz');click('back');click('back');click('back')
 for row,name in [(1,'Termine'),(2,'Stunden-Buchen'),(3,'Pflichtstunden'),(4,'Theorie')]:
  click('down',row);click('select');shot(prefix+'-'+name);click('back');click('back')
 click('select');shot(prefix+'-Planung');click('select');shot(prefix+'-Unterrichtsart');click('back');click('back')
 click('down',6);click('select');shot(prefix+'-Erklaerungen')
 for row,name in [(0,'Rechtliche-Vorgaben'),(1,'Bedingungen-Kuerzel'),(2,'Handy-Eingabe')]:
  if row:click('down')
  click('select');shot(prefix+'-'+name,46);click('back')
 click('back');click('back')
request({1:3,2:nonce+2,17:before['language']});time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
assert after['alarmOk'] and after['storageOk']
Path('/workspace/artifacts/Fahrschul-Planer-v3.8.5-(DEV)-Titelmessung.json').write_text(json.dumps(measurements,indent=2))
print('PASS Emery 3.8.5 DEV:',len(measurements),'DE/EN headers measured; visible text centers within 2px horizontally and 2.5px vertically; original data intact')
service.shutdown()
