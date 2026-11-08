"""Real packaged page -> pypkjs -> native Emery -> live page, no bridge mocks."""
from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
info=json.loads(Path('/tmp/pb-emulator.json').read_text());port=info['emery']['4.44']['pypkjs']['port'];url=f'http://127.0.0.1:{port}/config/7a1cd9f4-32ba-485c-ae41-605cc3d148eb/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.getElementById('status').textContent.indexOf('synchronisiert')>=0",timeout=20000)
 assert page.locator('#reload').count()==0
 initial=page.locator('#entries .entry').count()
 page.locator('#kind').select_option('2');page.locator('#when').fill('2027-01-15T09:25');page.locator('#units').fill('75');page.locator('#save').click()
 page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 assert page.locator('#entries .entry').count()==initial+1
 assert '75 Min.' in page.locator('#entries').inner_text()
 page.screenshot(path='/workspace/artifacts/v3.1-live-settings-de.png',full_page=True)
 page.locator('#language').select_option('1');page.locator('#applyLanguage').click();page.wait_for_function("document.getElementById('status').textContent==='Saved on the watch.'",timeout=20000)
 assert page.locator('h1').inner_text()=='Your driving lessons.'
 page.screenshot(path='/workspace/artifacts/v3.1-live-settings-en.png',full_page=True)
 page.locator('#language').select_option('0');page.locator('#applyLanguage').click();page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 page.on('dialog',lambda dialog:dialog.accept())
 card=page.locator('#entries .entry').filter(has_text='Autobahn').filter(has_text='15.01.2027')
 assert card.count()==1
 card.get_by_role('button',name='Löschen',exact=True).click()
 page.wait_for_function(f"document.querySelectorAll('#entries .entry').length==={initial}",timeout=20000)

 assert page.locator('#timeline').input_value()=='1'
 page.locator('#timeline').select_option('0');page.locator('#applyTimeline').click()
 page.wait_for_function("document.getElementById('applyTimeline').disabled===false && document.getElementById('timeline').value==='0'",timeout=10000)
 page.reload();page.wait_for_function("document.getElementById('timeline').value==='0'",timeout=10000)
 page.locator('#timeline').select_option('1');page.locator('#applyTimeline').click()
 page.wait_for_function("document.getElementById('applyTimeline').disabled===false && document.getElementById('timeline').value==='1'",timeout=10000)
 page.screenshot(path='/workspace/artifacts/v3.4-live-settings.png',full_page=True)
 assert not errors,errors
 browser.close()
print('PASS LIVE settings: bundled page opens, auto-sync from native watch, save 75-minute lesson, application ACK, switch DE/EN and delete without closing page')
