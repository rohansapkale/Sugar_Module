# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class PurchasePayment(Document):

    def validate(self):
        self.fetch_purchase_details()
        self.calculate_remaining()

    def on_submit(self):
        self.update_purchase()

    def on_cancel(self):
        self.revert_purchase()

    def fetch_purchase_details(self):
        if not self.sugar_purchase:
            return

        purchase = frappe.get_doc("Sugar Purchase", self.sugar_purchase)

        self.supplier = purchase.supplier
        self.total_amount = purchase.total_amount

    def calculate_remaining(self):

        purchase = frappe.get_doc("Sugar Purchase", self.sugar_purchase)

        current_paid = purchase.paid_amount or 0

        self.remaining_amount = (
             self.total_amount - (current_paid + (self.paid_amount or 0))
        )

        if self.remaining_amount <= 0:
            self.payment_status = "Paid"

        elif current_paid > 0 or self.paid_amount > 0:
            self.payment_status = "Partially Paid"

        else:
            self.payment_status = "Unpaid"

    def update_purchase(self):

        purchase = frappe.get_doc("Sugar Purchase", self.sugar_purchase)

        purchase.paid_amount = (purchase.paid_amount or 0) + (self.paid_amount or 0)

        purchase.remaining_amount = purchase.total_amount - purchase.paid_amount

        if purchase.remaining_amount <= 0:
            purchase.payment_status = "Paid"

        elif purchase.paid_amount > 0:
            purchase.payment_status = "Partially Paid"

        else:
            purchase.payment_status = "Unpaid"

        purchase.save(ignore_permissions=True)

    def revert_purchase(self):

        purchase = frappe.get_doc("Sugar Purchase", self.sugar_purchase)

        purchase.paid_amount = (
            purchase.paid_amount or 0
        ) - self.paid_amount

        purchase.remaining_amount = (
            purchase.total_amount - purchase.paid_amount
        )

        if purchase.remaining_amount <= 0:
            purchase.payment_status = "Paid"

        elif purchase.paid_amount > 0:
            purchase.payment_status = "Partially Paid"

        else:
            purchase.payment_status = "Unpaid"

        purchase.save(ignore_permissions=True)
