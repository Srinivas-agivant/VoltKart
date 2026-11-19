# Implementation Plan: Side Scroll Button & Top Specifications Expander

**Branch**: `011-shelf-scroll-specs-top` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/011-shelf-scroll-specs-top/spec.md`

## Summary

1. **Remove Page & Count Badges**:
   - In `frontend/storefront.py`, remove the `Page X of Y (N Laptops)` pill badge from the shelf header.
   - The header will cleanly display only the category title (e.g., `Deals on Office & Business Laptops`).
2. **Dedicated Right Side Scroll Button**:
   - For any deal shelf with >3 laptops, render a clean, elevated white scroll button (`›`) on the right side of the cards.
   - When clicked, it advances pagination through all laptops in the category and loops back when reaching the end.
3. **Move Detailed Specifications Slidebar to Top**:
   - Move the specifications expander bar (`🔍 Detailed Specifications for ...`) from below the orange shelf to directly ABOVE the orange shelf container (on top of every catalog).

## Technical Context

**Language/Version**: Python 3.10+ (Current runtime: Python 3.15)  
**Primary Dependencies**: Streamlit 1.67+, PyMongo 4.20+, Pandas 3.1+  
**Target Platform**: Web browser via Streamlit server  
**Files Modified**:
- `frontend/storefront.py`: Shelf header, card layout, side scroll button, and specifications expander positioning

## Constitution Check

- **Principle I (Streamlit-First)**: PASS. Uses native Streamlit components (`st.container`, `st.columns`, `st.expander`, `st.button`).
- **Principle VII & VIII (Strict Database Grounding)**: PASS. All laptop records and specs remain factual from MongoDB.
- **Principle XV (UI Responsiveness & Polish)**: PASS. Clean layout, zero clutter, smooth interaction.
