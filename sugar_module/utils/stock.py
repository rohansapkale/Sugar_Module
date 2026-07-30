import frappe


def refresh_dispatch_history(purchase_name):
    """
    Rebuild Dispatch History table inside Sugar Purchase
    """

    purchase = frappe.get_doc("Sugar Purchase", purchase_name)

    # Clear existing rows
    purchase.set("dispatch_history", [])

    # Get all submitted dispatch entries for this purchase
    dispatches = frappe.get_all(
        "Dispatch Entry",
        filters={
            "sugar_purchase": purchase_name,
            "docstatus": 1
        },
        fields=[
            "name",
            "dispatch_date",
            "broker",
            "vehicle_no",
            "customer_name",
            "dispatch_qty_quintal",
            "rate",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "payment_status",
            "status"
        ],
        order_by="dispatch_date asc",
        as_list=False
    )

    # Populate child table
    for d in dispatches:

        broker_name = frappe.db.get_value(
            "Broker",
            d.broker,
            "broker_name"
        )


        purchase.append("dispatch_history", {
            "dispatch_date": d.dispatch_date,
            "broker": broker_name,
            "customer": d.customer_name,
            "vehicle_no":d.vehicle_no,
            "dispatch_qty_quintal": d.dispatch_qty_quintal,
            "rate": d.rate,
            "total_amount": d.total_amount,
            "paid_amount": d.paid_amount,
            "balance_amount": d.balance_amount,
            "payment_status": d.payment_status,
            "status": d.status
        })

    purchase.flags.ignore_validate_update_after_submit = True

    purchase.save(
        ignore_permissions=True,
        ignore_version=True
    )

def get_total_purchased():
    result = frappe.db.sql("""
        SELECT IFNULL(SUM(converted_qty_kg), 0)
        FROM `tabSugar Purchase`
        WHERE docstatus = 1
    """)
    return result[0][0]


def get_total_sold():
    result = frappe.db.sql("""
        SELECT IFNULL(SUM(sale_qty_kg), 0)
        FROM `tabSugar Sale`
        WHERE docstatus = 1
    """)
    return result[0][0]


def get_remaining_stock():
    return get_total_purchased() - get_total_sold()
import frappe


def create_stock_ledger(
    posting_date,
    transaction_type,
    reference_doctype,
    reference_name,
    company,
    warehouse,
    item,
    in_qty=0,
    out_qty=0,
):
    previous_balance = frappe.db.sql(
        """
        SELECT balance_qty
        FROM `tabSugar Stock Ledger`
        ORDER BY creation DESC
        LIMIT 1
        """,
        as_dict=True,
    )

    balance = previous_balance[0].balance_qty if previous_balance else 0

    balance = balance + in_qty - out_qty

    ledger = frappe.new_doc("Sugar Stock Ledger")

    ledger.posting_date = posting_date
    ledger.transaction_type = transaction_type
    ledger.reference_doctype = reference_doctype
    ledger.reference_name = reference_name
    ledger.company = company
    ledger.warehouse = warehouse
    ledger.item = item
    ledger.in_qty = in_qty
    ledger.out_qty = out_qty
    ledger.balance_qty = balance

    ledger.insert(ignore_permissions=True)

    return ledger.name
