"""Verify the final round home margins with and without an appointment, restoring data."""
exec(open('tests/device_port_test.py').read().split("click('back');pebble")[0])
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4);pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.8)
before=snapshot();nonce=int(time.time())%1000000000
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
r=request({1:1,2:nonce,3:0,4:before['cls'],5:3,6:now+86400,7:60,8:0,9:1,10:255,11:before['revision'],16:5});assert r['status']==0;saved=r['state']['savedId'];time.sleep(2.3);shot('Termin-Startseite')
state=snapshot();assert request({1:2,2:nonce+1,3:saved,11:state['revision']})['status']==0;time.sleep(2.3);shot('Startseite')
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
assert after['alarmOk'] and after['storageOk']
print('PASS final Chalk home margins, 50-minute appointment and original data restored')
service.shutdown()
