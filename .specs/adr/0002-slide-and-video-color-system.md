---
id: ADR-0002
title: Slide and video color system
status: accepted
date: 2026-04-15
---

# Context

This repository needs a consistent visual system for Slidev slides and Manim-rendered videos.

The system should be reusable across spikes and should not carry external brand naming inside project artifacts.

# Decision

Use the following palette and typography choices as the canonical visual system for slides and videos in this repository.

Do not refer to this system using external brand labels in project documentation, code comments, or generated assets.

## Typography

- Primary font family: `Open Sans`, `Arial`, `sans-serif`
- Symbol font for icons when needed: `Material Symbols Rounded`

## Core colors

- `brand-red`: `#9e1b32`
- `brand-gray`: `#333e48`
- `primary-red`: `#9e1b32`
- `primary-orange`: `#e77204`
- `primary-yellow`: `#f1c319`
- `primary-green`: `#45842a`
- `primary-blue`: `#007298`
- `primary-purple`: `#652f6c`
- `black`: `#000000`
- `white`: `#ffffff`
- `gray`: `#333e48`

## Gray scale

- `gray-100`: `#e7e7e7`
- `gray-200`: `#cfcfcf`
- `gray-300`: `#b5b5b5`
- `gray-400`: `#9c9c9c`
- `gray-500`: `#828282`
- `gray-600`: `#696969`
- `gray-700`: `#4f4f4f`
- `gray-800`: `#363636`
- `gray-900`: `#1c1c1c`

## Shadow colors

- `shadow-red`: `#6d1222`
- `shadow-orange`: `#994a00`
- `shadow-yellow`: `#98700c`
- `shadow-green`: `#294d19`
- `shadow-blue`: `#004d66`
- `shadow-purple`: `#431f47`

## Highlight colors

- `highlight-red`: `#ffccd5`
- `highlight-orange`: `#ffe5cc`
- `highlight-yellow`: `#fff4cc`
- `highlight-green`: `#dbffcc`
- `highlight-blue`: `#cdf3ff`
- `highlight-purple`: `#f9ccff`

## Status colors

- `status-red`: `#e8002a`
- `status-orange`: `#ff9633`
- `status-yellow`: `#ffd332`
- `status-green`: `#36b300`
- `status-blue`: `#00ace6`
- `status-purple`: `#9e00b3`

## UI and slide defaults

- `text-color`: `#333e48`
- `link-color`: `#007298`
- `link-hover-color`: `#004d66`
- `disabled`: `#cfcfcf`
- `page-background`: `#f7f7f7`
- `footer-background`: `#333e48`
- `accessibility-focus-color`: `#cfcfcf`
- `border`: `#9c9c9c`
- `border-light`: `#cfcfcf`
- `border-dark`: `#696969`

## Primary background rule

- Use `primary-red`, `primary-orange`, `primary-yellow`, `primary-green`, `primary-blue`, and `primary-purple` as the default strong background colors for slides, panels, badges, and video-backed composition blocks when a primary accent background is needed.
- When one of those six primary colors is used as a background, the default foreground text color should be `white` (`#ffffff`) unless a spike is explicitly testing a different contrast treatment.

# Consequences

- New spikes should prefer this palette for Slidev layouts and Manim styling unless a spike is intentionally testing a different visual system.
- New docs and code should use generic token names such as `primary-green` or `highlight-blue`, not external brand-prefixed names.
- If a spike needs CSS variables, it should map local variables to this canonical palette instead of introducing a second naming system.
- New Slidev and Manim compositions should treat the six primary colors as the main solid-background palette and pair them with white text by default.
