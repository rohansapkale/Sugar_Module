# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2026, Rohan Sapkale and contributors

# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from sugar_module.utils.stock import refresh_dispatch_history


class DispatchEntry(Document):

    def validate(self):
        self.calculate_values()
        self.validate_dispatch_quantity()

        broker_name = frappe.db.get_value(
            "Broker",
            self.broker,
            "broker_name"
        )

        self.title = (
            f"{broker_name} | "
            f"{self.dispatch_qty_quintal} Qtl | "
            f"{self.dispatch_date}"
        )

        if self.sugar_purchase:
            self.supplier = frappe.db.get_value(
                "Sugar Purchase",
                self.sugar_purchase,
                "supplier"
            )

    def on_submit(self):

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

    # Validation
        if self.dispatch_qty_quintal > purchase.available_qty_quintal:
            frappe.throw(
                f"Only {purchase.available_qty_quintal} Quintal is available."
            )

        purchase.dispatched_qty_quintal += self.dispatch_qty_quintal

        purchase.available_qty_quintal = (
            purchase.purchase_qty_quintal
            - purchase.dispatched_qty_quintal
        )

        purchase.save(ignore_permissions=True)
        refresh_dispatch_history(self.sugar_purchase)
    def on_cancel(self):

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

        purchase.dispatched_qty_quintal -= self.dispatch_qty_quintal

        purchase.available_qty_quintal = (
            purchase.purchase_qty_quintal
            - purchase.dispatched_qty_quintal
        )

        purchase.save(ignore_permissions=True)
        refresh_dispatch_history(self.sugar_purchase)
    def calculate_values(self):

        qty = self.dispatch_qty_quintal or 0
        rate = self.rate or 0

        # Convert Quintal to KG
        self.dispatch_qty_kg = qty * 100

        # GST
        gst = rate * 5 / 100
        final_rate = rate + gst

        # Total Amount
        self.total_amount = qty * final_rate


    def validate_dispatch_quantity(self):

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

        available = purchase.available_qty_quintal or 0

        if self.dispatch_qty_quintal > available:

            frappe.throw(
                f"""
                Dispatch Quantity exceeds Available Stock.

                Purchase : {purchase.name}

                Available Qty : {available} Quintal

                Dispatch Qty : {self.dispatch_qty_quintal} Quintal
               """
            )
