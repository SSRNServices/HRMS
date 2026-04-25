"""
saas_core/middleware.py

Global request middleware that enforces SaaS limits at the API level.
Runs before every request on the control site.

This is a lightweight check that blocks requests if the control site
itself is over-subscribed (e.g., too many active organizations).
"""
import frappe
from frappe import _


def enforce_global_limits():
    """
    Global SaaS limits enforced before any request.
    Currently checks:
    - Max total organizations (from site_config.json)
    - Max concurrent provisioning jobs
    """
    # Skip for non-API requests (e.g., desk UI)
    if not frappe.form_dict:
        return

    # Skip for public endpoints (e.g., login)
    if frappe.local.request.method == "GET" and frappe.local.request.endpoint in ("login", "logout"):
        return

    # Check global org limit
    max_orgs = frappe.conf.get("saas_max_organizations", 1000)  # default 1000
    active_orgs = frappe.db.count("Organization", {"status": "Active"})
    if active_orgs >= max_orgs:
        frappe.throw(
            _("Global organization limit reached ({0}). Contact support.").format(max_orgs),
            frappe.ValidationError,
        )

    # Check provisioning queue depth (prevent DoS from too many concurrent provisions)
    max_provisioning = frappe.conf.get("saas_max_concurrent_provisioning", 5)
    in_progress = frappe.db.count("Organization", {"provisioning_status": "in_progress"})
    if in_progress >= max_provisioning:
        frappe.throw(
            _("Too many organizations provisioning concurrently. Try again later."),
            frappe.ValidationError,
        )