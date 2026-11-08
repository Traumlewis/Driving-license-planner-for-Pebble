"""Real Emery DEV design: appointment dashboard, direct New, preserved navigation and language."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png,datetime
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1,duration=180):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration',str(duration),'--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.3)
def shot(name):
 time.sleep(.7);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/'+name);return data
def snapshot():return request({1:0,2:0})['state']
click('back') # dismiss any SDK system overlay before starting the app
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.7)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();Path('/tmp/fahrschul-dev38-before.json').write_text(json.dumps(before));nonce=int(time.time())%1000000000
# Return to the dashboard regardless of any legitimate old completion prompt at startup.
request({1:3,2:nonce,17:before['language']});time.sleep(2.2)
baseline=shot('Fahrschul-Planer-v3.8-(DEV)-Ausgangsdaten.png')
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
when=int(datetime.datetime.fromtimestamp(now,datetime.timezone.utc).replace(hour=17,minute=0,second=0,microsecond=0).timestamp())
if when<=now:when+=86400
state=snapshot();created=request({1:1,2:nonce+1,3:0,4:state['cls'],5:3,6:when,7:60,8:30,9:1,10:255,11:state['revision'],16:5});assert created['status']==0
fixture=created['state']['savedId'];assert fixture>0;Path('/tmp/fahrschul-dev38-fixture.json').write_text(json.dumps({'id':fixture,'before':before}));time.sleep(2.2)
home=shot('Fahrschul-Planer-v3.8-(DEV)-Vorschau.png')
assert list(home[170][:3])==[0,255,255] and list(home[210][:3])==[255,255,255]
click('down');all_selected=shot('Fahrschul-Planer-v3.8-(DEV)-Alle-Termine.png');assert home[:160]==all_selected[:160]
assert list(all_selected[170][:3])==[255,255,255] and list(all_selected[210][:3])==[0,255,255]
click('select');click('back');returned=shot('Fahrschul-Planer-v3.8-(DEV)-Zurueck.png');assert returned==all_selected
click('back');click('select');shot('Fahrschul-Planer-v3.8-(DEV)-Neuer-Termin.png')
click('back');again=shot('Fahrschul-Planer-v3.8-(DEV)-Start.png');assert again==home
# Existing deeper menus and the hold-OK workflow remain usable.
click('down',3);click('select');click('down',4);progress=shot('Fahrschul-Planer-v3.8-(DEV)-Pflichtstunden.png');click('select',duration=850);click('back');back=shot('Fahrschul-Planer-v3.8-(DEV)-Pflichtstunden-Zurueck.png');assert back==progress
click('back');click('back')
request({1:3,2:nonce+2,17:1});time.sleep(2.2);shot('Fahrschul-Planer-v3.8-(DEV)-English.png')
request({1:3,2:nonce+3,17:before['language']});time.sleep(2.2)
state=snapshot();deleted=request({1:2,2:nonce+4,3:fixture,11:state['revision']});assert deleted['status']==0;time.sleep(2.2)
after=snapshot();assert after['entries']==before['entries'] and after['counts']==before['counts'] and after['topics']==before['topics'] and after['language']==before['language']
assert after['alarmOk'] and after['storageOk']
print('PASS Emery DEV: cyan/white dashboard navigation, header retained for first two choices, direct New with existing appointments, Back position, extras menu and English; fixture removed and original data restored')
service.shutdown()
