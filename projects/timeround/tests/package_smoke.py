exec(open('tests/emulator_protocol.py').read().split('state=request({1:0')[0])
import png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.3)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
r=request({1:0,2:0});assert r['status']==0 and r['state']['storageOk'] and r['state']['alarmOk']
image=Screenshot(pebble).grab_image();size={'emery':(200,228),'flint':(144,168),'gabbro':(260,260),'chalk':(180,180)}[test_platform]
assert len(image)==size[1] and len(image[0])==size[0]*3
png.from_array(image,mode='RGB;8').save('/workspace/artifacts/Fahrschul-Planer-'+test_platform+'-v3.8.15-(DEV)-Startseite.png')
print('PASS combined PBW installed/launched on',test_platform,'correct screenshot size, native snapshot, alarm/storage healthy; no data mutations')
service.shutdown()
