// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Labour Attendance Detail", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("Labour Attendance Detail", {

    labourer_name(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Disable Worker Name when Labourer selected
        if (row.labourer_name) {
            frappe.model.set_value(cdt, cdn, "worker_name", null);
            frm.fields_dict.labour_attendance_detail.grid.toggle_enable("worker_name", false, cdn);
        } else {
            frm.fields_dict.labour_attendance_detail.grid.toggle_enable("worker_name", true, cdn);
        }

        // Prevent duplicate Labourer + Work Type
        if (row.work_type && row.labourer_name) {
            let duplicate = frm.doc.labour_attendance_detail.some(r =>
                r.name !== cdn &&
                r.work_type === row.work_type &&
                r.labourer_name === row.labourer_name
            );

            if (duplicate) {
                frappe.model.set_value(cdt, cdn, "labourer_name", null);
                frappe.throw(__("Duplicate Labourer with same Work Type not allowed!"));
            }
        }
    },

    worker_name(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Disable Labourer Name when Worker selected
        if (row.worker_name) {
            frappe.model.set_value(cdt, cdn, "labourer_name", null);
            frm.fields_dict.labour_attendance_detail.grid.toggle_enable("labourer_name", false, cdn);
        } else {
            frm.fields_dict.labour_attendance_detail.grid.toggle_enable("labourer_name", true, cdn);
        }

        // Prevent duplicate Worker + Work Type
        if (row.work_type && row.worker_name) {
            let duplicate = frm.doc.labour_attendance_detail.some(r =>
                r.name !== cdn &&
                r.work_type === row.work_type &&
                r.worker_name === row.worker_name
            );

            if (duplicate) {
                frappe.model.set_value(cdt, cdn, "worker_name", null);
                frappe.throw(__("Duplicate Worker with same Work Type not allowed!"));
            }
        }
    },

    work_type(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Re-check duplication when work type changes
        if (row.labourer_name) {
            let duplicate = frm.doc.labour_attendance_detail.some(r =>
                r.name !== cdn &&
                r.work_type === row.work_type &&
                r.labourer_name === row.labourer_name
            );

            if (duplicate) {
                frappe.model.set_value(cdt, cdn, "work_type", null);
                frappe.throw(__("Duplicate Labourer with same Work Type not allowed!"));
            }
        }

        if (row.worker_name) {
            let duplicate = frm.doc.labour_attendance_detail.some(r =>
                r.name !== cdn &&
                r.work_type === row.work_type &&
                r.worker_name === row.worker_name
            );

            if (duplicate) {
                frappe.model.set_value(cdt, cdn, "work_type", null);
                frappe.throw(__("Duplicate Worker with same Work Type not allowed!"));
            }
        }
    }
});
