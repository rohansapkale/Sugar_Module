# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe.model.document import Document

import frappe
from frappe.model.document import Document


class BrokerAllocation(Document):

    def validate(self):
        self.calculate_values()

    def on_submit(self):
        self.status = "Open"

    def on_cancel(self):
        self.status = "Cancelled"

    def calculate_values(self):

        qty = self.allocated_qty_quintal or 0
        rate = self.rate or 0

        self.allocated_qty_kg = qty * 100
        self.total_amount = self.allocated_qty_kg * rate

        sold = self.sold_qty_kg or 0

        self.pending_qty_kg = self.allocated_qty_kg - sold

        if sold == 0:
            self.status = "Open"

        elif sold < self.allocated_qty_kg:
            self.status = "Partially Sold"

        else:
            self.status = "Completed"
