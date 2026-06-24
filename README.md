<div align="center">

# study-notes | 考前想收藏的那一个 HTML

> *「问 AI 一个知识点，得到的是一坨纯文本；公式是源码、推导铺一整屏、手机上还糊成一片。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-study--notes-blueviolet)](SKILL.md)
[![skills.sh](https://img.shields.io/badge/skills.sh-ErikaAlk%2Fstudy--notes-ff4d4f)](https://skills.sh/ErikaAlk/study-notes)
[![ClawHub](https://img.shields.io/badge/ClawHub-ErikaAlk%2Fstudy--notes-7c3aed)](https://clawhub.ai/ErikaAlk/study-notes)
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
npx skills add ErikaAlk/study-notes
```

或手动克隆：

```bash
git clone https://github.com/ErikaAlk/study-notes ~/.claude/skills/study-notes
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

- **2026-06-24 · v0.8.2** — Check 6 审查**整篇**笔记（不只例题），并把「教科书级严谨」前移进生成指导。
  - **审查范围放宽到全文**：Check 6 的 codex 角色从"解题审查者"改为"学习笔记审查者"，明确通读**整篇**——知识点介绍、概念讲解、定义/定理、推导、正文叙述、图都审，不再只盯例题/解答；判错标准对概念讲解与例题解答一视同仁。
  - **严谨约束前移**：「教科书级严谨」原先只写在审查门（Check 6 的第 ⑥ 项），现在也写进**生成指导**——`Content Structure` 新增 *Rigor standard* 小节 + 强化"严格定义"条，让 Claude 第一遍就按教科书级严谨写，而不是等 Check 6 打回来反复返工，省时省 token。生成与审查用同一套标准（单一真相）。改 `SKILL.md`。

- **2026-06-24 · v0.8.1** — Check 6 审查清单补一条：要求**表述达到教科书级严谨**。
  - codex 通读时，除概念/逻辑/公式-中文/图文外，再查第 ⑥ 项：定义、定理、条件与结论的陈述是否**精确完整**（前提、适用范围、正负号、边界不缺不含糊）、术语与记号是否规范统一、有无口语化或似是而非的断言——直觉铺垫可通俗，正式定义与结论必须严谨。改 `SKILL.md` 的 Check 6 prompt。

- **2026-06-24 · v0.8** — 收尾新增「外部交叉审查门」：成品交给第二个模型（codex）通读，抓 sympy 查不出的概念/逻辑/图文错。
  - **为什么**：Checks 1–5 全是机械/符号层——`build_and_check.py` 管渲染与裸 Unicode，`verify_solutions.py` 用 sympy 从给定量重算**数值**。但有一类错它们**结构上**看不见：数算对了、中文解释却写反。用户实例：一道「开气隙磁心有效磁导率」，$R_{m0}=(l_1+l_2)/(\mu_0 S)$ 分明是「同尺寸**全真空**」的磁阻、$\mu_e\approx91$ 也算对，正文却把 $R_{m0}$ 说成「同尺寸**全铁心**时磁阻」——sympy 只会确认 91 没错，看不出文字与公式自相矛盾。
  - **怎么改**：新增 **Check 6 外部交叉审查**——把最终 HTML 交给第二个模型（OpenAI **codex**，经其 MCP server）只查「①概念/物理是否真对 ②步骤逻辑是否自洽 ③每处公式与中文说明是否一致 ④图与题/文是否相符 ⑤量纲与特例」这些**符号计算查不出**的问题；主控（不是 codex）逐条裁决，改掉真错并**重跑 Check 2–5**，误报记一笔。codex 的审查**不授予**「已核验」徽章（徽章仍由 `verify_solutions.py` 把关），只能提示订正或降级。
  - **优雅降级**：仅当 `mcp__codex__codex` 工具可用（已配 codex MCP server）才跑，否则一行说明跳过、绝不阻断——没装 codex 的用户照常出片。一次性启用：`claude mcp add codex -- codex mcp-server`（Windows 把非 PATH 的二进制用 `cmd /c` 包一层，codex 需已登录）。
  - **实测**：对上面这道磁心题，codex 准确指出「$R_{m0}=(l_1+l_2)/(\mu_0 S)$ 是全真空磁阻、不是全铁心」「若真按全铁心代入，比值应 $\approx0.091$ 而非 91」「错只在中文定义、最终公式与 91 没问题」——正是机械门看不见、读者才察觉的那一层。同步成文：SKILL.md（Check 6 + 工作流步骤）、`references/lessons-learned.md`。

- **2026-06-16 · v0.7.1** — 图规则收紧：源里有图就用原图，别重画 SVG。
  - **用户实测两类翻车**：①例6 偏心轮把「平顶导板」画成了一根杆子（漏关键结构，得对着原题图才看懂）；②斜面圆盘受力图标签（$N$/$mg$/$\alpha$）糊在一起、偏移离谱。根因：旧图规则「简单图 → 画 SVG」留了个口子——模型把本来有原图的题判成「简单」去重画，必然丢元素/标签错位。
  - **新规则**：**第一问不是「图简不简单」，而是「题目本身有没有图」**。源里有图（课本/作业图、照片、扫描、曲线、电路、机构，甚至简单线条图）→ **一律嵌原图**（base64），**再简单也绝不重画 SVG**——重画只有丢元素/标签错位的下行风险、没有上行收益。**只有题目自己没图**（纯文字题，或纯为讲概念加的示意图）才画 SVG，且必须忠实、出图前渲染肉眼看；画不忠实就改用文字描述，绝不交付与原题矛盾的图。写进 `SKILL.md`（MODE B B4 + MODE C 图规则）、`design-system.md`（SVG 段首「先问该不该画」）、`problem-solutions.md` §3（决策规则重写）。
  - **修了例6 展示图**：重画成忠实的「平顶导板 + 偏心轮」——A 坐在导板平顶上、导板在铅直轨道里上下、偏心轮顶推导板平底，$O$/$C$/$e$/$R$/$\omega$ 标注清楚，$F_N$/$mg$ 不再与结构重叠；真机渲染肉眼核过。

- **2026-06-16 · v0.7** — 三个示例的**每一道题**都带上可执行「已核验」（共 109 个 x-verify 块）。
  - **从"部分"到"全部"**：v0.5.1 只让 MODE-B 的 17 道纯微积分题真核验，MODE-A 力学题与 MODE-C 概念题还停在「未自动核验」。本轮按用户要求把**所有题目**（含「本章自测」练习题与速查）都补上从给定量重算的 `<script type="text/x-verify">` 块：**MODE-A 72 + MODE-B 17 + MODE-C 20**，`verify_solutions.py` 三个文件 **109/109 PASS**，再无一个装饰性或散文式核验声明。
  - **力学题怎么机检**：把题解里写明的**治理方程**（牛顿第二定律 / 定轴 $J\alpha=\sum M$ / 动量·动量矩守恒 / 动能定理 / 虚位移 $\delta W=0$ / 达朗贝尔动静法）用 sympy 联立**重解**再与印出答案比对——是真重算，不是把答案抄成两边。连"机械能是否守恒"这类判断题也机检了：对光滑/粗糙/纯滚/打滑四种过程**重算摩擦力做功**（为零＝守恒、为负＝不守恒）。
  - **概念选择题（MODE-C 20 题）怎么机检**：每题**重算决定正确选项的关键量**——原点偏导用极限定义、隐函数二阶偏导、全微分相容条件 $P_y\stackrel?=Q_x$、连续性用路径/极坐标极限、二阶判别式、截痕切向量、对数求导 $x^y=y^x$、定义域不等式——并用**计算出的反例**否掉干扰项，确认键控答案。纯「详见例 N」的速查条目标 `已核验 ✓` 指向已验证例题，不重复写块。
  - **可执行门跨平台修复**：`verify_solutions.run_block` 现在**强制子进程 UTF-8 stdio**（`PYTHONIOENCODING=utf-8` + `encoding='utf-8'`）。此前在 GBK/CP-936 控制台（本机 Windows），检查名里只要带 `²ω√π` 之类非 GBK 字符，子进程 `print` 就抛 `UnicodeEncodeError`、整块被误判失败。`test_verify_solutions` 加一条 unicode 检查名用例锁死，9/9→**10/10**。
  - **核验顺带抓出两处印刷错误并修正**：①例1 滑块运动方程显示式外层系数 `l` 应为 `r`（对其求二阶导才给出印出的 $a_x=r\omega^2(\cos\omega t+\lambda\cos2\omega t)$）；②浮动起重船数值 `-0.318` 与它自己的公式（代入实为 `+0.318`）自相矛盾的符号笔误——这正是可执行门的价值：算一遍就露馅。
  - 工作流：12 个并行子代理分别核验 MODE-A 的 43 例题与 28 自测题（每块先经真 `verify_solutions` 跑通才回传），主控亲写并整合 MODE-C 20 题；四份副本同步、`test_build_and_check` 18/18。

- **2026-06-16 · v0.6** — 大笔记性能修复（展开解答不再卡顿）+ 核验徽章绿/琥珀高亮。
  - **展开解答卡几秒（每次都有）**：一篇 3000+ 公式的笔记 DOM 达 15.5 万节点、页面约 7.3 万像素高；展开一个 `<details>` 会让浏览器重排+重绘整页，在用户机器上 GPU 重绘约 10 秒（鼠标卡顿）。无头实测单次展开布局仅 ~8ms，说明瓶颈是**整页绘制**而非脚本死循环。两刀修复：①`renderMathInElement` 加 **`output:'html'`**——KaTeX 不再生成隐藏的 MathML 孪生节点，**DOM 15.5万→11.4万（−26%）**，公式照常渲染、0 报错；②`.card,.example-block` 加 **`content-visibility:auto`**——浏览器跳过屏幕外块的布局/绘制，**整页重排 43.8ms→1.3ms（−97%）、展开 0.4ms**。用户真机确认：加上即完全不卡。代价：超长笔记的滚动条位置/"记住阅读位置"变估算值，故把滚动恢复 `doRestore` 改成 **CV 感知**（逐帧 `scrollTo` 重试到位，估算高度长高后再逼近）。
  - **核验徽章高亮**：新增 **`.b-verified`**（绿色底框，已核验＝可执行门通过）；`.b-unverified` 由灰虚线改 **琥珀色底框**（未自动核验＝弃答，可能仍对、只是没机检——用"提醒"色而非红色，不暗示答错）。MODE-B 17 个已核验徽章换 `b-verified`、MODE-A 43 个未核验徽章自动变琥珀。徽章计数正则照旧匹配（`class="badge …">已核验`），三示例双门仍全绿（MODE-B 17/17）。
  - 真机 Chromium 实测：output:html→MathML 0、0 报错、公式 382 全渲染；CV 生效、展开 0.4ms；绿/琥珀徽章底色正确。回归 `test_build_and_check` 18/18、`test_verify_solutions` 9/9。

- **2026-06-16 · v0.5.1** — 三个展示示例补齐「已核验」可执行门，徽章计数收紧到只数徽章不数散文。
  - **根因两层**：①`check_verified_badges` 旧用裸正则 `re.compile("已核验")` 计数，把**正文散文**（"所有解答都做了独立核验（已核验 ✓）"）、CSS/JS 注释、图例里的徽章演示也算成徽章 → 计数虚高、误伤；②MODE-A/B 两个示例用的是**装饰性**「已核验 ✓」（MODE-A 还是 `style=` 的山寨 span），没有配套的可执行 `<script type="text/x-verify">` 块 → `build_and_check` 与 `verify_solutions` 双双 FAIL（MODE-A 74、MODE-B 20，均「badge 数 > 工件数」）。
  - **怎么改**：徽章计数收紧为只匹配**徽章元素** `<span class="badge …">已核验`（`build_and_check.py` 与 `verify_solutions.py` 两处正则**逐字一致**，免得一边过一边挂）；散文/注释/图例不再计入。图例改用 `<strong>` 而非真徽章 span。
  - **MODE-B（重积分应用 + 含参积分，纯微积分）**：给 17 道题各补一个 x-verify 块，用 sympy **从题面给定量重新积分/求导**再与印出答案逐一比对——曲面面积、质心、转动惯量、半圆环引力、含参积分极限、莱布尼茨求导、费曼对参数微分法（费曼/换序题用 `tan` 代换、`conds='none'`、`laplace_transform` 规避分支/Piecewise/超时）。17/17 真跑 PASS，徽章名副其实，成为 v0.4 可执行门的活样板。
  - **MODE-A（动力学，需建受力模型）**：这些题要画受力图、自选方程，不适合纯符号机检；43 个装饰徽章 + 全部散文「已核验」诚实降级为 `未自动核验`（设计系统规定的弃答徽章，新增 `.b-unverified` 样式），不再冒充已验证。MODE-C 本就干净。
  - **结果**：三个示例现在都干净通过 `build_and_check.py check` 与 `verify_solutions.py`。测试：`test_build_and_check.py` 18/18（+2 例锁定散文不计、徽章元素计一次）、`test_verify_solutions.py` 9/9（+1 例锁定散文不冒充徽章）；`fix_math`／`make_anki` 回归全过。SKILL.md Check 4 与 design-system.md「已核验 EXECUTABLE gate」同步「只数徽章元素」规则。

- **2026-06-16 · v0.5** — 移动端例题头排版修复 + SVG 防偏移安全子集。
  - **移动端例题头裂成竖排乱码**：`.example-header` 原是 `display:flex; flex-wrap:nowrap`，标题里只要夹着行内 KaTeX（`$v$`）、`<strong>`、行尾 `已核验` 徽章，每段裸文本就各成一个**匿名 flex item**，窄屏下各自 `flex-shrink` 到 min-width → 中文标题碎成好几条竖列（例3「圆锥摆求小球速度 v 与绳张力…」在 380px 实测复现）。改为 `display:block` 行内流，badge＋文字＋公式＋尾标作为一条普通行自然换行；保留 `writing-mode:horizontal-tb!important` 守竖排回归，徽章 `vertical-align:middle` 居中。真机 380px A/B 截图实测：旧版裂列、新版两行正常；三处展示示例 + 设计系统四份副本就地同步。
  - **SVG「莫名其妙偏移」**：审了一份 SVG 偏移调研报告——技术诊断属实（viewBox 映射 / 百分比相对最近视口 / CSS-transform 参考框 / 文本基线 / marker refX-refY 五类成因，逐条对 SVG2/MDN 核过）。但审计本技能 47 个真实图发现：5 类成因里**3 类按构造根本不可能**（无嵌套 `<svg>`、无 `%` 几何、无 `transform=`），技能早已"按例子守住安全子集"。于是只**采纳生成约束**、不上重型管线：design-system.md 新增成文的『SVG-safe-subset（避免莫名偏移）』规则 + "出图前渲染并肉眼看"；`build_and_check.py` 新增 `check_svg_offset_risks`（WARN 级，扫嵌套 svg / % 几何 / foreignObject / CSS-transform，favicon 先剥离防误报）。**放弃**报告的 resvg / SVGO 归一化 / 三引擎像素 diff / getBBox 投影——对"单文件 + 少量手绘图、用户端无构建步骤"属过度工程。
  - 测试：`test_build_and_check.py` 16/16（新增 7 例锁定四类命中 + favicon／SVG-attribute 不误报）；三个示例真实语料 `check` 实测 SVG 项 0 误报；`fix_math`／`verify_solutions`／`make_anki` 回归全过。
  - 报告核验与采纳方案用多代理工作流并行完成：逐条对抗式核验报告主张 + 真实 SVG 审计 + 最小采纳方案 + CSS 回归 review。

- **2026-06-16 · v0.4** —「已核验」从「凭证计数」升级为「可执行门」。
  - **为什么还要改**：v0.3 的凭证门是**静态计数**——只能证明「写了一条 `<!-- verify -->` 凭证」，证明不了「凭证内容为真」。模型仍可能编一条看起来对的凭证；根因是自评与答案同源、同样不可靠（同一上下文里「盲解双算」也不盲）。
  - **怎么改**：把盖章权从模型交给脚本。新增 `scripts/verify_helpers.py` + `scripts/verify_solutions.py`——每道可机检的题带一个隐藏 `<script type="text/x-verify">` 块，用 sympy **从题面给定量重算**并 `assert` 等于印出的答案（`check_derivative/integral/equal/consistent/limit/numeric`）；`verify_solutions.py` 把每个块真跑一遍，**只有 PASS 才配 `已核验`**，否则标 `未自动核验`（新增弃答徽章）。新增 Check 5；`build_and_check.py` 认 x-verify 块为工件。
  - **实测**：那道曲柄连杆题（v0.3 的起因）现在被脚本实测拦下——`recomputed = l·ω²(cosωt+λcos2ωt)` ≠ `claimed = -l·λ·ω²(…)`，exit 1，徽章不予放行。
  - 新增 `test_verify_solutions.py`（8/8）；`build_and_check` 9/9 仍过。诚实边界：x-verify 块仍由模型撰写，对「自信但非对抗」的失败模式已足够；若出现刻意自我作弊（`check_equal(claimed,claimed)`），再加「重算必须源自 given」的结构校验。
  - **展示素材刷新**：`examples/` 三个示例笔记按新设计规范（暗色对比度 + 公式/表格细滚动条）就地更新，README 截图与 hero 用 `scripts/make_showcase.sh` 从更新后的真实产物重出（暗色模式下徽章/标题/头部 pills 不再撞色）。

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
