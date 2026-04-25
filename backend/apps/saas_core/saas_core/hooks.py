app_name = "saas_core"
app_title = "SaaS Core"
app_publisher = "SSRNServices"
app_description = "SaaS Control Layer — manages organizations, site provisioning, subscriptions, and limit enforcement"
app_email = "info@ssrnservices.com"
app_license = "mit"
app_version = "0.1.0"

# ─── Required Apps ────────────────────────────────────────────────────────────
# saas_core runs on the CONTROL SITE only; it does NOT depend on any HR app.
# required_apps = []

# ─── After Install ────────────────────────────────────────────────────────────
after_install = "saas_core.install.after_install"

# ─── Document Events ─────────────────────────────────────────────────────────
# Hooks that enforce SaaS rules at the DocType level (control site only).
doc_events = {
    "Organization": {
        "before_insert": "saas_core.saas_core.doctype.organization.organization.validate_unique_subdomain",
        "before_save":   "saas_core.saas_core.doctype.organization.organization.validate_plan_limits",
        "after_insert":  "saas_core.saas_core.doctype.organization.organization.after_insert_trigger",
    },
    "Subscription": {
        "before_save":   "saas_core.saas_core.doctype.subscription.subscription.validate_subscription",
        "on_update":     "saas_core.saas_core.doctype.subscription.subscription.sync_limits_to_org",
    },
    "Org Admin": {
        "before_insert": "saas_core.saas_core.doctype.org_admin.org_admin.validate_admin_limit",
    },
}

# ─── Scheduled Tasks ─────────────────────────────────────────────────────────
scheduler_events = {
    # Hourly: check subscriptions that have expired and suspend orgs
    "hourly": [
        "saas_core.tasks.expire_subscriptions",
    ],
    # Daily: generate billing alerts, clean up failed provisioning jobs
    "daily": [
        "saas_core.tasks.daily_health_check",
        "saas_core.tasks.cleanup_failed_provisioning",
    ],
}

# ─── Request Hooks ────────────────────────────────────────────────────────────
# Global API limit enforcer runs before every request on the control site.
before_request = ["saas_core.middleware.enforce_global_limits"]

# ─── Whitelisted API modules ──────────────────────────────────────────────────
# All public APIs are in saas_core/api/ — individually whitelisted per function.
