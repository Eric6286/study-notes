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
# Prose / CSS-comment / JS that merely MENTIONS 已核验 is NOT a badge pill -> must not be counted
# (the old bare /已核验/ regex counted these and FAILed honest files; see the MODE-A/B examples).
PROSE_MENTION = (
    "<!-- a trailing 已核验 badge -->\n"
    "<p>所有解答都做了独立核验（已核验 ✓），可放心套用。</p>\n"
    "<script>label.replace(/已核验/, '')</script>"
)
# A real badge pill with extra attrs/whitespace (as the examples write it) IS counted.
BADGE_STYLED = "<span class=\"badge b-green\" style=\"font-weight:700;\">已核验 ✓</span>"

# Prime ' right after a TeX space inside math -> KaTeX "unknown group 'internal'" (MODE-C q7 trap).
PRIME_BAD = "<div class=\"fbox\">$\\vec r\\,'(0)=(1,0,3)$</div>"
PRIME_OK = "<div class=\"fbox\">$(\\vec r\\,)'(0)$ and $f'(x)$ and $a\\,b$</div>"  # fixed + normal primes

# Silently-broken macro definitions: the brace-wrapped forms render as KaTeX "Extra }" errors.
# As in the real HTML, each LaTeX backslash is doubled by the JS string literal.
BROKEN_BM = "macros:{'\\\\bm':'{\\\\boldsymbol}'}"          # \bm{F} -> {\boldsymbol}{F} -> error
BROKEN_UNIT = "macros:{'\\\\unit':'{\\\\,\\\\text}'}"        # \unit{m/s} -> error
FIXED_MACROS = "macros:{'\\\\bm':'\\\\boldsymbol','\\\\unit':'\\\\,\\\\text'}"  # correct aliases

# SVG safe-subset (WARN-level offset risks). The favicon data-URI <svg> must NEVER be flagged.
FAVICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 100 100'><text y='.9em' font-size='90'>X</text></svg>\">\n")
GOOD_SVG = (FAVICON +
    "<svg viewBox=\"0 0 200 120\" width=\"200\" xmlns=\"http://www.w3.org/2000/svg\">\n"
    "  <line x1=\"10\" y1=\"60\" x2=\"180\" y2=\"60\" marker-end=\"url(#arr)\"/>\n"
    "  <text x=\"95\" y=\"50\" text-anchor=\"middle\">F</text>\n</svg>")
NESTED_SVG = (FAVICON +
    "<svg viewBox=\"0 0 100 100\" width=\"100\"><svg viewBox=\"0 0 50 50\">"
    "<rect x=\"1\" y=\"1\" width=\"10\" height=\"10\"/></svg></svg>")
PCT_SVG = "<svg viewBox=\"0 0 100 100\" width=\"100\"><rect x=\"0\" y=\"0\" width=\"50%\" height=\"20\"/></svg>"
FOREIGN_SVG = ("<svg viewBox=\"0 0 100 100\" width=\"100\"><foreignObject x=\"0\" y=\"0\" "
               "width=\"40\" height=\"40\"><p>hi</p></foreignObject></svg>")
CSS_T_SVG = ("<svg viewBox=\"0 0 100 100\" width=\"100\"><g style=\"transform:rotate(5deg)\">"
             "<rect x=\"1\" y=\"1\" width=\"5\" height=\"5\"/></g></svg>")
TO_SVG = ("<svg viewBox=\"0 0 100 100\" width=\"100\"><g style=\"transform-origin:center\">"
          "<rect x=\"1\" y=\"1\" width=\"5\" height=\"5\"/></g></svg>")
ATTR_OK = ("<svg viewBox=\"0 0 100 100\" width=\"100\"><g transform=\"rotate(30 50 50)\">"
           "<rect x=\"1\" y=\"1\" width=\"5\" height=\"5\"/></g></svg>")


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

    # 7a. prose / comment / JS that only MENTIONS 已核验 is not a badge pill -> (0,0), never FAILs
    badges, notes = b.check_verified_badges(PROSE_MENTION)
    assert (badges, notes) == (0, 0), f"prose mention must not count, got {(badges, notes)}"

    # 7b. a styled badge pill (class=\"badge …\" + extra attrs) IS counted exactly once
    badges, _ = b.check_verified_badges(BADGE_STYLED)
    assert badges == 1, f"styled badge pill should count once, got {badges}"

    # 7c. a prime ' right after \\, inside math is caught (the KaTeX 'internal' render trap)
    assert b.check_prime_after_space(PRIME_BAD), "prime-after-space must be caught"

    # 7d. the fixed form (prime on a symbol) and ordinary primes are NOT flagged
    assert b.check_prime_after_space(PRIME_OK) == [], \
        f"clean primes wrongly flagged: {b.check_prime_after_space(PRIME_OK)}"

    # 8. brace-wrapped \bm / \unit macro bodies are flagged as silently-broken
    assert b.check_broken_macros(BROKEN_BM), "broken \\bm '{\\boldsymbol}' must be caught"
    assert b.check_broken_macros(BROKEN_UNIT), "broken \\unit '{\\,\\text}' must be caught"

    # 9. the corrected bare-alias forms are NOT flagged
    assert b.check_broken_macros(FIXED_MACROS) == [], \
        f"fixed aliases must not be flagged, got {b.check_broken_macros(FIXED_MACROS)}"

    # 10. a compliant diagram svg + favicon -> no SVG offset risks (favicon never flagged)
    assert b.check_svg_offset_risks(GOOD_SVG) == [], \
        f"clean svg flagged: {b.check_svg_offset_risks(GOOD_SVG)}"

    # 11. nested <svg> is flagged (the favicon's own <svg> is still ignored)
    cats = {c for _, c, _ in b.check_svg_offset_risks(NESTED_SVG)}
    assert "nested-svg" in cats, f"nested svg not caught: {cats}"

    # 12. % geometry inside an svg is flagged
    cats = {c for _, c, _ in b.check_svg_offset_risks(PCT_SVG)}
    assert "percent-geometry" in cats, f"% geometry not caught: {cats}"

    # 13. foreignObject is flagged
    cats = {c for _, c, _ in b.check_svg_offset_risks(FOREIGN_SVG)}
    assert "foreignObject" in cats, f"foreignObject not caught: {cats}"

    # 14. CSS transform: inside an svg is flagged
    cats = {c for _, c, _ in b.check_svg_offset_risks(CSS_T_SVG)}
    assert "css-transform" in cats, f"css transform not caught: {cats}"

    # 15. transform-origin inside an svg is flagged
    cats = {c for _, c, _ in b.check_svg_offset_risks(TO_SVG)}
    assert "transform-origin" in cats, f"transform-origin not caught: {cats}"

    # 16. the SVG attribute transform="rotate(...)" (the recommended form) is NOT flagged
    assert b.check_svg_offset_risks(ATTR_OK) == [], \
        f"SVG transform attribute wrongly flagged: {b.check_svg_offset_risks(ATTR_OK)}"

    print("OK  build_and_check regression tests passed (20/20)")


if __name__ == "__main__":
    run()
