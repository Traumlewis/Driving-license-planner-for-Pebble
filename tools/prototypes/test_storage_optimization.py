#!/usr/bin/env python3
"""Run the unchanged application store logic against a desktop compact-record adapter."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
PROJECTS=('time2','core2duo','time-pebble2','round2','timeround')

def run_project(project, temporary, compact, sanitize=False):
    folder=ROOT/'projects'/project
    original=(folder/'src/c/store.c').read_text()
    if compact:
        original=original.replace('#include "store.h"','#include "store.h"\n#include "compact_storage.h"\n#define persist_write_data compact_write_data\n#define persist_read_data compact_read_data\n#define persist_get_size compact_get_size',1)
    store=temporary/'store.c';store.write_text(original)
    test=(folder/'tests/store_test.c').read_text()
    test=test.replace('static int fail_key=-1;', '''static int fail_key=-1;
static int mutation_limit=-1,mutations,external_bytes;
static int used(void){int n=0;for(int i=0;i<300;i++)n+=sizes[i];return n;}
static bool reject_mutation(void){int step=mutations++;return mutation_limit>=0&&step>=mutation_limit;}
''')
    test=test.replace('if(key==fail_key)return -1;', 'if(key==fail_key||reject_mutation()||used()-sizes[key]+(int)n+external_bytes>4096)return -1;')
    test=test.replace('int persist_delete(int key){','int persist_delete(int key){if(key==fail_key||reject_mutation())return -1;')
    test=test.replace('int main(void){','int original_regression_suite(void){',1)
    # Falling off main is legal, but the renamed test function needs an explicit return.
    end=test.rfind('}');test=test[:end]+'return 0;\n'+test[end:]
    test+='\n'+(ROOT/'tools/prototypes/storage_optimization_harness.c').read_text()
    source=temporary/'test.c';source.write_text(test)
    binary=temporary/'test'
    command=['gcc','-std=c11','-Wall','-Wextra','-Werror','-I',str(folder/'tests/fake'),'-I',str(folder/'src/c'),'-I',str(ROOT/'tools/prototypes'),str(source),str(store)]
    if sanitize:command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g']
    if compact:command+=['-DCOMPACT',str(ROOT/'tools/prototypes/compact_storage.c')]
    compiled=subprocess.run(command+['-o',str(binary)],capture_output=True,text=True)
    if compiled.returncode:raise RuntimeError(compiled.stderr)
    result=subprocess.run([str(binary)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return json.loads(next(line[7:] for line in result.stdout.splitlines() if line.startswith('RESULT:')))

def main(output,sanitize=False):
    paths=[ROOT/'release.json',ROOT/'VERSION',ROOT/'Packs/App/Languages/index.json']+list((ROOT/'projects').glob('*/src/c/*.c'))
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    results=[]
    with tempfile.TemporaryDirectory(prefix='compact-storage-') as temp:
        for project in PROJECTS:
            old=run_project(project,Path(temp),False,sanitize)
            compact=run_project(project,Path(temp),True,sanitize)
            rows=[]
            for baseline,packed in zip(old['scenarios'],compact['scenarios']):
                rows.append(dict(mode=baseline['mode'],before=baseline['appBytes'],after=packed['appBytes'],savedBytes=baseline['appBytes']-packed['appBytes'],bookingPeakBefore=baseline['bookingPeakBytes'],bookingPeakAfter=packed['bookingPeakBytes'],remainingForLanguageAndManifest=packed['languageBudgetWithManifest']))
            results.append(dict(project=project,scenarios=rows,originalStoreTestsPassed=True,bookingFailureBoundaries=compact['bookingFailureBoundaries'],migrationFailureBoundaries=compact['migrationFailureBoundaries'],randomRoundtrips=12000))
            print(project,[(r['before'],r['after'],r['savedBytes']) for r in rows],flush=True)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in before.items())
    report=dict(productionVersion='3.8.49',productionUnchanged=True,nativeWatchBuild=False,sanitizers=sanitize,scope='desktop prototype using original store.c and its regression suite',quotaBytes=4096,scenarios=['empty','three appointments, one class','24 phone appointments, all class progress','24 appointments with all optional timestamps, all class progress'],projects=results)
    previous=ROOT/'docs/self-contained-language-pack-results.json'
    if previous.exists():
        remaining=results[0]['scenarios'][-1]['remainingForLanguageAndManifest']
        report['languageComparisons']=[]
        for row in json.loads(previous.read_text())['results']:
            minimum=min(row['deflateRawByWindow'].values())+32+len(row['name'].encode())+16
            report['languageComparisons'].append(dict(locale=row['locale'],selfContainedBpeStored=row['storedBytes'],bestDeflateStoredMinimum=minimum,remainingAfterWorstCaseAppAndJournal=remaining,bpeFitsWorstCase=row['storedBytes']<=remaining,deflateFitsWorstCase=minimum<=remaining,deflateNote='Size estimate only, including a minimal header/name/manifest; no native decoder or RAM feasibility claim.'))
    report['currentLanguageReserveInFaultTests']=2567
    report['journalBytes']=20
    report['testNotes']=['Original store.c business logic and original regression tests are compiled for each project; only persistence transport is adapted in a temporary file.','The fake SDK enforces 4096 bytes of persisted values including the selected language reserve.','Fault tests interrupt writes/deletes at every mutation boundary and reboot, including migration with a pending booking journal.','When --sanitize is used: AddressSanitizer and UndefinedBehaviorSanitizer; disable LeakSanitizer under a traced executor.','Desktop prototype only; no change to app sources, live catalogue, runtime data or PBW.','Measurements concern persisted value sizes, not a native RAM/build footprint or flash-controller overhead.']
    output.mkdir(parents=True,exist_ok=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--sanitize',action='store_true');args=parser.parse_args();main(args.output,args.sanitize)
