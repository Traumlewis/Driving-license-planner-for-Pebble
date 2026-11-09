'use strict';
// Actual production PKJS + real public HTTPS + native AppMessage emulator. No application ACKs are mocked.
const fs=require('fs'),path=require('path'),cp=require('child_process'),vm=require('vm'),assert=require('assert'),readline=require('readline');
const platform=process.argv[2],root=path.resolve(__dirname,'..'),project=root+'/projects/time2/src/pkjs',metadata=require(project+'/lang-pack'),fixtures=require(root+'/projects/time2/tools/language-packets.json').packs;
let offline=false,stopping=false,hello=null,restarted=0,finished=null,bridgeError=null;const urls=[],state={},events={},results=[],httpChildren=new Set(),timerIds=new Set();
class XHR {
 open(method,url){assert.strictEqual(method,'GET');assert(url.startsWith(metadata.baseURL)||url.startsWith(metadata.settingsBaseURL));this.url=url;}
 send(){urls.push(this.url);if(offline){setImmediate(()=>this.onerror());return;}this.child=cp.execFile('curl',['--fail','--silent','--show-error','--location','--max-time','15','--max-filesize','20000',this.url],{encoding:'utf8',maxBuffer:30000},(error,stdout)=>{httpChildren.delete(this.child);if(this.aborted)return;if(error){this.onerror();return;}this.status=200;this.responseText=stdout;this.onload();});httpChildren.add(this.child);}
 abort(){this.aborted=true;if(this.child)this.child.kill();}
}
global.XMLHttpRequest=XHR;
const child=cp.spawn('/workspace/.tools/pebble-tool/bin/python',['tools/run_emulator.py',platform,'tools/native_phone_bridge.py'],{cwd:root,stdio:['pipe','pipe','pipe']});
child.stderr.on('data',d=>{bridgeError=(bridgeError||'')+d.toString();});
function send(value){if(!stopping)child.stdin.write(JSON.stringify(value)+'\n');}
const storage={getItem:k=>state[k]||null,setItem:(k,v)=>state[k]=String(v),removeItem:k=>delete state[k]};
const context={require:n=>n==='./config-html'?'/*__INITIAL_STATE__*/':require(project+'/'+n.slice(2)),localStorage:storage,Date,Number,JSON,Array,String,Math,encodeURIComponent,decodeURIComponent,console,
 setTimeout:(f,n)=>{const id=setTimeout(()=>{timerIds.delete(id);f();},n);timerIds.add(id);return id;},clearTimeout:id=>{timerIds.delete(id);clearTimeout(id);},
 Pebble:{addEventListener:(n,f)=>events[n]=f,sendAppMessage:(data,ack)=>{send({action:'message',data});if(ack)ack();},sendConfigMessage:m=>{if(m.result)results.push(m.result);},insertTimelinePin:()=>{},deleteTimelinePin:()=>{}}};
vm.createContext(context);vm.runInContext(fs.readFileSync(project+'/index.js','utf8'),context);
readline.createInterface({input:child.stdout}).on('line',line=>{if(!line.startsWith('BRIDGE:'))return;const msg=JSON.parse(line.slice(7));if(msg.type==='hello')hello=msg;else if(msg.type==='appmessage'&&!stopping)events.appmessage({payload:msg.payload});else if(msg.type==='restarted')restarted++;else if(msg.type==='finished')finished=msg;});
function waitFor(test,limit=45000){const start=Date.now();return new Promise((resolve,reject)=>{function poll(){if(test())return resolve();if(child.exitCode!==null||Date.now()-start>limit)return reject(Error(bridgeError||'Integration timeout'));setTimeout(poll,25);}poll();});}
async function language(value){let response;events.configmessage({data:{type:'command',command:{action:'language',language:value}},respond:r=>response=r});assert(response.queued,JSON.stringify(response));await waitFor(()=>results.some(r=>r.rid===response.requestId&&r.status===0)&&!state['fahrschul.v2.pending']);assert.strictEqual(context.snapshot.languagePack.language,value);assert.strictEqual(context.snapshot.languagePack.id,fixtures.find(p=>p.language===value).id);assert.strictEqual(context.snapshot.languagePack.storedBytes,fixtures.find(p=>p.language===value).size+16);}
(async()=>{
 await waitFor(()=>hello);events.ready();await waitFor(()=>context.snapshot&&context.snapshot.languagePack.ready&&!state['fahrschul.v2.pending']);
 // This also covers initial loading of German when the updated native app has no compatible packet.
 const original=hello.language;
 if(process.argv.includes('--settings')){
  function settingsRPC(data){return new Promise(resolve=>events.configmessage({data,respond:resolve}));}
  await settingsRPC({type:'settingsRefresh'});await waitFor(()=>context.freshState().settingsLanguage.active);
  const nativeLanguage=context.snapshot.language;
  for(const locale of ['en','es','fr','de',fixtures.find(p=>p.language===original).locale]){const reply=await settingsRPC({type:'settingsSelect',locale});assert(!reply.error,reply.error);assert.strictEqual(reply.state.settingsLanguage.active.locale,locale);assert.strictEqual(context.snapshot.language,nativeLanguage);assert(!state['fahrschul.v2.pending']);}
  assert.strictEqual(JSON.parse(state['fahrschul.v2.settingsPacket']).locale,fixtures.find(p=>p.language===original).locale);
 }
 await language(3);await language(2);await language(original===0?1:0);await language(original);
 assert.strictEqual(JSON.parse(state['fahrschul.v2.languagePacket']).descriptor.language,original);const count=urls.length;
 offline=true;send({action:'restart'});await waitFor(()=>restarted===1);events.ready();await waitFor(()=>context.snapshot.languagePack.ready&&!state['fahrschul.v2.pending']);await language(original);assert.strictEqual(urls.length,count,'selected language contacted GitHub while offline');
 stopping=true;child.stdin.write(JSON.stringify({action:'finish'})+'\n');await waitFor(()=>finished);assert(finished.appDataPreserved);
 const out=root+'/docs/verification/dev/'+metadata.appVersion+'/'+platform;fs.mkdirSync(out,{recursive:true});fs.writeFileSync(out+'/remote-native.json',JSON.stringify({platform,version:metadata.appVersion,urls,offlineNativeRestart:true,singlePhoneCache:!!state['fahrschul.v2.languagePacket'],appDataPreserved:finished.appDataPreserved},null,2)+'\n');
 if(process.argv.includes('--settings'))console.log('PASS '+platform+': production settings bridge downloaded live GitHub catalogue and DE/EN/ES/FR settings packets without changing native watch data');
 console.log('PASS '+platform+': real GitHub → production phone client → native watch transfer, DE/EN/ES/FR replacement, one cache, offline native restart and original data preserved');
})().catch(e=>{console.error(e);console.error('Integration state',JSON.stringify({urls,pending:state['fahrschul.v2.pending'],packet:context.snapshot&&context.snapshot.languagePack,download:context.languageStore.info(),settings:context.settingsStore.state().error,hello:!!hello,bridgeError}));process.exitCode=1;if(!stopping){stopping=true;child.stdin.write(JSON.stringify({action:'finish'})+'\n');}}).finally(()=>{for(const id of timerIds)clearTimeout(id);for(const c of httpChildren)c.kill();});
