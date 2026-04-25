import frappe

def setup_roles():
    roles = ["HR Admin", "HR User", "Employee"]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": 1
            }).insert()
            print(f"Role {role} created.")
        else:
            print(f"Role {role} already exists.")

if __name__ == "__main__":
    setup_roles()
    frappe.db.commit()
