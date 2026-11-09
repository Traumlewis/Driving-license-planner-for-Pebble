"""Publish generic watch packets while retaining archived versioned LP3 packets."""
from pathlib import Path
import json
from watch_packets import ROOT,register

def export():
    for path in sorted((ROOT/'Packs/App/Languages').glob('*/watch-source.json')):register(json.loads(path.read_text()))
    return ROOT/'Packs/App/Languages'
if __name__=='__main__':print(export())
