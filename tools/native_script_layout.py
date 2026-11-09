"""Read-only navigation checks for resource-backed Greek/Cyrillic information pages."""
exec(open('tools/native_phone_bridge.py').read().split('home();before=')[0])
import png
from libpebble2.services.screenshot import Screenshot
from pebble_tool.commands.emucontrol import send_data_to_qemu,EmuButtonCommand
from libpebble2.communication.transports.qemu.protocol import QemuButton
version=json.loads(Path('release.json').read_text())['version'];out=Path('docs/verification/dev')/version/test_platform;out.mkdir(parents=True,exist_ok=True)
packs=json.loads(Path('projects/time2/tools/language-packets.json').read_text())['packs'];nonce=int(time.time())%1000000000
home();before=raw_request({1:0,2:0})['state']
def select_language(language):
 global nonce
 pack=next(p for p in packs if p['language']==language);home()
 for part,chunk in enumerate(pack['chunks']):
  nonce+=1;assert raw_request({1:4,2:nonce,3:pack['id'],14:part,15:len(pack['chunks']),13:chunk})['status']==0
 nonce+=1;assert raw_request({1:3,2:nonce,17:language})['status']==0;home();raw_request({1:0,2:0});time.sleep(1.5)
def click(name,count=1):
 for _ in range(count):
  send_data_to_qemu(pebble.transport,QemuButton(state=EmuButtonCommand.BUTTON_MAP[name]));time.sleep(.12);send_data_to_qemu(pebble.transport,QemuButton(state=0));time.sleep(1)
def capture(name):
 time.sleep(2.5) # Allow firmware window animations to settle under shared emulator CPU load.
 png.from_array(Screenshot(pebble).grab_image(),mode='RGB;8').save(str(out/(name+'.png')))
try:
 for locale,language in [('el',22),('bg',23)]:
  select_language(language);click('down',6);click('select');capture(locale+'-explanations')
  click('select');capture(locale+'-legal-top');click('down',5);capture(locale+'-legal-scrolled');click('back')
  click('down');click('select');capture(locale+'-guide-top');click('down',10);capture(locale+'-guide-scrolled');click('back')
  click('down');click('select');capture(locale+'-phone-input')
 print('PASS Greek/Cyrillic explanation-page navigation and resource-font rendering',test_platform,flush=True)
finally:
 select_language(before['language']);after=raw_request({1:0,2:0})['state']
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert before[key]==after[key],key
 (out/'script-layout.json').write_text(json.dumps(dict(platform=test_platform,version=version,greekCyrillicPagesCaptured=True,appDataPreserved=True),indent=2)+'\n');service.shutdown()
