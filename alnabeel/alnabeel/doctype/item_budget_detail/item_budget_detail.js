// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Item Budget Detail", {

// 	item_code(frm, cdt, cdn) {
// 		let row = locals[cdt][cdn];
// 		if (!row.item_code) return;

// 		frappe.db.get_value("Item", row.item_code, [
// 			"valuation_rate",
// 			"expense_account"
// 		]).then(r => {
// 			if (r.message) {
// 				row.cost_price = r.message.valuation_rate || 0;
// 				row.account = r.message.expense_account || "";
// 				refresh_field("item_budget_detail");
// 			}
// 		});
// 	},

// 	budget_qty(frm, cdt, cdn) {
// 		calculate_rate(cdt, cdn);
// 	},

// 	budget_amount(frm, cdt, cdn) {
// 		calculate_rate(cdt, cdn);
// 	}
// });

// function calculate_rate(cdt, cdn) {
// 	let row = locals[cdt][cdn];

// 	if (row.budget_qty > 0 && row.budget_amount) {
// 		row.rate = flt(row.budget_amount) / flt(row.budget_qty);
// 	} else {
// 		row.rate = 0;
// 	}

// 	refresh_field("item_budget_detail");
// }

frappe.ui.form.on("Item Budget Detail", {

    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.item_code) return;

        frappe.db.get_value("Item", row.item_code, [
            "item_name",
            "expense_account",
            "valuation_rate"
        ]).then(r => {
            if (r.message) {
                frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                frappe.model.set_value(cdt, cdn, "account", r.message.expense_account);
                frappe.model.set_value(cdt, cdn, "cost_price", r.message.valuation_rate);
            }
        });
    },

    budget_qty: function(frm, cdt, cdn) {
        calculate_rate(cdt, cdn);
    },

    budget_amount: function(frm, cdt, cdn) {
        calculate_rate(cdt, cdn);
    }
});

function calculate_rate(cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.budget_qty > 0 && row.budget_amount > 0) {
        frappe.model.set_value(cdt, cdn, "rate", row.budget_amount / row.budget_qty);
    } else {
        frappe.model.set_value(cdt, cdn, "rate", 0);
    }
}
