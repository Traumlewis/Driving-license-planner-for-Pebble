"""New mockup layout through packaged Pebble webview, PKJS and native Emery storage."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
port=json.loads(Path('/tmp/pb-emulator.json').read_text())['emery']['4.44']['pypkjs']['port'];url=f'http://127.0.0.1:{port}/config/7a1cd9f4-32ba-485c-ae41-605cc3d148eb/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 def snapshot():return page.evaluate("async()=> (await Pebble.sendMessage('pkjs',{type:'snapshot'})).state")
 def wait_saved():page.wait_for_function("['Auf der Uhr gespeichert.','Saved on the watch.'].includes(document.getElementById('status').textContent)",timeout=20000)
 before=snapshot();Path('/tmp/fahrschul-387-before.json').write_text(json.dumps(before));ids={e[0] for e in before['entries']}
 assert page.locator('#timeline').is_checked()==before['timeline']['enabled']
 page.locator('#cls').select_option('1');page.locator('#kind').select_option('3');page.locator('#increase').click();assert page.locator('#units').input_value()=='50'
 page.locator('#date').fill('2027-02-10');page.locator('#time').fill('10:35');page.locator('#lead2').select_option('0');page.locator('#save').click();wait_saved()
 state=snapshot();entry=next(e for e in state['entries'] if e[0] not in ids);entry_id=entry[0];Path('/tmp/fahrschul-387-fixture.json').write_text(json.dumps({'id':entry_id,'before':before}));assert entry[2]==1 and entry[3]==3 and entry[5]==60 and entry[6]==0 and entry[8]==5
 assert page.locator('#saveLabel').inner_text()=='Änderungen auf Uhr speichern'
 page.evaluate("window.nodes=Array.from(document.querySelector('#lead2').options);window.mutations=[];new MutationObserver(r=>mutations.push(...r)).observe(document.querySelector('#lead2'),{childList:true,subtree:true})")
 page.wait_for_timeout(5500);assert page.locator('#lead2').input_value()=='0';assert page.evaluate('mutations.length===0 && nodes.every((n,i)=>n===document.querySelector("#lead2").options[i])')
 page.locator('#increase').click();page.locator('#save').click();wait_saved();assert len(snapshot()['entries'])==len(ids)+1
 page.reload();page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 card=page.locator(f'.entry[data-id="{entry_id}"]');assert '55 Min.' in card.inner_text();card.get_by_role('button',name='Termin bearbeiten',exact=True).click()
 assert page.locator('#date').input_value()=='2027-02-10' and page.locator('#time').input_value()=='10:35' and page.locator('#lead2').input_value()=='0'
 page.locator('#language').select_option('1');page.locator('#applyLanguage').click();wait_saved();assert snapshot()['language']==1 and page.locator('h1').inner_text()=='Driving Planner'
 page.locator('#language').select_option(str(before['language']));page.locator('#applyLanguage').click();wait_saved()
 # New checkbox switch persists through real PKJS preferences and page reload.
 original=before['timeline']['enabled'];page.locator('#timeline').set_checked(not original);page.locator('#applyTimeline').click();page.wait_for_function('document.getElementById("applyTimeline").disabled===false');page.reload();page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000);assert page.locator('#timeline').is_checked()==(not original)
 page.locator('#timeline').set_checked(original);page.locator('#applyTimeline').click();page.wait_for_function('document.getElementById("applyTimeline").disabled===false')
 page.on('dialog',lambda d:d.accept());page.locator(f'.entry[data-id="{entry_id}"]').get_by_role('button',name='Löschen',exact=True).click();page.wait_for_function(f'document.querySelectorAll(".entry").length==={len(ids)}',timeout=20000)
 after=snapshot()
 for key in ['entries','counts','topics','remainders','language','cls','profile']:assert after[key]==before[key],key
 assert after['timeline']['enabled']==original and after['alarmOk'] and after['storageOk'];assert not errors,errors
 page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(300);page.screenshot(path='/workspace/artifacts/Fahrschul-Planer-v3.8.7-(DEV)-Settings-Live.png',full_page=True)
 browser.close()
print('PASS LIVE 3.8.7: packaged redesign auto-syncs, native date/time and 5-minute stepper save/update same ID, second Off survives polling/reopen, DE/EN and Timeline switch persist; test appointment deleted and original data restored')
