# Next Steps - HRMS SaaS

## Immediate (Do First)
1. **Initialize Next.js Frontend**: Create the `/frontend` directory and set up the base project (Next.js 14+, Tailwind, ShadcnUI).
2. **Leave Balance Validation**: Implement a `before_save` hook in `Leave Request` to prevent submissions that exceed the employee's `Leave Balance`.
3. **Attendance Reports**: Build the "Daily Attendance Summary" and "Monthly Attendance Sheet" reports in the backend.

## Next
- **Leave Accrual Engine**: Create a Python background job (`hooks.py` scheduler) to automatically grant leave based on `Leave Policy` rules.
- **Geo-fencing Validation**: Add server-side distance calculation to the `check_in` API to verify the employee is at the assigned `Location`.
- **Frontend Auth**: Connect Next.js to Frappe's authentication system (Session/Token).

## Later
- **Mobile PWA**: Optimize the frontend for mobile attendance marking.
- **Document Management**: Allow employees to upload sick notes or ID documents.
- **Phase 4 (Payroll)**: Start building the salary component logic.
