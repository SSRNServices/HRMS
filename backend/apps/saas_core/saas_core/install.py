"""
saas_core/install.py
Runs once after `bench install-app saas_core` on the control site.
Creates SaaS-level roles and seed data that must exist before any
Organization or Subscription documents are created.
"""
import frappe


def after_install():
    _create_roles()
    _create_plan_defaults()
    frappe.db.commit()
    frappe.logger("saas_core").info("saas_core: after_install complete.")


# ─── Roles ────────────────────────────────────────────────────────────────────

def _create_roles():
    """
    Create SaaS-level roles on the control site.
    These roles exist ONLY on the control site, never on tenant sites.
    """
    roles = [
        {"role_name": "SaaS Super Admin", "desk_access": 1},
        {"role_name": "SaaS Support",     "desk_access": 1},
    ]
    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            role_doc = frappe.get_doc({"doctype": "Role", **r})
            role_doc.insert(ignore_permissions=True)
            frappe.logger("saas_core").info(f"Created role: {r['role_name']}")


# ─── Seed Plan Defaults ───────────────────────────────────────────────────────

PLAN_DEFAULTS = {
    "starter": {"max_employees": 25,  "max_admins": 2,  "features": []},
    "growth":  {"max_employees": 100, "max_admins": 5,  "features": ["leave_management", "timesheets"]},
    "scale":   {"max_employees": 500, "max_admins": 15, "features": ["leave_management", "timesheets", "recruitment", "performance"]},
    "enterprise": {"max_employees": 0, "max_admins": 0, "features": ["*"]},  # 0 = unlimited
}


def _create_plan_defaults():
    """
    Stores plan metadata in Site Config so it is available without a DocType.
    Alternatively, a 'Plan' DocType can be added in a later iteration.
    This keeps Phase -1 lean and avoids premature over-engineering.
    """
    existing = frappe.conf.get("saas_plans")
    if not existing:
        frappe.conf["saas_plans"] = PLAN_DEFAULTS
        # Persist to site config JSON
        from frappe.utils.data import cstr
        import json, os
        site_config_path = os.path.join(frappe.get_site_path(), "site_config.json")
        with open(site_config_path, "r") as f:
            config = json.load(f)
        config["saas_plans"] = PLAN_DEFAULTS
        with open(site_config_path, "w") as f:
            json.dump(config, f, indent=1)
        frappe.logger("saas_core").info("saas_core: plan defaults written to site_config.json")
