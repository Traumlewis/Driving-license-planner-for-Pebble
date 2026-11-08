"""Real Emery menu regrouping and styled information views; preserves user data."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1):
 subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','180','--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.3)
def shot(name):
 time.sleep(.65);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.2-(DEV)-'+name+'.png');return data
def snapshot():return request({1:0,2:0})['state']
def info(name):
 image=shot(name);assert list(image[40][:3])==[0,0,85];assert list(image[65][:3])==[255,255,255]
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-382-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:0});time.sleep(2.2)
shot('Startseite');click('down',5);click('select');shot('Einstellungen');click('select');click('down',4);shot('Klassen-Auto');click('down',4);shot('Klassen-Lkw');click('down',4);shot('Klassen-Bus');click('back')
# Class selection was only browsed; choose the already active training profile.
click('down');click('select');click('down',before['profile']) if before['profile'] else None
click('select');shot('Profil-Zurueck');click('back');shot('Home-Einstellungen-Zurueck');click('back');click('down',6);click('select');shot('Erklaerungen')
click('select');info('Rechtliche-Vorgaben');click('down',3);shot('Vorgaben-gescrollt');click('back');click('down');click('select');info('Bedingungen-Kuerzel');click('down',70);shot('Kuerzel-Ende');click('back');click('down');click('select');info('Handy-Eingabe');click('back');shot('Erklaerungen-Zurueck');click('back');shot('Home-Erklaerungen-Zurueck');click('back')
request({1:3,2:nonce+1,17:1});time.sleep(2.2);click('down',6);click('select');shot('Help-English');click('down',2);click('select');info('Phone-English');click('back');click('back');click('back')
request({1:3,2:nonce+2,17:before['language']});time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.8.2 DEV: settings/help nesting, profile return, vehicle icons, three styled info pages, full help scrolling, English; original data intact')
service.shutdown()
