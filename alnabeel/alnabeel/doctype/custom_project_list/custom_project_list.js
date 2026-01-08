// // Copyright (c) 2026, krishna and contributors
// // For license information, please see license.txt

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

// ----------------------------------------------------
// MATERIAL REQUEST CREATION FROM PROJECT LIST
// ----------------------------------------------------

frappe.ui.form.on("Custom Project List", {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Material Request'), function() {
                open_material_request_popup(frm);
            });
        }
    }
});

function open_material_request_popup(frm) {
    let data = frm.doc.item_budget_detail.map(d => ({
        selected: 0,
        item_code: d.item_code,
        balance_qty: flt(d.budget_qty) - flt(d.consumed_qty),
        requested_qty: 0
    }));

    let d = new frappe.ui.Dialog({
        title: __('Create Material Request'),
        fields: [
            {
                fieldname: 'items',
                fieldtype: 'Table',
                label: 'Items',
                cannot_add_rows: true,
                in_place_edit: true,
                data: data,
                fields: [
                    { fieldname: 'selected', fieldtype: 'Check', label: 'Select' },
                    { fieldname: 'item_code', fieldtype: 'Data', label: 'Item', read_only: 1 },
                    { fieldname: 'balance_qty', fieldtype: 'Float', label: 'Balance Qty', read_only: 1 },
                    { fieldname: 'requested_qty', fieldtype: 'Float', label: 'Requested Qty' }
                ]
            }
        ],
        primary_action_label: __('Create MR'),
        primary_action(values) {
            const selected_items = values.items.filter(i => i.selected && i.requested_qty > 0);
            if (!selected_items.length) {
                frappe.throw(__('Please select at least one item with quantity'));
            }

            frappe.call({
                method: 'your_app.custom_project_list.create_material_request',
                args: {
                    project: frm.doc.name,
                    items: selected_items
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint(__('Material Request Created: {0}', [r.message]));
                        d.hide();
                        frm.reload_doc();
                    }
                }
            });
        }
    });

    d.show();
}
