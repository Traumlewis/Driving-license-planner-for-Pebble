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
