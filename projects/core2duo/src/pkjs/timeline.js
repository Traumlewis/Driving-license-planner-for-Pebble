'use strict';
// Local pins work with sideloaded apps. No token or external timeline server is used.
var PREFIX='fahrschul.lesson.',STORE='fahrschul.v2.timeline.';
var CLASSES=['AM','A1','A2','A','B','BE','C1','C1E','C','CE','D1','D1E','D','DE','L','T'];
var KINDS=[
 ['Praxis | Übungsfahrt','Practice | General driving'],
 ['Praxis | Landstraße','Practice | Country roads'],
 ['Praxis | Autobahn','Practice | Motorway'],
 ['Praxis | Nachtfahrt','Practice | Night driving'],
 ['Praxis | Grundausbildung','Practice | Basic training'],
 ['Theorie | Grundstoff','Theory | Core syllabus'],
 ['Theorie | Zusatzstoff','Theory | Class syllabus']
];
function pinForEntry(e,language,generation){
 if(!Array.isArray(e)||!Number.isInteger(e[0])||e[0]<1||!Number.isFinite(e[1])||!CLASSES[e[2]]||!KINDS[e[3]])return null;
 var en=language===1,duration=e[4]*(e[3]>=5?90:45)+(e[8]||0);
 if(!Number.isInteger(duration)||duration<1)return null;
 var body=(en?'Licence class ':'Führerscheinklasse ')+CLASSES[e[2]]+'\n'+KINDS[e[3]][en?1:0]+'\n'+duration+(en?' minutes':' Minuten');
 if(e[3]>=5&&e[7]!==255)body+='\n'+(en?'Topic ':'Thema ')+(e[7]<12?e[7]+1:e[7]-11);
 return {id:PREFIX+e[0]+(generation?'.g'+generation:''),time:new Date(e[1]*1000).toISOString(),duration:duration,
  layout:{type:'calendarPin',title:CLASSES[e[2]]+' | '+KINDS[e[3]][en?1:0],body:body}};
}
function create(pebble,storage){
 var enabled=storage.getItem(STORE+'enabled')!=='0',generation=Number(storage.getItem(STORE+'generation')||0),ledger={},last=null,started=false,status='waiting';
 try{var saved=JSON.parse(storage.getItem(STORE+'pins')||'{}');Object.keys(saved).forEach(function(id){if(id.indexOf(PREFIX)===0&&typeof saved[id]==='string')ledger[id]=saved[id];});}catch(e){}
 function supported(){return typeof pebble.insertTimelinePin==='function'&&typeof pebble.deleteTimelinePin==='function';}
 function persist(){storage.setItem(STORE+'pins',JSON.stringify(ledger));}
 function state(){return {enabled:enabled,supported:supported(),status:status};}
 function sync(snapshot){
  if(snapshot)last=snapshot;
  if(!supported()){status='unsupported';return state();}
  var desired={},failed=false;
  if(enabled&&last)last.entries.forEach(function(e){var pin=pinForEntry(e,last.language,generation);if(pin)desired[pin.id]=pin;});
  // An enabled startup waits for a real watch snapshot, rather than reviving cached appointments.
  if(enabled&&!last){status='waiting';return state();}
  Object.keys(ledger).forEach(function(id){
   if(desired[id])return;
   try{pebble.deleteTimelinePin(id);delete ledger[id];persist();}catch(e){failed=true;}
  });
  Object.keys(desired).forEach(function(id){
   var signature=JSON.stringify(desired[id]);
   if(started&&ledger[id]===signature)return;
   try{
    // Remember the ID before dispatch, so a restart/disable can remove a partially sent pin.
    ledger[id]='';persist();pebble.insertTimelinePin(desired[id]);ledger[id]=signature;persist();
   }catch(e){failed=true;}
  });
  started=true;status=failed?'retry':enabled?'submitted':'off';return state();
 }
 function setEnabled(value){
  // Some timeline hosts retain deletion tombstones. Re-enabling starts a new set of IDs.
  if(value&&!enabled){generation++;storage.setItem(STORE+'generation',String(generation));}
  enabled=value;storage.setItem(STORE+'enabled',value?'1':'0');started=false;return sync();
 }
 // Disabled preferences also clean up an interrupted removal after a JS restart.
 if(!enabled)sync();
 return {sync:sync,setEnabled:setEnabled,state:state};
}
module.exports={create:create,pinForEntry:pinForEntry};
