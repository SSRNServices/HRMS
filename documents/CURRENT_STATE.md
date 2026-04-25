# Current State - HRMS SaaS

## Working
- **Backend**: Frappe Framework v15 stable environment.
- **Organization Management**: `Company` and `Department` DocTypes with hierarchy support.
- **Employee Management**: `Employee`, `Designation`, and `Location` DocTypes implemented.
- **Attendance**: `Attendance` DocType with GPS tracking (lat/long) for both check-in and check-out.
- **APIs**: Whitelisted REST endpoints for `check_in` and `check_out`.
- **Roles**: Foundation roles (`HR Admin`, `HR User`, `Employee`) defined.

## Incomplete / In Progress
- **Attendance Reports**: Schema ready, but report views/analytics not yet built.
- **Site Isolation**: Multi-tenant site creation works, but cross-site data isolation needs formal testing.

## Not Started
- **Frontend**: Next.js application initialization and API integration.
- **Phase 2**: Leave Management (PTO), Policy engine, and Timesheets.
- **Phase 3**: Request Desk and Workflow engine.

## Tech Notes
- **Modular Apps**: Core functionality split across `hr_core`, `hr_employee`, and `hr_attendance`.
- **REST-First**: All business logic is accessible via Frappe's REST API for frontend decoupling.
- **Geo-Native**: Attendance records require GPS coordinates for validation.
