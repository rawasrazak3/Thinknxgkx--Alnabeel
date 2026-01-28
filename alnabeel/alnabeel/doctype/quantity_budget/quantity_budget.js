// // Copyright (c) 2026, krishna and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Quantity Budget", {
//     // Onload of parent form
//     onload: function(frm) {
//         // Set default actions for budget exceeding
//         frm.set_value("action_if_annual_budget_exceeded", "Warn");
//         frm.set_value("action_if_accumulated_monthly_budget_exceeded_on_mr", "Stop");

//         // Setup field filters similar to core Budget
//         frm.set_query("account", "item_budget_detail", function() {
//             return {
//                 filters: {
//                     company: frm.doc.company,
//                     report_type: "Profit and Loss",
//                     is_group: 0
//                 }
//             };
//         });

//         frm.set_query("monthly_distribution", function() {
//             return {
//                 filters: {
//                     fiscal_year: frm.doc.fiscal_year
//                 }
//             };
//         });

//         // Setup ERPNext dimensions (Cost Center / Project / Department filters)
//         if(erpnext && erpnext.accounts && erpnext.accounts.dimensions) {
//             erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
//         }
//     },

//     // On refresh of parent form
//     refresh: function(frm) {
//         frm.trigger("toggle_reqd_fields");
//     },

//     // Triggered when user changes "budget_against" field
//     budget_against: function(frm) {
//         frm.trigger("set_null_value");
//         frm.trigger("toggle_reqd_fields");
//     },

//     // Clear the opposite field depending on Budget Against
//     set_null_value: function(frm) {
//         if(frm.doc.budget_against === "Cost Center") {
//             frm.set_value("project", null);
//         } else if(frm.doc.budget_against === "Project") {
//             frm.set_value("cost_center", null);
//         }
//     },

//     // Toggle required property for Cost Center / Project
//     toggle_reqd_fields: function(frm) {
//         frm.toggle_reqd("cost_center", frm.doc.budget_against === "Cost Center");
//         frm.toggle_reqd("project", frm.doc.budget_against === "Project");
//     }
// });

// // Child table triggers for item calculations
// frappe.ui.form.on("Item Budget Detail", {
//     budget_qty: function(frm, cdt, cdn) {
//         calculate_budget_amount(frm, cdt, cdn);
//     },
//     budget_rate: function(frm, cdt, cdn) {
//         calculate_budget_amount(frm, cdt, cdn);
//     }
// });
// // Function to calculate Budget Amount per row
// function calculate_budget_amount(frm, cdt, cdn) {
//     const row = locals[cdt][cdn];
//     row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
//     frm.refresh_field("item_budget_detail");
// }

frappe.ui.form.on("Quantity Budget", {
    onload: function(frm) {
        frm.set_value("action_if_annual_budget_exceeded", "Warn");
        frm.set_value("action_if_accumulated_monthly_budget_exceeded_on_mr", "Stop");

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

        if(erpnext && erpnext.accounts && erpnext.accounts.dimensions) {
            erpnext.accounts.dimensions.setup_dimension_filters(frm, frm.doctype);
        }
    },

    refresh: function(frm) {
        frm.trigger("toggle_reqd_fields");

        // Recalculate budget amounts for all child rows
        frm.doc.item_budget_detail.forEach(row => {
            calculate_budget_amount(frm, row.doctype, row.name);
        });
    },

    budget_against: function(frm) {
        frm.trigger("set_null_value");
        frm.trigger("toggle_reqd_fields");
    },

    set_null_value: function(frm) {
        if(frm.doc.budget_against === "Cost Center") {
            frm.set_value("project", null);
        } else if(frm.doc.budget_against === "Project") {
            frm.set_value("cost_center", null);
        }
    },

    toggle_reqd_fields: function(frm) {
        frm.toggle_reqd("cost_center", frm.doc.budget_against === "Cost Center");
        frm.toggle_reqd("project", frm.doc.budget_against === "Project");
    }
});

// Child table triggers for item calculations
frappe.ui.form.on("Item Budget Detail", {
    budget_qty: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },
    budget_rate: function(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    }
});

// Function to calculate Budget Amount per row
function calculate_budget_amount(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
    frm.refresh_field("item_budget_detail");
}
