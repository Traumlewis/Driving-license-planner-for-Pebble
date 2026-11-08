from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
(root/'src/pkjs/config-html.js').write_text('module.exports = '+json.dumps((root/'phone/config.html').read_text(),ensure_ascii=False)+';\n')
