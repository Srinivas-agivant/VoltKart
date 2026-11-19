# Implementation Plan: Grid Side Scroll Button & Clean AI Assistant Shadow

**Branch**: `010-grid-scroll-clean-assistant` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-grid-scroll-clean-assistant/spec.md`

## Summary

1. **Side Scroll Buttons on the Grid**:
   - Embed functional side navigation arrow buttons (`‹` and `›`) directly alongside the product cards on the orange deal shelf.
   - Use Streamlit columns or interactive flex layouts embedded within the shelf container so the right arrow button (`›`) sits directly to the right of the 3 cards, and the left arrow button (`‹`) sits to the left (or both compactly integrated into the grid).
   - Clicking `›` advances pagination through all laptops in the category; clicking `‹` pages back.
2. **Remove Red Background Shade Near AI Assistant**:
   - Strip all red-colored box shadows (`rgba(225, 29, 72, ...)`) from `.st-key-floating_open_btn`, `.st-key-floating_launcher_wrap`, and the JavaScript DOM locker in `frontend/floating_chat.py`.
   - Replace with a clean, neutral, soft dark shadow (`box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15)`).
   - Ensure the area/canvas around the floating button has no red tint, halo, or aura.

## Technical Context

**Language/Version**: Python 3.10+ (Current runtime: Python 3.15)  
**Primary Dependencies**: Streamlit 1.67+, PyMongo 4.20+, Pandas 3.1+  
**Target Platform**: Web browser via Streamlit server  
**Files Modified**:
- `frontend/storefront.py`: Deal shelf layout, on-grid side scroll navigation buttons, and CSS
- `frontend/floating_chat.py`: Floating launcher CSS and DOM locker box-shadow (neutralize red glow)

## Constitution Check

- **Principle I (Streamlit-First)**: PASS. All interactive elements use native Streamlit buttons and CSS.
- **Principle VII & VIII (Grounded Retrieval & Zero Hallucination)**: PASS. Product catalog retrieval unchanged.
- **Principle XV (UI Responsiveness & Reliability)**: PASS. Pagination executes with smooth stateful reruns.
