# Copyright (c) 2025, Gate Pass and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GateOutward(Document):
    def validate(self):
        self.set_prepared_by()
        self.calculate_pending_qty()
    
    def before_submit(self):
        self.set_approved_by()
    
    def set_prepared_by(self):
        if not self.prepared_by:
            self.prepared_by = frappe.session.user
    
    def set_approved_by(self):
        self.approved_by = frappe.session.user
    
    def calculate_pending_qty(self):
        for item in self.items:
            item.pending_qty = item.qty - item.delivered_qty
    
    @frappe.whitelist()
    def fetch_items_from_dn(self, delivery_note):
        """Fetch items from Delivery Note"""
        if not delivery_note:
            return
        
        dn_doc = frappe.get_doc("Delivery Note", delivery_note)
        self.customer = dn_doc.customer
        self.source_document_type = "Delivery Note"
        self.source_document = delivery_note
        
        # Clear existing items
        self.items = []
        
        for item in dn_doc.items:
            self.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "delivered_qty": 0,
                "pending_qty": item.qty
            })
    
    @frappe.whitelist()
    def fetch_items_from_stock_entry(self, stock_entry):
        """Fetch items from Stock Entry"""
        if not stock_entry:
            return
        
        se_doc = frappe.get_doc("Stock Entry", stock_entry)
        self.source_document_type = "Stock Entry"
        self.source_document = stock_entry
        
        # Clear existing items
        self.items = []
        
        for item in se_doc.items:
            if item.s_warehouse:  # Only items coming from a warehouse (outward)
                self.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "warehouse": item.s_warehouse,
                    "delivered_qty": 0,
                    "pending_qty": item.qty
                }) 