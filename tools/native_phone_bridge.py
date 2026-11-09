"""Lab-only JSON-lines transport between the production PKJS test and a native emulator."""
exec(open('tools/protocol.py').read())
import sys
from libpebble2.services.appmessage import CString,Uint32
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
forward=False
output_lock=threading.Lock()
def emit(value):
 with output_lock:print('BRIDGE:'+json.dumps(value),flush=True)
def raw_reply(tid,uuid,data):
 if forward and uuid==app:emit({'type':'appmessage','payload':data})
service.register_handler('appmessage',raw_reply)
def home():
 pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.35)
 pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
def raw_request(data):
 global awaiting_rid
 awaiting_rid=data.get(2,0);done.clear();service.send_message(app,{k:CString(v) if isinstance(v,str) else Uint32(v) if v>=0 else Int32(v) for k,v in data.items()})
 if not done.wait(12):raise AssertionError('No native reply during lab cleanup')
 return dict(received)
home();before=raw_request({1:0,2:0})['state'];forward=True;emit({'type':'hello','language':before['language']})
try:
 for line in sys.stdin:
  command=json.loads(line)
  if command['action']=='message':service.send_message(app,{int(k):CString(v) if isinstance(v,str) else Uint32(v) if v>=0 else Int32(v) for k,v in command['data'].items()})
  elif command['action']=='restart':home();emit({'type':'restarted'})
  elif command['action']=='finish':break
finally:
 forward=False;current=raw_request({1:0,2:0})['state']
 # Recovery data is a lab fixture, never bundled in the production phone component.
 if current['language']!=before['language'] or not current['languagePack']['ready']:
  pack=json.loads(Path('projects/time2/tools/language-packets.json').read_text())['packs'][before['language']];nonce=int(time.time())%1000000000
  for part,chunk in enumerate(pack['chunks']):assert raw_request({1:4,2:nonce,3:pack['id'],14:part,15:len(pack['chunks']),13:chunk})['status']==0
  assert raw_request({1:3,2:nonce+1,17:before['language']})['status']==0
 home();after=raw_request({1:0,2:0})['state']
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 assert after['storageOk'] and after['alarmOk'];service.shutdown();emit({'type':'finished','appDataPreserved':True,'language':after['language']})
