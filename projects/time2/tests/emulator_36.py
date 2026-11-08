"""Real Emery: normalize 45+ minutes and verify readable status disappears after 2s."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
def click(name,n=1,duration=180):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration',str(duration),'--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.25)
def shot(name):
 data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/'+name);return data
def snapshot():return request({1:0,2:0})['state']
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.7)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=snapshot();cls=before['cls'];original_units=before['counts'][cls][0];original_minutes=before['remainders'][cls][0]
click('down',3);click('select');click('select',duration=850);click('down');click('select')
old=original_minutes//5;click('up',9-old);shot('v3.6-minutes-45.png');click('select')
state=snapshot();assert state['counts'][cls][0]==original_units+1 and state['remainders'][cls][0]==0
click('back');click('select');click('down');click('select') # restore whole-unit counter
click('select',duration=850);click('down');click('select');click('up',old);click('select');click('back');click('back')
state=snapshot();assert state['counts'][cls]==before['counts'][cls] and state['remainders'][cls]==before['remainders'][cls] and state['topics']==before['topics']
home=shot('v3.6-home-before.png')
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
rid=int(time.time())%1000000000
data={1:1,2:rid,3:0,4:cls,5:1,6:now+7200,7:60,8:0,9:1,10:255,11:state['revision'],16:0}
created=request(data);assert created['rid']==rid and created['status']==0 and created['state']['savedId']>0
new_id=created['state']['savedId'];assert next(e for e in created['state']['entries'] if e[0]==new_id)[6]==0
deleted=request({1:2,2:rid+1,3:new_id,11:created['state']['revision']});assert deleted['rid']==rid+1 and deleted['status']==0
during=shot('v3.6-status-deleted.png');assert list(during[86][300:303])==[0,255,255]
time.sleep(2.2);after=shot('v3.6-status-closed.png');assert during!=after and home[:34]==after[:34]
final=snapshot();assert final['entries']==before['entries'] and final['counts']==before['counts'] and final['storageOk'] and final['alarmOk']
print('PASS Emery 3.6: minute editor crosses 40, 45 converts to a whole unit, data restored; Off stored natively; readable status visible and automatically dismissed after 2s')
service.shutdown()
