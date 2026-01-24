import frappe

def lock_dla_after_mr_saved(doc, method):
    """
    Auto-lock DLA once the MR is saved manually.
    """
    if doc.docstatus != 1:  # Only after MR is submitted
        return

    if not getattr(doc, "daily_labour_attendance", None):
        return

    dla_name = doc.daily_labour_attendance
    dla = frappe.get_doc("Daily Labour Attendance", dla_name)
    dla.db_set("material_request_created", 1)
    dla.db_set("material_request", doc.name)

