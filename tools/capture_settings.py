"""Recapture a stable settings view with slower physical button input."""
exec(open('tools/capture_store.py').read().split('home();before=')[0])
folder=ROOT/'store/screenshots/platforms'/test_platform
home();before=snapshot();nonce=int(time.time())%1000000000
try:
 assert request({1:3,2:nonce,17:1})['status']==0;time.sleep(2.5);home();time.sleep(1)
 click('down',5,duration=.07,pause=.8);time.sleep(.8);click('select',duration=.07,pause=.8);time.sleep(1);shot('05-settings',folder)
finally:
 assert request({1:3,2:nonce+1,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 print('PASS settings screenshot recaptured; original data restored')
 service.shutdown()
