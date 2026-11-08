"""Real Emery: compact lesson cells, 60/30 defaults, long-OK extras edit/delete."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
def click(name,n=1,duration=180):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration',str(duration),'--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.25)
def shot(name):time.sleep(.8);png.from_array(Screenshot(pebble).grab_image(),mode='RGB;8').save('/workspace/artifacts/'+name)
def snapshot():return request({1:0,2:0})['state']
def hold_row(row):click('down',row);click('select',duration=850)
before=snapshot();cls=before['cls'];assert cls==4
click('down');click('select');click('select');shot('v3.5-plan.png')
click('select');shot('v3.5-lesson-types.png');click('back');click('back')
# Theory: add two manual units via hold menu, remove them with confirmation, preserve checks.
click('down',3);click('select');hold_row(4);shot('v3.5-extra-actions.png');click('select');click('up',2);click('select');click('back')
assert snapshot()['counts'][cls][4]==before['counts'][cls][4]+2
hold_row(4);click('down');click('select');click('down');click('select')
protected=(before['topics'][cls]&0xfff).bit_count();assert snapshot()['counts'][cls][4]==protected and snapshot()['topics'][cls]==before['topics'][cls]
click('down',4);click('select');click('up',before['counts'][cls][4]-protected);click('select');click('back')
# Practical: edit and clear only the extra minutes; preserve whole units.
click('down',3);click('select');hold_row(0);click('down');click('select')
old=before['remainders'][cls][0]//5;click('up' if old<4 else 'down',abs(4-old));click('select');click('back')
assert snapshot()['remainders'][cls][0]==20
hold_row(0);click('down',2);click('select');click('down');click('select');assert snapshot()['remainders'][cls][0]==0
hold_row(0);click('down');click('select');click('up',old);click('select');click('back');click('back')
after=snapshot();assert after['counts'][cls]==before['counts'][cls] and after['topics'][cls]==before['topics'][cls] and after['remainders'][cls]==before['remainders'][cls]
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.5: compact planning/type screenshots, long-OK menu edits/deletes manual theory units without changing checks, edits/deletes practice extra minutes without changing whole units; original data restored')
service.shutdown()
