---
name: epic2-frontend
description: Guide and technical specification for Epic 2 of Contact Book App, covering full CRUD lifecycle (Update, Delete), Star/Favorites, Interactive Glassmorphic Modals, Search & Sorting, CSV Export, and Advanced Django MVT Architecture.
---

# Epic 2 Frontend & Full Lifecycle Engineering Specification

This skill documents the complete feature set, UI/UX design patterns, and engineering workflows for Epic 2 of the Contact Book App.

## Overview
- **Epic**: Epic 2: Complete Contact Management & Interactive Operations
- **Components**:
  - Full CRUD operations: Create, Read, Update, Delete
  - Star / Favorites toggling and tab filtering
  - Multi-attribute search (Name, Phone, Email) & Sorting (Newest, Oldest, A–Z, Z–A)
  - Interactive Glassmorphism Modals (Quick-Edit & Delete Confirmation)
  - CSV Export Web API
  - Fallback dedicated pages: `edit.html` & `confirm_delete.html`

## Technical Details
- **Model**: `Contact` in `contacts/models.py` with `name`, `phone`, `email`, `is_favorite`, `created_at`, `updated_at`.
- **Form**: `ContactForm` in `contacts/forms.py` with whitespace trimming, optional email format validation, and max length checks.
- **Views**: In `contacts/views.py`:
  - `contact_list`: Search, sorting, tab filtering, and contact creation.
  - `contact_update`: Edit contact via instance binding.
  - `contact_delete`: Safe deletion using POST.
  - `contact_toggle_favorite`: Favorite status toggle.
  - `contact_export_csv`: Streaming CSV file attachment generation.
- **Styles**: In `contacts/static/contacts/style.css`:
  - Modals (`.modal-overlay`, `.modal-card`, blur filters, scale animations).
  - Filter tabs (`.directory-filter-tabs`, `.filter-tab.active`).
  - Star toggle buttons and favorite card accents (`.contact-card.is-favorite`).

## Testing & Verification
Execute the automated test suite:
```bash
python manage.py test
```
All 21 tests should pass with code 0.
