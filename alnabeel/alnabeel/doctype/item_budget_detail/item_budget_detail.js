
// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt
frappe.ui.form.on("Item Budget Detail", {
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        // set company silently
        if (!row.company && frm.doc.company) {
            row.company = frm.doc.company;
        }

        // Fetch Item details
        frappe.db.get_doc("Item", row.item_code).then(item => {
            row.item_name = item.item_name;
            row.cost_price = item.valuation_rate || 0;

            // Fetch default expense account from Company
            if (frm.doc.company) {
                frappe.db.get_value(
                    "Company",
                    frm.doc.company,
                    "default_expense_account"
                ).then(r => {
                    row.account = r.message.default_expense_account;
                    frm.refresh_field("item_budget_detail");
                });
            }

            frm.refresh_field("item_budget_detail");
        });
    },

    // when budget qty changes
    budget_qty(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
        calculate_balance_qty(frm, cdt, cdn);   
    },

    budget_rate(frm, cdt, cdn) {
        calculate_budget_amount(frm, cdt, cdn);
    },

    // when consumed qty changes (from backend / manual)
    consumed_qty(frm, cdt, cdn) {
        calculate_balance_qty(frm, cdt, cdn);   
    }
});

// Existing function (unchanged)
function calculate_budget_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.budget_amount = (row.budget_qty || 0) * (row.budget_rate || 0);
    frm.refresh_field("item_budget_detail");
}

//  balance qty calculation
function calculate_balance_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let budget_qty = row.budget_qty || 0;
    let revised_budget_qty = row.revised_budget_qty || 0;
    let consumed_qty = row.consumed_qty || 0;

    row.balance_qty = (budget_qty + revised_budget_qty) - consumed_qty;

    frm.refresh_field("item_budget_detail");
}