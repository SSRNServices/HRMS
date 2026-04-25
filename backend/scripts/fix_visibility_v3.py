import frappe
import json

def run_fix_v3():
    module_doctype_map = {
        "HR Core": ["Company", "Department"],
        "HR Employee": ["Employee", "Designation", "Location"],
        "HR Attendance": ["Attendance"],
        "HR Leave": ["Leave Request", "Leave Policy"],
        "HR Timesheet": ["Timesheet"]
    }

    for module, doctypes in module_doctype_map.items():
        print(f"Fixing {module}...")
        
        # Delete private versions that might be shadowing
        frappe.db.delete("Workspace", {"for_user": ["!=", ""], "label": module})
        
        doc = frappe.get_doc("Workspace", module)
        doc.links = []
        doc.shortcuts = []
        
        # Set content to None to force fallback to tables (common in v13/v14 transition)
        # OR better, generate a basic content JSON if we are on v14
        doc.content = None 
        
        doc.append("links", {
            "label": f"{module} Management",
            "type": "Card Break",
            "link_count": len(doctypes)
        })
        
        for dt in doctypes:
            doc.append("shortcuts", {
                "type": "DocType",
                "label": dt,
                "link_to": dt,
            })
            doc.append("links", {
                "type": "Link",
                "label": dt,
                "link_to": dt,
                "link_type": "DocType"
            })
            
            # Rebuild Global Search
            from frappe.utils.global_search import rebuild_for_doctype
            rebuild_for_doctype(dt)

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"  - {module} updated.")

    frappe.clear_cache()
    print("Done.")

if __name__ == "__main__":
    run_fix_v3()
