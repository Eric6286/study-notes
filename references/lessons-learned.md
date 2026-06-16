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

## Open watch-list (对标观察，下一轮从真实反馈进)

- [ ] 触发边界：上传 PDF 时 `study-notes`(出完整笔记) vs `summarize-slides`(出考点速查) 是否被正确区分？
      —— 已在 `evals.json → triggering` 加负例，需在真实会话里复核命中率。
- [x] "已核验 ✓" 已从"自评/人审/静态计数门"升级为**可执行门**：每个 badge 必须配一个
      `<script type="text/x-verify">` 块，`verify_solutions.py` 真跑 sympy、从给定量重算并比对，
      只有 PASS 才放行；不可机检的题标 `未自动核验`（2026-06-15）。这跨过了"计数门只证工件存在、
      不证为真"的边界——曲柄连杆那道错题已被它实测拦下（recomputed != claimed）。后续观察：
      x-verify 块仍由模型撰写，理论上可用 `check_equal(claimed,claimed)` 等方式自我作弊；当前对
      "自信但非对抗"的失败模式已足够，若出现刻意绕过，再加"recompute 必须源自 given、禁止等于 claimed"的结构校验。
- [ ] 大批量(≥8 题)并行子代理产物的一致性（同一套设计系统/图规则）——抽查拼接页有无风格漂移。
