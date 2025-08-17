// Copyright (c) 2024, Mohtashim and contributors
// For license information, please see license.txt

frappe.ui.form.on('Outward Gate Pass', {
	refresh(frm) {
		// your code here
	}
})


frappe.ui.form.on('Outward Gate Pass', {
	refresh: function (frm) {
		// Modify the get_query_filters function
		frm.fields_dict['customer'].get_query = function (doc) {
			return {
				filters: {
					'disabled': 0 // Only fetch customers with 'disabled' set to 0 (not disabled)
				}
			};
		};
	}
});


frappe.ui.form.on('Outward Gate Pass', {
	refresh: function (frm) {
		// Modify the get_query_filters function
		frm.fields_dict['supplier'].get_query = function (doc) {
			return {
				filters: {
					'disabled': 0 // Only fetch customers with 'disabled' set to 0 (not disabled)
				}
			};
		};
	}
});



