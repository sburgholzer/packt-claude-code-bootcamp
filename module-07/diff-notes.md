# Visual Diff — wireframe vs. renders

---

## Iteration 1
Comparison: `wireframe-sketch.png` (target) vs. `created.png` (first render).
All 5 gaps fixed.

### 1. Footer clipped — layout overflowed 720px viewport
**Gap:** Total height exceeded `100vh`; footer was barely visible at 1280×720.
**Fix applied:** Reduced `.kpi-card` padding `18px 22px 20px` → `12px 16px 14px` and `.body-row` gap `16px` → `12px`.

### 2. Outer margins created a floating-document look
**Gap:** `margin: 16px` on header, body-row, and footer left visible page-background gaps on all sides; wireframe fills edge-to-edge.
**Fix applied:** Removed margins from `.header`, `.body-row`, `.footer`; moved the 16px inset to `padding: 16px` on `.page` instead.

### 3. Active sidebar item had a gray highlight
**Gap:** "Overview" rendered with a filled gray rectangle; wireframe shows plain text-only nav items.
**Fix applied:** Removed `background: #f0f0f0` from `.sidebar nav a.active` selector (hover retained).

### 4. KPI value font weight too heavy
**Gap:** `font-weight: 700` made numerals noticeably blacker than the wireframe's medium-weight style.
**Fix applied:** Changed `.kpi-card .kpi-value` `font-weight: 700` → `500`.

### 5. Table row separators nearly invisible
**Gap:** `border-bottom: 1px solid #e8e8e8` was too close to white to read clearly.
**Fix applied:** Darkened to `1px solid #ccc`.

---

## Iteration 2
Comparison: `wireframe-sketch.png` (target) vs. `Screenshot 2026-05-31 at 12.17.38 AM.png` (second render).
Items 1–3 not actioned (not observed / user satisfied with current state). Items 4–5 fixed.

### 1. Footer still clipped — bottom border cut by viewport
**Gap:** `padding: 16px` on `.page` plus element heights still slightly exceeded `100vh`; footer bottom edge sliced off.
**Not fixed:** Not visible to user; skipped.

### 2. KPI cards too compact after over-correction
**Gap:** Reducing to `12px 16px 14px` made cards shorter than wireframe proportions.
**Not fixed:** User satisfied with current card size.

### 3. KPI value weight still too heavy
**Gap:** `font-weight: 500` still renders visibly bold on macOS system font.
**Not fixed:** User satisfied with current weight.

### 4. "Recent items" heading divider too dark
**Gap:** `1.5px solid #222` rendered near-black; wireframe shows a lighter, thinner rule.
**Fix applied:** Changed `.table-panel h2` border to `1px solid #aaa`.

### 5. Sidebar hover background too prominent
**Gap:** `#f0f0f0` hover fill is a noticeable rectangle; wireframe nav is text-only in feel.
**Fix applied:** Changed `.sidebar nav a:hover` background `#f0f0f0` → `#f8f8f8`.
