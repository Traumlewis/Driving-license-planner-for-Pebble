'use strict';
const assert=require('assert'),vm=require('vm'),fs=require('fs');
const source=fs.readFileSync(__dirname+'/../src/pkjs/index.js','utf8'),metadata=require('../src/pkjs/lang-pack'),packs=require('../tools/language-packets.json').packs;
const remote=require('../src/pkjs/remote-language'),folder=__dirname+'/../../../Packs/German/Languages/'+metadata.appVersion;
function setup(storage={}){
 const events={},sent=[],requests=[],timers=new Map();let nextTimer=1;
 const context={require:n=>n==='./lang-pack'?metadata:n==='./remote-language'?{create:(m,s)=>remote.create(m,s,{request:(url,cb)=>{requests.push(url);cb(null,fs.readFileSync(folder+'/'+url.split('/').pop(),'utf8'));}})}:n==='./timeline'?require('../src/pkjs/timeline'):'/*__INITIAL_STATE__*/',Date,Number,JSON,Array,String,Math,encodeURIComponent,decodeURIComponent,console,
 localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]},setTimeout:(fn)=>{const id=nextTimer++;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id),
 Pebble:{addEventListener:(e,fn)=>events[e]=fn,sendAppMessage:(m,ack)=>{sent.push(JSON.parse(JSON.stringify(m)));if(ack)ack();},sendConfigMessage:()=>{},insertTimelinePin:()=>{},deleteTimelinePin:()=>{}}};
 vm.runInNewContext(source,context);
 function state(rid=0,active=0,ready=true,received=0,preferred=active,status=0){const pack=packs[active],s={version:2,revision:1,language:preferred,entries:[],cls:4,languagePack:{id:ready?pack.id:0,language:ready?active:-1,bytes:ready?pack.size:0,ready,received}};events.appmessage({payload:{2:rid,12:status,14:0,15:1,13:JSON.stringify(s)}});}
 function command(language){let response;events.configmessage({data:{type:'command',command:{action:'language',language}},respond:r=>response=r});return response;}
 return {events,sent,requests,timers,storage,state,command,last:()=>sent[sent.length-1]};
}
const app=setup();app.state();
function transfer(target,old){
 assert(app.command(target).queued);const commandRid=JSON.parse(app.storage['fahrschul.v2.pending']).rid;let mask=0;
 for(let part=0;part<packs[target].chunks.length;part++){
  const m=app.last();assert.strictEqual(m[1],4);assert.notStrictEqual(m[2],commandRid);assert.strictEqual(m[14],part);assert.strictEqual(m[13],packs[target].chunks[part]);assert.strictEqual(m[3],packs[target].id);
  if(part){const n=app.sent.length;app.state(m[2],old,true,mask);assert.strictEqual(app.sent.length,n,'duplicate ACK advanced transfer');}
  mask|=1<<part;const last=part===packs[target].chunks.length-1;app.state(m[2],last?target:old,true,mask);
 }
 assert.strictEqual(app.last()[1],3);assert.strictEqual(app.last()[17],target);app.state(commandRid,target,true,mask);assert(!app.storage['fahrschul.v2.pending']);
}
transfer(1,0);transfer(0,1);transfer(1,0);assert.strictEqual(app.requests.length,6);assert.strictEqual(JSON.parse(app.storage['fahrschul.v2.languagePacket']).language,1);assert.strictEqual(app.command(7).error,'INVALID_COMMAND');
assert(app.command(1).queued);assert.strictEqual(app.last()[1],3,'active pack should be reused');app.state(app.last()[2],1);
const resume=setup();resume.state();resume.command(1);resume.state(resume.last()[2],0,true,0,0,-3);assert(resume.storage['fahrschul.v2.pending']);
const restart=setup(resume.storage);restart.events.ready();assert.strictEqual(restart.last()[1],4);assert.strictEqual(restart.last()[14],0);assert.strictEqual(restart.requests.length,0,'verified phone cache should resume without Internet');
for(const selected of [0,1]){const cold=setup();cold.state(0,selected,false,0,selected);assert.strictEqual(cold.last()[1],4);assert.strictEqual(cold.last()[3],packs[selected].id);}
console.log('PASS remote phone swap: DE→EN→DE→EN reloads the absent pack; active reuse, old-language ACKs, stale ACK rejection, restart and either-language bootstrap');
