frappe.ui.form.on('Event', {

    refresh: function(frm) {
        filter_child_rows(frm);
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

frappe.ui.form.on('Site Visit Detail', {

    custom_site_visit_detail_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Make sure parent fields are selected
        if(!frm.doc.custom_year || !frm.doc.custom_month || !frm.doc.custom_sales_person) {
            frappe.msgprint("Please select Year, Month, and Sales Person before adding a Site Visit.");
            frappe.model.clear_doc(row);
            return;
        }

        // Auto-fill child row values from parent
        frappe.model.set_value(cdt, cdn, 'year', frm.doc.custom_year);
        frappe.model.set_value(cdt, cdn, 'month', frm.doc.custom_month);
        frappe.model.set_value(cdt, cdn, 'sales_person', frm.doc.custom_sales_person);
    }

});

// Function to filter child table dynamically
function filter_child_rows(frm) {
    let year = frm.doc.custom_year;
    let month = frm.doc.custom_month;
    let sp = frm.doc.custom_sales_person;

    let grid = frm.fields_dict.custom_site_visit_detail.grid;
    if(!grid) return;

    grid.get_data = function() {
        return (frm.doc.custom_site_visit_detail || []).filter(row => {
            if(year && row.year != year) return false;
            if(month && row.month != month) return false;
            if(sp && row.sales_person != sp) return false;
            return true;
        });
    };

    frm.refresh_field('custom_site_visit_detail');
}


frappe.ui.form.on('Site Visit Detail', {

    convert_to_lead: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if(!row.new_customer && !row.existing_customer) {
            frappe.msgprint("Please select a customer before converting to Lead.");
            return;
        }

        // Prepare the values to prefill in the new Lead
        let doc = {
            first_name: row.new_customer || row.existing_customer,
            email_id: row.email_id,
            phone: row.phone_no,
            territory: row.location,
            expected_budget: row.expected_budget,
            lead_status: row.lead_status
        };

        // Open a new Lead form with prefilled values
        frappe.new_doc('Lead', doc);
    }

});