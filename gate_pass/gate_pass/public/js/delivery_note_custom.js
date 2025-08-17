// Copyright (c) 2025, Gate Pass and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        // Add custom button to fetch from Gate Outward
        frm.add_custom_button(__('Fetch from Gate Outward'), function() {
            fetch_from_gate_outward(frm);
        });
    }
});

function fetch_from_gate_outward(frm) {
    // Show dialog to select Gate Outward
    let d = new frappe.ui.Dialog({
        title: __('Select Gate Outward'),
        fields: [
            {
                fieldtype: 'Link',
                fieldname: 'gate_outward',
                label: __('Gate Outward'),
                options: 'Gate Outward',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'docstatus': 1,
                            'gate_outward_type': 'Delivery Note'
                        }
                    };
                }
            }
        ],
        primary_action_label: __('Fetch Items'),
        primary_action: function() {
            let gate_outward = d.get_value('gate_outward');
            if (gate_outward) {
                frappe.call({
                    method: 'gate_pass.gate_pass_events.fetch_items_from_gate_outward',
                    args: {
                        'delivery_note': frm.doc.name,
                        'gate_outward': gate_outward
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.reload_doc();
                            frappe.msgprint(__('Items fetched from Gate Outward successfully'));
                        }
                    }
                });
            }
            d.hide();
        }
    });
    d.show();
} 