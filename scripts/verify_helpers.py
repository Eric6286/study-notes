#!/usr/bin/env python3
r"""verify_helpers.py — deterministic checks that EARN the 已核验 badge.

These run inside a ``<script type="text/x-verify">`` block, executed for real by
``verify_solutions.py`` — NOT computed in the model's head. Each check recomputes a quantity
from the problem's GIVEN data with sympy and compares it to the answer the solution claims.
A mismatch raises AssertionError, the block exits non-zero, and verify_solutions marks the
solution FAILED → the 已核验 badge must be withheld (the answer is tagged 未自动核验 instead).

This is the gate that catches "confidently wrong but self-certified": the wrong slider-crank
second derivative fails here because sympy computes the *real* derivative from the given x(t)
and the comparison to the printed answer does not hold.

THE ONE RULE THE CALLER MUST FOLLOW
-----------------------------------
Never pass the claimed answer in as the recomputation. You supply the GIVEN expression and the
operation; the helper does the math. Writing ``check_equal(claimed, claimed)`` defeats the gate
and is the only way to fake it — don't.

Available checks (all take real sympy expressions, not strings):
  check_derivative(given, wrt, order, claimed, name)   d^order/d wrt^order of given == claimed
  check_integral(integrand, var, claimed, name)        d(claimed)/d var == integrand
  check_equal(recomputed, claimed, name)               recomputed == claimed (simplify+expand)
  check_consistent(route_a, route_b, name)             two independent routes agree (差分对账)
  check_limit(expr, var, point, expected, name)        limiting-case sanity
  check_numeric(expr, subs, expected, tol, name)       numeric-substitution sanity
"""
import sympy as sp

_n = 0  # number of checks executed in this block (a block with 0 checks is rejected)


def _equal(a, b):
    """Symbolic equality via simplify(expand(a-b)) == 0 (robust for trig/poly forms)."""
    diff = sp.simplify(sp.expand(sp.sympify(a) - sp.sympify(b)))
    return diff == 0 or (getattr(diff, "is_zero", None) is True)


def _pass(name, detail=""):
    global _n
    _n += 1
    print(f"PASS: {name}" + (f"  ({detail})" if detail else ""))


def _fail(name, recomputed, claimed):
    global _n
    _n += 1
    print(f"FAIL: {name}")
    print(f"      recomputed = {sp.simplify(recomputed)}")
    print(f"      claimed    = {sp.simplify(claimed)}")
    raise AssertionError(f"{name}: recomputed != claimed")


def check_derivative(given, wrt, order, claimed, name="derivative"):
    truth = sp.diff(given, wrt, order)
    if _equal(truth, claimed):
        _pass(name, f"d^{order}/d({wrt})^{order}")
    else:
        _fail(name, truth, claimed)


def check_integral(integrand, var, claimed, name="integral"):
    # antiderivatives differ by a constant, so verify by differentiating the claimed result
    if _equal(sp.diff(claimed, var), integrand):
        _pass(name, f"d(claimed)/d({var}) == integrand")
    else:
        _fail(name, sp.diff(claimed, var), integrand)


def check_equal(recomputed, claimed, name="equality"):
    if _equal(recomputed, claimed):
        _pass(name)
    else:
        _fail(name, recomputed, claimed)


def check_consistent(route_a, route_b, name="two-route agreement"):
    """差分对账 / blind double-solve made executable: two independent derivations must agree."""
    if _equal(route_a, route_b):
        _pass(name, "route A == route B")
    else:
        _fail(name, route_a, route_b)


def check_limit(expr, var, point, expected, name="limiting case"):
    truth = sp.limit(expr, var, point)
    if _equal(truth, expected):
        _pass(name, f"{var}->{point}")
    else:
        _fail(name, truth, expected)


def check_numeric(expr, subs, expected, tol=1e-6, name="numeric sanity"):
    global _n
    val = complex(sp.sympify(expr).subs(subs))
    exp = complex(expected)
    _n += 1
    if abs(val - exp) <= tol * max(1.0, abs(exp)):
        print(f"PASS: {name}  ({val.real:.6g} ~ {exp.real:.6g})")
    else:
        print(f"FAIL: {name}")
        print(f"      value    = {val}")
        print(f"      expected = {exp}")
        raise AssertionError(f"{name}: numeric mismatch")


def require_checks():
    """Appended by the runner after the block. A block that ran zero checks is not a
    verification — reject it so an empty block can never earn a badge."""
    if _n == 0:
        print("FAIL: x-verify block executed but ran no check_* assertions")
        raise SystemExit(2)
    print(f"-- {_n} check(s) passed --")
