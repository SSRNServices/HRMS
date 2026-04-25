🚀 Implementation Roadmap – HRMS SaaS (Frappe-based)
⚠️ Guiding Principle

Build in this order:

SaaS Control Layer (Global – Organizations)
Core Data Layer (Tenant – HRMS)
Core Workflows
Core UX (APIs + Dashboard)
Expansion Modules
Intelligence (Analytics, AI)

❌ Do NOT mix SaaS logic with HR logic
❌ Do NOT skip tenant isolation

🧠 SYSTEM ARCHITECTURE (NON-NEGOTIABLE)
Two-Level System
🔹 Level 1 – SaaS Control (You / Super Admin)
Owns all organizations
Creates & provisions tenants
Controls plans, limits, access
🔹 Level 2 – Organization (Client / Tenant)
Runs in isolated site
Admin manages only their org
No cross-org data access
🧱 Multi-Tenant Strategy

Use site-per-organization in Frappe Framework

org1.yourapp.com
org2.yourapp.com

👉 Shared DB multi-tenant = future disaster
👉 Stick to isolated sites

🚀 PHASE -1 – SAAS CONTROL LAYER (MANDATORY)
🎯 Goal:

You control organizations before HR exists

📦 App:
saas_core
📚 Core DocTypes (GLOBAL)
Organization
name
subdomain
status (active / suspended)
plan
max_employees
max_admins
owner_email
Site Mapping
organization
site_name
database_name
Subscription
organization
plan
start_date
end_date
billing_status
Org Admin (Global Reference)
email
organization
role (owner/admin)
⚙️ Core Responsibilities
Super Admin (YOU):
Create organization
Provision site
Install HRMS app
Create org admin
Enforce limits
🔌 REQUIRED APIs
Create Organization
Provision Site
Suspend Organization
Upgrade/Downgrade Plan
Enforce Limits
⚠️ HARD RULE

❌ No Employee
❌ No Attendance

Until this phase is DONE

🚀 PHASE 0 – FOUNDATION (TENANT LEVEL)
🎯 Goal:

Set base inside each organization

Modules:
Authentication
Roles & Permissions
Org structure
Build:
Company
Department
Location
Designation
Roles:
Org Admin
Manager
Employee
Mapping:
User → Employee
🚀 PHASE 1 – CORE HR (MVP START)
🎯 MVP STARTS HERE
Modules:
Org Setup
Employee Management
Attendance
Reports
1.1 Organization Setup
Company
Departments
Locations
Designations
1.2 Employee Management
Employee DocType

Fields:

employee_id
user
department
designation
manager
joining_date
status
Features:
Org chart
Employee directory
⚠️ SaaS Enforcement Hook

Before creating employee:

→ Check max_employees from SaaS layer
→ Block if exceeded

1.3 Attendance (CORE DIFFERENTIATOR)
Attendance DocType

Fields:

employee
date
check_in
check_out
latitude
longitude
device_id
status
APIs:
/api/checkin
/api/checkout
Logic:
Work hours calculation
Late detection
Geo validation (basic first)
1.4 Attendance Reports
Daily
Monthly
Late / Overtime
⚠️ STOP CONDITION

Do NOT move forward until:

Attendance is stable
Reports are accurate
APIs are reliable
🚀 PHASE 2 – LEAVE + TIME SYSTEM
Modules:
Leave Management
Time Tracking
Roster
2.1 Leave
Leave Request
Leave Policy
Leave Balance
Approval workflow
SaaS Hooks:
Limit policies per plan
Restrict advanced rules
2.2 Time Tracking
Timesheets
Overtime rules
2.3 Roster
Shift assignment
Weekly schedule
🚀 PHASE 3 – REQUEST SYSTEM
Modules:
Internal Ticketing
Build:
HR / IT / Resignation requests
Workflow engine
SaaS Hooks:
Limit number of active tickets
Feature access by plan
🚀 PHASE 4 – ONBOARDING / OFFBOARDING
Build:
Task templates
Joining workflows
Exit workflows
Document attachments
SaaS Hooks:
Limit workflows
Storage control
🚀 PHASE 5 – RECRUITMENT
Build:
Job posting
Candidate pipeline
Interview stages
Offer letters
⚠️ Enable only for higher plans
🚀 PHASE 6 – PERFORMANCE MANAGEMENT
Build:
Goals
Reviews
KPI tracking
Plan-based feature unlock
🚀 PHASE 7 – TRAINING + CAREER
Build:
Courses
Certifications
IDP
9-box matrix
🚀 PHASE 8 – SURVEYS + EMPLOYEE VOICE
Build:
Survey builder
Anonymous feedback
Reports
🚀 PHASE 9 – DISCIPLINE SYSTEM
Build:
Case tracking
Investigation workflow
🚀 PHASE 10 – REPORTING & ANALYTICS
Build:
Custom dashboards
Scheduled reports
Snapshots
🚀 PHASE 11 – HR ADMIN ADVANCED
Build:
Audit logs
Asset tracking
Policy publishing
Notifications
MFA
🚀 PHASE 12 – MOBILE APIs
Build:
Attendance APIs
Leave APIs
Dashboard APIs
🚀 PHASE 13 – PAYROLL CONNECTOR
Build:
External payroll integration
Data sync
🧠 GLOBAL LIMIT ENFORCEMENT (CRITICAL)
MUST enforce at backend:
Employee limits
Admin limits
Feature access
API usage
Where:
DocType hooks
API layer
Background jobs
🧠 DATA FLOW (FINAL)
Super Admin (You)
   ↓
Create Organization
   ↓
Provision Site
   ↓
Install HRMS App
   ↓
Create Org Admin
   ↓
Org Admin logs in
   ↓
Manages employees & attendance
⚠️ COMMON MISTAKES

❌ Building HR before SaaS
❌ Not enforcing limits server-side
❌ Mixing tenant data
❌ Overbuilding early features

🧠 MVP (ACTUAL PRODUCT)
MVP =
Organization onboarding (SaaS)
Site provisioning
Org admin creation
Employee management
Attendance (geo-based)
Basic reports
Employee limit enforcement

👉 That’s enough to launch
👉 Everything else is optional

⏱️ REAL TIMELINE
SaaS Core → 2 weeks
Core HR → 2 weeks
Attendance → 2 weeks

👉 Total: ~6 weeks

🔥 FINAL TRUTH

If you fail:
It won’t be because of missing features.

It’ll be because:

Bad tenant architecture
Weak attendance reliability
No strict limit enforcement