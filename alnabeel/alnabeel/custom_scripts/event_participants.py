import frappe

def sync_site_visit_leads(doc, method):

    # Stop if no site visit rows
    if not doc.custom_site_visit_detail:
        return

    # Collect existing participant leads
    existing_leads = [
        p.reference_docname
        for p in doc.event_participants
        if p.reference_doctype == "Lead"
    ]

    updated = False

    # Loop site visit rows
    for row in doc.custom_site_visit_detail:

        if row.lead_created == 1 and row.lead_id:

            if row.lead_id not in existing_leads:

                doc.append("event_participants", {
                    "reference_doctype": "Lead",
                    "reference_docname": row.lead_id,
                    "email": row.email_id,
                })

                updated = True

    # Save only if new participant added
    if updated:
        doc.save(ignore_permissions=True)