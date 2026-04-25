"""
saas_core/services/provisioning.py

Site Provisioning Engine — runs as a background job (Frappe RQ worker).
Every function here is idempotent: safe to retry on failure.

Flow:
    provision_site(organization)
        → _pre_flight_checks()
        → _create_site_record()
        → _run_bench_new_site()
        → _install_apps()
        → _configure_site()
        → _create_admin_user_on_tenant()
        → _mark_provisioning_complete()

On any exception:
        → _rollback_failed_site()
"""
import json
import os
import re
import subprocess
import secrets
import frappe
from frappe.utils import now_datetime

# ─── Constants ────────────────────────────────────────────────────────────────

# Apps installed on EVERY tenant site (order matters)
TENANT_APPS = ["frappe", "hr_core", "hr_employee", "hr_attendance"]

# Bench root — read from site_config.json key `bench_path`
# Fallback: parent of the frappe-bench sites directory
def _bench_root() -> str:
    configured = frappe.conf.get("bench_path")
    if configured:
        return configured
    # Infer from Frappe's own path resolution
    sites_path = frappe.get_site_path()          # e.g. /home/frappe/frappe-bench/sites/control.localhost
    return os.path.abspath(os.path.join(sites_path, "..", ".."))  # go up past sites/


# DNS base domain — set in site_config.json as `saas_domain`
def _base_domain() -> str:
    return frappe.conf.get("saas_domain", "hrms.localhost")


# ─── Public entry point (enqueued by Organization.after_insert_trigger) ───────

def provision_site(organization: str):
    """
    Entry point called by background worker.
    Wraps the full flow and handles rollback on any failure.
    """
    log = frappe.logger("saas_core.provisioning")
    log.info(f"[{organization}] Provisioning started.")

    try:
        _update_org_provisioning_status(organization, "in_progress", error=None)
        org = frappe.get_doc("Organization", organization)

        _pre_flight_checks(org)
        site_name = _build_site_name(org.subdomain)
        db_name   = _build_db_name(org.subdomain)
        admin_password = secrets.token_urlsafe(24)

        mapping = _create_site_record(org, site_name, db_name)
        _run_bench_new_site(site_name, db_name, admin_password, org)
        _install_apps(site_name)
        _configure_site(site_name, org)
        _create_admin_user_on_tenant(site_name, org, admin_password)
        _mark_provisioning_complete(org, mapping, site_name, db_name, admin_password)

        log.info(f"[{organization}] Provisioning complete → {site_name}")

    except ProvisioningError as exc:
        frappe.logger("saas_core.provisioning").error(
            f"[{organization}] Provisioning FAILED: {exc}"
        )
        _rollback_failed_site(organization, site_name=locals().get("site_name"), error=str(exc))
        raise  # re-raise so RQ marks the job as failed


# ─── Pre-flight ───────────────────────────────────────────────────────────────

def _pre_flight_checks(org):
    """Raise ProvisioningError early if the org is not ready to provision."""
    if org.status not in ("Pending", "Active"):
        raise ProvisioningError(
            f"Organization '{org.name}' has status '{org.status}'; cannot provision."
        )

    site_name = _build_site_name(org.subdomain)

    # Abort if a site_mapping already exists and is completed
    existing_mapping = frappe.db.get_value(
        "Site Mapping",
        {"organization": org.name, "site_status": "active"},
        "name",
    )
    if existing_mapping:
        raise ProvisioningError(
            f"Organization '{org.name}' already has an active site mapping: {existing_mapping}."
        )

    # Check bench exists
    bench = _bench_root()
    if not os.path.isdir(bench):
        raise ProvisioningError(
            f"Bench root not found at '{bench}'. Set 'bench_path' in site_config.json."
        )


# ─── Site Mapping record ─────────────────────────────────────────────────────

def _create_site_record(org, site_name: str, db_name: str):
    """
    Create (or get) a Site Mapping record in *pending* state.
    Idempotent: if a pending record already exists, return it.
    """
    existing = frappe.db.get_value(
        "Site Mapping",
        {"organization": org.name},
        "name",
    )
    if existing:
        mapping = frappe.get_doc("Site Mapping", existing)
        mapping.site_status = "pending"
        mapping.save(ignore_permissions=True)
        frappe.db.commit()
        return mapping

    mapping = frappe.get_doc({
        "doctype":       "Site Mapping",
        "organization":  org.name,
        "site_name":     site_name,
        "database_name": db_name,
        "subdomain":     org.subdomain,
        "site_status":   "pending",
        "bench_path":    _bench_root(),
    })
    mapping.insert(ignore_permissions=True)
    frappe.db.commit()
    return mapping


# ─── bench new-site ───────────────────────────────────────────────────────────

def _run_bench_new_site(site_name: str, db_name: str, admin_password: str, org):
    """
    Execute `bench new-site` via subprocess.
    Uses --db-name to get a deterministic database name.
    Raises ProvisioningError on non-zero exit code.
    """
    bench = _bench_root()
    cmd = [
        "bench", "new-site", site_name,
        "--db-name",           db_name,
        "--admin-password",    admin_password,
        "--mariadb-root-password", frappe.conf.get("db_root_password", "root"),
        "--no-mariadb-socket",
    ]

    frappe.logger("saas_core.provisioning").info(
        f"Running: {' '.join(cmd[:3])} {site_name} …"  # redact passwords from logs
    )

    result = _run_cmd(cmd, cwd=bench, timeout=300)
    if result.returncode != 0:
        raise ProvisioningError(
            f"bench new-site failed for '{site_name}'.\nSTDERR: {result.stderr}"
        )


# ─── App installation ─────────────────────────────────────────────────────────

def _install_apps(site_name: str):
    """
    Install TENANT_APPS on the newly created site, one by one.
    Frappe itself is installed by bench new-site; we skip it here.
    """
    bench = _bench_root()
    for app in TENANT_APPS:
        if app == "frappe":
            continue  # already installed by bench new-site
        cmd = ["bench", "--site", site_name, "install-app", app]
        result = _run_cmd(cmd, cwd=bench, timeout=180)
        if result.returncode != 0:
            raise ProvisioningError(
                f"Failed to install app '{app}' on site '{site_name}'.\nSTDERR: {result.stderr}"
            )
        frappe.logger("saas_core.provisioning").info(
            f"[{site_name}] App '{app}' installed."
        )


# ─── Site configuration ───────────────────────────────────────────────────────

def _configure_site(site_name: str, org):
    """
    Write per-tenant config keys into the tenant's site_config.json.
    These values are available via frappe.conf inside the tenant site.
    """
    bench = _bench_root()
    config_overrides = {
        "saas_organization":  org.name,
        "saas_subdomain":     org.subdomain,
        "saas_plan":          org.plan,
        "saas_max_employees": org.max_employees,
        "saas_max_admins":    org.max_admins,
        "saas_control_site":  frappe.local.site,  # control site hostname
    }
    for key, value in config_overrides.items():
        cmd = [
            "bench", "--site", site_name, "set-config",
            key, str(value),
        ]
        result = _run_cmd(cmd, cwd=bench, timeout=30)
        if result.returncode != 0:
            raise ProvisioningError(
                f"set-config '{key}' failed on '{site_name}'.\nSTDERR: {result.stderr}"
            )

    frappe.logger("saas_core.provisioning").info(
        f"[{site_name}] Site config written: {list(config_overrides.keys())}"
    )


# ─── Admin user creation on tenant site ──────────────────────────────────────

def _create_admin_user_on_tenant(site_name: str, org, admin_password: str):
    """
    Use `bench --site <site> execute` to call a Python snippet that creates
    the Org Admin user with the HR Admin role inside the tenant site.
    This is the correct way to interact with a different Frappe site from a
    background job running in the control site's context.
    """
    owner_email = org.owner_email
    bench = _bench_root()

    python_snippet = (
        "import frappe; frappe.connect(); "
        f"u=frappe.get_doc({{'doctype':'User','email':'{owner_email}',"
        f"'first_name':'Admin','new_password':'{admin_password}',"
        f"'roles':[{{'role':'HR Admin'}},{{'role':'System Manager'}}]}}); "
        "u.insert(ignore_permissions=True); frappe.db.commit(); "
        f"print('USER_CREATED:{owner_email}')"
    )

    cmd = ["bench", "--site", site_name, "execute", "--args", python_snippet]
    result = _run_cmd(cmd, cwd=bench, timeout=60)

    if result.returncode != 0 or f"USER_CREATED:{owner_email}" not in (result.stdout or ""):
        raise ProvisioningError(
            f"Admin user creation failed on '{site_name}'.\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )

    frappe.logger("saas_core.provisioning").info(
        f"[{site_name}] Admin user '{owner_email}' created on tenant site."
    )


# ─── Mark completion ──────────────────────────────────────────────────────────

def _mark_provisioning_complete(org, mapping, site_name: str, db_name: str, admin_password: str):
    """Update Site Mapping, Organization, and Org Admin records on success."""

    # 1. Update Site Mapping
    mapping.site_status    = "active"
    mapping.provisioned_at = now_datetime()
    mapping.apps_installed = json.dumps(TENANT_APPS)
    mapping.save(ignore_permissions=True)

    # 2. Update Organization
    org.status               = "Active"
    org.provisioning_status  = "completed"
    org.provisioning_error   = None
    # avoid re-triggering after_insert provisioning
    org.flags.ignore_after_insert = True
    org.save(ignore_permissions=True)

    # 3. Create Org Admin record (triggers admin limit check)
    _upsert_org_admin_record(org)

    frappe.db.commit()

    frappe.logger("saas_core.provisioning").info(
        f"Org '{org.name}' provisioning marked complete. Site: {site_name}"
    )


def _upsert_org_admin_record(org):
    """Create or update the control-site Org Admin record for the owner."""
    existing = frappe.db.get_value(
        "Org Admin",
        {"email": org.owner_email, "organization": org.name},
        "name",
    )
    if existing:
        admin_doc = frappe.get_doc("Org Admin", existing)
        admin_doc.status = "active"
        admin_doc.tenant_user_created = 1
        admin_doc.activated_at = now_datetime()
        admin_doc.save(ignore_permissions=True)
    else:
        admin_doc = frappe.get_doc({
            "doctype":             "Org Admin",
            "email":               org.owner_email,
            "organization":        org.name,
            "role":                "owner",
            "status":              "active",
            "full_name":           "Org Owner",
            "tenant_user_created": 1,
            "activated_at":        now_datetime(),
        })
        admin_doc.insert(ignore_permissions=True)


# ─── Rollback ─────────────────────────────────────────────────────────────────

def _rollback_failed_site(organization: str, site_name: str | None, error: str):
    """
    Attempt to clean up a partially created site:
    1. Drop the Frappe site (bench drop-site) if it was created.
    2. Update Site Mapping to 'failed'.
    3. Update Organization provisioning_status to 'failed'.
    """
    bench = _bench_root()
    log = frappe.logger("saas_core.provisioning")

    # Attempt bench drop-site (best-effort; may fail if site never existed)
    if site_name:
        log.warning(f"[{organization}] Rolling back — dropping site '{site_name}' …")
        drop_cmd = [
            "bench", "drop-site", site_name,
            "--root-password", frappe.conf.get("db_root_password", "root"),
            "--force",
        ]
        drop_result = _run_cmd(drop_cmd, cwd=bench, timeout=120)
        if drop_result.returncode == 0:
            log.info(f"[{organization}] Site '{site_name}' dropped successfully.")
        else:
            log.error(
                f"[{organization}] bench drop-site failed (may need manual cleanup): "
                f"{drop_result.stderr}"
            )

    # Update Site Mapping status
    try:
        mapping_name = frappe.db.get_value("Site Mapping", {"organization": organization}, "name")
        if mapping_name:
            frappe.db.set_value("Site Mapping", mapping_name, {
                "site_status": "failed",
            })
    except Exception as e:
        log.error(f"[{organization}] Could not update Site Mapping on rollback: {e}")

    # Update Organization provisioning status
    _update_org_provisioning_status(organization, "failed", error=error)
    frappe.db.commit()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _build_site_name(subdomain: str) -> str:
    return f"{subdomain}.{_base_domain()}"


def _build_db_name(subdomain: str) -> str:
    """Sanitize subdomain into a valid MariaDB database name (max 64 chars)."""
    safe = re.sub(r"[^a-z0-9_]", "_", subdomain.lower())
    return f"hrms_{safe}"[:64]


def _update_org_provisioning_status(organization: str, status: str, error: str | None):
    """Safe DB write that doesn't trigger any document hooks."""
    update = {"provisioning_status": status}
    if error is not None:
        update["provisioning_error"] = error[:500]  # truncate for DB field
    frappe.db.set_value("Organization", organization, update)
    frappe.db.commit()


def _run_cmd(cmd: list, cwd: str, timeout: int) -> subprocess.CompletedProcess:
    """Run a shell command and capture stdout/stderr. Does not raise on failure."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )


# ─── Custom Exception ─────────────────────────────────────────────────────────

class ProvisioningError(Exception):
    """Raised when a provisioning step fails; triggers full rollback."""
    pass
