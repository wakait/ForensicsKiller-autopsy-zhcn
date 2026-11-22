# -*- coding: utf-8 -*-
"""生成品牌位图：logo.png / favicon.png / og.png

几何与 docs/assets/logo.svg 保持一致（紫色盾牌 + 内部三角形）。
不依赖 cairosvg：用贝塞尔采样出盾牌轮廓，再用渐变遮罩合成，4 倍超采样抗锯齿。
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "docs" / "assets"
SS = 4  # 超采样倍数


def bez(p0, p1, p2, p3, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def shield_polygon(scale=512):
    """对应 SVG: M256 36 L440 96 V264 C440 360 356 432 256 476 C156 432 72 360 72 264 V96 Z"""
    pts = [(256, 36), (440, 96), (440, 264)]
    pts += bez((440, 264), (440, 360), (356, 432), (256, 476))[1:]
    pts += bez((256, 476), (156, 432), (72, 360), (72, 264))[1:]
    pts += [(72, 96)]
    k = scale / 512.0
    return [(x * k, y * k) for x, y in pts]


def triangle_polygon(scale=512):
    """对应 SVG: M256 158 L362 342 Q366 350 357 350 H155 Q146 350 150 342 Z（这里做成圆角近似）"""
    k = scale / 512.0
    raw = [(256, 158), (362, 342), (357, 350), (155, 350), (150, 342)]
    return [(x * k, y * k) for x, y in raw]


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.point((0, y), fill=c)
    return img.resize((w, h), Image.BICUBIC)


def render_logo(px=512):
    size = px * SS
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # 盾牌：渐变填充
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).polygon(shield_polygon(size), fill=255)
    grad = vertical_gradient((size, size), (0x9B, 0x6B, 0xFF), (0x4C, 0x1D, 0x95)).convert("RGBA")
    base.paste(grad, (0, 0), mask)

    # 内侧描边（按中心内缩，避免压在轮廓上）
    d = ImageDraw.Draw(base)
    poly = shield_polygon(size)
    cx = sum(x for x, _ in poly) / len(poly)
    cy = sum(y for _, y in poly) / len(poly)
    k = 0.90
    inner = [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in poly]
    d.line(inner + [inner[0]], fill=(255, 255, 255, 70), width=int(6 * SS), joint="curve")

    # 三角形
    tri = triangle_polygon(size)
    tri_mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(tri_mask).polygon(tri, fill=255)
    tri_grad = vertical_gradient((size, size), (255, 255, 255), (0xDD, 0xD6, 0xFE)).convert("RGBA")
    base.paste(tri_grad, (0, 0), tri_mask)

    # 三角投影 + 内描边
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x, y + 8 * SS) for x, y in tri], fill=(59, 7, 100, 70))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(6 * SS))
    base = Image.alpha_composite(base, sh)
    d = ImageDraw.Draw(base)
    d.line(tri + [tri[0]], fill=(0x6D, 0x28, 0xD9, 110), width=int(6 * SS), joint="curve")

    return base.resize((px, px), Image.LANCZOS)


def render_og(logo: Image.Image, out: Path):
    W, H = 1200, 630
    bg = vertical_gradient((W, H), (0x14, 0x0A, 0x24), (0x2A, 0x10, 0x4F)).convert("RGBA")
    d = ImageDraw.Draw(bg)
    # 柔和光斑
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-160, -200, 620, 520], fill=(124, 58, 237, 70))
    gd.ellipse([760, 300, 1400, 900], fill=(76, 29, 149, 90))
    bg = Image.alpha_composite(bg, glow)

    lg = logo.resize((248, 248), Image.LANCZOS)
    bg.alpha_composite(lg, (96, 190))

    def font(size, bold=False):
        p = r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc"
        return ImageFont.truetype(p, size)

    d = ImageDraw.Draw(bg)
    d.text((392, 214), "Autopsy", font=font(78, True), fill=(255, 255, 255))
    d.text((392, 308), "简体中文语言包", font=font(58, True), fill=(196, 181, 253))
    d.text((396, 400), "v2026.12-FINAL-R3 · 适配 Autopsy 4.23.1", font=font(30), fill=(167, 139, 250))
    d.text((396, 452), "180 个资源包 · 约 8900 条中文文案 · 一键安装", font=font(28), fill=(150, 130, 200))
    bg.convert("RGB").save(out, quality=92)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    logo = render_logo(512)
    logo.save(ASSETS / "logo.png")
    logo.resize((192, 192), Image.LANCZOS).save(ASSETS / "logo-192.png")
    logo.resize((64, 64), Image.LANCZOS).save(ASSETS / "favicon.png")
    logo.resize((32, 32), Image.LANCZOS).save(ASSETS / "favicon-32.png")
    render_og(logo, ASSETS / "og.png")
    for f in ("logo.png", "logo-192.png", "favicon.png", "favicon-32.png", "og.png"):
        print("%-16s %8.1f KB" % (f, (ASSETS / f).stat().st_size / 1024))


if __name__ == "__main__":
    main()
