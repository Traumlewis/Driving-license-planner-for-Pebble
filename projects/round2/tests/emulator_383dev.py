"""Emery regression for class settings using hardware keys; raw touch is covered by touch_test.py."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','130','--repeat',str(n),'--interval','130'],check=True,capture_output=True);time.sleep(.25)
def shot(name):
 time.sleep(.5);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.3-(DEV)-'+name+'.png');return data
def snapshot():return request({1:0,2:0})['state']
def header(image):return tuple(tuple(row) for row in image[:36])
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-383-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
request({1:3,2:nonce,17:0});time.sleep(2.2)
click('down',5);click('select');settings=shot('Einstellungen');click('select');classes_image=shot('Klassen-OK');click('back')
click('select');assert header(shot('Klassen-Erneut'))==header(classes_image)
assert snapshot()['cls']==before['cls'],'Opening class list must not choose a class'
click('down',before['cls']);click('select');selected_image=shot('Klasse-Zurueck');assert header(selected_image)==header(settings),'Class choice must return to Settings'
# A later class change uses that class saved profile, without opening setup.
click('select');alternative=8 if before['cls']!=8 else 4;click('down',alternative);click('select');assert snapshot()['cls']==alternative
assert header(shot('Klasse-Gewechselt'))==header(settings)
click('select');click('down',before['cls']);click('select');assert snapshot()['cls']==before['cls']
click('down');click('select');profile_image=shot('Vorbesitz-Separat');assert header(profile_image)!=header(settings) and header(profile_image)!=header(classes_image)
click('back');click('back');click('back');request({1:3,2:nonce+1,17:before['language']});time.sleep(2.2)
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.8.3 DEV: OK opens class list without changing class; class choice/change returns to Settings; previous licence remains separate; original data restored')
service.shutdown()
