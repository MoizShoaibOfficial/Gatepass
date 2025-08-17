// Copyright (c) 2025, Gate Pass and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gate Inward', {
    refresh: function(frm) {
        // Only show buttons if document is not submitted
        if (frm.doc.docstatus === 0) {
            // Add custom button to get items from Purchase Order
            frm.add_custom_button(__('Get Items From PO'), function() {
                get_items_from_po(frm);
            });
            
            // Add custom button to get items from Stock Entry
            frm.add_custom_button(__('Get Items From Stock Entry'), function() {
                get_items_from_stock_entry(frm);
            });
        }
    },
    
    // Also check on load
    onload: function(frm) {
        // Only show buttons if document is not submitted
        if (frm.doc.docstatus === 0) {
            // Add custom button to get items from Purchase Order
            frm.add_custom_button(__('Get Items From PO'), function() {
                get_items_from_po(frm);
            });
            
            // Add custom button to get items from Stock Entry
            frm.add_custom_button(__('Get Items From Stock Entry'), function() {
                get_items_from_stock_entry(frm);
            });
        }
    }
});

function get_items_from_po(frm) {
    // Check if document is already submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot fetch items. Gate Inward is already submitted.'));
        return;
    }
    
    // Show dialog to select Purchase Order
    let d = new frappe.ui.Dialog({
        title: __('Select Purchase Order'),
        fields: [
            {
                fieldtype: 'Link',
                fieldname: 'purchase_order',
                label: __('Purchase Order'),
                options: 'Purchase Order',
                reqd: 1,
                get_query: function() {
                    let filters = {
                        'docstatus': 1
                    };
                    
                    // If supplier is already set, filter by supplier
                    if (frm.doc.supplier) {
                        filters['supplier'] = frm.doc.supplier;
                    }
                    
                    return {
                        filters: filters
                    };
                }
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            let purchase_order = d.get_value('purchase_order');
            if (purchase_order) {
                // Check if document name is entered
                if (!frm.doc.name) {
                    frappe.msgprint(__('Please enter the Gate Inward name first before fetching items.'));
                    return;
                }
                fetch_items_from_po(frm, purchase_order);
            }
            d.hide();
        }
    });
    d.show();
}

function get_items_from_stock_entry(frm) {
    // Check if document is already submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot fetch items. Gate Inward is already submitted.'));
        return;
    }
    
    // Show dialog to select Stock Entry
    let d = new frappe.ui.Dialog({
        title: __('Select Stock Entry'),
        fields: [
            {
                fieldtype: 'Link',
                fieldname: 'stock_entry',
                label: __('Stock Entry'),
                options: 'Stock Entry',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'docstatus': 1,
                            'stock_entry_type': ['in', ['Material Receipt', 'Material Transfer']]
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            let stock_entry = d.get_value('stock_entry');
            if (stock_entry) {
                // Check if document name is entered
                if (!frm.doc.name) {
                    frappe.msgprint(__('Please enter the Gate Inward name first before fetching items.'));
                    return;
                }
                fetch_items_from_stock_entry(frm, stock_entry);
            }
            d.hide();
        }
    });
    d.show();
}

function fetch_items_from_po(frm, purchase_order) {
    frappe.call({
        method: 'gate_pass.gate_pass.doctype.gate_inward.gate_inward.fetch_items_from_po_for_form',
        args: {
            'gate_inward': frm.doc.name,
            'purchase_order': purchase_order
        },
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                // Update form fields
                frm.set_value('supplier', r.message.supplier);
                frm.set_value('source_document_type', r.message.source_document_type);
                frm.set_value('source_document', r.message.source_document);
                
                // Clear existing items
                frm.clear_table('items');
                
                // Add new items
                if (r.message.items && r.message.items.length > 0) {
                    r.message.items.forEach(function(item) {
                        let row = frm.add_child('items');
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.description = item.description;
                        row.qty = item.qty;
                        row.uom = item.uom;
                        row.warehouse = item.warehouse;
                        row.received_qty = item.received_qty;
                        row.pending_qty = item.pending_qty;
                    });
                }
                
                frm.refresh_field('items');
                frappe.msgprint(__('Items fetched from Purchase Order successfully'));
            } else {
                frappe.msgprint(__('Error: {0}').format(r.message ? r.message.message : 'Unknown error'));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Error: {0}').format(r.responseJSON._server_messages ? 
                JSON.parse(r.responseJSON._server_messages[0]).message : r.responseJSON.message || 'Unknown error'));
        }
    });
}

function fetch_items_from_stock_entry(frm, stock_entry) {
    frappe.call({
        method: 'gate_pass.gate_pass.doctype.gate_inward.gate_inward.fetch_items_from_stock_entry_for_form',
        args: {
            'gate_inward': frm.doc.name,
            'stock_entry': stock_entry
        },
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                // Update form fields
                frm.set_value('source_document_type', r.message.source_document_type);
                frm.set_value('source_document', r.message.source_document);
                
                // Clear existing items
                frm.clear_table('items');
                
                // Add new items
                if (r.message.items && r.message.items.length > 0) {
                    r.message.items.forEach(function(item) {
                        let row = frm.add_child('items');
                        row.item_code = item.item_code;
                        row.item_name = item.item_name;
                        row.description = item.description;
                        row.qty = item.qty;
                        row.uom = item.uom;
                        row.warehouse = item.warehouse;
                        row.received_qty = item.received_qty;
                        row.pending_qty = item.pending_qty;
                    });
                }
                
                frm.refresh_field('items');
                frappe.msgprint(__('Items fetched from Stock Entry successfully'));
            } else {
                frappe.msgprint(__('Error: {0}').format(r.message ? r.message.message : 'Unknown error'));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Error: {0}').format(r.responseJSON._server_messages ? 
                JSON.parse(r.responseJSON._server_messages[0]).message : r.responseJSON.message || 'Unknown error'));
        }
    });
} 