---
name: study-notes
description: Generate polished, standalone HTML study notes AND full step-by-step homework solutions for academic subjects, especially STEM (physics, math, chemistry, engineering, CS). Trigger on requests to create study notes, learning notes (学习笔记 / 复习笔记), a study guide, lecture notes, or self-study reference — e.g. "make me notes on X", "help me learn X", "summarize X for an exam"; when the user uploads a PDF textbook or course material and asks for review notes; or when the user gives homework / 习题 (作业题) and wants either re-learning notes for the chapter those problems test, or full collapsible solutions (each problem and figure shown, each solution folded). Output is one HTML file with KaTeX math, color-coded sections, collapsible derivations and solutions, callouts, worked examples, and practice problems. Not for slide/课件 exam cheat-sheets (use summarize-slides) or business/research reports (use visual-report).
---

# Study Notes Skill

Generates detailed, exam-ready HTML study notes — and full homework solutions — that are visually polished, mathematically rigorous, and pedagogically structured, modeled after the best university-level reference materials.

**Default audience assumption**: treat the reader as someone encountering this subject for the first time. Write as if they attended lectures but are confused and need everything explained clearly — intuition first, then rigor, then worked examples. Never assume prior knowledge beyond what is stated as a prerequisite.

**Path convention (read this first).** The examples below use `/mnt/user-data/uploads/` (inputs) and `/mnt/user-data/outputs/` (outputs) as **placeholders** — these are the Claude.ai web paths. In **Claude Code** (or any other environment) substitute the real paths: read inputs from wherever the user's files actually are, and write the final HTML to the current working directory (or a directory the user names). Every helper script in `scripts/` takes paths as arguments, so nothing is hard-coded — call them with the paths that exist in your environment.

**Environment portability.** Commands below say `python3` and end with `present_files` — both are Claude.ai-web conventions. On a local machine (e.g. Windows) the interpreter is usually just `python`, and there is no `present_files` — instead, simply report the absolute path of the finished HTML so the user can open it. Use whichever interpreter name resolves in the current environment.

---

## 0. Workflow Routing — 先判断模式（START HERE）

This skill is a **multi-branch workflow**. Before generating anything, read the input, then route to exactly one mode.

> On the relationship to Claude Code "dynamic workflows": a SKILL.md cannot *be* a dynamic workflow (those are JavaScript-orchestrated subagent runs). What this routing does is make the skill *behave* like one — a decision tree over input types. **All three modes should additionally run their generation as a workflow** — plan → fan-out → **verify** → assemble — rather than one giant pass. This is what fixes shallow notes and wrong answers. See **`references/workflow-orchestration.md`** (mandatory for MODE A and MODE B) and the scale tip in MODE C.

| Input | User's intent | → Mode |
|---|---|---|
| 课本 / 讲义 PDF (text or scanned images) | "出学习笔记 / 复习笔记 / review notes" | **MODE A** — PDF → 学习笔记 |
| 几道作业 / 习题 | "用这些题帮我重新学这一章" | **MODE B** — 作业题 → 章节学习笔记 |
| 一份作业 / 习题 | "给我每道题的解答 / 答案" | **MODE C** — 作业题 → 全部题目解答 |
| 只有一个主题，无文件 | "帮我做 X 的笔记" | **MODE A (scratch)** — 从零生成 |

**Routing rules**

1. **Read inputs first.** Extract PDF text/images (Step 0) and read any problem images before deciding.
2. **Detect intent from the verb, not just the attachment**: 学 / 复习 / 笔记 / 整理 → notes (A or B); 解 / 答案 / 做题 / solution → solutions (C).
3. **If ambiguous** (problems given, no clear verb), ask **exactly one** question:
   *"要我 ① 用这些题帮你重新学这一章（出学习笔记），还是 ② 直接给出每道题的详细解答？"* — then route.
4. **Combined inputs:**
   - PDF **+** 作业 → run MODE A on the PDF, then append a MODE C "习题详解" section to the same HTML.
   - "学这一章，顺便把作业做了" → MODE B notes, with each homework problem embedded as a **collapsible worked-example card** inside the section that teaches its concept.

All modes share the same design system, math-rendering rules, post-generation checks, and file-generation strategy described later in this file. The modes only differ in **what content to produce and how to structure it**.

---

## 0.5 Run generation as a workflow (MANDATORY for MODE A & MODE B)

Do not generate a whole document in one linear pass. Run each mode in four phases — this is the
fix for "笔记空泛" and especially "题做错了". Full details in **`references/workflow-orchestration.md`**; the essentials:

1. **Plan (one pass):** read the source, build the TOC + concept list, and write a **shared spec**
   — notation table (symbols, units, sign conventions from the source), section color plan, and
   the design/HTML/math rules. Every later unit receives this spec so parallel output stays consistent.
2. **Fan-out:** generate **one section per concept** as its own unit (dynamic workflow if the word
   "workflow" is in the run, else parallel subagents via the Task tool, else sequential for small
   topics). Focused units go deeper than one overloaded pass.
3. **Verify (the decisive step):** check each fragment with `scripts/build_and_check.py`, and
   **verify every answer** — every worked example (MODE A) and every homework solution (MODE B) —
   with the **per-problem verification checklist** in `references/workflow-orchestration.md`.
4. **Assemble + coherence pass:** concatenate in order, then one pass for consistent notation,
   no duplicate/clashing sections, working TOC links; re-run the post-generation checks.

**Why answers come out wrong — and the cure.** A linear pass writes a solution once and never
checks it, and does arithmetic in its head. The workflow cures both:

- **Blind double-solve.** Solve each problem, then **independently re-solve from only the problem
  statement** without looking at the first solution. If the two final answers disagree, find the
  error and reconcile — **never ship a problem whose two solves disagree.**
- **Compute with code.** Do every non-trivial number with `python3` and every non-trivial
  symbolic step — **especially every derivative, integral, and series/Taylor expansion** — with
  `sympy`; paste only verified results into the HTML. Never differentiate by hand. When a problem
  **gives** an equation and asks for its derivative, differentiate the **given** expression with
  `sympy` rather than recalling a "standard" textbook answer — pasting a remembered result is the
  classic source of a wrong-but-confident solution (cautionary case in `references/workflow-orchestration.md`).
- **Earn the `已核验 ✓` badge by EXECUTION, not assertion.** A SKILL.md instruction to "verify"
  is itself text the model can fake — so the badge is decided by a script, not by you. For every
  machine-verifiable problem, add an invisible `<script type="text/x-verify">` block that
  **recomputes the answer from the GIVEN data with sympy and asserts it equals the printed answer**
  (helpers: `check_derivative` / `check_integral` / `check_equal` / `check_consistent` /
  `check_limit` / `check_numeric`). Then run `python scripts/verify_solutions.py <file>.html`: it
  executes every block and **only a PASSING block may carry `已核验`**. If a check fails → the
  answer is wrong, fix it; if a problem has no clean symbolic check (proof, 讨论题) → tag
  `未自动核验` (abstain), **never** `已核验`. A false `已核验` is worse than none (same honesty rule
  as `.src-ref`). Full convention: `references/design-system.md` → "已核验 verification — the
  EXECUTABLE gate". **Never pass the claimed answer in as the recomputation** — that defeats the gate.
- **Ground in the source.** If a chapter PDF/notes are given, the method must match what the
  chapter teaches; cite formula numbers.

This phase/verify discipline is required even when you run everything sequentially in one context —
only the *parallelism* is optional; the **plan → fan-out → verify → assemble** structure and the
verification are not.

---

## MODE A — PDF 学习笔记模式 (PDF → Study Notes)

**Activate this mode** when the user uploads a PDF textbook or course material and asks for 学习笔记 / 复习笔记 / review notes / organised notes from the book. (With no PDF and only a topic, use the same Content Structure from scratch — "MODE A scratch".)

Follow Steps 0–4 below for PDF handling, then generate content using the **full Content Structure** (same depth as scratch mode — derivations, intuition, examples, everything), **run as the four-phase workflow in §0.5 / `references/workflow-orchestration.md`** (plan → fan-out → verify → assemble; full detail there). The steps below only govern how to read the PDF and handle special formatting rules; they do NOT reduce the depth or completeness of the notes.

**Exception — compact/formula-only mode**: If the user explicitly asks for a condensed version (e.g., "只要公式", "精简版", "只整理公式和概念"), then limit content to core formulas and key concepts only for that request.

### Step 0 — Read the PDF

Use the helper script — it auto-detects scanned PDFs, prints `--- PAGE N ---` markers, and renders page images:

```bash
python3 scripts/extract_pdf.py text <input.pdf> -o <outdir>/extracted.txt
# if extracted.txt is empty / near-empty → scanned PDF, render pages to images:
python3 scripts/extract_pdf.py images <input.pdf> -o <outdir>/pages --dpi 150
```

(The script wraps `pymupdf`; read its `--help` if you need the raw call.) If text extraction yields 0 / very few lines (scanned/image-only PDF), render pages to PNG and use the Read tool to view each page image. Read ALL pages — never skip content.

Then extract the table of contents: note every chapter title, section number, and sub-section heading. This becomes the TOC in the HTML notes.

### Step 1 — Detect subject and name the file

From the book's title page or content, determine the subject (e.g., 力学, 热学, 电磁学, 线性代数, 有机化学).
- Output filename: `<subject>学习笔记.html` (e.g., `力学学习笔记.html`)
- Page subtitle in the `.header`: `<subject>学习笔记 · 覆盖全书重点`

### Step 2 — Identify elective sections

Sections or problems marked with `*`, `★`, or labelled 选学/选读 are **elective** — the student has not studied them.

Rules:
- **Skip** elective sections entirely if they contain no concepts relevant to the core curriculum.
- **Include briefly** (one short card) if the section contains a formula or concept that cross-references non-elective material or is commonly tested.
- **Mark every included elective item** with an `.elective-badge` span, and append ` ★` (plain text) after its title in the TOC.
- Never expand elective content to the same depth as core content.

CSS + usage markup: `references/design-system.md` → **MODE A note components → Elective badge**.

### Step 3 — Figures, images, and tables

**Figures and diagrams**: In MODE A, do NOT draw SVG diagrams or embed base64 images unless the user explicitly asks — write an inline `<p class="fig-ref">（见图 X-X：图题）</p>` reference using the book's exact figure number and caption. CSS + markup: `references/design-system.md` → **MODE A note components → Figure reference**. (MODE C is different — figures are mandatory there, drawn as SVG or embedded from the original; see MODE C.)

**Tables**: Reproduce simple tables directly in the HTML using a `<table>` element inside a `.card`. Use the design system's table CSS (alternating row backgrounds). A table is "simple" if it has ≤ 8 columns and its content (text or short formulas) fits comfortably in a cell. For complex multi-page tables, write a reference instead: `（见表 X-X：表题）`.

### Step 4 — Example problems and exercises

**All example problems (例题) and exercise answers/hints (答案、提示) MUST be placed inside collapsible `<details>` blocks** — never inline. `<summary>` shows the problem number + title (always visible); statement, steps, answer, and hints go in `.details-body`. Omit the card if a section has no examples; group chapter-end exercise answers as one `<details>` per exercise in a single card at the chapter's end. Full HTML pattern: `references/design-system.md` → **MODE A note components → Collapsible example / exercise card**.

---

## MODE B — 作业题 → 对应章节学习笔记 (Homework → Chapter Notes)

**Goal**: the student gives a handful of homework problems; you infer which chapter/topic they test, then produce **full study notes for that chapter** (same depth as MODE A), using the problems as the spine for re-learning. The point is not to answer the problems in isolation — it is to **re-teach the chapter so the student can solve them and others like them.**

### Steps (run as the four-phase workflow — see `references/workflow-orchestration.md`)

The intent is unchanged: **reverse-infer the chapter from the problems and produce complete
notes for the whole chapter**, with each homework problem embedded as a collapsible worked
example. The phases below add a correctness layer so those embedded solutions are actually right —
this is the fix for "MODE B 有时候题都做不对".

**B0 — Read the problems.** Read text and/or images (see "Reading problem images" in `references/problem-solutions.md`). If a course PDF or chapter scan is also provided, use **its** section numbering and notation throughout.

**B1 — Plan: map problems → concepts + shared spec (one pass).** For each problem, identify the concept(s) it requires (e.g. 题3 → 动量守恒 + 完全非弹性碰撞；题5 → 转动惯量 + 平行轴定理) and its prerequisites. Tell the user this mapping in one short line, e.g. *"这几题集中在：动量守恒、非弹性碰撞、转动惯量——我会按这条线把整章重点串起来。"* Set **scope** = union of those concepts **+** prerequisites **+** surrounding chapter context, so the notes re-teach the whole chapter (not just the sub-points the problems poke at). Write the **shared spec** (notation table from the source, section color plan) used by all later units.

**B2 — Solve + VERIFY every problem (do this BEFORE writing the notes; one unit per problem).** This is the key step. For each problem:
- **Solve** the full step-by-step solution using the method the chapter teaches; do every non-trivial number with `python3` and every non-trivial symbolic step with `sympy` (don't do mental math).
- **Verify blind**: independently re-solve from ONLY the problem statement, then run the **verification checklist** (units, limiting cases, substitute the answer back, recompute with code, method matches source, state assumptions).
- **Reconcile**: if the two independent answers agree → encode the check as a `<script type="text/x-verify">` block (recompute from the **given** data, assert it equals the printed answer) and run `verify_solutions.py`; only a PASSING block earns `已核验 ✓`. If they disagree, or no clean symbolic check exists → fix it or tag `未自动核验`; **never ship a disagreeing/unchecked answer as 已核验.**
- Carry the verified solutions forward into B4. (For ≥6 independent problems, run this phase as a dynamic workflow / parallel subagents — one per problem.)

**B3 — Generate notes (fan-out, one unit per concept)** using the full **Content Structure** (intuition → rigorous statement → derivation → special cases → worked examples → common mistakes → connections → exam tips). Order sections pedagogically (prerequisite → core → harder), not in the order the problems happened to be given. Each unit gets the shared spec.

**B4 — Weave the VERIFIED homework solutions in as worked examples.** For EACH homework problem, place a worked-example card in the section that teaches its concept:
- `<summary>` names it, e.g. `作业 3　两物体完全非弹性碰撞求末速度` — always visible.
- The full statement, every solution step, and the final answer (`.answer-box`) go inside a collapsible `<details>`; add a small `已核验 ✓` marker **only if its `<script type="text/x-verify">` block passes `verify_solutions.py`** (otherwise `未自动核验`).
- The solution should point back to the concept just taught ("用刚才 §2.3 的动量守恒").
- If the problem came with a figure, **embed the original image** — do not redraw it as SVG even if it looks simple (see the **MODE C figure rule** / `references/problem-solutions.md` §3); draw an SVG only for a text-only problem, and only if you can reproduce it faithfully.
- This is what turns homework into a learning tool: the student reads the concept, then opens the matching problem to see the concept applied.

**B5 — Self-test card + assemble (coherence pass).** End with a "本章习题自测" card that lists every homework problem with a one-line `考点` tag and links to its worked-example card. Then concatenate, run the coherence pass (consistent notation, no duplicate/clashing sections, TOC links resolve) and the post-generation checks.

**Output**: `<subject>-<chapter>学习笔记.html` (e.g. `力学-动量守恒学习笔记.html`). Subtitle: `<chapter> · 由作业题反推重点`. Then run `scripts/build_and_check.py` and the post-generation checks.

---

## MODE C — 作业题 → 全部题目解答 (Homework → Collapsible Solutions)

**Goal**: a standalone HTML page containing **every** given problem with its full, step-by-step solution. The problem statement and its figure are **always visible**; the solution is **hidden in a `<details>` block** until the student clicks. This lets the student attempt each problem first, then check.

### Hard rules (summary — full templates in `references/problem-solutions.md`)

1. **One card per problem.** Always-visible: 题号 + 完整题目文字 + 题目图. Collapsible `<details>`: 解答 (every step), with the final result in an `.answer-box`. Multi-part problems: label `(1) (2) (3)`, each with its own answer.

2. **Figure rule (IMPORTANT — never drop a figure the problem depends on, never ship a wrong one):**
   - **First ask: did the problem COME WITH a figure?** (a textbook/worksheet figure, photo, scan, graph, circuit, mechanism — or even a simple line sketch.) **If yes → embed the ORIGINAL, do NOT redraw it as SVG even if it looks simple.** Crop it from the upload and inline it as a base64 `<img>` (`scripts/extract_pdf.py crop ...` for a PDF page, or `scripts/embed_images.py datauri <png>`); the HTML stays one self-contained file (never external `src`). Redrawing a figure you already have is pure downside — it routinely drops an element (a flat-top 导板 becoming a bare rod) or misplaces labels. This is the common case for homework from a book/worksheet.
   - **Only when the problem has NO figure of its own** (text-only problem, or a diagram you add purely to aid understanding) → draw a **minimal, faithful inline SVG**, following the **SVG-safe-subset** in `references/design-system.md` (single root `<svg>`, absolute viewBox coords, no nested `<svg>`/`%`/`foreignObject`/CSS-`transform`; `build_and_check.py` WARNs on those), then **render the file and eyeball every figure**. If you can't reproduce the setup faithfully and simply, **describe it in words instead — never ship a figure that contradicts the problem.** Don't invent a figure that wasn't given.
   - Full decision rule + crop/embed how-to: `references/problem-solutions.md` §3.

3. **Answers must be correct — verify every one.** Run the **blind double-solve + verification checklist** in `references/workflow-orchestration.md` for each problem: solve, then independently re-solve from the statement alone; do every non-trivial number with `python3` / `sympy` (no mental math); dimensional/units check, limiting cases, substitute the answer back, order-of-magnitude plausibility; state assumptions when ambiguous. If the two solves disagree, reconcile before shipping. Don't hand-wave a step the student would get stuck on. Tag a solution `已核验 ✓` **only after** its `<script type="text/x-verify">` block PASSES `python scripts/verify_solutions.py <file>.html` (the script recomputes from the given data with sympy and compares); a problem with no clean machine-checkable form is tagged `未自动核验`, never `已核验`. A false `已核验` is worse than none. For ≥6 independent problems, run this as a dynamic workflow / parallel subagents (one per problem).

4. **Layout** reuses the design system: each problem = a `.card` containing an `.example-block`; the figure (SVG or `<img>`) sits **above** the `<details>` solution. Cycle section colors by problem group or leave a single accent.

**Output**: `<subject>作业解答.html`. Subtitle: `<作业范围> · 习题详解`. Run `scripts/build_and_check.py` before presenting.

### Scale tip — spawn a dynamic workflow for big batches

If there are many problems (≈8+) or they are independent of each other, you may solve them with **parallel subagents / a Claude Code dynamic workflow** — one agent per problem or per cluster — then concatenate the resulting solution cards into the final HTML. Keep **all** rendering rules identical across agents (same design system, same figure rule, same `<details>` structure) so the concatenated page is consistent. For a handful of problems, just do them inline.

---

## Workflow (General)

1. **Route**: read the input and pick the mode (Section 0).
2. **Read** `references/design-system.md` before writing any code. For MODE A & MODE B also read `references/workflow-orchestration.md` (the plan→fan-out→verify→assemble workflow). For MODE C / any solutions also read `references/problem-solutions.md`.
3. **Read inputs**: PDF (Step 0 / `scripts/extract_pdf.py`) and/or problem images.
4. **Plan → fan-out → verify**: build the TOC + shared spec once, generate one unit per section/problem, and **verify every answer** (blind double-solve + checklist, compute with code) — see §0.5. Write HTML in part files.
5. **Build + check**: run `scripts/build_and_check.py build <part1> <part2> ... -o <output.html>` to concatenate and run the static checks, then run `scripts/verify_solutions.py <output.html>` to **execute** every verification block, then the six post-generation checks below (Check 6 hands the file to codex for a semantic proofread, when available) and the coherence pass. Fix and re-run until clean.
6. **Output** to `<outdir>/<name>.html` and call `present_files`.

## Content Structure

### Section count: driven by content, not by a fixed number

Ask: "If a student had to learn this topic from scratch using only these notes, would anything important be missing?" If yes, add more. There is no upper limit on sections. Cover everything in the given scope.

General arc:
```
Opening: Motivation & context (why this matters, where it appears)
Prerequisites: Any assumed knowledge that is used but not derived here
Core body: One section per distinct concept — as many as needed
  └─ Sub-sections within a section are fine for closely related ideas
Synthesis: Connections between concepts, unified perspective
Applications: Real physical/mathematical/engineering uses
Summary table: Side-by-side comparison of key formulas/ideas
Practice problems: Graded difficulty, all major question types
本章自测 (optional): an interactive self-test quiz — active recall, not passive re-reading
```

**Optional — interactive 本章自测 (MODE A & MODE B).** After the practice problems, you may
add a `.quiz` card: 3–8 multiple-choice questions that grade on click (green/red), reveal an
explanation, track a running score, and remember answers in `localStorage` — all self-contained
in the single file. It turns the notes from something you *read* into something you can *test
yourself on*. Full CSS + HTML pattern + the one-copy JS are in `references/design-system.md` →
**Self-test quiz widget**. Write the questions from the chapter's own pitfalls and exam points;
set `data-answer` to the 0-based correct index and click through once to confirm the key.

**Optional — Anki deck.** The notes can also carry a hidden spaced-repetition deck (a
`<div id="anki-deck" hidden>` of `.anki-card` front/back blocks — plain HTML, no JSON
escaping of LaTeX). It stays invisible in the single file; `python3 scripts/make_anki.py
<notes>.html` exports it (plus any quiz questions) to an Anki-importable TSV. Format in
`references/design-system.md` → **Anki flashcard deck**. Emit it only when the user wants
flashcards; one card per high-value fact/formula/pitfall.

### Within every concept section, cover ALL of the following that apply:

1. **Intuition / physical picture** — analogy, diagram description, or "why this makes sense" before any math. This is mandatory — never lead with a formula.
2. **Rigorous definition or statement** — precise, in a `.fbox` with LaTeX. Every symbol explained. Meet the **Rigor standard** below (textbook-grade: full premises, scope, signs/boundaries; standard, consistent terminology).
3. **Derivation or proof** — full derivation inside a collapsible `<details>` block. Do not skip steps; a student should be able to follow line by line. If multiple derivation routes exist, show the most illuminating one in the collapsible, mention the alternative in text.
4. **Special cases and limits** — what happens at boundary conditions, extreme values, or degenerate cases. These are high-value for understanding and often tested.
5. **Worked examples** — start simple (builds confidence), end at exam difficulty. Show every algebraic step. Minimum 2 examples per section; more for computation-heavy topics.
6. **Common mistakes** — `.mistake` callout. Be specific: not just "be careful with signs" but "students forget the negative sign in the $\hat{\boldsymbol{j}}$ component of the curl because the cofactor expansion alternates $+,-,+$".
7. **Connections** — explicitly state how this concept relates to others in the notes, or to topics from prerequisite courses. Use cross-references like "compare with §3 where we showed...".
8. **Exam tips** — `.exam` callout. What to memorize, what can be derived on the spot, typical question formats.

### Depth standard

The notes should be detailed enough that a student who has attended lectures but is confused can use these notes alone to fully understand the material. Concreteness beats brevity: one well-explained derivation with intermediate steps is worth more than three terse formula statements.

### Rigor standard — 表述要像教科书一样严谨（贯穿全文，不只例题）

直觉铺垫可以通俗、可以打比方；但凡是**正式内容**——知识点介绍里的定义、定理、性质、条件、结论，以及推导的每一步——都要写到教科书级的严谨。**在生成时就照此写**，而不是等 Check 6 打回来再返工（那样费时费 token）：

- **定义/定理陈述精确完整**：写全前提、适用范围、正负号、边界与例外；不缺条件、不含糊其辞。
- **术语与记号规范统一**：用学科标准术语和符号，全篇一致；同一量不换名、同一符号不换义、单位写法规范。
- **不靠"显然""容易看出"掩盖跳步**：该论证的论证，该限定的限定（"当 … 时"），该区分的区分（充分/必要、瞬时/平均、矢量/标量）。
- **直觉也要正确**：为了好懂而牺牲准确不行——错误的直觉比没有更糟。

这正是 **Check 6** 的第 ⑥ 审查项。生成阶段就守住它，能少一轮外部审查的返工——生成与审查用的是同一套标准。

## TOC Structure — Hierarchical Outline (MANDATORY)

Use `.toc-l1` / `.toc-l2` classes from the design system. Markup example: `references/design-system.md` → **HTML Page Template** (the `<div class="toc">` block).

Rules:
- `.toc-l1 > a` links to the `.sec-COLOR` wrapper (`id="s8-1"`)
- `.toc-l2 a` links to the first `<h3>` of that sub-section (`id="s8-1-1"`)
- Same `sec-dot` color for all entries within a chapter
- Sub-sections with no further breakdown may omit `.toc-l2`
- Elective sections: append ` ★` after title text in the TOC link
- **MODE C**: the TOC lists problems (`第1题`, `第2题`, …) instead of concepts — one `.toc-l1` per problem (or per problem group).

## Floating Navigator — Sub-heading Tracking

The nav panel JS tracks which `<h3>` inside a `.card` is on screen. Requirements:

1. Every `<h3>` starting a sub-section must have an `id` matching the TOC href (e.g. `<h3 id="s8-1-1">§8-1-1 近程有序性</h3>`).
2. Use the book's numbering in `<h3>` text (e.g. `§8-1-1`). The nav panel strips leading section numbers from the label automatically.
3. One sub-section per card — never put multiple sub-sections in one card.

## PDF Source Fidelity

When the user supplies a PDF:
- **Structure**: use the book's exact section numbers and titles
- **Formulas**: copy the book's formula numbering (e.g. "(3-14)") as a right-aligned label next to the formula box
- **Figures**: MODE A → write `（见图 X-X：图题）` inline (Step 3); MODE B/C → follow the figure rule (SVG or embed original)
- **Tables**: reproduce simple tables directly; reference complex ones (see Step 3)
- **Notation**: use the book's variable names exactly — never substitute different symbols
- **Language**: keep Chinese text in Chinese; reproduce equations verbatim. Add explanation and intuition on top of — not instead of — the source content.

### Source-grounded fidelity mode (optional)

Trigger when the user asks for 忠实模式 / 对照课本 / 标注出处 / "anchor everything to the
book", or whenever maximum verifiability is wanted. In this mode, **every** formula box and
key conclusion carries a `.src-ref` badge pointing to its exact place in the source —
`见课本 p.123 式(5-7)` — so the student can check each claim against the original book, the
way NotebookLM grounds answers in citations.

- `scripts/extract_pdf.py text` already prints `--- PAGE N ---` markers; record the page each
  formula/definition came from while reading, and attach it as `<span class="src-ref">见课本
  p.N 式(X-Y)</span>` next to the `.fbox` label (CSS in `references/design-system.md` →
  **Source citation tag**).
- Put one `.fidelity-banner` under the header so the reader knows every item is sourced.
- **Honesty (hard rule):** only cite a page/equation number you actually have from the
  extracted source. If you didn't read that page, omit the badge — **never invent a page
  number.** A fabricated citation is worse than none. This is the same discipline as the
  answer-verification gate: claims are grounded or they are hedged, never fabricated.

## Post-generation Formula Check (MANDATORY before presenting)

Run `scripts/build_and_check.py` first (static lint: Checks 2 & 3 plus div-balance, forbidden-command, and the Check 4 verified-badge scan). Then run `scripts/verify_solutions.py` (Check 5 — it **executes** the verification blocks). Run all five checks below (static + executable); then, when the codex MCP tool is available, the Check 6 external review. Present the file only after the five pass and you have adjudicated any Check 6 findings.

### Check 1: KaTeX error spans (runtime)

`class="katex-error"` is only added when KaTeX runs in the browser, so it is **not** present in the static HTML. To catch these, open the finished file in a browser — the template already shows a red banner counting `.katex-error` spans. (The static scans in Check 2/3 catch the silent failures that never raise an error.)

Common fixes:

| Error | Cause | Fix |
|---|---|---|
| `^\circ` without base | starts the formula | Use `{}^\circ\text{C}`, or the `\degree` / `\celsius` macro |
| `\degree`, `\celsius`, `\unit`, `\bm`, `\cdotp` | — | **Not errors** — these are pre-registered template macros (see `design-system.md` → KaTeX Pre-defined Macros). Use them freely; `build_and_check.py` is macro-aware and won't flag them. |
| `\SI{}`, `\qty{}`, `\si{}` | siunitx, not KaTeX and not a macro | Spell the unit: `9.8\,\text{m/s}^2` |
| `\boldsymbol` in display | missing amsmath | Use `\mathbf` or `\bm` |

### Check 2: Silent Unicode failures (CRITICAL — not caught by Check 1)

```bash
python3 scripts/build_and_check.py check <file>.html   # flags every naked ·/°/−/× inside a math span
```

Fix: `\text{J·mol}` → `\text{J}\cdot\text{mol}`, `°` → `{}^\circ`, `−` → `-`, `×` → `\times`, `≈` → `\approx`.

**Auto-repair (recovery):** to rewrite every naked-Unicode-in-math hit in place instead of by hand:

```bash
python3 scripts/fix_math.py <file>.html        # writes a .bak, then re-run the check
```

It only touches inside `$…$` / `$$…$$` (prose and SVG are left alone) and handles the
`\text{}` case correctly (a `·` inside `\text{J/(mol·K)}` becomes `\text{J/(mol}\cdot\text{K)}`,
not a literal `\cdot` stuck inside the text group). Prefer writing it right the first time;
this is for cleaning up a file that already slipped.

### Check 3: `\boxed{}` inside HTML containers (CRITICAL — silent visual failure)

`\boxed{}` wrapped around tall formulas (containing `\dfrac`, `\sqrt`, matrices) inside `.fbox` / `.big-formula` / `.callout` / `.answer-box` renders as an empty grey rectangle that **covers** the formula text. KaTeX raises NO error — Check 1 misses it entirely. The HTML wrappers already provide visible boxes; nested `\boxed{}` is redundant emphasis that breaks rendering.

```bash
grep -n '\\boxed' <file>.html
```

If matches found inside a colored container, REMOVE the `\boxed{...}` wrapper — keep only the inner formula. For full rules and bulk-strip recovery snippet, see `references/design-system.md` → "CRITICAL: Never use `\boxed{}` inside .fbox / .big-formula / .callout".

### Check 4: `已核验` badge must be earned (CRITICAL — credibility)

`build_and_check.py` FAILs the build when the file stamps more `已核验` badges than it records
`<!-- verify: ... -->` artifacts. The badge is a **claim that an independent re-solve agreed**, so
every one must be backed by the recorded check, placed right next to the answer:

```html
<span class="badge b-verified">已核验 ✓</span>
<!-- verify: sympy diff(x,t,2)=l*w^2*(cos(wt)+lam*cos(2wt)), matches main solution -->
```

```bash
python3 scripts/build_and_check.py check <file>.html   # FAILs on any 已核验 without a verify artifact
```

The counter matches only the **badge element** — a `<span class="badge …">已核验 …</span>` pill — so
explanatory prose ("所有解答都做了独立核验"), a legend showing what the pill looks like, and code/CSS
comments that merely name it do **not** inflate the count. Conversely, every reader-visible "已核验"
claim must BE that pill (don't fake-verify with an ad-hoc `<span style="…">已核验</span>` that escapes
the gate). The honest abstention is the matching pill `<span class="badge b-unverified">未自动核验</span>`.

If a badge has no artifact, either it was never truly re-verified → **remove the badge** (a false
`已核验` is worse than none, exactly like a fabricated `.src-ref` page number), or you did verify
but didn't write it down → **add the `<!-- verify: -->` comment** carrying the sympy/numeric result.
Do all differentiation/integration with `sympy`, never by hand — hand-differentiation is the
documented cause of the "wrong answer, still 已核验" failure (e.g. a given $x(t)$ whose printed
$\ddot x$ had the wrong sign and coefficient yet was stamped verified).

### Check 5: `verify_solutions.py` — EXECUTE the verification (CRITICAL — the real gate)

Check 4 only confirms a verify artifact *exists*; it can't prove it is *true* — a confidently-wrong
model can still write a plausible-looking note. Check 5 crosses that trust boundary by **running**
the checks:

```bash
python3 scripts/verify_solutions.py <file>.html
```

It extracts every `<script type="text/x-verify">` block, executes it (real sympy recomputes the
answer from the **given** data and compares to the printed answer), and **gates the badge**: a
solution may keep `已核验` only if its block PASSES; a block whose recomputation disagrees FAILs the
run (and prints the real value vs. the claimed one); a `已核验` with no passing block FAILs. Fix the
solution or downgrade it to `未自动核验` until this is clean. This is the check that actually catches
"自信地标了已核验却算错". Full convention: `references/design-system.md` → "已核验 verification — the
EXECUTABLE gate".

### Check 6: 外部交叉审查 — second-model proofread (catches what sympy can't)

Checks 1–5 are mechanical/symbolic: they catch KaTeX slips, naked Unicode, broken `\boxed{}`, and
answers whose **numbers** don't recompute. They are structurally blind to errors only a careful reader
notices — anywhere in the note, concept exposition and worked solutions alike: a statement that is
**conceptually** wrong, a derivation whose Chinese prose contradicts its own formula, a figure that
doesn't match the text, a logical jump between steps. (Canonical case: an effective-permeability solution that correctly computes
$\mu_e\approx91$ from $R_{m0}=(l_1+l_2)/(\mu_0 S)$ — the all-**vacuum** reluctance — while the Chinese
text labels $R_{m0}$ "同尺寸**全铁心**时磁阻". `sympy` confirms 91; only a reader catches that the
words contradict the formula — if $R_{m0}$ really were all-iron the ratio would be $\approx0.091$, not
91.) So, as the **final gate**, hand the **whole finished note** to a *second model* — OpenAI **codex**
via its MCP server — to proofread the entire document (knowledge-point exposition included, not just the
worked problems) for exactly these sympy-invisible errors.

**Run it only if the `mcp__codex__codex` tool is available** (the codex MCP server is configured in
this client). If it isn't, skip this check with a one-line note — never block on it; users without
codex still get their file. One-time setup: `claude mcp add codex -- codex mcp-server` (on Windows
wrap a non-PATH binary in `cmd /c`, e.g. `-- cmd /c codex mcp-server`; codex must be logged in). Call
it with the file's **absolute** path:

```
mcp__codex__codex(
  prompt: "你是严格的理工科学习笔记审查者。读取并通读 <ABS_PATH>.html 的**整篇笔记**——不仅是例题和解答，更包括知识点介绍、概念讲解、定义/定理陈述、推导、正文叙述与所有图。只找符号计算(sympy)查不出的问题：
           ①任一处内容（概念讲解、定义、定理、推导、例题解答一视同仁）在概念/物理上是否真的正确
           ②叙述与推导的逻辑是否自洽、有无跳步、循环论证或前后矛盾
           ③每处公式与其中文文字说明是否一致（定义、所指对象、条件/介质/符号别写反）
           ④图与正文/题目是否相符
           ⑤量纲、单位、特例与边界是否合理
           ⑥表述是否达到教科书级的严谨：定义/定理/条件与结论的陈述精确完整（前提、适用范围、正负号、边界不缺不含糊），术语与记号规范统一，无口语化、似是而非或想当然的断言——直觉铺垫可通俗，正式定义与结论必须严谨。
           逐条给出：问题位置（章节/小节/题号）+ 为什么错 + 应改成什么。只报问题，不要重写整篇。",
  cwd: "<ABS_OUTPUT_DIR>", sandbox: "read-only", approval-policy: "never"
)
```

Then **you (not codex) adjudicate** each finding: fix the genuinely-wrong ones, and after any content
fix **re-run Checks 2–5** (a fix can reintroduce a `\boxed{}`/Unicode slip or invalidate an x-verify
block). Note anything you judged a false positive and why. codex's review is a second opinion — it does
**not** grant `已核验` badges (those stay gated by `verify_solutions.py`); it can only prompt you to
correct or downgrade content. Present the file only after this pass.

Re-run all checks after fixing.

## Math Rendering

Copy the `<head>` KaTeX block **verbatim** from `references/design-system.md` → **HTML Page Template** — it loads KaTeX, registers the macros (`\degree`, `\celsius`, `\d`, `\e`, `\bm`, …), and installs the post-render error banner. Do not hand-roll a shorter `renderMathInElement` call; the macros and banner are load-bearing.

- Inline: `$...$` | Display: `$$...$$`
- Vectors: `\vec{F}` (arrow notation), unit vectors: `\hat{n}`, differentials: `\mathrm{d}x`
- Do NOT use `\boldsymbol{}` alone for vectors — bold is nearly invisible in body text.

### Units in KaTeX — CRITICAL

NEVER use Unicode `·` inside `\text{}`. Use `\cdot` (LaTeX command) instead.

| WRONG — silent failure | CORRECT |
|---|---|
| `$\text{J·mol}^{-1}$` | `$\text{J}\cdot\text{mol}^{-1}$` |
| `$\text{W·m}^{-1}$` | `$\text{W}\!\cdot\!\text{m}^{-1}$` |
| `$\text{m}^2\text{·s}^{-1}$` | `$\text{m}^2\!\cdot\!\text{s}^{-1}$` |

Inside `$...$` or `$$...$$`: ONLY ASCII and LaTeX commands — never Unicode symbols.

See `references/design-system.md` → **KaTeX Pre-defined Macros** and **KaTeX Forbidden Commands** for the complete macro / unit / forbidden-command tables. These naked-Unicode-in-math slips are silent — the browser shows no error — so always run the static scan before presenting:

```bash
python3 scripts/build_and_check.py check <file>.html
```

It flags every `·`, `°`, `−`, `×` that lands inside a math span (and is macro-aware: a command your file registers as a macro is not reported, while the same command used without a definition still is). Treat a FAIL as blocking — never ship a file until the scan is clean.

## Continuous improvement (when maintaining this skill)

Living document: when a real run comes out wrong, shallow, or mis-triggered, log it in **`references/lessons-learned.md`** and close the loop (distilled rule → backed by a `build_and_check.py` check + `test_*` case if detectable, else an eval). The `triggering` block in `evals/evals.json` guards discovery — update it whenever you tune the description.