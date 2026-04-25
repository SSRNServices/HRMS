import frappe

module_doctype_map = {
    "HR Core": ["Company", "Department"],
    "HR Employee": ["Employee", "Designation", "Location"],
    "HR Attendance": ["Attendance"],
    "HR Leave": ["Leave Request", "Leave Policy"],
    "HR Timesheet": ["Timesheet"]
}

def fix_workspace(module, doctypes):
    print(f"Fixing workspace for {module}...")
    
    if not frappe.db.exists("Workspace", module):
        print(f"Creating workspace for {module}")
        doc = frappe.new_doc("Workspace")
        doc.label = module
        doc.title = module
        doc.module = module
        doc.public = 1
        doc.insert(ignore_permissions=True)
    else:
        doc = frappe.get_doc("Workspace", module)
    
    doc.links = []
    doc.shortcuts = []
    
    # Add a Card Break first for links to show up nicely
    doc.append("links", {
        "label": module,
        "type": "Card Break",
        "link_count": len(doctypes)
    })
    
    for dt in doctypes:
        # Add as Shortcut
        doc.append("shortcuts", {
            "type": "DocType",
            "label": dt,
            "link_to": dt,
        })
        # Add as Link
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

    doc.save(ignore_permissions=True)
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
