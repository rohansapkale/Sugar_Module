# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class BrokerPayment(Document):

    def validate(self):
        self.validate_payment()

    def on_submit(self):
        self.update_dispatch()

    def on_cancel(self):
        self.update_dispatch(cancel=True)

    def validate_payment(self):

        dispatch = frappe.get_doc("Dispatch Entry", self.dispatch_entry)

        current_paid = dispatch.paid_amount or 0
        total_bill = dispatch.total_amount or 0

        if current_paid + self.paid_amount > total_bill:
            frappe.throw("Paid Amount cannot be greater than Bill Amount.")

    def update_dispatch(self, cancel=False):

        dispatch = frappe.get_doc("Dispatch Entry", self.dispatch_entry)

        paid = dispatch.paid_amount or 0

        if cancel:
            paid -= self.paid_amount
        else:
            paid += self.paid_amount

        balance = dispatch.total_amount - paid

        if paid == 0:
            payment_status = "Unpaid"
        elif balance > 0:
            payment_status = "Partially Paid"
        else:
            payment_status = "Paid"

        frappe.db.set_value(
            "Dispatch Entry",
            dispatch.name,
            {
                "paid_amount": paid,
                "balance_amount": balance,
                "payment_status": payment_status,
            },
        )
