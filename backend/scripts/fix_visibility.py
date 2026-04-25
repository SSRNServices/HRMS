import frappe

def run_fix():
    from frappe.utils.global_search import rebuild_for_doctype
    module_doctype_map = {
        "HR Core": ["Company", "Department"],
        "HR Employee": ["Employee", "Designation", "Location"],
        "HR Attendance": ["Attendance"],
        "HR Leave": ["Leave Request", "Leave Policy"],
        "HR Timesheet": ["Timesheet"]
    }

    for module, doctypes in module_doctype_map.items():
        print(f"Processing module: {module}")
        
        # 1. Workspace Configuration
        if not frappe.db.exists("Workspace", module):
            print(f"  - Creating Workspace: {module}")
            doc = frappe.new_doc("Workspace")
            doc.label = module
            doc.title = module
            doc.module = module
            doc.public = 1
            doc.insert(ignore_permissions=True)
        else:
            print(f"  - Updating Workspace: {module}")
            doc = frappe.get_doc("Workspace", module)
        
        # Reset links and shortcuts to ensure clean state
        doc.links = []
        doc.shortcuts = []
        
        # Add a Card Break for visual grouping
        doc.append("links", {
            "label": f"{module} Management",
            "type": "Card Break",
            "link_count": len(doctypes)
        })
        
        for dt in doctypes:
            # Add Shortcut
            doc.append("shortcuts", {
                "type": "DocType",
                "label": dt,
                "link_to": dt,
                "stats_filter": "{}"
            })
            
            # Add Link
            doc.append("links", {
                "type": "Link",
                "label": dt,
                "link_to": dt,
                "link_type": "DocType"
            })
            
            # 2. Enable Global Search
            print(f"  - Rebuilding Global Search for: {dt}")
            try:
                rebuild_for_doctype(dt)
            except Exception as e:
                print(f"    ! Failed to rebuild search for {dt}: {e}")

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"  - Module {module} fixed successfully.")

    # 3. Clear Cache
    frappe.clear_cache()
    print("\nSystem cache cleared.")

if __name__ == "__main__":
    run_fix()
