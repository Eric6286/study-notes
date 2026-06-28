# Workflow Orchestration & Verification (MODE A & MODE B)

This file explains how to run MODE A and MODE B **as a workflow** instead of a single
giant pass, and — most importantly — how to **verify** content so answers are correct.

## Contents

- **Why a single pass produces low-quality output** — failure → root-cause → fix table
- **How to actually run it (Claude Code)** — dynamic workflow / parallel subagents / sequential; the **shared spec**
- **MODE A workflow** — plan → fan-out (one unit/section) → verify → assemble
- **MODE B workflow** — concept map → solve+verify every problem → generate → weave in → self-test
- **Verification checklist (MANDATORY per problem)** — the blind double-solve + compute-with-code gate

## Why a single pass produces low-quality MODE B output (and how this fixes it)

When one pass has to (a) re-teach a whole chapter AND (b) solve every homework problem,
quality drops for concrete, fixable reasons:

| Failure | Root cause | Fix in this workflow |
|---|---|---|
| **题做错了 / wrong final answer** | The solution is written once and never independently checked. | **Blind double-solve + verify** each problem (below). Never ship an unverified answer. |
| **算错数 / arithmetic & algebra slips** | Mental math over many steps. | **Compute with code** (python/sympy) for every non-trivial number or symbolic step. |
| **方法跑偏 / method doesn't match the course** | No grounding in the source. | If a textbook/notes PDF is given, the method must match the chapter; cite formula numbers. |
| **笔记空泛 / shallow notes** | One context juggles 10+ concepts at once. | **Fan-out**: one focused unit per section/concept, each with room to go deep. |
| **前后不一致 / notation drift, duplicated or clashing sections** | Parallel work with no shared contract. | A **shared spec** handed to every unit + a final **coherence pass**. |

> Parallelism is a side benefit. The decisive quality lever is the **dedicated verification
> step**, which a single linear pass never does. Run the modes as a workflow precisely so
> that verification gets its own isolated attention per problem.

## How to actually run it (Claude Code)

A SKILL.md is Markdown, not a JavaScript orchestrator, so it cannot *be* a dynamic workflow.
Run these modes as a workflow using whichever mechanism is available:

- **Dynamic workflow** — include the word **"workflow"** in the run, letting Claude Code
  orchestrate subagents in JS. Best for many independent units (e.g. ≥6 sections or ≥6 problems).
- **Parallel subagents** — use the Task tool to spawn one subagent per unit. Good default.
- **Sequential, in one context** — if the topic is small (≤3 sections, ≤3 problems), just do
  the phases below in order in a single context. The phases and the verification step are
  mandatory regardless of mechanism; only the parallelism is optional.

**Shared spec (hand this to EVERY unit/subagent so output is consistent):**
- Subject + chapter + output filename.
- The **notation table**: every symbol and its meaning, taken from the source — units, sign
  conventions, variable names. Units must match the source exactly; never substitute symbols.
- **Section color plan**: which `.sec-COLOR` each section uses (assigned once, up front).
- The design-system rules (`references/design-system.md`) and the HTML part conventions
  (Part 1 opens `.page`; middle parts = complete sections; last part closes `.page` + nav JS).
- The math rules (KaTeX-only, no Unicode in math, no `\boxed` in containers).

Cap parallelism (≈8–16 concurrent) and keep rules identical across units, or the concatenated
page will be inconsistent.

---

## MODE A workflow — PDF/topic → study notes

**Phase 1 — Plan (single pass, do NOT skip).**
Read the source (or the topic). Produce, in one coherent pass:
1. The **TOC**: every chapter/section and sub-section, in pedagogical order.
2. The **concept list**: one planned section per distinct concept, each with a one-line scope so
   sections don't overlap or leave gaps.
3. The **notation table** and **section color plan** (the shared spec above).
Planning once, centrally, is what keeps the fanned-out sections consistent and gap-free.

**Phase 2 — Fan-out (one unit per section).**
Each unit generates ONE section's HTML following the full **Content Structure** (intuition →
rigorous statement → derivation in `<details>` → special cases → ≥2 worked examples → common
mistakes → connections → exam tips) and the design system. Each unit receives the shared spec
and only its own section's scope. Save each as a numbered part file.

**Phase 3 — Verify each section (before assembly).**
For every section unit:
- Run `scripts/build_and_check.py check <part>.html` on the fragment (Unicode-in-math, `\boxed`,
  forbidden commands, div balance, `$` balance).
- **Verify every worked-example answer** with the per-problem protocol below — worked examples
  in notes are answers too, and are a common source of errors.
- Check each derivation step actually follows; check formulas against the source.

**Phase 4 — Assemble + coherence pass.**
Concatenate parts in TOC order with `scripts/build_and_check.py build ... -o <file>.html`.
Then one coherence pass over the whole file: consistent notation across sections, no duplicated
content, TOC links resolve, colors cycle sensibly, no contradictions between sections. Re-run
the post-generation checks. Only then `present_files`.

---

## MODE B workflow — homework → full chapter notes (correctness-first)

The goal is unchanged: **reverse-infer the chapter from the problems and produce complete
notes for the whole chapter**, with each homework problem embedded as a collapsible worked
example. The workflow adds a correctness layer so the embedded solutions are actually right.

**Phase 1 — Concept map (single pass).**
For each problem, identify the concept(s) it tests and its prerequisites. Set scope = union of
those concepts + prerequisites + surrounding chapter context (so it re-teaches the whole
chapter, not just the poked sub-points). Tell the user the mapping in one line. Build the
shared spec (notation, color plan) — if a chapter PDF is supplied, use ITS numbering/notation.

**Phase 2 — Solve + verify EVERY problem (the key step; one unit per problem).**
This phase runs *before* writing the notes, so the teaching is built on solutions you trust.
For each problem:

1. **Solve (Solver).** Full step-by-step solution. Use the method the chapter teaches. Do every
   non-trivial calculation **with code** — `python3` for arithmetic, `sympy` for algebra/calculus,
   explicit unit tracking. Show steps; put the final result in an `.answer-box`.

2. **Verify blind (Verifier).** Independently re-solve from ONLY the problem statement, without
   reading the Solver's steps. Then run the **verification checklist** below. Produce an
   independent final answer.

3. **Reconcile.**
   - Solver and Verifier **agree** → encode the check as an executable `<script type="text/x-verify">`
     block (recompute from the **given** data with sympy, assert it equals the printed answer) and run
     `python scripts/verify_solutions.py <file>.html`. **The script, not you, decides the badge:** only
     a PASSING block earns `已核验 ✓`; a problem with no clean machine-checkable form is tagged
     `未自动核验`, never `已核验`. (Why a script and not a self-note: "I verified it" fails the same
     way the answer does — the model that miscomputed will also miscertify. A false `已核验` is worse
     than none, same honesty rule as `.src-ref`.)
   - They **disagree** → a reconciliation pass: locate the error (recompute the disputed step
     with code), re-derive, and only ship once two independent routes agree. **Never ship a
     problem whose two solves disagree.**

4. (For tricky/important problems) optionally solve a **third** way (e.g. energy vs. momentum,
   or a limiting-case argument) for self-consistency.

**Phase 3 — Generate chapter sections (fan-out, one unit per concept).**
Same as MODE A Phase 2: full Content Structure per concept, pedagogical order, shared spec.

**Phase 4 — Weave verified solutions in.**
Place each problem's **verified** solution as a collapsible worked-example card inside the
section that teaches its concept (see `references/problem-solutions.md` §5). The solution should
point back to the concept just taught ("用刚才 §2.3 的动量守恒"). Add a small `已核验 ✓` marker
in the card **only if** it carries its `<!-- verify: -->` artifact (the build check enforces the
1:1 pairing). Figures follow the figure rule (SVG for simple, embed original for complex/photo).

**Phase 5 — Self-test card + assemble.**
End with the `本章习题自测` card (each 作业题 + one-line 考点 tag + link to its worked example).
Concatenate, run the coherence pass and post-generation checks, then `present_files`.

---

## Verification checklist — MANDATORY per problem (MODE B & MODE C; and every MODE A worked example)

A problem's answer is not "done" until ALL applicable boxes pass:

- [ ] **Calculus done with `sympy`, never by hand** — every derivative, integral, and Taylor/series
      expansion is computed with code and the verified expression pasted in. Hand-differentiation
      is the single most common source of a wrong-but-confident answer (see the cautionary case below).
- [ ] **A problem that GIVES an equation and asks for its derivative** is solved by differentiating
      the GIVEN expression with `sympy` — never by pasting a remembered "standard"/textbook result.
- [ ] **Independent re-solve agrees** (blind double-solve; for important problems a third route).
- [ ] **Inputs read off a FIGURE are verified, not just the answer** — any geometry/label taken from a
      diagram (which point/edge, near vs far, length vs gap, above vs below, left vs right) is
      re-checked by **re-deriving a quantity the problem already pins down** (a printed range, a given
      total, a stated result) from your read values. A blind double-solve canNOT catch a mis-read
      figure — both solves inherit the same wrong setup; only re-deriving an independent given does.
      (Cautionary case: 劳埃德镜 — mirror length/position read backwards.)
- [ ] **Executable check passes** — the solution carries a `<script type="text/x-verify">` block that
      recomputes from the **given** data, and `verify_solutions.py` runs it GREEN. Only then may it
      carry `已核验`; otherwise tag `未自动核验`. A written-down note alone is NOT enough — the gate is
      that the check actually executes and agrees.
- [ ] **Units / dimensions** are consistent on both sides of every equation and in the final answer.
- [ ] **Limiting / special cases** behave sanely (set a mass→0, angle→0/90°, k→∞, etc.).
- [ ] **Substitute the answer back** into the governing equation / original condition — it holds.
- [ ] **Numbers recomputed with code**, not by hand (see snippet below).
- [ ] **Order of magnitude** is physically plausible.
- [ ] **Method matches the source** chapter (if a PDF/notes were given); formula numbers cited.
- [ ] **Assumptions stated** explicitly when the problem is ambiguous or under-specified.

If any box fails, fix and re-verify before the answer goes into the HTML.

### Compute with code — don't do mental math

For every non-trivial number or symbolic manipulation, run it rather than computing in your head.
Examples:

```bash
# numeric check
python3 -c "import math; m1,m2,v0=2,4,3; v=m1*v0/(m1+m2); dE=0.5*m1*v0**2-0.5*(m1+m2)*v**2; print(v, dE)"

# symbolic check (algebra / calculus) — install once if missing:
# pip install sympy --break-system-packages -q
python3 -c "
import sympy as sp
m1,m2,v0=sp.symbols('m1 m2 v0', positive=True)
v=m1*v0/(m1+m2)
dE=sp.simplify(sp.Rational(1,2)*m1*v0**2-sp.Rational(1,2)*(m1+m2)*v**2)
print('v=',v); print('dE=',dE)   # confirms the closed form before you write it in the notes
"
```

Paste the **verified** numbers/expressions into the HTML. This single habit removes the most
common cause of wrong answers.

### Cautionary case — the hand-differentiation trap (a real failure this gate exists to stop)

A slider-crank problem **gave** the slider's motion
$x = l\big[(1-\tfrac{\lambda^2}{4}) - \cos\omega t - \tfrac{\lambda}{4}\cos 2\omega t\big]$ and asked
for $\ddot x$. The note printed $\ddot x = -r\omega^2(\cos\omega t + \lambda\cos 2\omega t)$ — a
*remembered* textbook result — and stamped it `已核验`. But differentiating the **given** $x$ twice
gives $\ddot x = +\,l\omega^2(\cos\omega t + \lambda\cos 2\omega t)$: **opposite sign**, and the
coefficient is $l\omega^2 = r\omega^2/\lambda$, **not** $r\omega^2$. The whole answer was wrong yet
looked verified — exactly the credibility leak this gate closes.

Root cause: differentiation done in the head, and a "known answer" pasted instead of derived from
the data given. The cure is mechanical — run it, don't recall it:

```bash
python3 -c "import sympy as sp; t,w,lam,l=sp.symbols('t omega lambda l',positive=True);
x=l*((1-lam**2/4)-sp.cos(w*t)-(lam/4)*sp.cos(2*w*t)); print(sp.factor(sp.diff(x,t,2)))"
# -> l*omega**2*(lambda*cos(2*omega*t) + cos(omega*t))
```

Encode that as an executable `<script type="text/x-verify">` block —
`check_derivative(given=x, wrt=t, order=2, claimed=<printed answer>)` — and let
`verify_solutions.py` run it. It recomputes the real value and **FAILs the wrong `claimed`**, which
is exactly how this bug gets caught instead of rubber-stamped. (See `design-system.md` → "已核验
verification — the EXECUTABLE gate".)
