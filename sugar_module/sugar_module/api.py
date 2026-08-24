import json
import frappe
import frappe.sessions
from frappe import _
from frappe.utils import flt, nowdate, getdate


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_boot():
    """
    Returns initial boot information for the Sugar Desk Vue app
    """
    user = frappe.session.user
    user_info = frappe.db.get_value(
        "User", user, ["full_name", "user_image", "email"], as_dict=True
    ) or {}
    
    roles = frappe.get_roles(user)
    companies = frappe.get_all("Company", fields=["name", "company_name", "default_currency"], ignore_permissions=True)
    default_company = frappe.defaults.get_user_default("company") or (companies[0].name if companies else "Rajendra Narahari Lokhande")

    try:
        csrf_token = frappe.sessions.get_csrf_token()
    except Exception:
        csrf_token = getattr(frappe.session, "csrf_token", "") or ""

    return {
        "user": user,
        "full_name": user_info.get("full_name") or user,
        "user_image": user_info.get("user_image"),
        "roles": roles,
        "companies": companies,
        "default_company": default_company,
        "csrf_token": csrf_token,
        "today": nowdate(),
    }


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def search_ledgers_and_parties(query=None, doctype=None, limit=50, **kwargs):
    """
    High-speed typeahead search for real Frappe Sugar Module entities:
    - Supplier (Sugar Mills / Cane Suppliers)
    - Customer (Parties / Buyers)
    - Broker (Sugar Brokers)
    - Item (Sugar Grades e.g. M30, S-30, SS30)
    - Account (Bank & Cash Accounts)
    """
    query = (query or frappe.form_dict.get("query") or "").strip()
    doctype = doctype or frappe.form_dict.get("doctype")
    limit = int(limit or frappe.form_dict.get("limit") or 50)
    results = []

    if doctype:
        filters = {}
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
        
        if doctype == "Supplier":
            if query:
                or_filters["supplier_name"] = ["like", f"%{query}%"]
            fields = ["name", "supplier_name"]
        elif doctype == "Customer":
            if query:
                or_filters["customer_name"] = ["like", f"%{query}%"]
            fields = ["name", "customer_name"]
        elif doctype == "Broker":
            if query:
                or_filters["broker_name"] = ["like", f"%{query}%"]
            fields = ["name", "broker_name", "mobile_no", "city"]
        elif doctype == "Item":
            if query:
                or_filters["item_name"] = ["like", f"%{query}%"]
            fields = ["name", "item_name", "stock_uom"]
        elif doctype == "Account":
            if query:
                or_filters["account_name"] = ["like", f"%{query}%"]
            fields = ["name", "account_name", "account_type"]
        elif doctype == "Sugar Purchase":
            if query:
                or_filters["name"] = ["like", f"%{query}%"]
                or_filters["supplier"] = ["like", f"%{query}%"]
                or_filters["item"] = ["like", f"%{query}%"]
            fields = ["name", "supplier", "item", "purchase_qty_quintal", "purchase_rate", "total_amount", "available_qty_quintal"]
        elif doctype == "Dispatch Entry":
            if query:
                or_filters["name"] = ["like", f"%{query}%"]
                or_filters["customer_name"] = ["like", f"%{query}%"]
                or_filters["broker"] = ["like", f"%{query}%"]
            fields = ["name", "customer_name", "broker", "vehicle_no", "total_amount", "balance_amount"]
        else:
            fields = ["name"]

        # Order by creation desc for vouchers/purchases so latest records appear at the top
        order_by = "creation desc" if doctype in ("Sugar Purchase", "Dispatch Entry", "Purchase Payment", "Broker Party Payment") else "name asc"

        docs = frappe.get_all(
            doctype,
            filters=filters,
            or_filters=or_filters if query else None,
            fields=fields,
            limit=limit,
            order_by=order_by,
            ignore_permissions=True
        )
        for d in docs:
            if doctype == "Sugar Purchase":
                display_name = f"{d.name} — {d.supplier} ({d.item})"
                extra_type = f"Stock: {flt(d.available_qty_quintal)} Qtl"
            elif doctype == "Dispatch Entry":
                display_name = f"{d.name} — {d.customer_name}"
                extra_type = f"Bal: ₹{flt(d.balance_amount)}"
            else:
                display_name = (
                    d.get("supplier_name") or
                    d.get("customer_name") or
                    d.get("broker_name") or
                    d.get("item_name") or
                    d.get("account_name") or
                    d.name
                )
                extra_type = d.get("city") or d.get("account_type") or doctype
            results.append({
                "id": d.name,
                "name": d.name,
                "label": display_name,
                "doctype": doctype,
                "type": extra_type if extra_type else doctype,
                "details": d
            })
        return results

    # Global search across all parties, items, and accounts
    # 1. Accounts (Cash & Bank)
    accounts = frappe.get_all(
        "Account",
        filters={"is_group": 0},
        or_filters={"name": ["like", f"%{query}%"], "account_name": ["like", f"%{query}%"]} if query else None,
        fields=["name", "account_name", "account_type"],
        limit=10,
        ignore_permissions=True
    )
    for a in accounts:
        results.append({
            "id": a.name,
            "name": a.name,
            "label": a.account_name or a.name,
            "doctype": "Account",
            "type": a.account_type or "Bank/Cash A/c",
        })

    # 2. Suppliers
    suppliers = frappe.get_all(
        "Supplier",
        or_filters={"name": ["like", f"%{query}%"], "supplier_name": ["like", f"%{query}%"]} if query else None,
        fields=["name", "supplier_name"],
        limit=10,
        ignore_permissions=True
    )
    for s in suppliers:
        results.append({
            "id": s.name,
            "name": s.name,
            "label": s.supplier_name or s.name,
            "doctype": "Supplier",
            "type": "Sugar Mill / Supplier",
        })

    # 3. Customers
    customers = frappe.get_all(
        "Customer",
        or_filters={"name": ["like", f"%{query}%"], "customer_name": ["like", f"%{query}%"]} if query else None,
        fields=["name", "customer_name"],
        limit=10,
        ignore_permissions=True
    )
    for c in customers:
        results.append({
            "id": c.name,
            "name": c.name,
            "label": c.customer_name or c.name,
            "doctype": "Customer",
            "type": "Customer / Party",
        })

    # 4. Brokers
    brokers = frappe.get_all(
        "Broker",
        or_filters={"name": ["like", f"%{query}%"], "broker_name": ["like", f"%{query}%"]} if query else None,
        fields=["name", "broker_name", "city"],
        limit=10,
        ignore_permissions=True
    )
    for b in brokers:
        results.append({
            "id": b.name,
            "name": b.name,
            "label": b.broker_name or b.name,
            "doctype": "Broker",
            "type": f"Broker ({b.city})" if b.city else "Broker",
        })

    # 5. Items (Sugar, Gunny bags, etc.)
    items = frappe.get_all(
        "Item",
        or_filters={"name": ["like", f"%{query}%"], "item_name": ["like", f"%{query}%"]} if query else None,
        fields=["name", "item_name", "stock_uom"],
        limit=10,
        ignore_permissions=True
    )
    for i in items:
        results.append({
            "id": i.name,
            "name": i.name,
            "label": i.item_name or i.name,
            "doctype": "Item",
            "type": f"Item ({i.stock_uom or 'Qtl'})",
        })

    return results


def resolve_link(doctype, value, name_field=None):
    """
    Safely resolves a document ID if the user typed or passed a human label/name.
    """
    if not value:
        return None
    value = str(value).strip()
    # Check if value is directly the document name
    if frappe.db.exists(doctype, value):
        return value
    
    # Try searching by common name fields
    search_fields = [name_field] if name_field else []
    if doctype == "Broker":
        search_fields += ["broker_name"]
    elif doctype == "Customer":
        search_fields += ["customer_name"]
    elif doctype == "Supplier":
        search_fields += ["supplier_name"]
    elif doctype == "Item":
        search_fields += ["item_name"]
    elif doctype == "Sugar Purchase":
        sp = frappe.db.get_value("Sugar Purchase", {"name": value}) or frappe.db.get_value("Sugar Purchase", {"supplier": value})
        if sp:
            return sp

    for sf in search_fields:
        if not sf:
            continue
        res = frappe.db.get_value(doctype, {sf: value}, "name")
        if res:
            return res
        res = frappe.db.get_value(doctype, {sf: ["like", f"%{value}%"]}, "name")
        if res:
            return res
            
    return value


@frappe.whitelist(methods=["POST"], allow_guest=True)
def save_sugar_voucher(voucher_type, payload, submit=0):
    """
    Saves and optionally submits vouchers directly into Frappe Sugar Module DocTypes.
    """
    if isinstance(payload, str):
        payload = json.loads(payload)

    submit = int(submit)

    if voucher_type == "Sugar Purchase":
        supplier = resolve_link("Supplier", payload.get("supplier"), "supplier_name") or payload.get("supplier")
        item = resolve_link("Item", payload.get("item"), "item_name") or "S-302526"

        doc = frappe.new_doc("Sugar Purchase")
        doc.supplier = supplier
        doc.company = payload.get("company") or frappe.defaults.get_user_default("company") or "Rajendra Narahari Lokhande"
        doc.purchase_date = payload.get("purchase_date") or nowdate()
        doc.item = item
        doc.purchase_qty_quintal = flt(payload.get("purchase_qty_quintal"))
        doc.purchase_rate = flt(payload.get("purchase_rate"))
        doc.total_amount = doc.purchase_qty_quintal * doc.purchase_rate
        doc.status = "Draft"
        doc.insert(ignore_permissions=True)
        if submit:
            doc.submit()
        return {
            "success": True,
            "doctype": "Sugar Purchase",
            "name": doc.name,
            "docstatus": doc.docstatus,
            "total_amount": doc.total_amount,
            "message": _("Sugar Purchase {0} saved successfully").format(doc.name),
        }

    elif voucher_type == "Dispatch Entry":
        sugar_purchase = resolve_link("Sugar Purchase", payload.get("sugar_purchase"))
        # If sugar purchase is not provided, pick the latest active sugar purchase as fallback
        if not sugar_purchase or not frappe.db.exists("Sugar Purchase", sugar_purchase):
            latest_sp = frappe.get_all("Sugar Purchase", order_by="creation desc", limit=1, ignore_permissions=True)
            if latest_sp:
                sugar_purchase = latest_sp[0].name
            else:
                frappe.throw(_("Please select a valid Source Sugar Purchase lot."))

        broker = resolve_link("Broker", payload.get("broker"), "broker_name")
        customer_name = resolve_link("Customer", payload.get("customer_name"), "customer_name") or payload.get("customer_name")
        item = resolve_link("Item", payload.get("item"), "item_name") or "S-302526"

        doc = frappe.new_doc("Dispatch Entry")
        doc.sugar_purchase = sugar_purchase
        doc.company = payload.get("company") or frappe.defaults.get_user_default("company") or "Rajendra Narahari Lokhande"
        doc.broker = broker
        doc.customer_name = customer_name
        doc.vehicle_no = payload.get("vehicle_no")
        doc.dispatch_date = payload.get("dispatch_date") or nowdate()
        doc.item = item
        doc.dispatch_qty_quintal = flt(payload.get("dispatch_qty_quintal"))
        doc.rate = flt(payload.get("rate"))
        doc.total_amount = doc.dispatch_qty_quintal * doc.rate
        doc.balance_amount = doc.total_amount - flt(payload.get("paid_amount", 0))
        doc.paid_amount = flt(payload.get("paid_amount", 0))
        doc.payment_status = "Paid" if doc.balance_amount <= 0 else ("Partially Paid" if doc.paid_amount > 0 else "Unpaid")
        doc.status = "Draft"
        doc.insert(ignore_permissions=True)
        if submit:
            doc.submit()
        return {
            "success": True,
            "doctype": "Dispatch Entry",
            "name": doc.name,
            "docstatus": doc.docstatus,
            "total_amount": doc.total_amount,
            "message": _("Dispatch Entry {0} saved successfully").format(doc.name),
        }

    elif voucher_type == "Purchase Payment":
        supplier = resolve_link("Supplier", payload.get("supplier"), "supplier_name") or payload.get("supplier")
        sugar_purchase = resolve_link("Sugar Purchase", payload.get("sugar_purchase"))

        doc = frappe.new_doc("Purchase Payment")
        doc.supplier = supplier
        doc.sugar_purchase = sugar_purchase
        doc.payment_date = payload.get("payment_date") or nowdate()
        doc.payment_mode = payload.get("payment_mode") or "NEFT"
        doc.reference_no = payload.get("reference_no")
        doc.utr_no = payload.get("utr_no")
        doc.total_amount = flt(payload.get("total_amount") or payload.get("paid_amount"))
        doc.paid_amount = flt(payload.get("paid_amount"))
        doc.remaining_amount = max(0, doc.total_amount - doc.paid_amount)
        doc.payment_status = "Paid" if doc.remaining_amount <= 0 else ("Partially Paid" if doc.paid_amount > 0 else "Unpaid")
        doc.insert(ignore_permissions=True)
        if submit:
            doc.submit()
        return {
            "success": True,
            "doctype": "Purchase Payment",
            "name": doc.name,
            "docstatus": doc.docstatus,
            "paid_amount": doc.paid_amount,
            "message": _("Purchase Payment {0} recorded successfully").format(doc.name),
        }

    elif voucher_type == "Broker Party Payment":
        broker = resolve_link("Broker", payload.get("broker"), "broker_name")
        customer = resolve_link("Customer", payload.get("customer"), "customer_name") or payload.get("customer")
        dispatch_entry = resolve_link("Dispatch Entry", payload.get("dispatch_entry"))

        doc = frappe.new_doc("Broker Party Payment")
        doc.dispatch_entry = dispatch_entry
        doc.broker = broker
        doc.customer = customer
        doc.payment_date = payload.get("payment_date") or nowdate()
        doc.payment_mode = payload.get("payment_mode") or "NEFT"
        doc.utr_no = payload.get("utr_no")
        doc.paid_amount = flt(payload.get("paid_amount"))
        doc.remarks = payload.get("remarks")
        doc.insert(ignore_permissions=True)
        if submit:
            doc.submit()
        return {
            "success": True,
            "doctype": "Broker Party Payment",
            "name": doc.name,
            "docstatus": doc.docstatus,
            "paid_amount": doc.paid_amount,
            "message": _("Broker Party Payment {0} recorded successfully").format(doc.name),
        }

    else:
        frappe.throw(_("Unsupported voucher type: {0}").format(voucher_type))


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_register_data(voucher_type=None, query=None, limit=100, **kwargs):
    """
    Returns full register list with rich columns and totals for Sugar Purchase, Dispatch Entry, Purchase Payment, Broker Party Payment.
    """
    voucher_type = voucher_type or frappe.form_dict.get("voucher_type") or "Sugar Purchase"
    query = (query or frappe.form_dict.get("query") or "").strip()
    limit = int(limit or frappe.form_dict.get("limit") or 100)

    if voucher_type in ("Sugar Purchase", "purchase"):
        filters = {}
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["supplier"] = ["like", f"%{query}%"]
            or_filters["item"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Sugar Purchase",
            filters=filters,
            or_filters=or_filters if query else None,
            fields=[
                "name", "purchase_date", "supplier", "item", "purchase_qty_quintal",
                "purchase_rate", "total_amount", "paid_amount", "remaining_amount",
                "payment_status", "dispatched_qty_quintal", "available_qty_quintal",
                "status", "docstatus"
            ],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        return {
            "voucher_type": "Sugar Purchase",
            "title": "Sugar Purchase Register (List)",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_qty": sum(flt(r.purchase_qty_quintal) for r in records),
                "total_amount": sum(flt(r.total_amount) for r in records),
                "total_available_qty": sum(flt(r.available_qty_quintal) for r in records),
                "total_paid": sum(flt(r.paid_amount) for r in records),
                "total_remaining": sum(flt(r.remaining_amount) for r in records),
            }
        }

    elif voucher_type in ("Dispatch Entry", "dispatch"):
        filters = {}
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["customer_name"] = ["like", f"%{query}%"]
            or_filters["vehicle_no"] = ["like", f"%{query}%"]
            or_filters["broker"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Dispatch Entry",
            filters=filters,
            or_filters=or_filters if query else None,
            fields=[
                "name", "dispatch_date", "customer_name", "broker", "vehicle_no",
                "item", "dispatch_qty_quintal", "rate", "total_amount", "paid_amount",
                "balance_amount", "payment_status", "status", "docstatus", "sugar_purchase"
            ],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for r in records:
            if r.broker:
                r["broker_name"] = frappe.db.get_value("Broker", r.broker, "broker_name") or r.broker

        return {
            "voucher_type": "Dispatch Entry",
            "title": "Dispatch Entry Register (List)",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_qty": sum(flt(r.dispatch_qty_quintal) for r in records),
                "total_amount": sum(flt(r.total_amount) for r in records),
                "total_paid": sum(flt(r.paid_amount) for r in records),
                "total_balance": sum(flt(r.balance_amount) for r in records),
            }
        }

    elif voucher_type in ("Purchase Payment", "payment"):
        filters = {}
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["supplier"] = ["like", f"%{query}%"]
            or_filters["utr_no"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Purchase Payment",
            filters=filters,
            or_filters=or_filters if query else None,
            fields=[
                "name", "payment_date", "supplier", "sugar_purchase", "payment_mode",
                "reference_no", "utr_no", "total_amount", "paid_amount", "remaining_amount",
                "payment_status", "docstatus"
            ],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        return {
            "voucher_type": "Purchase Payment",
            "title": "Purchase Payment Register (List)",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_paid": sum(flt(r.paid_amount) for r in records),
            }
        }

    elif voucher_type in ("Broker Party Payment", "receipt"):
        filters = {}
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["customer"] = ["like", f"%{query}%"]
            or_filters["utr_no"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Broker Party Payment",
            filters=filters,
            or_filters=or_filters if query else None,
            fields=[
                "name", "payment_date", "customer", "broker", "dispatch_entry",
                "payment_mode", "utr_no", "paid_amount", "remarks", "docstatus"
            ],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for r in records:
            if r.broker:
                r["broker_name"] = frappe.db.get_value("Broker", r.broker, "broker_name") or r.broker

        return {
            "voucher_type": "Broker Party Payment",
            "title": "Broker Party Payment (Receipt) Register",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_received": sum(flt(r.paid_amount) for r in records),
            }
        }

    return {"records": [], "summary": {}}


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_daybook(date=None, voucher_type=None, limit=100, **kwargs):
    """
    Returns unified daybook feed of all sugar transactions.
    """
    date = date or frappe.form_dict.get("date")
    voucher_type = voucher_type or frappe.form_dict.get("voucher_type")
    limit = int(limit or frappe.form_dict.get("limit") or 100)
    entries = []
    has_date_filter = bool(date and date != "all")

    # 1. Sugar Purchase (F9)
    if not voucher_type or voucher_type == "Sugar Purchase":
        filters = {"purchase_date": date} if has_date_filter else {}
        purchases = frappe.get_all(
            "Sugar Purchase",
            filters=filters,
            fields=["name", "purchase_date", "supplier", "item", "purchase_qty_quintal", "purchase_rate", "total_amount", "docstatus", "status"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for p in purchases:
            entries.append({
                "id": p.name,
                "name": p.name,
                "date": str(p.purchase_date or "—"),
                "voucher_type": "Sugar Purchase",
                "fk_code": "F9",
                "particulars": p.supplier or "Supplier",
                "details": f"{p.item or 'Sugar'} · {p.purchase_qty_quintal or 0} Qtl @ ₹{p.purchase_rate or 0}",
                "ref_no": p.name,
                "debit": 0,
                "credit": flt(p.total_amount),
                "total": flt(p.total_amount),
                "status": "Submitted" if p.docstatus == 1 else ("Draft" if p.docstatus == 0 else "Cancelled"),
                "doctype": "Sugar Purchase",
            })

    # 2. Dispatch Entry (F8)
    if not voucher_type or voucher_type == "Dispatch Entry":
        filters = {"dispatch_date": date} if has_date_filter else {}
        dispatches = frappe.get_all(
            "Dispatch Entry",
            filters=filters,
            fields=["name", "dispatch_date", "customer_name", "broker", "vehicle_no", "item", "dispatch_qty_quintal", "rate", "total_amount", "docstatus", "status"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for d in dispatches:
            broker_name = frappe.db.get_value("Broker", d.broker, "broker_name") if d.broker else "Direct"
            entries.append({
                "id": d.name,
                "name": d.name,
                "date": str(d.dispatch_date or "—"),
                "voucher_type": "Dispatch Entry",
                "fk_code": "F8",
                "particulars": d.customer_name or "Customer",
                "details": f"Broker: {broker_name or d.broker or 'Direct'} · Veh: {d.vehicle_no or 'N/A'} · {d.dispatch_qty_quintal or 0} Qtl",
                "ref_no": d.vehicle_no or d.name,
                "debit": flt(d.total_amount),
                "credit": 0,
                "total": flt(d.total_amount),
                "status": "Submitted" if d.docstatus == 1 else ("Draft" if d.docstatus == 0 else "Cancelled"),
                "doctype": "Dispatch Entry",
            })

    # 3. Purchase Payment (F5)
    if not voucher_type or voucher_type == "Purchase Payment":
        filters = {"payment_date": date} if has_date_filter else {}
        payments = frappe.get_all(
            "Purchase Payment",
            filters=filters,
            fields=["name", "payment_date", "supplier", "sugar_purchase", "payment_mode", "utr_no", "paid_amount", "docstatus"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for py in payments:
            entries.append({
                "id": py.name,
                "name": py.name,
                "date": str(py.payment_date or "—"),
                "voucher_type": "Purchase Payment",
                "fk_code": "F5",
                "particulars": py.supplier or "Supplier Payment",
                "details": f"Ref: {py.sugar_purchase or 'N/A'} · {py.payment_mode or 'NEFT'} · UTR: {py.utr_no or '-'}",
                "ref_no": py.utr_no or py.name,
                "debit": flt(py.paid_amount),
                "credit": 0,
                "total": flt(py.paid_amount),
                "status": "Submitted" if py.docstatus == 1 else "Draft",
                "doctype": "Purchase Payment",
            })

    # 4. Broker Party Payment (F6)
    if not voucher_type or voucher_type == "Broker Party Payment":
        filters = {"payment_date": date} if has_date_filter else {}
        b_payments = frappe.get_all(
            "Broker Party Payment",
            filters=filters,
            fields=["name", "payment_date", "customer", "broker", "dispatch_entry", "payment_mode", "utr_no", "paid_amount", "docstatus"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )
        for bp in b_payments:
            broker_name = frappe.db.get_value("Broker", bp.broker, "broker_name") if bp.broker else bp.broker
            entries.append({
                "id": bp.name,
                "name": bp.name,
                "date": str(bp.payment_date or "—"),
                "voucher_type": "Broker Party Payment",
                "fk_code": "F6",
                "particulars": bp.customer or "Customer Receipt",
                "details": f"Broker: {broker_name or '-'} · Dis: {bp.dispatch_entry or '-'} · {bp.payment_mode or 'NEFT'}",
                "ref_no": bp.utr_no or bp.name,
                "debit": 0,
                "credit": flt(bp.paid_amount),
                "total": flt(bp.paid_amount),
                "status": "Submitted" if bp.docstatus == 1 else "Draft",
                "doctype": "Broker Party Payment",
            })

    entries.sort(key=lambda x: (x.get("date", ""), x.get("name", "")), reverse=True)
    return entries[:limit]


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_voucher_details(doctype, name, **kwargs):
    """
    Fetches full document details for editing or viewing in the voucher UI.
    """
    doctype = doctype or frappe.form_dict.get("doctype")
    name = name or frappe.form_dict.get("name")
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("Voucher {0} ({1}) not found").format(name, doctype))
    
    doc = frappe.get_doc(doctype, name)
    return doc.as_dict()


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_masters_summary(**kwargs):
    """
    Returns count of real Sugar Module masters
    """
    return {
        "suppliers_count": frappe.db.count("Supplier"),
        "customers_count": frappe.db.count("Customer"),
        "brokers_count": frappe.db.count("Broker"),
        "items_count": frappe.db.count("Item"),
        "sugar_purchases_count": frappe.db.count("Sugar Purchase"),
        "dispatches_count": frappe.db.count("Dispatch Entry"),
    }
