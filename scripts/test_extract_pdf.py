#!/usr/bin/env python3
"""Unit tests for extract_pdf.py — the pure detection/parse logic, with NO OCR or PDF.

OCR output and page rasters are synthesized so the locate/autocrop geometry (page-range
parsing, caption matching, column detection, figure-top delimiter) is tested deterministically
and offline. The OCR engine itself is exercised by running the tool on a real PDF, not here.

    python test_extract_pdf.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import extract_pdf as E  # noqa: E402


def box(x0, y0, x1, y1):
    """An OCR quad in RapidOCR's [[x,y]*4] order."""
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


_TESTS = []
def test(fn):
    _TESTS.append(fn)
    return fn


@test
def parse_pages():
    assert list(E._parse_pages(None, 5)) == [0, 1, 2, 3, 4]
    assert list(E._parse_pages("3", 10)) == [2]
    assert list(E._parse_pages("3-5", 10)) == [2, 3, 4]
    assert list(E._parse_pages("3-100", 10)) == [2, 3, 4, 5, 6, 7, 8, 9]  # hi clamps to page count


@test
def norm():
    assert E._norm("图 4.4 劳埃德镜") == "图4.4劳埃德镜"


@test
def find_caption_prefers_the_caption_line():
    res = [
        (box(100, 900, 600, 930), "(3)洛埃镜(Lloydmirror),如图4.4(a)所示", 0.9),  # body reference
        (box(120, 1000, 300, 1030), "图4.4 劳埃德镜", 0.9),                         # the actual caption
    ]
    found = E._find_caption(res, "图4.4")
    assert found is not None
    assert found[1].strip() == "图4.4 劳埃德镜"   # the short 图-prefixed line wins, not the body ref


@test
def find_caption_missing_returns_none():
    assert E._find_caption([(box(0, 0, 10, 10), "无关文字", 0.9)], "图9.9") is None


@test
def figure_captions_lists_only_caption_like():
    res = [
        (box(0, 0, 10, 10), "图4.4 劳埃德镜", 0.9),
        (box(0, 0, 10, 10), "正文无图注一句话", 0.9),
        (box(0, 0, 10, 10), "图 4.5 对切透镜", 0.9),
    ]
    caps = E._figure_captions(res)
    assert any("4.4" in c for c in caps) and any("4.5" in c for c in caps)
    assert "正文无图注一句话" not in caps


@test
def column_of_separates_two_columns():
    # white page, ink in two column bands with a blank center gutter + side margins
    g = np.full((400, 1000), 255.0)
    g[50:350, 100:400] = 0     # left column
    g[50:350, 600:900] = 0     # right column
    left = E._column_of(g, 250, 0, 400)    # x in left column
    right = E._column_of(g, 700, 0, 400)   # x in right column
    assert left[0] <= 100 and 400 <= left[1] <= 600     # right edge falls in the gutter
    assert 400 <= right[0] <= 600 and right[1] >= 900


@test
def figure_top_uses_wide_textline_not_narrow_label():
    cap = box(150, 600, 350, 630)
    res = [
        (box(110, 180, 390, 220), "一行很宽的正文文字占满整列做上界", 0.9),  # wide -> delimiter
        (box(200, 400, 230, 430), "S", 0.9),                            # narrow in-figure label -> ignored
        (cap, "图1.1 示意", 0.9),
    ]
    top = E._figure_top(res, 100, 400, cap)
    assert 220 <= top <= 240   # just below the wide text line, NOT down at the 'S' label (y=430)


if __name__ == "__main__":
    failed = 0
    for fn in _TESTS:
        try:
            fn()
            print(f"[PASS] {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"[FAIL] {fn.__name__}: {e}")
    print(f"\n{len(_TESTS) - failed}/{len(_TESTS)} passed")
    sys.exit(1 if failed else 0)
