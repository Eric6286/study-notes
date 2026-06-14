#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_features.py — score a study-notes HTML on the 10 auto-checks the skill
guarantees. Five are rendering-correctness checks (reused from build_and_check via
import) and five are structure-completeness checks. Used by evals/benchmark.md to
compare a real skill output against a no-skill baseline, reproducibly.

Usage:  python evals/check_features.py <file.html> [<file.html> ...]
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import build_and_check as b  # noqa: E402


def score(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    checks = {
        # rendering correctness (silent failures the browser never reports)
        "katex_template":   bool(re.search(r"renderMathInElement", html)),
        "no_naked_unicode": not b.check_unicode_in_math(html),
        "div_balanced":     (lambda o, c, _: o == c)(*b.check_div_balance(html)),
        "dollar_balanced":  b.check_dollar_balance(html) == 0,
        "forbidden_clean":  not b.check_forbidden(html),
        # structure completeness (the standardized exam-ready layout)
        "hierarchical_toc": bool(re.search(r'class="toc"', html)) and bool(re.search(r"toc-l1", html)),
        "floating_nav":     bool(re.search(r'id="nav-panel"', html)),
        "collapsibles":     len(re.findall(r"<details", html)) >= 1,
        "color_sections":   len(re.findall(r"sec-(purple|teal|coral|amber|blue|green|red)", html)) >= 1,
        "callouts":         len(re.findall(r"class=\"callout", html)) >= 1,
    }
    passed = sum(checks.values())
    return passed, checks


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check_features.py <file.html> [...]")
    for p in sys.argv[1:]:
        passed, checks = score(p)
        failed = [k for k, v in checks.items() if not v]
        print(f"{passed:2d}/10  {os.path.basename(p)}"
              + (f"   FAIL: {', '.join(failed)}" if failed else "   (all pass)"))


if __name__ == "__main__":
    main()
