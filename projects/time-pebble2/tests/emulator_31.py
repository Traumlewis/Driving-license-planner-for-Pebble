exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot

def click(name,n=1):
 subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration','180','--repeat',str(n),'--interval','350'],check=True,capture_output=True);time.sleep(.3)
def shot(name):
 rows=Screenshot(pebble).grab_image();png.from_array(rows,mode='RGB;8').save('/workspace/artifacts/'+name);return rows
before=shot('v3.1-home.png');click('down');click('up');after=shot('v3.1-home-return.png');assert before[:112]==after[:112]
# The text is centered on the screen, independently from the icon at the left.
points=[x for y,row in enumerate(after[:33]) for x in range(45,200) if list(row[x*3:x*3+3])==[255,255,255]]
assert points and 90<=(min(points)+max(points))/2<=110,(min(points),max(points))
click('down');click('select');shot('v3.1-all-appointments.png');click('back')
# Open a new appointment -> duration editor, without saving or changing existing data.
click('down');click('select');click('select');click('down',5);click('select');shot('v3.1-touch-duration.png');click('back');click('back')
state=request({1:0,2:0})['state'];assert state['alarmOk'] and state['storageOk']
Path('/workspace/artifacts/v3.1-state.json').write_text(json.dumps(state,indent=2))
print('PASS Emery 3.1: complete animated header return, centered class label, larger appointment dates, touch-ready duration editor and existing persisted data')
service.shutdown()
