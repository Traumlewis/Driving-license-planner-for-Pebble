'use strict';
const assert=require('assert'),vm=require('vm'),fs=require('fs');
const source=fs.readFileSync(__dirname+'/../src/pkjs/index.js','utf8'),pack=require('../src/pkjs/lang-pack');
function setup(storage={}){
 const events={},sent=[],timers=new Map();let nextTimer=1;
 const context={require:n=>n==='./lang-pack'?pack:n==='./timeline'?require('../src/pkjs/timeline'):'/*__INITIAL_STATE__*/',Date,Number,JSON,Array,String,Math,encodeURIComponent,decodeURIComponent,console,
 localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]},setTimeout:(fn)=>{const id=nextTimer++;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id),
 Pebble:{addEventListener:(e,fn)=>events[e]=fn,sendAppMessage:(m,ack)=>{sent.push(JSON.parse(JSON.stringify(m)));if(ack)ack();},sendConfigMessage:()=>{},insertTimelinePin:()=>{},deleteTimelinePin:()=>{}}};
 vm.runInNewContext(source,context);
 function state(rid=0,ready=false,received=0,language=0,status=0){const s={version:2,revision:1,language,entries:[],cls:4,languagePack:{id:pack.id,bytes:pack.size,ready,received}};events.appmessage({payload:{2:rid,12:status,14:0,15:1,13:JSON.stringify(s)}});}
 function command(language){let response;events.configmessage({data:{type:'command',command:{action:'language',language}},respond:r=>response=r});return response;}
 return {events,sent,timers,storage,state,command,last:()=>sent[sent.length-1]};
}
const app=setup();app.state();assert(app.command(1).queued);const first=app.last(),commandRid=JSON.parse(app.storage['fahrschul.v2.pending']).rid;
assert.strictEqual(first[1],4);assert.notStrictEqual(first[2],commandRid);
let mask=0;
for(let part=0;part<pack.chunks.length;part++){
 const m=app.last();assert.strictEqual(m[1],4);assert.strictEqual(m[14],part);assert.strictEqual(m[13],pack.chunks[part]);
 if(part){const before=app.sent.length;app.state(m[2],false,mask);assert.strictEqual(app.sent.length,before,'stale ACK advanced transfer');}
 mask|=1<<part;app.state(m[2],part===pack.chunks.length-1,mask);
}
assert.strictEqual(app.last()[1],3);assert.strictEqual(app.last()[17],1);assert(app.storage['fahrschul.v2.pending']);
app.state(commandRid,true,mask,1);assert(!app.storage['fahrschul.v2.pending']);
assert(app.command(0).queued);assert.strictEqual(app.last()[1],3);app.state(app.last()[2],true,mask,0);
assert(app.command(1).queued);assert.strictEqual(app.last()[1],3,'cached package was needlessly uploaded');app.state(app.last()[2],true,mask,1);
const resume=setup();resume.state();resume.command(1);const transferRid=resume.last()[2];resume.state(transferRid,false,0,0,-3);assert(resume.storage['fahrschul.v2.pending']);assert.strictEqual(resume.last()[1],4);
const restart=setup(resume.storage);restart.events.ready();assert.strictEqual(restart.last()[1],4);assert.strictEqual(restart.last()[14],0);
const repair=setup();repair.state(0,false,0,1);assert.strictEqual(repair.last()[1],4,'missing selected English pack not restored automatically');
console.log('PASS phone language packs: ordered native ACKs, duplicate ACK rejection, deferred language activation, cached switching, failed transfer persistence/restart and automatic missing-pack repair');
