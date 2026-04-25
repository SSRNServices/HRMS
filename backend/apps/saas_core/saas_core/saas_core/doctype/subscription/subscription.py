"""
saas_core/doctype/subscription/subscription.py

Manages subscription lifecycle and propagates plan changes to the
parent Organization's limits when a plan upgrade/downgrade is saved.
"""
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

# Plan → limits map (single source of truth shared across the saas_core app)
_PLAN_LIMITS = {
    "starter":    {"max_employees": 25,  "max_admins": 2},
    "growth":     {"max_employees": 100, "max_admins": 5},
    "scale":      {"max_employees": 500, "max_admins": 15},
    "enterprise": {"max_employees": 0,   "max_admins": 0},
}


class Subscription(Document):

    def before_save(self):
        self.validate_subscription()

    def on_update(self):
        self.sync_limits_to_org()

    # ── Validators ────────────────────────────────────────────────────────────

    def validate_subscription(self):
        """
        1. end_date must be after start_date if provided.
        2. trial_end_date must be within the subscription window.
        3. billing_status='canceled' requires cancellation_reason.
        """
        if self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw(
                _("End Date must be after Start Date for subscription {0}.").format(self.name)
            )

        if self.trial_end_date and self.start_date:
            if getdate(self.trial_end_date) < getdate(self.start_date):
                frappe.throw(_("Trial End Date cannot be before Start Date."))

        if self.billing_status == "canceled" and not self.cancellation_reason:
            frappe.throw(_("Cancellation Reason is required when billing_status is 'canceled'."))

    # ── Sync limits to parent Org ─────────────────────────────────────────────

    def sync_limits_to_org(self):
        """
        When a subscription's plan changes, update the linked Organization's
        max_employees, max_admins, and plan fields to stay in sync.
        """
        if not self.organization:
            return

        limits = _PLAN_LIMITS.get(self.plan, {})
        org = frappe.get_doc("Organization", self.organization)

        changed = False
        if org.plan != self.plan:
            org.plan = self.plan
            changed = True
        if limits.get("max_employees") and org.max_employees != limits["max_employees"]:
            org.max_employees = limits["max_employees"]
            changed = True
        if limits.get("max_admins") and org.max_admins != limits["max_admins"]:
            org.max_admins = limits["max_admins"]
            changed = True

        if changed:
            # Save without triggering the after_insert provisioning hook again
            org.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger("saas_core").info(
                f"Subscription {self.name}: synced plan '{self.plan}' limits to org '{self.organization}'."
            )


# ─── Standalone hook functions ─────────────────────────────────────────────────

def validate_subscription(doc, method=None):
    doc.validate_subscription()

def sync_limits_to_org(doc, method=None):
    doc.sync_limits_to_org()
