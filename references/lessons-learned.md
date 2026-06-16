# Lessons Learned — the living-document loop

This skill improves through **real usage**, not one-shot authoring. Every time a generated
note/solution is wrong, ugly, or shallow on a real task, record it here as one row, then
**close the loop**: turn the fix into a rule the skill enforces.

## The loop (do this for every real failure)

1. **Observe** — note the symptom on a real run (e.g. "MODE B 又把一道碰撞题算错了").
2. **Root cause** — why did it happen? (no independent check / mental math / wrong method / missed reference).
3. **Distilled rule** — the one-line rule that prevents it, added to the right place in `SKILL.md`
   or a reference (not here — here is just the log).
4. **Linked check** — if it's structurally detectable, add a rule to `scripts/build_and_check.py`
   (and a case to `scripts/test_build_and_check.py`); otherwise add an eval to `evals/evals.json`.
5. **Date** — when you closed it.

> Pro tip from the authoring guide: iterate on **one hard task** until Claude gets it right,
> then extract the winning approach into the skill — don't generalize from guesses.

## Registry

| Date | 症状 (symptom) | 根因 (root cause) | Distilled rule → where | Linked check |
|---|---|---|---|---|
| 2026-06-13 | 旧产物里 `\text{J/(mol·K)}` 静默失败，浏览器不报错 | 裸 Unicode `·` 落进数学 span，KaTeX 默默吞掉 | "数学 span 内只用 ASCII+LaTeX，单位点乘写 `\cdot`" → SKILL.md *Units in KaTeX* | `build_and_check.py check_unicode_in_math` + `fix_math.py` 自动修 |
| 2026-06-13 | `\boxed{}` 包高公式时渲染成空灰框盖住公式 | 容器已有可见框，再嵌 `\boxed` 触发 KaTeX 布局 bug，且不报错 | "禁止在 `.fbox`/`.big-formula`/`.callout` 里用 `\boxed{}`" → design-system.md | `build_and_check.py` grep `\boxed` + Check 3 |
| 2026-06-13 | `\celsius`/`\unit` 被检查器误报为禁用命令 | 检查器不认识模板预注册的宏 | 让扫描 macro-aware：把当前文件注册的宏排除 | `test_build_and_check.py`（4 例锁定，7 个假阳性翻 PASS） |
| 2026-06-13 | MODE B/C 偶发"题做错了" | 解一次就写、从不独立复核；心算多步 | "盲解双算 + 用 python/sympy 重算，两路一致才 `已核验 ✓`" → §0.5 + workflow-orchestration.md | 已升级为静态门（见 2026-06-15「假已核验」行） |
| 2026-06-15 | 公式/长文本在窄屏溢出；首版修复后又暴露两点：①滚动只在 ≤600px 触发、②滚动条是刺眼的系统白条带箭头 | `.katex-display:overflow:visible` 无处理；**首版只用 ≤600px 媒体查询门控**——但溢出取决于「公式宽 vs 容器宽」，与视口无关，700–900px 照样溢出；且没美化滚动条 | "改为**全宽生效**：`.katex-display{overflow-x:auto;overflow-y:hidden}`（y:hidden 既不裁高也不劫持竖向页面滚动）+ 主题细滚动条(thumb=`--text2`，过 WCAG 3:1，去掉 stepper 箭头)+ 仅给真正溢出的元素加 `tabindex` 让键盘可滚；prose 全局 `overflow-wrap`" → design-system.md | 真 KaTeX 渲染多断点(620/720/780)×暗亮实测 + WCAG 脚本核对比度 + 对抗式 CSS review |
| 2026-06-15 | `\bm{F}`、`\unit{m/s}` 渲染成红色报错（KaTeX "Extra }"） | 模板宏 `'\bm':'{\boldsymbol}'`、`'\unit':'{\,\text}'` 用花括号包住「参数来自宏外部」的命令——`\bm{F}` 展开成 `{\boldsymbol}{F}`，`\boldsymbol` 拿不到参数。检查器对已注册宏跳过禁用扫描，静态查不到；仅运行时报错横幅能发现 | "去掉外层花括号、用裸别名：`'\bm':'\boldsymbol'`、`'\unit':'\,\text'`（katex.renderToString 实测两式均 OK）" → design-system.md 模板宏块 | `build_and_check.py check_broken_macros`（命中 `{\boldsymbol}`/`{\,\text}` 宏体即 FAIL）+ `test_*`（9/9）|
| 2026-06-15 | 已经把 sympy / 盲解双算 / 已核验标签都加进工作流，标签也打了，但输出（含过程）还是错的 | 那些机制写在 SKILL.md 里**只是"指令"**，模型用生成文本一并糊弄过去：sympy 没真跑（被"叙述"了）、同上下文里"盲解"不盲（锚定第一遍的错解）、"已核验"只是高概率续写；自评与答案同源、同样不可靠（=報告里的規律 2/3） | "把盖章权从模型移交给脚本：用可执行 `<script type=text/x-verify>` 块以 sympy 从**给定量**重算并 assert == 印出的答案；`verify_solutions.py` 真跑、只有 PASS 才配 `已核验`；不可机检即 `未自动核验` 弃答" → SKILL.md Check 5 + design-system.md「已核验 EXECUTABLE gate」 | `verify_solutions.py`（执行 + badge 门；曲柄连杆错题实测被拦：recomputed≠claimed）+ `test_verify_solutions.py`（8/8）；`build_and_check` 已接受 x-verify 块为工件 |
| 2026-06-15 | 暗色模式下框内文字与底色撞色、几乎看不清 | 暗色 `:root` 只改了 `*-light` 背景，`*-dark` 文本与基础强调色仍是亮色值 → 暗底暗字（实测 teal-dark/teal-light 仅 1.46:1） | "暗色 root 同步覆盖基础强调色 + `*-dark`（实测回到 6.8–9.9:1）；图/流程图框文字禁与填充同色" → design-system.md 暗色 root + SVG 文字对比规则 | 对比度用 WCAG ratio 脚本核过（1.46→6.8+） |
| 2026-06-15 | 二阶导算错、整题答案错，却仍标"已核验"（曲柄连杆题） | 心算微分 + 套用记忆中的"标准答案"，未对给定 x(t) 实算；"已核验"是装饰、无强制 | "已核验须凭证：每个 badge 旁留 `<!-- verify: -->` 记录独立复算；微分一律走 sympy；给定方程求导就对给定式求导" → SKILL.md Check 4 + §0.5 + workflow-orchestration.md 警示案例 | `build_and_check.py check_verified_badges`（badge 数 > verify 工件数则 FAIL）+ `test_build_and_check.py`（7/7） |
| 2026-06-16 | 移动端例题头 `.example-header` 文字裂成竖排乱码（例3「圆锥摆求小球速度 $v$ …已核验✓」在 380px 下碎成多列） | 头部是 `display:flex; flex-wrap:nowrap`，标题里夹着行内 KaTeX `$v$` span、`<strong>`、行尾 `已核验` badge——每段裸文本各成一个**匿名 flex item**，窄屏下各自 `flex-shrink` 到 min-width → 多条竖列。`flex-shrink:0` 只护住了 badge，护不住文字 | "`.example-header` 改 `display:block`（行内流），让 badge+文字+KaTeX+尾标作为一条普通行自然换行；保留 `writing-mode:horizontal-tb!important` 守竖排回归；badge 用 `vertical-align:middle` 居中" → design-system.md `.example-header`。真机 380px A/B 截图实测：旧 flex 复现裂列，新 block 两行正常 | 纯 CSS、对抗式 review 确认无回归（桌面居中/竖排防线/尾标都不变）；比"包一层 span"更稳——任何未来行内内容都不会再变成独立 flex item |
| 2026-06-16 | 三个展示示例 `build_and_check`/`verify_solutions` 双双 FAIL（MODE-A「74 badge / 0 工件」、MODE-B「20/0」）——先于 v0.5、与之无关 | 两层根因：①徽章计数用裸正则 `re.compile("已核验")`，把**正文散文**（"标 已核验 ✓"）、CSS/JS 注释、图例徽章都算成徽章 → 计数虚高误伤；②MODE-A/B 用的是**装饰性**「已核验 ✓」（MODE-A 还是 `style=` 山寨 span），没有配套可执行 x-verify 块——v0.4 把门升级成可执行后，这些旧装饰徽章必然挂 | "计数收紧到只数**徽章元素** `<span class="badge …">已核验`（两脚本正则逐字一致），散文/注释/图例不计、图例改 `<strong>`；示例按性质分流：**纯微积分(MODE-B)补真 x-verify 块**让 17 个 已核验 名副其实，**需建物理模型(MODE-A)诚实降级 `未自动核验`**" → SKILL.md Check 4 + design-system.md「What counts as a badge」 | `build_and_check.py`/`verify_solutions.py` 徽章正则收紧并对齐 + `test_build_and_check.py`（18/18，+散文不计/元素计一次）+ `test_verify_solutions.py`（9/9，+散文不冒充徽章）；三示例 `check`＋`verify_solutions` 实测全绿（MODE-B 17/17 真跑 PASS） |
| 2026-06-16 | 担心 LLM 画的 SVG"莫名其妙偏移"（来自一份 SVG 偏移调研报告） | 报告诊断属实（viewBox 映射 / 百分比相对最近视口 / CSS-transform 参考框 / 文本基线 / marker refX-refY 五类），但**审计本技能 47 个真实图发现 5 类里 3 类按构造不可能**（无嵌套 svg、无 % 几何、无 `transform=`），余下两类只以良性形态出现——技能其实早已"按例子守住安全子集" | "把报告的**生成约束**收成 design-system.md『SVG-safe-subset』成文规则（单根 svg、绝对坐标、禁嵌套/%/foreignObject/CSS-transform、显式基线、复用既有 marker）+ 出图前『渲染并肉眼看』；**放弃**报告的重型管线（resvg / SVGO 归一化 / 三引擎像素 diff / getBBox 投影）——对单文件少量手绘图过度工程" → design-system.md SVG-safe-subset + SKILL.md MODE-C 图规则 | `build_and_check.py check_svg_offset_risks`（WARN 级：嵌套 svg / % 几何 / foreignObject / CSS-transform；favicon data-URI svg 先剥离不误报）+ `test_build_and_check.py`（16/16）；三个示例真实语料实测 0 误报 |
| 2026-06-16 | 用户要求"所有题目都带真已核验"，给 MODE-C 概念选择题写 x-verify 时，含 `²√πω` 的检查名让块在本机（Windows GBK 控制台）`UnicodeEncodeError` 整块误判 FAIL | `verify_solutions.run_block` 用 `subprocess.run(text=True)` 不指定编码 → 子进程 stdout 按**系统 locale（GBK/CP-936）**编码，`print("…x²…")` 抛 `UnicodeEncodeError`。MODE-A/B 之所以没踩，是因为它们的检查名碰巧都是 ASCII（`^2`/`pi`）；换成真 Unicode 数学符号就暴露——这是**门本身的跨平台脆弱性**，不是题的错 | "强制子进程 UTF-8 stdio：`env PYTHONIOENCODING=utf-8` + `subprocess.run(..., encoding='utf-8', errors='replace')`；从此检查名可含任意 Unicode、门与 locale 无关" → `verify_solutions.py run_block` | `test_verify_solutions.py` 新增 unicode 检查名用例（`name="面积 x² = √π·ω 验证"` 必须 run 通过），9/9→**10/10**；109 个真实块全跑过 |
| 2026-06-16 | 把"所有题目"都补可执行已核验时，机检顺手抓出两处**印刷错误**：例1 滑块 $x(t)$ 显示式外层系数写成 `l`（对其二阶导给 $a_x\propto l\omega^2$，与印出的 $r\omega^2$ 答案矛盾）；浮动起重船数值标 `-0.318` 但同处公式代入实为 `+0.318` | 这些是人/模型誊写时的笔误，肉眼看"有公式有答案"就放过了；只有**真算一遍**才露馅——正是 v0.4 可执行门的设计初衷（"自信地写错还自评通过"） | "可执行块从**给定量**重算、与印出答案逐一比对，不一致就改源文（系数 `l→r`、符号 `-0.318→+0.318`）而不是迁就；子代理发现 discrepancy 必须回报正确值由主控改 HTML" → 两处示例已订正 | 订正后对应 x-verify 块 PASS；体现"门能抓出连作者都没察觉的错" |
| 2026-06-16 | 展开解答（`<details>`）时鼠标卡顿约 10 秒、每次都有 | 一篇 3000+ 公式的笔记 DOM 15.5 万节点、页高 7.3 万 px；展开触发**整页重排+重绘**，用户机 GPU 重绘约 10s。无头单次展开布局仅 ~8ms→瓶颈是绘制非脚本；KaTeX 默认 `output:'htmlAndMathml'` 还把节点翻倍 | "①KaTeX `output:'html'` 去隐藏 MathML（节点−26%）；②`.card,.example-block{content-visibility:auto;contain-intrinsic-size:auto 600px}` 跳过屏外布局/绘制（整页重排 −97%、展开 0.4ms）；代价是页高变估算→`doRestore` 改 CV 感知逐帧重试" → design-system.md（KaTeX 模板 + .card CV + doRestore） | 真机 Chromium 实测（用户确认加 CV 后不卡）+ performance 多次量布局/重排耗时（43.8→1.3ms）；三示例 build_and_check+verify_solutions 全绿、tests 18/18+9/9 |

## Open watch-list (对标观察，下一轮从真实反馈进)

- [ ] 触发边界：上传 PDF 时 `study-notes`(出完整笔记) vs `summarize-slides`(出考点速查) 是否被正确区分？
      —— 已在 `evals.json → triggering` 加负例，需在真实会话里复核命中率。
- [x] "已核验 ✓" 已从"自评/人审/静态计数门"升级为**可执行门**：每个 badge 必须配一个
      `<script type="text/x-verify">` 块，`verify_solutions.py` 真跑 sympy、从给定量重算并比对，
      只有 PASS 才放行；不可机检的题标 `未自动核验`（2026-06-15）。这跨过了"计数门只证工件存在、
      不证为真"的边界——曲柄连杆那道错题已被它实测拦下（recomputed != claimed）。后续观察：
      x-verify 块仍由模型撰写，理论上可用 `check_equal(claimed,claimed)` 等方式自我作弊；当前对
      "自信但非对抗"的失败模式已足够，若出现刻意绕过，再加"recompute 必须源自 given、禁止等于 claimed"的结构校验。
- [x] **里程碑（2026-06-16, v0.7）**：三个示例的每一道题（109 块：MODE-A 72 + MODE-B 17 + MODE-C 20）都带可执行已核验、`verify_solutions` 全 PASS，已无装饰性/散文式核验声明。证明可执行门不止适用纯微积分：力学题联立治理方程重解、概念选择题重算决定性关键量 + 计算反例否干扰项，都能机检。
- [ ] 大批量(≥8 题)并行子代理产物的一致性（同一套设计系统/图规则）——抽查拼接页有无风格漂移。本轮用 **12 个并行子代理**核验 MODE-A 例题+自测，**每块先经真 `verify_solutions` 跑通才回传**、主控整合后再在整文件上重跑一遍门兜底——这套"子代理只产经自测的块、主控用同一把真尺复核"的模式有效防住了子代理的自评虚高，可复用。残留：MCQ"用反例否干扰项"类块仍是模型撰写的判定逻辑，门只保证它跑通、不保证选项映射的教学解释也对（与下方自我作弊观察同源）。
- [ ] SVG 偏移的真实来源更可能是**手调坐标差几像素**（cosmetic）或**暗色同色字消失**，而非报告主攻的深层坐标系 bug（本技能按构造已基本免疫）。`check_svg_offset_risks` 现为 WARN，跑顺示例语料若长期 0 命中可考虑提为 FAIL；"渲染并肉眼看"仍是抓 cosmetic 偏移的主力。
- [x] `examples/` 的 MODE-A/B 示例 `build_and_check` 因 `已核验` 计数（含正文里"标 已核验 ✓"的散文提及 + 无 x-verify 工件的装饰徽章）而 FAIL——**先于本轮、与本轮无关**。**已修（2026-06-16）**：三招齐下——计数只数徽章元素不数散文（两脚本正则对齐）、MODE-B 17 道纯微积分补真 x-verify 块（17/17 PASS，已核验名副其实）、MODE-A 力学题诚实降级 `未自动核验`。三示例现都干净通过两道门。详见上表 2026-06-16 行。
