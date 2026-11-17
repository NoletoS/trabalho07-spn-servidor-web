"""Gera os gráficos e a tabela LaTeX a partir do CSV avaliado no notebook."""
from pathlib import Path
from csv import DictReader
from math import ceil, log10
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
article = root.parent / "overleaf"
destination = article if (article / "main.tex").is_file() else root / "artefatos"
figures = destination / "figuras"
figures.mkdir(parents=True, exist_ok=True)
with (root / "resultados.csv").open(encoding="utf-8", newline="") as file:
    data = list(DictReader(file))

INK = "#182b3a"
BLUE = "#12658b"
TEAL = "#137966"
GRAY = "#cbd7df"
SLATE = "#3c5161"
FONT_DIR = Path("C:/Windows/Fonts")


def font(size, bold=False):
    try:
        return ImageFont.truetype(str(FONT_DIR / ("arialbd.ttf" if bold else "arial.ttf")), size)
    except OSError:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)


def num(value, digits=2):
    return f"{float(value):.{digits}f}".replace(".", ",")


def plot(group, rows, label_key, x_title, metrics):
    w, h = 1270, 725
    image = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(image)
    for panel, (key, name, unit, digits, color) in enumerate(metrics):
        left, right = 105 + 638 * panel, 602 + 638 * panel
        top, bottom = 123, 538
        values = [float(row[key]) for row in rows]
        raw_step = max(values) / 4
        order = 10 ** int(log10(raw_step)) if raw_step >= 1 else 10 ** (int(log10(raw_step)) - 1)
        step = next(f * order for f in (1, 2, 2.5, 5, 10) if f * order >= raw_step)
        ymax = ceil(max(values) / step) * step
        if ymax == max(values):
            ymax += step
        draw.line((left - 2, 56, left + 34, 56), fill=color, width=6)
        draw.ellipse((left + 10, 49, left + 24, 63), fill=color)
        draw.text((left + 46, 56), f"{name} ({unit})", fill=INK, font=font(31, True), anchor="lm")
        for i in range(round(ymax/step)+1):
            v = i * step
            y = bottom - v / ymax * (bottom - top)
            draw.line((left, y, right, y), fill=GRAY, width=2)
            draw.text((left - 12, y), f"{v:g}".replace(".", ","), fill=SLATE, font=font(26), anchor="rm")
        draw.line((left, top, left, bottom, right, bottom), fill=INK, width=3)
        points = []
        axis = list(range(len(rows))) if label_key == "id" else [int(row[label_key]) for row in rows]
        spacing = (right - left - 84) / (axis[-1] - axis[0])
        for i, (row, value) in enumerate(zip(rows, values)):
            x = left + 42 + (axis[i] - axis[0]) * spacing
            y = bottom - value / ymax * (bottom - top)
            points.append((x, y))
            draw.text((x, bottom + 25), row[label_key], fill=INK, font=font(27), anchor="mt")
        draw.line(points, fill=color, width=6)
        for (x, y), value in zip(points, values):
            draw.ellipse((x-8, y-8, x+8, y+8), fill=color)
            draw.text((x, y-13), num(value, 3 if key == "DP_pct" and value < 0.01 else digits), fill=INK, font=font(24, True), anchor="mb")
        draw.text(((right + left)/2, 638), x_title, fill=INK, font=font(30), anchor="mt")
    image.save(figures / f"{group.lower()}.png")


tp = ("TP", "Vazão", "req/s", 1, BLUE)
mrt = ("MRT_ms", "Resposta", "ms", 1, BLUE)
dp = ("DP_pct", "Descarte", "%", 2, TEAL)
u = ("U_pct", "Utilização", "%", 1, TEAL)
for group, key, title, metrics in (
    ("E1", "lambda", "Chegadas λ (req/s)", (tp, dp)),
    ("E2", "c", "Processadores c (unid.)", (mrt, u)),
    ("E3", "B", "Vagas de espera B (req.)", (mrt, dp)),
    ("E4", "id", "Cenário combinado", (mrt, dp)),
):
    plot(group, [row for row in data if row["id"].startswith(group)], key, title, metrics)

with (destination / "tabela.tex").open("w", encoding="utf-8") as file:
    for row in data:
        fields = [row[key] for key in ("id", "lambda", "c", "B", "K")]
        fields.extend(num(row[key], 3 if key == "DP_pct" else 2)
                      for key in ("TP", "MRT_ms", "MQT_ms", "U_pct", "DP_pct"))
        file.write(" & ".join(fields) + r" \\" + "\n")


