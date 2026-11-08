"""Exercise all 24 slots through the constrained native watch AppMessage path; clean up own fixtures."""
exec(open('tests/emulator_protocol.py').read().split('state=request({1:0')[0])
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
before=request({1:0,2:0})['state'];state=before;created=[];nonce=int(time.time())%1000000000
now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time
try:
 for i in range(24-len(before['entries'])):
  nonce+=1;r=request({1:1,2:nonce,3:0,4:before['cls'],5:3,6:now+14*86400+i*3600,7:60,8:0,9:1,10:255,11:state['revision'],16:5});assert r['status']==0,r
  state=r['state'];created.append(state['savedId'])
 assert len(state['entries'])==24 and state['storageOk'] and state['alarmOk']
 full=request({1:0,2:nonce+1})['state'];assert len(full['entries'])==24
 print('PASS',test_platform,'24 native appointment slots, complete multipart snapshot, alarm/storage healthy',flush=True)
finally:
 state=request({1:0,2:0})['state']
 for entry_id in created:
  nonce+=1;r=request({1:2,2:nonce,3:entry_id,11:state['revision']});assert r['status']==0;state=r['state']
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==state[key],key
 print('PASS capacity fixtures removed; original watch data restored',flush=True)
 service.shutdown()
