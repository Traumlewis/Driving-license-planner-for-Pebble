"""Native Emery typography, symbols and closed-app test alarm; preserves user data."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','100','--repeat',str(n),'--interval','100'],check=True,capture_output=True);time.sleep(.2)
def shot(name):
 time.sleep(.4);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.4-(DEV)-'+name+'.png');return data
def snapshot():return request({1:0,2:0})['state']
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-384-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:0});time.sleep(2.2)
click('down',5);click('select');shot('Einstellungen-Zahnrad');click('select');click('down',5);shot('Anhaenger-BE');click('down',4);shot('Anhaenger-Lkw');click('down',4);shot('Anhaenger-Bus');click('back');click('back');click('back')
click('down',6);click('select');click('select');shot('Rechtliche-Vorgaben');click('back');click('down');click('select');shot('Bedingungen-Kuerzel');click('back');click('down');click('select');shot('Handy-Eingabe');click('down',60);shot('Handy-Ende');click('back');click('back');click('back')
request({1:3,2:nonce+1,17:1});time.sleep(2.2);click('down',6);click('select');click('down',2);click('select');shot('Phone-English');click('back');click('back');click('back')
request({1:3,2:nonce+2,17:0});time.sleep(2.2);click('down',5);click('select');click('down',2);click('select');instructions=shot('Alarmtest-Anleitung');assert list(instructions[60][:3])==[255,255,255]
print('Native typography and symbols captured; waiting for closed-app test alarm',flush=True)
click('back');click('back');click('back');click('back')
# Wait for the actual one-minute system wakeup while the app is closed.
time.sleep(55)
result=shot('Alarmtest-Ergebnis')
assert tuple(tuple(row) for row in result[:48])==tuple(tuple(row) for row in instructions[:48]),'Test alarm must reopen in styled Alarmtest page'
assert list(result[60][:3])==[255,255,255]
click('back');request({1:3,2:nonce+3,17:before['language']});time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.8.4 DEV: centered headers, larger DE/EN explanations, gear/document icons, rear trailers; real closed-app alarm returns in matching design; original data intact')
service.shutdown()
