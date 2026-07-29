# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	return columns, data


def get_columns():
    return [
        {
            "label": "Purchase Payment",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Purchase Payment",
            "width": 180
        },
        {
            "label": "Payment Date",
            "fieldname": "payment_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 220
        },
        {
            "label": "Sugar Purchase",
            "fieldname": "sugar_purchase",
            "fieldtype": "Link",
            "options": "Sugar Purchase",
            "width": 220
        },
        {
            "label": "Total Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Paid Amount",
            "fieldname": "paid_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": "Remaining Amount",
            "fieldname": "remaining_amount",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Payment Mode",
            "fieldname": "payment_mode",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": "Reference No",
            "fieldname": "reference_no",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Status",
            "fieldname": "payment_status",
            "fieldtype": "Data",
            "width": 120
        }
    ]
def get_data(filters):

    filter_dict = {
        "docstatus": 1
    }

    if filters.get("supplier"):
        filter_dict["supplier"] = filters.get("supplier")

    if filters.get("from_date"):
        filter_dict["payment_date"] = [">=", filters.get("from_date")]

    if filters.get("to_date"):
        if "payment_date" in filter_dict:
            filter_dict["payment_date"] = [
                "between",
                [
                    filters.get("from_date"),
                    filters.get("to_date")
                ]
            ]
        else:
            filter_dict["payment_date"] = [
                "<=",
                filters.get("to_date")
            ]

    return frappe.get_all(
        "Purchase Payment",
        filters=filter_dict,
        fields=[
            "name",
            "payment_date",
            "supplier",
            "sugar_purchase",
            "total_amount",
            "paid_amount",
            "remaining_amount",
            "payment_mode",
            "reference_no",
            "payment_status"
        ],
        order_by="payment_date desc"
    )


def get_filters():
    return [
        {
            "fieldname": "supplier",
            "label": "Supplier",
            "fieldtype": "Link",
            "options": "Supplier"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date"
        }
    ]
def execute(filters=None):

    columns = get_columns()

    data = get_data(filters)

    return columns, data
