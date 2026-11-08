exec(open('tools/capture_store.py').read().split('home();before=')[0])
home();before=snapshot();nonce=int(time.time())%1000000000
try:
 assert request({1:3,2:nonce,17:0})['status']==0;time.sleep(2.5);home();time.sleep(1)
 click('down',6,duration=.12,pause=.8);click('select',duration=.12,pause=.8);click('down',duration=.12,pause=.8);click('select',duration=.12,pause=.8)
 # Keep the button held: repeat scrolling continues until the actual content limit.
 click('down',duration=18,pause=2)
 shot('credits-de',verify)
finally:
 assert request({1:3,2:nonce+1,17:before['language']})['status']==0;time.sleep(2.3);home();after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 print('PASS German guide footer captured after continuous scroll; original data restored')
 service.shutdown()
