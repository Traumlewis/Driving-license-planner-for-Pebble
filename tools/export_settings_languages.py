"""Export editable phone settings translations and a live language catalogue."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def export():
    translations=json.loads((ROOT/'tools/settings-translations.json').read_text());base=ROOT/'Packs/Germany/Languages';base.mkdir(parents=True,exist_ok=True)
    index_path=base/'index.json';index=json.loads(index_path.read_text()) if index_path.exists() else dict(schemaVersion=1,trainingCountry='DE',versions={})
    existing={d['locale']:d for d in index.get('settings',{}).get('languages',[])}
    schema=dict(keys=list(translations['en']['strings']),kinds=7,grounds=12)
    for locale,name,watch in [('de','Deutsch',0),('en','English',1)]:
        p=translations[locale];assert set(p['strings'])==set(schema['keys']) and p['locale']==locale
        raw=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode();folder=base/locale;folder.mkdir(exist_ok=True);(folder/'settings.json').write_bytes(raw)
        existing[locale]=dict(locale=locale,name=name,file=locale+'/settings.json',sha256=hashlib.sha256(raw).hexdigest(),watchLanguage=watch)
    index['settings']=dict(format='settings-v1',languages=list(existing.values()));index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    for folder in (ROOT/'projects').iterdir():
        if (folder/'src/pkjs').exists():(folder/'src/pkjs/settings-schema.js').write_text('module.exports = '+json.dumps(schema,separators=(',',':'))+';\n')
    return index_path
if __name__=='__main__':print(export())
