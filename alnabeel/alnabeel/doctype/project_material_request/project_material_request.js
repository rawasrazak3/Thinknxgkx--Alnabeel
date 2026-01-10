
// frappe.ui.form.on("Project Material Request", {
//     refresh(frm) {
//         // Button appears ONLY after save
//         if (!frm.is_new()) {
//             frm.add_custom_button(
//                 __("Create Material Request"),
//                 () => {
//                     load_pmr_table(frm);
//                 },
//                 __("Actions")
//             );
//         }
//     }
// });

// //load PMR Table from quantity budget
// function load_pmr_table(frm) {
//     if (!frm.doc.project || !frm.doc.warehouse) {
//         frappe.msgprint("Please fill Project and Warehouse");
//         return;
//     }

//     frappe.call({
//         method: "alnabeel.alnabeel.doctype.project_material_request.project_material_request.get_items_from_quantity_budget",
//         args: {
//             project: frm.doc.project
//         },
//         callback(r) {
//             if (!r.message || r.message.length === 0) {
//                 frappe.msgprint("No Quantity Budget found for this Project");
//                 return;
//             }

//             frm.clear_table("pmr_items");

//             r.message.forEach(d => {
//                 let row = frm.add_child("pmr_items");
//                 row.select_item = 1;
//                 row.item_code = d.item_code;
//                 row.item_name = d.item_name;
//                 row.budget_qty = d.budget_qty;
//                 row.consumed_qty = d.consumed_qty;
//                 row.balance_qty = d.balance_qty;
//             });

//             frm.set_value("show_pmr_table", 1);
//             frm.refresh_field("pmr_items");
//         }
//     });
// }


frappe.ui.form.on("Project Material Request", {
    refresh(frm) {
        // Button appears ONLY after save
        if (!frm.is_new()) {
            // Existing "Create Material Request" button
            frm.add_custom_button(
                __("Create Material Request"),
                () => {
                    load_pmr_table(frm);
                },
                __("Actions")
            );

            // New "Move to MR" button
            frm.add_custom_button(
                __("Move to MR"),
                () => {
                    // Filter only selected items with request_qty > 0
                    let selected_items = frm.doc.pmr_items.filter(row => row.select_item && flt(row.request_qty) > 0);

                    if (!selected_items.length) {
                        frappe.msgprint("Select at least one item and enter Request Qty.");
                        return;
                    }

                    // Validation: request_qty should not exceed balance_qty
                    let invalid_item = selected_items.find(row => flt(row.request_qty) > flt(row.balance_qty));
                    if (invalid_item) {
                        frappe.msgprint(`Request Qty for item ${invalid_item.item_code} cannot exceed Balance Qty (${invalid_item.balance_qty})`);
                        return;
                    }

                    // Call server-side method to create Material Request
                    frappe.call({
                        method: "alnabeel.alnabeel.doctype.project_material_request.project_material_request.create_material_request",
                        args: { pmr_name: frm.doc.name },
                        callback(r) {
                            if (r.message) {
                                frappe.set_route("Form", "Material Request", r.message);
                            }
                        }
                    });
                },
                __("Actions") // place next to Actions
            );
        }
    }
});

//load PMR Table from quantity budget
function load_pmr_table(frm) {
    if (!frm.doc.project || !frm.doc.warehouse) {
        frappe.msgprint("Please fill Project and Warehouse");
        return;
    }

    frappe.call({
        method: "alnabeel.alnabeel.doctype.project_material_request.project_material_request.get_items_from_quantity_budget",
        args: {
            project: frm.doc.project
        },
        callback(r) {
            if (!r.message || r.message.length === 0) {
                frappe.msgprint("No Quantity Budget found for this Project");
                return;
            }

            frm.clear_table("pmr_items");

            r.message.forEach(d => {
                let row = frm.add_child("pmr_items");
                row.select_item = 1;
                row.item_code = d.item_code;
                row.item_name = d.item_name;
                row.budget_qty = d.budget_qty;
                row.consumed_qty = d.consumed_qty;
                row.balance_qty = d.balance_qty;
            });

            frm.set_value("show_pmr_table", 1);
            frm.refresh_field("pmr_items");
        }
    });
}

