# Daily Log - HRMS SaaS

## 2026-04-25 (Implementation: Phase 0 & 1)
- **Completed Work**:
    - Initialized Frappe Bench (v15 stable) and development site (`dev.hrms.localhost`).
    - Established modular app architecture: `hr_core`, `hr_employee`, `hr_attendance`.
    - Created core DocTypes: `Company`, `Department`, `Employee`, `Designation`, `Location`, `Attendance`.
    - Automated role creation for `HR Admin`, `HR User`, and `Employee`.
    - Implemented whitelisted REST APIs for Geo-based `check_in` and `check_out` in `hr_attendance`.
    - Configured `.gitignore` for standard Frappe Bench exclusion.
    - Pushed initial Phase 0 & 1 codebase to GitHub.
- **Issues Faced**:
    - Missing system dependencies (`pkg-config`, `libmariadb-dev`) on host environment.
    - Frappe v17-dev branch had incompatible Python requirements (v3.14+); pivoted to stable v15.
- **Key Learnings**:
    - Modularizing HR domains into separate apps from the start simplifies future expansion and multi-tenant scaling.
    - Standard dev environment MariaDB root password is `root`.

## 2026-04-25 (Implementation: Phase 2)
- **Completed Work**:
    - Created `hr_leave` and `hr_timesheet` apps to extend HR functionality.
    - Implemented Leave Management: `Leave Type`, `Leave Policy`, `Leave Request`, and `Leave Balance` tracking.
    - Implemented Time Tracking: `Timesheet` logging and `Shift Assignment` (roster management).
    - Configured "Leave Approval" workflow (Open -> Pending -> Approved/Rejected).
    - **Structural Fix**: Reorganized all custom app folder structures to match Frappe v15 module nesting (`app/app/module/doctype`).
    - Integrated `Leave Policy` link into the `Employee` profile.
    - Verified Desk UI connectivity and Login functionality on `dev.hrms.localhost:8000`.
- **Issues Faced**:
    - **DocType Migration Failure**: Discovered that DocTypes were not being created in the DB because they were located outside the specific module folder. Resolved by moving all metadata to the nested module directory.
    - **Workflow Validation**: Initial rejection state attempted to use `doc_status 2` (Cancelled) from `Draft`, which triggered a Frappe validation error. Adjusted `Rejected` to remain in `doc_status 0`.
- **Key Learnings**:
    - Frappe apps require a specific three-level directory depth for metadata discovery: `apps/[app]/[app]/[module]`.
    - Workflows must strictly follow `doc_status` progression (0 -> 1 -> 2); you cannot skip from Draft to Cancelled.
