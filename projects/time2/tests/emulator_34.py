"""Run immediately after install: exercise the real manual GS/ZS editor and checkboxes."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
def click(name,n=1):
 if n:
  subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','180','--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.3)
def snapshot():return request({1:0,2:0})['state']
def topics_page():click('down',4);click('select')
def counter_page(k):click('down',3);click('select');click('down',k);click('select')
def set_count(k,current,value):
 counter_page(k);click('up' if value>current else 'down',abs(value-current));click('select');click('back')
def toggle(t):topics_page();click('down',t);click('select');click('back')
before=snapshot();cls=before['cls'];original=before['counts'][cls][:];mask=before['topics'][cls]
assert cls==4,'This emulator regression uses the saved class B profile'
for k,first,last in [(4,0,12),(5,12,14)]:
 for t in (first,first+1):
  if not snapshot()['topics'][cls]&(1<<t):toggle(t)
 now=snapshot();group=((1<<last)-1)^((1<<first)-1)
 protected=(now['topics'][cls]&group).bit_count();manual=now['counts'][cls][k]-protected
 # Extra minus presses stop at zero manual units, preserving all topic credit.
 counter_page(k);click('down',manual+3)
 if k==4:
  data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/v3.4-protected-gs.png')
 click('select');click('back')
 cleared=snapshot();assert cleared['counts'][cls][k]==protected and cleared['topics'][cls]==now['topics'][cls]
 set_count(k,0,2);assert snapshot()['counts'][cls][k]==protected+2
 toggle(first);assert snapshot()['counts'][cls][k]==protected+1
 toggle(first);assert snapshot()['counts'][cls][k]==protected+2
 set_count(k,2,0);assert snapshot()['topics'][cls]==now['topics'][cls]
 # Restore original topics and the exact original number of manual units.
 for t in range(first,last):
  if bool(snapshot()['topics'][cls]&(1<<t))!=bool(mask&(1<<t)):toggle(t)
 original_manual=original[k]-(mask&group).bit_count();set_count(k,0,original_manual)
after=snapshot();assert after['topics'][cls]==mask and after['counts'][cls]==original
assert after['storageOk'] and after['alarmOk']
data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/v3.4-home.png')
print('PASS native Emery: manual GS/ZS units clamp at zero and protect checkmarks, add/remove manual units and toggle topics independently; restore original topics and counts; alarms/storage remain healthy')
service.shutdown()
