"""
saas_core/tasks.py

Scheduled tasks for SaaS maintenance.
Run via Frappe's scheduler (RQ workers).
"""
import frappe
from frappe.utils import now_datetime, get_datetime


def expire_subscriptions():
    """
    Hourly: Check for expired subscriptions and suspend organizations.
    Updates billing_status to 'expired' and sets org status to 'Suspended'.
    """
    log = frappe.logger("saas_core.tasks")

    # Find subscriptions that have expired
    expired_subs = frappe.db.get_all(
        "Subscription",
        filters={
            "end_date": ["<", now_datetime()],
            "billing_status": ["in", ["active", "trial"]],
        },
        fields=["name", "organization"],
    )

    for sub in expired_subs:
        try:
            # Update subscription
            frappe.db.set_value("Subscription", sub.name, {
                "billing_status": "expired",
            })

            # Suspend the organization
            org_name = sub.organization
            frappe.db.set_value("Organization", org_name, {
                "status": "Suspended",
            })

            # Disable tenant site
            from saas_core.services.provisioning import _disable_tenant_site
            org = frappe.get_doc("Organization", org_name)
            _disable_tenant_site(org)

            log.info(f"Expired subscription {sub.name}: suspended org '{org_name}'")

        except Exception as e:
            log.error(f"Failed to expire subscription {sub.name}: {e}")

    frappe.db.commit()


def daily_health_check():
    """
    Daily: Basic health checks on active organizations and sites.
    - Verify site mappings point to existing sites
    - Check for orphaned site mappings
    - Log warnings for inconsistencies
    """
    log = frappe.logger("saas_core.tasks")

    # Check site mappings
    mappings = frappe.db.get_all(
        "Site Mapping",
        filters={"site_status": "active"},
        fields=["name", "organization", "site_name"],
    )

    for mapping in mappings:
        # Basic check: ensure organization still exists
        if not frappe.db.exists("Organization", mapping.organization):
            log.warning(f"Orphaned site mapping {mapping.name}: org '{mapping.organization}' missing")
            continue

        # TODO: In future, add bench site-list check to verify site exists on disk

    log.info(f"Daily health check complete. Checked {len(mappings)} active site mappings.")


def cleanup_failed_provisioning():
    """
    Daily: Clean up old failed provisioning records.
    - Delete site mappings for failed provisions older than 30 days
    - Reset provisioning_status on stuck 'in_progress' orgs (older than 1 day)
    """
    log = frappe.logger("saas_core.tasks")
    from frappe.utils import add_days

    cutoff_date = add_days(now_datetime(), -30)

    # Clean up old failed mappings
    failed_mappings = frappe.db.get_all(
        "Site Mapping",
        filters={
            "site_status": "failed",
            "modified": ["<", cutoff_date],
        },
        fields=["name"],
    )

    for mapping in failed_mappings:
        frappe.delete_doc("Site Mapping", mapping.name, ignore_permissions=True)
        log.info(f"Cleaned up failed site mapping {mapping.name}")

    # Reset stuck provisioning
    stuck_orgs = frappe.db.get_all(
        "Organization",
        filters={
            "provisioning_status": "in_progress",
            "modified": ["<", add_days(now_datetime(), -1)],
        },
        fields=["name"],
    )

    for org in stuck_orgs:
        frappe.db.set_value("Organization", org.name, {
            "provisioning_status": "failed",
            "provisioning_error": "Provisioning timed out after 24 hours",
        })
        log.warning(f"Reset stuck provisioning for org '{org.name}'")

    frappe.db.commit()
    log.info("Cleanup complete.")