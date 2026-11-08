"""Runs inside `pebble repl`; exercises real AppMessage/native storage in Emery."""
import json,time,threading
from pathlib import Path
from uuid import UUID
from libpebble2.services.appmessage import AppMessageService,Int32
service=AppMessageService(pebble)
app=UUID('7a1cd9f4-32ba-485c-ae41-605cc3d148eb')
received={};done=threading.Event();parts={};expected=0;awaiting_rid=0

def reply(tid,uuid,data):
 global expected,parts
 if uuid!=app or 13 not in data:return
 if data[14]==0:parts={};expected=data[15]
 parts[data[14]]=data[13]
 if len(parts)==expected:
  if data[2]!=awaiting_rid:return
  received.clear();received.update({'rid':data[2],'status':data[12],'state':json.loads(''.join(parts[i] for i in range(expected)))});done.set()
service.register_handler('appmessage',reply)
def request(data):
 global awaiting_rid
 awaiting_rid=data.get(2,0)
 done.clear();service.send_message(app,{k:Int32(v) for k,v in data.items()})
 if not done.wait(12):raise AssertionError('No native application reply')
 return dict(received)
state=request({1:0,2:0})['state'];print('Snapshot:',state['revision'],len(state['entries']),'entries; alarm=',state['alarmOk'])
# Use a date safely after the emulator's prior virtual-time tests.
when=int(time.time())+3*86400
base={1:1,2:600001,3:0,4:4,5:1,6:when,7:1440,8:30,9:2,10:255,11:state['revision']}
a=request(base);assert a['status']==0,a;assert len(a['state']['entries'])==len(state['entries'])+1
same=request(base);assert same['status']==0 and len(same['state']['entries'])==len(a['state']['entries'])
second=dict(base);second[2]=600002;second[5]=5;second[6]=when+86400;second[9]=1;second[10]=0;second[11]=a['state']['revision']
b=request(second);assert b['status']==0,b
stale=dict(base);stale[2]=600003;assert request(stale)['status']==-2
entry=next(e for e in b['state']['entries'] if e[3]==1)
edit=dict(base);edit[2]=600004;edit[3]=entry[0];edit[9]=3;edit[11]=b['state']['revision']
c=request(edit);assert c['status']==0,c
assert next(e for e in c['state']['entries'] if e[0]==entry[0])[4]==3
# Add and delete a disposable entry.
temp=dict(base);temp[2]=600005;temp[11]=c['state']['revision'];d=request(temp);assert d['status']==0,d
id_new=max(e[0] for e in d['state']['entries']);deleted=request({1:2,2:600006,3:id_new,11:d['state']['revision']});assert deleted['status']==0,deleted
assert len(deleted['state']['entries'])==len(c['state']['entries'])
Path('/workspace/artifacts/v2-protocol-state.json').write_text(json.dumps(deleted['state'],indent=2))
print('PASS native AppMessage: snapshot, add two, retry without duplication, stale revision rejection, edit, delete; retained',len(deleted['state']['entries']),'entries')
service.shutdown()
