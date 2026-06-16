<div align="center">

# study-notes | 考前想收藏的那一个 HTML

> *「问 AI 一个知识点，得到的是一坨纯文本；公式是源码、推导铺一整屏、手机上还糊成一片。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-study--notes-blueviolet)](SKILL.md)
[![skills.sh](https://img.shields.io/badge/skills.sh-Eric6286%2Fstudy--notes-ff4d4f)](https://skills.sh/Eric6286/study-notes)
[![ClawHub](https://img.shields.io/badge/ClawHub-eric6286%2Fstudy--notes-7c3aed)](https://clawhub.ai/eric6286/study-notes)
[![Runtime](https://img.shields.io/badge/Claude%20Code-ready-blue)](https://claude.com/claude-code)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**把一章课本或一份作业，变成考前就想收藏的那一个 HTML——KaTeX 数学、彩色分区、可折叠推导，每道题都盲解双算核验过。**

[看效果](#效果示例) · [安装](#快速开始) · [触发方式](#触发方式) · [和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界)

</div>

---

![study-notes hero：电脑端 + 手机端真实产物，KaTeX 公式、彩色分区、可折叠推导](assets/hero.png)
<sub>主视觉由 `scripts/make_hero.py` 用真实运行截图合成，非设计稿。完整产物见 [examples/](examples/)。</sub>

---

## 它解决什么问题

你让 AI 讲过一个知识点吗？它给你一段散文：概念是对的，公式是 `\frac` 的源码，推导从第一行铺到最后一行没法收起，例题和正文混在一起，手机上一行公式横着溢出。你想要的其实是一份**能直接当复习资料的成品**——而不是又一坨要你自己再排版的文本。

这个 skill 换了一个思路：**笔记不是写出来的，是搭出来的。** 它按输入分三种模式，跑一个四段工作流——**先规划**（读源、建目录、定一份共享规范：符号表、配色、数学规则），**再分发**（一个概念一节、各自写深，而不是一遍过把十个概念糊在一起），**重点是核验**（每道例题/每道作业题先解一遍，再**只看题面盲解一遍**，非平凡的数都用 `python`/`sympy` 算，两路答案不一致绝不交付），**最后才组装**并做一致性收尾。

产出是**一个自包含 HTML 文件**：KaTeX 把每个公式排好，推导收在可折叠块里、想看再点开，章节按概念配色，例题/常见错误/考试重点各有 callout，目录分层、侧边浮动导航跟随，手机上零横向溢出。考完还能翻，不依赖任何账号或订阅。

## 效果示例

**输入**（一句话，真实 eval prompt）：

```text
帮我做一份大学物理《热力学第一定律》的复习笔记，期末要用——内能、各种过程的功和热、
绝热过程、卡诺循环都要讲清楚，每个概念配直觉解释、公式推导和例题。
```

**输出**（真实产物的滚动演示 + 三个截面）：

![study-notes 滚动演示：主题头 → 考点框 → KaTeX 公式 → 例题与答案框](assets/demo.gif)

| 分层目录 + 彩色分区（MODE A） | 公式框 + 例题 + 答案框（MODE B） | 手机端 |
|---|---|---|
| ![toc](assets/toc-desktop.png) | ![examples](assets/examples-desktop.png) | ![mobile](assets/mobile.png) |

注意截图里的细节：摄氏度、单位点乘这些符号**写进数学里很容易静默失败**——浏览器不报错，但 KaTeX 会吞字或错排（`$27°C$` 里的裸 `°`、`J/(mol·K)` 里的裸 `·`）。这个 skill 把这类坑全收进了一个静态校验器，交付前必须 PASS；上面 MODE A 那篇实测 **3177 个公式、0 渲染错误**，三个样张 `build_and_check` 全过。

**对照实验**（10 项自动检查，真实产物 vs 无 skill 基线，[完整数据与复现命令](evals/benchmark.md)）：

| 配置 | 自动检查 | build_and_check | 裸 Unicode | 分层目录 | 可折叠解答 | 彩色分区 |
|---|---|---|---|---|---|---|
| **with skill**（3 个真实产物） | **10/10** | 全过 | 0 | ✅ | ✅ | ✅ |
| baseline（无 skill） | 4/10 | **FAIL** | 3 处 | ❌ | ❌ | ❌ |

成本如实说：with-skill 明显更费 token——这是"规划→分发→**核验**→组装"工作流加完整排版构建的价格，换来的是一份校验干净、能直接复习的成品，而不是一次性的一段文字。

## 快速开始

一行安装（推荐）：

```bash
npx skills add Eric6286/study-notes
```

或手动克隆：

```bash
git clone https://github.com/Eric6286/study-notes ~/.claude/skills/study-notes
```

装完对 Claude Code 说（可直接复制）：

```text
帮我做一份《刚体定轴转动》的复习笔记，配推导和例题
```

无前置依赖、零 API key：数学用 KaTeX（CDN，免 key），读 PDF 用自带的 `scripts/extract_pdf.py`（首次会装 `pymupdf`）。

> **提效小贴士：** 如果输入是扫描版 PDF 或作业照片，先把图片备好；带题目图的作业，简单图会重画成 SVG、复杂图/照片会原样嵌进 HTML（仍是单文件）。想要"只整理公式、精简版"也可以直接说。

## 触发方式

- 帮我做一份 X 的学习笔记 / 复习笔记
- 帮我把这章 PDF 整理成复习笔记（附讲义/课本 PDF）
- 用这几道作业题帮我把这一章重新过一遍
- 给我这套题每道的详细解答，我想对答案
- make me study notes on X / summarize X for an exam
- help me learn X — intuition, derivations, worked examples

## 它会交付什么

一个自包含 HTML 学习件，按模式不同包含：主题化头部 + 分层目录（章/节两级、彩点）+ 侧边浮动导航；每个概念一节、按概念配色，结构为 直觉 → 严格定义（公式框）→ 推导（可折叠）→ 特殊/极限情形 → ≥2 例题 → 常见错误 → 考试重点；KaTeX 数学（摄氏度/单位点乘等走预注册宏，数学 span 内零裸 Unicode）；作业题作为可折叠 worked-example 嵌进对应概念节、或整卷逐题全解，**每个答案经盲解双算核验、标「已核验 ✓」**；手机端适配；交付前过静态校验器。

三种模式：

- **MODE A** — 课本/讲义 PDF（或一个主题）→ 整章学习笔记
- **MODE B** — 几道作业题 → 反推考点、出对应章节的完整学习笔记（作业题嵌为 worked example）
- **MODE C** — 一份作业 → 每道题逐题全解（题面始终可见、解答折叠，先做后对）

## 它和同类有什么不同

公开生态里，"把题目/PDF 变成考试向单文件 HTML + KaTeX" 这个精确组合几乎没有正面竞品——同类要么输出 Markdown、要么要二次编译、要么锁在平台账号里：

| 维度 | 同类常见做法 | 本 skill |
|---|---|---|
| 产物形态 | Markdown 文本（[paper-distiller](https://github.com/2j1ejyu/paper-distiller)、[obsidian-notes-creator](https://github.com/szeyu/vibe-study-skills)、[ppt-to-notes](https://github.com/rutulpatel07/ppt-to-notes)） | 单文件 HTML，KaTeX 精排、彩色分区、可折叠、深色模式 |
| 数学排版 | 纯文本/源码，或要 Overleaf 编译（[cheatsheet-generator](https://github.com/Evan715823/cheatsheet-generator-skill)） | 浏览器即开即读；KaTeX 渲染；**裸 Unicode 静态校验把关** |
| 答案正确性 | 一次生成、不复核 | **盲解双算 + 代码验算**，两路一致才标「已核验 ✓」 |
| 作业支持 | 多为笔记/闪卡（[deckhand](https://github.com/F1veYearPlan/deckhand)） | 三模式，含逐题全解；作业题嵌为可折叠 worked example |
| 依赖/所有权 | 平台账号 + 订阅（NotebookLM / Knowt / Turbo AI） | 零依赖、零注册，一个 HTML 永久归你、可离线 |

## 安全边界

- **帮你学会，不是帮你交差。** 解答默认**折叠**——题面先可见，你先做、再点开对答案；built to learn, not to hand in。
- **不编公式、不编答案。** 给了课本/讲义就按那一章的方法、引用公式编号；每个非平凡的数用 `python`/`sympy` 算过，答案盲解双算两路一致才标「已核验 ✓」，不一致绝不交付。
- **不做静默失败。** 交付前跑 `scripts/build_and_check.py`：裸 Unicode 进数学、`<div>` 失衡、`\boxed` 套在公式框里这类浏览器不报错的坑，FAIL 即阻断、改干净才出。
- **不碰你的文件**：只在你指定的目录写一个 HTML，不删不改别的东西；无外部请求、不要任何凭据。

## 文件结构

```
study-notes/
├── SKILL.md                          # 多分支工作流：PDF→笔记 / 作业→章节笔记 / 作业→全解
├── references/
│   ├── design-system.md              # HTML 输出规范（CSS/JS 模板 + 全部组件 + KaTeX 规则）
│   ├── workflow-orchestration.md     # plan→fan-out→verify→assemble + 盲解双算核验清单
│   ├── problem-solutions.md          # 作业题→HTML：题面/图/折叠解答、SVG vs 嵌原图
│   └── lessons-learned.md            # 活体登记册：真实失败→根因→规则→对应检查→日期
├── scripts/
│   ├── build_and_check.py            # 输出静态校验（裸 Unicode / div / $ / 禁用命令，宏感知）
│   ├── test_build_and_check.py       # 校验器自身的回归测试（锁住宏感知修复）
│   ├── extract_pdf.py                # PDF 取文字/渲染页/裁图
│   ├── embed_images.py               # 图片 base64 内联，保持单文件自包含
│   └── make_showcase.sh              # 从真实产物重生成 README 截图/GIF（可复现）
├── evals/
│   ├── evals.json                    # 3 个标准测试 prompt（MODE A/B/C）+ 期望输出
│   ├── benchmark.md                  # with/without skill 对照 + 语料证据
│   ├── check_features.py             # 10 项特征自动检查电池
│   └── baseline_sample.html          # 无 skill 基线样本（对照用）
├── examples/                         # 三个真实运行产物，每模式一个
└── assets/                           # README 截图/GIF（全部出自真实产物）
```

## 验证与测试

拿 [evals/evals.json](evals/evals.json) 里的 prompt 跑一遍，合格产物应当一次通过两道门：

```bash
python scripts/build_and_check.py check <输出>.html    # 静态正确性（裸 Unicode / div / $ / 禁用命令）
python evals/check_features.py <输出>.html             # 10 项结构+正确性特征，应 10/10
```

校验器为什么可信：它对模板**宏感知**——你注册成宏的命令（`\celsius`/`\unit`/`\bm` 等）不会误报，没注册却裸用的才拦；这条由 `scripts/test_build_and_check.py` 锁死。对照实验方法与数据见 [evals/benchmark.md](evals/benchmark.md)。

## 更新记录

- **2026-06-16 · v0.4** —「已核验」从「凭证计数」升级为「可执行门」。
  - **为什么还要改**：v0.3 的凭证门是**静态计数**——只能证明「写了一条 `<!-- verify -->` 凭证」，证明不了「凭证内容为真」。模型仍可能编一条看起来对的凭证；根因是自评与答案同源、同样不可靠（同一上下文里「盲解双算」也不盲）。
  - **怎么改**：把盖章权从模型交给脚本。新增 `scripts/verify_helpers.py` + `scripts/verify_solutions.py`——每道可机检的题带一个隐藏 `<script type="text/x-verify">` 块，用 sympy **从题面给定量重算**并 `assert` 等于印出的答案（`check_derivative/integral/equal/consistent/limit/numeric`）；`verify_solutions.py` 把每个块真跑一遍，**只有 PASS 才配 `已核验`**，否则标 `未自动核验`（新增弃答徽章）。新增 Check 5；`build_and_check.py` 认 x-verify 块为工件。
  - **实测**：那道曲柄连杆题（v0.3 的起因）现在被脚本实测拦下——`recomputed = l·ω²(cosωt+λcos2ωt)` ≠ `claimed = -l·λ·ω²(…)`，exit 1，徽章不予放行。
  - 新增 `test_verify_solutions.py`（8/8）；`build_and_check` 9/9 仍过。诚实边界：x-verify 块仍由模型撰写，对「自信但非对抗」的失败模式已足够；若出现刻意自我作弊（`check_equal(claimed,claimed)`），再加「重算必须源自 given」的结构校验。

- **2026-06-15 · v0.3** — 真机核验修四处缺陷：移动端溢出、暗色撞色、假「已核验」、静默坏宏。
  - **暗色模式对比度**：暗色 `:root` 原先只覆盖 `*-light` 背景，`*-dark` 文本与基础强调色仍是亮色值 → 徽章/标题/做题选项暗底暗字（实测 teal-dark/teal-light 仅 1.46:1）。补齐暗色强调色 + `*-dark`，实测回到 6.8–9.9:1；并加「图/流程图框文字禁与填充同色」规则。
  - **宽公式溢出（改为全宽生效）**：首版只在 ≤600px 触发是错的——溢出取决于「公式宽 vs 框宽」、与视口无关。改为 `.katex-display{overflow-x:auto;overflow-y:hidden}` 任意宽度都在框内横向滚动（y:hidden 既不裁高也不劫持页面竖向滚动），换主题细滚动条（thumb=`--text2`，过 WCAG 3:1，去系统箭头），仅给真正溢出的公式/表格加 `tabindex` 可键盘滚；prose 全局 `overflow-wrap`。
  - **「已核验」必须凭证**：以前 badge 是装饰、算错也照标。现在每个 `已核验` 必须配一条 `<!-- verify: … -->` 独立复算凭证，否则 `build_and_check.py` 的 `check_verified_badges` FAIL；微分/积分一律走 sympy 禁手算（起因是一道曲柄连杆题：对给定 x(t) 心算二阶导，符号与系数全错却标了已核验）。
  - **修两个静默坏宏**：`\bm`、`\unit` 旧定义用花括号包住「参数来自外部」的命令，使 `\bm{F}`/`\unit{m/s}` 渲染成 KaTeX「Extra }」报错（`\bm` 还是推荐的向量加粗写法）；改为裸别名，新增 `check_broken_macros` 守门。
  - 真 KaTeX 多断点（620/720/780）× 暗/亮实测 + WCAG 对比度脚本 + 对抗式 CSS review；`test_build_and_check.py` 9/9 通过。

- **2026-06-14 · v0.2** — review-my-skill 打磨：触发更准 + 渐进披露重构。
  - **触发更准**：description 收紧到 916 字（原 1005），补负向触发（课件考点速查走 summarize-slides、业务报告走 visual-report）；`evals/` 新增触发测试段，6 条该触发的正例 + 5 条该让路的负例。
  - **渐进披露**：`SKILL.md` 正文从 493 行压到 375 行。把「写代码时本来就要先读」的 CSS、HTML 模板、内联校验片段（选学徽章、图引用、例题卡、KaTeX `<head>`、分层 TOC 标记、Check 2 扫描）全部收进 `design-system.md` 作单一真相，正文只留规则和指针；数学里裸 Unicode 那条铁律仍留正文。
  - **更易读**：三个超过 100 行的参考文件各补一个 `## Contents` 目录，部分读取也能看到全貌。
  - **持续学习**：新增 `references/lessons-learned.md` 活体登记册（症状→根因→规则→对应检查→日期），约定每次真实翻车补一条；`SKILL.md` 补跨环境提示（本地 `python3` 即 `python`、无 `present_files` 就报输出路径）。
  - 回归测试全过（`build_and_check` / `fix_math` / `make_anki`），三样张 `check_features` 仍 10/10。

- **2026-06-13 · v0.1** — 冻结基线 + 出师打包。
  - **校验器宏感知修复**：`build_and_check.py` 原先把模板合法宏 `\celsius`/`\unit` 当禁用命令误报（在它们的注册行上）。改为宏感知：文件注册过的宏不报、裸用未注册的才拦。真实语料回放：**7 个假阳性 FAIL→PASS，0 个真 bug 漏网**，由 `test_build_and_check.py` 锁死。
  - **修 SKILL.md 截断 + 文档自洽**：补全中途截断的结尾；`\celsius`/`\unit`/`\bm` 在"禁用表/可用宏表"之间的矛盾统一——文档、模板、校验器三者一致。
  - **出师打包**：补 README、`evals/`（3 用例 + benchmark + 10 项电池）、`examples/`（每模式一个真实产物）、`assets/`（成品截图/GIF）、`scripts/make_showcase.sh`（可复现展示素材）、LICENSE。
  - 基线能力：三分支工作流（PDF→笔记 / 作业→章节笔记 / 作业→全解）+ 976 行设计系统 + plan→fan-out→**verify**→assemble + 盲解双算核验。

## 致谢

- 这套 HTML 视觉/排版规范是本仓库的设计系统原生地——同作者的 trip-planner skill 的视觉规范即脱胎于此。

## License

[MIT](LICENSE)

---

<div align="center">

*能直接复习的才叫笔记，要你再排一遍的叫草稿。*

</div>
