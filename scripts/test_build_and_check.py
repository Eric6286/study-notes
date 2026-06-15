#!/usr/bin/env python3
r"""Self-contained regression tests for build_and_check.py.

Locks in the macro-aware forbidden-command fix: a \command that the file registers
as a KaTeX macro must NOT be flagged, while the same command used WITHOUT a macro
definition (older templates) must still be caught. No external corpus needed.

Run:  python test_build_and_check.py
"""
import build_and_check as b

# Mimic a real template macro-registration line: in the HTML bytes, '\celsius' has
# TWO backslashes (a JS string escaping one LaTeX backslash). \\\\ here -> '\\' there.
DEFINES = (
    "<script>renderMathInElement(document.body,{macros:{"
    "'\\\\celsius':'{{{}^\\\\circ\\\\text{C}}}','\\\\unit':'{\\\\,\\\\text}',"
    "'\\\\degree':'{{}^\\\\circ}'}});</script>\n"
    "<div class=\"fbox\">$T=20\\celsius$ and $v=3\\unit{m/s}$</div>"
)
USES_UNDEFINED = "<div class=\"fbox\">$T=20\\celsius$</div>"
SI_ALWAYS_BAD = "<script>macros:{'\\\\degree':'{{}^\\\\circ}'}</script><div>$\\SI{1}{m}$</div>"

# verified-badge gate: a 已核验 badge must be backed by a <!-- verify: --> artifact.
BADGE_OK = (
    "<span class=\"badge\">已核验 ✓</span>\n"
    "<!-- verify: sympy diff(x,t,2)=l*w^2*(cos(wt)+lam*cos(2wt)), matches main solution -->"
)
BADGE_BARE = "<span class=\"badge\">已核验 ✓</span> with no artifact recorded"
NO_BADGE = "<div class=\"answer-box\"><p>$x=5$</p></div>"  # no claim -> no requirement

# Silently-broken macro definitions: the brace-wrapped forms render as KaTeX "Extra }" errors.
# As in the real HTML, each LaTeX backslash is doubled by the JS string literal.
BROKEN_BM = "macros:{'\\\\bm':'{\\\\boldsymbol}'}"          # \bm{F} -> {\boldsymbol}{F} -> error
BROKEN_UNIT = "macros:{'\\\\unit':'{\\\\,\\\\text}'}"        # \unit{m/s} -> error
FIXED_MACROS = "macros:{'\\\\bm':'\\\\boldsymbol','\\\\unit':'\\\\,\\\\text'}"  # correct aliases


def run():
    # 1. macros the file defines are recognised
    macros = b.registered_macros(DEFINES)
    assert {"celsius", "unit", "degree"} <= macros, f"macros not detected: {macros}"

    # 2. a defined macro is NOT reported as forbidden (the old false positive)
    hits = b.check_forbidden(DEFINES)
    assert hits == [], f"defined \\celsius/\\unit must not be flagged, got {hits}"

    # 3. the SAME command, used without being defined, is STILL caught
    hits = b.check_forbidden(USES_UNDEFINED)
    assert any(cmd == r"\celsius" for _, cmd in hits), \
        f"undefined \\celsius must still be caught, got {hits}"

    # 4. genuinely unsupported commands stay forbidden regardless of unrelated macros
    hits = b.check_forbidden(SI_ALWAYS_BAD)
    assert any(cmd == r"\SI" for _, cmd in hits), f"\\SI must always be caught, got {hits}"

    # 5. a 已核验 badge backed by a verify artifact is compliant (badges == notes)
    badges, notes = b.check_verified_badges(BADGE_OK)
    assert (badges, notes) == (1, 1), f"backed badge should be (1,1), got {(badges, notes)}"

    # 6. a bare 已核验 badge with no artifact is non-compliant (notes < badges -> FAIL)
    badges, notes = b.check_verified_badges(BADGE_BARE)
    assert badges == 1 and notes == 0, f"bare badge should be (1,0), got {(badges, notes)}"

    # 7. no badge -> no requirement (0/0, never fails)
    badges, notes = b.check_verified_badges(NO_BADGE)
    assert (badges, notes) == (0, 0), f"no-badge file should be (0,0), got {(badges, notes)}"

    # 8. brace-wrapped \bm / \unit macro bodies are flagged as silently-broken
    assert b.check_broken_macros(BROKEN_BM), "broken \\bm '{\\boldsymbol}' must be caught"
    assert b.check_broken_macros(BROKEN_UNIT), "broken \\unit '{\\,\\text}' must be caught"

    # 9. the corrected bare-alias forms are NOT flagged
    assert b.check_broken_macros(FIXED_MACROS) == [], \
        f"fixed aliases must not be flagged, got {b.check_broken_macros(FIXED_MACROS)}"

    print("OK  build_and_check regression tests passed (9/9)")


if __name__ == "__main__":
    run()
