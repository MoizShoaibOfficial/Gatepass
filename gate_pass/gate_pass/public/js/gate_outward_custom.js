// Copyright (c) 2025, Gate Pass and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gate Outward', {
    refresh: function(frm) {
        // Only show buttons if document is not submitted
        if (frm.doc.docstatus === 0) {
            // Add custom button to get items from Delivery Note
            frm.add_custom_button(__('Get Items From DN'), function() {
                get_items_from_dn(frm);
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
            // Add custom button to get items from Delivery Note
            frm.add_custom_button(__('Get Items From DN'), function() {
                get_items_from_dn(frm);
            });
            
            // Add custom button to get items from Stock Entry
            frm.add_custom_button(__('Get Items From Stock Entry'), function() {
                get_items_from_stock_entry(frm);
            });
        }
    }
});

function get_items_from_dn(frm) {
    // Check if document is already submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot fetch items. Gate Outward is already submitted.'));
        return;
    }
    
    // Show dialog to select Delivery Note
    let d = new frappe.ui.Dialog({
        title: __('Select Delivery Note'),
        fields: [
            {
                fieldtype: 'Link',
                fieldname: 'delivery_note',
                label: __('Delivery Note'),
                options: 'Delivery Note',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'docstatus': 1
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            let delivery_note = d.get_value('delivery_note');
            if (delivery_note) {
                // First save the document if it's new
                if (frm.doc.__islocal) {
                    frm.save('Update', function() {
                        fetch_items_from_dn(frm, delivery_note);
                    });
                } else {
                    fetch_items_from_dn(frm, delivery_note);
                }
            }
            d.hide();
        }
    });
    d.show();
}

function get_items_from_stock_entry(frm) {
    // Check if document is already submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot fetch items. Gate Outward is already submitted.'));
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
                            'stock_entry_type': ['in', ['Material Issue', 'Material Transfer']]
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            let stock_entry = d.get_value('stock_entry');
            if (stock_entry) {
                // First save the document if it's new
                if (frm.doc.__islocal) {
                    frm.save('Update', function() {
                        fetch_items_from_stock_entry(frm, stock_entry);
                    });
                } else {
                    fetch_items_from_stock_entry(frm, stock_entry);
                }
            }
            d.hide();
        }
    });
    d.show();
}

function fetch_items_from_dn(frm, delivery_note) {
    frappe.call({
        method: 'gate_pass.gate_pass_events.fetch_items_from_dn',
        args: {
            'gate_outward': frm.doc.name,
            'delivery_note': delivery_note
        },
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.msgprint(__('Items fetched from Delivery Note successfully'));
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
        method: 'gate_pass.gate_pass_events.fetch_items_from_stock_entry_outward',
        args: {
            'gate_outward': frm.doc.name,
            'stock_entry': stock_entry
        },
        callback: function(r) {
            if (r.message) {
                frm.reload_doc();
                frappe.msgprint(__('Items fetched from Stock Entry successfully'));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Error: {0}').format(r.responseJSON._server_messages ? 
                JSON.parse(r.responseJSON._server_messages[0]).message : r.responseJSON.message || 'Unknown error'));
        }
    });
} 