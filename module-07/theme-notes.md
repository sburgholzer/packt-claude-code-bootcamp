# Theme Notes

## Prompt

> Theme the dashboard (light + dark) using only plain CSS variables. have a button that is moon if on light and sun if on dark so they know what the button does.

## What was built

- All hardcoded colors in `static/style.css` replaced with CSS custom properties defined on `:root` (light) and `:root.dark` (dark).
- Toggle button (`.btn-theme`) added to the header alongside the existing "+ New Note" button, grouped in a `.header-actions` flex container.
- Button shows 🌙 in light mode (click to go dark) and ☀️ in dark mode (click to go light).
- Theme class toggled on `<html id="root">` via a small inline `<script>` block in `index.html`.
- Preference persisted to `localStorage` so the chosen theme survives page refresh.
- Inline script runs before first paint to apply the saved dark class, preventing flash of wrong theme.

## CSS variables defined

| Variable | Light | Dark |
|---|---|---|
| `--bg` | `#ffffff` | `#18181b` |
| `--surface` | `#ffffff` | `#27272a` |
| `--border` | `#222` | `#52525b` |
| `--border-row` | `#ccc` | `#3f3f46` |
| `--border-heading` | `#aaa` | `#52525b` |
| `--border-dots` | `#bbb` | `#52525b` |
| `--text` | `#111` | `#f4f4f5` |
| `--text-muted` | `#444` | `#a1a1aa` |
| `--text-faint` | `#555` | `#71717a` |
| `--hover-bg` | `#f8f8f8` | `#3f3f46` |
| `--btn-bg` | `#ffffff` | `#27272a` |
| `--btn-hover` | `#f5f5f5` | `#3f3f46` |
| `--footer-bg` | `#fafafa` | `#27272a` |
