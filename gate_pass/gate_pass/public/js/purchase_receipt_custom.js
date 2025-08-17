// Copyright (c) 2025, Gate Pass and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        // Only show buttons if document is not submitted
        if (frm.doc.docstatus === 0) {
            // Add custom button to create Gate Inward
            frm.add_custom_button(__('Create Gate Inward'), function() {
                create_gate_inward_from_pr(frm);
            });
        }
    }
});

// Override the existing add_custom_buttons method to replace with our comprehensive Get Items From functionality
frappe.ui.form.on('Purchase Receipt', {
    add_custom_buttons: function(frm) {
        // Only add our custom Get Items From button (replaces the original)
        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(
                __("Get Items From"),
                function() {
                    show_get_items_from_dialog(frm);
                }
            );
        }
    }
});

function show_get_items_from_dialog(frm) {
    // Create a comprehensive dialog for Get Items From
    let d = new frappe.ui.Dialog({
        title: __('Get Items From'),
        fields: [
            {
                fieldtype: 'Select',
                fieldname: 'source',
                label: __('Source'),
                options: 'Purchase Quotation\nPurchase Order\nGate Inward',
                reqd: 1,
                default: 'Purchase Order'
            },
            {
                fieldtype: 'Link',
                fieldname: 'source_name',
                label: __('Source Name'),
                reqd: 1,
                get_query: function() {
                    let source = d.get_value('source');
                    if (source === 'Gate Inward') {
                        return {
                            query: 'gate_pass.gate_pass_events.get_gate_inwards_for_get_items',
                            filters: {
                                'supplier': frm.doc.supplier || ''
                            }
                        };
                    } else if (source === 'Purchase Order') {
                        return {
                            filters: {
                                'docstatus': 1,
                                'supplier': frm.doc.supplier || ''
                            }
                        };
                    } else if (source === 'Purchase Quotation') {
                        return {
                            filters: {
                                'docstatus': 1,
                                'supplier': frm.doc.supplier || ''
                            }
                        };
                    }
                }
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            let source = d.get_value('source');
            let source_name = d.get_value('source_name');
            
            if (source === 'Gate Inward') {
                // Handle Gate Inward - replicate Purchase Order behavior
                erpnext.utils.map_current_doc({
                    method: 'gate_pass.gate_pass_events.make_purchase_receipt_from_gate_inward',
                    source_doctype: 'Gate Inward',
                    target: frm,
                    setters: {
                        supplier: frm.doc.supplier,
                    },
                    get_query_filters: {
                        docstatus: 1,
                        supplier: frm.doc.supplier || '',
                        gate_inward_type: 'Purchase Order',
                    },
                    query: 'gate_pass.gate_pass.doctype.gate_inward.gate_inward.get_gate_inwards_for_purchase_receipt',
                });
                d.hide();
            } else if (source === 'Purchase Order') {
                // Handle Purchase Order - use standard ERPNext method
                erpnext.utils.map_current_doc({
                    method: 'erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt',
                    source_doctype: 'Purchase Order',
                    target: frm,
                    setters: {
                        supplier: frm.doc.supplier,
                        schedule_date: undefined,
                    },
                    get_query_filters: {
                        docstatus: 1,
                        status: ["not in", ["Closed", "On Hold"]],
                        per_received: ["<", 99.99],
                        company: frm.doc.company,
                    },
                });
                d.hide();
            } else if (source === 'Purchase Quotation') {
                // Handle Purchase Quotation - replicate Purchase Order behavior
                erpnext.utils.map_current_doc({
                    method: 'gate_pass.gate_pass_events.make_purchase_receipt_from_supplier_quotation',
                    source_doctype: 'Supplier Quotation',
                    target: frm,
                    setters: {
                        supplier: frm.doc.supplier,
                    },
                    get_query_filters: {
                        docstatus: 1,
                        supplier: frm.doc.supplier || '',
                    },
                });
                d.hide();
            }
        }
    });
    
    d.show();
}

function fetch_from_gate_inward(frm) {
    // Check if document is submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot fetch items on submitted document.'));
        return;
    }
    
    // Save document first if it's new
    if (frm.doc.__islocal) {
        frm.save('Update', function() {
            show_gate_inward_dialog(frm);
        });
    } else {
        show_gate_inward_dialog(frm);
    }
}

function show_gate_inward_dialog(frm) {
    // Check if supplier is selected
    if (!frm.doc.supplier) {
        frappe.msgprint(__('Please select a supplier first.'));
        return;
    }
    
    // Get available Gate Inwards for the supplier
    frappe.call({
        method: 'gate_pass.gate_pass_events.get_available_gate_inwards',
        args: {
            'supplier': frm.doc.supplier
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                show_gate_inward_selection_dialog(frm, r.message);
            } else {
                frappe.msgprint(__('No available Gate Inwards found for supplier {0}').format(frm.doc.supplier));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Error: {0}').format(r.message || 'Unknown error occurred'));
        }
    });
}

function show_gate_inward_selection_dialog(frm, gate_inwards) {
    // Create options for the dropdown
    let options = gate_inwards.map(function(gi) {
        return {
            label: gi.name + ' - ' + gi.creation_date + ' (' + gi.total_pending_qty + ' items)',
            value: gi.name
        };
    });
    
    // Show dialog to select Gate Inward
    let d = new frappe.ui.Dialog({
        title: __('Select Gate Inward for {0}').format(frm.doc.supplier),
        fields: [
            {
                fieldtype: 'Select',
                fieldname: 'gate_inward',
                label: __('Gate Inward'),
                options: options,
                reqd: 1
            }
        ],
        primary_action_label: __('Fetch Items'),
        primary_action: function() {
            let gate_inward = d.get_value('gate_inward');
            if (gate_inward) {
                frappe.call({
                    method: 'gate_pass.gate_pass_events.fetch_items_from_gate_inward',
                    args: {
                        'purchase_receipt': frm.doc.name,
                        'gate_inward': gate_inward
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.reload_doc();
                            frappe.msgprint(__('Items fetched from Gate Inward successfully'));
                        }
                    },
                    error: function(r) {
                        frappe.msgprint(__('Error: {0}').format(r.message || 'Unknown error occurred'));
                    }
                });
            }
            d.hide();
        }
    });
    d.show();
}

function create_gate_inward_from_pr(frm) {
    // Check if document is submitted
    if (frm.doc.docstatus === 1) {
        frappe.msgprint(__('Cannot create Gate Inward from submitted document.'));
        return;
    }
    
    // Save document first if it's new
    if (frm.doc.__islocal) {
        frm.save('Update', function() {
            create_gate_inward(frm);
        });
    } else {
        create_gate_inward(frm);
    }
}

function create_gate_inward(frm) {
    frappe.call({
        method: 'gate_pass.gate_pass_events.create_gate_inward_from_pr',
        args: {
            'purchase_receipt': frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frappe.msgprint(__('Gate Inward {0} created successfully').format(r.message));
            }
        },
        error: function(r) {
            frappe.msgprint(__('Error: {0}').format(r.message || 'Unknown error occurred'));
        }
    });
} 