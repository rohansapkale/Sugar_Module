import frappe

def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 110,
        },

        {
            "label": "Transaction",
            "fieldname": "transaction_type",
            "fieldtype": "Data",
            "width": 130,
        },

        {
            "label": "Voucher No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "width": 180,
        },

        {
            "label": "Party",
            "fieldname": "party",
            "fieldtype": "Data",
            "width": 180,
        },

        {
            "label": "Broker",
            "fieldname": "broker",
            "fieldtype": "Data",
            "width": 160,
        },

        {
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 130,
        },

        {
            "label": "Qty (Qtl)",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
        },

        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 110,
        },

        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 130,
        },

        {
            "label": "Paid",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 120,
        },

        {
            "label": "Balance",
            "fieldname": "balance_amount",
            "fieldtype": "Currency",
            "width": 120,
        },

        {
            "label": "Status",
            "fieldname": "payment_status",
            "fieldtype": "Data",
            "width": 120,
        },
    ]


def get_data(filters):

    data = []

    purchases = frappe.get_all(
        "Sugar Purchase",
        filters={"docstatus": 1},
        fields=[
            "name",
            "purchase_date",
            "supplier",
            "item",
            "purchase_qty_quintal",
            "purchase_rate",
            "total_amount"
        ],
        order_by="purchase_date asc"
    )

    for p in purchases:

        data.append({
            "date": p.purchase_date,
            "transaction_type": "Purchase",
            "reference_doctype": "Sugar Purchase",
            "voucher_no": p.name,
            "party": p.supplier,
            "broker": "",
            "item": p.item,
            "qty": p.purchase_qty_quintal,
            "rate": p.purchase_rate,
            "amount": p.total_amount,
            "paid_amount": 0,
            "balance_amount": 0,
            "payment_status": ""
        })

    dispatches = frappe.get_all(
        "Dispatch Entry",
        filters={"docstatus": 1},
        fields=[
            "name",
            "dispatch_date",
            "customer_name",
            "broker",
            "item",
            "dispatch_qty_quintal",
            "rate",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "payment_status"
        ],
        order_by="dispatch_date asc"
    )

    for d in dispatches:

        broker_name = frappe.db.get_value(
            "Broker",
            d.broker,
            "broker_name"
        ) or d.broker

        data.append({
            "date": d.dispatch_date,
            "transaction_type": "Dispatch",
            "reference_doctype": "Dispatch Entry",
            "voucher_no": d.name,
            "party": d.customer_name,
            "broker": broker_name,
            "item": d.item,
            "qty": d.dispatch_qty_quintal,
            "rate": d.rate,
            "amount": d.total_amount,
            "paid_amount": d.paid_amount,
            "balance_amount": d.balance_amount,
            "payment_status": d.payment_status
        })

    data = sorted(data, key=lambda x: x["date"])
    
    return data
