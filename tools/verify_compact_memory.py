"""Run native language/memory verification without changing menus or user progress."""
from pathlib import Path
exec(compile(Path('tools/native_generic_memory.py').read_text(),'native_language_memory.py','exec'),globals())
