# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():

    return [
        {
            "label": _("Broker"),
            "fieldname": "broker",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Allocated (Qtl)"),
            "fieldname": "allocated_qty_quintal",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Sold (Qtl)"),
            "fieldname": "sold_qty_quintal",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Pending (Qtl)"),
            "fieldname": "pending_qty_quintal",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label":_("Supplier"),
            "fieldname":"supplier",
            "fieldtype":"Link",
            "options":"Supplier",
            "width":180,
        },
	{
	    "label":_("Comment"),
	    "fieldname":"comment",
	    "fieldtype":"Data",
	    "width":250,
	},

    ]


def get_data(filters):

    filter_dict = {"docstatus": 1}

    # Broker Filter
    if filters.get("broker"):
        filter_dict["broker"] = filters.get("broker")

    # From Date Filter
    if filters.get("from_date"):
        filter_dict["allocation_date"] = [">=", filters.get("from_date")]

    # To Date Filter
    if filters.get("to_date"):
        if "allocation_date" in filter_dict:
            filter_dict["allocation_date"] = [
                "between",
                [filters.get("from_date"), filters.get("to_date")],
            ]
        else:
            filter_dict["allocation_date"] = [
                "<=",
                filters.get("to_date"),
            ]
    allocations = frappe.get_all(
        "Broker Quantity",
        fields=[
            "broker",
            "allocated_qty_quintal",
            "sold_qty_kg",
            "pending_qty_kg",
            "status",
            "sugar_purchase",
	    "comment",
        ],
        order_by="creation desc",
    )

    data = []

    for row in allocations:

        supplier = ""
        purchase_qty = 0
        purchase_rate = 0
        gst_rate = 5
        final_rate = 0
        total_amount = 0

        broker_name = frappe.db.get_value(
            "Broker",
            row.broker,
            "broker_name"
        )




        if row.sugar_purchase:

            purchase = frappe.get_doc("Sugar Purchase", row.sugar_purchase)

            supplier = purchase.supplier
            purchase_qty = purchase.purchase_qty_quintal or 0
            purchase_rate = purchase.purchase_rate or 0

            final_rate = purchase_rate + ((purchase_rate * gst_rate) / 100)

            total_amount = purchase_qty * final_rate

        data.append(
            {
                "broker": broker_name,
                "allocated_qty_quintal": row.allocated_qty_quintal,
                "sold_qty_quintal": (row.sold_qty_kg or 0) / 100,
                "pending_qty_quintal": (row.pending_qty_kg or 0) / 100,
                "status": row.status,
                "supplier": supplier,
                "purchase_rate": purchase_rate,
                "gst": gst_rate,
                "final_rate": final_rate,
                "total_amount": total_amount,
		"comment":row.comment,
            }
        )

    return data
