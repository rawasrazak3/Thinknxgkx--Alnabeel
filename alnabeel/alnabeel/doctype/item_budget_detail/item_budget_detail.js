// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Item Budget Detail", {
//     item_code(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         if (!row.item_code) return;

// 		 // set company silently
//         if (!row.company && frm.doc.company) {
//             row.company = frm.doc.company;
//         }

//          // Autofill Cost Center / Project from parent Quantity Budget
//         if(frm.doc.budget_against == "Cost Center") {
//             row.cost_center = frm.doc.cost_center;
//         } else if(frm.doc.budget_against == "Project") {
//             row.project = frm.doc.project;
//         }

//         // Fetch Item details
//         frappe.db.get_doc("Item", row.item_code).then(item => {
//             row.item_name = item.item_name;
//             row.cost_price = item.valuation_rate || 0;

//             // Fetch default expense account from Company
//             if (frm.doc.company) {
//                 frappe.db.get_value(
//                     "Company",
//                     frm.doc.company,
//                     "default_expense_account"
//                 ).then(r => {
//                     row.account = r.message.default_expense_account;
//                     frm.refresh_field("item_budget_detail");
//                 });
//             }

//             frm.refresh_field("item_budget_detail");
//         });
//     },

//     budget_qty(frm, cdt, cdn) {
//         calculate_budget_amount(frm, cdt, cdn);
//     },

//     budget_rate(frm, cdt, cdn) {
//         calculate_budget_amount(frm, cdt, cdn);
//     }
// });

// function calculate_budget_amount(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];
//     row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
//     frm.refresh_field("item_budget_detail");
// }



frappe.ui.form.on("Item Budget Detail", {
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        // Set company from parent
        if (!row.company && frm.doc.company) {
            row.company = frm.doc.company;
        }

        // Autofill Cost Center / Project from parent
        if (!row.cost_center && frm.doc.budget_against == "Cost Center") {
            row.cost_center = frm.doc.cost_center;
        }
        if (!row.project && frm.doc.budget_against == "Project") {
            row.project = frm.doc.project;
        }

        // Fetch Item details
        frappe.db.get_doc("Item", row.item_code).then(item => {
            row.item_name = item.item_name;
            row.cost_price = item.valuation_rate || 0;

            if (frm.doc.company) {
                frappe.db.get_value("Company", frm.doc.company, "default_expense_account")
                .then(r => {
                    if (r.message && r.message.default_expense_account) {
                        row.account = r.message.default_expense_account;
                    }
                    frm.refresh_field("item_budget_detail"); // Refresh once at the end
                });
            } else {
                frm.refresh_field("item_budget_detail"); // Refresh if no company
            }
        });
    },

    budget_qty(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },

    budget_rate(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    }
});

function calculate_budget_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
    frm.refresh_field("item_budget_detail");
}
