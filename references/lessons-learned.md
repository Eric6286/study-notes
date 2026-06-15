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
| 2026-06-13 | MODE B/C 偶发"题做错了" | 解一次就写、从不独立复核；心算多步 | "盲解双算 + 用 python/sympy 重算，两路一致才 `已核验 ✓`" → §0.5 + workflow-orchestration.md | evals 期望含"已核验 ✓"；尚无静态检查（人审） |

## Open watch-list (对标观察，下一轮从真实反馈进)

- [ ] 触发边界：上传 PDF 时 `study-notes`(出完整笔记) vs `summarize-slides`(出考点速查) 是否被正确区分？
      —— 已在 `evals.json → triggering` 加负例，需在真实会话里复核命中率。
- [ ] "已核验 ✓" 目前靠人审，没有静态检查能证明双算真的发生过。若出现"标了已核验仍算错"，
      考虑加一条 eval 或要求把验算的 python 输出留在 `<details>` 里以便抽查。
- [ ] 大批量(≥8 题)并行子代理产物的一致性（同一套设计系统/图规则）——抽查拼接页有无风格漂移。
