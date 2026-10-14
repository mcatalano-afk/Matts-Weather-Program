"""Assemble 'Elmer Weather.app' and zip it for download. Icon is an original drawing (CC0)."""
import io, os, shutil, struct, zipfile, stat
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist")
APP = os.path.join(OUT, "Elmer Weather.app")
C = os.path.join(APP, "Contents")

# ---------- Icon: glossy sun behind a cloud, Aqua-era free-form style ----------
def radial(size, center, radius, inner, outer):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    cx, cy = center
    for y in range(size):
        for x in range(size):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** .5 / radius
            t = min(1, d)
            px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(4))
    return img

def vertical(size, top, bottom):
    img = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        t = y / (size - 1)
        d.line([(0, y), (size, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4)))
    return img

def icon(S=1024):
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    u = S / 1024

    # Sun with rays
    sun_c, sun_r = (600 * u, 380 * u), 230 * u
    rays = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    import math
    for i in range(12):
        a = i * math.pi / 6
        x1, y1 = sun_c[0] + math.cos(a) * (sun_r + 30 * u), sun_c[1] + math.sin(a) * (sun_r + 30 * u)
        x2, y2 = sun_c[0] + math.cos(a) * (sun_r + 120 * u), sun_c[1] + math.sin(a) * (sun_r + 120 * u)
        rd.line([(x1, y1), (x2, y2)], fill=(255, 176, 20, 255), width=int(44 * u))
        for (x, y) in ((x1, y1), (x2, y2)):
            rd.ellipse([x - 22 * u, y - 22 * u, x + 22 * u, y + 22 * u], fill=(255, 176, 20, 255))
    base = Image.alpha_composite(base, rays)

    sun_fill = radial(S, (sun_c[0] - 70 * u, sun_c[1] - 90 * u), sun_r * 1.6, (255, 250, 200, 255), (240, 128, 0, 255))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([sun_c[0] - sun_r, sun_c[1] - sun_r, sun_c[0] + sun_r, sun_c[1] + sun_r], fill=255)
    base.paste(sun_fill, (0, 0), m)
    gm = Image.new("L", (S, S), 0)
    ImageDraw.Draw(gm).ellipse([sun_c[0] - 150 * u, sun_c[1] - 205 * u, sun_c[0] + 110 * u, sun_c[1] - 40 * u], fill=150)
    gloss = Image.new("RGBA", (S, S), (255, 255, 255, 0)); gloss.putalpha(gm.filter(ImageFilter.GaussianBlur(10 * u)))
    base = Image.alpha_composite(base, gloss)

    # Cloud: union of circles plus a rounded base
    cm = Image.new("L", (S, S), 0)
    cd = ImageDraw.Draw(cm)
    for (x, y, r) in ((300, 600, 170), (500, 520, 220), (720, 620, 160), (180, 700, 120)):
        cd.ellipse([(x - r) * u, (y - r) * u, (x + r) * u, (y + r) * u], fill=255)
    cd.rounded_rectangle([90 * u, 600 * u, 880 * u, 830 * u], radius=int(115 * u), fill=255)

    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow.putalpha(cm.point(lambda v: v * 0.45))
    shadow = shadow.transform((S, S), Image.AFFINE, (1, 0, 0, 0, 1, -28 * u)).filter(ImageFilter.GaussianBlur(26 * u))
    base = Image.alpha_composite(base, shadow)

    edge = Image.new("RGBA", (S, S), (110, 128, 150, 255))
    base.paste(edge, (0, 0), cm)
    inner = cm.filter(ImageFilter.MinFilter(int(9 * u) | 1))
    base.paste(vertical(S, (255, 255, 255, 255), (196, 210, 228, 255)), (0, 0), inner)
    hm = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hm).ellipse([340 * u, 335 * u, 650 * u, 460 * u], fill=230)
    hl = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    hl.putalpha(Image.composite(hm.filter(ImageFilter.GaussianBlur(14 * u)), Image.new("L", (S, S), 0), inner))
    base = Image.alpha_composite(base, hl)
    # leave the standard margin around Mac icons
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    small = base.resize((int(S * .86), int(S * .86)), Image.LANCZOS)
    out.alpha_composite(small, (int(S * .06), int(S * .05)))
    return out

big = icon(1024)
big.save(os.path.join(HERE, "icon-preview.png"))

def png(img, size):
    b = io.BytesIO()
    img.resize((size, size), Image.LANCZOS).save(b, "PNG")
    return b.getvalue()

chunks = [(b"ic11", 32), (b"ic12", 64), (b"ic07", 128), (b"ic13", 256), (b"ic08", 256),
          (b"ic14", 512), (b"ic09", 512), (b"ic10", 1024)]
body = b"".join(t + struct.pack(">I", 8 + len(d)) + d for t, d in ((t, png(big, s)) for t, s in chunks))
icns = b"icns" + struct.pack(">I", 8 + len(body)) + body

# ---------- Bundle ----------
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(C, "MacOS"))
os.makedirs(os.path.join(C, "Resources"))
open(os.path.join(C, "Resources", "AppIcon.icns"), "wb").write(icns)
shutil.copy(os.path.join(HERE, "..", "index.html"), os.path.join(C, "Resources", "index.html"))
shutil.copy(os.path.join(HERE, "main.jxa"), os.path.join(C, "Resources", "main.jxa"))

launcher = """#!/bin/bash
# Starts the Elmer Weather window (JavaScript for Automation, built into macOS)
RES="$(cd "$(dirname "$0")/../Resources" && pwd)"
exec /usr/bin/osascript -l JavaScript "$RES/main.jxa" "$RES"
"""
exe = os.path.join(C, "MacOS", "Elmer Weather")
open(exe, "w").write(launcher)
os.chmod(exe, 0o755)

open(os.path.join(C, "Info.plist"), "w").write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Elmer Weather</string>
  <key>CFBundleDisplayName</key><string>Elmer Weather</string>
  <key>CFBundleIdentifier</key><string>local.elmerweather.station</string>
  <key>CFBundleExecutable</key><string>Elmer Weather</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>10.13</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSHumanReadableCopyright</key><string>Weather data and radar: U.S. National Weather Service (public domain). Icons: original, CC0.</string>
</dict>
</plist>
""")
open(os.path.join(C, "PkgInfo"), "w").write("APPL????")

# ---------- Zip, keeping Unix permissions so the app can launch ----------
import time
NOW = time.localtime()[:6]
zpath = os.path.join(OUT, "Elmer Weather.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(APP):
        rel = os.path.relpath(root, OUT)
        zi = zipfile.ZipInfo(rel + "/", NOW); zi.create_system = 3
        zi.external_attr = (stat.S_IFDIR | 0o755) << 16 | 0x10
        z.writestr(zi, "")
        for f in sorted(files):
            p = os.path.join(root, f)
            zi = zipfile.ZipInfo(os.path.join(rel, f), NOW); zi.create_system = 3
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (stat.S_IFREG | (os.stat(p).st_mode & 0o777)) << 16
            z.writestr(zi, open(p, "rb").read())
print("built", zpath, os.path.getsize(zpath))
