---
name: epic1-frontend
description: Guide and technical specification of the frontend features, UI/UX architecture, styling design system, and client interactions implemented for Epic 1 of the Contact Book App.
---

# Epic 1 Frontend Technical Reference & Skills

This skill documents the frontend features, design tokens, templates, and interactive client scripts for Epic 1 of the Contact Book App.

## Overview
- **Epic**: Epic 1: Contact Creation & Directory View
- **Architecture**: Django MVT (Model-View-Template)
- **Primary Template**: `contacts/templates/contacts/index.html`
- **Stylesheet**: `contacts/static/contacts/style.css`

## Key Frontend Features
1. **Glassmorphic Dark UI**:
   - Palette based on CSS Custom Properties (`--bg-base: #0b0f19`, `--primary: #6366f1`).
   - Ambient glow backdrops using blurred radial gradients.
   - Translucent card backgrounds with soft frosted borders.

2. **Form Interaction & Validation**:
   - CSRF protection via `{% csrf_token %}`.
   - Inline field error styling via `has-error` class and `.field-error-message`.
   - SVG icons embedded in inputs with focus-ring glow effects.

3. **Dynamic Template Data**:
   - Contact count counter badge with automatic pluralization (`{{ total_contacts|pluralize }}`).
   - Initial avatar generation (`{{ contact.name|slice:':1'|upper }}`).
   - Dismissible Django message banners (Success / Error).

4. **Client-Side Vanilla JS**:
   - **Live Filter**: Case-insensitive instant filtering by name/phone with `[data-name]` and `[data-phone]` matching.
   - **One-Click Copy**: Asynchronous clipboard copy via `navigator.clipboard.writeText()` with feedback state.
   - **Auto Alert Fade**: 5-second timeout automatic alert dismiss with smooth CSS transitions.

## Verification
Run `python manage.py test` to verify template rendering and integration tests.
Start dev server with `python manage.py runserver` and navigate to `http://127.0.0.1:8000/`.
