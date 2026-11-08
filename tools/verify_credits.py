"""Capture the complete last lines of the guide on slower monochrome firmware."""
exec(open('tools/capture_store.py').read().split('home();before=')[0])
home();before=snapshot();nonce=int(time.time())%1000000000
try:
 for language,label in [(1,'en'),(0,'de')]:
  assert request({1:3,2:nonce+language+1,17:language})['status']==0;time.sleep(2.3);home()
  click('down',6);click('select');click('down');click('select')
  click('down',110,duration=.05,pause=.2);shot('credits-'+label,verify)
finally:
 assert request({1:3,2:nonce+10,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 print('PASS complete DE/EN footer recaptured; original data restored')
 service.shutdown()
