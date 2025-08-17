# Copyright (c) 2025, Gate Pass and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc

def create_gate_inward_from_po(doc, method):
    """Create Gate Inward when Purchase Order is submitted"""
    try:
        # Check if gate inward already exists for this PO
        existing_gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Purchase Order",
            "source_document": doc.name
        })
        
        if existing_gate_inward:
            return
        
        # Create Gate Inward
        gate_inward = frappe.new_doc("Gate Inward")
        gate_inward.gate_inward_type = "Purchase Order"
        gate_inward.source_document_type = "Purchase Order"
        gate_inward.source_document = doc.name
        gate_inward.supplier = doc.supplier
        gate_inward.creation_date = doc.transaction_date
        
        # Add items
        for item in doc.items:
            gate_inward.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "received_qty": 0,
                "pending_qty": item.qty
            })
        
        gate_inward.insert()
        frappe.msgprint(_("Gate Inward {0} created for Purchase Order {1}").format(
            gate_inward.name, doc.name
        ))
        
    except Exception as e:
        frappe.log_error(f"Error creating Gate Inward from PO {doc.name}: {str(e)}")

def cancel_gate_inward_from_po(doc, method):
    """Cancel Gate Inward when Purchase Order is cancelled"""
    try:
        gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Purchase Order",
            "source_document": doc.name
        })
        
        if gate_inward:
            gate_inward_doc = frappe.get_doc("Gate Inward", gate_inward)
            if gate_inward_doc.docstatus == 1:
                gate_inward_doc.cancel()
            frappe.msgprint(_("Gate Inward {0} cancelled").format(gate_inward))
            
    except Exception as e:
        frappe.log_error(f"Error cancelling Gate Inward from PO {doc.name}: {str(e)}")

def create_gate_outward_from_dn(doc, method):
    """Create Gate Outward when Delivery Note is submitted"""
    try:
        # Check if gate outward already exists for this DN
        existing_gate_outward = frappe.db.exists("Gate Outward", {
            "source_document_type": "Delivery Note",
            "source_document": doc.name
        })
        
        if existing_gate_outward:
            return
        
        # Create Gate Outward
        gate_outward = frappe.new_doc("Gate Outward")
        gate_outward.gate_outward_type = "Delivery Note"
        gate_outward.source_document_type = "Delivery Note"
        gate_outward.source_document = doc.name
        gate_outward.customer = doc.customer
        gate_outward.creation_date = doc.posting_date
        
        # Add items
        for item in doc.items:
            gate_outward.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "delivered_qty": 0,
                "pending_qty": item.qty
            })
        
        gate_outward.insert()
        frappe.msgprint(_("Gate Outward {0} created for Delivery Note {1}").format(
            gate_outward.name, doc.name
        ))
        
    except Exception as e:
        frappe.log_error(f"Error creating Gate Outward from DN {doc.name}: {str(e)}")

def cancel_gate_outward_from_dn(doc, method):
    """Cancel Gate Outward when Delivery Note is cancelled"""
    try:
        gate_outward = frappe.db.exists("Gate Outward", {
            "source_document_type": "Delivery Note",
            "source_document": doc.name
        })
        
        if gate_outward:
            gate_outward_doc = frappe.get_doc("Gate Outward", gate_outward)
            if gate_outward_doc.docstatus == 1:
                gate_outward_doc.cancel()
            frappe.msgprint(_("Gate Outward {0} cancelled").format(gate_outward))
            
    except Exception as e:
        frappe.log_error(f"Error cancelling Gate Outward from DN {doc.name}: {str(e)}")

def create_gate_pass_from_stock_entry(doc, method):
    """Create Gate Inward/Outward when Stock Entry is submitted"""
    try:
        # Check if gate pass already exists for this Stock Entry
        existing_gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Stock Entry",
            "source_document": doc.name
        })
        
        existing_gate_outward = frappe.db.exists("Gate Outward", {
            "source_document_type": "Stock Entry",
            "source_document": doc.name
        })
        
        if existing_gate_inward or existing_gate_outward:
            return
        
        # Separate items for inward and outward
        inward_items = []
        outward_items = []
        
        for item in doc.items:
            if item.t_warehouse and not item.s_warehouse:
                # Inward movement (items going to a warehouse)
                inward_items.append(item)
            elif item.s_warehouse and not item.t_warehouse:
                # Outward movement (items coming from a warehouse)
                outward_items.append(item)
            elif item.s_warehouse and item.t_warehouse:
                # Transfer between warehouses - treat as outward from source and inward to target
                outward_items.append(item)
                inward_items.append(item)
        
        # Create Gate Inward if there are inward items
        if inward_items:
            gate_inward = frappe.new_doc("Gate Inward")
            gate_inward.gate_inward_type = "Stock Entry"
            gate_inward.source_document_type = "Stock Entry"
            gate_inward.source_document = doc.name
            gate_inward.creation_date = doc.posting_date
            
            for item in inward_items:
                gate_inward.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "warehouse": item.t_warehouse,
                    "received_qty": 0,
                    "pending_qty": item.qty
                })
            
            gate_inward.insert()
            frappe.msgprint(_("Gate Inward {0} created for Stock Entry {1}").format(
                gate_inward.name, doc.name
            ))
        
        # Create Gate Outward if there are outward items
        if outward_items:
            gate_outward = frappe.new_doc("Gate Outward")
            gate_outward.gate_outward_type = "Stock Entry"
            gate_outward.source_document_type = "Stock Entry"
            gate_outward.source_document = doc.name
            gate_outward.creation_date = doc.posting_date
            
            for item in outward_items:
                gate_outward.append("items", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "warehouse": item.s_warehouse,
                    "delivered_qty": 0,
                    "pending_qty": item.qty
                })
            
            gate_outward.insert()
            frappe.msgprint(_("Gate Outward {0} created for Stock Entry {1}").format(
                gate_outward.name, doc.name
            ))
        
    except Exception as e:
        frappe.log_error(f"Error creating Gate Pass from Stock Entry {doc.name}: {str(e)}")

def cancel_gate_pass_from_stock_entry(doc, method):
    """Cancel Gate Pass when Stock Entry is cancelled"""
    try:
        # Cancel Gate Inward
        gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Stock Entry",
            "source_document": doc.name
        })
        
        if gate_inward:
            gate_inward_doc = frappe.get_doc("Gate Inward", gate_inward)
            if gate_inward_doc.docstatus == 1:
                gate_inward_doc.cancel()
            frappe.msgprint(_("Gate Inward {0} cancelled").format(gate_inward))
        
        # Cancel Gate Outward
        gate_outward = frappe.db.exists("Gate Outward", {
            "source_document_type": "Stock Entry",
            "source_document": doc.name
        })
        
        if gate_outward:
            gate_outward_doc = frappe.get_doc("Gate Outward", gate_outward)
            if gate_outward_doc.docstatus == 1:
                gate_outward_doc.cancel()
            frappe.msgprint(_("Gate Outward {0} cancelled").format(gate_outward))
            
    except Exception as e:
        frappe.log_error(f"Error cancelling Gate Pass from Stock Entry {doc.name}: {str(e)}")

def update_gate_inward_from_pr(doc, method):
    """Update Gate Inward received quantities when Purchase Receipt is submitted"""
    try:
        # Find related Gate Inward
        gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Purchase Order",
            "source_document": doc.purchase_order
        })
        
        if not gate_inward:
            return
        
        gate_inward_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Update received quantities
        for pr_item in doc.items:
            for gi_item in gate_inward_doc.items:
                if gi_item.item_code == pr_item.item_code:
                    gi_item.received_qty += pr_item.qty
                    gi_item.pending_qty = gi_item.qty - gi_item.received_qty
                    break
        
        gate_inward_doc.save()
        frappe.msgprint(_("Gate Inward {0} updated with received quantities").format(gate_inward))
        
    except Exception as e:
        frappe.log_error(f"Error updating Gate Inward from PR {doc.name}: {str(e)}")

def revert_gate_inward_from_pr(doc, method):
    """Revert Gate Inward received quantities when Purchase Receipt is cancelled"""
    try:
        # Find related Gate Inward
        gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Purchase Order",
            "source_document": doc.purchase_order
        })
        
        if not gate_inward:
            return
        
        gate_inward_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Revert received quantities
        for pr_item in doc.items:
            for gi_item in gate_inward_doc.items:
                if gi_item.item_code == pr_item.item_code:
                    gi_item.received_qty -= pr_item.qty
                    gi_item.pending_qty = gi_item.qty - gi_item.received_qty
                    break
        
        gate_inward_doc.save()
        frappe.msgprint(_("Gate Inward {0} reverted with cancelled quantities").format(gate_inward))
        
    except Exception as e:
        frappe.log_error(f"Error reverting Gate Inward from PR {doc.name}: {str(e)}")

@frappe.whitelist()
def fetch_items_from_gate_inward(purchase_receipt, gate_inward):
    """Fetch items from Gate Inward to Purchase Receipt"""
    try:
        # Check if purchase receipt exists
        if not frappe.db.exists("Purchase Receipt", purchase_receipt):
            frappe.throw(_("Purchase Receipt {0} not found").format(purchase_receipt))
        
        pr_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
        
        # Check if document is already submitted
        if pr_doc.docstatus == 1:
            frappe.throw(_("Purchase Receipt already submitted. Cannot fetch items."))
        
        gi_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Clear existing items
        pr_doc.items = []
        
        # Add items from Gate Inward
        for gi_item in gi_doc.items:
            if gi_item.pending_qty > 0:  # Only add items with pending quantity
                # Validate that item_code exists
                if not gi_item.item_code:
                    frappe.throw(_("Item Code is missing in Gate Inward item"))
                
                # Get item details to ensure we have all required fields
                try:
                    item_doc = frappe.get_doc("Item", gi_item.item_code)
                except Exception as e:
                    frappe.throw(_("Item {0} not found in Item master").format(gi_item.item_code))
                
                # Ensure we have all required data
                item_name = gi_item.item_name or item_doc.item_name
                uom = gi_item.uom or item_doc.stock_uom
                
                if not item_name:
                    frappe.throw(_("Item Name is missing for item {0}").format(gi_item.item_code))
                
                if not uom:
                    frappe.throw(_("UOM is missing for item {0}").format(gi_item.item_code))
                
                pr_doc.append("items", {
                    "item_code": gi_item.item_code,
                    "item_name": item_name,
                    "description": gi_item.description or "",
                    "qty": gi_item.pending_qty,
                    "received_qty": gi_item.pending_qty,  # Required field
                    "uom": uom,
                    "stock_uom": item_doc.stock_uom,  # Required field
                    "conversion_factor": 1.0,  # Required field
                    "warehouse": gi_item.warehouse,
                    "rate": 0,  # Required field
                    "base_rate": 0,  # Required field
                    "amount": 0,
                    "base_amount": 0,
                    "source_document_type": "Gate Inward",  # Track source
                    "source_document": gate_inward  # Track source
                })
        
        pr_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Gate Inward {gate_inward} to PR {purchase_receipt}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_gate_inward_via_get_items(purchase_receipt, gate_inward):
    """Fetch items from Gate Inward to Purchase Receipt via Get Items From functionality"""
    try:
        # Check if purchase receipt exists
        if not frappe.db.exists("Purchase Receipt", purchase_receipt):
            frappe.throw(_("Purchase Receipt {0} not found").format(purchase_receipt))
        
        pr_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
        
        # Check if document is already submitted
        if pr_doc.docstatus == 1:
            frappe.throw(_("Purchase Receipt already submitted. Cannot fetch items."))
        
        gi_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Validate that Gate Inward is submitted
        if gi_doc.docstatus != 1:
            frappe.throw(_("Gate Inward {0} is not submitted").format(gate_inward))
        
        # Validate supplier match
        if pr_doc.supplier and gi_doc.supplier and pr_doc.supplier != gi_doc.supplier:
            frappe.throw(_("Supplier mismatch. Purchase Receipt supplier {0} does not match Gate Inward supplier {1}").format(pr_doc.supplier, gi_doc.supplier))
        
        # Set supplier if not already set
        if not pr_doc.supplier and gi_doc.supplier:
            pr_doc.supplier = gi_doc.supplier
        
        # Clear existing items
        pr_doc.items = []
        
        # Add items from Gate Inward
        for gi_item in gi_doc.items:
            if gi_item.pending_qty > 0:  # Only add items with pending quantity
                # Validate that item_code exists
                if not gi_item.item_code:
                    frappe.throw(_("Item Code is missing in Gate Inward item"))
                
                # Get item details to ensure we have all required fields
                try:
                    item_doc = frappe.get_doc("Item", gi_item.item_code)
                except Exception as e:
                    frappe.throw(_("Item {0} not found in Item master").format(gi_item.item_code))
                
                # Ensure we have all required data
                item_name = gi_item.item_name or item_doc.item_name
                uom = gi_item.uom or item_doc.stock_uom
                
                if not item_name:
                    frappe.throw(_("Item Name is missing for item {0}").format(gi_item.item_code))
                
                if not uom:
                    frappe.throw(_("UOM is missing for item {0}").format(gi_item.item_code))
                
                pr_doc.append("items", {
                    "item_code": gi_item.item_code,
                    "item_name": item_name,
                    "description": gi_item.description or "",
                    "qty": gi_item.pending_qty,
                    "received_qty": gi_item.pending_qty,  # Required field
                    "uom": uom,
                    "stock_uom": item_doc.stock_uom,  # Required field
                    "conversion_factor": 1.0,  # Required field
                    "warehouse": gi_item.warehouse,
                    "rate": 0,  # Required field
                    "base_rate": 0,  # Required field
                    "amount": 0,
                    "base_amount": 0,
                    "source_document_type": "Gate Inward",  # Track source
                    "source_document": gate_inward  # Track source
                })
        
        pr_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Gate Inward {gate_inward} to PR {purchase_receipt}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_gate_outward(delivery_note, gate_outward):
    """Fetch items from Gate Outward to Delivery Note"""
    try:
        dn_doc = frappe.get_doc("Delivery Note", delivery_note)
        go_doc = frappe.get_doc("Gate Outward", gate_outward)
        
        # Clear existing items
        dn_doc.items = []
        
        # Add items from Gate Outward
        for go_item in go_doc.items:
            if go_item.pending_qty > 0:  # Only add items with pending quantity
                # Get item details to ensure we have all required fields
                item_doc = frappe.get_doc("Item", go_item.item_code)
                
                dn_doc.append("items", {
                    "item_code": go_item.item_code,
                    "item_name": go_item.item_name or item_doc.item_name,
                    "description": go_item.description or "",
                    "qty": go_item.pending_qty,
                    "uom": go_item.uom or item_doc.stock_uom,
                    "stock_uom": item_doc.stock_uom,
                    "conversion_factor": 1.0,
                    "warehouse": go_item.warehouse,
                    "rate": 0,  # You may want to fetch rate from SO
                    "amount": 0,
                    "base_rate": 0,
                    "base_amount": 0
                })
        
        dn_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Gate Outward {gate_outward} to DN {delivery_note}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_po(gate_inward, purchase_order):
    """Fetch items from Purchase Order to Gate Inward"""
    try:
        # Check if gate inward exists
        if not frappe.db.exists("Gate Inward", gate_inward):
            frappe.throw(_("Gate Inward {0} not found").format(gate_inward))
        
        gi_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Check if document is already submitted
        if gi_doc.docstatus == 1:
            frappe.throw(_("Gate Inward already submitted. Cannot fetch items."))
        
        po_doc = frappe.get_doc("Purchase Order", purchase_order)
        
        # Update gate inward details only if not already set
        if not gi_doc.source_document:
            gi_doc.gate_inward_type = "Purchase Order"
            gi_doc.source_document_type = "Purchase Order"
            gi_doc.source_document = purchase_order
            gi_doc.supplier = po_doc.supplier
        
        # Clear existing items
        gi_doc.items = []
        
        # Add items from Purchase Order
        for po_item in po_doc.items:
            gi_doc.append("items", {
                "item_code": po_item.item_code,
                "item_name": po_item.item_name,
                "description": po_item.description or "",
                "qty": po_item.qty,
                "uom": po_item.uom,
                "warehouse": po_item.warehouse,
                "received_qty": 0,
                "pending_qty": po_item.qty
            })
        
        gi_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from PO {purchase_order} to Gate Inward {gate_inward}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_stock_entry(gate_inward, stock_entry):
    """Fetch items from Stock Entry to Gate Inward"""
    try:
        # Check if gate inward exists
        if not frappe.db.exists("Gate Inward", gate_inward):
            frappe.throw(_("Gate Inward {0} not found").format(gate_inward))
        
        gi_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Check if document is already submitted
        if gi_doc.docstatus == 1:
            frappe.throw(_("Gate Inward already submitted. Cannot fetch items."))
        
        se_doc = frappe.get_doc("Stock Entry", stock_entry)
        
        # Update gate inward details only if not already set
        if not gi_doc.source_document:
            gi_doc.gate_inward_type = "Stock Entry"
            gi_doc.source_document_type = "Stock Entry"
            gi_doc.source_document = stock_entry
        
        # Clear existing items
        gi_doc.items = []
        
        # Add items from Stock Entry (only inward movements)
        for se_item in se_doc.items:
            if se_item.t_warehouse and not se_item.s_warehouse:  # Only items going to a warehouse
                gi_doc.append("items", {
                    "item_code": se_item.item_code,
                    "item_name": se_item.item_name,
                    "description": se_item.description or "",
                    "qty": se_item.qty,
                    "uom": se_item.uom,
                    "warehouse": se_item.t_warehouse,
                    "received_qty": 0,
                    "pending_qty": se_item.qty
                })
        
        gi_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Stock Entry {stock_entry} to Gate Inward {gate_inward}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_dn(gate_outward, delivery_note):
    """Fetch items from Delivery Note to Gate Outward"""
    try:
        go_doc = frappe.get_doc("Gate Outward", gate_outward)
        
        # Check if document is already submitted
        if go_doc.docstatus == 1:
            frappe.throw(_("Gate Outward already submitted. Cannot fetch items."))
        
        dn_doc = frappe.get_doc("Delivery Note", delivery_note)
        
        # Update gate outward details only if not already set
        if not go_doc.source_document:
            go_doc.gate_outward_type = "Delivery Note"
            go_doc.source_document_type = "Delivery Note"
            go_doc.source_document = delivery_note
            go_doc.customer = dn_doc.customer
        
        # Clear existing items
        go_doc.items = []
        
        # Add items from Delivery Note
        for dn_item in dn_doc.items:
            go_doc.append("items", {
                "item_code": dn_item.item_code,
                "item_name": dn_item.item_name,
                "description": dn_item.description or "",
                "qty": dn_item.qty,
                "uom": dn_item.uom,
                "warehouse": dn_item.warehouse,
                "delivered_qty": 0,
                "pending_qty": dn_item.qty
            })
        
        go_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from DN {delivery_note} to Gate Outward {gate_outward}: {str(e)}")
        return False

@frappe.whitelist()
def fetch_items_from_stock_entry_outward(gate_outward, stock_entry):
    """Fetch items from Stock Entry to Gate Outward"""
    try:
        go_doc = frappe.get_doc("Gate Outward", gate_outward)
        
        # Check if document is already submitted
        if go_doc.docstatus == 1:
            frappe.throw(_("Gate Outward already submitted. Cannot fetch items."))
        
        se_doc = frappe.get_doc("Stock Entry", stock_entry)
        
        # Update gate outward details only if not already set
        if not go_doc.source_document:
            go_doc.gate_outward_type = "Stock Entry"
            go_doc.source_document_type = "Stock Entry"
            go_doc.source_document = stock_entry
        
        # Clear existing items
        go_doc.items = []
        
        # Add items from Stock Entry (only outward movements)
        for se_item in se_doc.items:
            if se_item.s_warehouse and not se_item.t_warehouse:  # Only items coming from a warehouse
                go_doc.append("items", {
                    "item_code": se_item.item_code,
                    "item_name": se_item.item_name,
                    "description": se_item.description or "",
                    "qty": se_item.qty,
                    "uom": se_item.uom,
                    "warehouse": se_item.s_warehouse,
                    "delivered_qty": 0,
                    "pending_qty": se_item.qty
                })
        
        go_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Stock Entry {stock_entry} to Gate Outward {gate_outward}: {str(e)}")
        return False

@frappe.whitelist()
def create_gate_inward_from_pr(purchase_receipt):
    """Create Gate Inward from Purchase Receipt"""
    try:
        # Check if purchase receipt exists
        if not frappe.db.exists("Purchase Receipt", purchase_receipt):
            frappe.throw(_("Purchase Receipt {0} not found").format(purchase_receipt))
        
        pr_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
        
        # Check if document is already submitted
        if pr_doc.docstatus == 1:
            frappe.throw(_("Purchase Receipt already submitted. Cannot create Gate Inward."))
        
        # Check if gate inward already exists for this PR
        existing_gate_inward = frappe.db.exists("Gate Inward", {
            "source_document_type": "Purchase Receipt",
            "source_document": purchase_receipt
        })
        
        if existing_gate_inward:
            frappe.throw(_("Gate Inward already exists for this Purchase Receipt"))
        
        # Create Gate Inward
        gate_inward = frappe.new_doc("Gate Inward")
        gate_inward.gate_inward_type = "Purchase Receipt"
        gate_inward.source_document_type = "Purchase Receipt"
        gate_inward.source_document = purchase_receipt
        gate_inward.supplier = pr_doc.supplier
        gate_inward.creation_date = pr_doc.posting_date
        
        # Add items from Purchase Receipt
        for pr_item in pr_doc.items:
            gate_inward.append("items", {
                "item_code": pr_item.item_code,
                "item_name": pr_item.item_name,
                "description": pr_item.description or "",
                "qty": pr_item.qty,
                "uom": pr_item.uom,
                "warehouse": pr_item.warehouse,
                "received_qty": pr_item.qty,  # Already received
                "pending_qty": 0
            })
        
        gate_inward.insert()
        return gate_inward.name
        
    except Exception as e:
        frappe.log_error(f"Error creating Gate Inward from PR {purchase_receipt}: {str(e)}")
        return False 

@frappe.whitelist()
def get_available_gate_inwards(supplier):
    """Get available Gate Inwards for a supplier that don't have Purchase Receipts created against them"""
    try:
        # Get all submitted Gate Inwards for the supplier
        gate_inwards = frappe.get_all("Gate Inward", 
            filters={
                'supplier': supplier,
                'docstatus': 1,
                'gate_inward_type': 'Purchase Order'
            },
            fields=['name', 'creation_date', 'source_document']
        )
        
        available_gate_inwards = []
        
        for gi in gate_inwards:
            # Check if any Purchase Receipt exists for this Gate Inward
            existing_pr = frappe.db.exists("Purchase Receipt", {
                'source_document_type': 'Gate Inward',
                'source_document': gi.name
            })
            
            # Also check if any Purchase Receipt has items from this Gate Inward
            # (This is a more comprehensive check)
            existing_pr_items = frappe.db.sql("""
                SELECT DISTINCT parent 
                FROM `tabPurchase Receipt Item` 
                WHERE source_document_type = 'Gate Inward' 
                AND source_document = %s
            """, gi.name)
            
            if not existing_pr and not existing_pr_items:
                # Calculate total pending quantity for this Gate Inward
                total_pending_qty = frappe.db.sql("""
                    SELECT SUM(pending_qty) as total_pending
                    FROM `tabGate Inward Item`
                    WHERE parent = %s AND pending_qty > 0
                """, gi.name, as_dict=True)
                
                pending_qty = total_pending_qty[0].total_pending if total_pending_qty and total_pending_qty[0].total_pending else 0
                
                if pending_qty > 0:  # Only include if there are pending items
                    available_gate_inwards.append({
                        'name': gi.name,
                        'creation_date': gi.creation_date,
                        'source_document': gi.source_document,
                        'total_pending_qty': pending_qty
                    })
        
        return available_gate_inwards
        
    except Exception as e:
        frappe.log_error(f"Error getting available Gate Inwards for supplier {supplier}: {str(e)}")
        return [] 

@frappe.whitelist()
def make_purchase_receipt_from_supplier_quotation(source_name, target_doc=None):
    """Make Purchase Receipt from Supplier Quotation - replicates Purchase Order behavior"""
    from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order
    
    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")
    
    def update_item(obj, target, source_parent):
        target.qty = flt(obj.qty)
        target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)
        target.amount = flt(obj.qty) * flt(obj.rate)
        target.base_amount = flt(obj.qty) * flt(obj.rate) * flt(source_parent.conversion_rate)
    
    doc = get_mapped_doc(
        "Supplier Quotation",
        source_name,
        {
            "Supplier Quotation": {
                "doctype": "Purchase Receipt",
                "validation": {
                    "docstatus": ["=", 1],
                },
            },
            "Supplier Quotation Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "supplier_quotation_item",
                    "parent": "supplier_quotation",
                    "material_request": "material_request",
                    "material_request_item": "material_request_item",
                    "sales_order": "sales_order",
                },
                "postprocess": update_item,
            },
            "Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "reset_value": True},
        },
        target_doc,
        set_missing_values,
    )
    
    return doc

@frappe.whitelist()
def make_purchase_receipt_from_gate_inward(source_name, target_doc=None):
    """Make Purchase Receipt from Gate Inward - replicates Purchase Order behavior"""
    
    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")
    
    def update_item(obj, target, source_parent):
        target.qty = flt(obj.pending_qty)
        target.received_qty = flt(obj.pending_qty)
        target.stock_qty = flt(obj.pending_qty) * flt(obj.conversion_factor or 1.0)
        target.amount = 0  # Gate Inward doesn't have rates
        target.base_amount = 0
        # Add source tracking
        target.source_document_type = "Gate Inward"
        target.source_document = source_name
    
    # Validate that Gate Inward has pending items
    pending_items = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabGate Inward Item`
        WHERE parent = %s AND pending_qty > 0
    """, source_name, as_dict=True)
    
    if not pending_items or pending_items[0].count == 0:
        frappe.throw(_("Gate Inward {0} has no pending items to fetch").format(source_name))
    
    doc = get_mapped_doc(
        "Gate Inward",
        source_name,
        {
            "Gate Inward": {
                "doctype": "Purchase Receipt",
                "validation": {
                    "docstatus": ["=", 1],
                },
            },
            "Gate Inward Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "gate_inward_item",
                    "parent": "gate_inward",
                    "item_code": "item_code",
                    "item_name": "item_name",
                    "description": "description",
                    "uom": "uom",
                    "warehouse": "warehouse",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.pending_qty > 0,
            },
        },
        target_doc,
        set_missing_values,
    )
    
    return doc

@frappe.whitelist()
def get_gate_inwards_for_get_items(doctype, txt, searchfield, start, page_len, filters):
    """Get Gate Inwards for Get Items From dialog"""
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
        frappe.log_error(f"Error getting Gate Inwards for Get Items From: {str(e)}")
        return [] 

@frappe.whitelist()
def fetch_items_from_supplier_quotation(purchase_receipt, supplier_quotation):
    """Fetch items from Supplier Quotation to Purchase Receipt"""
    try:
        # Check if purchase receipt exists
        if not frappe.db.exists("Purchase Receipt", purchase_receipt):
            frappe.throw(_("Purchase Receipt {0} not found").format(purchase_receipt))
        
        pr_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
        
        # Check if document is already submitted
        if pr_doc.docstatus == 1:
            frappe.throw(_("Purchase Receipt already submitted. Cannot fetch items."))
        
        sq_doc = frappe.get_doc("Supplier Quotation", supplier_quotation)
        
        # Validate that Supplier Quotation is submitted
        if sq_doc.docstatus != 1:
            frappe.throw(_("Supplier Quotation {0} is not submitted").format(supplier_quotation))
        
        # Validate supplier match
        if pr_doc.supplier and sq_doc.supplier and pr_doc.supplier != sq_doc.supplier:
            frappe.throw(_("Supplier mismatch. Purchase Receipt supplier {0} does not match Supplier Quotation supplier {1}").format(pr_doc.supplier, sq_doc.supplier))
        
        # Set supplier if not already set
        if not pr_doc.supplier and sq_doc.supplier:
            pr_doc.supplier = sq_doc.supplier
        
        # Clear existing items
        pr_doc.items = []
        
        # Add items from Supplier Quotation
        for sq_item in sq_doc.items:
            # Validate that item_code exists
            if not sq_item.item_code:
                frappe.throw(_("Item Code is missing in Supplier Quotation item"))
            
            # Get item details to ensure we have all required fields
            try:
                item_doc = frappe.get_doc("Item", sq_item.item_code)
            except Exception as e:
                frappe.throw(_("Item {0} not found in Item master").format(sq_item.item_code))
            
            # Ensure we have all required data
            item_name = sq_item.item_name or item_doc.item_name
            uom = sq_item.uom or item_doc.stock_uom
            
            if not item_name:
                frappe.throw(_("Item Name is missing for item {0}").format(sq_item.item_code))
            
            if not uom:
                frappe.throw(_("UOM is missing for item {0}").format(sq_item.item_code))
            
            pr_doc.append("items", {
                "item_code": sq_item.item_code,
                "item_name": item_name,
                "description": sq_item.description or "",
                "qty": sq_item.qty,
                "received_qty": sq_item.qty,  # Required field
                "uom": uom,
                "stock_uom": item_doc.stock_uom,  # Required field
                "conversion_factor": sq_item.conversion_factor or 1.0,  # Required field
                "warehouse": sq_item.warehouse,
                "rate": sq_item.rate or 0,  # Required field
                "base_rate": sq_item.rate or 0,  # Required field
                "amount": (sq_item.qty or 0) * (sq_item.rate or 0),
                "base_amount": (sq_item.qty or 0) * (sq_item.rate or 0),
                "supplier_quotation": supplier_quotation,  # Track source
                "supplier_quotation_item": sq_item.name  # Track source item
            })
        
        pr_doc.save()
        return True
        
    except Exception as e:
        frappe.log_error(f"Error fetching items from Supplier Quotation {supplier_quotation} to Purchase Receipt {purchase_receipt}: {str(e)}")
        return False 

@frappe.whitelist()
def fetch_items_from_purchase_order(purchase_receipt, purchase_order):
    """Fetch items from Purchase Order to Purchase Receipt"""
    try:
        frappe.logger().info(f"Starting fetch_items_from_purchase_order: PR={purchase_receipt}, PO={purchase_order}")
        
        # Try to get the purchase receipt document, create new if doesn't exist
        try:
            if frappe.db.exists("Purchase Receipt", purchase_receipt):
                pr_doc = frappe.get_doc("Purchase Receipt", purchase_receipt)
                frappe.logger().info(f"Found existing PR: {purchase_receipt}")
            else:
                # Create a new document with the given name
                pr_doc = frappe.new_doc("Purchase Receipt")
                pr_doc.name = purchase_receipt
                frappe.logger().info(f"Created new PR with name: {purchase_receipt}")
        except Exception as e:
            frappe.logger().error(f"Error getting/creating PR document: {str(e)}")
            # Create a new document as fallback
            pr_doc = frappe.new_doc("Purchase Receipt")
            pr_doc.name = purchase_receipt
        
        # Check if document is already submitted
        if hasattr(pr_doc, 'docstatus') and pr_doc.docstatus == 1:
            frappe.throw(_("Purchase Receipt already submitted. Cannot fetch items."))
        
        po_doc = frappe.get_doc("Purchase Order", purchase_order)
        
        # Validate that Purchase Order is submitted
        if po_doc.docstatus != 1:
            frappe.throw(_("Purchase Order {0} is not submitted").format(purchase_order))
        
        # Set supplier if not already set
        if not pr_doc.supplier and po_doc.supplier:
            pr_doc.supplier = po_doc.supplier
        
        # Clear existing items
        frappe.logger().info(f"Clearing existing items from PR {purchase_receipt}")
        pr_doc.items = []
        
        # Add items from Purchase Order
        frappe.logger().info(f"Processing {len(po_doc.items)} items from PO {purchase_order}")
        
        items_added = 0
        for po_item in po_doc.items:
            frappe.logger().info(f"Processing PO item: {po_item.item_code}, qty: {po_item.qty}")
            
            # Calculate remaining quantity to receive
            received_qty = frappe.db.sql("""
                SELECT COALESCE(SUM(pr_item.qty), 0) as received_qty
                FROM `tabPurchase Receipt Item` pr_item
                INNER JOIN `tabPurchase Receipt` pr ON pr_item.parent = pr.name
                WHERE pr_item.purchase_order_item = %s
                AND pr.docstatus = 1
            """, po_item.name, as_dict=True)
            
            remaining_qty = po_item.qty - (received_qty[0].received_qty or 0)
            frappe.logger().info(f"Remaining qty for {po_item.item_code}: {remaining_qty}")
            
            if remaining_qty > 0:
                # Validate that item_code exists
                if not po_item.item_code:
                    frappe.throw(_("Item Code is missing in Purchase Order item"))
                
                # Get item details to ensure we have all required fields
                try:
                    item_doc = frappe.get_doc("Item", po_item.item_code)
                except Exception as e:
                    frappe.throw(_("Item {0} not found in Item master").format(po_item.item_code))
                
                # Ensure we have all required data
                item_name = po_item.item_name or item_doc.item_name
                uom = po_item.uom or item_doc.stock_uom
                
                if not item_name:
                    frappe.throw(_("Item Name is missing for item {0}").format(po_item.item_code))
                
                if not uom:
                    frappe.throw(_("UOM is missing for item {0}").format(po_item.item_code))
                
                pr_doc.append("items", {
                    "item_code": po_item.item_code,
                    "item_name": item_name,
                    "description": po_item.description or "",
                    "qty": remaining_qty,
                    "received_qty": remaining_qty,  # Required field
                    "uom": uom,
                    "stock_uom": item_doc.stock_uom,  # Required field
                    "conversion_factor": po_item.conversion_factor or 1.0,  # Required field
                    "warehouse": po_item.warehouse,
                    "rate": po_item.rate or 0,  # Required field
                    "base_rate": po_item.base_rate or 0,  # Required field
                    "amount": remaining_qty * (po_item.rate or 0),
                    "base_amount": remaining_qty * (po_item.base_rate or 0),
                    "purchase_order": purchase_order,  # Track source
                    "purchase_order_item": po_item.name  # Track source item
                })
                frappe.logger().info(f"Added item {po_item.item_code} with qty {remaining_qty} to PR")
                items_added += 1
        
        frappe.logger().info(f"Total items added to PR: {items_added}")
        frappe.logger().info(f"PR items count before save: {len(pr_doc.items)}")
        
        # Save the document
        pr_doc.save()
        frappe.logger().info(f"PR saved successfully")
        
        # Verify the items were actually saved
        saved_pr = frappe.get_doc("Purchase Receipt", purchase_receipt)
        frappe.logger().info(f"PR items count after save: {len(saved_pr.items)}")
        for i, item in enumerate(saved_pr.items):
            frappe.logger().info(f"Saved item {i+1}: {item.item_code}, {item.item_name}, {item.qty}")
        
        frappe.logger().info(f"Successfully fetched items from PO {purchase_order} to PR {purchase_receipt}")
        return True
        
    except Exception as e:
        frappe.logger().error(f"Error fetching items from Purchase Order {purchase_order} to Purchase Receipt {purchase_receipt}: {str(e)}")
        frappe.log_error(f"Error fetching items from Purchase Order {purchase_order} to Purchase Receipt {purchase_receipt}: {str(e)}")
        return False 

@frappe.whitelist()
def test_purchase_order_items(purchase_order):
    """Test method to check Purchase Order items"""
    try:
        po_doc = frappe.get_doc("Purchase Order", purchase_order)
        result = {
            'name': po_doc.name,
            'supplier': po_doc.supplier,
            'docstatus': po_doc.docstatus,
            'status': po_doc.status,
            'items': []
        }
        
        for item in po_doc.items:
            # Calculate remaining quantity to receive
            received_qty = frappe.db.sql("""
                SELECT COALESCE(SUM(pr_item.qty), 0) as received_qty
                FROM `tabPurchase Receipt Item` pr_item
                INNER JOIN `tabPurchase Receipt` pr ON pr_item.parent = pr.name
                WHERE pr_item.purchase_order_item = %s
                AND pr.docstatus = 1
            """, item.name, as_dict=True)
            
            remaining_qty = item.qty - (received_qty[0].received_qty or 0)
            
            result['items'].append({
                'item_code': item.item_code,
                'item_name': item.item_name,
                'qty': item.qty,
                'received_qty': received_qty[0].received_qty or 0,
                'remaining_qty': remaining_qty,
                'uom': item.uom,
                'rate': item.rate
            })
        
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error testing PO {purchase_order}: {str(e)}")
        return {'error': str(e)}

@frappe.whitelist()
def fetch_items_from_purchase_order_for_form(purchase_receipt_name, purchase_order):
    """Fetch items from Purchase Order for form (without requiring document to exist in DB)"""
    try:
        frappe.logger().info(f"Starting fetch_items_from_purchase_order_for_form: PR={purchase_receipt_name}, PO={purchase_order}")
        
        po_doc = frappe.get_doc("Purchase Order", purchase_order)
        
        # Validate that Purchase Order is submitted
        if po_doc.docstatus != 1:
            return {"status": "error", "message": f"Purchase Order {purchase_order} is not submitted"}
        
        # Prepare items data
        items_data = []
        for po_item in po_doc.items:
            # Calculate remaining quantity to receive
            received_qty = frappe.db.sql("""
                SELECT COALESCE(SUM(pr_item.qty), 0) as received_qty
                FROM `tabPurchase Receipt Item` pr_item
                INNER JOIN `tabPurchase Receipt` pr ON pr_item.parent = pr.name
                WHERE pr_item.purchase_order_item = %s
                AND pr.docstatus = 1
            """, po_item.name, as_dict=True)
            
            remaining_qty = po_item.qty - (received_qty[0].received_qty or 0)
            
            if remaining_qty > 0:
                # Get item details
                try:
                    item_doc = frappe.get_doc("Item", po_item.item_code)
                except Exception as e:
                    continue  # Skip this item if not found
                
                items_data.append({
                    "item_code": po_item.item_code,
                    "item_name": po_item.item_name or item_doc.item_name,
                    "description": po_item.description or "",
                    "qty": remaining_qty,
                    "received_qty": remaining_qty,
                    "uom": po_item.uom or item_doc.stock_uom,
                    "stock_uom": item_doc.stock_uom,
                    "conversion_factor": po_item.conversion_factor or 1.0,
                    "warehouse": po_item.warehouse,
                    "rate": po_item.rate or 0,
                    "base_rate": po_item.base_rate or 0,
                    "amount": remaining_qty * (po_item.rate or 0),
                    "base_amount": remaining_qty * (po_item.base_rate or 0),
                    "purchase_order": purchase_order,
                    "purchase_order_item": po_item.name
                })
        
        return {
            "status": "success",
            "supplier": po_doc.supplier,
            "items": items_data,
            "total_items": len(items_data)
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in fetch_items_from_purchase_order_for_form: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def fetch_items_from_supplier_quotation_for_form(purchase_receipt_name, supplier_quotation):
    """Fetch items from Supplier Quotation for form (without requiring document to exist in DB)"""
    try:
        frappe.logger().info(f"Starting fetch_items_from_supplier_quotation_for_form: PR={purchase_receipt_name}, SQ={supplier_quotation}")
        
        sq_doc = frappe.get_doc("Supplier Quotation", supplier_quotation)
        
        # Validate that Supplier Quotation is submitted
        if sq_doc.docstatus != 1:
            return {"status": "error", "message": f"Supplier Quotation {supplier_quotation} is not submitted"}
        
        # Prepare items data
        items_data = []
        for sq_item in sq_doc.items:
            # Get item details
            try:
                item_doc = frappe.get_doc("Item", sq_item.item_code)
            except Exception as e:
                continue  # Skip this item if not found
            
            items_data.append({
                "item_code": sq_item.item_code,
                "item_name": sq_item.item_name or item_doc.item_name,
                "description": sq_item.description or "",
                "qty": sq_item.qty,
                "received_qty": sq_item.qty,
                "uom": sq_item.uom or item_doc.stock_uom,
                "stock_uom": item_doc.stock_uom,
                "conversion_factor": sq_item.conversion_factor or 1.0,
                "warehouse": sq_item.warehouse,
                "rate": sq_item.rate or 0,
                "base_rate": sq_item.rate or 0,
                "amount": (sq_item.qty or 0) * (sq_item.rate or 0),
                "base_amount": (sq_item.qty or 0) * (sq_item.rate or 0),
                "supplier_quotation": supplier_quotation,
                "supplier_quotation_item": sq_item.name
            })
        
        return {
            "status": "success",
            "supplier": sq_doc.supplier,
            "items": items_data,
            "total_items": len(items_data)
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in fetch_items_from_supplier_quotation_for_form: {str(e)}")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def fetch_items_from_gate_inward_for_form(purchase_receipt_name, gate_inward):
    """Fetch items from Gate Inward for form (without requiring document to exist in DB)"""
    try:
        frappe.logger().info(f"Starting fetch_items_from_gate_inward_for_form: PR={purchase_receipt_name}, GI={gate_inward}")
        
        gi_doc = frappe.get_doc("Gate Inward", gate_inward)
        
        # Validate that Gate Inward is submitted
        if gi_doc.docstatus != 1:
            return {"status": "error", "message": f"Gate Inward {gate_inward} is not submitted"}
        
        # Prepare items data
        items_data = []
        for gi_item in gi_doc.items:
            if gi_item.pending_qty > 0:  # Only add items with pending quantity
                # Get item details
                try:
                    item_doc = frappe.get_doc("Item", gi_item.item_code)
                except Exception as e:
                    continue  # Skip this item if not found
                
                items_data.append({
                    "item_code": gi_item.item_code,
                    "item_name": gi_item.item_name or item_doc.item_name,
                    "description": gi_item.description or "",
                    "qty": gi_item.pending_qty,
                    "received_qty": gi_item.pending_qty,
                    "uom": gi_item.uom or item_doc.stock_uom,
                    "stock_uom": item_doc.stock_uom,
                    "conversion_factor": 1.0,
                    "warehouse": gi_item.warehouse,
                    "rate": 0,
                    "base_rate": 0,
                    "amount": 0,
                    "base_amount": 0,
                    "source_document_type": "Gate Inward",
                    "source_document": gate_inward
                })
        
        return {
            "status": "success",
            "supplier": gi_doc.supplier,
            "items": items_data,
            "total_items": len(items_data)
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in fetch_items_from_gate_inward_for_form: {str(e)}")
        return {"status": "error", "message": str(e)} 