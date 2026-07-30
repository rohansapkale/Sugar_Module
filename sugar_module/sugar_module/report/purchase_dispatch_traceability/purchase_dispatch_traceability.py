# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe


def execute(filters=None):

    columns = get_columns()

    data = get_data(filters)

    return columns, data


def get_columns():

    return [

        {
            "label": "Sugar Purchase",
            "fieldname": "sugar_purchase",
            "fieldtype": "Link",
            "options": "Sugar Purchase",
            "width": 180
        },

        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 180
        },

        {
            "label": "Purchase Qty",
            "fieldname": "purchase_qty_quintal",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Dispatch Entry",
            "fieldname": "dispatch_entry",
            "fieldtype": "Link",
            "options": "Dispatch Entry",
            "width": 170
        },

        {
            "label": "Dispatch Date",
            "fieldname": "dispatch_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Broker",
            "fieldname": "broker",
            "fieldtype": "Link",
            "options": "Broker",
            "width": 150
        },

        {
            "label": "Customer",
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 180
        },

        {
            "label": "Vehicle",
            "fieldname": "vehicle_no",
            "fieldtype": "Data",
            "width": 120
        },

        {
            "label": "Dispatch Qty",
            "fieldname": "dispatch_qty_quintal",
            "fieldtype": "Float",
            "width": 120
        },

        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120
        },

        {
            "label": "Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Received Amount",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 140
        },

        {
            "label": "Balance Amount",
            "fieldname": "balance_amount",
            "fieldtype": "Currency",
            "width": 140
        },

        {
            "label": "Payment Status",
            "fieldname": "payment_status",
            "fieldtype": "Data",
            "width": 140
        }

    ]


def get_data(filters):

    conditions = ""

    if filters.get("from_date"):
        conditions += f" AND d.dispatch_date >= '{filters.get('from_date')}'"

    if filters.get("to_date"):
        conditions += f" AND d.dispatch_date <= '{filters.get('to_date')}'"

    if filters.get("supplier"):
        conditions += f" AND s.supplier = '{filters.get('supplier')}'"

    if filters.get("broker"):
        conditions += f" AND d.broker = '{filters.get('broker')}'"

    if filters.get("payment_status"):
        conditions += f" AND d.payment_status = '{filters.get('payment_status')}'"

    return frappe.db.sql(f"""

        SELECT

            d.sugar_purchase,
            s.supplier,
            s.purchase_qty_quintal,

            d.name AS dispatch_entry,
            d.dispatch_date,
            b.broker_name AS broker,
            d.customer_name,
            d.vehicle_no,
            d.dispatch_qty_quintal,
            d.rate,
            d.paid_amount,
            d.balance_amount,
            d.total_amount,
            d.payment_status

        FROM `tabDispatch Entry` d

        LEFT JOIN `tabSugar Purchase` s
            ON d.sugar_purchase = s.name

        LEFT JOIN `tabBroker` b
            ON d.broker = b.name

        WHERE d.docstatus = 1

        {conditions}

        ORDER BY d.dispatch_date DESC

    """, as_dict=True)
