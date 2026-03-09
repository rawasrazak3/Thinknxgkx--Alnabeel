
# import frappe
# import json

# @frappe.whitelist()
# def send_site_visit_email(event_name, rows):

#     if isinstance(rows, str):
#         rows = json.loads(rows)

#     event = frappe.get_doc("Event", event_name)

#     if not rows:
#         frappe.throw("No Site Visit rows to send.")

#     table_html = """
#     <h3>Site Visit Details</h3>
#     <table border="1" style="border-collapse:collapse;font-size:13px;">
#         <tr style="background:#f2f2f2;">
#             <th>Sales Person</th>
#             <th>Visit Date/Time</th>
#             <th>New Customer</th>
#             <th>Existing Customer</th>
#             <th>Lead</th>
#             <th>Location</th>
#             <th>Lead Status</th>
#             <th>Follow Up</th>
#             <th>Expected Budget</th>
#             <th>Remarks</th>
#             <th>Mobile</th>
#             <th>Phone</th>
#             <th>Whatsapp</th>
#             <th>Email</th>
#         </tr>
#     """

#     sent_rows = []

#     for row in rows:

#         table_html += f"""
#         <tr>
#             <td>{row.get('sales_person') or ''}</td>
#             <td>{row.get('visit_datetime') or ''}</td>
#             <td>{row.get('new_customer') or ''}</td>
#             <td>{row.get('existing_customer') or ''}</td>
#             <td>{row.get('lead') or ''}</td>
#             <td>{row.get('location') or ''}</td>
#             <td>{row.get('lead_status') or ''}</td>
#             <td>{row.get('follow_up_datetime') or ''}</td>
#             <td>{row.get('expected_budget') or ''}</td>
#             <td>{row.get('remarks') or ''}</td>
#             <td>{row.get('mobile_no') or ''}</td>
#             <td>{row.get('phone') or ''}</td>
#             <td>{row.get('whatsapp') or ''}</td>
#             <td>{row.get('email_id') or ''}</td>
#         </tr>
#         """

#         sent_rows.append(row.get("name"))

#     table_html += "</table>"

#     # ---------------- Recipients ----------------

#     recipients = []

#     # Directors (Role: Director Alnabeel)
#     directors = frappe.get_all(
#         "Has Role",
#         filters={"role": "Director Al Nabeel"},
#         pluck="parent"
#     )

#     for user in directors:
#         email = frappe.db.get_value("User", user, "email")
#         if email:
#             recipients.append(email)

#     # Sales Person email
#     if event.custom_sales_person:

#         sp_email = frappe.db.get_value(
#             "Employee",
#             event.custom_sales_person,
#             "company_email"
#         )

#         if sp_email:
#             recipients.append(sp_email)

#     # Remove duplicates
#     recipients = list(set(recipients))

#     if not recipients:
#         frappe.throw("No recipients found")

#     # ---------------- Send Email ----------------

#     frappe.sendmail(
#         recipients=recipients,
#         subject=f"Site Visit Report - {event.name}",
#         message=table_html,
#         reference_doctype="Event",
#         reference_name=event.name
#     )

#     # ---------------- Mark Rows Sent ----------------

#     for row_name in sent_rows:
#         frappe.db.set_value("Site Visit Detail", row_name, "email_sent", 1)

#     frappe.db.commit()

#     return True
import frappe
import json
from frappe.utils import get_url_to_form
from frappe.utils.pdf import get_pdf


@frappe.whitelist()
def send_site_visit_email(event_name, rows):

    if isinstance(rows, str):
        rows = json.loads(rows)

    event = frappe.get_doc("Event", event_name)

    if not rows:
        frappe.throw("No Site Visit rows to send.")

    event_link = get_url_to_form("Event", event.name)

    # ---------------- EMAIL TABLE ----------------

    table_html = """
    <h3>Site Visit Details</h3>
    <table border="1" style="border-collapse:collapse;font-size:13px;width:100%;">
        <tr style="background:#f2f2f2;">
            <th>Sales Person</th>
            <th>Visit Date</th>
            <th>Customer</th>
            <th>Location</th>
            <th>Lead Status</th>
            <th>Expected Budget</th>
            <th>Remarks</th>
        </tr>
    """

    # ---------------- PDF HTML ----------------

    pdf_html = f"""
    <h2 style="text-align:center;">Site Visit Report</h2>

    <p>
    <b>Event:</b> {event.name}<br>
    <b>Subject:</b> {event.subject or ''}<br>
    <b>Sales Person:</b> {event.custom_sales_person or ''}<br>
    <b>Event Link:</b> <a href="{event_link}">{event_link}</a>
    </p>

    <table border="1" style="border-collapse:collapse;font-size:11px;width:100%;">
    <tr style="background:#f2f2f2;">
        <th>Sales Person</th>
        <th>Visit Date/Time</th>
        <th>New Customer</th>
        <th>Existing Customer</th>
        <th>Lead</th>
        <th>Location</th>
        <th>Lead Status</th>
        <th>Follow Up</th>
        <th>Expected Budget</th>
        <th>Remarks</th>
        <th>Mobile</th>
        <th>Phone</th>
        <th>Whatsapp</th>
        <th>Email</th>
    </tr>
    """

    sent_rows = []

    for row in rows:

        customer = row.get("new_customer") or row.get("existing_customer") or ""

        # Email table row (short version)
        table_html += f"""
        <tr>
            <td>{row.get('sales_person') or ''}</td>
            <td>{row.get('visit_datetime') or ''}</td>
            <td>{customer}</td>
            <td>{row.get('location') or ''}</td>
            <td>{row.get('lead_status') or ''}</td>
            <td>{row.get('expected_budget') or ''}</td>
            <td>{row.get('remarks') or ''}</td>
        </tr>
        """

        # PDF row (full details)
        pdf_html += f"""
        <tr>
            <td>{row.get('sales_person') or ''}</td>
            <td>{row.get('visit_datetime') or ''}</td>
            <td>{row.get('new_customer') or ''}</td>
            <td>{row.get('existing_customer') or ''}</td>
            <td>{row.get('lead') or ''}</td>
            <td>{row.get('location') or ''}</td>
            <td>{row.get('lead_status') or ''}</td>
            <td>{row.get('follow_up_datetime') or ''}</td>
            <td>{row.get('expected_budget') or ''}</td>
            <td>{row.get('remarks') or ''}</td>
            <td>{row.get('mobile_no') or ''}</td>
            <td>{row.get('phone') or ''}</td>
            <td>{row.get('whatsapp') or ''}</td>
            <td>{row.get('email_id') or ''}</td>
        </tr>
        """

        sent_rows.append(row.get("name"))

    table_html += "</table>"
    pdf_html += "</table>"

    # ---------------- Recipients ----------------

    recipients = []

    directors = frappe.get_all(
        "Has Role",
        filters={"role": "Director Al Nabeel"},
        pluck="parent"
    )

    for user in directors:
        email = frappe.db.get_value("User", user, "email")
        if email:
            recipients.append(email)

    if event.custom_sales_person:

        sp_email = frappe.db.get_value(
            "Employee",
            event.custom_sales_person,
            "company_email"
        )

        if sp_email:
            recipients.append(sp_email)

    recipients = list(set(recipients))

    if not recipients:
        frappe.throw("No recipients found")

    # ---------------- Generate PDF ----------------

    pdf = get_pdf(pdf_html)

    # ---------------- Email Message ----------------

    message = f"""
    <p>Dear Team,</p>

    <p>Please find the latest <b>Site Visit Report</b> below.</p>

    <p>
    <b>Event:</b> {event.name}<br>
    <b>Sales Person:</b> {event.custom_sales_person or ''}<br>
    <b>View Event:</b> <a href="{event_link}">{event_link}</a>
    </p>

    {table_html}

    <p>Full report is attached as PDF.</p>
    """

    # ---------------- Send Email ----------------

    frappe.sendmail(
        recipients=recipients,
        subject=f"Site Visit Report - {event.name}",
        message=message,
        attachments=[
            {
                "fname": f"Site_Visit_Report_{event.name}.pdf",
                "fcontent": pdf
            }
        ],
        reference_doctype="Event",
        reference_name=event.name
    )

    # ---------------- Mark Rows Sent ----------------

    for row_name in sent_rows:
        frappe.db.set_value("Site Visit Detail", row_name, "email_sent", 1)

    frappe.db.commit()

    return True