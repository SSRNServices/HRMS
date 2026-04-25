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
