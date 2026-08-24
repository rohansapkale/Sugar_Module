import frappe
import frappe.sessions
from frappe import _
from frappe.utils import get_system_timezone

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/sugar-desk"
        raise frappe.Redirect

    frappe.db.commit()
    context.boot = get_boot()
    return context


@frappe.whitelist(methods=["POST"])
def get_context_for_dev():
    return get_boot()


def get_boot():
    user = frappe.session.user
    user_info = frappe.db.get_value(
        "User", user, ["full_name", "user_image", "email"], as_dict=True
    ) or {}

    roles = frappe.get_roles(user)
    companies = frappe.get_all("Company", fields=["name", "company_name", "default_currency"])
    default_company = frappe.defaults.get_user_default("company") or (companies[0].name if companies else "")

    try:
        csrf_token = frappe.sessions.get_csrf_token()
    except Exception:
        csrf_token = getattr(frappe.session, "csrf_token", "") or ""

    return {
        "site_name": frappe.local.site,
        "csrf_token": csrf_token,
        "session_user": user,
        "full_name": user_info.get("full_name") or user,
        "user_image": user_info.get("user_image"),
        "roles": roles,
        "companies": companies,
        "default_company": default_company,
        "date_format": frappe.get_system_settings("date_format") or "dd-mm-yyyy",
        "timezone": get_system_timezone(),
    }
