#!/usr/bin/env python3
"""
Prépare les photos d'œuvres pour le site.

Pour chaque image d'un dossier source :
  - applique l'orientation EXIF puis supprime toutes les métadonnées (GPS compris),
  - convertit en sRGB,
  - écrit un grand format (côté long 2000 px) dans assets/img/works/full/,
  - écrit une vignette (largeur 900 px) dans assets/img/works/thumbs/,
  - ajoute en option une signature discrète dont la teinte s'adapte au fond,
  - imprime les lignes YAML à coller dans _galleries/<rubrique>.md.

Usage (depuis la racine du dépôt) :
    pip install Pillow
    python tools/prepare_images.py sources/d-apres-nature
    python tools/prepare_images.py sources/etudes --watermark "© M.-L. Pouliquen"

Le dossier sources/ est ignoré par git : vos originaux ne sont pas publiés.
"""
import argparse
import io
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat, ImageCms

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "assets/img/works/full"
THUMBS = ROOT / "assets/img/works/thumbs"
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic"}


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "oeuvre"


def to_srgb(im: Image.Image) -> Image.Image:
    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            dst = ImageCms.createProfile("sRGB")
            im = ImageCms.profileToProfile(im, src, dst, outputMode="RGB")
        except Exception:
            pass
    if im.mode != "RGB":
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if im.mode in ("RGBA", "LA"):
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
    return im


def watermark(im: Image.Image, text: str) -> Image.Image:
    im = im.copy()
    w, h = im.size
    size = max(12, int(min(w, h) * 0.022))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(im)
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    margin = int(size * 1.2)
    box = (w - tw - margin, h - th - margin, w - margin, h - margin)
    # teinte adaptative : clair sur fond sombre, sombre sur fond clair
    lum = ImageStat.Stat(im.crop(box).convert("L")).mean[0]
    fill = (255, 255, 255) if lum < 128 else (30, 30, 30)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(box[:2], text, font=font, fill=fill + (110,))
    return Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="dossier contenant les photos originales")
    ap.add_argument("--full", type=int, default=2000, help="côté long du grand format (px)")
    ap.add_argument("--thumb", type=int, default=900, help="largeur des vignettes (px)")
    ap.add_argument("--quality", type=int, default=84)
    ap.add_argument("--watermark", default="", help="texte de signature (grand format uniquement)")
    args = ap.parse_args()

    if args.source.suffix.lower() in EXTS:
        files = [args.source]
    else:
        files = sorted(p for p in args.source.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        sys.exit(f"Aucune image trouvée dans {args.source}")

    FULL.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)

    print("\n# À coller sous `works:` dans le front matter de la rubrique\n")
    for src in files:
        try:
            im = Image.open(src)
        except Exception as e:  # HEIC sans pillow-heif, fichier corrompu…
            print(f"# ignoré : {src.name} ({e})", file=sys.stderr)
            continue
        im = to_srgb(ImageOps.exif_transpose(im))
        name = slugify(src.stem) + ".jpg"

        full = im.copy()
        full.thumbnail((args.full, args.full), Image.LANCZOS)
        if args.watermark:
            full = watermark(full, args.watermark)
        full.save(FULL / name, "JPEG", quality=args.quality, optimize=True, progressive=True)

        thumb = im.copy()
        thumb.thumbnail((args.thumb, args.thumb * 4), Image.LANCZOS)
        thumb.save(THUMBS / name, "JPEG", quality=args.quality - 4, optimize=True, progressive=True)

        print(f"  - file: {name}\n    title: \n    year: \n    medium: \n"
              f"    width: {thumb.width}\n    height: {thumb.height}")
    print()


if __name__ == "__main__":
    main()
