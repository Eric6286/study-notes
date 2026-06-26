# Design System Reference

Complete CSS and HTML component library for study notes. Copy the CSS block verbatim into `<style>` tags.

## Contents

- **Full CSS** — the complete `:root` palette, dark-mode, layout, and every component class
- **HTML Page Template** — head (KaTeX + macros + error banner), `.page`, header, TOC, nav JS
- **Layout Consistency Rule (MANDATORY)** — the one-sub-section-per-card invariant
- **Callout Quick Reference** — `.mistake` / `.exam` / `.tip` / `.note` variants
- **Section Color Assignment Guide** — which `.sec-COLOR` for which kind of section
- **Big Formula Usage** — `.big-formula` vs `.fbox`
- **SVG Diagram Rules (CRITICAL)** — arrow size, proportions, label placement, Unicode-in-`<text>`
- **Vector Notation in KaTeX** — `\vec` / `\hat`, when bold is OK
- **KaTeX Pre-defined Macros** — `\degree` `\celsius` `\d` `\e` `\bm` … (always available)
- **KaTeX Forbidden Commands** — what produces red error text
- **Never use `\boxed{}` inside `.fbox`/`.big-formula`/`.callout`** — silent visual failure + recovery
- **Self-test quiz widget** (optional) — CSS + HTML pattern + the one-copy JS
- **Anki flashcard deck** (optional) — hidden `#anki-deck` format for `make_anki.py`
- **Source citation tag `.src-ref`** — for source-grounded fidelity mode
- **MODE A note components** — elective badge, figure reference, collapsible example/exercise card

---

## Full CSS

```css
:root {
  --bg:#ffffff; --bg2:#f7f6f2; --bg3:#f0ede6; --bg4:#e8e4db;
  --text:#1a1a18; --text2:#5a5a56; --text3:#8a8a84;
  --border:rgba(0,0,0,0.11);
  --purple:#534AB7; --purple-light:#EEEDFE; --purple-dark:#3C3489; --purple-mid:#7F77DD;
  --teal:#0F6E56;   --teal-light:#E1F5EE;   --teal-dark:#085041;   --teal-mid:#1D9E75;
  --coral:#993C1D;  --coral-light:#FAECE7;  --coral-dark:#712B13;  --coral-mid:#D85A30;
  --amber:#BA7517;  --amber-light:#FAEEDA;  --amber-dark:#854F0B;  --amber-mid:#EF9F27;
  --blue:#185FA5;   --blue-light:#E6F1FB;   --blue-dark:#0C447C;   --blue-mid:#378ADD;
  --green:#3B6D11;  --green-light:#EAF3DE;  --green-dark:#27500A;  --green-mid:#639922;
  --red:#A32D2D;    --red-light:#FCEBEB;    --red-dark:#791F1F;
  --pink:#993556;   --pink-light:#FBEAF0;
  --radius:10px;
}
@media(prefers-color-scheme:dark){
  :root{
    --bg:#1e1e1c; --bg2:#252523; --bg3:#2c2c2a; --bg4:#333330;
    --text:#e8e6de; --text2:#a8a69e; --text3:#706e68;
    --border:rgba(255,255,255,0.1);
    --purple-light:#26215C; --teal-light:#04342C; --coral-light:#4A1B0C;
    --amber-light:#412402; --blue-light:#042C53; --green-light:#173404;
    --red-light:#501313; --pink-light:#4B1528;
    /* CRITICAL dark-mode contrast fix. The block above only re-darkens the *-light
       BACKGROUNDS; without the two lines below, the base accents and the *-dark TEXT
       colours keep their light-mode (dark) values, so every "accent text on accent-light
       background" pairing — badges (.b-teal), section headings (.sec-* h2), .flabel,
       callout icons, graded .quiz-opt — becomes dark-on-dark and unreadable (old
       teal-dark on teal-light measured 1.46:1). Brightening them restores 6.8–9.9:1.
       *-mid are already bright; leave them untouched. */
    --purple:#9A92E6; --teal:#3FB389; --coral:#E07B52; --amber:#E89A2A;
    --blue:#5B9FE0; --green:#7FB23E; --red:#E07676; --pink:#D87B9C;
    --purple-dark:#C7C2F5; --teal-dark:#74D6B0; --coral-dark:#F4A487; --amber-dark:#F2B75A;
    --blue-dark:#92C2F0; --green-dark:#A6CF6B; --red-dark:#F2A6A6;
  }
}
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);font-size:15px;line-height:1.8;}
.page{max-width:900px;margin:0 auto;padding:32px 24px 100px;}
/* Safety net: if a div escapes .page due to a tag mismatch, body still constrains width */
body>*:not(.page){max-width:900px;margin-left:auto;margin-right:auto;padding-left:24px;padding-right:24px;}
.katex{font-size:1.06em;}
/* ── Wide display-formula handling (revised) ──
   A display formula wider than the text column must NOT spill past its box / the viewport.
   That overflow happens at ANY width (a long equation overflows a 900px column too, not just
   on a phone), so the fix must be width-independent: scroll the formula horizontally INSIDE
   its own box at all widths. overflow-y:hidden is deliberate and load-bearing — it stops
   .katex-display from becoming a *vertical* scroll container, so a mostly-vertical wheel /
   trackpad gesture passes straight through to the page instead of being trapped on the formula
   (the "jump" the earlier all-visible design was trying to avoid). The box auto-sizes to the
   formula's natural height, so overflow-y:hidden never clips a tall \dfrac / \int / \sqrt /
   matrix (verified by rendering). The chunky OS-native scrollbar is replaced by the thin,
   theme-aware one defined just below. */
.katex-display{margin:4px 0!important;overflow-x:auto;overflow-y:hidden;
  overscroll-behavior-x:contain;padding:2px 0;-webkit-overflow-scrolling:touch;}
/* Thin, theme-aware scrollbar for the only two things that scroll horizontally — wide
   formulas and wide tables — instead of the jarring white OS default with stepper arrows.
   It only appears when content actually overflows; formulas that fit show no bar. The thumb
   is --text2 (not --text3): --text3 measured 2.7–3.0:1 on the box bg, just under WCAG 1.4.11's
   3:1 for non-text UI; --text2 clears it at ~5.7:1 and reads as a clearer scroll affordance. */
.katex-display,table{scrollbar-width:thin;scrollbar-color:var(--text2) transparent;}
.katex-display::-webkit-scrollbar,table::-webkit-scrollbar{height:7px;}
.katex-display::-webkit-scrollbar-track,table::-webkit-scrollbar-track{background:transparent;}
.katex-display::-webkit-scrollbar-thumb,table::-webkit-scrollbar-thumb{background:var(--text2);border-radius:4px;}
.katex-display:hover::-webkit-scrollbar-thumb,table:hover::-webkit-scrollbar-thumb{background:var(--text);}
/* drop the chunky stepper-arrow buttons at the ends → a clean, minimal bar */
.katex-display::-webkit-scrollbar-button,table::-webkit-scrollbar-button{display:none;width:0;height:0;}
/* keyboard a11y: the JS below adds tabindex=0 to a formula/table ONLY when it actually
   overflows, so a keyboard user can focus it and arrow-scroll. Show a focus ring for them. */
.katex-display:focus-visible,table:focus-visible{outline:2px solid var(--blue-mid);outline-offset:2px;border-radius:4px;}

/* ── Global width normalisation ──
   Every block component is width:100% and cannot overflow its container.
   NOTE: <details> is intentionally excluded — it needs overflow:visible for tall formulas. */
.card,.fbox,.callout,.big-formula,.example-block,.toc,
table,.answer-box,.two-col,.steps,.visual-row{
  width:100%;
  max-width:100%;
  box-sizing:border-box;
}
/* Tables may be wide — allow horizontal scroll only on the table element itself,
   not on formula containers (scrollbars on formula boxes intercept page scroll). */
table{overflow-x:auto;display:block;}

/* Header */
.header{text-align:center;padding:48px 0 36px;border-bottom:1px solid var(--border);margin-bottom:40px;}
.header h1{font-size:30px;font-weight:700;margin-bottom:10px;letter-spacing:-0.5px;}
.header .subtitle{color:var(--text2);font-size:14px;margin-bottom:16px;}
.tags{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;}
.tag{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:500;}

/* TOC — hierarchical outline style */
.toc{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:22px 26px;margin-bottom:44px;}
.toc-title{font-size:12px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;}
/* L1: chapter rows */
.toc-l1{margin-bottom:2px;}
.toc-l1>a{display:flex;align-items:center;gap:8px;color:var(--text);text-decoration:none;
  font-size:14px;font-weight:600;padding:5px 6px;border-radius:6px;transition:background 0.12s;}
.toc-l1>a:hover{background:var(--bg3);}
.toc-l1>a .sec-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
/* L2: sub-section rows */
.toc-l2{padding-left:22px;margin-top:1px;margin-bottom:3px;}
.toc-l2 a{display:flex;align-items:center;gap:7px;color:var(--blue);text-decoration:none;
  font-size:13px;padding:3px 6px;border-radius:5px;transition:background 0.12s;
  border-left:2px solid var(--border);}
.toc-l2 a:hover{background:var(--bg3);text-decoration:none;}
.toc-l2 a .sec-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0;opacity:0.7;}

/* Section */
.section{margin-bottom:60px;}
.section-header{display:flex;align-items:center;gap:14px;margin-bottom:22px;padding-bottom:14px;border-bottom:2.5px solid var(--border);}
.section-num{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;flex-shrink:0;}
.section h2{font-size:23px;font-weight:700;}

/* ── Cards ── */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:22px 26px;margin-bottom:16px;}
/* ── Perf on huge notes (1000s of formulas) ──
   content-visibility:auto lets the browser SKIP layout + paint of off-screen blocks, so opening a
   <details> (or any reflow) no longer forces the whole tall page to re-layout/repaint — that whole-
   page repaint on a 100k+ node page is what makes opening a solution jank for seconds. contain-
   intrinsic-size is an estimated off-screen height; the 'auto' keyword caches the real size once a
   block has rendered. Trade-off: scrollbar position and scroll-memory restore are approximate on
   very long notes until scrolled through once (the doRestore retry below copes) — well worth it. */
.card,.example-block{content-visibility:auto;contain-intrinsic-size:auto 600px;}

/* Level 1 card title: prominent, full-width bottom rule */
.card h3{font-size:17px;font-weight:700;margin:0 0 16px;padding-bottom:10px;border-bottom:1px solid var(--border);}

/* Level 2 sub-heading: left accent bar + slightly indented */
.card h4{font-size:14px;font-weight:700;margin:20px 0 8px;padding-left:10px;
  border-left:3px solid var(--border);color:var(--text);line-height:1.4;}

/* Level 3 sub-sub-heading: muted, no decoration, tight top margin */
.card h5{font-size:13px;font-weight:600;margin:14px 0 6px;color:var(--text2);letter-spacing:0.02em;}

.card p{margin-bottom:10px;line-height:1.8;}
.card p:last-child{margin-bottom:0;}
.card ul,.card ol{padding-left:22px;margin-bottom:10px;}
.card li{margin-bottom:6px;line-height:1.8;font-size:14px;}

/* Formula boxes */
.fbox{background:var(--bg3);border-left:3.5px solid;border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0;overflow:visible;}
.fbox .flabel{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;margin-bottom:12px;opacity:0.75;}
/* CRITICAL: never set line-height on .frow — KaTeX uses internal vertical-align to position
   fractions, integrals, matrices. If line-height is smaller than the formula's rendered height,
   the inline content inside .katex-display protrudes below the line box, and the NEXT element's
   background covers it (paint order issue). Use line-height:normal to reset the inherited
   body line-height of 1.8 which is the root cause of the occlusion bug. */
.fbox .frow{margin:10px 0;line-height:normal;overflow:visible;}
.fbox .frow:first-of-type{margin-top:0;}
.fbox .fnote{font-size:13px;color:var(--text2);margin-top:10px;line-height:1.6;}

/* Same fix for big-formula — must not inherit body line-height */
.big-formula{text-align:center;padding:22px 18px;background:var(--bg2);border-radius:10px;margin:18px 0;overflow:visible;border:1px solid var(--border);line-height:normal;}
.big-formula.highlight{border-width:2px;}

/* Callouts */
.callout{border-radius:9px;padding:14px 18px;margin:14px 0;display:flex;gap:13px;}
.callout-icon{font-size:15px;flex-shrink:0;margin-top:3px;line-height:1;}
.callout-body{flex:1;}
/* Only the direct-child <strong> (the callout title line) gets display:block.
   <strong> nested inside <p> or <li> stays inline — never add display:block
   to a general tag selector like 'strong' without a '>' combinator. */
.callout-body > strong{display:block;font-size:13px;font-weight:700;margin-bottom:5px;}
.callout-body p strong,.callout-body li strong{display:inline;font-size:inherit;font-weight:700;}
.callout-body p,.callout-body li{font-size:14px;margin:0 0 4px;line-height:1.7;}
.callout-body ul{padding-left:18px;margin:0;}
/* note=blue💡, tip=teal✦, warn=amber⚠, exam=red★, intuition=purple🔍, mistake=pink✗, derivation=gray∴ */
.note{background:var(--blue-light);border:1px solid rgba(24,95,165,0.18);}
.note .callout-icon::before{content:"💡";}
.tip{background:var(--teal-light);border:1px solid rgba(15,110,86,0.18);}
.tip .callout-icon::before{content:"✦";color:var(--teal);font-size:13px;}
.warn{background:var(--amber-light);border:1px solid rgba(186,117,23,0.2);}
.warn .callout-icon::before{content:"⚠";color:var(--amber);}
.exam{background:var(--red-light);border:1px solid rgba(163,45,45,0.22);}
.exam .callout-icon::before{content:"★";color:var(--red);}
.intuition{background:var(--purple-light);border:1px solid rgba(83,74,183,0.2);}
.intuition .callout-icon::before{content:"🔍";}
.mistake{background:var(--pink-light);border:1px solid rgba(153,53,86,0.2);}
.mistake .callout-icon::before{content:"✗";color:var(--pink);font-size:13px;}
.derivation{background:var(--bg3);border:1px solid var(--border);}
.derivation .callout-icon::before{content:"∴";color:var(--text3);font-size:14px;font-weight:700;}

/* Tables */
table{width:100%;border-collapse:collapse;font-size:14px;margin:14px 0;}
th{background:var(--bg3);font-weight:600;padding:10px 14px;text-align:left;border:1px solid var(--border);}
td{padding:10px 14px;border:1px solid var(--border);vertical-align:middle;line-height:1.9;}
tr:nth-child(even) td{background:var(--bg2);}
td .katex,th .katex{font-size:0.95em;}

/* Collapsible details —
   overflow:hidden would clip tall KaTeX content (fractions, integrals, matrices)
   at the bottom of an open <details> block. Use overflow:visible instead.
   border-radius still renders on the border itself; only interior corner-clipping
   of overflowing children is lost, which is acceptable. */
details{border:1px solid var(--border);border-radius:9px;margin-bottom:10px;overflow:visible;}
summary{padding:13px 18px;font-weight:600;font-size:14px;cursor:pointer;background:var(--bg2);display:flex;align-items:center;gap:8px;list-style:none;user-select:none;}
summary::-webkit-details-marker{display:none;}
summary::before{content:"▶";font-size:9px;color:var(--text3);transition:transform 0.2s;flex-shrink:0;}
details[open] summary::before{transform:rotate(90deg);}
.details-body{padding:18px 20px;}
.details-body p{margin-bottom:8px;font-size:14px;}

/* Steps —
   .step is a flex row: [step-num] [step-body]. The IDEAL nesting puts every formula/callout
   INSIDE .step-body. But a block (.fbox/.callout/.answer-box/.big-formula or a <p>) sometimes
   ends up as a DIRECT child of .step (a sibling of .step-body) — e.g. a solver agent emits
   <div class="step-body">…</div><div class="fbox">…</div>. Without the guards below that block
   becomes a third flex item, and a wide display formula's min-content width squeezes .step-body
   toward 0 so CJK text shatters to ONE CHARACTER PER LINE (a real MODE-C failure: 4 solutions
   rendered as vertical columns of single chars). Three load-bearing guards make .step robust to
   that mis-nesting:
     • flex-wrap:wrap            — lets a stray block move to its own line instead of competing
     • .step-body{flex:1 1 0;min-width:0} — min-width:0 lets the text body shrink/wrap normally
                                    (default min-width:auto is what lets a sibling starve it)
     • .step>BLOCK{flex:0 0 100%} — forces any stray block child to a full-width row BELOW
   build_and_check.py also WARNs on the mis-nesting so it gets cleaned up at the source. */
.step{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:16px;}
.step-num{width:28px;height:28px;border-radius:50%;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;}
.step-body{flex:1 1 0;min-width:0;font-size:14px;line-height:1.75;}
.step>.fbox,.step>.callout,.step>.answer-box,.step>.big-formula,.step>p{flex:0 0 100%;width:100%;box-sizing:border-box;margin-top:0;}
/* Step title: direct-child strong only */
.step-body > strong{display:block;margin-bottom:4px;}
.step-body p strong,.step-body li strong{display:inline;font-weight:700;}

/* Section color accents — apply to wrapper div, e.g. <div class="sec-purple"> */
.sec-purple .section-num{background:var(--purple-light);color:var(--purple-dark);}
.sec-purple .section h2{color:var(--purple-dark);}
.sec-purple .fbox{border-color:var(--purple);}
.sec-purple .step-num{background:var(--purple-light);color:var(--purple-dark);}
.sec-teal .section-num{background:var(--teal-light);color:var(--teal-dark);}
.sec-teal .section h2{color:var(--teal-dark);}
.sec-teal .fbox{border-color:var(--teal);}
.sec-teal .step-num{background:var(--teal-light);color:var(--teal-dark);}
.sec-coral .section-num{background:var(--coral-light);color:var(--coral-dark);}
.sec-coral .section h2{color:var(--coral-dark);}
.sec-coral .fbox{border-color:var(--coral);}
.sec-coral .step-num{background:var(--coral-light);color:var(--coral-dark);}
.sec-amber .section-num{background:var(--amber-light);color:var(--amber-dark);}
.sec-amber .section h2{color:var(--amber-dark);}
.sec-amber .fbox{border-color:var(--amber);}
.sec-amber .step-num{background:var(--amber-light);color:var(--amber-dark);}
.sec-blue .section-num{background:var(--blue-light);color:var(--blue-dark);}
.sec-blue .section h2{color:var(--blue-dark);}
.sec-blue .fbox{border-color:var(--blue);}
.sec-blue .step-num{background:var(--blue-light);color:var(--blue-dark);}
.sec-green .section-num{background:var(--green-light);color:var(--green-dark);}
.sec-green .section h2{color:var(--green-dark);}
.sec-green .fbox{border-color:var(--green);}
.sec-green .step-num{background:var(--green-light);color:var(--green-dark);}
.sec-red .section-num{background:var(--red-light);color:var(--red-dark);}
.sec-red .section h2{color:var(--red-dark);}
.sec-red .fbox{border-color:var(--red);}
.sec-red .step-num{background:var(--red-light);color:var(--red-dark);}

/* Badges */
.badge{display:inline-block;padding:2px 9px;border-radius:4px;font-size:11px;font-weight:600;margin-right:4px;}
.b-purple{background:var(--purple-light);color:var(--purple-dark);}
.b-teal{background:var(--teal-light);color:var(--teal-dark);}
.b-coral{background:var(--coral-light);color:var(--coral-dark);}
.b-amber{background:var(--amber-light);color:var(--amber-dark);}
.b-blue{background:var(--blue-light);color:var(--blue-dark);}
.b-green{background:var(--green-light);color:var(--green-dark);}
.b-red{background:var(--red-light);color:var(--red-dark);}
/* Verification badges (boxed highlight). b-verified = a solution whose executable x-verify block
   PASSED (green box). b-unverified = 未自动核验, an honest abstention — not machine-verified, may
   still be correct (amber "heads-up" box, deliberately NOT red so it doesn't read as "wrong"). */
.b-verified{background:var(--green-light);color:var(--green-dark);border:1px solid var(--green);font-weight:700;}
.b-unverified{background:var(--amber-light);color:var(--amber-dark);border:1px solid var(--amber);}

/* "How to use" lead box at top of a solutions page (用法说明 + 核验图例). */
.lead{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:20px 24px;margin-bottom:28px;}
.lead p{margin-bottom:8px;}
.lead a{color:var(--blue);font-weight:600;}
/* Legend chip — looks like a verification badge but is NOT counted as one (class is .lgnd, not .badge),
   so a legend that demonstrates 已核验/未自动核验 never inflates the badge gate. Use ONLY in the legend. */
.lgnd{display:inline-block;padding:1px 8px;border-radius:4px;font-size:12px;font-weight:700;}
.lg-v{background:var(--green-light);color:var(--green-dark);border:1px solid var(--green);}
.lg-u{background:var(--amber-light);color:var(--amber-dark);border:1px solid var(--amber);}

/* Example blocks — no fixed height, no max-height, no writing-mode.
   The header is a horizontal strip at the top; content expands to fit.
   NEVER use writing-mode, transform:rotate, or height/max-height on these. */
.example-block{border:1px solid var(--border);border-radius:9px;overflow:visible;margin:14px 0;
  height:auto !important;max-height:none !important;}
.example-header{background:var(--bg3);padding:10px 18px;font-size:13px;font-weight:700;line-height:1.7;
  /* Block flow, NOT flex. The header holds free text broken up by inline elements — a KaTeX
     $v$ span, <strong>, a trailing 已核验 badge. Under display:flex each text run becomes a
     separate anonymous flex item that shrinks to min-width on a phone, shattering the Chinese
     title into vertical columns. Inline/block flow lets badge+text+math wrap as one normal
     line. writing-mode/height stay !important to keep the past vertical-text fix. */
  border-bottom:1px solid var(--border);border-radius:9px 9px 0 0;
  writing-mode:horizontal-tb !important;height:auto !important;}
.example-header .badge{vertical-align:middle;}
.example-body{padding:16px 20px;height:auto !important;max-height:none !important;}
.example-body p{font-size:14px;margin-bottom:8px;line-height:1.75;}
.example-body p:last-child{margin-bottom:0;}

/* Answer highlight */
.answer-box{background:var(--green-light);border:1.5px solid rgba(59,109,17,0.25);border-radius:8px;padding:12px 16px;margin-top:10px;}
.answer-box p{font-size:14px;margin:0;}

/* Two-column layout */
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0;}
@media(max-width:580px){.two-col{grid-template-columns:1fr;}}

/* ── Floating section navigator ── */
#nav-btn{
  position:fixed;bottom:24px;right:24px;z-index:9999;
  width:34px;height:34px;border-radius:8px;
  background:var(--bg2);color:var(--text2);
  border:1px solid var(--border);cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 1px 6px rgba(0,0,0,0.18);
  transition:background 0.15s,color 0.15s,box-shadow 0.15s;
  font-size:15px;line-height:1;
}
#nav-btn:hover{background:var(--bg3);color:var(--text);box-shadow:0 2px 12px rgba(0,0,0,0.22);}
#nav-panel{
  position:fixed;bottom:66px;right:24px;z-index:9998;
  background:var(--bg);border:1px solid var(--border);border-radius:10px;
  box-shadow:0 4px 20px rgba(0,0,0,0.18);
  width:240px;max-height:65vh;overflow-y:auto;
  padding:8px 0;
  opacity:0;transform:translateY(8px) scale(0.97);
  pointer-events:none;transition:opacity 0.15s,transform 0.15s;
}
#nav-panel.open{opacity:1;transform:none;pointer-events:auto;}
#nav-panel a{
  display:flex;align-items:center;gap:9px;
  padding:6px 14px;font-size:13px;color:var(--text);
  text-decoration:none;line-height:1.4;
  transition:background 0.1s;
}
#nav-panel a:hover{background:var(--bg2);}
#nav-panel a .nd{
  width:20px;height:20px;border-radius:5px;font-size:10px;font-weight:700;
  display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;
  color:#fff;
}
#nav-panel .nav-title{
  font-size:10px;font-weight:700;color:var(--text3);
  text-transform:uppercase;letter-spacing:0.08em;
  padding:0 14px 5px;border-bottom:1px solid var(--border);margin-bottom:3px;
}

/* ── Universal overflow guard ──
   Long inline math, URLs, or unbroken strings must wrap instead of pushing the page wide.
   (KaTeX inline atoms still won't split mid-symbol, but this stops prose from overflowing.) */
.card p,.card li,.callout-body p,.callout-body li,.example-body p,.details-body p,.step-body,
.answer-box p,.fnote{overflow-wrap:break-word;}

/* ── Mobile (≤600px) ──
   Wide-formula overflow is already handled width-independently by .katex-display above; here
   we only reclaim horizontal space (tighter padding) and shrink oversized headings/math so
   long rows need less scrolling in the first place. */
@media(max-width:600px){
  body{font-size:14px;}
  .page{padding:24px 14px 80px;}
  .card{padding:18px 16px;}
  .fbox{padding:14px 16px;}
  .big-formula{padding:18px 12px;}
  .katex{font-size:1em;}
  .header h1{font-size:24px;}
  .section h2{font-size:20px;}
}
```

---

## HTML Page Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TOPIC — 学习笔记</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📖</text></svg>">
<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="
    renderMathInElement(document.body, {
      delimiters: [
        {left:'$$', right:'$$', display:true},
        {left:'$',  right:'$',  display:false}
      ],
      throwOnError: false,
      output: 'html',  // skip KaTeX's hidden MathML twin: ~halves DOM nodes and drops MathML layout-on-reveal — a real perf win on notes with thousands of formulas
      macros: {
        /* Inexact differential (đ, not a state function) */
        '\\dj':      '{\\text{đ}}',
        /* Degree symbol workaround: ^\circ requires an empty base */
        '\\degree':  '{{}^\\circ}',
        /* Common shorthands */
        '\\d':       '{\\mathrm{d}}',
        '\\e':       '{\\mathrm{e}}',
        '\\i':       '{\\mathrm{i}}',
        /* \cdotp is NOT a KaTeX command — it renders as an error.
           Map it to \cdot (centre dot, correct for unit products like J·mol⁻¹) */
        '\\cdotp':   '{\\cdot}',
        /* siunitx-style unit helper (not a KaTeX built-in).
           NO wrapping braces: the inner \text takes its argument from OUTSIDE the macro
           (\unit{m/s}). '{\\,\\text}' would expand \unit{m/s} → {\,\text}{m/s}, leaving \text
           with no argument → KaTeX "Extra }" parse error (silent until render). */
        '\\unit':    '\\,\\text',
        '\\celsius': '{{{}^\\circ\\text{C}}}',
        /* Bold vector alternative — bare alias, NOT '{\\boldsymbol}': \bm{F} must expand to
           \boldsymbol{F}, not {\boldsymbol}{F} (the latter errors, same reason as \unit above). */
        '\\bm':      '\\boldsymbol'
      }
    });
    /* Signal that KaTeX rendering is complete */
    window.__katexDone = true;
    window.dispatchEvent(new Event('katexdone'));
    /* Post-render error scan */
    var errs = document.querySelectorAll('.katex-error');
    if(errs.length){
      var banner = document.createElement('div');
      banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#A32D2D;color:#fff;font-size:13px;padding:8px 16px;';
      banner.textContent = '⚠ 发现 ' + errs.length + ' 处公式渲染错误（红色高亮）。常见原因：\\dj 已内置为 đ；°C 请写为 {}^\\circ\\text{C}；检查是否有未转义的 LaTeX 命令。';
      document.body.appendChild(banner);
    }
  "></script>
<!-- Disable browser scroll-restoration so our localStorage restore wins -->
<script>if('scrollRestoration' in history) history.scrollRestoration = 'manual';</script>
<style>
/* PASTE FULL CSS HERE */
</style>
</head>
<body>
<div class="page">

<!-- HEADER -->
<div class="header">
  <h1>TOPIC</h1>
  <p class="subtitle">SUBTITLE</p>
  <div class="tags">
    <span class="tag" style="background:var(--purple-light);color:var(--purple-dark)">Tag1</span>
    <!-- more tags -->
  </div>
</div>

<!-- TOC — hierarchical outline: one .toc-l1 per chapter, .toc-l2 for sub-sections -->
<div class="toc">
  <div class="toc-title">目录</div>

  <div class="toc-l1">
    <a href="#s8-1"><span class="sec-dot" style="background:var(--purple-mid)"></span>§8-1 液体的微观结构</a>
    <div class="toc-l2">
      <a href="#s8-1-1"><span class="sec-dot" style="background:var(--purple-mid)"></span>§8-1-1 近程有序性</a>
      <a href="#s8-1-2"><span class="sec-dot" style="background:var(--purple-mid)"></span>§8-1-2 液晶</a>
    </div>
  </div>

  <div class="toc-l1">
    <a href="#s8-2"><span class="sec-dot" style="background:var(--teal-mid)"></span>§8-2 热传导与扩散</a>
    <div class="toc-l2">
      <a href="#s8-2-1"><span class="sec-dot" style="background:var(--teal-mid)"></span>§8-2-1 热传导</a>
      <a href="#s8-2-2"><span class="sec-dot" style="background:var(--teal-mid)"></span>§8-2-2 黏性</a>
    </div>
  </div>

  <!-- Repeat .toc-l1 block for each chapter; omit .toc-l2 if no sub-sections -->
</div>

<!-- SECTION TEMPLATE
     div nesting:  .page > .sec-COLOR > .section > .section-header / .card
     Every section opens exactly 2 divs (.sec-COLOR and .section)
     and closes exactly 2 divs at the end (</div></div>).
     NEVER nest another .sec-COLOR div inside a section.
-->
<div class="sec-purple" id="s1">  <!-- depth +1 -->
<div class="section">             <!-- depth +2 -->

  <div class="section-header">
    <div class="section-num">1</div>
    <h2>Section Title</h2>
  </div>

  <!-- Section-level banner callouts (ONLY these live outside a .card) -->
  <div class="callout intuition">
    <div class="callout-icon"></div>
    <div class="callout-body">
      <strong>直觉解释</strong>
      <p>...</p>
    </div>
  </div>

  <!-- Everything else goes inside a .card -->
  <div class="card">
    <h3>定义</h3>

    <!-- Formula box inside card -->
    <div class="fbox">
      <div class="flabel" style="color:var(--purple)">定义名称</div>
      <div class="frow">$$FORMULA$$</div>
      <div class="fnote">符号说明</div>
    </div>

    <!-- Derivation (collapsible) inside card -->
    <details>
      <summary>推导过程</summary>
      <div class="details-body">
        <div class="fbox">
          <div class="frow">$$STEP1$$</div>
          <div class="frow">$$STEP2$$</div>
        </div>
      </div>
    </details>
  </div>

  <!-- Worked example in its own card -->
  <div class="card">
    <h3>例题</h3>
    <div class="example-block">
      <div class="example-header">
        <span class="badge b-purple">例 1</span> 题目描述
      </div>
      <div class="example-body">
        <p>题目内容</p>
        <details>
          <summary>解答</summary>
          <div class="details-body">
            <div class="fbox">
              <div class="frow">$$SOLUTION$$</div>
            </div>
          </div>
        </details>
      </div>
    </div>
  </div>

  <!-- Mistake and exam callouts in their own card -->
  <div class="card">
    <div class="callout mistake">
      <div class="callout-icon"></div>
      <div class="callout-body">
        <strong>常见错误</strong>
        <ul><li>...</li></ul>
      </div>
    </div>
    <div class="callout exam">
      <div class="callout-icon"></div>
      <div class="callout-body">
        <strong>考试重点</strong>
        <p>...</p>
      </div>
    </div>
  </div>

</div>  <!-- closes .section   depth -1 -->
</div>  <!-- closes .sec-COLOR  depth -2 -->
<!-- END SECTION -->

<div style="text-align:center;color:var(--text3);font-size:12px;padding:24px 0 8px;border-top:1px solid var(--border);margin-top:20px;">
  TOPIC 学习笔记
</div>

</div><!-- closes .page -->

<!-- ── Floating section navigator ── -->
<button id="nav-btn" title="章节导航" aria-label="章节导航">≡</button>
<div id="nav-panel" role="navigation" aria-label="章节列表">
  <div class="nav-title">章节导航</div>
  <div id="nav-list"></div>
</div>

<script>
(function(){
  var SK = 'sp:' + location.pathname;

  /* ── Scroll position memory ── */
  function doRestore(y, tries){
    if(tries <= 0) return;
    var prev = window.scrollY;
    window.scrollTo({top: y, behavior:'instant'});
    /* content-visibility:auto leaves the page height ESTIMATED until a region is scrolled into, so a
       deep target clamps short; each scrollTo renders more (height grows), so retry on the next frame
       until we reach y — or stop making progress (clamped at the true end, prev unchanged). */
    if(Math.abs(window.scrollY - y) > 4 && window.scrollY !== prev)
      requestAnimationFrame(function(){ doRestore(y, tries - 1); });
  }
  function tryRestore(){
    var raw = localStorage.getItem(SK);
    if(raw !== null && +raw > 0){
      if(location.hash) history.replaceState(null, '', location.pathname + location.search);
      doRestore(+raw, 60);
    }
  }
  if(window.__katexDone) tryRestore();
  else window.addEventListener('katexdone', tryRestore, {once:true});
  window.addEventListener('load', function(){ setTimeout(tryRestore, 80); });
  window.addEventListener('pageshow', function(e){ if(e.persisted) setTimeout(tryRestore, 80); });

  var saving = false;
  window.addEventListener('scroll', function(){
    if(!saving){ saving = true;
      requestAnimationFrame(function(){
        if(window.scrollY > 0) localStorage.setItem(SK, window.scrollY);
        saving = false;
      });
    }
  }, {passive:true});


  /* ── Floating navigator: hierarchical heading tracking ── */
  var COLORS = {
    purple:'#534AB7', teal:'#0F6E56', coral:'#993C1D',
    amber:'#BA7517',  blue:'#185FA5', green:'#3B6D11', red:'#A32D2D'
  };
  if(window.matchMedia('(prefers-color-scheme:dark)').matches) COLORS = {
    purple:'#AFA9EC', teal:'#5DCAA5', coral:'#F0997B',
    amber:'#EF9F27',  blue:'#85B7EB', green:'#97C459', red:'#F09595'
  };

  var list  = document.getElementById('nav-list');
  var btn   = document.getElementById('nav-btn');
  var panel = document.getElementById('nav-panel');
  if(!list || !btn || !panel) return;

  /* anchors: ordered list of {el, link, level} for scroll tracking */
  var anchors = [];

  var secs = document.querySelectorAll(
    '[id].sec-purple,[id].sec-teal,[id].sec-coral,[id].sec-amber,[id].sec-blue,[id].sec-green,[id].sec-red'
  );
  secs.forEach(function(sec){
    var hdr = sec.querySelector('.section-header');
    if(!hdr) return;
    var num   = (hdr.querySelector('.section-num')||{}).textContent || '';
    var ttl   = (hdr.querySelector('h2')||{}).textContent || '';
    var cls   = (sec.className||'').match(/sec-(\w+)/);
    var color = cls ? (COLORS[cls[1]] || '#888') : '#888';

    /* L0: chapter row */
    var row = document.createElement('a');
    row.href = '#' + sec.id;
    row.style.cssText = 'display:flex;align-items:center;gap:8px;padding:7px 14px 5px;'+
      'font-size:13px;font-weight:600;color:inherit;text-decoration:none;'+
      'transition:background 0.1s;margin-top:2px;';
    var badge = document.createElement('span');
    badge.textContent = num;
    badge.style.cssText = 'min-width:22px;height:20px;border-radius:4px;font-size:10px;font-weight:700;'+
      'display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;padding:0 3px;'+
      'background:'+color+';color:#fff;';
    var lbl = document.createElement('span');
    lbl.textContent = ttl;
    lbl.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
    row.appendChild(badge); row.appendChild(lbl);
    row.addEventListener('click', function(){ panel.classList.remove('open'); });
    list.appendChild(row);
    anchors.push({el: hdr, link: row, level: 0, color: color});

    /* L1: sub-headings — collect section-header h2 siblings at card/h3/h4 level.
       We look for elements that bear an id (section sub-anchors assigned by TOC)
       OR card h3 headings (auto-assigned ids below). */
    /* Auto-assign ids to h3 headings that don't have one */
    sec.querySelectorAll('.card h3').forEach(function(h3, i){
      if(!h3.id) h3.id = sec.id + '-s' + i;
    });
    /* Also pick up explicit subsection anchors (h3 with class .subsec or just any h3 with id) */
    sec.querySelectorAll('.card h3[id]').forEach(function(h3){
      var sub = document.createElement('a');
      sub.href = '#' + h3.id;
      sub.style.cssText = 'display:flex;align-items:center;gap:7px;'+
        'padding:3px 14px 3px 32px;font-size:12px;color:var(--text2,#a8a69e);'+
        'text-decoration:none;transition:background 0.1s,color 0.1s;'+
        'border-left:2px solid transparent;margin-left:0;';
      var dot = document.createElement('span');
      dot.style.cssText = 'width:4px;height:4px;border-radius:50%;background:'+color+';'+
        'flex-shrink:0;opacity:0.5;transition:opacity 0.1s;';
      var slbl = document.createElement('span');
      slbl.textContent = h3.textContent.replace(/^\s*[\d§.]+\s*/, ''); /* strip leading numbers */
      slbl.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
      sub.appendChild(dot); sub.appendChild(slbl);
      sub.addEventListener('click', function(){ panel.classList.remove('open'); });
      list.appendChild(sub);
      anchors.push({el: h3, link: sub, level: 1, dot: dot, color: color});
    });
  });

  /* ── Scroll-based active tracking (more accurate than IntersectionObserver for dense headings) ── */
  var active = null;
  function setActive(a){
    if(active === a) return;
    if(active){
      active.link.style.background = '';
      if(active.level === 0){
        active.link.style.fontWeight = '600';
        active.link.style.color = '';
      } else {
        active.link.style.color = 'var(--text2,#a8a69e)';
        active.link.style.borderLeftColor = 'transparent';
        if(active.dot) active.dot.style.opacity = '0.5';
      }
    }
    active = a;
    if(!a) return;
    a.link.style.background = 'var(--bg3,#2c2c2a)';
    if(a.level === 0){
      a.link.style.fontWeight = '700';
      a.link.style.color = 'var(--text,#e8e6de)';
    } else {
      a.link.style.color = 'var(--text,#e8e6de)';
      a.link.style.borderLeftColor = a.color || '#378ADD';
      if(a.dot) a.dot.style.opacity = '1';
    }
    /* Scroll nav panel to keep active item visible */
    if(panel.classList.contains('open'))
      a.link.scrollIntoView({block:'nearest'});
  }

  function updateActive(){
    /* Find the last anchor whose top edge is above the 30% viewport mark */
    var threshold = window.innerHeight * 0.30;
    var best = null;
    for(var i = 0; i < anchors.length; i++){
      var rect = anchors[i].el.getBoundingClientRect();
      if(rect.top <= threshold) best = anchors[i];
      else break;
    }
    if(!best && anchors.length) best = anchors[0];
    setActive(best);
  }

  var ticking = false;
  window.addEventListener('scroll', function(){
    if(!ticking){ ticking = true; requestAnimationFrame(function(){ updateActive(); ticking = false; }); }
  }, {passive:true});
  /* Initial call after layout settles */
  setTimeout(updateActive, 300);
  window.addEventListener('katexdone', function(){ setTimeout(updateActive, 150); }, {once:true});

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    panel.classList.toggle('open');
    if(panel.classList.contains('open') && active)
      setTimeout(function(){ active.link.scrollIntoView({block:'nearest'}); }, 160);
  });
  document.addEventListener('click', function(e){
    if(!panel.contains(e.target) && e.target !== btn) panel.classList.remove('open');
  });
})();</script>

<!-- ── Keyboard a11y for horizontally-scrollable content ──
   A wide formula/table scrolls sideways, but a <div>/<table> isn't focusable, so a
   keyboard-only user can't reach it. This standalone block (independent of the nav script
   above, so it runs even if the nav is removed) tags ONLY elements that actually overflow as
   focusable scroll regions, and re-checks on resize so tab order isn't cluttered with
   formulas that fit. The :focus-visible ring is styled in the CSS. -->
<script>
(function(){
  function tagScrollables(){
    document.querySelectorAll('.katex-display, table').forEach(function(el){
      var over = el.scrollWidth - el.clientWidth > 2;
      if(over && el.tabIndex !== 0){
        el.tabIndex = 0; el.setAttribute('role','region');
        el.setAttribute('aria-label','可横向滚动'); el.dataset.scrollable = '1';
      } else if(!over && el.dataset.scrollable){
        el.removeAttribute('tabindex'); el.removeAttribute('role');
        el.removeAttribute('aria-label'); delete el.dataset.scrollable;
      }
    });
  }
  window.addEventListener('katexdone', function(){ setTimeout(tagScrollables, 200); }, {once:true});
  window.addEventListener('load', function(){ setTimeout(tagScrollables, 250); });
  var stt; window.addEventListener('resize', function(){ clearTimeout(stt); stt = setTimeout(tagScrollables, 250); }, {passive:true});
})();
</script>

<!-- ── Mobile formula-fit (MANDATORY) ──
   Horizontal scroll on a phone READS AS BROKEN: a wide display formula stops part-way, its
   left half is clipped, and a lone √ vinculum looks like a stray over-line (real user report).
   So instead of scrolling, shrink any overflowing display formula to fit its column. -->
<script>
(function(){
  function fit(){
    document.querySelectorAll('.katex-display').forEach(function(el){
      var avail = el.clientWidth; if(avail < 10) return;            // not yet rendered (content-visibility) → skip
      var k = el.querySelector('.katex'); if(!k) return;
      if(!k.dataset.fitBase) k.dataset.fitBase = parseFloat(getComputedStyle(k).fontSize) || 16;
      k.style.fontSize = k.dataset.fitBase + 'px';                  // reset, then re-measure
      var need = k.scrollWidth;
      if(need > avail + 1){
        var s = Math.max(avail / need, 0.4) * 0.99;                 // floor 0.4 keeps it legible
        k.style.fontSize = (k.dataset.fitBase * s) + 'px';
      }
    });
  }
  window.addEventListener('katexdone', function(){ setTimeout(fit, 60); setTimeout(fit, 300); }, {once:true});
  window.addEventListener('load', function(){ setTimeout(fit, 200); });
  var rt; window.addEventListener('resize', function(){ clearTimeout(rt); rt = setTimeout(fit, 200); }, {passive:true});
  var st; window.addEventListener('scroll', function(){ clearTimeout(st); st = setTimeout(fit, 160); }, {passive:true});
})();
</script>

</body>
</html>
```

### Mobile formula-fit + verification (MANDATORY — learned 2026-06-23)

Horizontal-scrolling a wide display formula is fine on desktop but **reads as broken on a phone**:
the formula stops part-way, its left half is clipped, a lone `\sqrt` vinculum looks like a stray
over-line, and the thin scrollbar reads as a misplaced grey line. Two defenses, both required:

1. **The fit script above** (in the template `<body>` foot) auto-shrinks any overflowing
   `.katex-display` to fit its column. Copy it verbatim.
2. **Split "one row, many equations".** Never put `$$A=…,\quad B=…,\quad C=…$$` on one `.frow`;
   give each equation its own `<div class="frow">$$…$$</div>`. The fit script is the safety net;
   short rows are the real fix.

**Verify before shipping (do NOT claim "done" on static/numeric gates alone):** serve the file
(a local `http.server` — `file://` is blocked in headless Chromium) and render it at **390 px
width**. Assert every `.katex-display` has `scrollWidth - clientWidth ≤ 2` (overflow = 0) and
`.katex-error` count = 0. **Also assert text columns didn't collapse:** every `.step-body` (and
`.example-body`, `.callout-body`) must have a sane rendered width — `getBoundingClientRect().width`
well above a few characters (e.g. `> 120px` at 390 px viewport). A near-zero body width means CJK
has shattered to one character per line (a block mis-nested as a `.step` flex child squeezing the
text — see the `.step` CSS note). **Measuring only formula overflow misses this** — it shipped a
real "vertical text" bug because the earlier render-check probed `.katex-display` but never the
prose body width. Then **screenshot every figure and eyeball it** — the numeric/static
gates cannot see a reversed phasor, a missing component, or an invisible arrow. Cache-bust with
`?v=N` after each rebuild, and **re-send the file to the user** after edits (they may be looking
at a stale copy).

---

## Layout Consistency Rule (MANDATORY)

**All block-level components must be placed inside a `.card` wrapper.** Never place `.fbox`, `.callout`, `.big-formula`, `.example-block`, or `<details>` directly inside a `<div class="section">` — doing so changes their apparent width because `.card` adds 26px side padding while a bare section div has none, producing visually inconsistent block widths.

The only elements that live directly inside `.section` (outside any `.card`) are:

- The `.section-header` (number badge + title)
- Another `.card`
- A `.callout` that acts as a section-level banner (e.g. the "this is the exam core" red callout at the top of a section) — in this case add `margin: 0 0 16px` to keep spacing consistent

Everything else — formula boxes, derivations, examples, tables, sub-headings — goes inside a `.card`.

```html
<!-- ✓ Correct: fbox inside card -->
<div class="sec-blue" id="gauss">
<div class="section">
  <div class="section-header">...</div>

  <div class="callout exam">...</div>          <!-- section-level banner: OK outside card -->

  <div class="card">
    <h3>定理陈述</h3>
    <div class="fbox">...</div>               <!-- fbox inside card: consistent width -->
    <div class="big-formula">...</div>        <!-- same -->
    <details>...</details>                    <!-- same -->
  </div>

  <div class="card">
    <h3>例题</h3>
    <div class="example-block">...</div>      <!-- inside card -->
  </div>
</div>
</div>

<!-- ✗ Wrong: fbox directly in section, bypassing card padding -->
<div class="section">
  <div class="section-header">...</div>
  <div class="fbox">...</div>   <!-- width differs from fbox inside card → inconsistent -->
</div>
```

## Callout Quick Reference

| Class | Icon | Use for |
|---|---|---|
| `note` | 💡 | Important notes, key facts |
| `tip` | ✦ | Clever tricks, shortcuts |
| `warn` | ⚠ | Pitfalls, conditions that must hold |
| `exam` | ★ | Exam tips, what to memorize |
| `intuition` | 🔍 | Physical/geometric intuition, analogies |
| `mistake` | ✗ | Common errors students make |
| `derivation` | ∴ | Summary of a derivation result |

## Section Color Assignment Guide

Assign colors based on conceptual role, not sequence:

| Color | Best for |
|---|---|
| `sec-purple` | Foundational definitions, prerequisites |
| `sec-teal` | Geometric or spatial concepts (gradient, vectors) |
| `sec-coral` | Scalar-producing operations (divergence, norms) |
| `sec-amber` | Rotational/dynamic concepts (curl, angular quantities) |
| `sec-blue` | Major theorems and integral laws |
| `sec-green` | Applications, worked-out results |
| `sec-red` | Practice problems, exams |
| neutral `.section-num` style | Summary/comparison sections |

## Big Formula Usage

Reserve `.big-formula.highlight` (bordered, colored background) for the single most important equation in a section — typically the key theorem. Use plain `.big-formula` for important but not defining results.

```html
<!-- Most important: highlighted -->
<div class="big-formula highlight" style="border-color:rgba(24,95,165,0.5);background:var(--blue-light);">
  $$\oiint_S \boldsymbol{F}\cdot\mathrm{d}\boldsymbol{S} = \iiint_V \nabla\cdot\boldsymbol{F}\,\mathrm{d}V$$
</div>

<!-- Important but not the star: plain -->
<div class="big-formula">
  $$\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} + \frac{\partial^2 f}{\partial z^2}$$
</div>
```

---

## SVG Diagram Rules (CRITICAL — do not skip)

**Before drawing: should this be an SVG at all?** If the problem/source already came with a figure, **embed the ORIGINAL image instead of redrawing it** — even if it looks simple (decision rule: `problem-solutions.md` §3). A redraw of a figure you already have only risks dropping an element or misplacing labels. These rules are for the *other* case: a diagram you must draw because there is no source figure.

These rules fix three recurring problems: oversized arrows that obscure labels, unreadable proportions, and **mysterious offset** — elements that each look right on their own but no longer line up because several coordinate mechanisms (viewBox mapping, percentage lengths, CSS transforms, text baselines, marker reference points) got mixed. Stay inside the safe-subset below and the offset stops happening; the arrow/label rules after it handle the other two.

### SVG-safe-subset (avoid mysterious offset)

LLM-drawn SVGs drift when several coordinate mechanisms get mixed: viewBox mapping, percentage lengths, CSS
transforms, text baselines, marker reference points. Each element ends up "correct on its own" but no longer
aligned. Stay inside this narrow subset and the offset becomes a non-issue. Our own diagram examples already
follow it — copy them.

- **One root `<svg>` per figure, no nested `<svg>`.** A nested `<svg>` opens a *new* coordinate system and
  viewport; use `<g>` for grouping/layering instead. (The favicon `<svg>` in `<head>` does not count — it is a
  separate `data:` image.)
- **Always write `viewBox` + a matching `width`.** Use `viewBox="0 0 W H"` and a `width` with the **same aspect
  ratio** (e.g. `viewBox="0 0 300 200" width="280"`), as the examples do. Mismatched ratios let
  `preserveAspectRatio` letterbox the content, and that reads as "shifted", not "scaled".
- **Absolute numbers only — never `%` geometry.** All `x` `y` `cx` `cy` `x1` `y1` `x2` `y2` `width` `height` on
  shapes must be plain numbers in the viewBox coordinate system. A percentage resolves against the nearest SVG
  viewport, which silently means the wrong box.
- **No `foreignObject`.** Put any rich/HTML content (formulas, paragraphs) in normal HTML *below* the figure
  (e.g. a `.fbox`), never inside the SVG.
- **No CSS `transform` / `transform-origin` on SVG elements.** The CSS form is not equivalent to the SVG
  attribute and its reference box is browser-dependent. To rotate, use the **SVG attribute with an explicit
  centre**: `transform="rotate(30 150 100)"` (angle, then cx cy). Keep to at most one `<g transform="…">` layer.
- **Place every `<text>` deliberately — don't leave centring to chance.** Set `text-anchor` (`middle` to centre
  horizontally). For the vertical position, either set `dominant-baseline` (`middle` / `central`) as in the
  side-label templates above, **or** place `y` against the default alphabetic baseline with a few px of
  clearance (what the examples do). What fails is the half-measure: no anchor and an un-tuned `y` lands the
  label wherever the font's baseline heuristics put it.
- **Markers: reuse our marker, don't invent one.** The arrow marker defined above (`viewBox="0 0 10 10"
  refX="9" refY="5" markerWidth="5" markerHeight="5"`) already declares explicit `viewBox`/`refX`/`refY` and a
  small size — exactly what keeps the arrowhead glued to the line endpoint. Use it via `marker-end="url(#arr)"`.
  If you ever define a new marker, copy those explicit attributes; do not rely on marker defaults.

**Before shipping a figure, render and look.** The static scan (`build_and_check.py`) WARNs on the high-risk
constructs (nested `<svg>`, `%` geometry, `foreignObject`, CSS `transform`/`transform-origin`), but it cannot
see whether things actually *line up*. Open the finished file — you already do this for the KaTeX error banner —
and glance at each diagram: nothing pushed outside the box, no label sitting on an arrowhead, no same-hue text
vanishing (check dark mode too), every arrowhead attached. This single-engine "render and look" is the
skill-sized substitute for a cross-browser screenshot-diff pipeline: keep the cheap structural check static, and
replace the expensive pixel-diff with one human/agent glance at the rendered figures.

### Arrow size

**Arrow markers must be small.** The arrowhead should look like a tip, not a filled triangle dominating the line. Use these exact marker dimensions and never increase them:

```svg
<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M1 1 L9 5 L1 9" fill="none" stroke="context-stroke"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

Key values:
- `markerWidth="5" markerHeight="5"` — never exceed 6. Values of 10+ produce the oversized arrows seen in the bad example.
- `refX="9"` — positions the tip precisely at the line endpoint so the shaft doesn't poke through.
- Open chevron (`fill="none"`) — lighter and cleaner than a filled triangle.
- `context-stroke` — the head inherits the line color automatically; no color mismatch.

### Proportions and label clearance

- **Label text must be readable at normal zoom.** Use `font-size="12"` for callout labels alongside arrows, `font-size="13"` for component names inside boxes. Never go below 11.
- **Leave at least 14px between an arrowhead and any text label.** Place labels *beside* the arrow, not on top of it. For vertical arrows, the label goes to the right; for horizontal arrows, the label goes above.
- **Arrow length should be proportional to what it represents.** A reaction force arrow and a weight arrow on the same diagram should be similar lengths unless magnitude difference is the point. Do not draw arrows that are longer than the objects they act on.
- **Objects (boxes, shapes) must be visually larger than the arrows on them.** If the arrow is taller than the box it points to, shrink the arrow or enlarge the box.

### Text contrast inside boxes & flowcharts (CRITICAL — readability)

A recurring bug: a box (flowchart node, legend, callout drawn in SVG) is filled with a tint of
an accent colour, and its **text is set to the same accent hue**, so the label is nearly
invisible — worst in dark mode, where a saturated label on a same-hue tint can fall to ~1.5:1.

**Rules — never put accent-coloured text on a same-hue fill:**

- **Saturated/solid coloured fill** (e.g. `fill="#534AB7"`) → text must be **white / near-white**
  (`fill="#fff"`), never the accent itself.
- **Light/pale tint fill** → text must be a **dark** shade of the hue (or `var(--text)`), not the
  mid/base accent. Aim for ≥ 4.5:1; check a borderline pair before shipping.
- **One hue per box does double duty at most** — use the accent for the *border* and a
  *neutral/contrasting* colour for the *text*; do not paint border, fill, and text the same hue.
- **SVG `<text>` hardcoded colours do NOT follow dark mode.** A colour readable on the light page
  background may vanish on the dark one (and vice-versa). Either pick a colour that clears 4.5:1
  on **both** `#ffffff` and `#1e1e1c`, or drive fills from the CSS palette: give the `<svg>`
  `color:var(--text)` and use `fill="currentColor"` for text, `stroke="currentColor"` for lines.
- For **HTML** flowchart boxes (divs, not SVG), prefer the design-system vars — `background:var(--purple-light); color:var(--purple-dark)` — which are now dark-mode-safe after the contrast fix in the dark `:root`. Do **not** write `color:var(--purple)` text on a `var(--purple-light)` box.

```svg
<!-- ✗ wrong: teal text on a teal tint — invisible in dark mode -->
<rect x="10" y="10" width="160" height="44" rx="8" fill="#04342C" stroke="#1D9E75"/>
<text x="90" y="37" fill="#1D9E75" text-anchor="middle" font-size="13">求 约束反力</text>

<!-- ✓ right: white text on a solid fill, OR currentColor that adapts -->
<rect x="10" y="10" width="160" height="44" rx="8" fill="#0F6E56" stroke="#0F6E56"/>
<text x="90" y="37" fill="#fff" text-anchor="middle" font-size="13">求 约束反力</text>
```

### Label placement template for force diagrams

```svg
<!-- Vertical upward force with label to the right -->
<line x1="200" y1="160" x2="200" y2="90" stroke="#1D9E75" stroke-width="2"
      marker-end="url(#arr)"/>
<text x="212" y="128" font-size="12" fill="#1D9E75" dominant-baseline="middle">N</text>

<!-- Vertical downward force with label to the right -->
<line x1="200" y1="160" x2="200" y2="230" stroke="#D85A30" stroke-width="2"
      marker-end="url(#arr)"/>
<text x="212" y="198" font-size="12" fill="#D85A30" dominant-baseline="middle">G</text>

<!-- Horizontal force with label above -->
<line x1="240" y1="160" x2="310" y2="160" stroke="#378ADD" stroke-width="2"
      marker-end="url(#arr)"/>
<text x="275" y="150" font-size="12" fill="#378ADD" text-anchor="middle">F</text>
```

### SVG `<text>` elements must use Unicode — never `$...$` KaTeX syntax

KaTeX is a JavaScript library that scans the HTML DOM after page load. It **cannot enter SVG** — SVG `<text>` nodes are not part of the HTML text flow, so any `$...$` or `$$...$$` inside an SVG will be displayed as raw literal characters, not rendered as math.

**Rule: all labels, subscripts, and symbols inside `<svg>` must be written directly in Unicode.**

| What you want | Wrong (KaTeX won't run here) | Correct (Unicode) |
|---|---|---|
| Subscript number | `$v_1$` | `v₁` |
| Subscript letter | `$T_p$` | `Tₚ` |
| Superscript | `$v^2$` | `v²` |
| Greek letters | `$\omega$`, `$\theta$`, `$\Delta$` | `ω`, `θ`, `Δ` |
| Arrow over letter | `$\vec{v}$` | `v⃗` or just `v` with an arrow drawn separately |
| Fractions / complex math | `$\frac{1}{2}mv^2$` | Avoid in SVG — put the formula in a `.fbox` below the diagram instead |
| Infinity | `$\infty$` | `∞` |
| Proportional | `$\propto$` | `∝` |
| Approximately | `$\approx$` | `≈` |
| Plus-minus | `$\pm$` | `±` |

**Unicode subscript/superscript digits and letters:**

```
Subscripts:   ₀₁₂₃₄₅₆₇₈₉  ₐₑₒₓₙₘₖₗ  (limited — not all letters exist)
Superscripts: ⁰¹²³⁴⁵⁶⁷⁸⁹  ⁿ
Greek:        α β γ δ ε ζ η θ ι κ λ μ ν ξ π ρ σ τ υ φ χ ψ ω
              Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Π Ρ Σ Τ Υ Φ Χ Ψ Ω
Common:       → ← ↑ ↓ ↗ ↘  ∝ ≈ ≠ ≤ ≥ ∞ ± × ÷ √ ∫ ∑ ∂ ∇
```

**If a label needs complex math that can't be expressed in Unicode, do not put it in the SVG.** Instead, place a simplified Unicode label in the SVG (e.g. `"f(v)"`) and put the full formula in a `.fbox` immediately below the diagram with a text explanation like "其中 $f(v)$ 的完整表达式见上方公式框".

- [ ] `markerWidth` and `markerHeight` are both ≤ 6
- [ ] Every arrow label is offset at least 14px from the arrow shaft
- [ ] No label is hidden behind or on top of an arrow or shape
- [ ] Object boxes/shapes are visually larger than the arrows on them
- [ ] All text is ≥ 11px font-size
- [ ] No box/flowchart text shares its fill's hue (white on solid fill, dark on pale tint; ≥4.5:1, checked in dark mode too)

---

## Vector Notation in KaTeX

Vectors in inline and display math must use **arrow notation** for single-letter symbols, which is unambiguous and standard in Chinese university physics/math courses. Bold alone (`\boldsymbol{}`) is hard to distinguish from a regular letter in body text.

> **Use `\overrightarrow{}` in prose, not `\vec{}` (learned 2026-06-23).** KaTeX's `\vec` arrow is
> a tiny combining glyph that is **nearly invisible at body/mobile font sizes** — a real user
> twice reported "公式没标向量" when the source did use `\vec`. Prefer `\overrightarrow{U}` /
> `\overrightarrow{U}_R` in running text and figure captions, where the arrow must be obvious.
> `\vec` is acceptable only inside large display formulas. And when you write a vector *sum* in
> prose, state the magnitude relation explicitly so it can't be misread as scalar addition, e.g.
> "$\overrightarrow{U}=\overrightarrow{U}_R+\overrightarrow{U}_L$（矢量和，$U\ne U_R+U_L$）".

### Rules

| Context | Notation | KaTeX | Example |
|---|---|---|---|
| Single-letter vector (force, field, position…) | Arrow over letter | `\vec{F}`, `\vec{r}`, `\vec{B}` | $\vec{F} = m\vec{a}$ |
| Unit vector | Hat over letter | `\hat{r}`, `\hat{n}` | outward normal $\hat{n}$ |
| Multi-letter / operator vector (nabla, bold name) | Bold | `\boldsymbol{\nabla}`, `\mathbf{grad}` | $\boldsymbol{\nabla} f$ |
| Vector with hat + bold (physics convention) | Hat bold | `\hat{\boldsymbol{r}}` | $\hat{\boldsymbol{r}} = \vec{r}/r$ |
| Scalar magnitude of a vector | No decoration | `F`, `r`, `|\vec{F}|` | $F = |\vec{F}|$ |

### Correct vs wrong

```
✓  \vec{F} = m\vec{a}          →  F⃗ = ma⃗   (arrow clearly visible)
✗  \boldsymbol{F} = m\boldsymbol{a}  →  **F** = m**a**  (bold invisible in body text)

✓  \vec{E} = -\nabla\varphi    →  E⃗ = −∇φ
✗  \mathbf{E} = -\nabla\varphi →  **E** = −∇φ  (ambiguous)

✓  the magnitude is r = |\vec{r}|
✗  the magnitude is r = |\boldsymbol{r}|
```

### When bold is still appropriate

- `\nabla` and its combinations (`\nabla\cdot`, `\nabla\times`, `\nabla^2`) — these are operators, not vectors; no arrow needed.
- Named vector quantities written out in words, e.g. `\mathbf{curl}\,\vec{F}`.
- Matrices and tensors: `\mathbf{A}`, `\boldsymbol{\sigma}`.

---

## KaTeX Pre-defined Macros (always available in generated notes)

These macros are registered in the `renderMathInElement` call in the HTML template. Use them freely:

| Macro | Renders as | Use for |
|---|---|---|
| `\dj` | đ | Inexact differential (heat đQ, work đW) |
| `\degree` | °  | Degree symbol with correct base: `20\degree` → 20° |
| `\d` | d (upright) | Exact differential: `\d U`, `\d t` |
| `\e` | e (upright) | Euler's number: `\e^{x}` |
| `\i` | i (upright) | Imaginary unit |
| `\cdotp` | · | Centre dot for unit products: `\text{J}\cdotp\text{mol}` (alias of `\cdot`) |
| `\unit` | (upright text) | siunitx-style unit text: `\unit{m/s}` → upright `m/s` |
| `\celsius` | °C | Degrees Celsius with correct base: `37\celsius` → 37°C |
| `\bm` | **bold** | Bold symbol (alias of `\boldsymbol`); for single-letter vectors prefer `\vec{}` |

These nine macros are registered in the template's `renderMathInElement` call, so they
render correctly in every generated file. `build_and_check.py` is **macro-aware**: a
command your file registers as a macro is not flagged, so using `\celsius` / `\unit` /
`\bm` here is fine. The one caveat is portability — if you paste a fragment into a page
that does **not** carry these macro definitions, it breaks; inside our self-contained
single-file output that never happens.

## KaTeX Forbidden Commands (will produce red error text)

Never use these — they are LaTeX packages KaTeX does not support and the template does
**not** register as macros (contrast the macro table above, whose commands are safe):

| Do NOT write | Write instead |
|---|---|
| `^\circ\text{C}` without base | `{}^\circ\text{C}` or `\celsius` |
| `\SI{9.8}{m/s^2}` | `9.8\,\text{m/s}^2` |
| `\qty{1}{J}` | `1\,\text{J}` |
| `\si{...}` | spell the unit in `\text{}` |
| `\tensor{}` | Use index notation |
| `\cancel{}` | Use `\not` or rephrase |
| `\ket{}`, `\bra{}` | `|\psi\rangle`, `\langle\psi|` |

---

## CRITICAL: Never use `\boxed{}` inside `.fbox` / `.big-formula` / `.callout`

**Rule:** Do NOT wrap any formula in `\boxed{...}` when that formula sits inside an HTML container that already provides a visible box (`.fbox`, `.big-formula`, `.big-formula.highlight`, `.callout`, `.answer-box`, `.example-block`).

### Why

KaTeX renders `\boxed{...}` as `<span class="mord boxbox">` with `border-style:solid` and internal padding. When the wrapped formula contains tall constructs — `\dfrac`, `\sqrt`, `\frac` over 2 lines, matrices — KaTeX's height calculation for the box mis-estimates the content's vertical extent. The result, especially in dark mode and inside containers with their own `background-color`:

- The `\boxed{}` border renders at the wrong position
- The interior of the box appears as a solid grey rectangle that **covers** the actual formula text
- Only the bottom of the formula (e.g. the denominator of a `\dfrac`) peeks out below the grey box
- This is **NOT** a CSS-fixable overflow issue — it is a rendering bug inside KaTeX

This issue is silent: no `katex-error` span is produced, so the post-generation Check 1 (KaTeX error spans) will not catch it. The formula appears partially or entirely hidden behind a grey rounded rectangle in the final HTML.

### What to do instead

The HTML wrappers ARE the box. They already provide a visible border and a colored background. Adding `\boxed{}` on top is redundant emphasis that breaks rendering:

| WRONG | CORRECT |
|---|---|
| `<div class="big-formula highlight">$$\boxed{F=ma}$$</div>` | `<div class="big-formula highlight">$$F=ma$$</div>` |
| `<div class="fbox"><div class="frow">$$\boxed{T=\dfrac{G}{2\cos\alpha}}$$</div></div>` | `<div class="fbox"><div class="frow">$$T=\dfrac{G}{2\cos\alpha}$$</div></div>` |
| `<div class="answer-box"><p>$\boxed{x=5}$</p></div>` | `<div class="answer-box"><p>$x=5$</p></div>` |

Visual emphasis is provided by the wrapping `<div>` styling — colored background, border, padding. The formula reads cleanly and renders reliably.

### When `\boxed{}` IS acceptable

Only inside **plain prose** where there is no surrounding HTML box, e.g. a result mentioned mid-paragraph:

```html
<p>由对称性可立即得到 $\boxed{T_A=T_B}$，无需进一步计算。</p>
```

Even here, prefer `<strong>` tags or a `.fbox` for emphasis when the result is important enough to highlight.

### Post-generation check (MANDATORY)

After concatenating all parts, verify no `\boxed` appears anywhere in the file. Since boxed should be avoided everywhere except rare prose use, the strictest check is just:

```bash
grep -n '\\boxed' /mnt/user-data/outputs/<file>.html
```

If matches are found, decide for each: if inside a `.fbox` / `.big-formula` / `.callout` / `.answer-box`, REMOVE the `\boxed{...}` wrapper (keep the inner formula). If inside plain prose, leave it.

### Recovery: bulk-strip `\boxed{}`

If many `\boxed{}` slipped in, run this Python snippet to remove all of them while preserving inner content (handles nested braces):

```python
def strip_boxed(s):
    out, i = [], 0
    while i < len(s):
        if s[i:i+7] == r'\boxed{':
            depth, j = 1, i+7
            while j < len(s) and depth > 0:
                if s[j] == '{': depth += 1
                elif s[j] == '}': depth -= 1
                j += 1
            if depth == 0:
                out.append(strip_boxed(s[i+7:j-1])); i = j
            else:
                out.append(s[i]); i += 1
        else:
            out.append(s[i]); i += 1
    return ''.join(out)

with open(path, 'r', encoding='utf-8') as f: text = f.read()
with open(path, 'w', encoding='utf-8') as f: f.write(strip_boxed(text))
```

### CSS reminder — do NOT add `display:inline-block` to `.katex`

Some "fixes" found online suggest `.katex-display > .katex { display: inline-block }` to make tall formulas wrap properly. **This makes the `\boxed{}` issue worse** by forcing KaTeX's outer span into inline-block layout, which interacts badly with the `\boxed{}` border. The default block layout for `.katex-display > .katex` is correct — leave it alone.

---

## Self-test quiz widget (interactive active-recall — optional)

A `.quiz` card turns the end of a chapter into **active recall** instead of passive
re-reading: each question grades on click (green correct / red wrong), reveals its
explanation, updates a running score, and remembers answers in `localStorage`. It is
**self-contained** — pure HTML/CSS/JS in the single file, no dependency, no account —
so it fits the "one HTML, offline, owned by the student" model. KaTeX renders inside
stems, options, and explanations.

Use it as an **optional** closing card in MODE A / MODE B notes (a `本章自测` after the
summary). Keep it to 3–8 questions per chapter; every option and explanation may contain
`$…$` math. Set `data-answer` to the **0-based index** of the correct option.

### CSS (add to the `<style>` block)

```css
/* ── Self-test quiz widget ── */
.quiz{--accent:var(--purple);--accent-light:var(--purple-light)}
.quiz-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.quiz-head .quiz-title{font-size:13px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.06em}
.quiz-score{font-size:13px;font-weight:700;color:var(--text2);background:var(--bg3);border-radius:20px;padding:3px 12px;white-space:nowrap}
.quiz-q{border:1px solid var(--border);border-radius:9px;padding:14px 16px;margin-bottom:12px;background:var(--bg)}
.quiz-q:last-child{margin-bottom:0}
.quiz-stem{font-size:14px;font-weight:600;margin-bottom:10px}
.quiz-stem .qn{display:inline-flex;align-items:center;justify-content:center;min-width:22px;height:22px;border-radius:6px;
  background:var(--accent-light);color:var(--accent);font-size:12px;font-weight:700;margin-right:8px}
.quiz-opt{display:block;width:100%;text-align:left;border:1px solid var(--border);background:var(--bg2);color:var(--text);
  border-radius:7px;padding:9px 13px;margin:6px 0;font:inherit;font-size:13.5px;cursor:pointer;transition:background .12s,border-color .12s}
.quiz-opt:hover:not(:disabled){background:var(--bg3)}
.quiz-opt:disabled{cursor:default}
.quiz-opt .mk{float:right;font-weight:700}
.quiz-opt.correct{background:var(--green-light);border-color:rgba(59,109,17,.5);color:var(--green-dark)}
.quiz-opt.wrong{background:var(--red-light);border-color:rgba(163,45,45,.45);color:var(--red-dark)}
.quiz-explain{display:none;margin-top:8px;font-size:13px;color:var(--text2);background:var(--bg3);
  border-left:3px solid var(--accent);border-radius:0 7px 7px 0;padding:9px 13px;line-height:1.7}
.quiz-q.answered .quiz-explain{display:block}
.quiz-reset{margin-top:6px;font-size:12px;color:var(--text3);background:none;border:none;cursor:pointer;text-decoration:underline}
```

### HTML pattern (one `.quiz` card; `data-answer` = 0-based correct index)

```html
<div class="card quiz" data-quiz="ch5-selftest">
  <div class="quiz-head">
    <span class="quiz-title">★ 本章自测</span>
    <span class="quiz-score" data-score>0 / 3</span>
  </div>

  <div class="quiz-q" data-answer="1">
    <div class="quiz-stem"><span class="qn">1</span>理想气体等温膨胀过程中，下列哪个量保持不变？</div>
    <button class="quiz-opt">内能增加</button>
    <button class="quiz-opt">温度 $T$ 不变，故内能 $U$ 不变</button>
    <button class="quiz-opt">系统不做功</button>
    <div class="quiz-explain">等温过程 $T$ 不变，理想气体内能只是温度的函数，故 $\Delta U=0$。</div>
  </div>

  <!-- more .quiz-q blocks … -->
</div>
```

To tint a quiz with a section colour, set `style="--accent:var(--teal);--accent-light:var(--teal-light)"` on the `.quiz` card.

### JS (add ONE copy before `</body>`, after the nav script)

```html
<script>
/* Self-test quiz: click an option → grade, reveal explanation, update score,
   persist per-question result in localStorage. Self-contained, no dependencies. */
(function(){
  document.querySelectorAll('.quiz').forEach(function(quiz){
    var key='quiz:'+location.pathname+':'+(quiz.dataset.quiz||'q');
    var saved={};
    try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
    var qs=[].slice.call(quiz.querySelectorAll('.quiz-q'));
    var scoreEl=quiz.querySelector('[data-score]');
    function updateScore(){
      var correct=qs.filter(function(q){return q.dataset.result==='1'}).length;
      var done=qs.filter(function(q){return q.dataset.result!==undefined}).length;
      if(scoreEl) scoreEl.textContent=correct+' / '+qs.length+(done<qs.length?'（已答 '+done+'）':'');
    }
    function grade(q,picked){
      var ans=+q.dataset.answer, opts=q.querySelectorAll('.quiz-opt');
      opts.forEach(function(o,i){
        o.disabled=true;
        if(i===ans){o.classList.add('correct');o.querySelector('.mk')||o.insertAdjacentHTML('beforeend','<span class="mk">✓</span>');}
        else if(i===picked){o.classList.add('wrong');o.insertAdjacentHTML('beforeend','<span class="mk">✗</span>');}
      });
      q.classList.add('answered');
      q.dataset.result=(picked===ans)?'1':'0';
      saved[[].indexOf.call(qs,q)]=picked;
      try{localStorage.setItem(key,JSON.stringify(saved))}catch(e){}
      updateScore();
    }
    qs.forEach(function(q,qi){
      q.querySelectorAll('.quiz-opt').forEach(function(o,i){
        o.addEventListener('click',function(){if(!q.classList.contains('answered'))grade(q,i);});
      });
      if(saved[qi]!==undefined) grade(q,saved[qi]);
    });
    updateScore();
    var reset=document.createElement('button');
    reset.className='quiz-reset';reset.textContent='重做本测';
    reset.addEventListener('click',function(){try{localStorage.removeItem(key)}catch(e){}location.reload();});
    quiz.appendChild(reset);
  });
})();
</script>
```

Validation: the static checks treat a quiz as ordinary cards/divs, so `build_and_check.py`
covers it; confirm the answer key by opening the file and clicking through once.

---

## Anki flashcard deck (optional export)

The notes can carry their own spaced-repetition deck **without breaking the single-file
model**: embed a hidden block of plain HTML cards (NOT JSON — backslashes are literal in
HTML, so `$\tfrac{3}{2}R$` needs no escaping; in JSON `\t`/`\n` would silently corrupt
`\tfrac`/`\nabla`). It is invisible in the page; `scripts/make_anki.py` exports it to an
Anki-importable TSV on demand.

```html
<!-- place once, anywhere in the body; the `hidden` attribute keeps it off-screen -->
<div id="anki-deck" hidden>
  <div class="anki-card" data-tags="热学 第一定律">
    <div class="anki-front">等温过程理想气体内能如何变化？</div>
    <div class="anki-back">$\Delta U = 0$（内能只是温度的函数，$T$ 不变）</div>
  </div>
  <div class="anki-card" data-tags="热学 热容">
    <div class="anki-front">单原子理想气体定容摩尔热容 $C_{V,m}$？</div>
    <div class="anki-back">$$C_{V,m}=\tfrac{3}{2}R$$（3 个平动自由度）</div>
  </div>
</div>
```

Write one card per high-value fact/formula/pitfall; use ordinary `$…$` / `$$…$$` math.
Export (also pulls in any `.quiz` questions as cards):

```bash
python3 scripts/make_anki.py <notes>.html            # → <notes>.tsv
```

The TSV is `front <TAB> back <TAB> tags` with a `#separator:tab` / `#html:true` /
`#tags column:3` header; math is converted to Anki's MathJax (`\(…\)` / `\[…\]`) so cards
render on import (Anki → File → Import → Fields separated by Tab). Add `--no-quiz` to
export only the authored deck.

---

## Source citation tag `.src-ref` (for source-grounded fidelity mode)

A small, muted badge that anchors a formula or conclusion to its exact place in the
source book, so the student can verify every claim against the original — the
"source-grounded" trust model. Use it next to an `.fbox` label or right after a stated
result.

```css
.src-ref{display:inline-block;font-size:11px;font-weight:600;color:var(--text3);
  background:var(--bg3);border:1px solid var(--border);border-radius:4px;
  padding:1px 7px;margin-left:8px;vertical-align:middle;letter-spacing:.02em;white-space:nowrap;}
.src-ref::before{content:"\1F4D6";margin-right:4px;opacity:.8;}
/* Banner shown at the top of a fidelity-mode page */
.fidelity-banner{font-size:12.5px;color:var(--text2);background:var(--bg2);
  border:1px dashed var(--border);border-radius:8px;padding:8px 14px;margin-bottom:18px;text-align:center;}
```

```html
<div class="fbox">
  <div class="flabel" style="color:var(--blue)">高斯定理 <span class="src-ref">见课本 p.123 式(5-7)</span></div>
  <div class="frow">$$\oiint_S \vec{E}\cdot\mathrm{d}\vec{S} = \frac{q}{\varepsilon_0}$$</div>
</div>

<!-- once, under the header -->
<div class="fidelity-banner">忠实模式：每个公式/结论都标注了课本出处，可逐条对照原书核验。</div>
```

**Hard rule (honesty):** only ever write a page/equation number you actually have from
the extracted source. If you did not read that page, omit the `.src-ref` — never invent a
citation. A fabricated page number is worse than none.

---

## MODE A note components (elective badge · figure reference · example card)

Three small components used by MODE A study notes. Add the CSS to the `<style>` block (it is
part of the Full CSS contract, repeated here so MODE A has everything in one place).

### Elective badge

Sections/problems marked `*`, `★`, or 选学/选读 are **elective** — the student hasn't studied
them. Skip them entirely unless they cross-reference core material or are commonly tested; if
included, keep them to one short card, never at core depth, and tag every included item:

```css
.elective-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: var(--amber-dark);
  background: var(--amber-light);
  border: 1px solid var(--amber);
  border-radius: 4px;
  padding: 1px 6px;
  margin-left: 6px;
  vertical-align: middle;
  letter-spacing: 0.04em;
}
```

Usage: `<h3 id="sX-X">§X.X 节标题 <span class="elective-badge">★ 选学</span></h3>`.
In the TOC, append ` ★` (plain text) after the title of any elective section link.

### Figure reference (MODE A only)

In MODE A do **not** draw SVG diagrams or embed base64 images unless the user explicitly asks —
write an inline reference instead, using the book's exact figure number and caption:

```html
<p class="fig-ref">（见图 3-5：弹簧振子示意图）</p>
```

```css
.fig-ref { color: var(--text3); font-size: 13px; font-style: italic;
           padding: 4px 0 4px 12px; border-left: 3px solid var(--border); margin: 8px 0; }
```

Format: `（见图 X-X：图题）`. (MODE B/C are different — figures are mandatory there and either
drawn as SVG or embedded from the original image; see `problem-solutions.md`.)

### Collapsible example / exercise card

**All 例题 and 练习答案/提示 MUST live inside `<details>` blocks — never inline.** The `<summary>`
shows the problem number + title (always visible); the full statement, solution steps, answer,
and hints go in `<div class="details-body">`. Omit the card entirely if a section has no
examples. Chapter-end exercise answers: one `<details>` per exercise, grouped in a single card
at the end of that chapter.

```html
<div class="card">
  <h3>例题 &amp; 练习</h3>

  <details>
    <summary>例 3-2　弹簧振子的周期</summary>
    <div class="details-body">
      <p><strong>题目：</strong>质量为 $m$ 的物体挂在劲度系数为 $k$ 的弹簧上，求振动周期。</p>
      <p><strong>解：</strong>由 $F = -kx$ 和牛顿第二定律…</p>
      <div class="fbox">$$T = 2\pi\sqrt{\frac{m}{k}}$$</div>
    </div>
  </details>

  <details>
    <summary>练习 3-4　答案与提示</summary>
    <div class="details-body">
      <p><strong>答案：</strong>$T = 0.63\,\text{s}$</p>
      <p><strong>提示：</strong>代入 $m = 0.1\,\text{kg}$，$k = 10\,\text{N/m}$。</p>
    </div>
  </details>
</div>
```

---

## 已核验 verification — the EXECUTABLE gate (MODE B & MODE C)

A `已核验 ✓` badge is a **claim that an independent check passed**. The only way to make that
claim trustworthy is to let a machine, not the model, decide it — otherwise a confidently-wrong
solution self-certifies (the documented slider-crank failure: a remembered textbook answer was
stamped 已核验 while the real derivative of the *given* $x(t)$ disagreed in sign and coefficient).

So the badge is **earned by execution**, not asserted. Every machine-verifiable solution carries an
invisible `<script type="text/x-verify">` block that **recomputes the answer from the GIVEN data
with sympy and asserts it equals the printed answer**. `scripts/verify_solutions.py` runs every
block for real and gates the badge:

- a block whose recomputation ≠ the claimed answer → **FAIL** (it prints the real recomputed value);
- `已核验` is allowed **only** on a solution with a PASSING block; more badges than passing checks → FAIL;
- anything not machine-verifiable (a proof, a conceptual answer) is tagged **`未自动核验`** (abstain), **never** `已核验`.

**What counts as a badge.** Both gates count only the badge **element** — a `<span class="badge …">已核验 …</span>`
pill (regex `<span … class="…badge…" …>已核验`, identical in `build_and_check.py` and `verify_solutions.py`).
Prose that *describes* verification ("所有解答都做了独立核验"), a CSS/JS comment that names the badge, and a
**legend** that demonstrates the pill are NOT badges and must not inflate the count — so write a legend with
`<strong>已核验 ✓</strong>` (or `<code></code>`), never a real `<span class="badge …">` pill, or it reads as one
more unbacked badge. The flip side: never present a reader-visible "已核验" as an ad-hoc `<span style="…">已核验</span>`
that has the look of a badge but escapes the `class="badge"` counter — that is a silent false claim the gate can't
see. Earned → the `badge b-verified` pill (green box) + a passing x-verify block; not earned → the `badge b-unverified` pill (amber box).

### The x-verify block (invisible; executed by `verify_solutions.py`)

```html
<div class="card">
  <h3>例 1　曲柄连杆求滑块加速度 <span class="badge b-verified">已核验 ✓</span></h3>
  <!-- ... statement + steps + .answer-box with the printed answer ... -->

  <!-- Invisible (a non-JS <script> never renders). Recompute from the GIVEN data; the helper
       does the math — NEVER pass the claimed answer in as the recomputation. -->
  <script type="text/x-verify" data-for="例1 滑块加速度 a_x">
import sympy as sp
t, w, lam, l = sp.symbols('t omega lambda l', positive=True)
x = l*((1 - lam**2/4) - sp.cos(w*t) - (lam/4)*sp.cos(2*w*t))   # GIVEN x(t), copied from the题面
check_derivative(given=x, wrt=t, order=2,
                 claimed=l*w**2*(sp.cos(w*t) + lam*sp.cos(2*w*t)),  # the answer the card prints
                 name="例1 a_x")
  </script>
</div>
```

Pre-imported helpers (from `scripts/verify_helpers.py`) — each recomputes, then compares:
`check_derivative(given,wrt,order,claimed)` · `check_integral(integrand,var,claimed)` ·
`check_equal(recomputed,claimed)` · `check_consistent(route_a,route_b)` (两路差分对账 / blind
double-solve made executable) · `check_limit(expr,var,point,expected)` (极限 sanity) ·
`check_numeric(expr,subs,expected)` (数值代入 sanity). Put 2–3 checks per problem when possible
(e.g. one `check_derivative` + one `check_limit`), so the badge reflects more than one angle.

`name=` strings may contain any Unicode (`²`, `√`, `π`, `ω`, Chinese …): `verify_solutions.run_block`
forces the child subprocess to UTF-8 stdio, so the gate behaves identically on a UTF-8 or a
GBK/CP-936 (Windows) console — a non-ASCII check name can no longer crash a block with
`UnicodeEncodeError`. **A conceptual MCQ is still verifiable**: recompute the *decisive quantity*
that fixes the keyed option (a limit / derivative / discriminant / tangent vector …) and refute the
distractors with *computed* counterexamples — never by asserting the answer.

### Abstention badge (when you cannot machine-verify)

```css
.b-verified{background:var(--green-light);color:var(--green-dark);border:1px solid var(--green);font-weight:700;}  /* 已核验 — green box */
.b-unverified{background:var(--amber-light);color:var(--amber-dark);border:1px solid var(--amber);}  /* 未自动核验 — amber box */
```

Usage: `<span class="badge b-verified">已核验 ✓</span>` (passed the gate) / `<span class="badge b-unverified">未自动核验</span>` (abstain). This is the honest default whenever a
problem has no clean symbolic check (proofs, "解释/讨论"类, experiment design). A `未自动核验`
solution may still be correct — it just was not auto-checked, so it does not claim to be.

### Run order

```bash
python scripts/build_and_check.py check <file>.html      # static lint (the artifact EXISTS)
python scripts/verify_solutions.py <file>.html           # executes the checks (the artifact is TRUE)
```

`build_and_check` accepts an x-verify block as a valid verify artifact; `verify_solutions` is the
decisive gate. **Hard rule:** if `verify_solutions` FAILs a solution, fix the solution (or downgrade
its badge to `未自动核验`) before shipping — a false `已核验` is worse than none.
