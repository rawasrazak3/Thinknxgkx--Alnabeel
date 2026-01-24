// Copyright (c) 2026, krishna and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Daily Labour Attendance", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Daily Labour Attendance", {
    refresh(frm) {
        set_labourer_filter(frm);
        // load_standard_hours(frm);
        set_labourer_filter(frm);

        // Show "Create Material Request" only if saved & MR not created
        if (!frm.is_new() && !frm.doc.material_request_created) {
            frm.add_custom_button(__('Create Material Request'), () => {
                frappe.call({
                    method: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.create_material_request_from_dla",
                    args: { dla_name: frm.doc.name },
                    callback: function(r) {
                        if (r.message) {
                            // Open the newly created MR in form view
                            frappe.set_route("Form", "Material Request", r.message);
                        }
                    }
                });
            });
        }

        // Lock DLA if MR is already created
        if (frm.doc.material_request_created) {
            frm.set_read_only();
            frm.disable_save();
            frm.clear_custom_buttons();
            frm.dashboard.set_headline(__('Material Request Created-Document Locked'));
        }
    },

    contractor(frm) {
        frm.clear_table("labour_attendance_detail");
        frm.refresh_field("labour_attendance_detail");
        set_labourer_filter(frm);
    },

    project(frm) {
        set_labourer_filter(frm);
        load_standard_hours(frm);
        set_labourer_filter(frm);
    },
      
    date(frm) {
        set_labourer_filter(frm);
    },

    select_all(frm) {
        select_all_times(frm);
    },

    unselect_all(frm) {
        unselect_all_times(frm);
    }
});

// --------------------------------------
// Get selected project from child table (if multiple projects)
function get_selected_project(frm) {
    if (!frm.doc.project || !frm.doc.project.length) return null;
    return frm.doc.project[0].project;
}

// --------------------------------------
// Set Labourer Link field filter (dynamic by Work Type)
// --------------------------------------
function set_labourer_filter(frm) {
    frm.fields_dict.labour_attendance_detail.grid.get_field("labourer_name").get_query =
        function (doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            // Only filter if work_type is selected
           if (!row.work_type || !frm.doc.date) {
                return { filters: {} };
            }

            return {
                query: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.get_filtered_labourers_by_work_type",
                filters: {
                    contractor: frm.doc.contractor,
                    project: get_selected_project(frm),
                    work_type: row.work_type,
                     date: frm.doc.date
                },
                ignore_user_permissions: 1
            };
        };
}

// --------------------------------------
// Child table logic
// --------------------------------------
frappe.ui.form.on("Labour Attendance Detail", {
    work_type(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Reset labourer/worker selection when work type changes
        if (row.labourer_name) {
            frappe.model.set_value(cdt, cdn, "worker_name", null);
            fetch_labourer_rate(frm, row);
        }

        if (row.worker_name) {
            frappe.model.set_value(cdt, cdn, "labourer_name", null);
            fetch_worker_rate(frm, row);
        }
    },

    labourer_name(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.labourer_name) return;

        frappe.model.set_value(cdt, cdn, "worker_name", null);
        toggle_fields(frm, row);
        fetch_labourer_rate(frm, row);
        prevent_duplicate(frm, row, "labourer_name");
    },

    worker_name(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.worker_name) return;

        frappe.model.set_value(cdt, cdn, "labourer_name", null);
        toggle_fields(frm, row);
        fetch_worker_rate(frm, row);
        prevent_duplicate(frm, row, "worker_name");
    },

    // fot ot and normal hours cal
    from_time(frm, cdt, cdn) {
        calculate_hours(frm, locals[cdt][cdn]);
    },

    to_time(frm, cdt, cdn) {
        calculate_hours(frm, locals[cdt][cdn]);
    },

    // for standard and ot hours rate cal
     rate_per_hour(frm, cdt, cdn) {
        calculate_hours(frm, locals[cdt][cdn]);
    },
    ot_rate_per_hour(frm, cdt, cdn) {
        calculate_hours(frm, locals[cdt][cdn]);
    }
});

// --------------------------------------
// Toggle Labourer / Worker fields
// --------------------------------------
function toggle_fields(frm, row) {
    let grid_row = frm.fields_dict.labour_attendance_detail.grid.grid_rows_by_docname[row.name];
    if (!grid_row) return;
    grid_row.toggle_editable("worker_name", !row.labourer_name);
    grid_row.toggle_editable("labourer_name", !row.worker_name);
}

// --------------------------------------
// Fetch Labourer rate
// --------------------------------------
function fetch_labourer_rate(frm, row) {
    if (!row.labourer_name || !row.work_type) return;

    frappe.call({
        method: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.get_labourer_rate",
        args: {
            contractor: frm.doc.contractor,
            project: get_selected_project(frm),
            date: frm.doc.date,
            labourer_name: row.labourer_name,
            work_type: row.work_type
        },
        callback(r) {
            if (!r.message) return;
            frappe.model.set_value(row.doctype, row.name, "rate_per_hour", r.message.standard_rate);
            frappe.model.set_value(row.doctype, row.name, "ot_rate_per_hour", r.message.overtime_rate);
            frappe.model.set_value(row.doctype, row.name, "bonus_rate", r.message.bonus_rate);
        }
    });
}

// --------------------------------------
// Fetch Worker rate
// --------------------------------------
function fetch_worker_rate(frm, row) {
    if (!row.worker_name || !row.work_type) return;

    frappe.call({
        method: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.get_worker_rate",
        args: {
            contractor: frm.doc.contractor,
            project: get_selected_project(frm),
            date: frm.doc.date,
            work_type: row.work_type
        },
        callback(r) {
            if (!r.message) return;
            frappe.model.set_value(row.doctype, row.name, "rate_per_hour", r.message.base_labour_rate);
            frappe.model.set_value(row.doctype, row.name, "ot_rate_per_hour", r.message.overtime_rate);
            frappe.model.set_value(row.doctype, row.name, "bonus_rate", r.message.bonus_rate);
        }
    });
}

// --------------------------------------
// Prevent duplicate entries in same grid
// --------------------------------------
function prevent_duplicate(frm, current_row, field) {
    if (!current_row[field] || !current_row.work_type) return;

    let duplicate = frm.doc.labour_attendance_detail.some(row =>
        row.name !== current_row.name &&
        row.work_type === current_row.work_type &&
        row[field] === current_row[field]
    );

    if (duplicate) {
        frappe.msgprint({
            title: __("Duplicate Entry"),
            message: __("Same {0} with the same Work Type cannot be selected again.").replace("{0}", field === "labourer_name" ? "Labourer" : "Worker"),
            indicator: "red"
        });
        frappe.model.set_value(current_row.doctype, current_row.name, field, null);
    }
}


// --------------------------------------
// Select All From/To Times
// --------------------------------------
function select_all_times(frm) {
    if (!frm.doc.from_time || !frm.doc.to_time) {
        frappe.msgprint(__('Please enter From Time and To Time at the top before selecting all.'));
        return;
    }

    frm.doc.labour_attendance_detail.forEach(row => {
        frappe.model.set_value(row.doctype, row.name, 'from_time', frm.doc.from_time);
        frappe.model.set_value(row.doctype, row.name, 'to_time', frm.doc.to_time);
        calculate_hours(frm, row);
    });

    frm.refresh_field('labour_attendance_detail');
}

// --------------------------------------
// Unselect All From/To Times
// --------------------------------------
function unselect_all_times(frm) {
    frm.doc.labour_attendance_detail.forEach(row => {
        frappe.model.set_value(row.doctype, row.name, 'from_time', null);
        frappe.model.set_value(row.doctype, row.name, 'to_time', null);
    });

    frm.refresh_field('labour_attendance_detail');
}

// Fetch & cache standard hours
// function load_standard_hours(frm) {
//     let project = get_selected_project(frm);
//     if (!project) return;

//     frappe.call({
//     method: "alnabeel.alnabeel.doctype.daily_labour_attendance.daily_labour_attendance.get_project_standard_hours",
//     args: { 
//         contractor: frm.doc.contractor,
//         project: get_selected_project(frm) 
//     },
//     callback(r) {
//         frm.standard_working_hours = flt(r.message) || 8;

//         frm.doc.labour_attendance_detail.forEach(row => calculate_hours(frm, row));
//         frm.refresh_field('labour_attendance_detail');
//     }
// });

// }

function calculate_hours(frm, row) {
    if (!row.from_time || !row.to_time) return;

    let from = moment(row.from_time, "HH:mm");
    let to = moment(row.to_time, "HH:mm");
    if (!from.isValid() || !to.isValid()) return;

    let total_hours = moment.duration(to.diff(from)).asHours();
    if (total_hours < 0) total_hours = 0;

   // normal hours = parent normal working hours
    let normal_hours = frm.doc.normal_working_hours || 0;

    // OT hours = anything above normal working hours
    let ot_hours = Math.max(total_hours - normal_hours, 0);

    frappe.model.set_value(row.doctype, row.name, "normal_hours", normal_hours);
    frappe.model.set_value(row.doctype, row.name, "ot_hours", ot_hours);

    // Calculate row amounts
    let rate_per_hour = row.rate_per_hour || 0;
    let ot_rate_per_hour = row.ot_rate_per_hour || 0;
    let bonus_rate = row.bonus_rate || 0;

    let standard_hours_amt = flt(normal_hours * rate_per_hour, 3);
    let ot_hours_amt = flt(ot_hours * ot_rate_per_hour, 3);
    let bonus_amt = flt(normal_hours * bonus_rate, 3); // or you can decide formula

    frappe.model.set_value(row.doctype, row.name, "standard_hours_amt", standard_hours_amt);
    frappe.model.set_value(row.doctype, row.name, "ot_hours_amt", ot_hours_amt);
    frappe.model.set_value(row.doctype, row.name, "bonus_amt", bonus_amt);

    // Update totals
    update_totals(frm);
}


function update_totals(frm) {
    let total_standard_amount = 0;
    let total_ot_amount = 0;
    let total_bonus_amount = 0;

    frm.doc.labour_attendance_detail.forEach(row => {
        total_standard_amount += row.standard_hours_amt || 0;
        total_ot_amount += row.ot_hours_amt || 0;
        total_bonus_amount += row.bonus_amt || 0;
    });

    frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_standard_amount", flt(total_standard_amount, 3));
    frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_ot_amount", flt(total_ot_amount, 3));
    frappe.model.set_value(frm.doc.doctype, frm.doc.name, "total_bonus_amount", flt(total_bonus_amount, 3));
}

