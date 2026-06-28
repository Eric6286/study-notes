#!/usr/bin/env python3
"""extract_pdf.py — PDF helpers for the study-notes skill.

Five subcommands:

  text     Extract text per page (for textbook/worksheet reading).
  images   Render each page to a PNG (for scanned PDFs or layout viewing).
  locate   OCR-search a SCANNED PDF for a keyword -> the page number(s) it's on
           (scanned books have no text layer, so 'text' returns nothing and you
           can't grep them; flipping pages by eye is unreliable — let OCR find it).
  autocrop Auto-detect and crop a figure by its 图X.Y caption — the bbox is DETECTED
           (column gutters + the figure's own caption + tighten-to-ink), never hand-typed.
           This is the fix for "I eyeballed the --bbox and clipped half the figure".
  crop     Crop a HAND-SPECIFIED rectangular region of one page (fallback for when
           autocrop can't find a caption, or the source isn't a captioned textbook figure).

All paths are arguments — nothing is hard-coded.

Requires PyMuPDF:  pip install pymupdf --break-system-packages -q
'locate' and 'autocrop' additionally need numpy + RapidOCR (CPU, models bundled in the wheel):
                   pip install rapidocr-onnxruntime numpy --break-system-packages -q
"""
import argparse
import os
import re
import sys


def _open(path):
    try:
        import fitz  # PyMuPDF
    except ImportError:
        sys.exit("PyMuPDF not installed. Run: pip install pymupdf --break-system-packages -q")
    if not os.path.exists(path):
        sys.exit(f"File not found: {path}")
    return fitz.open(path)


def cmd_text(args):
    doc = _open(args.pdf)
    chunks, nonempty = [], 0
    for i, page in enumerate(doc):
        txt = page.get_text()
        if txt.strip():
            nonempty += 1
        chunks.append(f"--- PAGE {i + 1} ---\n{txt}")
    out = "\n".join(chunks)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        total_chars = len(out)
        print(f"Wrote {args.out}  ({len(doc)} pages, {nonempty} with text, {total_chars} chars)")
        if nonempty == 0:
            print("WARNING: no extractable text — this is likely a scanned PDF. Use 'locate' to "
                  "find a problem by keyword and 'images'/'autocrop' to read/cut the pages.")
    else:
        print(out)


def cmd_images(args):
    doc = _open(args.pdf)
    os.makedirs(args.out, exist_ok=True)
    n = 0
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=args.dpi)
        dest = os.path.join(args.out, f"page_{i + 1:03d}.png")
        pix.save(dest)
        n += 1
    print(f"Saved {n} page image(s) to {args.out}/ at {args.dpi} dpi")


# ---------------------------------------------------------------------------
# OCR-assisted helpers (scanned textbooks)
# ---------------------------------------------------------------------------
# A scanned PDF is just images — no text layer — so both "which page is this
# problem on?" and "where is the figure on the page?" have to be read off the
# rendered raster. We do that with OCR, but keep the RESULT deterministic: the
# crop bbox is computed from column gutters + the figure's own caption, never
# typed by hand. Hand-typed bboxes are exactly what clip half a figure.

_INK = 150  # a pixel darker than this counts as ink


def _lazy_np():
    try:
        import numpy as np
        return np
    except ImportError:
        sys.exit("numpy needed. Run: pip install numpy --break-system-packages -q")


def _lazy_ocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        sys.exit("RapidOCR needed (a scanned PDF has no text layer). "
                 "Run: pip install rapidocr-onnxruntime --break-system-packages -q")
    return RapidOCR()


def _page_rgb(page, dpi, np):
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    return (img[:, :, :3] if pix.n == 4 else img).copy()


def _parse_pages(spec, n):
    if not spec:
        return range(n)
    s = spec.strip()
    if "-" in s:
        a, b = s.split("-", 1)
        return range(max(1, int(a)) - 1, min(n, int(b)))
    i = int(s)
    return range(i - 1, i)


def cmd_locate(args):
    np = _lazy_np()
    ocr = _lazy_ocr()
    doc = _open(args.pdf)
    pages = _parse_pages(args.pages, len(doc))
    kws = args.keyword
    found = 0
    for i in pages:
        res, _ = ocr(_page_rgb(doc[i], args.dpi, np))
        lines = [ln[1] for ln in (res or [])]
        text = "".join(lines)
        present = [k for k in kws if k in text]
        if present:
            snippet = [ln for ln in lines if any(k in ln for k in kws)][:2]
            print(f"PAGE {i + 1}: {present}  | {' / '.join(snippet)}")
            found += 1
    print(f"--- {found} page(s) matched {kws} in pages {args.pages or 'all'} ---")
    if not found:
        sys.exit(1)


def _norm(t):
    return t.replace(" ", "")


def _figure_captions(res):
    out = []
    for box, txt, _sc in res or []:
        if re.search(r"图\s*\d+\s*[.\-]\s*\d+", txt):
            out.append(txt.strip())
    return out


def _find_caption(res, target):
    m = re.search(r"(\d+)\s*[.\-]\s*(\d+)", target)
    num = f"{m.group(1)}.{m.group(2)}" if m else _norm(target)
    cands = []
    for box, txt, _sc in res or []:
        t = _norm(txt).replace("．", ".")
        if num in t or _norm(target) in t:
            cands.append(((0 if t.startswith(("图", "圖")) else 1, len(t)), box, txt))
    cands.sort(key=lambda c: c[0])
    return (cands[0][1], cands[0][2]) if cands else None


def _column_of(gray, cx, y0, y1):
    """The text column containing x=cx, found as the span between the nearest
    sustained vertical whitespace gaps (page margins and the center gutter)."""
    W = gray.shape[1]
    band = (gray[y0:y1, :] < _INK).sum(0).astype(float)
    thr = max(2.0, band.max() * 0.03)
    low = band <= thr
    GUT = 26
    gutters, i = [], 0
    while i < W:
        if low[i]:
            j = i
            while j < W and low[j]:
                j += 1
            if j - i >= GUT:
                gutters.append((i, j))
            i = j
        else:
            i += 1
    left, right, c = 0, W, int(cx)
    for a, b in gutters:
        if b <= c and b > left:
            left = b
        if a >= c and a < right:
            right = a
    return left, right


def _figure_top(res, x0, x1, cap_box):
    """Top of the figure = bottom edge of the nearest WIDE text line above the caption.
    A delimiter must overlap the column horizontally (so a full-width page header bounds
    both columns); narrow in-figure labels (S, N, (a)…) fail the width test and are ignored."""
    cap_top = min(p[1] for p in cap_box)
    colw = max(1, x1 - x0)
    top = 0
    for box, _txt, _sc in res or []:
        bl, br = min(p[0] for p in box), max(p[0] for p in box)
        if br <= x0 or bl >= x1:          # must overlap the column horizontally
            continue
        if max(p[1] for p in box) <= cap_top - 4 and (br - bl) >= 0.32 * colw:
            top = max(top, max(p[1] for p in box) + 4)
    return int(top)


def cmd_autocrop(args):
    import fitz
    np = _lazy_np()
    ocr = _lazy_ocr()
    doc = _open(args.pdf)
    idx = args.page - 1
    if idx < 0 or idx >= len(doc):
        sys.exit(f"--page {args.page} out of range (PDF has {len(doc)} pages)")
    page = doc[idx]
    img = _page_rgb(page, args.dpi, np)
    gray = img.mean(2)
    res, _ = ocr(img)

    if args.list or not args.caption:
        caps = _figure_captions(res)
        print(f"Figures detected on page {args.page}: {caps or '(none — OCR saw no 图X.Y caption)'}")
        if not args.caption:
            print("Pass --caption '图X.Y' (or a caption keyword) to crop one.")
            return

    found = _find_caption(res, args.caption)
    if not found:
        sys.exit(f"caption {args.caption!r} not found on page {args.page}. "
                 f"Detected: {_figure_captions(res)}")
    if not args.out:
        sys.exit("pass -o OUT.png to write the crop")
    cap_box, cap_txt = found
    cx = sum(p[0] for p in cap_box) / 4
    cap_bot = int(max(p[1] for p in cap_box))
    cap_top = int(min(p[1] for p in cap_box))
    x0, x1 = _column_of(gray, cx, max(0, cap_top - 700), cap_bot)
    top = _figure_top(res, x0, x1, cap_box)
    sub = gray[top:cap_bot + 8, x0:x1] < _INK
    rows = np.where(sub.any(1))[0]
    cols = np.where(sub.any(0))[0]
    if len(rows) == 0 or len(cols) == 0:
        sys.exit("no ink found in the detected figure region")
    m = args.margin
    # Clamp to the IMAGE bounds, not the column — so the margin may reach into the
    # (blank) gutter and never clips a label sitting right at the column edge (e.g. '2a').
    H, W = gray.shape
    yy0 = max(0, top + int(rows.min()) - m)
    yy1 = min(H, top + int(rows.max()) + m)
    xx0 = max(0, x0 + int(cols.min()) - m)
    xx1 = min(W, x0 + int(cols.max()) + m)
    # Re-render exactly that region via a PDF-point clip so the saved crop is a crisp
    # native render (not a resample of the detection raster).
    rect = page.rect
    f = 72.0 / args.dpi
    clip = fitz.Rect(rect.x0 + xx0 * f, rect.y0 + yy0 * f, rect.x0 + xx1 * f, rect.y0 + yy1 * f)
    out_pix = page.get_pixmap(dpi=args.out_dpi, clip=clip)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out_pix.save(args.out)
    print(f"autocropped '{cap_txt.strip()}' (page {args.page}) -> {args.out}  "
          f"[{out_pix.width}x{out_pix.height}px @ {args.out_dpi}dpi]  (bbox auto-detected, not hand-typed)")
    print("Next: python3 scripts/embed_images.py datauri " + args.out)


def _parse_bbox(s):
    try:
        parts = [float(x) for x in s.split(",")]
    except ValueError:
        sys.exit("--bbox must be four comma-separated numbers, e.g. 0.1,0.2,0.9,0.55")
    if len(parts) != 4:
        sys.exit("--bbox needs exactly 4 numbers: x0,y0,x1,y1")
    return parts


def cmd_crop(args):
    import fitz
    doc = _open(args.pdf)
    idx = args.page - 1
    if idx < 0 or idx >= len(doc):
        sys.exit(f"--page {args.page} out of range (PDF has {len(doc)} pages)")
    page = doc[idx]
    x0, y0, x1, y1 = _parse_bbox(args.bbox)
    rect = page.rect
    fractional = all(0.0 <= v <= 1.0 for v in (x0, y0, x1, y1))
    if fractional:
        clip = fitz.Rect(rect.x0 + x0 * rect.width,
                         rect.y0 + y0 * rect.height,
                         rect.x0 + x1 * rect.width,
                         rect.y0 + y1 * rect.height)
        mode = "fractional"
    else:
        clip = fitz.Rect(x0, y0, x1, y1)
        mode = "absolute(pt)"
    if clip.is_empty or clip.width <= 0 or clip.height <= 0:
        sys.exit(f"Computed clip is empty: {clip}")
    pix = page.get_pixmap(dpi=args.dpi, clip=clip)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    pix.save(args.out)
    print(f"Cropped page {args.page} ({mode} bbox) -> {args.out}  "
          f"[{pix.width}x{pix.height}px @ {args.dpi}dpi]")
    print("Next: python3 scripts/embed_images.py datauri " + args.out)


def main():
    p = argparse.ArgumentParser(description="PDF helpers for the study-notes skill.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("text", help="extract text per page")
    pt.add_argument("pdf")
    pt.add_argument("-o", "--out", help="output .txt (prints to stdout if omitted)")
    pt.set_defaults(func=cmd_text)

    pi = sub.add_parser("images", help="render each page to PNG")
    pi.add_argument("pdf")
    pi.add_argument("-o", "--out", default="pages", help="output directory (default: pages)")
    pi.add_argument("--dpi", type=int, default=150)
    pi.set_defaults(func=cmd_images)

    pl = sub.add_parser("locate", help="OCR-search a scanned PDF for a keyword -> page number(s)")
    pl.add_argument("pdf")
    pl.add_argument("keyword", nargs="+", help="one or more keywords (a page matches on ANY)")
    pl.add_argument("--pages", help="page range like 3-20 (default: all)")
    pl.add_argument("--dpi", type=int, default=200)
    pl.set_defaults(func=cmd_locate)

    pa = sub.add_parser("autocrop",
                        help="auto-detect & crop a figure by its 图X.Y caption (no eyeballed bbox)")
    pa.add_argument("pdf")
    pa.add_argument("--page", type=int, required=True, help="1-based page number")
    pa.add_argument("--caption", help="caption to anchor on, e.g. '图4.4' or a caption keyword")
    pa.add_argument("--list", action="store_true",
                    help="just list the 图X.Y captions detected on the page, then exit")
    pa.add_argument("-o", "--out", help="output .png")
    pa.add_argument("--dpi", type=int, default=300, help="detection/OCR dpi")
    pa.add_argument("--out-dpi", dest="out_dpi", type=int, default=300, help="final crop dpi")
    pa.add_argument("--margin", type=int, default=18, help="px margin around the tightened figure")
    pa.set_defaults(func=cmd_autocrop)

    pc = sub.add_parser("crop", help="crop a HAND-SPECIFIED region (fallback for non-captioned figures)")
    pc.add_argument("pdf")
    pc.add_argument("--page", type=int, required=True, help="1-based page number")
    pc.add_argument("--bbox", required=True,
                    help="x0,y0,x1,y1 — fractional (0..1, from top-left) or absolute points")
    pc.add_argument("-o", "--out", required=True, help="output .png")
    pc.add_argument("--dpi", type=int, default=200)
    pc.set_defaults(func=cmd_crop)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
