#!/usr/bin/env python3
"""Pack and register an additional watch translation using the existing frozen codec."""
import argparse,json
from pathlib import Path
from watch_packets import register
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);a=p.parse_args();packet=register(json.loads(a.source.read_text()));print(packet['locale'],packet['size'],'bytes; registered without compiling a PBW')
