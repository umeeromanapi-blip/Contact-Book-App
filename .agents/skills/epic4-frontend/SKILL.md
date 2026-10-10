---
name: epic4-frontend
description: Technical guide and specification for Epic 4 of the Contact Book App, featuring multi-user authentication and data isolation, RFC vCard (.vcf) mobile export, visual KPI analytics dashboard, and activity audit logging.
---

# Epic 4 Enterprise Security, Analytics & Mobile Sync Reference

This skill documents the complete feature set, authentication lifecycle, mobile vCard sync, and analytics dashboard for Epic 4 of the Contact Book App.

## Overview
- **Epic**: Epic 4: Multi-User Security, Visual Analytics & Mobile Sync
- **Components**:
  - Django User Authentication (`UserRegistrationForm`, `UserLoginForm`, `user_demo_login`)
  - Multi-tenant Contact Privacy & Isolation (`Contact.user` foreign key)
  - RFC 2426 vCard 3.0 Mobile Synchronization (`contact_export_vcard`)
  - Visual Analytics Dashboard (`analytics_dashboard` in `dashboard.html`)
  - Chronological Audit Trail (`ActivityLog` & `log_activity`)
  - User Status Header & 1-Click Demo Login (`demo_user`)

## Verification & Automated Tests
Execute the full test suite:
```bash
python manage.py test
```
All 29 tests across Epics 1, 2, 3, and 4 should pass with code 0.
