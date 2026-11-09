'use strict';
// SHA-256 of UTF-8 text. No platform crypto or external dependency is required.
var K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
function r(x,n){return x>>>n|x<<32-n;}
module.exports=function(text){
 var bytes=[],i,c,d;
 for(i=0;i<text.length;i++){
  c=text.charCodeAt(i);
  if(c>=0xd800&&c<=0xdbff){d=text.charCodeAt(++i);if(!(d>=0xdc00&&d<=0xdfff))throw Error('Invalid UTF-8 input');c=0x10000+((c-0xd800)<<10)+d-0xdc00;}
  else if(c>=0xdc00&&c<=0xdfff)throw Error('Invalid UTF-8 input');
  if(c<128)bytes.push(c);else if(c<2048)bytes.push(192|c>>6,128|c&63);else if(c<65536)bytes.push(224|c>>12,128|c>>6&63,128|c&63);else bytes.push(240|c>>18,128|c>>12&63,128|c>>6&63,128|c&63);
 }
 var bits=bytes.length*8;bytes.push(128);while(bytes.length%64!==56)bytes.push(0);
 for(i=0;i<4;i++)bytes.push(0);for(i=3;i>=0;i--)bytes.push(bits>>>i*8&255);
 var h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],w=[];
 for(i=0;i<bytes.length;i+=64){
  var t;for(t=0;t<16;t++)w[t]=bytes[i+t*4]<<24|bytes[i+t*4+1]<<16|bytes[i+t*4+2]<<8|bytes[i+t*4+3];
  for(t=16;t<64;t++){var x=w[t-15],y=w[t-2];w[t]=((r(x,7)^r(x,18)^x>>>3)+w[t-16]+(r(y,17)^r(y,19)^y>>>10)+w[t-7])|0;}
  var a=h[0],b=h[1],cc=h[2],dd=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
  for(t=0;t<64;t++){var p=(hh+(r(e,6)^r(e,11)^r(e,25))+(e&f^~e&g)+K[t]+w[t])|0,q=((r(a,2)^r(a,13)^r(a,22))+(a&b^a&cc^b&cc))|0;hh=g;g=f;f=e;e=dd+p|0;dd=cc;cc=b;b=a;a=p+q|0;}
  var v=[a,b,cc,dd,e,f,g,hh];for(t=0;t<8;t++)h[t]=h[t]+v[t]|0;
 }
 return h.map(function(x){return ('00000000'+(x>>>0).toString(16)).slice(-8);}).join('');
};
