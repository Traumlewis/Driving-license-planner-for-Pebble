'use strict';
const assert=require('assert'),vm=require('vm'),fs=require('fs');
const source=fs.readFileSync(__dirname+'/../src/pkjs/index.js','utf8');
const events={},storage={},sent=[],timers=[],urls=[],pushed=[];
const pins=[],deletions=[];
const context={require:name=>name==='./timeline'?require('../src/pkjs/timeline'):'<script>/*__INITIAL_STATE__*/</script>',Date,Number,JSON,Array,String,Math,encodeURIComponent,decodeURIComponent,console,localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=String(v),removeItem:k=>delete storage[k]},setTimeout:(fn,delay)=>{timers.push({fn,delay});return timers.length;},clearTimeout:()=>{},Pebble:{insertTimelinePin:p=>pins.push(p),deleteTimelinePin:id=>deletions.push(id),addEventListener:(event,fn)=>events[event]=fn,sendAppMessage:(data,ack)=>{sent.push(data);if(ack)ack();},openURL:url=>urls.push(url),sendConfigMessage:m=>pushed.push(m)}};
vm.runInNewContext(source,context);
function snapshot(rid,status,revision,error,named=true,entries=[],savedId=0){const data=JSON.stringify({version:2,language:0,revision,cls:4,entries,savedId,error:error||''}),split=Math.floor(data.length/2);for(let p=0;p<2;p++){const d=named?{Rid:rid,Status:status,Part:p,Total:2,Payload:p?data.slice(split):data.slice(0,split)}:{2:rid,12:status,14:p,15:2,13:p?data.slice(split):data.slice(0,split)};events.appmessage({payload:d});}}
// A legacy settings URL must open inside showConfiguration itself, even when no watch replies.
events.showConfiguration();assert.strictEqual(urls.length,1);assert(decodeURIComponent(urls[0]).includes('"fresh":false'));assert(!timers.some(t=>t.delay===6000));
snapshot(0,0,10);assert(JSON.parse(storage['fahrschul.v2.snapshot']).revision===10);assert(pushed[pushed.length-1].state.fresh);
let reply;events.configmessage({data:{type:'snapshot'},respond:r=>reply=r});assert(reply.state.fresh&&sent[sent.length-1][1]===0);
events.configmessage({data:{type:'command',command:{action:'save',id:0,revision:10,cls:4,kind:1,when:1900000000,lead1:1440,lead2:30,units:2,extra:5,topic:255}},respond:r=>reply=r});
assert(reply.queued&&storage['fahrschul.v2.pending']);const message=sent[sent.length-1];assert.strictEqual(message[1],1);assert.strictEqual(message[16],5);
const rid=message[2];snapshot(rid,0,11,'',true,[],123);assert(!storage['fahrschul.v2.pending']);assert(pushed[pushed.length-1].result.action==='save');assert.strictEqual(pushed[pushed.length-1].result.id,123);
events.webviewclosed({response:encodeURIComponent(JSON.stringify({action:'delete',id:2,revision:11}))});const del=sent[sent.length-1];snapshot(del[2],-2,12,'Daten geändert');assert(storage['fahrschul.v2.lastError']);
events.webviewclosed({response:'CANCELLED'});assert(!storage['fahrschul.v2.pending']);
events.configmessage({data:{type:'command',command:{action:'language',id:0,language:1,revision:12}},respond:r=>reply=r});const languageMessage=sent[sent.length-1];assert.strictEqual(languageMessage[1],3);assert.strictEqual(languageMessage[17],1);snapshot(languageMessage[2],0,13,'',false);assert(!storage['fahrschul.v2.pending']);
console.log('PASS PKJS: named and numeric response keys, immediate legacy opening, packaged live bridge, snapshots, application ACK and conflict handling');
events.configmessage({data:{type:'timeline',enabled:false},respond:r=>reply=r});assert.strictEqual(reply.state.timeline.enabled,false);assert.strictEqual(storage['fahrschul.v2.timeline.enabled'],'0');
events.webviewclosed({response:encodeURIComponent(JSON.stringify({action:'timeline',enabled:true}))});assert.strictEqual(storage['fahrschul.v2.timeline.enabled'],'1');assert(!storage['fahrschul.v2.pending']);
console.log('PASS PKJS Timeline preference: live settings and legacy close persist without an open watch command');

snapshot(0,0,14,'',true,[[20,1900000000,4,1,1,60,15,255,5]]);assert.strictEqual(pins.length,1);
events.configmessage({data:{type:'timeline',enabled:false},respond:r=>reply=r});assert.strictEqual(deletions[0],pins[0].id);
events.configmessage({data:{type:'timeline',enabled:true},respond:r=>reply=r});assert.strictEqual(pins.length,2);
snapshot(0,0,15);assert.strictEqual(deletions[1],pins[1].id);assert.notStrictEqual(pins[0].id,pins[1].id);
console.log('PASS PKJS Timeline integration: fresh watch snapshots add pins, disable deletes them, enable restores them and deleted appointments are removed');

events.configmessage({data:{type:'command',command:{action:'reminder2',enabled:false,revision:15}},respond:r=>reply=r});assert.strictEqual(reply.error,'INVALID_COMMAND');
console.log('PASS obsolete global reminder-2 command is removed; appointment lead2=0 remains supported');
