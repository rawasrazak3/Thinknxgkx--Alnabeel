frappe.ui.form.on('Opportunity', {

    onload: function(frm) {

        // Only run if created from Lead
        if (frm.doc.opportunity_from === "Lead" && frm.doc.party_name) {

            frappe.db.get_doc('Lead', frm.doc.party_name)
                .then(lead => {

                    if (lead.custom_lead_amount) {
                        frm.set_value('opportunity_amount', lead.custom_lead_amount);
                    }

                    if (lead.custom_remarks) {
                        frm.set_value('custom_remark', lead.custom_remarks);
                    }

                });
        }
    }

});