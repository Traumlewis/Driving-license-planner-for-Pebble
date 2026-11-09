"""Publish watch packets for the currently supported codec only."""
from pathlib import Path
import json,re,shutil
from watch_packets import ROOT,register,compatibility

def export():
    for path in sorted((ROOT/'Packs/App/Languages').glob('*/watch-source.json')):register(json.loads(path.read_text()))
    base=ROOT/'Packs/App/Languages';tag=compatibility()['tag'];index_path=base/'index.json'
    # Prune only after every source has encoded successfully. Keep custom
    # registrations in the current variant, including data-only additions.
    index=json.loads(index_path.read_text());index['watchPacks']={tag:index['watchPacks'][tag]}
    index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    for folder in (base/'watch').iterdir():
        if folder.is_dir() and folder.name!=tag and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{8}',folder.name):shutil.rmtree(folder)
    return base
if __name__=='__main__':print(export())
