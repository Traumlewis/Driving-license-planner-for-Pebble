import code,sys
from pathlib import Path
# Reuse the installed CLI's supported connection and emulator management.
script=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).with_name('emulator_protocol.py')).read_text()
def run(local=None,**kwargs):
 exec(compile(script,'emulator_protocol.py','exec'),local)
code.interact=run
sys.argv=['pebble','repl','--emulator','emery']
from pebble_tool import run_tool
run_tool()
