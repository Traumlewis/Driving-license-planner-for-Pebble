"""Real settings: per-appointment Off survives saving, polling, re-opening and updates."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
port=json.loads(Path('/tmp/pb-emulator.json').read_text())['emery']['4.44']['pypkjs']['port']
url=f'http://127.0.0.1:{port}/config/7a1cd9f4-32ba-485c-ae41-605cc3d148eb/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 assert page.locator('#reminder2Enabled').count()==0 and page.locator('#applyReminder2').count()==0
 initial=page.locator('#entries .entry').count()
 page.locator('#cls').select_option('1');page.locator('#kind').select_option('3');page.locator('#units').fill('50');page.locator('#when').fill('2027-02-10T10:35');page.locator('#lead2').select_option('0')
 page.evaluate("""() => {window.nodes=Array.from(document.getElementById('lead2').options);window.mutations=[];window.observer=new MutationObserver(r=>mutations.push(...r));observer.observe(document.getElementById('lead2'),{childList:true,subtree:true});}""")
 page.locator('#save').click();page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 assert page.locator('#lead2').input_value()=='0'
 assert page.locator('#save').inner_text()=='Änderungen auf Uhr speichern'
 assert page.locator('#entries .entry').count()==initial+1
 page.wait_for_timeout(6000)
 assert page.locator('#lead2').input_value()=='0' and page.evaluate('mutations.length')==0
 assert page.evaluate("nodes.every((n,i)=>n===document.getElementById('lead2').options[i])")
 # A second save updates the same appointment, rather than creating a duplicate.
 page.locator('#units').fill('55');page.locator('#save').click();page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 assert page.locator('#entries .entry').count()==initial+1 and page.locator('#lead2').input_value()=='0'
 snapshot=page.evaluate("async()=> (await Pebble.sendMessage('pkjs',{type:'snapshot'})).state")
 entry=next(e for e in snapshot['entries'] if e[2]==1 and e[3]==3 and e[8]==10)
 assert entry[5]==60 and entry[6]==0
 page.screenshot(path='/workspace/artifacts/v3.6-settings-off-saved.png',full_page=True)
 page.reload();page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 card=page.locator('#entries .entry').filter(has_text='55 Min.').filter(has_text='10.02.2027');assert card.count()==1
 card.get_by_role('button',name='Termin bearbeiten',exact=True).click();assert page.locator('#lead2').input_value()=='0'
 page.on('dialog',lambda d:d.accept());card.get_by_role('button',name='Löschen',exact=True).click()
 page.wait_for_function(f"document.querySelectorAll('#entries .entry').length==={initial}",timeout=20000)
 assert not errors,errors
 browser.close()
print('PASS LIVE 3.6: redundant reminder card removed, Off retained after create/update/poll/re-open, saved ID avoids duplicates; original appointments restored')
