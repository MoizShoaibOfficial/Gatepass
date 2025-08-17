# Copyright (c) 2025, Gate Pass and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GateOutwardItem(Document):
    def validate(self):
        self.set_item_name()
    
    def set_item_name(self):
        if self.item_code and not self.item_name:
            item_name = frappe.db.get_value("Item", self.item_code, "item_name")
            if item_name:
                self.item_name = item_name 