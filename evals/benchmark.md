# study-notes — benchmark (iteration-1)

**Method.** A study-notes page either renders correctly and carries the standardized
exam-ready structure, or it doesn't — so the auto-checks are a 10-point battery
(`evals/check_features.py`): five *rendering-correctness* checks reused from
`scripts/build_and_check.py` (KaTeX template present, no naked Unicode in math, `<div>`
balance, `$` balance, macro-aware forbidden-command scan) and five *structure* checks
(hierarchical TOC, floating nav, collapsible `<details>`, colour-coded sections,
callouts). The battery runs over real artifacts in `examples/`; the baseline is a small
representative no-skill page (`evals/baseline_sample.html`) — what a generic assistant
emits when asked "make study notes" with no skill: plain prose, basic KaTeX, and °/·
written straight into math. Everything here is reproducible:

```bash
python evals/check_features.py examples/*.html evals/baseline_sample.html
```

| eval artifact | config | auto-checks | build_and_check | size |
|---|---|---|---|---|
| 动力学学习笔记 (MODE A) | with_skill | **10/10** | pass | 446 KB |
| 重积分应用与含参积分 (MODE B) | with_skill | **10/10** | pass | 81 KB |
| 多元函数微分学期中测验 (MODE C) | with_skill | **10/10** | pass | 81 KB |
| baseline_sample (no skill) | baseline | 4/10 | **FAIL** (3 naked Unicode) | 1.6 KB |

## Discriminating vs non-discriminating checks

- **Discriminating (skill wins):** *no naked Unicode in math*, *hierarchical TOC*,
  *floating nav*, *collapsible `<details>`*, *colour-coded sections*, *callouts*. The
  baseline fails **all six**: it writes `$T = 27°C$` and `$\text{J/(mol·K)}$` with the
  literal `°`/`·` (a silent KaTeX failure the browser shows no error for — exactly what
  `build_and_check`'s Unicode scan exists to catch), and produces a flat single-column
  page with no TOC, no navigation, no folding, no colour, no callouts.
- **Non-discriminating (both pass):** *KaTeX template present*, *`<div>`/`$` balance*,
  *forbidden-command clean*. A competent baseline gets these for free — so the skill's
  unique lift is concentrated in **guaranteed checker-clean math + the standardized,
  navigable, collapsible exam-ready structure**, not in "remembering to load KaTeX".

## Corpus evidence (the verification gate earns its place)

Replaying `build_and_check.py` over the author's 27 standalone real products: **19 pass
all static checks**; the 8 failures are all *older outputs that predate the verification
discipline* — 7 with naked-Unicode-in-math (worst: a recalled-exam page with 18) and one
with a `<div>` imbalance. None of the recent, gate-checked products fail. That is the
benchmark that matters: the gate flips exactly the buggy legacy files to FAIL with **zero
false positives** after the macro-aware fix (see `scripts/test_build_and_check.py`), so a
red light now means a real, fixable defect — not noise.

## Qualitative

- **MODE A (动力学):** 3177 KaTeX spans render with **0 errors**, 46 colour-coded cards,
  89 collapsible derivations/solutions, 39 inline SVG figures, hierarchical TOC + floating
  nav; mobile (390 px) shows **0 horizontal overflow**.
- **MODE B (重积分):** every homework problem is woven in as a collapsible worked-example
  that points back to the concept just taught; formula speed-table + per-problem SVG
  figures + green answer boxes; the audit's most complete product (fbox 47 / details 19).
- **MODE C (多元函数期中):** 20 problems, each a card with the statement always visible and
  the full step-by-step solution folded — built for "attempt first, then check".

## Cost note

The skill spends materially more tokens than a no-skill answer — the price of the
plan → fan-out → **verify** (blind double-solve + compute-with-code) → assemble workflow
and the full styled single-file build. The payoff is a checker-clean, exam-ready artifact
a student keeps and reopens, versus a one-shot block of prose.

## iteration-1 (2026-06-13) — macro-aware checker fix validation

Replay of the new `build_and_check.py` over the real corpus: **7 false-positive FAILs
flip to PASS** (files failing only on `\celsius`/`\unit` defined as macros on their own
registration line), while **every genuine failure stays caught** (naked Unicode, div
imbalance). 0 real bugs lost. Locked in by `scripts/test_build_and_check.py` (4 cases).
