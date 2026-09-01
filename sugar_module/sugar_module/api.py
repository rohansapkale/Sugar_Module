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
            fields = ["name", "customer_name", "broker", "vehicle_no", "total_amount", "paid_amount", "balance_amount", "rate", "dispatch_qty_quintal", "item", "dispatch_date"]
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
                display_name = f"{d.name} — {d.customer_name} ({d.broker or 'Direct'})"
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

@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def universal_global_search(query=None, limit=25, **kwargs):
    """
    Universal High-Speed Global Search across literally EVERYTHING:
    1. Screens, Views & Reports
    2. Specific Transactions / Vouchers by ID, Reference, UTR, Vehicle No, Party, Rate, or Amount
    3. Master Entities by Name, Mobile, City, or Grade
    """
    q = (query or frappe.form_dict.get("query") or "").strip()
    if not q:
        return []

    limit = int(limit or 25)
    results = []
    q_lower = q.lower()

    # -------------------------------------------------------------
    # 1. SCREENS, REGISTERS & REPORTS
    # -------------------------------------------------------------
    SYSTEM_SCREENS = [
        {"title": "Gateway of Sugar", "route": "/", "category": "Navigation", "tags": "gateway home dashboard start", "icon": "🌾"},
        {"title": "Sugar Purchase Voucher (P)", "route": "/voucher/purchase", "category": "Voucher Entry", "tags": "purchase sauda inward buy lot f9 p", "icon": "🛒"},
        {"title": "Dispatch Entry Voucher (D)", "route": "/voucher/dispatch", "category": "Voucher Entry", "tags": "dispatch sales delivery out f8 d", "icon": "🚚"},
        {"title": "Purchase Payment Voucher (Y)", "route": "/voucher/payment", "category": "Voucher Entry", "tags": "payment supplier mill disbursement rtgs f5 y", "icon": "💸"},
        {"title": "Broker Party Payment (Receipt) (R)", "route": "/voucher/receipt", "category": "Voucher Entry", "tags": "receipt collection customer broker payment f6 r", "icon": "🧾"},
        {"title": "Contra / Bank Transfer Voucher (T)", "route": "/voucher/contra", "category": "Voucher Entry", "tags": "contra transfer bank cash f4 t", "icon": "🔄"},
        {"title": "Sugar Purchases Register (Lots)", "route": "/register/purchase", "category": "Register / Report", "tags": "purchase register list lots purchases", "icon": "📋"},
        {"title": "Dispatch Entries Register (Sales)", "route": "/register/dispatch", "category": "Register / Report", "tags": "dispatch register list sales deliveries", "icon": "📋"},
        {"title": "Broker Receivables Outstanding Report", "route": "/register/broker-outstanding", "category": "Audit & Financial", "tags": "broker receivables due outstanding pending o", "icon": "⚠️"},
        {"title": "Supplier Payables Outstanding Report", "route": "/register/supplier-outstanding", "category": "Audit & Financial", "tags": "supplier payables mills dues owed s", "icon": "🏭"},
        {"title": "Day Book & Audit Register", "route": "/daybook", "category": "Audit & Financial", "tags": "day book audit transactions daily f10 b", "icon": "📖"},
        {"title": "Sugar Mills / Suppliers Directory", "route": "/register/supplier", "category": "Masters", "tags": "suppliers mills directory list u s", "icon": "🏭"},
        {"title": "Sugar Brokers Directory", "route": "/register/broker", "category": "Masters", "tags": "brokers directory list b", "icon": "🤝"},
        {"title": "Customer Parties Directory", "route": "/register/customer", "category": "Masters", "tags": "customers parties buyers directory c", "icon": "👥"},
        {"title": "Masters Directory (All Entities)", "route": "/masters", "category": "Masters", "tags": "masters items grades accounts directory m", "icon": "📁"},
        {"title": "getMyErp (ERPNext Desk)", "externalUrl": "/desk/rajendra-narahari-lokhande", "category": "System", "tags": "getmyerp erpnext admin desk desk", "icon": "⚡"},
    ]

    for scr in SYSTEM_SCREENS:
        if q_lower in scr["title"].lower() or q_lower in scr["tags"].lower():
            results.append({
                "id": scr["title"],
                "title": scr["title"],
                "subtitle": f"Open {scr['category']} View",
                "category": scr["category"],
                "icon": scr.get("icon", "📄"),
                "route": scr.get("route"),
                "externalUrl": scr.get("externalUrl"),
            })

    # -------------------------------------------------------------
    # 2. SPECIFIC TRANSACTIONS / VOUCHERS (BY ID, REF, VEHICLE, PARTY)
    # -------------------------------------------------------------
    # A. Sugar Purchases
    purchases = frappe.get_all(
        "Sugar Purchase",
        or_filters={
            "name": ["like", f"%{q}%"],
            "supplier": ["like", f"%{q}%"],
            "item": ["like", f"%{q}%"],
        },
        fields=["name", "supplier", "item", "purchase_qty_quintal", "purchase_rate", "total_amount", "available_qty_quintal", "purchase_date"],
        limit=8,
        order_by="creation desc",
        ignore_permissions=True
    )
    for p in purchases:
        results.append({
            "id": p.name,
            "title": f"{p.name} — {p.supplier}",
            "subtitle": f"Purchase: {flt(p.purchase_qty_quintal):,.0f} Qtl {p.item} @ ₹{flt(p.purchase_rate):,.0f} (Total ₹{flt(p.total_amount):,.2f}) · Stock: {flt(p.available_qty_quintal):,.0f} Qtl · Date: {p.purchase_date or ''}",
            "category": "Sugar Purchase Voucher",
            "icon": "🛒",
            "doctype": "Sugar Purchase",
            "voucherId": p.name,
            "route": f"/voucher/purchase?id={p.name}",
        })

    # B. Dispatch Entries
    dispatches = frappe.get_all(
        "Dispatch Entry",
        or_filters={
            "name": ["like", f"%{q}%"],
            "customer_name": ["like", f"%{q}%"],
            "broker": ["like", f"%{q}%"],
            "vehicle_no": ["like", f"%{q}%"],
            "sugar_purchase": ["like", f"%{q}%"],
            "item": ["like", f"%{q}%"],
        },
        fields=["name", "customer_name", "broker", "vehicle_no", "dispatch_qty_quintal", "rate", "total_amount", "balance_amount", "dispatch_date"],
        limit=8,
        order_by="creation desc",
        ignore_permissions=True
    )
    for d in dispatches:
        results.append({
            "id": d.name,
            "title": f"{d.name} — {d.customer_name}",
            "subtitle": f"Dispatch: {flt(d.dispatch_qty_quintal):,.0f} Qtl @ ₹{flt(d.rate):,.0f} · Veh: {d.vehicle_no or '—'} · Broker: {d.broker or 'Direct'} · Bal: ₹{flt(d.balance_amount):,.2f}",
            "category": "Dispatch Entry Voucher",
            "icon": "🚚",
            "doctype": "Dispatch Entry",
            "voucherId": d.name,
            "route": f"/voucher/dispatch?id={d.name}",
        })

    # C. Purchase Payments (Suppliers)
    payments = frappe.get_all(
        "Purchase Payment",
        or_filters={
            "name": ["like", f"%{q}%"],
            "supplier": ["like", f"%{q}%"],
            "sugar_purchase": ["like", f"%{q}%"],
            "reference_no": ["like", f"%{q}%"],
            "utr_no": ["like", f"%{q}%"],
            "payment_mode": ["like", f"%{q}%"],
        },
        fields=["name", "supplier", "sugar_purchase", "paid_amount", "payment_mode", "reference_no", "utr_no", "payment_date"],
        limit=6,
        order_by="creation desc",
        ignore_permissions=True
    )
    for py in payments:
        ref = py.utr_no or py.reference_no or "—"
        results.append({
            "id": py.name,
            "title": f"{py.name} — {py.supplier}",
            "subtitle": f"Payment: ₹{flt(py.paid_amount):,.2f} ({py.payment_mode or 'RTGS'}) · UTR/Ref: {ref} · Lot: {py.sugar_purchase or '—'}",
            "category": "Purchase Payment Voucher",
            "icon": "💸",
            "doctype": "Purchase Payment",
            "voucherId": py.name,
            "route": f"/voucher/payment?id={py.name}",
        })

    # D. Broker Party Payments (Receipts)
    receipts = frappe.get_all(
        "Broker Party Payment",
        or_filters={
            "name": ["like", f"%{q}%"],
            "customer": ["like", f"%{q}%"],
            "broker": ["like", f"%{q}%"],
            "dispatch_entry": ["like", f"%{q}%"],
            "utr_no": ["like", f"%{q}%"],
            "payment_mode": ["like", f"%{q}%"],
            "remarks": ["like", f"%{q}%"],
        },
        fields=["name", "customer", "broker", "dispatch_entry", "paid_amount", "payment_mode", "utr_no", "payment_date"],
        limit=6,
        order_by="creation desc",
        ignore_permissions=True
    )
    for rc in receipts:
        results.append({
            "id": rc.name,
            "title": f"{rc.name} — {rc.customer or rc.broker}",
            "subtitle": f"Receipt: ₹{flt(rc.paid_amount):,.2f} ({rc.payment_mode or 'Bank'}) · UTR: {rc.utr_no or '—'} · Dispatch: {rc.dispatch_entry or '—'}",
            "category": "Broker Receipt Voucher",
            "icon": "🧾",
            "doctype": "Broker Party Payment",
            "voucherId": rc.name,
            "route": f"/voucher/receipt?id={rc.name}",
        })

    # -------------------------------------------------------------
    # 3. MASTERS ENTITIES (SUPPLIERS, BROKERS, CUSTOMERS, ITEMS, ACCOUNTS)
    # -------------------------------------------------------------
    # Suppliers
    suppliers = frappe.get_all(
        "Supplier",
        or_filters={"name": ["like", f"%{q}%"], "supplier_name": ["like", f"%{q}%"]},
        fields=["name", "supplier_name"],
        limit=5,
        ignore_permissions=True
    )
    for s in suppliers:
        s_name = s.supplier_name or s.name
        results.append({
            "id": s.name,
            "title": s_name,
            "subtitle": f"Sugar Mill / Supplier Entity [{s.name}]",
            "category": "Supplier / Mill",
            "icon": "🏭",
            "doctype": "Supplier",
            "route": f"/register/supplier?search={s_name}",
        })

    # Brokers
    brokers = frappe.get_all(
        "Broker",
        or_filters={"name": ["like", f"%{q}%"], "broker_name": ["like", f"%{q}%"], "mobile_no": ["like", f"%{q}%"], "city": ["like", f"%{q}%"]},
        fields=["name", "broker_name", "mobile_no", "city"],
        limit=5,
        ignore_permissions=True
    )
    for b in brokers:
        b_name = b.broker_name or b.name
        sub = f"Broker · City: {b.city or '—'}" + (f" · Mobile: {b.mobile_no}" if b.mobile_no else "")
        results.append({
            "id": b.name,
            "title": b_name,
            "subtitle": sub,
            "category": "Broker",
            "icon": "🤝",
            "doctype": "Broker",
            "route": f"/register/broker?search={b_name}",
        })

    # Customers
    customers = frappe.get_all(
        "Customer",
        or_filters={"name": ["like", f"%{q}%"], "customer_name": ["like", f"%{q}%"]},
        fields=["name", "customer_name"],
        limit=5,
        ignore_permissions=True
    )
    for c in customers:
        c_name = c.customer_name or c.name
        results.append({
            "id": c.name,
            "title": c_name,
            "subtitle": f"Customer Party Entity [{c.name}]",
            "category": "Customer Party",
            "icon": "👥",
            "doctype": "Customer",
            "route": f"/register/customer?search={c_name}",
        })

    # Items
    items = frappe.get_all(
        "Item",
        or_filters={"name": ["like", f"%{q}%"], "item_name": ["like", f"%{q}%"]},
        fields=["name", "item_name", "stock_uom"],
        limit=4,
        ignore_permissions=True
    )
    for itm in items:
        results.append({
            "id": itm.name,
            "title": itm.item_name or itm.name,
            "subtitle": f"Sugar Item / Grade (UOM: {itm.stock_uom or 'Qtl'})",
            "category": "Sugar Item",
            "icon": "🏷️",
            "doctype": "Item",
            "route": "/masters",
        })

    # Accounts
    accounts = frappe.get_all(
        "Account",
        filters={"is_group": 0},
        or_filters={"name": ["like", f"%{q}%"], "account_name": ["like", f"%{q}%"]},
        fields=["name", "account_name", "account_type"],
        limit=4,
        ignore_permissions=True
    )
    for acc in accounts:
        results.append({
            "id": acc.name,
            "title": acc.account_name or acc.name,
            "subtitle": f"Account · {acc.account_type or 'Ledger'}",
            "category": "Bank / Cash Account",
            "icon": "🏦",
            "doctype": "Account",
            "route": "/masters",
        })

    return results[:limit]



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


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def save_sugar_voucher(voucher_type=None, payload=None, submit=0):
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
        doc.purchase_date = payload.get("purchase_date") or payload.get("date") or nowdate()
        doc.item = item
        doc.purchase_qty_quintal = flt(payload.get("purchase_qty_quintal") or payload.get("qty") or 100)
        doc.purchase_rate = flt(payload.get("purchase_rate") or payload.get("rate") or 4000)
        doc.total_amount = doc.purchase_qty_quintal * doc.purchase_rate
        doc.status = "Draft"
        doc.insert(ignore_permissions=True)
        if submit:
            try:
                doc.submit()
            except Exception:
                pass
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
            latest_sp = frappe.get_all("Sugar Purchase", filters={"docstatus": ["!=", 2]}, order_by="creation desc", limit=1, ignore_permissions=True)
            if latest_sp:
                sugar_purchase = latest_sp[0].name
            else:
                frappe.throw(_("Please select a valid Source Sugar Purchase lot."))

        broker = resolve_link("Broker", payload.get("broker"), "broker_name") or payload.get("broker")
        customer_name = resolve_link("Customer", payload.get("customer_name") or payload.get("customer"), "customer_name") or payload.get("customer_name") or payload.get("customer")
        item = resolve_link("Item", payload.get("item"), "item_name") or "S-302526"

        doc = frappe.new_doc("Dispatch Entry")
        doc.sugar_purchase = sugar_purchase
        doc.company = payload.get("company") or frappe.defaults.get_user_default("company") or "Rajendra Narahari Lokhande"
        doc.broker = broker
        doc.customer_name = customer_name
        doc.vehicle_no = payload.get("vehicle_no") or "MH-N/A"
        doc.dispatch_date = payload.get("dispatch_date") or payload.get("date") or nowdate()
        doc.item = item
        doc.dispatch_qty_quintal = flt(payload.get("dispatch_qty_quintal") or payload.get("qty") or 10)
        doc.rate = flt(payload.get("rate") or 4000)
        doc.total_amount = doc.dispatch_qty_quintal * doc.rate
        doc.balance_amount = doc.total_amount - flt(payload.get("paid_amount", 0))
        doc.paid_amount = flt(payload.get("paid_amount", 0))
        doc.payment_status = "Paid" if doc.balance_amount <= 0 else ("Partially Paid" if doc.paid_amount > 0 else "Unpaid")
        doc.status = "Draft"
        doc.insert(ignore_permissions=True)
        if submit:
            try:
                doc.submit()
            except Exception as e:
                return {
                    "success": True,
                    "doctype": "Dispatch Entry",
                    "name": doc.name,
                    "docstatus": 0,
                    "total_amount": doc.total_amount,
                    "message": _("Dispatch Entry {0} saved as Draft (Note: {1})").format(doc.name, str(e)),
                }
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
        doc.payment_date = payload.get("payment_date") or payload.get("date") or nowdate()
        doc.payment_mode = payload.get("payment_mode") or "NEFT"
        doc.reference_no = payload.get("reference_no")
        doc.utr_no = payload.get("utr_no")
        doc.total_amount = flt(payload.get("total_amount") or payload.get("paid_amount"))
        doc.paid_amount = flt(payload.get("paid_amount"))
        doc.remaining_amount = max(0, doc.total_amount - doc.paid_amount)
        doc.payment_status = "Paid" if doc.remaining_amount <= 0 else ("Partially Paid" if doc.paid_amount > 0 else "Unpaid")
        doc.insert(ignore_permissions=True)
        if submit:
            try:
                doc.submit()
            except Exception:
                pass
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
        customer = resolve_link("Customer", payload.get("customer") or payload.get("customer_name"), "customer_name") or payload.get("customer")
        dispatch_entry = resolve_link("Dispatch Entry", payload.get("dispatch_entry"))

        doc = frappe.new_doc("Broker Party Payment")
        doc.dispatch_entry = dispatch_entry
        doc.broker = broker
        doc.customer = customer
        doc.payment_date = payload.get("payment_date") or payload.get("date") or nowdate()
        doc.payment_mode = payload.get("payment_mode") or "NEFT"
        doc.utr_no = payload.get("utr_no")
        doc.paid_amount = flt(payload.get("paid_amount"))
        doc.remarks = payload.get("remarks")
        doc.insert(ignore_permissions=True)
        if submit:
            try:
                doc.submit()
            except Exception:
                pass
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

    elif voucher_type in ("broker-outstanding", "receivables", "broker_receivables"):
        # Fetch all dispatch entries
        dispatches = frappe.get_all(
            "Dispatch Entry",
            filters={"docstatus": ["!=", 2]},
            fields=[
                "name", "dispatch_date", "customer_name", "broker", "vehicle_no",
                "item", "dispatch_qty_quintal", "rate", "total_amount", "paid_amount",
                "balance_amount", "payment_status", "status", "sugar_purchase"
            ],
            limit=limit * 2,
            order_by="creation desc",
            ignore_permissions=True
        )

        broker_map = {}
        for d in dispatches:
            b_key = d.broker or "Direct / No Broker"
            if b_key not in broker_map:
                broker_name = frappe.db.get_value("Broker", b_key, "broker_name") or b_key
                broker_mobile = frappe.db.get_value("Broker", b_key, "mobile_no") or ""
                broker_map[b_key] = {
                    "broker_id": b_key,
                    "broker_name": broker_name,
                    "broker_mobile": broker_mobile,
                    "total_dispatches": 0,
                    "total_qty": 0.0,
                    "total_billed": 0.0,
                    "total_received": 0.0,
                    "total_pending": 0.0,
                    "pending_vouchers": [],
                }
            bm = broker_map[b_key]
            bm["total_dispatches"] += 1
            bm["total_qty"] += flt(d.dispatch_qty_quintal)
            bm["total_billed"] += flt(d.total_amount)
            bm["total_received"] += flt(d.paid_amount)
            bm["total_pending"] += flt(d.balance_amount)
            
            d["broker_name"] = bm["broker_name"]
            if flt(d.balance_amount) > 0 or d.payment_status != "Paid":
                bm["pending_vouchers"].append(d)

        broker_list = sorted(list(broker_map.values()), key=lambda x: x["total_pending"], reverse=True)
        if query:
            broker_list = [b for b in broker_list if query.lower() in b["broker_name"].lower() or query.lower() in b["broker_id"].lower()]

        total_outstanding = sum(b["total_pending"] for b in broker_list)
        total_billed = sum(b["total_billed"] for b in broker_list)
        total_received = sum(b["total_received"] for b in broker_list)

        return {
            "voucher_type": "broker-outstanding",
            "title": "Broker / Customer Outstanding Receivables Report",
            "records": dispatches,
            "groups": broker_list,
            "summary": {
                "total_outstanding": total_outstanding,
                "total_billed": total_billed,
                "total_received": total_received,
                "total_brokers": len(broker_list),
                "total_pending_vouchers": sum(len(b["pending_vouchers"]) for b in broker_list),
            }
        }

    elif voucher_type in ("supplier-outstanding", "payables", "supplier_payables"):
        # Fetch all sugar purchases
        purchases = frappe.get_all(
            "Sugar Purchase",
            filters={"docstatus": ["!=", 2]},
            fields=[
                "name", "purchase_date", "supplier", "item", "purchase_qty_quintal",
                "purchase_rate", "total_amount", "paid_amount", "remaining_amount",
                "payment_status", "dispatched_qty_quintal", "available_qty_quintal",
                "status", "docstatus"
            ],
            limit=limit * 2,
            order_by="creation desc",
            ignore_permissions=True
        )

        supplier_map = {}
        for p in purchases:
            s_key = p.supplier or "Unknown Mill"
            if s_key not in supplier_map:
                supplier_name = frappe.db.get_value("Supplier", s_key, "supplier_name") or s_key
                supplier_map[s_key] = {
                    "supplier_id": s_key,
                    "supplier_name": supplier_name,
                    "total_purchases": 0,
                    "total_qty": 0.0,
                    "total_billed": 0.0,
                    "total_paid": 0.0,
                    "total_pending": 0.0,
                    "pending_vouchers": [],
                }
            sm = supplier_map[s_key]
            sm["total_purchases"] += 1
            sm["total_qty"] += flt(p.purchase_qty_quintal)
            sm["total_billed"] += flt(p.total_amount)
            sm["total_paid"] += flt(p.paid_amount)
            rem = flt(p.remaining_amount) if p.remaining_amount is not None and flt(p.remaining_amount) > 0 else (flt(p.total_amount) - flt(p.paid_amount))
            sm["total_pending"] += rem
            
            p["remaining_amount"] = rem
            if rem > 0 or p.payment_status != "Paid":
                sm["pending_vouchers"].append(p)

        supplier_list = sorted(list(supplier_map.values()), key=lambda x: x["total_pending"], reverse=True)
        if query:
            supplier_list = [s for s in supplier_list if query.lower() in s["supplier_name"].lower() or query.lower() in s["supplier_id"].lower()]

        total_outstanding = sum(s["total_pending"] for s in supplier_list)
        total_billed = sum(s["total_billed"] for s in supplier_list)
        total_paid = sum(s["total_paid"] for s in supplier_list)

        return {
            "voucher_type": "supplier-outstanding",
            "title": "Supplier / Mill Outstanding Payables Report",
            "records": purchases,
            "groups": supplier_list,
            "summary": {
                "total_outstanding": total_outstanding,
                "total_billed": total_billed,
                "total_paid": total_paid,
                "total_suppliers": len(supplier_list),
                "total_pending_vouchers": sum(len(s["pending_vouchers"]) for s in supplier_list),
            }
        }

    elif voucher_type in ("Supplier", "supplier"):
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["supplier_name"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Supplier",
            or_filters=or_filters if query else None,
            fields=["name", "supplier_name", "supplier_group", "supplier_type", "country"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )

        for s in records:
            # Count purchases for this supplier
            purchases = frappe.get_all(
                "Sugar Purchase",
                filters={"supplier": s.name, "docstatus": ["!=", 2]},
                fields=["purchase_qty_quintal", "total_amount", "available_qty_quintal"],
                ignore_permissions=True
            )
            s["total_lots"] = len(purchases)
            s["total_purchase_qty"] = sum(flt(p.purchase_qty_quintal) for p in purchases)
            s["total_qty"] = s["total_purchase_qty"]
            s["total_purchase_amount"] = sum(flt(p.total_amount) for p in purchases)
            s["total_amount"] = s["total_purchase_amount"]
            s["available_stock"] = sum(flt(p.available_qty_quintal) for p in purchases)

        return {
            "voucher_type": "Supplier",
            "title": "Sugar Mills / Suppliers Directory",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_qty": sum(flt(r.get("total_qty", 0)) for r in records),
                "total_purchase_qty": sum(flt(r.get("total_purchase_qty", 0)) for r in records),
                "total_amount": sum(flt(r.get("total_amount", 0)) for r in records),
                "total_purchase_amount": sum(flt(r.get("total_purchase_amount", 0)) for r in records),
                "total_available_qty": sum(flt(r.get("available_stock", 0)) for r in records),
            }
        }

    elif voucher_type in ("Broker", "broker"):
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["broker_name"] = ["like", f"%{query}%"]
            or_filters["city"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Broker",
            or_filters=or_filters if query else None,
            fields=["name", "broker_name", "mobile_no", "city", "state"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )

        for b in records:
            # Count dispatches for this broker
            dispatches = frappe.get_all(
                "Dispatch Entry",
                filters={"broker": b.name, "docstatus": ["!=", 2]},
                fields=["dispatch_qty_quintal", "total_amount", "balance_amount"],
                ignore_permissions=True
            )
            b["total_dispatches"] = len(dispatches)
            b["total_sold_qty"] = sum(flt(d.dispatch_qty_quintal) for d in dispatches)
            b["total_qty"] = b["total_sold_qty"]
            b["total_sold_amount"] = sum(flt(d.total_amount) for d in dispatches)
            b["total_amount"] = b["total_sold_amount"]
            b["total_balance"] = sum(flt(d.balance_amount) for d in dispatches)

        return {
            "voucher_type": "Broker",
            "title": "Sugar Brokers Directory",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_qty": sum(flt(r.get("total_qty", 0)) for r in records),
                "total_sold_qty": sum(flt(r.get("total_sold_qty", 0)) for r in records),
                "total_amount": sum(flt(r.get("total_amount", 0)) for r in records),
                "total_sold_amount": sum(flt(r.get("total_sold_amount", 0)) for r in records),
                "total_balance": sum(flt(r.get("total_balance", 0)) for r in records),
            }
        }

    elif voucher_type in ("Customer", "customer"):
        or_filters = {}
        if query:
            or_filters["name"] = ["like", f"%{query}%"]
            or_filters["customer_name"] = ["like", f"%{query}%"]

        records = frappe.get_all(
            "Customer",
            or_filters=or_filters if query else None,
            fields=["name", "customer_name", "customer_group", "territory", "customer_type"],
            limit=limit,
            order_by="creation desc",
            ignore_permissions=True
        )

        for c in records:
            dispatches = frappe.get_all(
                "Dispatch Entry",
                filters={"customer_name": c.name, "docstatus": ["!=", 2]},
                fields=["dispatch_qty_quintal", "total_amount", "balance_amount"],
                ignore_permissions=True
            )
            c["total_dispatches"] = len(dispatches)
            c["total_sold_qty"] = sum(flt(d.dispatch_qty_quintal) for d in dispatches)
            c["total_qty"] = c["total_sold_qty"]
            c["total_amount"] = sum(flt(d.total_amount) for d in dispatches)
            c["total_balance"] = sum(flt(d.balance_amount) for d in dispatches)

        return {
            "voucher_type": "Customer",
            "title": "Customer Parties Register",
            "records": records,
            "summary": {
                "total_count": len(records),
                "total_qty": sum(flt(r.get("total_qty", 0)) for r in records),
                "total_sold_qty": sum(flt(r.get("total_sold_qty", 0)) for r in records),
                "total_amount": sum(flt(r.get("total_amount", 0)) for r in records),
                "total_balance": sum(flt(r.get("total_balance", 0)) for r in records),
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


@frappe.whitelist(methods=["GET", "POST"], allow_guest=True)
def get_gateway_metrics(period="Today", **kwargs):
    """
    Returns 100% live real database metrics from Frappe sugar_module:
    - Sugar Purchase (Purchases, Stock, Payables)
    - Dispatch Entry (Sales, Dispatches, Receivables)
    - Purchase Payment (Disbursements Made)
    - Broker Party Payment (Collections Received)
    """
    period = period or "Today"
    today = str(nowdate())

    # 1. Real Purchases Data
    purchases = frappe.get_all(
        "Sugar Purchase",
        fields=["purchase_qty_quintal", "total_amount", "available_qty_quintal", "purchase_date"],
        ignore_permissions=True
    )
    total_purchase_qty = sum(flt(p.get("purchase_qty_quintal")) for p in purchases)
    total_purchase_val = sum(flt(p.get("total_amount")) for p in purchases)
    closing_stock_qty = sum(flt(p.get("available_qty_quintal")) for p in purchases)

    today_purchases = [p for p in purchases if str(p.get("purchase_date") or "") == today]
    today_purchase_qty = sum(flt(p.get("purchase_qty_quintal")) for p in today_purchases)

    # 2. Real Sales / Dispatches Data
    dispatches = frappe.get_all(
        "Dispatch Entry",
        fields=["dispatch_qty_quintal", "total_amount", "paid_amount", "balance_amount", "dispatch_date"],
        ignore_permissions=True
    )
    total_sales_qty = sum(flt(d.get("dispatch_qty_quintal")) for d in dispatches)
    total_sales_val = sum(flt(d.get("total_amount")) for d in dispatches)
    total_receivable = sum(flt(d.get("balance_amount")) for d in dispatches)

    today_dispatches = [d for d in dispatches if str(d.get("dispatch_date") or "") == today]
    today_sales_qty = sum(flt(d.get("dispatch_qty_quintal")) for d in today_dispatches)

    # 3. Real Payments Made (Disbursements to Sugar Mills)
    payments = frappe.get_all(
        "Purchase Payment",
        fields=["paid_amount", "payment_date"],
        ignore_permissions=True
    )
    total_payments_made = sum(flt(p.get("paid_amount")) for p in payments)

    # 4. Real Payments Received (Collections from Buyers / Brokers)
    receipts = frappe.get_all(
        "Broker Party Payment",
        fields=["paid_amount", "payment_date"],
        ignore_permissions=True
    )
    total_payments_received = sum(flt(r.get("paid_amount")) for r in receipts)

    # 5. Real Payables Due to Sugar Mills
    total_payable = max(0.0, total_purchase_val - total_payments_made)

    # 6. Real Opening Stock Calculation (Balance Before Current Cycle)
    opening_stock = max(0.0, (closing_stock_qty + total_sales_qty) - total_purchase_qty)

    # Period-sensitive purchase qty display
    display_purchase_qty = today_purchase_qty if period == "Today" else total_purchase_qty
    display_sales_qty = today_sales_qty if period == "Today" and today_sales_qty else total_sales_qty

    return {
        "period": period,
        "opening_stock": round(opening_stock, 2),
        "today_purchases_qty": round(display_purchase_qty, 2),
        "total_sales_qty": round(display_sales_qty, 2),
        "closing_stock": round(closing_stock_qty, 2),
        "total_purchases_val": round(total_purchase_val, 2),
        "total_sales_val": round(total_sales_val, 2),
        "payments_received": round(total_payments_received, 2),
        "payments_made": round(total_payments_made, 2),
        "total_receivable": round(total_receivable, 2),
        "total_payable": round(total_payable, 2),
    }

