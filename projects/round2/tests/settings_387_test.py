"""Responsive settings, new controls, stable polling and DE/EN using the real page script."""
from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
state={'version':2,'language':0,'revision':7,'cls':4,'fresh':True,'alarmOk':True,'storageOk':True,'timeline':{'enabled':True,'status':'submitted'},'entries':[[1,1794504600,4,3,1,60,30,255,0],[2,1794672000,4,5,1,60,0,0,0]],'extras':[2,4,4,4,2,0,6,0,10,4,10,0,18,0,2,6]}
catalogue=json.loads((root.parents[1]/'Packs/App/Languages/index.json').read_text())['settings']['languages'];packets={locale:json.loads((root.parents[1]/'Packs/App/Languages'/locale/'settings.json').read_text()) for locale in ['de','en']}
state['settingsLanguage']={'catalogue':catalogue,'active':{'locale':'de','watchLanguage':0,'packet':packets['de']},'loading':False,'error':None}
html=(root/'phone/config.html').read_text().replace('/*__INITIAL_STATE__*/','window.__FAHRSCHUL_INITIAL_STATE__='+json.dumps(state)+';')
bridge='''<script>window.callbacks={};window.testState=STATE;window.Pebble={addEventListener:(name,cb)=>callbacks[name]=cb,readyTargets:()=>['pkjs'],sendMessage:async(target,data)=>{if(data.type==='settingsSelect')testState.settingsLanguage.active={locale:data.locale,watchLanguage:data.locale==='de'?0:1,packet:PACKETS[data.locale]};return {state:testState};}};</script>'''.replace('STATE',json.dumps(state)).replace('PACKETS',json.dumps(packets))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page(viewport={'width':390,'height':844},locale='de-DE',timezone_id='Europe/Berlin');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(html.replace('<head>','<head>'+bridge,1))
 assert page.locator('#timeline').is_checked() and not page.locator('#topicField').is_visible()
 assert page.locator('#lead1').input_value()=='60' and page.locator('#lead2').input_value()=='30'
 page.locator('#increase').click();assert page.locator('#units').input_value()=='50';page.locator('#decrease').click();page.locator('#decrease').click();assert page.locator('#units').input_value()=='45'
 page.locator('#units').fill('67');page.locator('#increase').click();assert page.locator('#units').input_value()=='70';page.locator('#decrease').click();assert page.locator('#units').input_value()=='65'
 page.locator('#units').fill('540');page.locator('#increase').click();assert page.locator('#units').input_value()=='540'
 page.locator('#kind').select_option('5');assert page.locator('#topicField').is_visible() and page.locator('#units').input_value()=='1';page.locator('#increase').click();assert page.locator('#units').input_value()=='2';assert '90' in page.locator('#unitSuffix').inner_text()
 page.locator('#kind').select_option('3');page.locator('#units').fill('50');page.locator('#date').fill('2027-04-01');page.locator('#time').fill('12:30');page.locator('#lead2').select_option('0')
 page.evaluate("window.nodes=Array.from(document.querySelector('#lead2').options);window.mutations=[];new MutationObserver(r=>mutations.push(...r)).observe(document.querySelector('#lead2'),{childList:true,subtree:true})")
 # Preview changes must survive incoming snapshots without rebuilding option lists.
 page.locator('#timeline').uncheck();page.wait_for_timeout(5300)
 assert not page.locator('#timeline').is_checked() and page.locator('#date').input_value()=='2027-04-01' and page.locator('#time').input_value()=='12:30'
 assert page.locator('#units').input_value()=='50' and page.locator('#lead2').input_value()=='0'
 assert page.evaluate('mutations.length===0 && nodes.every((n,i)=>n===document.querySelector("#lead2").options[i])')
 page.locator('#language').select_option('en');page.wait_for_function("document.querySelector('h1').textContent==='Driving Planner'");assert page.locator('h1').inner_text()=='Driving Planner';assert page.locator('#lead2').input_value()=='0'
 # Settings translations still update after the independent watch connection goes stale.
 page.evaluate('testState.fresh=false');page.locator('#language').select_option('de');page.wait_for_function("document.documentElement.lang==='de'");page.evaluate('testState.fresh=true')
 for lang in ['de','en']:
  page.locator('#language').select_option(lang);page.wait_for_function("locale=>document.documentElement.lang===locale",arg=lang)
  for width in [320,360,390,430,768]:
   page.set_viewport_size({'width':width,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(lang,width)
 page.locator('#newAppointment').click();assert page.locator('#cancel').is_hidden() and page.locator('#lead2').input_value()=='30'
 assert not errors,errors
 browser.close()
print('PASS 3.8.7 settings: stepper bounds, theory/practice, native date/time, second Off, stable automatic polling, dirty Timeline switch, DE/EN and 320–768px layouts')
