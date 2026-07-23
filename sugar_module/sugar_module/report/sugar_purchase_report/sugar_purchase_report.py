# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe


def execute(filters = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():

	return [
		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options":"Supplier",
			"width":"180",
		},
		{
			"label": "Warehouse",
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options":"Warehouse",
			"width":"180",
		},
                {
			"label":"Purchase Qty(quintal)",
			"fieldname":"purchase_qty_quintal",
			"fieldtype":"Float",
			"width":"150",
		},
		{
			"label":"Purchase Rate",
			"fieldname":"purchase_rate",
			"fieldtype":"Float",
			"width":"150",
		},
	]


def get_data(filters=None):

	return frappe.get_all(
	    "Sugar Purchase",
            fields=[
		"supplier",
		"warehouse",
		"purchase_qty_quintal",
		"purchase_rate",
	    ],
	    order_by="creation desc",
	)
