---
name: epic3-frontend
description: Technical guide and specification for Epic 3 of the Contact Book App, featuring contact categorization, bulk selection actions, pagination, CSV import/export, dark/light theme switching, and programmatic REST API integration.
---

# Epic 3 Enterprise Features & Architecture Reference

This skill documents the complete feature set, REST API interface, UI/UX design patterns, and engineering workflows for Epic 3 of the Contact Book App.

## Overview
- **Epic**: Epic 3: Enterprise Contact Management & Programmatic Integration
- **Components**:
  - Contact Categorization & Tagging (`personal`, `work`, `family`, `friends`, `vip`)
  - Floating Bulk Selection Action Bar (Star, Unstar, Delete selected)
  - Pagination Engine (`django.core.paginator.Paginator`)
  - CSV Bulk Ingestion Engine (`/import/csv/`) & Sample Template Download
  - Programmatic REST API Endpoints (`/api/contacts/`, `/api/contacts/<pk>/`, `/api/contacts/stats/`)
  - Dark Glassmorphism and Clean Light Theme Switcher with `localStorage` persistence
  - 5 Interactive Modals (Quick-Edit, Delete Confirmation, Contact Profile Details, CSV Import Dropzone, REST API Explorer)

## Testing & Verification
```bash
python manage.py test
```
All 22 unit, integration, and REST API tests pass with code 0.
