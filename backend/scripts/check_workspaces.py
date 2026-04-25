import frappe

modules = ["HR Core", "HR Employee", "HR Attendance", "HR Leave", "HR Timesheet"]

for module in modules:
    workspaces = frappe.get_all("Workspace", filters={"module": module}, fields=["name", "module"])
    print(f"Module: {module} - Workspaces: {workspaces}")

    if not workspaces:
        print(f"Creating workspace for {module}")
        # Try to auto-generate
        try:
            from frappe.desk.doctype.workspace.workspace import create_workspace_for_module
            create_workspace_for_module(module)
            frappe.db.commit()
            print(f"Auto-generated workspace for {module}")
        except Exception as e:
            print(f"Failed to auto-generate workspace for {module}: {e}")
