"""
saas_core/api/organization.py

Production-grade REST APIs for Organization management.
All endpoints are Frappe-whitelisted and require SaaS Super Admin or
System Manager role (enforced by _require_saas_admin()).

Endpoints:
    POST /api/method/saas_core.api.organization.create_organization
    POST /api/method/saas_core.api.organization.suspend_organization
    POST /api/method/saas_core.api.organization.reactivate_organization
    POST /api/method/saas_core.api.organization.upgrade_plan
    GET  /api/method/saas_core.api.organization.get_organization
    GET  /api/method/saas_core.api.organization.list_organizations
"""
import frappe
from frappe import _
from frappe.utils import now_datetime
from saas_core.api._auth import require_saas_admin


# ─── Create Organization ──────────────────────────────────────────────────────

@frappe.whitelist()
def create_organization(
    organization_name: str,
    subdomain: str,
    owner_email: str,
    plan: str = "starter",
    max_employees: int = None,
    max_admins: int = None,
):
    """
    Create a new Organization and enqueue site provisioning.

    Request (JSON body or query-string):
        organization_name   str     required
        subdomain           str     required  (lowercase, 2-63 chars)
        owner_email         str     required
        plan                str     optional  default: starter
        max_employees       int     optional  default: plan default
        max_admins          int     optional  default: plan default

    Response 200:
        { "status": "success", "organization": "<name>",
          "provisioning_status": "queued", "site_name": "<site>" }

    Errors:
        403  Not authorized
        409  Duplicate subdomain
        400  Invalid subdomain format / missing fields
    """
    require_saas_admin()

    # Build doc — validation + limit enforcement happens in the controller
    doc = frappe.get_doc({
        "doctype":           "Organization",
        "organization_name": organization_name,
        "subdomain":         subdomain.lower().strip(),
        "owner_email":       owner_email,
        "plan":              plan,
        "max_employees":     max_employees,
        "max_admins":        max_admins,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status":               "success",
        "organization":         doc.name,
        "provisioning_status":  doc.provisioning_status,
        "site_name":            f"{doc.subdomain}.{frappe.conf.get('saas_domain', 'hrms.localhost')}",
    }


# ─── Suspend Organization ─────────────────────────────────────────────────────

@frappe.whitelist()
def suspend_organization(organization: str, reason: str = ""):
    """
    Suspend an Active organization — disables tenant site access.

    Errors:
        403  Not authorized
        404  Organization not found
        400  Already suspended / terminated
    """
    require_saas_admin()
    org = _get_org_or_throw(organization)

    if org.status in ("Suspended", "Terminated"):
        frappe.throw(
            _(f"Organization '{organization}' is already '{org.status}'."),
            frappe.ValidationError,
        )

    _disable_tenant_site(org)
    org.status = "Suspended"
    org.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger("saas_core").info(
        f"Organization '{organization}' suspended. Reason: {reason}"
    )

    return {"status": "success", "organization": organization, "new_status": "Suspended"}


# ─── Reactivate Organization ──────────────────────────────────────────────────

@frappe.whitelist()
def reactivate_organization(organization: str):
    """
    Reactivate a Suspended organization.

    Errors:
        403  Not authorized
        404  Organization not found
        400  Not suspended
    """
    require_saas_admin()
    org = _get_org_or_throw(organization)

    if org.status != "Suspended":
        frappe.throw(
            _(f"Organization '{organization}' is not suspended (current: '{org.status}')."),
            frappe.ValidationError,
        )

    _enable_tenant_site(org)
    org.status = "Active"
    org.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "organization": organization, "new_status": "Active"}


# ─── Upgrade / Downgrade Plan ─────────────────────────────────────────────────

@frappe.whitelist()
def upgrade_plan(organization: str, new_plan: str):
    """
    Change the plan for an organization.
    Automatically syncs limits via the Subscription.sync_limits_to_org hook.

    Errors:
        403  Not authorized
        404  Organization not found
        400  Invalid plan / downgrade blocked
    """
    require_saas_admin()

    valid_plans = ("starter", "growth", "scale", "enterprise")
    if new_plan not in valid_plans:
        frappe.throw(
            _(f"Invalid plan '{new_plan}'. Must be one of: {', '.join(valid_plans)}."),
            frappe.ValidationError,
        )

    org = _get_org_or_throw(organization)
    old_plan = org.plan

    # Update the Subscription record (triggers sync_limits_to_org hook)
    sub_name = frappe.db.get_value("Subscription", {"organization": organization}, "name")
    if sub_name:
        sub = frappe.get_doc("Subscription", sub_name)
        sub.plan = new_plan
        sub.save(ignore_permissions=True)
    else:
        # No subscription yet — update org directly
        org.plan = new_plan
        org.save(ignore_permissions=True)

    # Push updated config to tenant site
    _push_config_to_tenant(org)
    frappe.db.commit()

    frappe.logger("saas_core").info(
        f"Organization '{organization}': plan changed {old_plan} → {new_plan}"
    )

    return {
        "status":       "success",
        "organization": organization,
        "old_plan":     old_plan,
        "new_plan":     new_plan,
    }


# ─── Get Organization ─────────────────────────────────────────────────────────

@frappe.whitelist()
def get_organization(organization: str):
    """
    Retrieve full details of an organization.

    Response 200:
        { organization fields + site_mapping + subscription }
    """
    require_saas_admin()
    org = _get_org_or_throw(organization)

    site_mapping = frappe.db.get_value(
        "Site Mapping",
        {"organization": organization},
        ["site_name", "database_name", "site_status", "provisioned_at"],
        as_dict=True,
    )

    subscription = frappe.db.get_value(
        "Subscription",
        {"organization": organization},
        ["plan", "billing_status", "start_date", "end_date"],
        as_dict=True,
    )

    admins = frappe.get_all(
        "Org Admin",
        filters={"organization": organization},
        fields=["email", "role", "status", "full_name"],
    )

    return {
        "status":       "success",
        "organization": org.as_dict(),
        "site_mapping": site_mapping or {},
        "subscription": subscription or {},
        "admins":       admins,
    }


# ─── List Organizations ───────────────────────────────────────────────────────

@frappe.whitelist()
def list_organizations(status: str = None, plan: str = None, page: int = 1, page_size: int = 25):
    """
    Paginated list of organizations with optional filters.
    """
    require_saas_admin()

    filters = {}
    if status:
        filters["status"] = status
    if plan:
        filters["plan"] = plan

    total = frappe.db.count("Organization", filters=filters)
    orgs = frappe.get_all(
        "Organization",
        filters=filters,
        fields=[
            "name", "organization_name", "subdomain", "owner_email",
            "status", "plan", "max_employees", "max_admins",
            "provisioning_status", "created_at",
        ],
        limit_start=(page - 1) * page_size,
        limit_page_length=page_size,
        order_by="created_at desc",
    )

    return {
        "status":    "success",
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "data":      orgs,
    }


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _get_org_or_throw(organization: str):
    if not frappe.db.exists("Organization", organization):
        frappe.throw(
            _(f"Organization '{organization}' not found."),
            frappe.DoesNotExistError,
        )
    return frappe.get_doc("Organization", organization)


def _disable_tenant_site(org):
    """Set maintenance_mode=1 on the tenant site via bench."""
    from saas_core.services.provisioning import _bench_root, _build_site_name, _run_cmd
    bench = _bench_root()
    site_name = _build_site_name(org.subdomain)
    _run_cmd(
        ["bench", "--site", site_name, "set-maintenance-mode", "on"],
        cwd=bench, timeout=30
    )


def _enable_tenant_site(org):
    """Lift maintenance_mode on the tenant site."""
    from saas_core.services.provisioning import _bench_root, _build_site_name, _run_cmd
    bench = _bench_root()
    site_name = _build_site_name(org.subdomain)
    _run_cmd(
        ["bench", "--site", site_name, "set-maintenance-mode", "off"],
        cwd=bench, timeout=30
    )


def _push_config_to_tenant(org):
    """Push updated plan limits into the tenant site_config after a plan change."""
    from saas_core.services.provisioning import _bench_root, _build_site_name, _run_cmd
    bench = _bench_root()
    site_name = _build_site_name(org.subdomain)
    for key, value in [
        ("saas_plan",          org.plan),
        ("saas_max_employees", str(org.max_employees)),
        ("saas_max_admins",    str(org.max_admins)),
    ]:
        _run_cmd(
            ["bench", "--site", site_name, "set-config", key, value],
            cwd=bench, timeout=30
        )
