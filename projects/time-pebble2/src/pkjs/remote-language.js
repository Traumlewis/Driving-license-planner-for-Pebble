'use strict';
var sha256=require('./sha256');
var CACHE='fahrschul.v2.languagePacket';
function crc32(chunks){var crc=0xffffffff;chunks.forEach(function(chunk){for(var i=0;i<chunk.length;i+=2){crc^=parseInt(chunk.substr(i,2),16);for(var b=0;b<8;b++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}});return (crc^0xffffffff)>>>0;}
function download(url,callback){
 var done=false,xhr,timer;function finish(error,raw){if(done)return;done=true;if(timer)clearTimeout(timer);callback(error,raw);}
 try{
  xhr=new XMLHttpRequest();xhr.open('GET',url,true);
  xhr.onload=function(){if(xhr.status!==200)return finish('HTTP_'+xhr.status);if(typeof xhr.responseText!=='string'||xhr.responseText.length>20000)return finish('INVALID_DOWNLOAD');finish(null,xhr.responseText);};
  xhr.onerror=function(){finish('NETWORK_ERROR');};xhr.ontimeout=function(){finish('DOWNLOAD_TIMEOUT');};
  timer=setTimeout(function(){finish('DOWNLOAD_TIMEOUT');try{if(xhr.abort)xhr.abort();}catch(e){}},15000);xhr.send();
 }catch(e){finish('NETWORK_ERROR');}
}
exports.create=function(metadata,storage,options){
 options=options||{};var request=options.request||download,cached=null,flight=null,lastError=null,nextAttempt=0;var now=options.now||Date.now;
 function descriptor(language){if(language!==0&&language!==1)throw Error('INVALID_LANGUAGE');return metadata.packs[language];}
 function validate(raw,language){
  var p=descriptor(language);if(typeof raw!=='string'||raw.length>20000||sha256(raw)!==p.sha256)throw Error('CHECKSUM_MISMATCH');
  var packet=JSON.parse(raw);
  if(packet.language!==language||packet.id!==p.id||packet.crc!==p.crc||packet.size!==p.size||!Array.isArray(packet.chunks)||packet.chunks.length!==Math.ceil(p.size/128))throw Error('INCOMPATIBLE_PACKET');
  var size=0;packet.chunks.forEach(function(c,i){if(typeof c!=='string'||!/^(?:[0-9a-f]{2}){1,128}$/i.test(c)||i<packet.chunks.length-1&&c.length!==256)throw Error('INVALID_PACKET');size+=c.length/2;});
  if(size!==p.size||crc32(packet.chunks)!==p.crc)throw Error('INVALID_PACKET');return packet;
 }
 try{var stored=JSON.parse(storage.getItem(CACHE)||'null');if(stored&&stored.appVersion===metadata.appVersion){cached={language:stored.language,packet:validate(stored.raw,stored.language),raw:stored.raw};}else if(stored)storage.removeItem(CACHE);}catch(e){try{storage.removeItem(CACHE);}catch(ignore){}}
 function info(){return {downloading:!!flight,cachedLanguage:cached?cached.language:-1,error:lastError};}
 function ensure(language,callback){
  var p;try{p=descriptor(language);}catch(e){callback(e.message);return;}
  if(cached&&cached.language===language){lastError=null;callback(null,cached.packet);return;}
  if(lastError&&now()<nextAttempt){callback(lastError);return;}
  if(flight){if(flight.language===language)flight.callbacks.push(callback);else callback('DOWNLOAD_BUSY');return;}
  var job={language:language,callbacks:[callback]};flight=job;lastError=null;
  function finish(error,raw,packet){
   if(flight!==job)return;flight=null;lastError=error||null;nextAttempt=error?now()+30000:0;
   if(!error){cached={language:language,packet:packet,raw:raw};try{storage.setItem(CACHE,JSON.stringify({appVersion:metadata.appVersion,language:language,raw:raw}));}catch(e){/* The verified packet can still be forwarded from memory. */}}
   job.callbacks.forEach(function(cb){cb(error,packet);});
  }
  var base=metadata.baseURL+metadata.appVersion+'/';
  request(base+'manifest.json',function(error,raw){
   if(flight!==job)return;if(error){finish(error);return;}
   try{
    if(typeof raw!=='string'||raw.length>20000)throw Error('INVALID_MANIFEST');var m=JSON.parse(raw);
    if(m.schemaVersion!==1||m.trainingCountry!=='DE'||m.rulesetDirectory!=='Germany'||m.appVersion!==metadata.appVersion||m.format!=='LP3/swap128'||m.scope!=='menu'||!Array.isArray(m.languages))throw Error('INCOMPATIBLE_MANIFEST');
    var matches=m.languages.filter(function(x){return x.language===language;});if(matches.length!==1)throw Error('INVALID_MANIFEST');var entry=matches[0];
    if(entry.locale!==p.locale||entry.file!==p.file||entry.packId!==p.id||entry.crc32!==p.crc||entry.payloadBytes!==p.size||entry.sha256!==p.sha256)throw Error('INCOMPATIBLE_MANIFEST');
   }catch(e){finish(e.message||'INVALID_MANIFEST');return;}
   request(base+p.file,function(error,raw){if(flight!==job)return;if(error){finish(error);return;}try{var packet=validate(raw,language);}catch(e){finish(e.message||'INVALID_PACKET');return;}finish(null,raw,packet);});
  });
 }
 return {ensure:ensure,info:info,descriptor:descriptor,retry:function(){nextAttempt=0;}};
};
