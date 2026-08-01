#!/usr/bin/env python3
"""Genera el icono de la app (icon.png de 1024) con tema video + descarga."""
from PIL import Image, ImageDraw

S = 1024
SS = 4               # supersampling para bordes suaves
W = S * SS
img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# --- fondo: cuadrado redondeado con degradado rojo vertical ---
top = (255, 66, 66)      # rojo claro
bot = (198, 0, 0)        # rojo YouTube oscuro
radius = int(W * 0.225)
# degradado dibujando líneas horizontales, recortado al rounded-rect via máscara
grad = Image.new("RGBA", (W, W), (0, 0, 0, 0))
gd = ImageDraw.Draw(grad)
for y in range(W):
    t = y / W
    r = int(top[0] + (bot[0] - top[0]) * t)
    g = int(top[1] + (bot[1] - top[1]) * t)
    b = int(top[2] + (bot[2] - top[2]) * t)
    gd.line([(0, y), (W, y)], fill=(r, g, b, 255))
mask = Image.new("L", (W, W), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, W - 1], radius=radius, fill=255)
img.paste(grad, (0, 0), mask)
d = ImageDraw.Draw(img)

white = (255, 255, 255, 255)
cx = W // 2

# --- triángulo "play" (video) en la parte superior-central ---
tri_h = int(W * 0.30)
tri_w = int(W * 0.26)
tri_cy = int(W * 0.40)
p1 = (cx - tri_w // 2, tri_cy - tri_h // 2)
p2 = (cx - tri_w // 2, tri_cy + tri_h // 2)
p3 = (cx + tri_w // 2, tri_cy)
# esquinas suavizadas dibujando el polígono con contorno redondeado
d.polygon([p1, p2, p3], fill=white)
for (a, b) in [(p1, p2), (p2, p3), (p3, p1)]:
    d.line([a, b], fill=white, width=int(W * 0.045), joint="curve")
r_round = int(W * 0.022)
for p in (p1, p2, p3):
    d.ellipse([p[0] - r_round, p[1] - r_round, p[0] + r_round, p[1] + r_round], fill=white)

# --- flecha de descarga en la parte inferior ---
shaft_w = int(W * 0.072)
arr_cx = cx
shaft_top = int(W * 0.595)
shaft_bot = int(W * 0.690)
d.rounded_rectangle(
    [arr_cx - shaft_w // 2, shaft_top, arr_cx + shaft_w // 2, shaft_bot],
    radius=shaft_w // 2, fill=white,
)
# punta de la flecha (por encima de la bandeja, sin sobresalir)
head_w = int(W * 0.185)
head_top = shaft_bot - int(W * 0.005)
head_tip = int(W * 0.795)
d.polygon(
    [(arr_cx - head_w // 2, head_top), (arr_cx + head_w // 2, head_top),
     (arr_cx, head_tip)],
    fill=white,
)
# bandeja / línea base
tray_w = int(W * 0.30)
tray_y = int(W * 0.820)
tray_h = int(W * 0.052)
d.rounded_rectangle(
    [arr_cx - tray_w // 2, tray_y, arr_cx + tray_w // 2, tray_y + tray_h],
    radius=tray_h // 2, fill=white,
)

# downscale con antialiasing
icon = img.resize((S, S), Image.LANCZOS)
icon.save("icon.png")
print("icon.png generado")
