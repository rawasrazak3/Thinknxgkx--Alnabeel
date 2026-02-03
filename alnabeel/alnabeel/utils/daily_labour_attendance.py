# in daily_labour_attendance.py or utils.py
import frappe

@frappe.whitelist()
def lock_dla_after_mr(doc, method=None):
    """
    Lock DLA after Material Request is submitted
    """
    if not getattr(doc, "custom_daily_labour_attendance", None):
        return

    dla = frappe.get_doc(
        "Daily Labour Attendance",
        doc.custom_daily_labour_attendance
    )

    dla.db_set("material_request_created", 1)
    dla.db_set("material_request", doc.name)
