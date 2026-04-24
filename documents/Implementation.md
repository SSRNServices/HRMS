# Implementation Roadmap – HRMS SaaS (Frappe-based)

## ⚠️ Guiding Principle

Build in this order:
1. Core Data Layer
2. Core Workflows
3. Core UX (Dashboard + APIs)
4. Expansion Modules
5. Intelligence (Analytics, AI, Automation)

DO NOT jump modules randomly.

---

# 🚀 PHASE 0 – Foundation (MANDATORY)

## Goal:
Set up base system that everything depends on

### Modules:
- Multi-tenant setup (Frappe sites)
- Authentication (Users, Roles)
- Permissions system
- Company / Organization

### Build:
- Company DocType
- Department DocType
- Role & Permission mapping
- User → Employee mapping

---

# 🚀 PHASE 1 – CORE HR (YOUR STARTING POINT)

## 🎯 This is your MVP (DO THIS FIRST)

### Modules:
- Org Onboarding
- Employee Management
- Attendance (Geo-based)
- Attendance Reports

---

## 1.1 Organization Setup

### Build:
- Company
- Departments
- Locations
- Designations

### Why first?
Everything depends on org structure.

---

## 1.2 Employee Management

### Build:
- Employee DocType
- Employee Profile
- Employee → Department mapping
- Employee → Manager hierarchy
- Document attachments

### Features:
- Org chart
- Directory
- Work schedules

---

## 1.3 Attendance (CRITICAL CORE)

### Build:
- Attendance DocType
- Check-in / Check-out API
- Geo-location fields (lat, long)
- Device tracking

### Features:
- Clock-in/out
- Geo-fencing (basic first)
- Work hours calculation

---

## 1.4 Attendance Reports

### Build:
- Daily attendance report
- Monthly report
- Late / overtime reports

---

## ⚠️ DO NOT MOVE FORWARD UNTIL:
- Attendance works end-to-end
- Reports are accurate
- Mobile API works

---

# 🚀 PHASE 2 – LEAVE + TIME SYSTEM

## Modules:
- PTO / Leave
- Time Tracking
- Roster (basic)

---

## 2.1 Leave Management

### Build:
- Leave Request
- Leave Policy
- Leave Balance
- Approval workflow

---

## 2.2 Time Tracking

### Build:
- Timesheets
- Overtime rules
- Work hours calculation

---

## 2.3 Roster (basic version)

### Build:
- Shift assignment
- Weekly schedule

---

# 🚀 PHASE 3 – REQUEST SYSTEM (IMPORTANT)

## Modules:
- Request Desk

### Build:
- Ticket system
- Request types:
  - HR
  - IT
  - Resignation
- Workflow engine

---

# 🚀 PHASE 4 – ONBOARDING / OFFBOARDING

## Modules:
- Onboarding
- Offboarding

### Build:
- Task templates
- Employee onboarding workflow
- Document attachments
- Email automation

---

# 🚀 PHASE 5 – RECRUITMENT

## Modules:
- Hiring system

### Build:
- Job posting
- Candidate pipeline
- Interview stages
- Offer letters

---

# 🚀 PHASE 6 – PERFORMANCE MANAGEMENT

## Modules:
- Reviews
- Goals

### Build:
- 360 reviews
- KPI tracking
- Review cycles

---

# 🚀 PHASE 7 – TRAINING + CAREER

## Modules:
- Training
- Career Development

### Build:
- Courses
- Certifications
- IDP
- 9-box matrix

---

# 🚀 PHASE 8 – SURVEYS + EMPLOYEE VOICE

## Modules:
- Surveys
- Grievances

### Build:
- Survey builder
- Anonymous feedback
- Reporting

---

# 🚀 PHASE 9 – DISCIPLINE SYSTEM

## Modules:
- Case management

### Build:
- Case tracking
- Investigator assignment
- Workflow steps

---

# 🚀 PHASE 10 – REPORTING & ANALYTICS

## Modules:
- Advanced analytics

### Build:
- Custom reports
- Dashboards
- Scheduled reports
- Snapshot reporting

---

# 🚀 PHASE 11 – HR ADMIN ADVANCED

## Modules:
- HR Administration

### Build:
- Audit logs
- Asset tracking
- Policy publishing
- Notifications system
- MFA

---

# 🚀 PHASE 12 – MOBILE APP

## Modules:
- Mobile APIs

### Build:
- Attendance APIs (geo tracking)
- Leave APIs
- Dashboard APIs

---

# 🚀 PHASE 13 – PAYROLL CONNECTOR

## Modules:
- Integrations

### Build:
- External payroll API
- Data sync

---

# 🧠 Dependency Map (IMPORTANT)

DO NOT BREAK THIS ORDER:

Org → Employee → Attendance → Leave → Requests → Everything else

---

# ⚠️ Common Mistakes (DON’T DO THIS)

❌ Start recruitment first  
❌ Build dashboards before data  
❌ Build mobile before backend  
❌ Overbuild workflows early  

---

# 🧠 MVP Definition (what you should launch)

### MVP = Phase 1 + Phase 2 (partial)

- Employee Management
- Attendance (geo)
- Leave
- Basic Reports

👉 That’s enough to launch

---

# 🚀 Suggested Timeline

Phase 1 → 2–3 weeks  
Phase 2 → 2 weeks  
Phase 3 → 1–2 weeks  

👉 MVP in ~6 weeks (if focused)

---

# 🔥 Final Advice

Your edge is NOT:
- Fancy UI
- ERP-level features

Your edge is:
👉 **Geo-based attendance + simplicity**

Focus there.

---

# ✅ Your NEXT STEP

Start building:

👉 Organization + Employee + Attendance

---

When ready, ask:

👉 “design first DocTypes”

I’ll give you exact schema + code-level structure.