
// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

frappe.ui.form.on("Quantity Budget", {
    // Onload of parent form
    onload: function(frm) {
        // Set default actions for budget exceeding
        frm.set_value("action_if_annual_budget_exceeded", "Warn");
        frm.set_value("action_if_accumulated_monthly_budget_exceeded_on_mr", "Stop");

        // Setup field filters similar to core Budget
        frm.set_query("account", "item_budget_detail", function() {
            return {
                filters: {
                    company: frm.doc.company,
                    report_type: "Profit and Loss",
                    is_group: 0
                }
            };
        });

        frm.set_query("monthly_distribution", function() {
            return {
                filters: {
                    fiscal_year: frm.doc.fiscal_year
                }
            };
        });

        // Setup ERPNext dimensions (Cost Center / Project / Department filters)
        if(erpnext && erpnext.accounts && erpnext.accounts.dimensions) {
            erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
        }
    },

    // On refresh of parent form
    refresh: function(frm) {
        frm.trigger("toggle_reqd_fields");
    },

    // Triggered when user changes "budget_against" field
    budget_against: function(frm) {
        frm.trigger("set_null_value");
        frm.trigger("toggle_reqd_fields");
    },

    // Clear the opposite field depending on Budget Against
    set_null_value: function(frm) {
        if(frm.doc.budget_against === "Cost Center") {
            frm.set_value("project", null);
        } else if(frm.doc.budget_against === "Project") {
            frm.set_value("cost_center", null);
        }
    },

    // Toggle required property for Cost Center / Project
    toggle_reqd_fields: function(frm) {
        frm.toggle_reqd("cost_center", frm.doc.budget_against === "Cost Center");
        frm.toggle_reqd("project", frm.doc.budget_against === "Project");
    },

    refresh(frm) {
        if (frm.doc.docstatus === 1 && !frm.doc.revised_budget) {
            frm.add_custom_button(
                __("Create Revised Budget"),
                () => {
                    frappe.call({
                        method: "alnabeel.alnabeel.doctype.quantity_budget.quantity_budget.create_revised_budget",
                        args: {
                            budget_name: frm.doc.name
                        },
                        callback(r) {
                            if (r.message) {
                                frappe.set_route("Form", "Quantity Budget", r.message);
                            }
                        }
                    });
                }
            );
        }
    },

});

// Child table triggers for Item Budget Detail
frappe.ui.form.on("Item Budget Detail", {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        // Auto-fill company from parent
        if (!row.company && frm.doc.company) {
            row.company = frm.doc.company;
        }

        // Auto-fill cost center / project
        if (!row.cost_center && frm.doc.budget_against == "Cost Center") {
            row.cost_center = frm.doc.cost_center;
        }
        if (!row.project && frm.doc.budget_against == "Project") {
            row.project = frm.doc.project;
        }

        // Fetch item details and cost price
        frappe.db.get_doc("Item", row.item_code).then(item => {
            row.item_name = item.item_name;
            row.cost_price = item.valuation_rate || 0;

            if (frm.doc.company) {
                frappe.db.get_value("Company", frm.doc.company, "default_expense_account")
                    .then(r => {
                        if (r.message && r.message.default_expense_account) {
                            row.account = r.message.default_expense_account;
                        }
                        frm.refresh_field("item_budget_detail");
                    });
            } else {
                frm.refresh_field("item_budget_detail");
            }
        });
    },

    budget_qty: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
        calculate_balance_qty(frm, cdt, cdn);
    },

    budget_rate: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },

    consumed_qty: function(frm, cdt, cdn) {
        calculate_balance_qty(frm, cdt, cdn);
    },


    revised_budget_qty(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.revised_budget_amount = flt(row.revised_budget_qty) * flt(row.revised_budget_rate);
        frm.refresh_field('item_budget_detail');
    },
    revised_budget_rate(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.revised_budget_amount = flt(row.revised_budget_qty) * flt(row.revised_budget_rate);
        frm.refresh_field('item_budget_detail');
    }
});

// Function to calculate budget amount
function calculate_budget_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
    frm.refresh_field("item_budget_detail");
}

// Function to calculate balance quantity
function calculate_balance_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.balance_qty = (row.budget_qty || 0) - (row.consumed_qty || 0);
    frm.refresh_field("item_budget_detail");
}

