'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const folder=path.resolve(__dirname,'../../../Packs/App/Languages'),metadata=require('../src/pkjs/lang-pack'),urls=[],packets={};
let index=JSON.parse(fs.readFileSync(folder+'/index.json','utf8'));
for(const locale of ['de','en'])packets[locale+'/settings.json']=fs.readFileSync(folder+'/'+locale+'/settings.json','utf8');
const fr=JSON.parse(packets['en/settings.json']);fr.locale='fr';fr.strings.appName='Planificateur';packets['fr/settings.json']=JSON.stringify(fr);index.settings.languages.push({locale:'fr',name:'Français',file:'fr/settings.json',sha256:crypto.createHash('sha256').update(packets['fr/settings.json']).digest('hex'),watchLanguage:null});
let offline=false;
global.XMLHttpRequest=class {open(m,url){this.url=url;}send(){urls.push(this.url);setImmediate(()=>{if(offline)return this.onerror();this.status=200;this.responseText=this.url.endsWith('/index.json')?JSON.stringify(index):packets[this.url.slice(metadata.settingsBaseURL.length)];this.onload();});}abort(){}};
const storage={},events={},sent=[],published=[],localStorage={getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]};
function start(){const ctx={require:n=>n==='./config-html'?'/*__INITIAL_STATE__*/':require('../src/pkjs/'+n.slice(2)),Date,Number,JSON,Array,String,Math,encodeURIComponent,decodeURIComponent,console,localStorage,setTimeout:()=>1,clearTimeout:()=>{},Pebble:{addEventListener:(n,f)=>events[n]=f,sendAppMessage:m=>sent.push(m),sendConfigMessage:m=>published.push(m),insertTimelinePin:()=>{},deleteTimelinePin:()=>{}}};vm.runInNewContext(fs.readFileSync(__dirname+'/../src/pkjs/index.js','utf8'),ctx);return ctx;}
function rpc(data){return new Promise(resolve=>events.configmessage({data,respond:resolve}));}
async function wait(test){for(let i=0;i<100;i++){if(test())return;await new Promise(r=>setTimeout(r,5));}throw Error('No settings update');}
(async()=>{let app=start();const native={version:2,revision:4,language:0,cls:4,entries:[],counts:[1,2],topics:[1],remainders:[5]};events.appmessage({payload:{2:0,12:0,14:0,15:1,13:JSON.stringify(native)}});const snapshot=storage['fahrschul.v2.snapshot'];
 await rpc({type:'settingsRefresh'});await wait(()=>app.freshState().settingsLanguage.active);assert.strictEqual(app.freshState().settingsLanguage.active.locale,'de');const before=sent.length;
 let reply=await rpc({type:'settingsSelect',locale:'fr'});assert(!reply.error);assert.strictEqual(reply.state.settingsLanguage.active.watchLanguage,null);assert.strictEqual(sent.length,before);assert(!storage['fahrschul.v2.pending']);assert.strictEqual(storage['fahrschul.v2.snapshot'],snapshot);const legacyCache=app.settingsStore.exportCache();
 offline=true;app=start();assert.strictEqual(app.freshState().settingsLanguage.active.locale,'fr');await rpc({type:'settingsRefresh'});await wait(()=>app.freshState().settingsLanguage.error);assert.strictEqual(app.freshState().settingsLanguage.active.locale,'fr');reply=await rpc({type:'settingsSelect',locale:'en'});assert(reply.error);assert.strictEqual(reply.state.settingsLanguage.active.locale,'fr');
 offline=false;reply=await rpc({type:'settingsSelect',locale:'en'});assert(!reply.error&&reply.state.settingsLanguage.active.watchLanguage===1);assert.strictEqual(sent.length,before);
 events.webviewclosed({response:encodeURIComponent(JSON.stringify({action:'settingsLanguage',settingsCache:legacyCache}))});assert.strictEqual(app.freshState().settingsLanguage.active.locale,'fr');assert.strictEqual(sent[sent.length-1][1],0);assert(!storage['fahrschul.v2.pending']);
 reply=await rpc({type:'command',command:{action:'language',language:1}});assert(reply.queued);assert.strictEqual(sent[sent.length-1][17],1);assert.strictEqual(storage['fahrschul.v2.snapshot'],snapshot);
 console.log('PASS production settings bridge: live catalogue, dynamic phone-only language, no unintended watch changes, restart/offline cache, download recovery and explicit watch-language command');
})().catch(e=>{console.error(e);process.exitCode=1;});
