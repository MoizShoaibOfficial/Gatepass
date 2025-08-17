# Copyright (c) 2025, Gate Pass and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GateInward(Document):
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
            item.pending_qty = item.qty - item.received_qty
    
    @frappe.whitelist()
    def fetch_items_from_po(self, purchase_order):
        """Fetch items from Purchase Order"""
        if not purchase_order:
            return
        
        po_doc = frappe.get_doc("Purchase Order", purchase_order)
        self.supplier = po_doc.supplier
        self.source_document_type = "Purchase Order"
        self.source_document = purchase_order
        
        # Clear existing items
        self.items = []
        
        for item in po_doc.items:
            self.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "received_qty": 0,
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
            if item.t_warehouse:  # Only items going to a warehouse (inward)
                self.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "warehouse": item.t_warehouse,
                    "received_qty": 0,
                    "pending_qty": item.qty
                }) 

@frappe.whitelist()
def get_gate_inwards_for_purchase_receipt(doctype, txt, searchfield, start, page_len, filters):
    """Custom query method for Gate Inward selection in Purchase Receipt"""
    try:
        # Build the base query
        query = """
            SELECT DISTINCT gi.name, gi.creation_date, gi.supplier
            FROM `tabGate Inward` gi
            INNER JOIN `tabGate Inward Item` gi_item ON gi.name = gi_item.parent
            WHERE gi.docstatus = 1 
            AND gi.gate_inward_type = 'Purchase Order'
            AND gi_item.pending_qty > 0
        """
        
        # Add search conditions
        search_conditions = []
        if txt:
            search_conditions.append("(gi.name LIKE %s OR gi.supplier LIKE %s)")
        
        # Add supplier filter
        if filters.get('supplier'):
            search_conditions.append("gi.supplier = %s")
        
        # Combine conditions
        if search_conditions:
            query += " AND " + " AND ".join(search_conditions)
        
        # Add ordering and limit
        query += " ORDER BY gi.creation_date DESC LIMIT %s, %s"
        
        # Prepare parameters
        params = []
        if txt:
            params.extend(['%' + txt + '%', '%' + txt + '%'])
        if filters.get('supplier'):
            params.append(filters.get('supplier'))
        params.extend([start, page_len])
        
        # Execute query
        gate_inwards = frappe.db.sql(query, params, as_dict=True)
        
        # Format the results for Link field (return list of tuples with name as first element)
        results = []
        for gi in gate_inwards:
            # Calculate total pending quantity
            total_pending = frappe.db.sql("""
                SELECT SUM(pending_qty) as total_pending
                FROM `tabGate Inward Item`
                WHERE parent = %s AND pending_qty > 0
            """, gi.name, as_dict=True)
            
            pending_qty = total_pending[0].total_pending if total_pending and total_pending[0].total_pending else 0
            
            # Return tuple with name as first element for Link field
            results.append((gi.name,))
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Error getting Gate Inwards for Purchase Receipt: {str(e)}")
        return []