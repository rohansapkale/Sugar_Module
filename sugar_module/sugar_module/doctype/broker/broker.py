# Copyright (c) 2026, Rohan Sapkale and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class Broker(Document):

    def validate(self):
        self.validate_mobile()

    def validate_mobile(self):
        if self.mobile_no:
            self.mobile_no = self.mobile_no.strip()

            if not self.mobile_no.isdigit():
                frappe.throw("Mobile Number should contain only digits.")

            if len(self.mobile_no) != 10:
                frappe.throw("Mobile Number must be exactly 10 digits.")
