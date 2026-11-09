"""Native DEV verification; fixtures are removed explicitly after upgrade/rollback tests."""
exec(open('tools/native_phone_bridge.py').read().split('home();before=')[0])
from libpebble2.protocol.system import TimeMessage,GetTimeRequest
import os
phase=Path('/tmp/compact-native-phase').read_text().strip();out=Path('docs/verification/dev/3.8.50')/test_platform;out.mkdir(parents=True,exist_ok=True);fixture=out/'roundtrip-fixtures.json';baseline=json.loads(Path('/workspace/backups/3.8.49-before-compact-storage/'+test_platform+'-state.json').read_text())
home();state=raw_request({1:0,2:0})['state'];nonce=int(time.time()*1000)%1900000000
keys=['entries','counts','topics','remainders','language','cls','profile']
if phase=='seed':
 assert all(state[k]==baseline[k] for k in keys),('Before fixture creation',test_platform)
 assert state['storage']['compact'] and state['storageOk'] and state['alarmOk']
 now=pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time;ids=[]
 for kind,extra,topic,offset in [(1,20,255,10800),(5,0,2,21600)]:
  nonce+=1;r=raw_request({1:1,2:nonce,3:0,4:baseline['cls'],5:kind,6:now+offset,7:60,8:30,9:1,10:topic,11:state['revision'],16:extra});assert r['status']==0,r;state=r['state'];ids.append(state['savedId']);fixture.write_text(json.dumps(dict(ids=ids,state=state),indent=2))
 home();state=raw_request({1:0,2:0})['state'];fixture.write_text(json.dumps(dict(ids=ids,state=state),indent=2));print('PASS seeded native roundtrip',test_platform,state['storage'],flush=True)
elif phase=='cleanup':
 stored=json.loads(fixture.read_text());assert all(state[k]==stored['state'][k] for k in keys),('Before fixture cleanup',phase,test_platform)
 for identity in stored['ids']:
  nonce+=1;r=raw_request({1:2,2:nonce,3:identity,11:state['revision']});assert r['status']==0,r;state=r['state']
 home();state=raw_request({1:0,2:0})['state'];assert all(state[k]==baseline[k] for k in keys);assert state['storage']['compact'];print('PASS cleaned fixtures; all original data preserved',test_platform,state['storage'],flush=True)
else:
 stored=json.loads(fixture.read_text());assert all(state[k]==stored['state'][k] for k in keys),(phase,test_platform)
 if phase=='legacy':assert not state['storage']['compact'] and not state['storage']['compactRecords']
 if phase=='recompact':assert state['storage']['compact'] and state['storage']['compactRecords']
 print('PASS native storage roundtrip',phase,test_platform,state.get('storage'),flush=True)
assert state['storageOk'] and state['alarmOk'];(out/(phase+'.json')).write_text(json.dumps(state,indent=2));service.shutdown()
