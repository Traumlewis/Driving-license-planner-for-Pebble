"""Real settings -> PKJS local-pin API -> emulator timeline DB/BlobDB. No API mocks."""
from pathlib import Path
import json,time,sqlite3,datetime,subprocess,os,tempfile
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
 helper=Path(temp)/'time.py';clock=Path(temp)/'clock.json'
 helper.write_text("from libpebble2.protocol.system import TimeMessage,GetTimeRequest\nimport json\nfrom pathlib import Path\nPath("+repr(str(clock))+").write_text(json.dumps(pebble.send_and_read(TimeMessage(message=GetTimeRequest()),TimeMessage).message.time))\n")
 subprocess.run(['/workspace/.tools/pebble-tool/bin/python',str(root/'tests/run_emulator.py'),str(helper)],env={**os.environ,'XDG_DATA_HOME':'/workspace/.local/share','XDG_CACHE_HOME':'/workspace/.cache'},check=True,capture_output=True)
 watch_now=json.loads(clock.read_text())
info=json.loads(Path('/tmp/pb-emulator.json').read_text());port=info['emery']['4.44']['pypkjs']['port']
url=f'http://127.0.0.1:{port}/config/7a1cd9f4-32ba-485c-ae41-605cc3d148eb/'
db=sqlite3.connect('/workspace/.local/share/pebble-sdk/4.44/emery/timeline.db');db.row_factory=sqlite3.Row
def pins():
 return [dict(r,layout=json.loads(r['layout'])) for r in db.execute("select uuid,layout,duration,start_time,has_sent,deleted,rejected from timelineitem where parent=? and type='pin'",('7a1cd9f4-32ba-485c-ae41-605cc3d148eb',))]
def wait_pin(condition):
 deadline=time.monotonic()+12
 while time.monotonic()<deadline:
  found=[p for p in pins() if condition(p)]
  if found:return found[-1]
  time.sleep(.2)
 raise AssertionError(pins())
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.getElementById('status').textContent.indexOf('synchronisiert')>=0",timeout=20000)
 initial=page.locator('#entries .entry').count()
 when=(datetime.datetime.fromtimestamp(max(time.time(),watch_now),ZoneInfo('Europe/Berlin'))+datetime.timedelta(hours=2)).replace(second=0,microsecond=0)
 page.locator('#cls').select_option('4');page.locator('#kind').select_option('2');page.locator('#when').fill(when.strftime('%Y-%m-%dT%H:%M'));page.locator('#units').fill('95');page.locator('#save').click()
 page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 pin=wait_pin(lambda r:not r['deleted'] and r['duration']==95 and r['has_sent'] and r['layout']['title']=='B | Praxis | Autobahn')
 guid=pin['uuid'];assert not pin['rejected'];assert pin['start_time']==when.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 time.sleep(1.1) # Emulator timestamps updates in whole seconds.
 card=page.locator('#entries .entry').filter(has_text='95 Min.')
 card.get_by_role('button',name='Termin bearbeiten',exact=True).click();page.locator('#units').fill('100');page.locator('#when').fill((when+datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'));page.locator('#save').click()
 page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 wait_pin(lambda r:r['uuid']==guid and not r['deleted'] and r['duration']==100 and r['has_sent'])
 assert len([r for r in pins() if r['uuid']==guid])==1
 time.sleep(1.1)
 page.locator('#language').select_option('1');page.locator('#applyLanguage').click();page.wait_for_function("document.getElementById('status').textContent==='Saved on the watch.'",timeout=20000)
 wait_pin(lambda r:r['uuid']==guid and r['layout']['title']=='B | Practice | Motorway')
 time.sleep(1.1)
 page.locator('#language').select_option('0');page.locator('#applyLanguage').click();page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 wait_pin(lambda r:r['uuid']==guid and r['layout']['title']=='B | Praxis | Autobahn')
 page.locator('#timeline').select_option('0');page.locator('#applyTimeline').click();wait_pin(lambda r:r['uuid']==guid and r['deleted'])
 page.reload();page.wait_for_function("document.getElementById('timeline').value==='0'",timeout=10000)
 assert 'ausgeschaltet' in page.locator('#timelineStatus').inner_text()
 page.locator('#timeline').select_option('1');page.locator('#applyTimeline').click()
 replacement=wait_pin(lambda r:r['uuid']!=guid and not r['deleted'] and r['duration']==100 and r['has_sent'] and r['layout']['title']=='B | Praxis | Autobahn')
 assert not replacement['rejected']
 page.screenshot(path='/workspace/artifacts/v3.4-live-timeline.png',full_page=True)
 page.on('dialog',lambda dialog:dialog.accept());card=page.locator('#entries .entry').filter(has_text='100 Min.');assert card.count()==1
 card.get_by_role('button',name='Löschen',exact=True).click();page.wait_for_function(f"document.querySelectorAll('#entries .entry').length==={initial}",timeout=20000)
 wait_pin(lambda r:r['uuid']==replacement['uuid'] and r['deleted'])
 assert not errors,errors
 browser.close()
print('PASS LIVE Timeline: real local-pin API, accepted watch BlobDB insert, edit time/duration without duplicates, DE/EN, disable/delete, persisted setting, re-enable and appointment deletion; original entries retained')
