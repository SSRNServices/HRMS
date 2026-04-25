import frappe

def create_hr_workspaces():
    workspaces = {
        "HR Core": ["Company", "Department"],
        "HR Employee": ["Employee", "Designation", "Location"],
        "HR Attendance": ["Attendance"],
        "HR Leave": ["Leave Type", "Leave Policy", "Leave Request", "Leave Balance"],
        "HR Timesheet": ["Timesheet", "Shift Assignment"]
    }
    
    for ws_name, doctypes in workspaces.items():
        if not frappe.db.exists("Workspace", ws_name):
            doc = frappe.get_doc({
                "doctype": "Workspace",
                "label": ws_name,
                "name": ws_name,
                "title": ws_name, # Added title
                "module": ws_name,
                "is_standard": 1,
                "public": 1,
                "content": "[]",
                "links": [
                    {
                        "link_type": "DocType",
                        "link_to": dt,
                        "label": dt,
                        "type": "Link"
                    } for dt in doctypes
                ]
            })
            doc.insert(ignore_permissions=True)
            print(f"Created workspace: {ws_name}")
        else:
            print(f"Workspace already exists: {ws_name}")
            
    frappe.db.commit()

if __name__ == "__main__":
    create_hr_workspaces()
