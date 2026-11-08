exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot

def click(name,n=1):
 subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','180','--repeat',str(n),'--interval','350'],check=True,capture_output=True);time.sleep(.25)
def shot(name):
 data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/'+name)
before=request({1:0,2:0})['state'];cls=before['cls'];counts_before=before['counts'][cls][:];mask=before['topics'][cls]
click('down',4);click('select');click('select');gs=request({1:0,2:0})['state'];assert gs['topics'][cls]==mask^1
expected=max(0,counts_before[4]-1) if mask&1 else counts_before[4]+1
assert gs['counts'][cls][4]==expected
click('down',12);click('select');zs=request({1:0,2:0})['state'];assert zs['topics'][cls]==mask^1^(1<<12)
expected_z=max(0,counts_before[5]-1) if mask&(1<<12) else counts_before[5]+1
assert zs['counts'][cls][5]==expected_z and zs['counts'][cls][4]==expected
shot('v3.3-topics.png');click('back');click('down',3);click('select');click('down',4);shot('v3.3-required-lessons.png')
click('back');click('down',4);click('select');click('select');click('down',12);click('select')
restored=request({1:0,2:0})['state'];assert restored['topics'][cls]==mask and restored['counts'][cls]==counts_before
assert restored['alarmOk'] and restored['storageOk']
click('back');shot('v3.3-home.png');click('back');time.sleep(1);shot('v3.3-launcher.png')
print('PASS actual Emery: GS/ZS checkbox counts update and revert, no other counters change; launcher screenshot captured')
service.shutdown()
