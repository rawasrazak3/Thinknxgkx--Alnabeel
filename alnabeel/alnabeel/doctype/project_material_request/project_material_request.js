
// // frappe.ui.form.on("Project Material Request", {
// //     refresh(frm) {
// //         if (frm.is_new()) return;

// //         // Remove all buttons first
// //         frm.clear_custom_buttons();

// //         // 🔹 If PMR table NOT visible → show Create Material Request
// //         if (!frm.doc.show_pmr_table) {
// //             frm.add_custom_button(
// //                 __("Create Material Request"),
// //                 () => {
// //                     load_pmr_table(frm);
// //                 },
// //                 __("Actions")
// //             );
// //         }

// //         // 🔹 If PMR table IS visible → show Move to MR
// //         if (frm.doc.show_pmr_table) {
// //             frm.add_custom_button(
// //                 __("Move to MR"),
// //                 () => {
// //                     move_to_material_request(frm);
// //                 },
// //                 __("Actions")
// //             );
// //         }
// //     }
// // });



frappe.ui.form.on("Project Material Request", {
    refresh(frm) {
        if (frm.is_new()) return;

        frm.clear_custom_buttons();

        //  LOCK after MR creation
        if (frm.doc.mr_created) {
            frm.set_read_only(true);
            frappe.show_alert({
                message: __("Material Request already created. Document locked."),
                indicator: "green"
            });
            return;
        }

        // STEP 1: Header saved → Load PMR items
        if (!frm.doc.show_pmr_table) {
            frm.add_custom_button(
                __("Create Material Request"),
                () => load_pmr_table(frm)
            ).addClass("btn-primary");
        }

        // Add Select / Unselect buttons above PMR table
        if (frm.doc.show_pmr_table) {
            const grid = frm.get_field("pmr_items").grid;

            if (!grid.wrapper.find(".pmr-select-actions").length) {
                const html = `
                    <div class="pmr-select-actions" style="margin-bottom:10px;">
                        <button class="btn btn-sm btn-secondary pmr-select-all">
                            Select All
                        </button>
                        <button class="btn btn-sm btn-secondary pmr-unselect-all" style="margin-left:5px;">
                            Unselect All
                        </button>
                    </div>
                `;

                grid.wrapper.prepend(html);

                // Select All
                grid.wrapper.find(".pmr-select-all").on("click", () => {
                    (frm.doc.pmr_items || []).forEach(row => {
                        row.select_item = 1;
                    });
                    frm.refresh_field("pmr_items");
                });

                // Unselect All
                grid.wrapper.find(".pmr-unselect-all").on("click", () => {
                    (frm.doc.pmr_items || []).forEach(row => {
                        row.select_item = 0;
                    });
                    frm.refresh_field("pmr_items");
                });
            }
        }


        // STEP 2: PMR saved → Move to MR
        if (frm.doc.show_pmr_table && !frm.is_dirty()) {
            frm.add_custom_button(
                __("Move to MR"),
                () => move_to_material_request(frm)
            ).addClass("btn-primary");
        }
    }
});

//move to MR function
function move_to_material_request(frm) {
    let selected_items = (frm.doc.pmr_items || []).filter(
        row => row.select_item && flt(row.request_qty) > 0
    );

    if (!selected_items.length) {
        frappe.msgprint("Select at least one item and enter Request Qty.");
        return;
    }

    let invalid = selected_items.find(
        row => flt(row.request_qty) > flt(row.balance_qty)
    );

    if (invalid) {
        frappe.msgprint(
            `Request Qty for item ${invalid.item_code} cannot exceed Balance Qty (${invalid.balance_qty})`
        );
        return;
    }

    frappe.call({
        method: "alnabeel.alnabeel.doctype.project_material_request.project_material_request.create_material_request",
        args: { pmr_name: frm.doc.name },
        callback(r) {
            if (r.message) {
                frappe.set_route("Form", "Material Request", r.message);
            }
        }
    });
}

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
            if (!r.message || !r.message.length) {
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

            //  Button switches automatically
            frm.refresh();
        }
    });
}

