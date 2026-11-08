'use strict';
const assert=require('assert'),fs=require('fs');
const timeline=require('../src/pkjs/timeline');
const data={},storage={getItem:k=>data[k]||null,setItem:(k,v)=>data[k]=String(v)};
const inserted=[],deleted=[];let failInsert=false,failDelete=false;
const pebble={insertTimelinePin:pin=>{if(failInsert)throw Error('offline');inserted.push(JSON.parse(JSON.stringify(pin)));},deleteTimelinePin:id=>{if(failDelete)throw Error('offline');deleted.push(id);}};
const practice=[41,1900000000,4,3,1,1440,30,255,20],theory=[42,1900003600,4,5,2,60,15,1,0];
const state={version:2,language:0,entries:[practice,theory]};
let sync=timeline.create(pebble,storage);assert(sync.state().enabled);assert.strictEqual(inserted.length,0);
assert.strictEqual(sync.sync(state).status,'submitted');assert.strictEqual(inserted.length,2);
assert.strictEqual(inserted[0].duration,65);assert.strictEqual(inserted[1].duration,180);
assert(inserted[0].layout.title.includes('Nachtfahrt'));assert(inserted[1].layout.body.includes('Thema 2'));
assert.strictEqual(inserted[0].time,new Date(practice[1]*1000).toISOString());assert(!inserted[0].reminders); // watch alarms already handle reminders
sync.sync(state);assert.strictEqual(inserted.length,2); // no duplicates or needless updates
practice[1]+=86400;practice[8]=25;sync.sync(state);assert.strictEqual(inserted.length,3);assert.strictEqual(inserted[2].id,'fahrschul.lesson.41');assert.strictEqual(inserted[2].duration,70);
state.language=1;sync.sync(state);assert.strictEqual(inserted.length,5);assert(inserted[3].layout.title.includes('Night driving'));
state.entries=[theory];sync.sync(state);assert.deepStrictEqual(deleted,['fahrschul.lesson.41']);
sync.setEnabled(false);assert.strictEqual(sync.state().status,'off');assert.deepStrictEqual(deleted,['fahrschul.lesson.41','fahrschul.lesson.42']);
sync=timeline.create(pebble,storage);assert(!sync.state().enabled);sync.sync(state);assert.strictEqual(inserted.length,5);
sync.setEnabled(true);assert.strictEqual(inserted.length,6);assert.strictEqual(inserted[5].id,'fahrschul.lesson.42.g1');
// Fresh startups reassert current pins once, and never sync old snapshot data before the watch replies.
sync=timeline.create(pebble,storage);assert.strictEqual(inserted.length,6);sync.sync(state);assert.strictEqual(inserted.length,7);
failInsert=true;theory[4]=3;assert.strictEqual(sync.sync(state).status,'retry');failInsert=false;sync.sync(state);assert.strictEqual(inserted[7].duration,270);
failDelete=true;sync.setEnabled(false);assert.strictEqual(sync.state().status,'retry');failDelete=false;
sync=timeline.create(pebble,storage);assert.strictEqual(sync.state().status,'off');assert.strictEqual(Object.keys(JSON.parse(data['fahrschul.v2.timeline.pins'])).length,0);
const unsupported=timeline.create({},storage);assert.strictEqual(unsupported.sync(state).status,'unsupported');assert(!unsupported.state().supported);
assert.strictEqual(timeline.pinForEntry([0,1900000000,4,3,1,0,0,255,0],0),null);
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(timeline.pinForEntry([900000001,Math.floor(Date.now()/1000)+3600,4,3,1,60,15,255,5],0),null,2));
console.log('PASS local Timeline pins: stable IDs, duration, DE/EN, reschedule/update/delete, toggle persistence, restart reconciliation and retry after failures');
