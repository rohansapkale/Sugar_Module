# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2026, Rohan Sapkale and contributors

import frappe
from frappe.model.document import Document


class DispatchEntry(Document):

    def validate(self):
        self.calculate_values()
        self.validate_quantity()

    def on_submit(self):
        self.update_allocation()

    def on_cancel(self):
        self.reverse_allocation()

    def calculate_values(self):

        qty = self.dispatch_qty_quintal or 0

        self.dispatch_qty_kg = qty * 100

        self.total_amount = qty * (self.rate or 0)

    def validate_quantity(self):

        allocation = frappe.get_doc("Broker Allocation", self.allocation)

        pending = allocation.pending_qty_kg or 0

        if self.dispatch_qty_kg > pending:
            frappe.throw(
                f"Only {pending} Kg is pending in this allocation."
            )

    def update_allocation(self):

        allocation = frappe.get_doc("Broker Allocation", self.allocation)

        sold = (allocation.sold_qty_kg or 0) + self.dispatch_qty_kg

        allocation.sold_qty_kg = sold
        allocation.pending_qty_kg = allocation.allocated_qty_kg - sold

        if allocation.pending_qty_kg == 0:
            allocation.status = "Completed"
        else:
            allocation.status = "Open"

        allocation.save(ignore_permissions=True)

    def reverse_allocation(self):

        allocation = frappe.get_doc("Broker Allocation", self.allocation)

        sold = (allocation.sold_qty_kg or 0) - self.dispatch_qty_kg

        allocation.sold_qty_kg = sold
        allocation.pending_qty_kg = allocation.allocated_qty_kg - sold

        if allocation.sold_qty_kg == 0:
            allocation.status = "Open"
        else:
            allocation.status = "Partially Delivered"

        allocation.save(ignore_permissions=True)
