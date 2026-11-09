'use strict';
var sha256=require('./sha256'),schema=require('./settings-schema');
var CATALOGUE='fahrschul.v2.settingsCatalogue',PACKET='fahrschul.v2.settingsPacket';
function get(storage,key){try{return storage.getItem(key);}catch(e){return null;}}
function put(storage,key,value){try{storage.setItem(key,value);}catch(e){/* In-memory use remains available. */}}
function request(url,callback){
 var finished=false,xhr,timer;function done(error,raw){if(finished)return;finished=true;if(timer)clearTimeout(timer);callback(error,raw);}
 try{xhr=new XMLHttpRequest();xhr.open('GET',url,true);xhr.onload=function(){if(xhr.status!==200)return done('HTTP_'+xhr.status);if(typeof xhr.responseText!=='string'||xhr.responseText.length>60000)return done('INVALID_DOWNLOAD');done(null,xhr.responseText);};xhr.onerror=function(){done('NETWORK_ERROR');};xhr.ontimeout=function(){done('TIMEOUT');};timer=setTimeout(function(){done('TIMEOUT');try{xhr.abort();}catch(e){}},15000);xhr.send();}catch(e){done('NETWORK_ERROR');}
}
function catalogue(raw){
 if(typeof raw!=='string'||raw.length>60000)throw Error('INVALID_CATALOGUE');var data=JSON.parse(raw),seen={};
 if(data.schemaVersion!==1||data.trainingCountry!=='DE'||!data.settings||data.settings.format!=='settings-v1'||!Array.isArray(data.settings.languages)||!data.settings.languages.length||data.settings.languages.length>64)throw Error('INVALID_CATALOGUE');
 data.settings.languages.forEach(function(d){
  if(typeof d.locale!=='string'||!/^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,2}$/.test(d.locale)||seen[d.locale]||typeof d.name!=='string'||!d.name.length||d.name.length>80||d.file!==d.locale+'/settings.json'||typeof d.sha256!=='string'||!/^[0-9a-f]{64}$/.test(d.sha256)||![null,0,1].some(function(v){return v===d.watchLanguage;})||d.watchLanguage===0&&d.locale!=='de'||d.watchLanguage===1&&d.locale!=='en')throw Error('INVALID_LANGUAGE_ENTRY');seen[d.locale]=true;
 });return data;
}
function descriptor(data,locale){var list=data.settings.languages;for(var i=0;i<list.length;i++)if(list[i].locale===locale)return list[i];throw Error('UNKNOWN_LANGUAGE');}
function packet(raw,d){
 if(typeof raw!=='string'||raw.length>60000||sha256(raw)!==d.sha256)throw Error('CHECKSUM_MISMATCH');var p=JSON.parse(raw);
 if(p.schemaVersion!==1||p.format!=='settings-v1'||p.trainingCountry!=='DE'||p.locale!==d.locale||!p.strings||typeof p.strings!=='object'||Array.isArray(p.strings))throw Error('INVALID_SETTINGS_PACKET');
 schema.keys.forEach(function(key){if(!Object.prototype.hasOwnProperty.call(p.strings,key)||typeof p.strings[key]!=='string'||p.strings[key].length>2000||!p.strings[key].length)throw Error('MISSING_TRANSLATION');});
 ['kinds','grounds'].forEach(function(key){if(!Array.isArray(p[key])||p[key].length!==schema[key]||p[key].some(function(v){return typeof v!=='string'||!v.length||v.length>200;}))throw Error('INVALID_SETTINGS_PACKET');});return p;
}
exports.create=function(baseURL,storage,options){
 options=options||{};var fetch=options.request||request,data=null,catalogueRaw=null,active=null,indexBusy=false,selection=0,selectBusy=false,error=null;
 try{catalogueRaw=get(storage,CATALOGUE);if(catalogueRaw)data=catalogue(catalogueRaw);}catch(e){catalogueRaw=null;}
 try{var saved=JSON.parse(get(storage,PACKET)||'null');if(saved){var original=catalogue(saved.catalogue),d=descriptor(original,saved.locale);active={packet:packet(saved.raw,d),descriptor:d,record:saved};if(!data){data=original;catalogueRaw=saved.catalogue;}}}catch(e){/* Invalid stored packets never become active. */}
 function effective(d){var copy={};Object.keys(d).forEach(function(k){copy[k]=d[k];});if(options.watch){copy.watchLanguage=null;var variants=data&&data.watchPacks,variant=variants&&variants[options.watch.tag];if(variant&&variant.schemaId===options.watch.schemaId&&variant.codecId===options.watch.codecId&&variant.format===options.watch.format&&Array.isArray(variant.languages)){var matches=variant.languages.filter(function(p){return p.locale===d.locale&&Number.isInteger(p.language)&&p.language>=0&&p.language<=63;});if(matches.length===1)copy.watchLanguage=matches[0].language;}}return copy;}
 function state(){return {catalogue:data?data.settings.languages.map(effective):[],active:active?{packet:active.packet,locale:active.descriptor.locale,name:active.descriptor.name,watchLanguage:effective(active.descriptor).watchLanguage}:null,loading:indexBusy||selectBusy,error:error};}
 function select(locale,callback){
  var d;try{d=descriptor(data,locale);}catch(e){callback('UNKNOWN_LANGUAGE');return;}
  var job=++selection;selectBusy=false;
  if(active&&active.descriptor.locale===locale&&active.descriptor.sha256===d.sha256){error=null;callback(null,state());return;}
  var usedCatalogue=catalogueRaw;selectBusy=true;error=null;
  fetch(baseURL+d.file,function(err,raw){if(job!==selection){callback('CANCELLED');return;}selectBusy=false;
   var p;if(!err)try{p=packet(raw,d);}catch(e){err=e.message;}
   if(err){error=err;callback(err,state());return;}
   var record={locale:locale,catalogue:usedCatalogue,raw:raw};active={packet:p,descriptor:d,record:record};put(storage,PACKET,JSON.stringify(record));error=null;callback(null,state());
  });
 }
 function refresh(preferred,callback){
  if(indexBusy){callback(null,state());return;}indexBusy=true;error=null;
  fetch(baseURL+'index.json',function(err,raw){indexBusy=false;var next;if(!err)try{next=catalogue(raw);}catch(e){err=e.message;}
   if(err){error=err;callback(err,state());return;}data=next;catalogueRaw=raw;put(storage,CATALOGUE,raw);
   var locale=active?active.descriptor.locale:preferred;if(typeof locale==='number'){var matches=data.settings.languages.map(effective).filter(function(d){return d.watchLanguage===locale;});locale=matches.length?matches[0].locale:'en';}try{descriptor(data,locale);}catch(e){locale=active?null:(data.settings.languages.some(function(d){return d.locale==='en';})?'en':data.settings.languages[0].locale);}
   if(locale&&!selectBusy)select(locale,callback);else callback(null,state());
  });
 }
 return {state:state,select:select,refresh:refresh,exportCache:function(){return {catalogue:catalogueRaw,packet:active?JSON.stringify(active.record):null};}};
};
