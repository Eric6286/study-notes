#!/usr/bin/env python3
r"""verify_solutions.py — the deterministic gate that decides who gets the 已核验 badge.

WHY THIS EXISTS
---------------
build_and_check.py is STATIC: it can confirm a verification artifact *exists*, but not that the
artifact is *true* — a confidently-wrong model can fabricate a passing-looking note. This script
crosses that trust boundary: it EXECUTES the verification (real sympy in a subprocess) and lets
the machine, not the model, decide pass/fail. The badge becomes earned, not asserted.

HOW A SOLUTION DECLARES ITS CHECK
---------------------------------
Inside the solution's card, add an (invisible) block that recomputes the answer from the GIVEN
data and asserts it equals the printed answer:

    <script type="text/x-verify" data-for="例1 滑块加速度">
    import sympy as sp
    t, w, lam, l = sp.symbols('t omega lambda l', positive=True)
    x = l*((1 - lam**2/4) - sp.cos(w*t) - (lam/4)*sp.cos(2*w*t))   # GIVEN x(t), copied from the题面
    check_derivative(given=x, wrt=t, order=2,
                     claimed=-l*lam*w**2*(sp.cos(w*t) + lam*sp.cos(2*w*t)),  # the answer the card prints
                     name="例1 a_x")
    </script>

(check_derivative / check_integral / check_equal / check_consistent / check_limit / check_numeric
come from verify_helpers and are pre-imported into every block.)

THE GATE
--------
  * Every block is run for real. A failing assertion (recomputed != claimed) FAILs the build and
    prints the real recomputed value next to the claimed one.
  * A solution may carry 已核验 ONLY if it has a PASSING block. More 已核验 badges than passing
    blocks => FAIL (an unearned badge).
  * Anything that can't be machine-verified must be tagged 未自动核验 (abstention) — never 已核验.

SECURITY: this executes Python embedded in the HTML. Only run it on notes you generated yourself.
Each block runs in a subprocess with a timeout.

Usage:
    python verify_solutions.py notes.html
    python verify_solutions.py notes.html --timeout 20
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

BLOCK_RE = re.compile(
    r'<script[^>]*\btype\s*=\s*["\']text/x-verify["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)
DATA_FOR_RE = re.compile(r'data-for\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
# Count only the badge ELEMENT (a `<span class="badge …">已核验/未自动核验</span>` pill), not every
# mention of the characters in prose, a comment, or a legend. Kept byte-identical to
# build_and_check.VERIFY_BADGE_RE so the static gate and this executable gate agree on the count —
# otherwise a file can pass one and fail the other on the same badges.
BADGE_RE = re.compile(
    r'<span\b[^>]*\bclass\s*=\s*["\'][^"\']*\bbadge\b[^"\']*["\'][^>]*>\s*已核验')
ABSTAIN_RE = re.compile(
    r'<span\b[^>]*\bclass\s*=\s*["\'][^"\']*\bbadge\b[^"\']*["\'][^>]*>\s*未自动核验')

# Header injected before every block so the check_* helpers and sympy are available, and a block
# that ran no checks is rejected at the end.
RUNNER_HEADER = (
    "import sys\n"
    f"sys.path.insert(0, {HERE!r})\n"
    "import sympy as sp\n"
    "import verify_helpers as _vh\n"
    "from verify_helpers import (check_derivative, check_integral, check_equal,\n"
    "    check_consistent, check_limit, check_numeric)\n"
)
RUNNER_FOOTER = "\n_vh.require_checks()\n"


def extract_blocks(html):
    """Return list of (label, code) for every x-verify block."""
    blocks = []
    for m in BLOCK_RE.finditer(html):
        head = html[m.start():m.start() + (m.group(1).find("\n") if "\n" in m.group(1) else 0) + 200]
        label_m = DATA_FOR_RE.search(html[m.start():m.start() + 300])
        label = label_m.group(1) if label_m else f"block@line{html[:m.start()].count(chr(10))+1}"
        blocks.append((label, m.group(1)))
    return blocks


def run_block(code, timeout=20):
    """Execute one block in a subprocess. Return (ok, output)."""
    src = RUNNER_HEADER + "\n" + code + RUNNER_FOOTER
    fd, path = tempfile.mkstemp(suffix=".py", prefix="xverify_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(src)
        try:
            # Force UTF-8 for the child's stdout AND decode it as UTF-8, so a check name with a
            # non-ASCII math symbol (²  √  π  ω …) can't crash the run on a non-UTF-8 locale
            # (e.g. Windows GBK): without this the child raises UnicodeEncodeError on print and the
            # block looks "failed". errors='replace' is a final guard so a stray byte never throws.
            env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
            r = subprocess.run([sys.executable, path], capture_output=True, text=True,
                               timeout=timeout, encoding="utf-8", errors="replace", env=env)
        except subprocess.TimeoutExpired:
            return False, f"TIMEOUT after {timeout}s"
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out.strip()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def run_checks(html, timeout=20):
    blocks = extract_blocks(html)
    badges = len(BADGE_RE.findall(html))
    abstain = len(ABSTAIN_RE.findall(html))

    print(f"=== verify_solutions: {len(blocks)} x-verify block(s), "
          f"{badges} '已核验' badge(s), {abstain} '未自动核验' tag(s) ===")

    passed = failed = 0
    fail_details = []
    for label, code in blocks:
        ok, out = run_block(code, timeout)
        if ok:
            passed += 1
            print(f"[PASS] {label}")
        else:
            failed += 1
            print(f"[FAIL] {label}")
            fail_details.append((label, out))

    problems = 0

    if failed:
        problems += 1
        print(f"\n[FAIL] {failed} verification(s) did NOT hold — the recomputed value disagrees")
        print("       with the claimed answer. This is a wrong answer, not a passing one:")
        for label, out in fail_details:
            print(f"\n  ── {label} ──")
            for line in out.splitlines():
                print(f"    {line}")
        print("\n   Fix the solution (or tag it 未自动核验) — do NOT ship it as 已核验.")

    if badges > passed:
        problems += 1
        print(f"\n[FAIL] {badges} '已核验' badge(s) but only {passed} PASSING check(s).")
        print("       Every 已核验 must be backed by a passing x-verify block. Either add the")
        print("       missing executable check, or downgrade the badge to 未自动核验 (abstain).")

    print()
    if problems:
        print(f"RESULT: {problems} problem(s). The 已核验 badge is NOT justified as-is.")
        return False
    if badges == 0 and passed == 0:
        print("RESULT: no executable checks and no 已核验 badges — nothing to verify (ok).")
        return True
    print(f"RESULT: all {passed} executable check(s) passed; every 已核验 badge is earned.")
    return True


def main():
    p = argparse.ArgumentParser(description="Run embedded x-verify blocks and gate the 已核验 badge.")
    p.add_argument("html")
    p.add_argument("--timeout", type=int, default=20, help="per-block timeout in seconds")
    args = p.parse_args()
    try:
        with open(args.html, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        sys.exit(f"file not found: {args.html}")
    ok = run_checks(html, args.timeout)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
