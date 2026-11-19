from PIL import Image, ImageDraw
from graficos import figures, font, INK, BLUE, TEAL
from math import atan2, cos, sin

im = Image.new("RGB", (1200, 540), "white")
d = ImageDraw.Draw(im)

def arrow(*points):
    d.line(points, fill=INK, width=4, joint="curve")
    (x1,y1),(x,y) = points[-2:]
    a = atan2(y-y1,x-x1)
    d.polygon([(x,y),(x-15*cos(a-.48),y-15*sin(a-.48)),(x-15*cos(a+.48),y-15*sin(a+.48))], fill=INK)

y = 230
for x0, x1 in ((75,157),(243,318),(334,416),(504,576),(592,676),(764,894)):
    arrow((x0,y),(x1,y))
arrow((912,y),(1080,y))
arrow((200,273),(200,393))
arrow((527,110),(326,110),(326,185))
arrow((904,187),(904,53),(570,53),(570,65))
arrow((586,405),(584,275))
arrow((904,274),(904,449),(630,449))

for x, cy, label, pos in [
    (200,y,"Entrada","below"),(460,y,"Fila","below"),(720,y,"Ocupados","below"),
    (570,110,"Vagas","right"),(586,449,"Livres","below")]:
    d.ellipse((x-43,cy-43,x+43,cy+43), fill="white", outline=BLUE, width=6)
    if pos == "right":
        d.text((x+56,cy),label,font=font(30,True),fill=INK,anchor="lm")
    else:
        d.text((x-63 if label == "Entrada" else x,cy+47 if label == "Entrada" else cy+53),label,font=font(30,True),fill=INK,anchor="mt")
for x, top, bottom, label, tx, ty in [
    (65,186,274,"Chegar",65,311),(326,186,274,"Admitir",326,311),
    (584,186,274,"Iniciar",637,314),(904,186,274,"Concluir",966,311),
    (200,393,414,"Descartar",200,454)]:
    if label in {"Chegar","Concluir"}:
        d.rectangle((x-10,top,x+10,bottom), outline=BLUE, width=4, fill="white")
    elif label == "Descartar":
        d.rectangle((x-40,top,x+40,bottom), fill=TEAL)
    else:
        d.rectangle((x-8,top,x+8,bottom), fill=TEAL)
    d.text((tx,ty),label,font=font(29,True),fill=INK,anchor="mt")
d.text((247,373),"se Vagas = 0", font=font(25), fill=INK)
d.text((1102,228),"Saída",font=font(30,True),fill=INK,anchor="lm")
base = im
im = Image.new("RGB", (1380, 540), "white")
im.paste(base, (180, 0))
d = ImageDraw.Draw(im)
arrow((113, 230), (233, 230))
arrow((245, 184), (245, 133), (70, 133), (70, 185))
d.ellipse((27, 187, 113, 273), fill="white", outline=BLUE, width=6)
d.ellipse((63, 223, 77, 237), fill=INK)
d.text((70, 283), "Fonte", font=font(30, True), fill=INK, anchor="mt")
im.save(figures / "rede.png")


