# Problem Solutions Reference (MODE B / MODE C)

How to turn homework problems into HTML — the always-visible problem + figure, the collapsible solution, and the figure decision (draw SVG vs. embed the original image). Read this together with `design-system.md`.

## Contents

1. **Reading problem images** — text / photo / PDF worksheet; transcribe exactly
2. **The MODE C problem card** — 题号+题目 visible, `<details>` solution, `.answer-box`
3. **Figure decision — SVG vs. embed original** — the core MODE C rule + checklist
4. **Embedding the original figure (base64)** — crop from PDF / datauri / inline-at-end
5. **MODE B — homework as a worked-example card** — problem lives inside the concept section

---

## 1. Reading problem images

Homework arrives as: pasted text, photos of a worksheet, or a PDF.

- **Text / pasted**: use it directly.
- **Photo / screenshot (PNG/JPG)**: open it with the Read tool and transcribe the problem text faithfully. Keep the figure for embedding (Section 4).
- **PDF worksheet**: extract text + render pages, then crop each problem's figure:

```bash
python3 scripts/extract_pdf.py text homework.pdf -o hw.txt
python3 scripts/extract_pdf.py images homework.pdf -o hw_pages/ --dpi 200   # to view layout
# crop one figure (bbox = fractions of the page: x0,y0,x1,y1 from top-left):
python3 scripts/extract_pdf.py crop homework.pdf --page 2 --bbox 0.08,0.18,0.92,0.52 -o fig_q3.png
```

Transcribe **exactly** — same given numbers, same symbols, same units. Never silently "fix" a problem; if something is missing or contradictory, state the assumption you make.

---

## 2. The MODE C problem card

One `.card` per problem. Structure: **题号 + 题目文字 (visible) → 图 (visible) → `<details>` 解答 (hidden)**.

```html
<div class="sec-blue" id="q3">
<div class="section">
  <div class="section-header">
    <div class="section-num">3</div>
    <h2>第 3 题</h2>
  </div>

  <div class="card">
    <h3 id="q3-stmt">题目</h3>
    <p>质量 $m_1 = 2\,\text{kg}$ 的滑块以 $v_0 = 3\,\text{m/s}$ 撞上静止的 $m_2 = 4\,\text{kg}$ 滑块并粘连，求碰后共同速度与机械能损失。</p>

    <!-- FIGURE: either inline SVG (simple) or embedded <img> (complex/photo). See §3–§4. -->
    <div style="text-align:center;margin:12px 0;">
      <svg viewBox="0 0 360 120" width="360" xmlns="http://www.w3.org/2000/svg"><!-- simple diagram --></svg>
    </div>

    <details>
      <summary>解答</summary>
      <div class="details-body">
        <p><strong>(1) 动量守恒</strong>（碰撞瞬间外力冲量可忽略）：</p>
        <div class="fbox"><div class="frow">$$m_1 v_0 = (m_1+m_2)\,v$$</div></div>
        <p>解得</p>
        <div class="answer-box"><p>$v = \dfrac{m_1 v_0}{m_1+m_2} = 1\,\text{m/s}$</p></div>

        <p><strong>(2) 机械能损失</strong>：</p>
        <div class="fbox"><div class="frow">$$\Delta E = \tfrac12 m_1 v_0^2 - \tfrac12 (m_1+m_2)v^2$$</div></div>
        <div class="answer-box"><p>$\Delta E = 9 - 3 = 6\,\text{J}$</p></div>

        <div class="callout intuition">
          <div class="callout-icon"></div>
          <div class="callout-body"><strong>直觉</strong>
            <p>两块粘在一起后一起走，动量这块"账"在碰撞瞬间没漏（外力冲量可忽略），但动能转成了热和形变，所以速度落在 0 与 $v_0$ 之间、能量必有损失。</p></div>
        </div>
        <div class="callout mistake">
          <div class="callout-icon"></div>
          <div class="callout-body"><strong>易错</strong>
            <p>完全非弹性碰撞**不能**用机械能守恒列方程（能量不守恒）；只能用动量守恒求 $v$，再单独算能量损失。</p></div>
        </div>
        <!-- 注意：不再放读者侧「检验」框（量纲/极限核验）——用户偏好，正确性由 sympy 可执行门把关。 -->
      </div>
    </details>
  </div>
</div>
</div>
```

Rules （解答呈现规范 — 对齐金标准范本《理论力学·动力学作业详解》，完整说明见 SKILL.md §0.6『HTML 落地』）:
- `<summary>` 写 `查看解答` 并把已核验徽章放进去（`查看解答 <span class="badge b-verified">已核验 ✓</span>`）；never reveal the answer in the summary.
- **步骤要细，用 `.step`，一步一个动作**（识别题型 → 选对象/建系画受力 → 列方程 → 变形/分离变量 → 代入初值 →
  积分求解 → 反解 → 取极限/特例 → 即时小检验），范本约 **7–8 步/题**，别用 3–4 步草草带过。
  `step-body` 先一句**加粗的"这一步在干什么"**，紧跟**融入式口语化叙述**把"为什么这么做、为什么这样变形更顺手、
  用的是哪条原理"讲清楚——像老师边写边讲，**不要**塞进生硬的"为什么：…"标签框或自造 `.why` 类。
- **加粗两级、正文强调走行内**：步骤标题＝`step-body` 开头那**一个** `<strong>`（独占一行）；正文术语强调用**行内 `<strong>`**，
  嵌在句中、**绝不另起一行或独占一行**。别把强调词单独成段 / 块级（会碎成一行一个、和标题撞成同层级）；强调要克制，一段点一两个即可。
- **每个公式都配 `.fnote`**：每个 `.fbox` 算式下用 `<div class="fnote">` 写一行——这一步在做什么
  （"两边同除以 $m$""分离变量后的形式"）或新符号含义（"$\eta$ 阻尼系数，向下为正"）。**不留没注释的公式。**
- **点名原理、能链则链**：用到的定理/方法写出名字或课本编号；同目录有配套《学习笔记》就把原理名链到对应小节
  （`<a href="…学习笔记.html#sX-Y" target="_blank">`）。
- **每题二件套 callout**：`.callout intuition`（直觉：物理/几何图景或"为什么结果合理"）+ `.callout mistake`
  （易错：本题最易踩的符号/方向/条件坑）。**不要**单立读者侧「检验」框（量纲/极限核验）——用户偏好，
  正确性由 §0.5 sympy 可执行门把关；想做的小检查可顺手融进步骤正文（如"代回初值吻合"）。
  禁止用"显然/易得/同理/不难看出"掩盖跳步；能即时验的小检查直接写进步骤。
- Final result(s) in `.answer-box`. Multi-part → one `.answer-box` per part, labelled `(1) (2) (3)`.
- 顶部放 `.lead`（或 `.callout note`）用法说明 + 核验图例（图例用 `<strong>已核验 ✓</strong>` 或 `.lgnd` 小 chip，
  **不要**用真 `<span class="badge">`，以免被核验门计成无据徽章）。
- TOC lists `第 1 题 / 第 2 题 / …` (one `.toc-l1` per problem). Cycle section colors per problem or per group.

---

## 3. Figure decision — embed the original vs. draw SVG (the core rule)

> **The first question is NOT "is the figure simple?" — it is "did the problem come with a figure of its own?"**
>
> **Did the problem come with ANY figure — a textbook/worksheet figure, photo, scan, plotted graph, circuit, mechanism, OR even a simple line sketch (block on incline, cam + follower)? → embed the ORIGINAL image. Do NOT redraw it as SVG, even if it looks simple.** A redraw routinely **drops a key element** (a flat-top 导板 silently becomes a bare rod, so the student can't tell what's pushing the block) or **misplaces labels** (overlapping `N`/`mg`/`α` on a tilted free-body). The faithful original is always safer and costs nothing — an SVG redraw of a figure you already have is pure downside.
>
> **Draw inline SVG ONLY when the problem has no figure of its own** — a text-only problem, or a diagram you're adding purely to make a concept easier to grasp. Then keep it minimal and faithful; if you can't reproduce the setup faithfully, **describe it in words instead of shipping a wrong figure.**

Decision:
- **Embed the original** (Section 4) if the problem came with a figure of **any** kind — photo, scan, screenshot, data plot, circuit, mechanism, map, **or a simple line drawing**. If it was in the source, embed it; do not "improve" it into SVG.
- **Draw inline SVG** only if **ALL** are true:
  - [ ] The problem came with **no figure of its own** (it's text-only, or the diagram is your own aid for a concept, not a reproduction of a given figure).
  - [ ] A diagram genuinely helps the reader.
  - [ ] You can reproduce the setup **faithfully** and simply with the SVG-safe-subset in `design-system.md` — and you've rendered the file and eyeballed it (labels placed, nothing overlapping, every part the problem mentions actually drawn).
- If you can't draw it faithfully → **describe it in words.** Never omit a figure the problem depends on, never invent a figure that wasn't given, and **never ship an SVG that contradicts the problem.**

---

## 4. Embedding the original figure (standalone, base64)

The HTML must remain a single self-contained file, so embed images as base64 data-URIs (no external `src`).

**Option A — crop straight from a PDF page** (best when the source is a PDF). A **scanned textbook has no text layer**, so first OCR-**locate** the page, then **autocrop** the figure by its caption — the bbox is *detected* (column gutters + the figure's own 图X.Y caption + tighten-to-ink), never hand-typed:

```bash
# 1. find which page the problem is on (a scanned book can't be grepped):
python3 scripts/extract_pdf.py locate textbook.pdf 劳埃德 洛埃 --pages 2-40
# 2. list the figures on that page, then auto-crop one by its caption:
python3 scripts/extract_pdf.py autocrop textbook.pdf --page 3 --list
python3 scripts/extract_pdf.py autocrop textbook.pdf --page 3 --caption "图4.4" -o fig_q3.png
python3 scripts/embed_images.py datauri fig_q3.png      # prints: data:image/png;base64,iVBORw0...
```

> **Why not type the bbox by hand?** An eyeballed `--bbox` is exactly what clips half a figure (a source point, a `2a` label) — the same eyeball error as paraphrasing a figure's geometry (§3). `autocrop` removes the guess. Fall back to the hand-bbox `crop` below **only** when the figure has no 图X.Y caption to anchor on (a bare photo, a non-textbook scan):

```bash
# fallback — hand-specified fractional bbox (x0,y0,x1,y1 from the top-left), no caption to anchor:
python3 scripts/extract_pdf.py crop homework.pdf --page 2 --bbox 0.08,0.18,0.92,0.52 -o fig_q3.png
```

**Option B — from a photo/PNG/JPG the user uploaded**:

```bash
python3 scripts/embed_images.py datauri /path/to/photo.jpg
```

Paste the printed string into the `src`:

```html
<div style="text-align:center;margin:12px 0;">
  <img src="data:image/png;base64,iVBORw0KGgo..." alt="第3题图"
       style="max-width:100%;border:1px solid var(--border);border-radius:8px;">
</div>
```

**Option C — write `<img src="fig_q3.png">` first, inline everything at the end**: keep local file refs while drafting, then run once before presenting:

```bash
python3 scripts/embed_images.py inline final.html   # replaces every local <img src> with base64 in place
```

Image hygiene:
- Add `style="max-width:100%; border:1px solid var(--border); border-radius:8px;"` so figures never overflow and match the design.
- Always give a meaningful `alt` (e.g. `第3题图`).
- Crop tightly to the figure; don't include surrounding problem text in the crop (the text is already transcribed above the image).
- Prefer PNG for line art/diagrams; JPG is fine for photos. Keep crops ≤ ~1600px wide to keep the file small.
- **A clean crop prevents mis-reading the figure; an x-verify catches it if you still do.** If you transcribed any number/geometry off the figure to solve, add a `<script type="text/x-verify">` block that re-derives a quantity the problem already prints (a range, a count, a stated answer) from your read values — see the `workflow-orchestration.md` checklist. (劳埃德镜: reading the mirror as 20cm-not-30cm recomputes **15** fringes, not the printed **33** → the gate FAILs the mis-read, no human review needed.)

---

## 5. MODE B — homework as a worked-example card

In MODE B the homework problem lives **inside the concept section that teaches it**, as a collapsible worked example (not a standalone problem card). Same figure rule applies.

```html
<div class="card">
  <h3 id="s2-3-ex">应用：作业题精讲</h3>
  <div class="example-block">
    <div class="example-header">
      <span class="badge b-amber">作业 3</span> 两滑块完全非弹性碰撞
    </div>
    <div class="example-body">
      <p>质量 $m_1=2\,\text{kg}$ 的滑块以 $v_0=3\,\text{m/s}$ 撞上静止的 $m_2=4\,\text{kg}$ 并粘连，求共同速度与能量损失。</p>
      <!-- figure here if any (SVG or embedded <img>) -->
      <details>
        <summary>解答与思路</summary>
        <div class="details-body">
          <p><strong>思路：</strong>先判定碰撞类型→选守恒律→列式→检验。</p>
          <div class="fbox"><div class="frow">$$m_1 v_0=(m_1+m_2)v$$</div></div>
          <div class="answer-box"><p>$v=1\,\text{m/s}$，$\Delta E=6\,\text{J}$</p></div>
        </div>
      </details>
    </div>
  </div>
</div>
```

Difference from MODE C: the summary may say `解答与思路`, and the solution should **point back to the concept just taught** ("用刚才 §2.3 的动量守恒") so the problem reinforces the lesson. End the chapter with a `本章习题自测` card listing each 作业 题 + a one-line `考点` tag.

Same as MODE C, the **每步讲清「为什么」铁律 + 解答呈现规范 (SKILL.md §0.6)** applies here too: 步骤要细、
每步先加粗"做什么"再融入式讲"为什么"（不用生硬的 `.why` 标签框）、**每个公式配 `.fnote`**、点名所用原理
（能链就链到本章对应小节）、每题带「直觉 + 易错」二件套（不要读者侧「检验」框），no 显然/易得 跳步。范本：《理论力学·动力学作业详解》。
