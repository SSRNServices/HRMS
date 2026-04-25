"""
saas_core/doctype/organization/organization.py

Controller for the Organization DocType (SaaS control site only).

Responsibilities:
- Validate subdomain format and uniqueness
- Apply plan limits to max_employees / max_admins
- Trigger async provisioning after first insert
- Block status changes on suspended orgs where required
"""
import re
import json
import frappe
from frappe import _
from frappe.model.document import Document

# ─── Subdomain validation regex ───────────────────────────────────────────────
_SUBDOMAIN_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$")

# ─── Plan → default limits map (mirrors site_config) ─────────────────────────
_PLAN_LIMITS = {
    "starter":    {"max_employees": 25,  "max_admins": 2},
    "growth":     {"max_employees": 100, "max_admins": 5},
    "scale":      {"max_employees": 500, "max_admins": 15},
    "enterprise": {"max_employees": 0,   "max_admins": 0},
}


class Organization(Document):

    # ── Document hooks ────────────────────────────────────────────────────────

    def before_insert(self):
        self.validate_unique_subdomain()
        self.apply_plan_defaults()
        self.created_at = frappe.utils.now_datetime()
        self.provisioning_status = "queued"

    def before_save(self):
        self.validate_plan_limits()
        self.validate_subdomain_format()

    def after_insert(self):
        self.after_insert_trigger()

    # ── Validators ────────────────────────────────────────────────────────────

    def validate_subdomain_format(self):
        """Subdomain must be lowercase, start/end with alphanumeric, allow hyphens."""
        if not _SUBDOMAIN_RE.match(self.subdomain or ""):
            frappe.throw(
                _("Subdomain '{0}' is invalid. Use 2–63 lowercase letters, digits, or hyphens. "
                  "Must start and end with a letter or digit.").format(self.subdomain),
                title=_("Invalid Subdomain"),
            )

    def validate_unique_subdomain(self):
        """Enforce subdomain uniqueness at the Python level (DB unique constraint is secondary)."""
        existing = frappe.db.get_value("Organization", {"subdomain": self.subdomain}, "name")
        if existing and existing != self.name:
            frappe.throw(
                _("Subdomain '{0}' is already taken by organization '{1}'.").format(
                    self.subdomain, existing
                ),
                title=_("Duplicate Subdomain"),
            )

    def validate_plan_limits(self):
        """
        Ensure max_employees / max_admins are at least what the plan requires.
        Super Admin can set higher values; we only prevent going BELOW the plan minimum.
        """
        plan_defaults = _PLAN_LIMITS.get(self.plan, {})
        min_emp  = plan_defaults.get("max_employees", 0)
        min_adm  = plan_defaults.get("max_admins", 0)

        # 0 = unlimited (enterprise) — skip checks
        if min_emp and self.max_employees and self.max_employees < min_emp:
            frappe.throw(
                _("max_employees cannot be less than {0} for the '{1}' plan.").format(
                    min_emp, self.plan
                )
            )
        if min_adm and self.max_admins and self.max_admins < min_adm:
            frappe.throw(
                _("max_admins cannot be less than {0} for the '{1}' plan.").format(
                    min_adm, self.plan
                )
            )

    def apply_plan_defaults(self):
        """Set limits from plan when creating a new org (only if not already provided)."""
        defaults = _PLAN_LIMITS.get(self.plan, {})
        if not self.max_employees:
            self.max_employees = defaults.get("max_employees", 25)
        if not self.max_admins:
            self.max_admins = defaults.get("max_admins", 2)

    # ── Post-insert trigger ───────────────────────────────────────────────────

    def after_insert_trigger(self):
        """
        Enqueue site provisioning as a background job so the HTTP response
        returns immediately while provisioning runs asynchronously.
        """
        frappe.enqueue(
            "saas_core.services.provisioning.provision_site",
            queue="long",
            timeout=900,  # 15-minute timeout for bench operations
            is_async=True,
            organization=self.name,
        )
        frappe.logger("saas_core").info(
            f"Organization '{self.name}' created — provisioning job enqueued."
        )


# ─── Standalone hook functions (called from hooks.py doc_events) ─────────────
# These simply delegate to the Document class methods above.

def validate_unique_subdomain(doc, method=None):
    doc.validate_unique_subdomain()

def validate_plan_limits(doc, method=None):
    doc.validate_plan_limits()

def after_insert_trigger(doc, method=None):
    doc.after_insert_trigger()
