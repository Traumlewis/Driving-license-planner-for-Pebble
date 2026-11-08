"""Inspect shared title/subtitle headers, long labels and confirmation headings in DE and EN."""
exec(open('tests/device_port_test.py').read().split("click('back');pebble")[0])
def home():
 pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.4)
 pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(.9)
home();before=snapshot();nonce=int(time.time())%1000000000
for language in [0,1]:
 nonce+=1;assert request({1:3,2:nonce,17:language})['status']==0;time.sleep(2.3);home()
 prefix='DE-' if not language else 'EN-'
 click('down',3);click('select');shot(prefix+'Pflichtstunden');click('select',duration=.8);shot(prefix+'Zusaetze');click('down',2);click('select');shot(prefix+'Zusaetze-Loeschen')
 home();click('select');click('select');click('down',5);click('select');click('down',6);click('select');shot(prefix+'Thema-Waehlen')
 home();click('down',4);click('select');shot(prefix+'Theorie')
 home();click('down',5);click('select');click('down');click('select');shot(prefix+'Vorbesitz')
nonce+=1;assert request({1:3,2:nonce,17:before['language']})['status']==0;time.sleep(2.3);home()
after=snapshot()
for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
print('PASS Time Round title/subtitle, extras/confirmation, topic selection and profile headers in DE/EN; original data restored')
service.shutdown()
