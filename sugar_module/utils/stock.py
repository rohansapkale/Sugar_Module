import frappe


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
