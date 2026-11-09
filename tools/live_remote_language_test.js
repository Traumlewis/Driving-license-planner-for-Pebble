'use strict';
// Run the production client's HTTP path against public GitHub using a desktop XHR adapter.
const fs=require('fs'),path=require('path'),assert=require('assert'),cp=require('child_process');
const project=path.resolve(__dirname,'../projects/time2/src/pkjs'),metadata=require(project+'/lang-pack'),calls=[];
let offline=false;
class XHR {
 open(method,url){assert.strictEqual(method,'GET');assert(url.startsWith(metadata.baseURL));this.url=url;}
 send(){calls.push(this.url);if(offline){setImmediate(()=>this.onerror());return;}this.child=cp.execFile('curl',['--fail','--silent','--show-error','--location','--max-time','15','--max-filesize','20000',this.url],{encoding:'utf8',maxBuffer:30000},(error,stdout)=>{if(this.aborted)return;if(error){this.onerror();return;}this.status=200;this.responseText=stdout;this.onload();});}
 abort(){this.aborted=true;if(this.child)this.child.kill();}
}
global.XMLHttpRequest=XHR;
const create=require(project+'/remote-language').create,state={},storage={getItem:k=>state[k]||null,setItem:(k,v)=>state[k]=v,removeItem:k=>delete state[k]};
const client=create(metadata,storage),out=path.resolve('/tmp/real-github-language-'+metadata.appVersion);fs.mkdirSync(out,{recursive:true});
function ensure(api,language){return new Promise((resolve,reject)=>api.ensure(language,(error,packet)=>error?reject(Error(error)):resolve(packet)));}
(async()=>{
 for(const language of [0,1]){const packet=await ensure(client,language),record=JSON.parse(state['fahrschul.v2.languagePacket']);assert.strictEqual(record.language,language);assert.strictEqual(Object.keys(state).length,1);assert.strictEqual(packet.id,metadata.packs[language].id);fs.writeFileSync(path.join(out,language?'en.json':'de.json'),record.raw);}
 assert.strictEqual(calls.length,4);offline=true;const copy=JSON.stringify(state),fresh=create(metadata,storage);await ensure(fresh,1);assert.strictEqual(calls.length,4);let failed=false;try{await ensure(fresh,0);}catch(e){failed=true;}assert(failed);assert.strictEqual(JSON.stringify(state),copy);
 fs.writeFileSync(path.join(out,'download-report.json'),JSON.stringify({version:metadata.appVersion,urls:calls,cacheCount:Object.keys(state).length,cachedLanguage:client.info().cachedLanguage,offlineReuse:true,failedReplacementPreservedCache:true},null,2)+'\n');
 console.log('PASS real GitHub client: verified DE/EN manifest+packet HTTPS downloads, one cache, offline reload and failed replacement preserve EN');
})().catch(e=>{console.error(e);process.exitCode=1;});
