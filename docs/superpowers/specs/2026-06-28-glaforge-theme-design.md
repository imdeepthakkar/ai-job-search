# glaforge.dev Theme Design Specification

**Date:** 2026-06-28  
**Status:** Approved  
**Topic:** Transitioning the Vercel Job opportunities portal style to match the authentic light theme of glaforge.dev.

---

## 1. Design Principles & Palette
The new theme is a clean, typography-driven light theme that replaces the dark glassmorphic portal design. It uses Guillaume Laforge's exact color palette:

- **Bordeaux (`#817`):** Primary headings, logo accent.
- **Red (`#a35`):** Text links, primary interactive states, success/applied buttons.
- **Violet (`#639`):** Divider lines, secondary accents.
- **Dark Blue (`#36b`):** Match score/fit indicators, focus borders.
- **Light Gray (`#EEE`):** Sidebar background, card borders, and hover states.
- **White (`#FFF`):** App base background and main panels.

---

## 2. Typography
We will import Google Fonts in `index.css`:
- **Body & Controls:** `'PT Sans', sans-serif` for highly readable text.
- **Headings & Badges:** `'Roboto Slab', serif` with a font weight of `800` for strong, classic serif headers.

---

## 3. Structural Overrides
- **Gradient Page Border:** Add a `1rem` solid top and bottom border to the `body` (or `html`) using the linear-gradient: `linear-gradient(90deg, #a35, #36b)`.
- **Dividers:** Change standard division elements and `hr` tags to use a `3px` dashed `#639` border.
- **Sidebar:** Set background to a solid `#EEE` or vertical gradient `#EEE` to `#FFF`.
- **Job Cards:** White panels with a solid `#EEE` border, removing neon box-shadows.

---

## 4. UI Component Updates

### Badges (Fit & Source)
- **High Fit:** Red (`#a35`) background or text.
- **Medium Fit:** Dark Blue (`#36b`) background or text.
- **Low Fit:** Violet (`#639`) background or text.
- **Source:** Bordeaux (`#817`) or Slate Gray text.

### Buttons & Inputs
- **Autopilot Tailor (Primary):** Solid Red (`#a35`) background with white text.
- **Mark Applied (Success):** Bordeaux (`#817`) background.
- **Dismiss (Danger):** Charcoal/Dark Gray.
- **Input Fields:** Pure white background with a thin `#CCC` border, highlighting in `--darkblue` (`#36b`) on focus.
