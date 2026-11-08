"""Live packaged settings: stable DOM during polling, defaults and persistent reminder-2 mute."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
info=json.loads(Path('/tmp/pb-emulator.json').read_text());port=info['emery']['4.44']['pypkjs']['port']
url=f'http://127.0.0.1:{port}/config/7a1cd9f4-32ba-485c-ae41-605cc3d148eb/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(url);page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 assert page.locator('#lead1').input_value()=='60' and page.locator('#lead2').input_value()=='30'
 before=page.locator('#entries .entry').count()
 page.locator('#cls').select_option('1');page.locator('#kind').select_option('3');page.locator('#lead1').select_option('45');page.locator('#lead2').select_option('15');page.locator('#units').fill('70')
 page.locator('#language').select_option('1');page.locator('#reminder2Enabled').select_option('0')
 page.evaluate("""() => {
 window.optionNodes={};for(const id of ['cls','kind','topic','lead1','lead2','language','reminder2Enabled','timeline'])optionNodes[id]=Array.from(document.getElementById(id).options);
 window.optionMutations=[];window.observer=new MutationObserver(records=>optionMutations.push(...records));
 for(const id of Object.keys(optionNodes))observer.observe(document.getElementById(id),{childList:true,subtree:true});
 }""")
 # More than one full automatic polling interval, with a select focused.
 page.locator('#kind').focus();page.wait_for_timeout(11000)
 assert page.evaluate("optionMutations.length")==0
 assert page.evaluate("Object.keys(optionNodes).every(id=>optionNodes[id].every((node,i)=>node===document.getElementById(id).options[i]))")
 assert [page.locator('#'+x).input_value() for x in ['cls','kind','lead1','lead2','units','language','reminder2Enabled']]==['1','3','45','15','70','1','0']
 assert page.locator('h1').inner_text()=='Your driving lessons.'
 page.evaluate('observer.disconnect()')
 page.locator('#applyReminder2').click();page.wait_for_function("document.getElementById('status').textContent==='Saved on the watch.'",timeout=20000)
 assert page.locator('#units').input_value()=='70' # Saving a setting does not discard a draft.
 assert page.evaluate("async()=> (await Pebble.sendMessage('pkjs',{type:'snapshot'})).state.reminder2") is False
 page.reload();page.wait_for_function("document.getElementById('status').textContent.includes('synchronisiert')",timeout=20000)
 assert page.locator('#reminder2Enabled').input_value()=='0'
 assert 'ausgeschaltet' in page.locator('#secondMuted').inner_text()
 assert page.locator('#lead1').input_value()=='60' and page.locator('#lead2').input_value()=='30'
 page.screenshot(path='/workspace/artifacts/v3.5-settings-reminder2-off.png',full_page=True)
 page.locator('#reminder2Enabled').select_option('1');page.locator('#applyReminder2').click();page.wait_for_function("document.getElementById('status').textContent==='Auf der Uhr gespeichert.'",timeout=20000)
 assert page.evaluate("async()=> (await Pebble.sendMessage('pkjs',{type:'snapshot'})).state.reminder2") is True
 assert page.locator('#entries .entry').count()==before
 assert not errors,errors
 browser.close()
print('PASS LIVE 3.5: unchanged option nodes across automatic polling, focused selections and language preview retained, 60/30-minute defaults, persistent watch reminder-2 mute/unmute and draft preservation')
