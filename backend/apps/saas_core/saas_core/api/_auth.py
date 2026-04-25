"""
saas_core/api/_auth.py

Shared authentication helpers for SaaS API endpoints.
"""
import frappe
from frappe import _


def require_saas_admin():
    """
    Require the user to have 'SaaS Super Admin' or 'System Manager' role.
    Throws 403 if not authorized.
    """
    user = frappe.session.user
    if user == "Administrator":
        return  # always allow

    roles = frappe.get_roles(user)
    if "SaaS Super Admin" not in roles and "System Manager" not in roles:
        frappe.throw(
            _("Access denied. SaaS Super Admin or System Manager role required."),
            frappe.PermissionError,
        )