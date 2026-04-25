"""
fix_hrms_workspaces.py
======================
Run via:
  echo "exec(open('/home/cyrus/Desktop/HRMS/backend/scripts/fix_hrms_workspaces.py').read()); run_fix()" \
    | bench --site dev.hrms.localhost console

What this does:
  1. For each HR module, update the Workspace document with:
       - Proper `content` JSON (required by the Workspace validator – must be a list)
       - Shortcuts pointing to each DocType
       - Links (Card Break + DocType links) for the sidebar
  2. Rebuilds the Global Search index for every DocType.
  3. Clears the Frappe cache.
"""

import frappe
import json
from frappe.utils.global_search import rebuild_for_doctype

MODULE_DOCTYPES = {
    "HR Core":       ["Company",      "Department"],
    "HR Employee":   ["Employee",     "Designation", "Location"],
    "HR Attendance": ["Attendance"],
    "HR Leave":      ["Leave Request", "Leave Policy"],
    "HR Timesheet":  ["Timesheet"],
}


def _build_content_json(doctypes):
    """
    Build the 'content' JSON that Frappe's Workspace validator expects.
    This is the block-editor content – a list of widget descriptors.
    Each shortcut card entry looks like:
      [{"id": "<uuid>", "type": "shortcut", "data": {...}}, ...]
    For simplicity we produce an empty list; shortcuts are stored in the
    child table (tabWorkspace Shortcut) and rendered independently.
    """
    return "[]"


def run_fix():
    fixed = []
    errors = []

    for module, doctypes in MODULE_DOCTYPES.items():
        try:
            print(f"\n{'='*50}")
            print(f"Processing: {module}")
            print(f"{'='*50}")

            # ── 1. Load workspace ─────────────────────────────────────
            if not frappe.db.exists("Workspace", module):
                print(f"  [!] Workspace '{module}' does not exist. Creating...")
                doc = frappe.new_doc("Workspace")
                doc.label  = module
                doc.title  = module
                doc.module = module
                doc.public = 1
                doc.content = _build_content_json(doctypes)
            else:
                doc = frappe.get_doc("Workspace", module)
                # content MUST be a valid JSON list string
                try:
                    parsed = json.loads(doc.content or "[]")
                    if not isinstance(parsed, list):
                        doc.content = "[]"
                except Exception:
                    doc.content = "[]"

            # ── 2. Reset child tables ─────────────────────────────────
            doc.links     = []
            doc.shortcuts = []

            # ── 3. Add Card Break + DocType links ─────────────────────
            doc.append("links", {
                "label":      module,
                "type":       "Card Break",
                "link_count": len(doctypes),
            })

            for dt in doctypes:
                doc.append("links", {
                    "type":      "Link",
                    "label":     dt,
                    "link_to":   dt,
                    "link_type": "DocType",
                    "onboard":   1,
                })

            # ── 4. Add Shortcuts ──────────────────────────────────────
            for dt in doctypes:
                doc.append("shortcuts", {
                    "type":     "DocType",
                    "label":    dt,
                    "link_to":  dt,
                })

            # ── 5. Ensure workspace is public ─────────────────────────
            doc.public = 1

            # ── 6. Save ───────────────────────────────────────────────
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"  ✓ Workspace saved with {len(doctypes)} DocTypes.")

            # ── 7. Rebuild Global Search ──────────────────────────────
            for dt in doctypes:
                try:
                    rebuild_for_doctype(dt)
                    print(f"  ✓ Global search rebuilt for: {dt}")
                except Exception as se:
                    print(f"  ! Global search failed for {dt}: {se}")

            fixed.append(module)

        except Exception as e:
            import traceback
            msg = f"FAILED {module}: {e}\n{traceback.format_exc()}"
            print(f"  ✗ {msg}")
            errors.append(msg)
            frappe.db.rollback()

    # ── 8. Clear all caches ───────────────────────────────────────────
    frappe.clear_cache()
    print("\n✓ Cache cleared.")

    # ── 9. Summary ────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"  Fixed:  {fixed}")
    if errors:
        print(f"  Errors ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("  No errors.")


if __name__ == "__main__":
    run_fix()
