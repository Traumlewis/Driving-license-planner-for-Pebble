"""All remote watch languages expose the correct watch-language commands."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'Packs/App/Languages';index=json.loads((base/'index.json').read_text());tag=json.loads((ROOT/'projects/time2/src/pkjs/lang-pack.js').read_text().split('=',1)[1].strip().rstrip(';'))['watch']['tag'];watch=index['watchPacks'][tag]['languages'];catalogue=[dict(d,watchLanguage=next((p['language'] for p in watch if p['locale']==d['locale']),None)) for d in index['settings']['languages']]
es=json.loads((base/'es/settings.json').read_text());state=dict(version=2,revision=1,language=0,cls=4,fresh=True,entries=[],settingsLanguage=dict(catalogue=catalogue,active=dict(locale='es',watchLanguage=2,packet=es),loading=False,error=None))
html=(ROOT/'projects/time2/phone/config.html').read_text().replace('/*__INITIAL_STATE__*/','window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state)+';')
bridge='<script>window.testState='+json.dumps(state)+";window.messages=[];window.callbacks={};window.Pebble={addEventListener:(n,f)=>callbacks[n]=f,readyTargets:()=>['pkjs'],sendMessage:async(target,data)=>{messages.push(data);return {queued:true,state:testState};}};</script>"
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for descriptor in watch:
  locale,name,language=descriptor['locale'],descriptor['name'],descriptor['language']
  button=json.loads((base/locale/'settings.json').read_text())['strings']['languageSave']
  packet=json.loads((base/locale/'settings.json').read_text());state['settingsLanguage']['active']=dict(locale=locale,watchLanguage=language,packet=packet)
  html=(ROOT/'projects/time2/phone/config.html').read_text().replace('/*__INITIAL_STATE__*/','window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state)+';')
  bridge='<script>window.testState='+json.dumps(state)+";window.messages=[];window.callbacks={};window.Pebble={addEventListener:(n,f)=>callbacks[n]=f,readyTargets:()=>['pkjs'],sendMessage:async(target,data)=>{messages.push(data);return {queued:true,state:testState};}};</script>"
  page.set_content(html.replace('<head>','<head>'+bridge,1));assert page.locator('#language option[value='+locale+']').inner_text()==name;assert page.locator('#applyLanguage').is_visible();assert page.locator('#applyLanguage').inner_text()==button;page.locator('#applyLanguage').click();assert page.evaluate("language=>messages.some(m=>m.type==='command'&&m.command.action==='language'&&m.command.language===language)",language)
  for width in [320,390,768]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors;browser.close()
print('PASS twenty-four-language watch UI: translated Apply button, language 0–23 commands, accents and responsive layouts')
