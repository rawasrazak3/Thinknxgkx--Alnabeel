
// ========================= EVENT PARENT =========================

frappe.ui.form.on('Event', {

    refresh: function(frm) {
        filter_child_rows(frm);
        color_convert_buttons(frm);
    },

    custom_year: function(frm) {
        filter_child_rows(frm);
    },

    custom_month: function(frm) {
        filter_child_rows(frm);
    },

    custom_sales_person: function(frm) {
        filter_child_rows(frm);
    }

});


// ========================= CHILD TABLE ADD =========================

frappe.ui.form.on('Site Visit Detail', {

    custom_site_visit_detail_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!frm.doc.custom_year || !frm.doc.custom_month || !frm.doc.custom_sales_person) {
            frappe.msgprint("Please select Year, Month, and Sales Person before adding a Site Visit.");
            frappe.model.clear_doc(row);
            return;
        }

        frappe.model.set_value(cdt, cdn, 'year', frm.doc.custom_year);
        frappe.model.set_value(cdt, cdn, 'month', frm.doc.custom_month);
        frappe.model.set_value(cdt, cdn, 'sales_person', frm.doc.custom_sales_person);
    }

});


// ========================= FILTER FUNCTION =========================

function filter_child_rows(frm) {

    let year = frm.doc.custom_year;
    let month = frm.doc.custom_month;
    let sp = frm.doc.custom_sales_person;

    let grid = frm.fields_dict.custom_site_visit_detail.grid;
    if (!grid) return;

    grid.get_data = function() {
        return (frm.doc.custom_site_visit_detail || []).filter(row => {
            if (year && row.year != year) return false;
            if (month && row.month != month) return false;
            if (sp && row.sales_person != sp) return false;
            return true;
        });
    };

    frm.refresh_field('custom_site_visit_detail');
}


// ========================= CONVERT TO LEAD =========================

frappe.ui.form.on('Site Visit Detail', {

    convert_to_lead: function(frm, cdt, cdn) {

        let row = locals[cdt][cdn];

        if (row.lead_created) {
            frappe.msgprint({
                title: "Already Created",
                message: "Lead already created for this row.",
                indicator: "orange"
            });
            return;
        }

        if (!row.new_customer && !row.existing_customer) {
             frappe.msgprint({
                title: "Missing Customer",
                message: "Please select a customer before converting.",
                indicator: "red"
            });
            return;
        }

        let lead_status = row.lead_status || "Lead";

        frappe.call({
            method: "frappe.client.insert",
            args: {
                doc: {
                    doctype: "Lead",
                    first_name: row.new_customer || row.existing_customer,
                    email_id: row.email_id,
                    phone: row.phone,
                    mobile_no: row.mobile_no,
                    whatsapp_no: row.whatsapp,
                    custom_expected_budget: row.expected_budget
                }
            },
            callback: function(r) {

                if (r.message) {

                    let lead_name = r.message.name;

                    // update status
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Lead",
                            name: lead_name,
                            fieldname: "status",
                            value: lead_status
                        },
                        callback: function() {

                            // Update child row
                            frappe.model.set_value(cdt, cdn, "lead_created", 1);
                            frappe.model.set_value(cdt, cdn, "lead_id", lead_name);

                            frm.save();

                            frappe.show_alert({
                            message: "Lead " + lead_name + " created successfully",
                            indicator: "green"
                        });


                            frm.refresh_field("custom_site_visit_detail");
                        }
                    });
                }
            }
        });
    }
});