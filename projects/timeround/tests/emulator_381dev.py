"""Real Emery coverage for the full-menu 3.8.1 DEV design, restoring all test data."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png,datetime
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1,duration=180):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration',str(duration),'--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.3)
def shot(suffix,delay=.7):
 time.sleep(delay);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-v3.8.1-(DEV)-'+suffix+'.png');return data
def snapshot():return request({1:0,2:0})['state']
click('back');pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.7)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();cls=before['cls'];assert cls==4;nonce=int(time.time())%1000000000
Path('/tmp/fahrschul-381-before.json').write_text(json.dumps(before))
request({1:3,2:nonce,17:before['language']});time.sleep(2.2)
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
when=int(datetime.datetime.fromtimestamp(now,datetime.timezone.utc).replace(hour=17,minute=0,second=0,microsecond=0).timestamp());when+=86400 if when<=now else 0
ids=[]
for j,kind in enumerate([3,5,1]):
 state=snapshot();r=request({1:1,2:nonce+j+1,3:0,4:cls,5:kind,6:when+j*86400,7:60,8:30,9:1,10:255,11:state['revision'],16:5 if kind<5 else 0});assert r['status']==0
 ids.append(r['state']['savedId']);Path('/tmp/fahrschul-381-fixtures.json').write_text(json.dumps({'ids':ids,'before':before}))
time.sleep(2.2);shot('Startseite');click('down');click('select');click('down');listing=shot('Alle-Termine')
assert list(listing[100][:3])==[0,255,255]
click('back');click('back');click('select');click('select');click('down',3);click('select');plan=shot('Termin-planen')
assert list(plan[60][:3])==[0,255,255]
click('down');click('select');shot('Datum');click('back');click('back') # date editor -> plan -> direct home origin
click('down',3);click('select');click('select');click('up');click('select');progress=shot('Pflichtstunden')
state=snapshot();assert state['counts'][cls][0]==before['counts'][cls][0]+1 and state['topics']==before['topics']
assert list(progress[70][:3])==[0,255,255]
click('select');click('down');click('select') # restore original whole units
click('select',duration=850);click('down');click('select');old=before['remainders'][cls][0]//5;click('up',10-old);shot('Minuten-50');click('back');click('back');click('back');click('back')
assert snapshot()['remainders']==before['remainders']
click('down',4);click('select')
if not before['topics'][cls]&1:click('select')
click('down')
if not before['topics'][cls]&2:click('select')
click('down');topics_image=shot('Theorie-Themen');assert list(topics_image[206][:3])==[0,0,85]
state=snapshot();assert state['counts'][cls][4]==before['counts'][cls][4]+int(not before['topics'][cls]&1)+int(not before['topics'][cls]&2)
click('up',2)
if not before['topics'][cls]&1:click('select')
click('down')
if not before['topics'][cls]&2:click('select')
assert snapshot()['topics']==before['topics']
click('back');click('back')
request({1:3,2:nonce+10,17:1});time.sleep(2.2);click('down',4);click('select');shot('Theory-English');click('back');click('back')
request({1:3,2:nonce+11,17:before['language']});time.sleep(2.2)
for j,id in enumerate(ids):
 state=snapshot();r=request({1:2,2:nonce+20+j,3:id,11:state['revision']});assert r['status']==0
status=shot('Bestaetigung',.2);assert list(status[86][300:303])==[0,255,255]
time.sleep(2.2);shot('Zurueck-Start')
after=snapshot();assert after['entries']==before['entries'] and after['counts']==before['counts'] and after['topics']==before['topics'] and after['remainders']==before['remainders'] and after['language']==before['language']
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.8.1 DEV: cyan list/editor selection, date editor, live progress counts/bars, 50-minute editor cancel, protected linked checkboxes, fixed footer, English and 2s success; all original data restored')
service.shutdown()
