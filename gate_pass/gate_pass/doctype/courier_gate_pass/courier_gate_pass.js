// Copyright (c) 2024, Mohtashim and contributors
// For license information, please see license.txt


frappe.ui.form.on("Courier Gate Pass", "onload", function (frm) {
    frm.set_value("currency", "USD");
});
frappe.ui.form.on("Courier Gate Pass", "onload", function (frm) {
    frm.set_query("courier_supplier", function () {
        return {
            "filters": {
                "supplier_group": "Courier Services"
            }
        };
    });
});


frappe.ui.form.on("Courier Gate Pass CT", {

    qty: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        calc(frm, cdt, cdn);
        set_cur(frm, cdt, cdn);
    },
    price: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        calc(frm, cdt, cdn);
        set_cur(frm, cdt, cdn);
    },
    discription_of_goods: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];

        set_cur(frm, cdt, cdn);
    },



});

function set_cur(frm, cdt, cdn) {
    var d = locals[cdt][cdn];


    frappe.model.set_value(d.doctype, d.name, 'currency', "USD");


}



function calc(frm, cdt, cdn) {
    var d = locals[cdt][cdn];


    frappe.model.set_value(d.doctype, d.name, 'amount', d.qty * d.price);


}


frappe.ui.form.on("Courier Gate Pass CT", {
    qty: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_qty = 0;
        frm.doc.courier_gate_pass_ct.forEach(function (d) { total_qty += d.qty; });
        frm.set_value("total_qty", total_qty);
        refresh_field('total_qty');
    },
    items_remove: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_qty = 0;
        frm.doc.courier_gate_pass_ct.forEach(function (d) { total_qty += d.qty; });
        frm.set_value('total_qty', total_qty);
        refresh_field('total_qty');
    }

});



frappe.ui.form.on('Courier Gate Pass CT', {
    amount: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_amount = 0;
        frm.doc.courier_gate_pass_ct.forEach(function (d) {
            total_amount += d.amount;
        });
        frm.set_value('total_amount', total_amount);
        refresh_field('total_amount');
    },
    items_remove: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_amount = 0;
        frm.doc.courier_gate_pass_ct.forEach(function (d) { total_amount += d.amount; });
        frm.set_value('total_amount', total_amount);
        refresh_field('total_amount');
    }
});




frappe.ui.form.on('Courier Gate Pass', {
    packet: function (frm) {
        frm.clear_table('dimensions');

        for (var i = 0; i < frm.doc.packet; i++) {
            var row = frappe.model.add_child(frm.doc, 'Dimensions', 'dimensions');
            row.packet = i + 1;
        }

        frm.refresh_field('dimensions');
    }
});
frappe.ui.form.on('Dimensions', {
    weight: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_weight = 0;
        frm.doc.dimensions.forEach(function (d) {
            total_weight += d.weight;
        });
        frm.set_value('total_weight', total_weight);
        refresh_field('total_weight');
    },
    items_remove: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_weight = 0;
        frm.doc.dimensions.forEach(function (d) { total_weight += d.weight; });
        frm.set_value('total_weight', total_weight);
        refresh_field('total_weight');
    }
});

frappe.ui.form.on("Dimensions", {
    dimensions: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        set_weight(frm, cdt, cdn);
    }


});


function set_weight(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    var length = d.l;
    var width = d.w;
    var hight = d.h;
    var weight = (length * width * hight) / 5000;
    frappe.model.set_value(d.doctype, d.name, 'weight', weight);

}

frappe.ui.form.on('Courier Gate Pass', {
    next_to_shipping: function (frm) {
        frm.page.set_primary_action(__('Next'), function () {
            frm.set_value("shipping_details_tab", "Shipping Details"); 
        });
    }
});




// frappe.ui.form.on("Courier Gate Pass", "refresh", function (frm) {



// });



frappe.ui.form.on('Courier Gate Pass', {
    refresh
    : function (frm) {
        frm.fields_dict['supplier'].get_query = function (doc) {
            return {
                filters: {
                    'disabled': 0 
                }
            };
        };
    }
});


frappe.ui.form.on('Courier Gate Pass', {
    refresh: function (frm) {
        frm.fields_dict['customer'].get_query = function (doc) {
            return {
                filters: {
                    'disabled': 0 
                }
            };
        };
    }
});




frappe.ui.form.on("Courier Gate Pass", "refresh", function (frm) {
    frm.fields_dict['courier_bank_information'].grid.get_field('sales_order').get_query = function (doc, cdt, cdn) {

        var child = locals[cdt][cdn];
        return {
            filters: [
                ['customer', '=', doc.customer]
            ]
        }
    }
});


frappe.ui.form.on('Courier Gate Pass', {
    no_of_packages: function (frm) {
        let no_of_packages = frm.doc.no_of_packages;
        let item_code = " ";

        if (!no_of_packages || no_of_packages <= 0) {
            frappe.msgprint(__('Please enter a valid number of rows.'));
            return;
        }

        frm.clear_table("dimensions");

        for (let i = 0; i < no_of_packages; i++) {
            let new_row = frm.add_child("dimensions");
            frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', item_code);
        }
        frm.refresh_field("dimensions");
    }
});


frappe.ui.form.on('Courier Gate Pass', {
    refresh: function (frm) {
        frm.set_df_property('dimensions', 'cannot_add_rows', true); 
    }
});

frappe.ui.form.on("Courier Gate Pass", "customer", function(frm) {
    frm.set_query("contact_link", function() {
        return {
            "filters": {
                "custom_customer": frm.doc.customer
            }
        };
    });
});

frappe.ui.form.on('Dimensions', { 
    l: calculate_and_set_weight,
    w: calculate_and_set_weight,
    h: calculate_and_set_weight
});

function calculate_and_set_weight(frm, cdt, cdn) {
    let d = locals[cdt][cdn];
    let weight = (d.l * d.w * d.h) / 5000;
    frappe.model.set_value(cdt, cdn, 'weight', weight);
}





frappe.ui.form.on("Courier Gate Pass", "onload", function(frm) {
    frm.set_query("contact", function() {
        return {
            filters: {
                custom_courier_contact: 1
            }
        };
    });
});


frappe.ui.form.on("Courier Gate Pass", "onload", function(frm) {
    frm.set_query("link_address", function() {
        if (frm.doc.out_to === "Supplier" && frm.doc.supplier) {
            return {
                filters: {
                    address_title: frm.doc.supplier
                }
            };
        } else if (frm.doc.customer && frm.doc.out_to === "Customer") {
            return {
                filters: {
                    address_title: frm.doc.customer
                }
            };
        } else {
            return {};
        }
    });
});



frappe.ui.form.on('Courier Gate Pass', {
    refresh(frm) {
        frm.set_query('contact_link', () => {
            if (frm.doc.out_to === 'Supplier' && frm.doc.supplier) {
                return {
                    filters: {
                        custom_supplier: frm.doc.supplier
                    }
                };
            } else {
                return {};
            }
        });
    }
});


frappe.ui.form.on('Courier Gate Pass', {
    refresh(frm) {
        frm.set_query('contact_link', () => {
            if (frm.doc.out_to === 'Supplier' && frm.doc.supplier) {
                return {
                    filters: {
                        custom_supplier: frm.doc.supplier
                    }
                };
            } else {
                return {};
            }
        });
    }
});


// weight calculation

frappe.ui.form.on('Courier Gate Pass', {
    refresh(frm) {
        // Example: frappe.msgprint('1');
    }
});


frappe.ui.form.on('Dimensions', { 
    l: calculate_and_set_weight,
    w: calculate_and_set_weight,
    h: calculate_and_set_weight
});

function calculate_and_set_weight(frm, cdt, cdn) {
    let d = locals[cdt][cdn];
    let weight = (d.l * d.w * d.h) / 5000;
    frappe.model.set_value(cdt, cdn, 'weight', weight);
}


// custom_courier_contact


frappe.ui.form.on("Courier Gate Pass", "onload", function(frm) {
    frm.set_query("contact", function() {
        return {
            filters: {
                custom_courier_contact: 1
            }
        };
    });
});

frappe.ui.form.on("Courier Gate Pass", "customer", function(frm) {
    frm.set_query("contact_link", function() {
        return {
            "filters": {
                "custom_customer": frm.doc.customer
            }
        };
    });
});


frappe.ui.form.on("Courier Gate Pass", "onload", function(frm) {
    frm.set_query("link_address", function() {
        return {
            "filters": {
                "address_title": frm.doc.customer
            }
        };
    });
});


// 



frappe.ui.form.on('Dimensions', { // Replace 'Dimension Item' with the actual DocType name of the child table
    l: calculate_and_set_weight,
    w: calculate_and_set_weight,
    h: calculate_and_set_weight
});

function calculate_and_set_weight(frm, cdt, cdn) {
    let d = locals[cdt][cdn];
    let weight = (d.l * d.w * d.h) / 5000;
    frappe.model.set_value(cdt, cdn, 'weight', weight);
}





frappe.ui.form.on("Courier Gate Pass", "onload", function(frm) {
    frm.set_query("contact", function() {
        return {
            filters: {
                custom_courier_contact: 1
            }
        };
    });
});
