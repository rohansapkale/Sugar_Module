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
            "label": "Broker",
            "fieldname": "broker",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": "Customer",
            "fieldname": "customer_name",
            "fieldtype": "Link",
	    "options":"customer",
            "width": 180,
        },
        {
            "label": "Vehicle No",
            "fieldname": "vehicle_no",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": "Dispatch Date",
            "fieldname": "dispatch_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": "Qty (Qtl)",
            "fieldname": "dispatch_qty_quintal",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": "Rate",
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150,
        },
	{
            "label": "Paid Amount",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Balance",
            "fieldname": "balance_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Payment Status",
            "fieldname": "payment_status",
            "fieldtype": "Data",
            "width": 150,
        },
    ]


def get_data(filters):

    filter_dict = {"docstatus": 1}

    if filters.get("broker"):
        filter_dict["broker"] = filters.get("broker")

    if filters.get("from_date"):
        filter_dict["dispatch_date"] = [">=", filters.get("from_date")]

    if filters.get("to_date"):
        if "dispatch_date" in filter_dict:
            filter_dict["dispatch_date"] = [
                "between",
                [filters.get("from_date"), filters.get("to_date")],
            ]
        else:
            filter_dict["dispatch_date"] = ["<=", filters.get("to_date")]

    dispatches = frappe.get_all(
        "Dispatch Entry",
        filters=filter_dict,
        fields=[
            "broker",
            "customer_name",
            "vehicle_no",
            "dispatch_date",
            "dispatch_qty_quintal",
            "rate",
            "total_amount",
            "paid_amount",
            "balance_amount",
            "payment_status",
        ],
        order_by="broker asc, dispatch_date asc",
    )

    # Fetch all broker names once
    broker_map = {
        d.name: d.broker_name
        for d in frappe.get_all(
            "Broker",
            fields=["name", "broker_name"]
        )
    }

    # Replace Broker ID with Broker Name
    for row in dispatches:
        row["broker"] = broker_map.get(row["broker"], row["broker"])

    return dispatches
