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
            "fieldtype": "Link",
            "options": "Broker",
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
    ]


def get_data(filters):

    allocations = frappe.get_all(
        "Broker Allocation",
        fields=[
            "broker",
            "allocated_qty_quintal",
            "sold_qty_kg",
            "pending_qty_kg",
            "status",
        ],
        order_by="creation desc",
    )

    data = []

    for row in allocations:

        data.append(
            {
                "broker": row.broker,
                "allocated_qty_quintal": row.allocated_qty_quintal,
                "sold_qty_quintal": (row.sold_qty_kg or 0) / 100,
                "pending_qty_quintal": (row.pending_qty_kg or 0) / 100,
                "status": row.status,
            }
        )

    return data
