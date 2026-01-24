// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Contractor Rate Master Per Worker", {
//     onload(frm) {
//         // Filter Labourer Name by selected Work Type in child table
//         frm.set_query("labourer_name", "contractor_rate_master_details", function(doc, cdt, cdn) {
//             let row = locals[cdt][cdn];
//             if (!row.work_type) return {};

//             return {
//                 query: "alnabeel.alnabeel.api.labourer_query.get_labourers_by_work_type",
//                 filters: { work_type: row.work_type }
//             };
//         });
//     }
// });

// frappe.ui.form.on("Contractor Rate Master Details", {
//     work_type(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         frappe.model.set_value(cdt, cdn, "labourer_name", null);
//         frappe.model.set_value(cdt, cdn, "worker_name", null);
//     },

//     labourer_name(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // Disable Worker Name
//         if (row.labourer_name) {
//             frm.fields_dict.contractor_rate_master_details.grid.toggle_enable("worker_name", false, cdn);
//             frappe.model.set_value(cdt, cdn, "worker_name", null);
//         } else {
//             frm.fields_dict.contractor_rate_master_details.grid.toggle_enable("worker_name", true, cdn);
//         }

//         // Prevent duplicate Labourer + Work Type
//         let duplicate = frm.doc.contractor_rate_master_details.some(r => 
//             r.name !== cdn && r.work_type === row.work_type && r.labourer_name === row.labourer_name
//         );
//         if (duplicate) {
//             frappe.model.set_value(cdt, cdn, "labourer_name", null);
//             frappe.throw("Duplicate Labourer Name with same Work Type not allowed!");
//         }
//     },

//     worker_name(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         // Disable Labourer Name
//         if (row.worker_name) {
//             frm.fields_dict.contractor_rate_master_details.grid.toggle_enable("labourer_name", false, cdn);
//             frappe.model.set_value(cdt, cdn, "labourer_name", null);
//         } else {
//             frm.fields_dict.contractor_rate_master_details.grid.toggle_enable("labourer_name", true, cdn);
//         }

//         // Prevent duplicate Worker + Work Type
//         let duplicate = frm.doc.contractor_rate_master_details.some(r => 
//             r.name !== cdn && r.work_type === row.work_type && r.worker_name === row.worker_name
//         );
//         if (duplicate) {
//             frappe.model.set_value(cdt, cdn, "worker_name", null);
//             frappe.throw("Duplicate Worker Name with same Work Type not allowed!");
//         }
//     }
// });


frappe.ui.form.on("Contractor Rate Master Per Worker", {
    refresh(frm) {
        set_labourer_filter(frm);
    },

    contractor(frm) {
        set_labourer_filter(frm);

        // Optional: clear child table when contractor changes
        frm.clear_table("contractor_rate_master_details");
        frm.refresh_field("contractor_rate_master_details");
    }
});

function set_labourer_filter(frm) {
    frm.fields_dict.contractor_rate_master_details.grid.get_field("labourer_name").get_query =
        function (doc, cdt, cdn) {
            return {
                filters: {
                    contractor: frm.doc.contractor,
                     status: "Active"
                }
            };
        };
}

/* ================= DUPLICATE PREVENTION ================= */

frappe.ui.form.on("Contractor Rate Master Details", {
    labourer_name(frm, cdt, cdn) {
        check_duplicate_labourer(frm, cdt, cdn);
    },

    work_type(frm, cdt, cdn) {
        check_duplicate_labourer(frm, cdt, cdn);
    }
});

function check_duplicate_labourer(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.labourer_name || !row.work_type) return;

    let duplicate = frm.doc.contractor_rate_master_details.some(r =>
        r.name !== row.name &&
        r.labourer_name === row.labourer_name &&
        r.work_type === row.work_type
    );

    if (duplicate) {
        frappe.msgprint({
            title: "Duplicate Entry",
            message: "Same Labourer cannot be entered again for the same Work Type.",
            indicator: "red"
        });

        frappe.model.set_value(cdt, cdn, "labourer_name", "");
    }
}


