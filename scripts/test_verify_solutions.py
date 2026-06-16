#!/usr/bin/env python3
r"""Regression tests for verify_solutions.py — the executable 已核验 gate.

Locks in the behaviour that matters: a WRONG recomputation fails (so a self-certified wrong
answer cannot ship as 已核验), a CORRECT one passes, an unbacked badge fails, and an honest
未自动核验 abstention is fine. Requires sympy (already a dependency of the skill).

Run:  python test_verify_solutions.py
"""
import verify_solutions as v

# A correct check: d^2/dt^2 of x == claimed (the real answer).
CORRECT = r"""
t, w, lam, l = sp.symbols('t omega lambda l', positive=True)
x = l*((1 - lam**2/4) - sp.cos(w*t) - (lam/4)*sp.cos(2*w*t))
check_derivative(given=x, wrt=t, order=2,
                 claimed=l*w**2*(sp.cos(w*t) + lam*sp.cos(2*w*t)), name="correct a_x")
"""

# The real slider-crank bug: claimed is the recalled textbook answer, wrong in sign & coeff.
WRONG = r"""
t, w, lam, l = sp.symbols('t omega lambda l', positive=True)
x = l*((1 - lam**2/4) - sp.cos(w*t) - (lam/4)*sp.cos(2*w*t))
check_derivative(given=x, wrt=t, order=2,
                 claimed=-l*lam*w**2*(sp.cos(w*t) + lam*sp.cos(2*w*t)), name="wrong a_x")
"""

EMPTY = "x = 1 + 1  # ran no check_* calls\n"

def card(label, code, badge="已核验 ✓"):
    return (f'<div class="card"><h3>{label} <span class="badge">{badge}</span></h3>'
            f'<script type="text/x-verify" data-for="{label}">{code}</script></div>')


def run():
    # 1. a correct block executes and passes
    ok, out = v.run_block(CORRECT)
    assert ok, f"correct block should pass, got:\n{out}"

    # 2. the WRONG slider-crank block fails, and the real recomputed value is surfaced
    ok, out = v.run_block(WRONG)
    assert not ok, "wrong block must fail"
    assert "recomputed" in out and "claimed" in out, f"failure must show both values:\n{out}"

    # 3. a block that runs no checks is rejected (can't earn a badge by doing nothing)
    ok, out = v.run_block(EMPTY)
    assert not ok, f"empty block must fail (require_checks), got:\n{out}"

    # 4. extract_blocks picks up the data-for label
    blocks = v.extract_blocks(card("例7 碰撞末速度", CORRECT))
    assert blocks and blocks[0][0] == "例7 碰撞末速度", f"label not extracted: {blocks}"

    # 5. 已核验 + a PASSING block  -> overall pass
    assert v.run_checks(card("ex-ok", CORRECT)) is True, "badge backed by passing check must pass"

    # 6. 已核验 + a FAILING block  -> overall fail (the headline failure mode)
    assert v.run_checks(card("ex-bad", WRONG)) is False, "badge over a failing check must fail"

    # 7. 已核验 + NO block          -> overall fail (unbacked badge)
    nohtml = '<div class="card"><h3>ex <span class="badge">已核验 ✓</span></h3></div>'
    assert v.run_checks(nohtml) is False, "unbacked 已核验 badge must fail"

    # 8. 未自动核验 abstention + NO block -> ok (honest abstain, no requirement)
    ab = '<div class="card"><h3>ex <span class="badge">未自动核验</span></h3><p>概念题，无符号可算。</p></div>'
    assert v.run_checks(ab) is True, "honest 未自动核验 abstention must be allowed"

    print("OK  verify_solutions regression tests passed (8/8)")


if __name__ == "__main__":
    run()
