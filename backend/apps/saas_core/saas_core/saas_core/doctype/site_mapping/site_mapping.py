"""
saas_core/doctype/site_mapping/site_mapping.py
Simple controller — most logic lives in services/provisioning.py.
"""
import frappe
from frappe.model.document import Document


class SiteMapping(Document):

    def before_insert(self):
        # Mirror subdomain from the linked Organization
        if self.organization:
            org = frappe.get_doc("Organization", self.organization)
            self.subdomain = org.subdomain

    def validate(self):
        self._check_unique_organization()

    def _check_unique_organization(self):
        """One site per organization — enforce at Python level too."""
        existing = frappe.db.get_value(
            "Site Mapping",
            {"organization": self.organization},
            "name",
        )
        if existing and existing != self.name:
            frappe.throw(
                frappe._(
                    "Organization '{0}' already has a site mapping: '{1}'."
                ).format(self.organization, existing)
            )
