"""Generate opaque native 1-bit class symbols for Flint from the color asset alpha masks."""
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[1];folder=root/'resources/images/bw';folder.mkdir(exist_ok=True)
for i in range(16):
 image=Image.open(root/f'resources/images/class-{i}.png').convert('RGBA');mask=image.getchannel('A').point(lambda p:255 if p>=128 else 0);out=Image.new('1',image.size,0);out.paste(1,mask=mask);out.save(folder/f'class-{i}.png')
