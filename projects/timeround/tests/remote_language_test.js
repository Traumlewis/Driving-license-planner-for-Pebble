'use strict';
const assert=require('assert'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const create=require('../src/pkjs/remote-language').create,metadata=require('../src/pkjs/lang-pack'),sha=require('../src/pkjs/sha256');
const folder=path.resolve(__dirname,'../../../Packs/Germany/Languages',metadata.appVersion),manifest=fs.readFileSync(path.join(folder,'manifest.json'),'utf8');
const packets=metadata.packs.map(p=>fs.readFileSync(path.join(folder,p.file),'utf8'));
function storage(){let state={};return {state,getItem:k=>state[k]||null,setItem:(k,v)=>state[k]=v,removeItem:k=>delete state[k]};}
function setup(store=storage(),modify=(raw)=>raw){const requests=[];let clock=1;const api=create(metadata,store,{now:()=>clock,request:(url,cb)=>{requests.push(url);const name=url.split('/').pop();let raw=name==='manifest.json'?manifest:packets[name==='de.json'?0:1];raw=modify(raw,name);if(raw instanceof Error)cb(raw.message);else cb(null,raw);}});return {api,store,requests,later:()=>clock+=31000};}
function ensure(t,language){let result;t.api.ensure(language,(error,packet)=>result={error,packet});assert(result);return result;}
for(const text of ['', 'abc','Umlaute äöü und 😎','a'.repeat(20000)])assert.strictEqual(sha(text),crypto.createHash('sha256').update(text).digest('hex'));
const ok=setup();assert(!ensure(ok,0).error);assert.strictEqual(ok.requests.length,2);assert.strictEqual(ok.api.info().cachedLanguage,0);assert.strictEqual(Object.keys(ok.store.state).length,1);
const before=ok.requests.length;assert(!ensure(ok,0).error);assert.strictEqual(ok.requests.length,before);assert(!ensure(ok,1).error);assert.strictEqual(ok.api.info().cachedLanguage,1);assert.strictEqual(Object.keys(ok.store.state).length,1);
assert.strictEqual(JSON.parse(Object.values(ok.store.state)[0]).language,1);
const offline=setup(ok.store,()=>new Error('NETWORK_ERROR'));assert(!ensure(offline,1).error);assert.strictEqual(offline.requests.length,0,'cached packet should work offline');assert(ensure(offline,0).error);assert.strictEqual(offline.api.info().cachedLanguage,1);
const count=offline.requests.length;ensure(offline,0);assert.strictEqual(offline.requests.length,count,'failure backoff was ignored');offline.api.retry();ensure(offline,0);assert.strictEqual(offline.requests.length,count+1);
for(const mutate of [
 (s,n)=>n==='manifest.json'?s.replace('"trainingCountry": "DE"','"trainingCountry": "AT"'):s,
 (s,n)=>n==='manifest.json'?s.replace(metadata.appVersion,'0.0.0'):s,
 (s,n)=>n==='manifest.json'?s.replace('de.json','../../foreign.json'):s,
 (s,n)=>n==='manifest.json'?s:s+' ',
 (s,n)=>n==='manifest.json'?s:'not json',
 ()=>new Error('HTTP_404')
]){const bad=setup(storage(),mutate);assert(ensure(bad,0).error);assert.strictEqual(bad.api.info().cachedLanguage,-1);assert.strictEqual(Object.keys(bad.store.state).length,0);}
const corrupt=storage();corrupt.setItem('fahrschul.v2.languagePacket',JSON.stringify({appVersion:metadata.appVersion,language:0,raw:'invalid'}));const fixed=setup(corrupt);assert(!ensure(fixed,0).error);assert.strictEqual(fixed.requests.length,2);
// An unsuccessful replacement leaves the previous verified cache intact.
const preserved=setup(ok.store,(s,n)=>n==='manifest.json'?s:s+'bad');const saved=JSON.stringify(ok.store.state);assert(ensure(preserved,0).error);assert.strictEqual(JSON.stringify(ok.store.state),saved);
let callback;const lateStore=storage(),late=create(metadata,lateStore,{request:(url,cb)=>callback=cb});let calls=0;late.ensure(0,()=>calls++);callback('DOWNLOAD_TIMEOUT');callback(null,manifest);assert.strictEqual(calls,1);assert.strictEqual(Object.keys(lateStore.state).length,0);
console.log('PASS remote language client: SHA-256/reference vectors, version/country/identity validation, single cache, offline reuse, corruption, backoff, timeout and preserved previous cache');
