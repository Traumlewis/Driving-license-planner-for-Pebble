from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
repo=root.parents[1]
translations=json.loads((repo/'tools/settings-translations.json').read_text())
page=root/'phone/config.html';html=page.read_text()
fallback=translations['en'];fallback_js='var strings='+json.dumps(fallback['strings'],ensure_ascii=False)+';\nvar kinds='+json.dumps(fallback['kinds'],ensure_ascii=False)+';\nvar grounds='+json.dumps(fallback['grounds'],ensure_ascii=False)+';'
def replace_block(text,label,content):
 return re.sub(r'/\*__'+label+r'_START__\*/.*?/\*__'+label+r'_END__\*/',lambda m:'/*__'+label+'_START__*/\n'+content+'\n/*__'+label+'_END__*/',text,flags=re.S)
html=replace_block(html,'SETTINGS_FALLBACK',fallback_js)
sha=(root/'src/pkjs/sha256.js').read_text();client=(root/'src/pkjs/settings-language.js').read_text();schema=(root/'src/pkjs/settings-schema.js').read_text()
inline='(function(){var hash=(function(){var module={exports:{}};'+sha+';return module.exports;})();var schema=(function(){var module={exports:{}};'+schema+';return module.exports;})();var module={exports:{}},exports=module.exports,require=function(name){return name==="./sha256"?hash:schema;};'+client+';window.SettingsLanguages=module.exports;})();'
html=replace_block(html,'SETTINGS_CLIENT',inline);page.write_text(html)
(root/'src/pkjs/config-html.js').write_text('module.exports = '+json.dumps(html,ensure_ascii=False)+';\n')
