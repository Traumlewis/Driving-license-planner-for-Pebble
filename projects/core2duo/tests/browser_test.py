from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
state={'version':2,'language':0,'revision':7,'cls':4,'fresh':True,'alarmOk':True,'storageOk':True,'entries':[[1,int(time.time())+172800,4,1,1,1440,30,255,20],[2,int(time.time())+259200,4,5,1,1440,30,0,0]],'extras':[2,4,4,4,2,0,6,0,10,4,10,0,18,0,2,6]}
html=(root/'phone/config.html').read_text().replace('/*__INITIAL_STATE__*/','window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state)+';')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,timezone_id='Europe/Berlin',locale='de-DE')
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html)
 assert page.locator('#entries .entry').count()==2
 assert page.locator('#reload').count()==0
 assert page.locator('#lead1 option').count()==192 and page.locator('#lead2 option').count()==193
 assert 'Landstraße' in page.locator('#entries').inner_text()
 page.get_by_role('button',name='Termin bearbeiten',exact=True).nth(0).click()
 assert page.locator('#units').input_value()=='65' and page.locator('#units').get_attribute('step')=='5'
 page.locator('#units').fill('70');assert page.locator('#units').evaluate('(x)=>x.checkValidity()')
 page.locator('#units').fill('67');assert not page.locator('#units').evaluate('(x)=>x.checkValidity()')
 page.get_by_role('button',name='Termin bearbeiten',exact=True).nth(1).click()
 assert page.locator('#kind').input_value()=='5' and page.locator('#topic').input_value()=='0'
 assert page.locator('#topic option').count()==13 and page.locator('#units').get_attribute('step')=='1'
 page.locator('#date').fill('2027-03-28');page.locator('#time').fill('02:30');page.locator('#save').click();assert 'gültiges Datum' in page.locator('#error').inner_text()
 page.locator('#date').fill('2027-04-01');page.locator('#time').fill('12:30');page.locator('#lead1').select_option('30');page.locator('#lead2').select_option('30');page.locator('#save').click();assert 'unterschiedliche Erinnerungen' in page.locator('#error').inner_text()
 page.locator('#language').select_option('1');assert page.locator('h1').inner_text()=='Driving Planner'
 assert page.locator('#topic').input_value()=='0' and page.locator('#units').input_value()=='1'
 assert 'Core syllabus' in page.locator('#entries').inner_text()
 assert page.locator('#applyLanguage').inner_text()=='Apply language'
 page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(250);page.screenshot(path='/workspace/artifacts/Fahrschul-Planer-v3.8.7-(DEV)-Settings-English.png',full_page=True)
 page.locator('#language').select_option('0');page.locator('#cancel').click();page.locator('#cls').select_option('14');assert page.locator('#kind option').count()==2
 page.locator('#cls').select_option('4');page.locator('#kind').select_option('3');assert 'Nachtfahrt' in page.locator('#kind').inner_text()
 page.locator('#units').fill('50');page.locator('#date').fill('2027-04-01');page.locator('#time').fill('12:30');page.locator('#lead1').select_option('1440');page.locator('#lead2').select_option('30');page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(250);page.screenshot(path='/workspace/artifacts/Fahrschul-Planer-v3.8.7-(DEV)-Settings-Deutsch.png',full_page=True)
 assert not errors,errors
 browser.close()
print('PASS browser: automatic-refresh UI, DE/EN settings, umlauts, expanded lesson types, 5-minute practice duration, whole theory units and date validation')
