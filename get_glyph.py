from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import svgwrite
import os

# === 1. 設定路徑 ===
font_path = "YourFont.ttf"  # 換成你的字體檔案路徑
output_dir = "export_svg"
os.makedirs(output_dir, exist_ok=True)

# === 2. 讀取字體 ===
font = TTFont(font_path)
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()  # 取得 Unicode → glyph 名稱對應表

# === 3. 逐一匯出字形 ===
for codepoint, glyph_name in cmap.items():
    if glyph_name not in glyph_set:
        continue

    glyph = glyph_set[glyph_name]
    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_data = pen.getCommands()

    # 如果是空白字形就跳過
    bounds = glyph.boundingBox()
    if bounds is None:
        continue

    xmin, ymin, xmax, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin

    # Unicode 字元和代碼
    char = chr(codepoint)
    safe_char = char if char.isprintable() and char not in ['/', '\\', ':', '*', '?', '"', '<', '>', '|'] else ''
    filename = f"U+{codepoint:04X}_{safe_char}.svg"

    # === 4. 建立 SVG ===
    dwg = svgwrite.Drawing(
        filename=os.path.join(output_dir, filename),
        size=(f"{width}px", f"{height}px"),
        viewBox=f"{xmin} {ymin} {width} {height}"
    )

    # 翻轉 Y 軸（SVG 的座標系是反的）
    group = dwg.g(transform=f"scale(1,-1) translate(0,{-ymax - ymin})")
    group.add(dwg.path(d=path_data, fill="black"))
    dwg.add(group)
    dwg.save()

print(f"✅ 匯出完成，共 {len(cmap)} 個可用字元。輸出資料夾：{output_dir}")
