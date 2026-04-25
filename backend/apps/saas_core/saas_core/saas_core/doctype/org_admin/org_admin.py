"""
saas_core/doctype/org_admin/org_admin.py

Controller for Org Admin (global reference record on the control site).
Enforces the max_admins limit before a new admin is added.
Manages invite token generation.
"""
import secrets
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, now_datetime, get_datetime

INVITE_TOKEN_EXPIRY_DAYS = 7


class OrgAdmin(Document):

    def before_insert(self):
        self.validate_admin_limit()
        self._generate_invite_token()
        self.invited_at = now_datetime()

    def validate(self):
        self._validate_unique_admin_per_org()

    # ── Limit enforcement ─────────────────────────────────────────────────────

    def validate_admin_limit(self):
        """
        Count existing active Org Admins for this organization.
        Raise if the count already meets or exceeds max_admins.
        max_admins == 0 means unlimited (enterprise plan).
        """
        org = frappe.get_doc("Organization", self.organization)
        max_admins = org.max_admins or 0

        if max_admins == 0:
            return  # unlimited

        current_count = frappe.db.count(
            "Org Admin",
            filters={
                "organization": self.organization,
                "status": ["!=", "deactivated"],
            },
        )
        if current_count >= max_admins:
            frappe.throw(
                _(
                    "Admin limit reached for organization '{0}'. "
                    "Max allowed: {1}. Current active: {2}. "
                    "Upgrade the plan to add more admins."
                ).format(self.organization, max_admins, current_count),
                title=_("Admin Limit Exceeded"),
            )

    def _validate_unique_admin_per_org(self):
        """Same email cannot be an admin of the same organization twice."""
        existing = frappe.db.get_value(
            "Org Admin",
            {"email": self.email, "organization": self.organization},
            "name",
        )
        if existing and existing != self.name:
            frappe.throw(
                _("'{0}' is already registered as an admin for '{1}'.").format(
                    self.email, self.organization
                )
            )

    # ── Invite token ──────────────────────────────────────────────────────────

    def _generate_invite_token(self):
        """Generate a cryptographically secure invite token."""
        self.invite_token = secrets.token_urlsafe(32)
        self.invite_token_expiry = add_days(now_datetime(), INVITE_TOKEN_EXPIRY_DAYS)

    def is_invite_valid(self):
        """Check if invite token is still valid (not expired)."""
        if not self.invite_token_expiry:
            return False
        return get_datetime(self.invite_token_expiry) > get_datetime(now_datetime())

    def mark_activated(self):
        """Mark admin as active after successful first login / password set."""
        self.status = "active"
        self.activated_at = now_datetime()
        self.invite_token = None
        self.invite_token_expiry = None
        self.save(ignore_permissions=True)
        frappe.db.commit()


# ─── Standalone hook function ─────────────────────────────────────────────────

def validate_admin_limit(doc, method=None):
    doc.validate_admin_limit()
