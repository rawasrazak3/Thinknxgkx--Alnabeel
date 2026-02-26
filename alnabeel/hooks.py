app_name = "alnabeel"
app_title = "Alnabeel"
app_publisher = "krishna"
app_description = "alnabeel"
app_email = "kpriyapv20@gmail.com"
app_license = "mit"

doc_events = {
   
    "Material Request": {
        "on_submit": [
            "alnabeel.alnabeel.utils.daily_labour_attendance.lock_dla_after_mr",
            "alnabeel.alnabeel.utils.dla_mr.lock_dla_after_mr_saved",
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
           
        ],
        "on_cancel": [
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
        ],
        "validate": [ 
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.validate_material_request_budget",
            ],
       
    },

    "Purchase Order": {
        "on_submit": [
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",

        ],
        "on_cancel": [
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
    
        ],
        "validate": [ 
            "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.validate_purchase_order_budget",
             ],
    },

    "Purchase Invoice": {
    "on_submit": [
        "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
        ],

    "on_cancel": [
        "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
        ],

    "validate": [
        "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.validate_purchase_invoice_budget",
        ],
    },

    "Journal Entry": {
    "validate": "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.validate_journal_entry_budget",
    "on_submit": "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
    "on_cancel": "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.recalculate_from_doc",
    },

}



doctype_js = {
    "Payment Entry": "public/js/payment_entry.js",
    "Event": "public/js/event.js"
}

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "alnabeel",
# 		"logo": "/assets/alnabeel/logo.png",
# 		"title": "Alnabeel",
# 		"route": "/alnabeel",
# 		"has_permission": "alnabeel.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alnabeel/css/alnabeel.css"
# app_include_js = "/assets/alnabeel/js/alnabeel.js"

# include js, css files in header of web template
# web_include_css = "/assets/alnabeel/css/alnabeel.css"
# web_include_js = "/assets/alnabeel/js/alnabeel.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "alnabeel/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "alnabeel/public/icons.svg"

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
# 	"methods": "alnabeel.utils.jinja_methods",
# 	"filters": "alnabeel.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "alnabeel.install.before_install"
# after_install = "alnabeel.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "alnabeel.uninstall.before_uninstall"
# after_uninstall = "alnabeel.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "alnabeel.utils.before_app_install"
# after_app_install = "alnabeel.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "alnabeel.utils.before_app_uninstall"
# after_app_uninstall = "alnabeel.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alnabeel.notifications.get_notification_config"

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
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"alnabeel.tasks.all"
# 	],
# 	"daily": [
# 		"alnabeel.tasks.daily"
# 	],
# 	"hourly": [
# 		"alnabeel.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alnabeel.tasks.weekly"
# 	],
# 	"monthly": [
# 		"alnabeel.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "alnabeel.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alnabeel.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alnabeel.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["alnabeel.utils.before_request"]
# after_request = ["alnabeel.utils.after_request"]

# Job Events
# ----------
# before_job = ["alnabeel.utils.before_job"]
# after_job = ["alnabeel.utils.after_job"]

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
# 	"alnabeel.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
    {
        "doctype": "Custom Field", 
        "filters": [
            [
                "name",
                "in",
                [
                    "Project-custom_item_budget_detail",
                    "Event-custom_site_visit_plan",
                    "Event-custom_sales_person",
                    "Event-custom_year",
                    "Event-custom_column_break_n8yd8",
                    "Event-custom_month",
                    "Event-custom_site_visit_details",
                    "Event-custom_site_visit_detail"
                ]
            ]                         
        ]
}

]