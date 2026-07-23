# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
from frappe import _

import frappe
from sugar_module.utils.stock import (
    get_total_purchased,
    get_total_sold,
    get_remaining_stock,
)


def execute(filters=None):
    columns = [
        {
            "label": "Metric",
            "fieldname": "metric",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "label": "Quantity (Kg)",
            "fieldname": "value",
            "fieldtype": "Float",
            "width": 180,
        },
    ]

    data = [
        {
            "metric": "Total Purchased",
            "value": get_total_purchased(),
        },
        {
            "metric": "Total Sold",
            "value": get_total_sold(),
        },
        {
            "metric": "Remaining Stock",
            "value": get_remaining_stock(),
        },
    ]

    return columns, data
