import frappe
from frappe.permissions import add_permission

def grant_hr_permissions():
    doctypes = [
        "Company", "Department",
        "Employee", "Designation", "Location",
        "Attendance",
        "Leave Type", "Leave Policy", "Leave Request", "Leave Balance",
        "Timesheet", "Shift Assignment"
    ]
    
    roles = ["HR Admin", "HR User"]
    
    for dt in doctypes:
        for role in roles:
            if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role}):
                # We use DocPerm if it's standard, but here we'll add to DocType permissions
                doc = frappe.get_doc("DocType", dt)
                
                # Check if role already exists in permissions
                exists = False
                for p in doc.permissions:
                    if p.role == role:
                        exists = True
                        break
                
                if not exists:
                    doc.append("permissions", {
                        "role": role,
                        "read": 1,
                        "write": 1,
                        "create": 1,
                        "delete": 1 if role == "HR Admin" else 0,
                        "report": 1,
                        "export": 1,
                        "share": 1,
                        "print": 1,
                        "email": 1
                    })
                    doc.save()
                    print(f"Granted {role} access to {dt}")
    
    frappe.db.commit()

if __name__ == "__main__":
    grant_hr_permissions()
