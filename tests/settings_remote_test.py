"""Exercise the shipped settings page with live catalogue changes and one persistent packet."""
from pathlib import Path
import json,hashlib,threading,http.server,functools
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];BASE='https://raw.githubusercontent.com/Traumlewis/Driving-license-planner-for-Pebble/main/Packs/Germany/Languages/'
files={name:(ROOT/'Packs/Germany/Languages'/name).read_text() for name in ['index.json','de/settings.json','en/settings.json']}
state={'version':2,'language':0,'revision':7,'cls':4,'fresh':True,'alarmOk':True,'storageOk':True,'timeline':{'enabled':True,'status':'submitted'},'entries':[[1,1900000000,4,3,1,60,30,255,0]],'extras':[2,4,4,4,2,0,6,0,10,4,10,0,18,0,2,6]}
state['settingsCache']={'catalogue':files['index.json'],'packet':json.dumps({'locale':'de','catalogue':files['index.json'],'raw':files['de/settings.json']})}
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);context=browser.new_context(viewport={'width':390,'height':844});page=context.new_page();errors=[];calls=[];offline=False
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   calls.append(r.request.url)
   if offline:return r.abort()
   raw=files.get(r.request.url[len(BASE):])
   if raw is None:return r.fulfill(status=404,body='missing',headers={'Access-Control-Allow-Origin':'*'})
   return r.fulfill(status=200,body=raw,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
  page.route(BASE+'**',route)
  page.add_init_script('window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state))
  url=f'http://127.0.0.1:{server.server_port}/projects/time2/phone/config.html';page.goto(url)
  page.wait_for_function("document.querySelector('h1').textContent==='Fahrschul Planer'")
  assert page.locator('#language option').count()==2 and page.locator('#language').input_value()=='de'
  page.locator('#date').fill('2030-04-01');page.locator('#time').fill('12:30');page.locator('#units').fill('65');page.locator('#lead2').select_option('0')
  page.locator('#language').select_option('en');page.wait_for_function("document.querySelector('h1').textContent==='Driving Planner'")
  assert page.locator('#date').input_value()=='2030-04-01' and page.locator('#time').input_value()=='12:30' and page.locator('#units').input_value()=='65' and page.locator('#lead2').input_value()=='0'
  # Add a test-only language after the page/JS bytes are already fixed.
  fr=json.loads(files['en/settings.json']);fr['locale']='fr';fr['strings']['appName']='Planificateur';fr['strings']['phoneOnly']='téléphone uniquement';files['fr/settings.json']=json.dumps(fr,ensure_ascii=False)
  index=json.loads(files['index.json']);index['settings']['languages'].append(dict(locale='fr',name='Français',file='fr/settings.json',sha256=hashlib.sha256(files['fr/settings.json'].encode()).hexdigest(),watchLanguage=None));files['index.json']=json.dumps(index)
  page.reload();page.wait_for_function("document.querySelectorAll('#language option').length===3")
  page.locator('#language').select_option('fr');page.wait_for_function("document.querySelector('h1').textContent==='Planificateur'")
  assert page.locator('#applyLanguage').inner_text()=='Save language' and 'watch language stays unchanged' in page.locator('#settingsLanguageStatus').inner_text()
  assert 'téléphone uniquement' in page.locator('#language option[value=fr]').inner_text()
  cache=page.evaluate("localStorage.getItem('fahrschul.v2.settingsPacket')");assert json.loads(cache)['locale']=='fr'
  offline=True;page.reload();page.wait_for_function("document.querySelector('h1').textContent==='Planificateur'")
  assert page.locator('#language').input_value()=='fr'
  page.wait_for_function("!document.querySelector('#language').disabled")
  page.locator('#language').select_option('de');page.wait_for_function("!document.querySelector('#language').disabled")
  assert page.locator('h1').inner_text()=='Planificateur' and page.locator('#language').input_value()=='fr' and page.evaluate("localStorage.getItem('fahrschul.v2.settingsPacket')")==cache
  offline=False;page.reload();page.wait_for_function("!document.querySelector('#language').disabled")
  page.locator('#language').select_option('de');page.wait_for_function("document.querySelector('h1').textContent==='Fahrschul Planer'")
  assert json.loads(page.evaluate("localStorage.getItem('fahrschul.v2.settingsPacket')"))['locale']=='de'
  for width in [320,390,768]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  browser.close()
 print('PASS browser: actual bundled page, dynamic third settings language without rebuild, safe phone-only choice, one-cache offline restart/failure recovery, form preservation and responsive layouts')
finally:server.shutdown()
