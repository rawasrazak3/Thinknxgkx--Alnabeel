// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Quantity Budget", {
// 	refresh(frm) {

// 	},
// });
// Copyright (c) 2016, Frappe Technologies Pvt. Ltd.
// For license information, please see license.txt

frappe.provide("erpnext.accounts.dimensions");

frappe.ui.form.on("Quantity Budget", {
	onload: function (frm) {

		// Monthly Distribution filter (same as Budget)
		frm.set_query("monthly_distribution", function () {
			return {
				filters: {
					fiscal_year: frm.doc.fiscal_year,
				},
			};
		});

		// Setup Accounting Dimensions (Cost Center, Project, etc.)
		erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
	},

	refresh: function (frm) {
		frm.trigger("toggle_reqd_fields");
	},

	budget_against: function (frm) {
		frm.trigger("set_null_value");
		frm.trigger("toggle_reqd_fields");
	},

	set_null_value: function (frm) {
		if (frm.doc.budget_against === "Cost Center") {
			frm.set_value("project", null);
		} else if (frm.doc.budget_against === "Project") {
			frm.set_value("cost_center", null);
		}
	},

	toggle_reqd_fields: function (frm) {
		frm.toggle_reqd("cost_center", frm.doc.budget_against === "Cost Center");
		frm.toggle_reqd("project", frm.doc.budget_against === "Project");
	},
});


frappe.ui.form.on("Item Budget Detail", {
	budget_qty(frm, cdt, cdn) {
		calc_rate(frm, cdt, cdn);
	},
	budget_amount(frm, cdt, cdn) {
		calc_rate(frm, cdt, cdn);
	},
});

function calc_rate(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	if (row.budget_qty > 0) {
		frappe.model.set_value(
			cdt,
			cdn,
			"rate",
			row.budget_amount / row.budget_qty
		);
	}
}

