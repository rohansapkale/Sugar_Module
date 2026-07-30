# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from sugar_module.utils.stock import refresh_dispatch_history

class BrokerPartyPayment(Document):

    def validate(self):
        self.validate_payment()

    def on_submit(self):
        self.update_dispatch()

    def on_cancel(self):
        self.update_dispatch(cancel=True)

    def validate_payment(self):

        dispatch = frappe.get_doc(
            "Dispatch Entry",
            self.dispatch_entry
        )

        current_paid = dispatch.paid_amount or 0
        total_bill = dispatch.total_amount or 0

        # While cancelling, don't validate
        if self.docstatus == 2:
            return

        if (current_paid + self.paid_amount) > total_bill:
            frappe.throw(
                f"""
                Payment exceeds Bill Amount.

                Bill Amount : {total_bill}
                Already Paid : {current_paid}
                Current Payment : {self.paid_amount}
                """
            )

    def update_dispatch(self, cancel=False):

        dispatch = frappe.get_doc(
            "Dispatch Entry",
            self.dispatch_entry
        )

        paid = dispatch.paid_amount or 0

        if cancel:
            paid -= self.paid_amount
        else:
            paid += self.paid_amount

        if paid < 0:
            paid = 0

        balance = (dispatch.total_amount or 0) - paid

        if balance < 0:
            balance = 0

        # Payment Status
        if paid == 0:
            payment_status = "Unpaid"

        elif balance == 0:
            payment_status = "Paid"

        else:
            payment_status = "Partially Paid"

        dispatch.paid_amount = paid
        dispatch.balance_amount = balance
        dispatch.payment_status = payment_status

        dispatch.flags.ignore_validate_update_after_submit = True
        dispatch.save(ignore_permissions=True)

        refresh_dispatch_history(dispatch.sugar_purchase)
        frappe.db.commit()
