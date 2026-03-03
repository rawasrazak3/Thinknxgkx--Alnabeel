
// Common function
function load_last_transactions(frm, item_code) {

    if (!item_code) return;

    frappe.call({
        method: "alnabeel.alnabeel.custom_scripts.item_transaction.get_last_transactions",
        args: { item_code: item_code },
        callback: function(r) {

            if (r.message) {

                frm.clear_table("custom_item_transaction_details");

                r.message.forEach(function(d) {

                    let child = frm.add_child("custom_item_transaction_details");

                    child.invoice = d.invoice;
                    child.supplier = d.supplier;
                    child.posting_date = d.posting_date;
                    child.project = d.project;
                    child.cost_center = d.cost_center;
                    child.qty = d.qty;
                    child.rate = d.rate;
                    child.amount = d.amount;
                    child.item_tax_template = d.item_tax_template;
                    child.valuation_rate = d.valuation_rate;
                    child.purchase_order = d.purchase_order;
                });

                frm.refresh_field("custom_item_transaction_details");
            }
        }
    });
}


// Purchase Order
frappe.ui.form.on('Purchase Order Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        load_last_transactions(frm, row.item_code);
    }
});

// Quotation
frappe.ui.form.on('Quotation Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        load_last_transactions(frm, row.item_code);
    }
});

// Sales Invoice
frappe.ui.form.on('Sales Invoice Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        load_last_transactions(frm, row.item_code);
    }
});
