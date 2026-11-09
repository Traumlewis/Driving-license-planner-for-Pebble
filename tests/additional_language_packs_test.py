"""Validate new remote translations and actual watch-enabled phone UI/cache behavior."""
from pathlib import Path
import functools,hashlib,http.server,json,sys,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from watch_packets import encode,signature,compatibility
BASE=ROOT/'Packs/App/Languages';REMOTE='https://raw.githubusercontent.com/Traumlewis/Driving-license-planner-for-Pebble/main/Packs/App/Languages/'
index=json.loads((BASE/'index.json').read_text());english=json.loads((BASE/'en/settings.json').read_text());schema=json.loads((ROOT/'tools/watch-schema.json').read_text());variant=index['watchPacks'][compatibility()['tag']];new={'it':'Italiano','pt':'Português','nl':'Nederlands','pl':'Polski'};report={}
for locale,name in new.items():
 descriptor=next(d for d in index['settings']['languages'] if d['locale']==locale);raw=(BASE/descriptor['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==descriptor['sha256'];packet=json.loads(raw)
 assert packet['locale']==locale and set(packet['strings'])==set(english['strings'])
 assert len(packet['kinds'])==7 and len(packet['grounds'])==12 and len(raw)<60000
 assert descriptor['watchLanguage'] is None
 watch=next(d for d in variant['languages'] if d['locale']==locale)
 source=json.loads((BASE/locale/'watch-source.json').read_text());assert source['name']==name and set(source['strings'])=={r['de'] for r in schema}
 for row in schema:
  value=source['strings'][row['de']];assert value and len(value.encode())<=row['maxBytes'] and signature(value)==row['signature'],(locale,row['de'])
 helptext=next(v for k,v in source['strings'].items() if k.startswith('FAHRSCHUL PLANER'))
 assert '{version}' in helptext and '(Idee by Traumlewis | Code by Codex)' in helptext
 encoded=encode(source);size=encoded['size'];assert 0<size<=2560 and encoded['language']==watch['language'] and encoded['id']==watch['id']
 assert hashlib.sha256((BASE/watch['file']).read_bytes()).hexdigest()==watch['sha256']
 report[locale]=dict(name=name,settingsBytes=len(raw),settingsStrings=len(packet['strings']),watchStrings=len(schema),watchPayloadBytes=size,currentWatchLimit=2560,watchAvailable=True)
files={p.relative_to(BASE).as_posix():p.read_text() for p in BASE.rglob('*.json')};state={'version':2,'language':0,'revision':7,'cls':4,'fresh':True,'alarmOk':True,'storageOk':True,'entries':[],'settingsCache':{'catalogue':files['index.json'],'packet':json.dumps({'locale':'de','catalogue':files['index.json'],'raw':files['de/settings.json']})}}
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844});errors=[];offline=False;calls=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   calls.append(r.request.url)
   if offline:return r.abort()
   raw=files.get(r.request.url[len(REMOTE):])
   return r.fulfill(status=200 if raw is not None else 404,body=raw or 'missing',content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
  page.route(REMOTE+'**',route);page.add_init_script('window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state));url=f'http://127.0.0.1:{server.server_port}/projects/time2/phone/config.html'
  out=ROOT/'docs/verification/dev/languages-it-pt-nl-pl';out.mkdir(parents=True,exist_ok=True)
  for locale,name in new.items():
   packet=json.loads(files[locale+'/settings.json']);s=packet['strings'];offline=False;page.goto(url);page.wait_for_function("!document.querySelector('#language').disabled")
   page.locator('#date').fill('2030-04-01');page.locator('#time').fill('12:30');page.locator('#units').fill('65');page.locator('#lead2').select_option('0');page.locator('#language').select_option(locale)
   page.wait_for_function("v=>document.querySelector('h1').textContent===v",arg=s['appName']);page.wait_for_function("!document.querySelector('#language').disabled")
   assert page.locator('#language').input_value()==locale and page.locator('#language option[value='+locale+']').inner_text()==name
   page.wait_for_function("v=>document.querySelector('#settingsLanguageStatus').textContent===v",arg=s['settingsReady'])
   assert page.locator('#applyLanguage').inner_text()==s['languageSave']
   assert page.locator('#date').input_value()=='2030-04-01' and page.locator('#time').input_value()=='12:30' and page.locator('#units').input_value()=='65' and page.locator('#lead2').input_value()=='0'
   cache=page.evaluate("localStorage.getItem('fahrschul.v2.settingsPacket')");assert json.loads(cache)['locale']==locale
   for width in [320,390,768]:
    page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(out/(locale+'-settings.png')),full_page=True)
   offline=True;page.reload();page.wait_for_function("v=>document.querySelector('h1').textContent===v",arg=s['appName']);assert page.locator('#language').input_value()==locale
   page.wait_for_function("!document.querySelector('#language').disabled");page.locator('#language').select_option('de');page.wait_for_function("!document.querySelector('#language').disabled")
   assert page.locator('h1').inner_text()==s['appName'] and page.locator('#language').input_value()==locale and page.evaluate("localStorage.getItem('fahrschul.v2.settingsPacket')")==cache
   report[locale]['browserOnlineOfflinePassed']=True;print('PASS',locale,'remote phone settings, preserved form, one-packet cache, offline restart/failure recovery; complete watch packet validated, matching Apply action offered',flush=True)
  assert not errors,errors;browser.close()
 (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
finally:server.shutdown()
