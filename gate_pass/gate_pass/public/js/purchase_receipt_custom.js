// Copyright (c) 2025, Gate Pass and contributors
// For license information, please see license.txt

console.log('Purchase Receipt Custom JS loaded successfully!');

frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        console.log('Purchase Receipt form refreshed!');
        
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
        console.log('Adding custom buttons to Purchase Receipt form');
        // Only add our custom Get Items From button (replaces the original)
        if (frm.doc.docstatus == 0) {
            console.log('Adding Get Items From button');
            frm.add_custom_button(
                __("Get Items From"),
                function() {
                    console.log('Get Items From button clicked!');
                    show_get_items_from_dialog(frm);
                }
            );
        }
    }
});

function show_get_items_from_dialog(frm) {
    console.log('show_get_items_from_dialog called');
    console.log('Supplier:', frm.doc.supplier);
    
    // Check if supplier is selected
    if (!frm.doc.supplier) {
        console.log('No supplier selected');
        frappe.msgprint(__('Please select a supplier first before getting items.'));
        return;
    }
    
    console.log('Creating Get Items From dialog');
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
                default: 'Purchase Order',
                onchange: function() {
                    // Clear the source_name field when source changes
                    d.set_value('source_name', '');
                    
                    // Update the source_name field options based on selected source
                    let source = d.get_value('source');
                    let source_name_field = d.get_field('source_name');
                    
                    if (source === 'Gate Inward') {
                        source_name_field.df.options = 'Gate Inward';
                        source_name_field.df.filters = {
                            'docstatus': 1
                        };
                    } else if (source === 'Purchase Order') {
                        source_name_field.df.options = 'Purchase Order';
                        source_name_field.df.filters = {
                            'docstatus': 1,
                            'supplier': frm.doc.supplier || '',
                            'status': ['not in', ['Closed', 'On Hold']],
                            'per_received': ['<', 99.99]
                        };
                    } else if (source === 'Purchase Quotation') {
                        source_name_field.df.options = 'Supplier Quotation';
                        source_name_field.df.filters = {
                            'docstatus': 1,
                            'supplier': frm.doc.supplier || ''
                        };
                    }
                    
                    // Refresh the field to update the options and clear the value
                    source_name_field.set_value('');
                    source_name_field.refresh();
                }
            },
            {
                fieldtype: 'Link',
                fieldname: 'source_name',
                label: __('Source Name'),
                reqd: 1,
                options: 'Purchase Order',
                filters: {
                    'docstatus': 1,
                    'supplier': frm.doc.supplier || '',
                    'status': ['not in', ['Closed', 'On Hold']],
                    'per_received': ['<', 99.99]
                },
                description: __('Select the source document to fetch items from')
            }
        ],
        primary_action_label: __('Get Items'),
        primary_action: function() {
            console.log('Get Items button clicked in dialog');
            let source = d.get_value('source');
            let source_name = d.get_value('source_name');
            
            console.log('Source:', source);
            console.log('Source Name:', source_name);
            
            if (!source_name) {
                console.log('No source name selected');
                frappe.msgprint(__('Please select a source document.'));
                return;
            }
            
            console.log('About to fetch items directly...');
            console.log('Document is local:', frm.doc.__islocal);
            console.log('Document name:', frm.doc.name);
            
            // Fetch items directly without saving first
            fetch_items_from_source(frm, source, source_name, d);
        }
    });
    
    console.log('Dialog created, showing it now');
    d.show();
    console.log('Dialog should be visible now');
}

function fetch_items_from_source(frm, source, source_name, d) {
    console.log('fetch_items_from_source called');
    console.log('Source:', source);
    console.log('Source Name:', source_name);
    console.log('Form name:', frm.doc.name);
    
    if (source === 'Gate Inward') {
        // Handle Gate Inward
        frappe.call({
            method: 'gate_pass.gate_pass_events.fetch_items_from_gate_inward_via_get_items',
            args: {
                'purchase_receipt': frm.doc.name,
                'gate_inward': source_name
            },
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                    frappe.msgprint(__('Items fetched from Gate Inward successfully'));
                }
            },
            error: function(r) {
                let errorMsg = 'Unknown error occurred';
                if (r.message) {
                    errorMsg = r.message;
                } else if (r.exc) {
                    errorMsg = r.exc;
                } else if (r.responseJSON && r.responseJSON._server_messages) {
                    try {
                        let serverMessages = JSON.parse(r.responseJSON._server_messages);
                        if (serverMessages.length > 0) {
                            errorMsg = serverMessages[0];
                        }
                    } catch (e) {
                        errorMsg = r.responseJSON._server_messages;
                    }
                }
                frappe.msgprint(__('Error: {0}').format(errorMsg));
            }
        });
        d.hide();
    } else if (source === 'Purchase Order') {
        // Handle Purchase Order - use our new method that works with form data
        console.log('Fetching items from Purchase Order:', source_name);
        console.log('Purchase Receipt:', frm.doc.name);
        
        frappe.call({
            method: 'gate_pass.gate_pass_events.fetch_items_from_purchase_order_for_form',
            args: {
                'purchase_receipt_name': frm.doc.name,
                'purchase_order': source_name
            },
            callback: function(r) {
                console.log('Fetch items response:', r);
                
                if (r.message && r.message.status === 'success') {
                    console.log('Items fetched successfully, adding to form...');
                    
                    // Set supplier if not already set
                    if (r.message.supplier && !frm.doc.supplier) {
                        frm.set_value('supplier', r.message.supplier);
                    }
                    
                    // Clear existing items
                    frm.clear_table('items');
                    
                    // Add new items to the form
                    if (r.message.items && r.message.items.length > 0) {
                        r.message.items.forEach(function(item) {
                            let row = frm.add_child('items');
                            row.item_code = item.item_code;
                            row.item_name = item.item_name;
                            row.description = item.description;
                            row.qty = item.qty;
                            row.received_qty = item.received_qty;
                            row.uom = item.uom;
                            row.stock_uom = item.stock_uom;
                            row.conversion_factor = item.conversion_factor;
                            row.warehouse = item.warehouse;
                            row.rate = item.rate;
                            row.base_rate = item.base_rate;
                            row.amount = item.amount;
                            row.base_amount = item.base_amount;
                            row.purchase_order = item.purchase_order;
                            row.purchase_order_item = item.purchase_order_item;
                        });
                        
                        // Refresh the items table
                        frm.refresh_field('items');
                        console.log(`Added ${r.message.items.length} items to the form`);
                        frappe.msgprint(__('Items fetched from Purchase Order successfully'));
                    } else {
                        frappe.msgprint(__('No items were fetched. Please check if the Purchase Order has items to receive.'));
                    }
                } else {
                    console.log('Error fetching items:', r.message);
                    let errorMsg = r.message && r.message.message ? r.message.message : 'Unknown error occurred';
                    frappe.msgprint(__('Error: {0}').format(errorMsg));
                }
            },
            error: function(r) {
                console.log('Error response:', r);
                let errorMsg = 'Unknown error occurred';
                if (r.message) {
                    errorMsg = r.message;
                } else if (r.exc) {
                    errorMsg = r.exc;
                } else if (r.responseJSON && r.responseJSON._server_messages) {
                    try {
                        let serverMessages = JSON.parse(r.responseJSON._server_messages);
                        if (serverMessages.length > 0) {
                            errorMsg = serverMessages[0];
                        }
                    } catch (e) {
                        errorMsg = r.responseJSON._server_messages;
                    }
                }
                frappe.msgprint(__('Error: {0}').format(errorMsg));
            }
        });
        d.hide();
    } else if (source === 'Purchase Quotation') {
        // Handle Purchase Quotation
        frappe.call({
            method: 'gate_pass.gate_pass_events.fetch_items_from_supplier_quotation',
            args: {
                'purchase_receipt': frm.doc.name,
                'supplier_quotation': source_name
            },
            callback: function(r) {
                if (r.message) {
                    frm.reload_doc();
                    frappe.msgprint(__('Items fetched from Purchase Quotation successfully'));
                }
            },
            error: function(r) {
                let errorMsg = 'Unknown error occurred';
                if (r.message) {
                    errorMsg = r.message;
                } else if (r.exc) {
                    errorMsg = r.exc;
                } else if (r.responseJSON && r.responseJSON._server_messages) {
                    try {
                        let serverMessages = JSON.parse(r.responseJSON._server_messages);
                        if (serverMessages.length > 0) {
                            errorMsg = serverMessages[0];
                        }
                    } catch (e) {
                        errorMsg = r.responseJSON._server_messages;
                    }
                }
                frappe.msgprint(__('Error: {0}').format(errorMsg));
            }
        });
        d.hide();
    }
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
    // if (!frm.doc.supplier) {
    //     frappe.msgprint(__('Please select a supplier first.'));
    //     return;
    // }
    
    // Get available Gate Inwards for the supplier
    frappe.call({
        method: 'gate_pass.gate_pass_events.get_available_gate_inwards',
        args: {
            // 'supplier': frm.doc.supplier
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                show_gate_inward_selection_dialog(frm, r.message);
            } else {
                frappe.msgprint(__('No available Gate Inwards found for supplier {0}').format(frm.doc.supplier));
            }
        },
        error: function(r) {
            let errorMsg = 'Unknown error occurred';
            if (r.message) {
                errorMsg = r.message;
            } else if (r.exc) {
                errorMsg = r.exc;
            } else if (r.responseJSON && r.responseJSON._server_messages) {
                try {
                    let serverMessages = JSON.parse(r.responseJSON._server_messages);
                    if (serverMessages.length > 0) {
                        errorMsg = serverMessages[0];
                    }
                } catch (e) {
                    errorMsg = r.responseJSON._server_messages;
                }
            }
            frappe.msgprint(__('Error: {0}').format(errorMsg));
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
                        let errorMsg = 'Unknown error occurred';
                        if (r.message) {
                            errorMsg = r.message;
                        } else if (r.exc) {
                            errorMsg = r.exc;
                        } else if (r.responseJSON && r.responseJSON._server_messages) {
                            try {
                                let serverMessages = JSON.parse(r.responseJSON._server_messages);
                                if (serverMessages.length > 0) {
                                    errorMsg = serverMessages[0];
                                }
                            } catch (e) {
                                errorMsg = r.responseJSON._server_messages;
                            }
                        }
                        frappe.msgprint(__('Error: {0}').format(errorMsg));
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
            let errorMsg = 'Unknown error occurred';
            if (r.message) {
                errorMsg = r.message;
            } else if (r.exc) {
                errorMsg = r.exc;
            } else if (r.responseJSON && r.responseJSON._server_messages) {
                try {
                    let serverMessages = JSON.parse(r.responseJSON._server_messages);
                    if (serverMessages.length > 0) {
                        errorMsg = serverMessages[0];
                    }
                } catch (e) {
                    errorMsg = r.responseJSON._server_messages;
                }
            }
            frappe.msgprint(__('Error: {0}').format(errorMsg));
        }
    });
} 