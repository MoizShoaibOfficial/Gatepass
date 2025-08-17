from frappe import _


def get_data():
		return {
			"heatmap": True,
			"heatmap_message": _(
				"This is based on transactions against this Customer. See timeline below for details"
			),
			"fieldname": "customer_name",
			"non_standard_fieldnames": {
				"Outward Gate Pass":"customer_name"
			},
		# "dynamic_links": {"party_name": ["Customer", "quotation_to"]},
		"transactions": [
			{"label": _("Pre Sales"), "items": ["Opportunity", "Quotation"]},
			{"label": _("Customer"), "items": ["Customer"]},
		],
	}
