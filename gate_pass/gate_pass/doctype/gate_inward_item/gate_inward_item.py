# Copyright (c) 2025, Gate Pass and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GateInwardItem(Document):
    def validate(self):
        self.set_item_name()
    
    def set_item_name(self):
        if self.item_code:
            # Always fetch item_name from Item doctype to ensure it's set
            item_name = frappe.db.get_value("Item", self.item_code, "item_name")
            if item_name:
                self.item_name = item_name
            
            # Also ensure UOM is set
            if not self.uom:
                stock_uom = frappe.db.get_value("Item", self.item_code, "stock_uom")
                if stock_uom:
                    self.uom = stock_uom 