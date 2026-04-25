# Current State - HRMS SaaS

## Working
- **Backend Infrastructure**: Frappe Framework v15 stable with corrected app nesting.
- **Org & Employee**: Hierarchy support (Company/Dept) and enriched Employee profiles with Leave Policy mapping.
- **Attendance**: Whitelisted Geo-tracking APIs for check-in/out logic.
- **Leave Management**: Full lifecycle (Policies -> Allocations -> Requests) with an active Approval Workflow.
- **Time Tracking**: Timesheet logging and shift assignment foundation.
- **Security**: Automated role provisioning (`HR Admin`, `HR User`, `Employee`).
- **UI**: Frappe Desk is accessible and verified.

## Incomplete / In Progress
- **Leave Accruals**: Logic for periodic leave allocation (monthly/yearly accrual) is planned but currently requires manual balance setup.
- **Validation Logic**: `Leave Request` does not yet validate if the requested days exceed the current `Leave Balance`.
- **Geo-fencing**: APIs log coordinates but do not yet restrict check-ins based on `Location` radius.

## Not Started
- **Frontend (Next.js)**: UI initialization and client-side API integration.
- **Reporting**: Advanced analytics for attendance trends and leave liability.
- **Payroll**: Phase 4 integration for salary processing based on attendance/leave data.

## Tech Notes
- **App Structure**: Standardized to `apps/[app]/[app]/[module]/doctype/` for all custom modules.
- **Multi-tenancy**: Site-based isolation enabled for `dev.hrms.localhost`.
- **Workflow**: `Leave Approval` workflow governs the `Leave Request` status field.
