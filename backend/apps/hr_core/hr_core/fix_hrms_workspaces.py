"""
Frappe workspace fix – invokable via:
  bench --site dev.hrms.localhost execute fix_hrms_workspaces.fix_workspaces
"""
import frappe
import json
from frappe.utils.global_search import rebuild_for_doctype

def fix_workspaces():
    MODULE_DOCTYPES = {"HR Core": ["Company", "Department"], "HR Employee": ["Employee", "Designation", "Location"], "HR Attendance": ["Attendance"], "HR Leave": ["Leave Request", "Leave Policy"], "HR Timesheet": ["Timesheet"]}
    fixed = []; errors = []
    for module, doctypes in MODULE_DOCTYPES.items():
        print(f"\n=== {module} ===")
        try:
            if not frappe.db.exists("Workspace", module):
                print(f"  Creating workspace {module}...")
                doc = frappe.new_doc("Workspace")
                doc.label = module; doc.title = module; doc.module = module; doc.public = 1; doc.content = "[]"
            else:
                doc = frappe.get_doc("Workspace", module)
                try:
                    parsed = json.loads(doc.content or "[]")
                    if not isinstance(parsed, list): doc.content = "[]"
                except Exception: doc.content = "[]"
            doc.links = []; doc.shortcuts = []
            doc.append("links", {"label": module, "type": "Card Break", "link_count": len(doctypes)})
            for dt in doctypes:
                doc.append("links", {"type": "Link", "label": dt, "link_to": dt, "link_type": "DocType", "onboard": 1})
            for dt in doctypes:
                doc.append("shortcuts", {"type": "DocType", "label": dt, "link_to": dt})
            doc.public = 1
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"  Saved. Links: {len(doctypes)}, Shortcuts: {len(doctypes)}")
            for dt in doctypes:
                try: rebuild_for_doctype(dt); print(f"  Global search rebuilt: {dt}")
                except Exception as se: print(f"  ! Search failed {dt}: {se}")
            fixed.append(module)
        except Exception as e:
            import traceback; msg = f"{module}: {e}"; print(f"  FAIL: {msg}"); errors.append(msg); frappe.db.rollback()
    frappe.clear_cache()
    print(f"\nFixed: {fixed}\nErrors: {errors}\nCache cleared.")
