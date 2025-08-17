app_name = "gate_pass"
app_title = "Gate Pass"
app_publisher = "Moiz"
app_description = "Made by Moiz"
app_email = "moizshoaib015@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "gate_pass",
# 		"logo": "/assets/gate_pass/logo.png",
# 		"title": "Gate Pass",
# 		"route": "/gate_pass",
# 		"has_permission": "gate_pass.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gate_pass/css/gate_pass.css"
# app_include_js = "/assets/gate_pass/js/gate_pass.js"

# include js, css files in header of web template
# web_include_css = "/assets/gate_pass/css/gate_pass.css"
# web_include_js = "/assets/gate_pass/js/gate_pass.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gate_pass/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Purchase Receipt" : "gate_pass/public/js/purchase_receipt_custom.js",
    "Delivery Note" : "gate_pass/public/js/delivery_note_custom.js",
    "Gate Inward" : "gate_pass/public/js/gate_inward_custom.js",
    "Gate Outward" : "gate_pass/public/js/gate_outward_custom.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gate_pass/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gate_pass.utils.jinja_methods",
# 	"filters": "gate_pass.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gate_pass.install.before_install"
# after_install = "gate_pass.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gate_pass.uninstall.before_uninstall"
# after_uninstall = "gate_pass.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gate_pass.utils.before_app_install"
# after_app_install = "gate_pass.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gate_pass.utils.before_app_uninstall"
# after_app_uninstall = "gate_pass.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gate_pass.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"Purchase Order": {
# 		"on_submit": "gate_pass.gate_pass_events.create_gate_inward_from_po",
# 		"on_cancel": "gate_pass.gate_pass_events.cancel_gate_inward_from_po"
# 	},
# 	"Delivery Note": {
# 		"on_submit": "gate_pass.gate_pass_events.create_gate_outward_from_dn",
# 		"on_cancel": "gate_pass.gate_pass_events.cancel_gate_outward_from_dn"
# 	},
# 	"Stock Entry": {
# 		"on_submit": "gate_pass.gate_pass_events.create_gate_pass_from_stock_entry",
# 		"on_cancel": "gate_pass.gate_pass_events.cancel_gate_pass_from_stock_entry"
# 	},
# 	"Purchase Receipt": {
# 		"on_submit": "gate_pass.gate_pass_events.update_gate_inward_from_pr",
# 		"on_cancel": "gate_pass.gate_pass_events.revert_gate_inward_from_pr"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"gate_pass.tasks.all"
# 	],
# 	"daily": [
# 		"gate_pass.tasks.daily"
# 	],
# 	"hourly": [
# 		"gate_pass.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gate_pass.tasks.weekly"
# 	],
# 	"monthly": [
# 		"gate_pass.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "gate_pass.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gate_pass.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gate_pass.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gate_pass.utils.before_request"]
# after_request = ["gate_pass.utils.after_request"]

# Job Events
# ----------
# before_job = ["gate_pass.utils.before_job"]
# after_job = ["gate_pass.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gate_pass.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

