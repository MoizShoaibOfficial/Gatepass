# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from frappe import _


def get_dashboard_for_employee(data):
	data["transactions"].extend(
		[
			{"label": _("Gate Pass"), "items": ["Outward Gate Pass", "Courier Gate Pass"]},
		]
	)
	return data
