# Architecture – HRMS SaaS

## 1. High-Level Architecture

Frontend (React / Next.js)
        |
        | REST API
        |
Backend (Frappe Framework)
        |
Database (PostgreSQL / MariaDB)
        |
Workers (Redis + Background Jobs)

---

## 2. Components

### 2.1 Backend (Frappe)
- Custom Apps (modular)
- REST API layer
- Authentication
- Role-based permissions
- Workflow engine

### 2.2 Frontend
- Next.js (recommended)
- API-driven UI
- Dashboard widgets
- Mobile-first responsive design

### 2.3 Database
- Multi-tenant (site-based or schema-based)
- Core entities:
  - Employee
  - Company
  - Attendance
  - Leave
  - Requests
  - Reviews

### 2.4 Workers
- Background jobs (emails, reports)
- Scheduled tasks
- Notifications

---

## 3. Multi-Tenancy Model

Option A: Frappe Sites (recommended)
- Each company = separate site

Option B: Shared DB (advanced)
- Tenant ID per record

---

## 4. Module Architecture

Each module = separate Frappe App

- hr_core
- hr_employee
- hr_attendance
- hr_recruitment
- hr_performance
- hr_training
- hr_requests

---

## 5. API Layer

- REST endpoints via Frappe
- JWT/Auth tokens
- Rate limiting
- Mobile APIs

---

## 6. Mobile Integration

- API-first design
- Geo tracking endpoints
- Real-time sync

---

## 7. Security

- MFA
- Role-based access
- Audit logs
- Data isolation per tenant