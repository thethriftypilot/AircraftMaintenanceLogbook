"""Generate a code-native aviation icon; no external artwork dependencies."""
from pathlib import Path
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]
image=Image.new('RGBA',(256,256),(13,27,46,255));draw=ImageDraw.Draw(image)
draw.rounded_rectangle((15,15,241,241),radius=48,outline='#5ec5d1',width=7)
draw.ellipse((50,50,206,206),outline='#34516c',width=3)
draw.line((33,128,223,128),fill='#34516c',width=3)
draw.polygon([(128,40),(142,108),(212,153),(211,167),(142,143),(140,192),(163,208),(162,218),(128,208),(94,218),(93,208),(116,192),(114,143),(45,167),(44,153),(114,108)],fill='#dceef5')
image.save(root/'resources'/'app.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
image.save(root/'resources'/'app.png')
