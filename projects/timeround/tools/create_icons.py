"""Native-size solid pixel symbols matching the DEV front-facing car."""
from pathlib import Path
from PIL import Image,ImageDraw
folder=Path(__file__).resolve().parents[1]/'resources/images'
folder.mkdir(parents=True,exist_ok=True)
WHITE=(255,255,255,255);CLEAR=(0,0,0,0);NAVY=(0,0,85,255)
for cls in range(16):
 im=Image.new('RGBA',(36,34));d=ImageDraw.Draw(im)
 def box(b,fill=WHITE):d.rectangle(b,fill=fill)
 def poly(p,fill=WHITE):d.polygon(p,fill=fill)
 def disc(x,y,r,fill=WHITE):d.ellipse((x-r,y-r,x+r,y+r),fill=fill)
 def wheel(x,y,r):
  disc(x,y,r);disc(x,y,max(1,r-2),CLEAR)
 trailer=cls in (5,7,9,11,13)
 if cls<=3:
  # Scooter AM; light, medium and large motorbike silhouettes.
  wheel(7,25,5);wheel(29,25,5)
  if cls==0:
   poly([(7,22),(11,17),(17,18),(18,23),(24,23),(27,12),(30,12),(28,25),(16,26)])
   box((10,14,18,16));box((26,8,31,10));box((27,10,29,15))
  else:
   poly([(7,22),(13,16),(24,16),(29,22),(26,24),(20,20),(12,24)])
   poly([(13,16),(18,11),(23,13),(25,18),(17,19)])
   box((9,12,16,14));poly([(25,9),(29,10),(30,16),(27,17)])
   if cls==1:box((18,12,21,14),CLEAR)
   if cls==2:poly([(16,11),(21,10),(24,14),(19,14)])
   if cls==3:poly([(20,8),(28,9),(32,17),(24,17)])
 elif cls==4:
  poly([(4,24),(4,15),(8,12),(11,6),(25,6),(28,12),(32,15),(32,25),(4,25)])
  poly([(12,8),(24,8),(27,14),(9,14)],CLEAR)
  box((8,18,12,20),CLEAR);box((24,18,28,20),CLEAR)
  box((7,24,12,29));box((24,24,29,29))
 elif cls==5:
  # Side view, nose points left; caravan is behind the rear bumper.
  poly([(1,23),(1,18),(5,16),(8,11),(16,11),(20,16),(22,17),(22,24),(1,24)])
  poly([(9,13),(15,13),(18,17),(6,17)],CLEAR)
  box((2,19,4,21),CLEAR);wheel(6,26,3);wheel(18,26,3)
  box((22,22,25,23));box((25,13,34,23));box((27,15,30,18),CLEAR);wheel(30,26,3)
 elif cls in (6,7,8,9):
  small=cls in (6,7);top=11 if small else 6
  # Cab at the left/front, load body behind it.
  poly([(1,24),(1,17),(5,12),(10,12),(10,24)])
  poly([(3,17),(6,14),(8,14),(8,18),(3,18)],CLEAR)
  end=22 if trailer else 34;box((12,top,end,24));wheel(6,26,4);wheel(end-5,26,4)
  if not small:box((15,top+3,end-3,top+4),CLEAR)
  if trailer:box((22,22,25,23));box((25,top+2,34,23));wheel(30,26,3)
 elif cls in (10,11,12,13):
  small=cls in (10,11);top=12 if small else 7;end=23 if trailer else 34
  poly([(2,top+4),(5,top),(end,top),(end,24),(2,24)])
  box((4,top+4,7,top+10),CLEAR) # front windscreen/driver area at left
  for x in range(10,end-3,6):box((x,top+3,x+3,top+8),CLEAR)
  wheel(7,26,4);wheel(end-4,26,4)
  if not small:box((5,top-3,end-2,top-2))
  if trailer:box((23,22,26,23));box((26,16,34,23));wheel(30,26,3)
 else:
  wheel(10,25,7);wheel(29,27,4);box((6,8,18,20));box((9,11,15,17),CLEAR)
  box((4,5,20,7));box((19,16,29,22));box((25,10,27,17));box((6,19,21,22))
  if cls==15:box((1,30,5,31));box((20,13,30,15));poly([(28,16),(32,19),(32,23),(29,23)])
 im.save(folder/f'class-{cls}.png')
# Crisp 25px launcher badge, navy tile with a traffic light and cyan frame.
im=Image.new('RGBA',(25,25));d=ImageDraw.Draw(im)
d.rounded_rectangle((0,0,24,24),radius=5,fill=NAVY)
d.rounded_rectangle((7,2,17,21),radius=3,fill=(0,255,255,255))
d.rounded_rectangle((9,3,15,20),radius=2,fill=NAVY)
for y,color in [(6,(255,85,85,255)),(12,(255,255,0,255)),(18,(85,255,85,255))]:
 d.ellipse((10,y-2,14,y+2),fill=color)
d.rectangle((11,21,13,23),fill=WHITE)
im.save(folder/'app-icon.png')
print('Created traffic-light launcher and 16 solid vehicle symbols')
