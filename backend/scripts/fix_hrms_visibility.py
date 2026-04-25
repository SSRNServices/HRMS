import frappe
from frappe.desk.doctype.workspace.workspace import create_workspace_for_module

module_doctype_map = {
    "HR Core": ["Company", "Department"],
    "HR Employee": ["Employee", "Designation", "Location"],
    "HR Attendance": ["Attendance"],
    "HR Leave": ["Leave Request", "Leave Policy"],
    "HR Timesheet": ["Timesheet"]
}

def fix_workspace(module, doctypes):
    print(f"Fixing workspace for {module}...")
    
    # Check if workspace exists
    if not frappe.db.exists("Workspace", module):
        print(f"Creating workspace for {module}")
        create_workspace_for_module(module)
        frappe.db.commit()
    
    doc = frappe.get_doc("Workspace", module)
    
    # Clear existing links and shortcuts to avoid duplicates and ensure freshness
    doc.links = []
    doc.shortcuts = []
    
    for dt in doctypes:
        # Add as Shortcut
        doc.append("shortcuts", {
            "type": "DocType",
            "label": dt,
            "link_to": dt,
        })
        # Add as Link (optional, but good for visibility in the list)
        doc.append("links", {
            "type": "Link",
            "label": dt,
            "link_to": dt,
            "link_type": "DocType"
        })
        
        # Enable Global Search for the DocType
        print(f"Rebuilding global search for {dt}")
        from frappe.utils.global_search import rebuild_for_doctype
        rebuild_for_doctype(dt)

    doc.save()
    frappe.db.commit()
    print(f"Workspace {module} updated.")

for module, doctypes in module_doctype_map.items():
    try:
        fix_workspace(module, doctypes)
    except Exception as e:
        print(f"Failed to fix workspace for {module}: {e}")

# Final Clear Cache
frappe.clear_cache()
print("Done.")
