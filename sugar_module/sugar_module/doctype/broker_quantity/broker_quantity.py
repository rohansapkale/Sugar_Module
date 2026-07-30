# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe.model.document import Document
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class BrokerQuantity(Document):

    def validate(self):
        self.calculate_values()

        if self.sugar_purchase:
            self.supplier = frappe.db.get_value(
                "Sugar Purchase",
                self.sugar_purchase,
                "supplier"
            )


    def on_submit(self):
        self.status = "Open"

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

        purchase_qty = purchase.purchase_qty_quintal or 0
        allocated_qty = purchase.allocated_qty_quintal or 0

        available_qty = purchase_qty - allocated_qty

        if self.allocated_qty_quintal > available_qty:
            frappe.throw(
                f"Only {available_qty} Quintal is available."
            )

        purchase.save(ignore_permissions=True)



    def on_cancel(self):

        self.status = "Open"

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

        purchase_qty = purchase.purchase_qty_quintal or 0
        allocated_qty = purchase.allocated_qty_quintal or 0

        available_qty = purchase_qty - allocated_qty

        if self.allocated_qty_quintal > available_qty:
            frappe.throw(
                f"Only {available_qty} Quintal is available."
            )

         

        purchase.save(ignore_permissions=True)

        purchase = frappe.get_doc(
            "Sugar Purchase",
            self.sugar_purchase
        )

        purchase.allocated_qty_quintal -= self.allocated_qty_quintal
        purchase.save(ignore_permissions=True)
        update_purchase_history(self.sugar_purchase)

    def calculate_values(self):

        qty_qtl = self.allocated_qty_quintal or 0
        rate = self.rate or 0

    # Convert Quintal to KG
        self.allocated_qty_kg = qty_qtl * 100

    # Add 5% GST
        gst = rate * 5 / 100
        final_rate = rate + gst

    # Optional (only if these fields exist)
    # self.gst_amount = gst
    # self.final_rate = final_rate

    # Total Amount = Quintal Qty × Final Rate
        self.total_amount = qty_qtl * final_rate

        sold = self.sold_qty_kg or 0

        self.pending_qty_kg = self.allocated_qty_kg - sold

        if sold == 0:
            self.status = "Open"

        elif sold < self.allocated_qty_kg:
            self.status = "Partially Sold"

        else:
            self.status = "Completed"

    def autoname(self):

        broker_name = frappe.db.get_value(
            "Broker",
            self.broker,
            "broker_name"
        ) or self.broker

        broker_name = broker_name.replace(" ", "").upper()

        allocation_date = frappe.utils.getdate(self.allocation_date).strftime("%d%m%Y")

        self.name = f"{broker_name}-{allocation_date}-{make_autoname('.####')}"
