import code,sys
from pathlib import Path
platform=sys.argv[1];script=Path(sys.argv[2]).read_text()
def run(local=None,**kwargs):
 local['test_platform']=platform
 exec(compile(script,'device_protocol_test.py','exec'),local)
code.interact=run
sys.argv=['pebble','repl','--emulator',platform]
from pebble_tool import run_tool
run_tool()
