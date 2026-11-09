'use strict';
var configHTML=require('./config-html');
var languagePack=require('./lang-pack');
var packTransfer=null;
var timeline=require('./timeline').create(Pebble,localStorage);
var KEYS={op:1,rid:2,id:3,cls:4,kind:5,when:6,lead1:7,lead2:8,units:9,topic:10,revision:11,status:12,payload:13,part:14,total:15,extra:16,language:17};
var RESPONSE_NAMES={2:'Rid',12:'Status',13:'Payload',14:'Part',15:'Total'};
function field(data,key){return data[key]!==undefined?data[key]:data[RESPONSE_NAMES[key]];}
var STORE='fahrschul.v2.',snapshot=null,parts=[],expected=0,batch=0,lastReply=0,waiting=false,retries=0,retryTimer=null;
try{snapshot=JSON.parse(localStorage.getItem(STORE+'snapshot')||'null');}catch(e){}
function pending(){try{return JSON.parse(localStorage.getItem(STORE+'pending')||'null');}catch(e){return null;}}
function empty(){return {version:2,language:Number(localStorage.getItem(STORE+'language')||0),revision:0,cls:4,profile:0,entries:[],counts:[],topics:[]};}
function freshState(){
 var s=snapshot?JSON.parse(JSON.stringify(snapshot)):empty();s.fresh=lastReply>0&&Date.now()-lastReply<20000;s.timeline=timeline.state();
 if(!s.error)s.error=localStorage.getItem(STORE+'lastError')||'';
 var command=pending();
 if(command&&command.action==='language'){s.language=command.language;if(s.languagePack)s.languagePack.transferring=command.language===1&&(!s.languagePack.ready||s.languagePack.id!==languagePack.id);}
 if(pending())s.pending=s.language?'Transfer pending. Open the watch app and connect Bluetooth.':'Übertragung ausstehend. Bitte Uhr-App öffnen und Bluetooth verbinden.';
 return s;
}
function requestSnapshot(){var data={};data[KEYS.op]=0;data[KEYS.rid]=0;try{Pebble.sendAppMessage(data,function(){},function(){});}catch(e){}}
function publish(result){if(typeof Pebble.sendConfigMessage==='function')Pebble.sendConfigMessage({type:'state',state:freshState(),result:result||null});}
function nextRequestId(){var previous=Number(localStorage.getItem(STORE+'nonce')||0),rid=Math.max(previous+1,Date.now()%2000000000);localStorage.setItem(STORE+'nonce',String(rid));return rid;}
function sendPackPart(){
 var transfer=packTransfer;if(!transfer)return;var sentPart=transfer.part;waiting=true;
 var data={};data[KEYS.op]=4;data[KEYS.rid]=transfer.rid;data[KEYS.id]=languagePack.id;data[KEYS.part]=transfer.part;data[KEYS.total]=languagePack.chunks.length;data[KEYS.payload]=languagePack.chunks[transfer.part];
 function retry(){if(packTransfer!==transfer||transfer.part!==sentPart)return;waiting=false;packTransfer=null;if(retries++<2)retryTimer=setTimeout(transmit,1500);else{localStorage.setItem(STORE+'lastError','Language pack transfer paused. Reconnect the watch.');publish();}}
 try{Pebble.sendAppMessage(data,function(){if(packTransfer===transfer&&transfer.part===sentPart)retryTimer=setTimeout(retry,7000);},retry);}catch(e){retry();}
}
function transmit(){
 var p=pending();if(!p||waiting)return;
 if(p.action==='language'&&p.language===1&&snapshot&&snapshot.languagePack&&(!snapshot.languagePack.ready||snapshot.languagePack.id!==languagePack.id)){packTransfer={rid:nextRequestId(),part:0};sendPackPart();return;}
 waiting=true;var data={};
 data[KEYS.op]=p.action==='delete'?2:p.action==='language'?3:1;data[KEYS.rid]=p.rid;data[KEYS.id]=p.id||0;data[KEYS.revision]=p.revision||0;
 if(p.action==='save')['cls','kind','when','lead1','lead2','units','topic','extra'].forEach(function(k){data[KEYS[k]]=p[k]||0;});
 if(p.action==='language')data[KEYS.language]=p.language;
 try{Pebble.sendAppMessage(data,function(){
  retryTimer=setTimeout(function(){waiting=false;if(retries++<2)transmit();},7000);
 },function(){waiting=false;if(retries++<2)retryTimer=setTimeout(transmit,1500);});}catch(e){waiting=false;}
}
function queueCommand(p){
 if(!p||['save','delete','language'].indexOf(p.action)===-1)return {error:'INVALID_COMMAND'};
 if(pending())return {error:'TRANSFER_PENDING',state:freshState()};
 p.rid=nextRequestId();
 localStorage.setItem(STORE+'nonce',String(p.rid));localStorage.setItem(STORE+'pending',JSON.stringify(p));
 waiting=false;retries=0;transmit();return {queued:true,requestId:p.rid,state:freshState()};
}
Pebble.addEventListener('ready',function(){requestSnapshot();retries=0;transmit();});
// Older mobile apps still get an immediate, synchronous configuration page. No waiting for
// a watch response before openURL, and no navigation from a timer callback.
Pebble.addEventListener('showConfiguration',function(){
 var state=JSON.stringify(freshState()).replace(/</g,'\\u003c');
 var html=configHTML.replace('/*__INITIAL_STATE__*/','window.__FAHRSCHUL_INITIAL_STATE__='+state+';');
 Pebble.openURL('data:text/html;charset=utf-8,'+encodeURIComponent(html));requestSnapshot();
});
// Current mobile apps load the bundled configPage directly; it stays open while syncing.
Pebble.addEventListener('configmessage',function(e){
 var m=e.data||{};
 if(m.type==='timeline'&&typeof m.enabled==='boolean'){timeline.setEnabled(m.enabled);e.respond({state:freshState()});publish();requestSnapshot();return;}
 if(m.type==='snapshot'){e.respond({state:freshState()});requestSnapshot();if(pending()&&!waiting){retries=0;transmit();}return;}
 if(m.type==='command'){e.respond(queueCommand(m.command));return;}
 e.respond({error:'INVALID_MESSAGE'});
});
Pebble.addEventListener('appmessage',function(event){
 var d=event.payload;var total=Number(field(d,KEYS.total)),part=Number(field(d,KEYS.part)),rid=Number(field(d,KEYS.rid)),status=Number(field(d,KEYS.status));
 if(!Number.isFinite(total)||total<1||total>20||part<0||part>=total)return;
 if(part===0){parts=[];expected=total;batch=rid;}if(rid!==batch||total!==expected)return;parts[part]=String(field(d,KEYS.payload)||'');
 for(var i=0;i<total;i++)if(typeof parts[i]!=='string')return;
 try{var next=JSON.parse(parts.join(''));if(next.version!==2||!Array.isArray(next.entries))return;snapshot=next;localStorage.setItem(STORE+'snapshot',JSON.stringify(snapshot));localStorage.setItem(STORE+'language',String(snapshot.language||0));lastReply=Date.now();}catch(e){return;}
 if(packTransfer&&rid===packTransfer.rid){
  if(retryTimer)clearTimeout(retryTimer);
  if(status<0){packTransfer=null;waiting=false;if(retries++<2)retryTimer=setTimeout(transmit,1500);else{localStorage.setItem(STORE+'lastError',snapshot.error||'Language pack transfer failed.');publish();}return;}
  if(!snapshot.languagePack)return;
  if(snapshot.languagePack.ready&&snapshot.languagePack.id===languagePack.id){packTransfer=null;waiting=false;retries=0;transmit();return;}
  if(snapshot.languagePack.received&(1<<packTransfer.part)){packTransfer.part++;if(packTransfer.part<languagePack.chunks.length)sendPackPart();}
  publish();return;
 }
 var p=pending(),result=null;
 if(p&&p.rid===rid){if(retryTimer)clearTimeout(retryTimer);waiting=false;localStorage.removeItem(STORE+'pending');result={rid:rid,status:status,action:p.action,id:p.id||snapshot.savedId||0};if(status<0){snapshot.error=snapshot.error||'Die Uhr hat die Änderung abgelehnt. Bitte Eingabe prüfen.';localStorage.setItem(STORE+'lastError',snapshot.error);}else localStorage.removeItem(STORE+'lastError');}
 timeline.sync(snapshot);publish(result);
 if(snapshot.language===1&&snapshot.languagePack&&(!snapshot.languagePack.ready||snapshot.languagePack.id!==languagePack.id)&&!pending())queueCommand({action:'language',language:1,revision:snapshot.revision});
});
Pebble.addEventListener('webviewclosed',function(event){
 if(!event.response||event.response==='CANCELLED')return;var p;try{p=JSON.parse(decodeURIComponent(event.response));}catch(e){return;}
 if(p.action==='timeline'&&typeof p.enabled==='boolean'){timeline.setEnabled(p.enabled);requestSnapshot();return;}
 queueCommand(p);
});
