# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SugarPurchase(Document):

    def autoname(self):

        supplier_code = self.supplier.replace(" ", "").upper()

        self.name=(
            supplier_code
            + "-"
            + str(int(self.purchase_rate))
            + "-"
            + make_autoname('.####')
        )


    def validate(self):
        self.calculate_values()

    def on_submit(self):
        self.status = "Submitted"

    def on_cancel(self):
        self.status = "Cancelled"

    def calculate_values(self):

        qty_qtl = self.purchase_qty_quintal or 0
        rate = self.purchase_rate or 0

    # Convert Quintal to Kg
        self.converted_qty_kg = qty_qtl * 100

    # Calculate GST @5%
        self.gst_amount = rate * 5 / 100

    # Rate including GST
        self.final_rate = rate + self.gst_amount

    # Total Amount = Quantity (Quintal) × Final Rate
        self.total_amount = qty_qtl * self.final_rate
