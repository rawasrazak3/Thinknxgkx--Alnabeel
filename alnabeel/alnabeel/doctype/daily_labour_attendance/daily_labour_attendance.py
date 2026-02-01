# Copyright (c) 2026, krishna and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class DailyLabourAttendance(Document):
# 	pass


import frappe
from frappe.model.document import Document
from frappe.utils import getdate, flt, today
from frappe import _

class DailyLabourAttendance(Document):
     def before_save(self):
        if self.material_request_created:
            frappe.throw(_("This Daily Labour Attendance is locked because a Material Request is already created."))

# --------------------------------------
# Get labourer rate from Contractor Rate Master Details
# --------------------------------------
@frappe.whitelist()
def get_labourer_rate(contractor, project, date, work_type, labourer_name):
    """
    Fetch rate from Contractor Rate Master Per Worker (child table: Contractor Rate Master Details)
    considering date range from effective_from and effective_to.
    """
    date = getdate(date)

    # Get parent based on project mapping & date range
    parent = frappe.db.sql("""
        SELECT name
        FROM `tabContractor Rate Master Per Worker`
        WHERE contractor = %s
          AND project = %s
          AND effective_from <= %s
          AND (effective_to IS NULL OR effective_to >= %s)
          AND (docstatus = 1 OR docstatus = 0)
        LIMIT 1
    """, (contractor, project, date, date), as_dict=True)

    if not parent:
        frappe.throw(_("No Contractor Rate Master Per Worker found for given Contractor, Project and Date"))

    parent_name = parent[0]["name"]

    # Get rate from child table
    rate = frappe.db.get_value(
        "Contractor Rate Master Details",
        {
            "parent": parent_name,
            "labourer_name": labourer_name,
            "work_type": work_type
        },
        ["standard_rate", "overtime_rate", "bonus_rate"],
        as_dict=True
    )

    if not rate:
        frappe.throw(_("No rate found for Labourer {0} with Work Type {1}").format(labourer_name, work_type))

    rate["rate_master"] = parent_name
    return rate

# --------------------------------------
# Get worker rate from Contractor Labour Rate Details
# --------------------------------------
@frappe.whitelist()
def get_worker_rate(contractor, project, date, work_type):
    """
    Fetch rate from Contractor Labour Rate (child table: Contractor Labour Rate Details)
    considering date range from effective_from and effective_to.
    """
    date = getdate(date)

    parent = frappe.db.sql("""
        SELECT name
        FROM `tabContractor Labour Rate`
        WHERE contractor = %s
          AND project = %s
          AND effective_from <= %s
          AND (effective_to IS NULL OR effective_to >= %s)
          AND docstatus = 1
        LIMIT 1
    """, (contractor, project, date, date), as_dict=True)

    if not parent:
        frappe.throw(_("No Contractor Labour Rate found for given Contractor, Project and Date"))

    parent_name = parent[0]["name"]

    # Get rate from child table
    rate = frappe.db.get_value(
        "Contractor Labour Rate Details",
        {
            "parent": parent_name,
            "work_type": work_type
        },
        ["base_labour_rate", "overtime_rate", "bonus_rate"],
        as_dict=True
    )

    if not rate:
        frappe.throw(_("No rate found for Work Type {0}").format(work_type))

    rate["rate_master"] = parent_name
    return rate

# --------------------------------------
# Filter Labourers for Link field
# --------------------------------------
@frappe.whitelist()
def get_filtered_labourers(doctype, txt, searchfield, start, page_len, filters):
    """
    Filter Labourer Names based on Contractor and Project.
    No creation allowed, date ignored.
    """
    contractor = filters.get("contractor")
    project = filters.get("project")
    date = filters.get("date")

    if not all([contractor, project]):
        return []

    return frappe.db.sql("""
        SELECT DISTINCT crmd.labourer_name
        FROM `tabContractor Rate Master Details` crmd
        JOIN `tabContractor Rate Master Per Worker` crm
            ON crmd.parent = crm.name
        WHERE crm.contractor = %s
          AND crm.project = %s
          AND crmd.labourer_name LIKE %s
        ORDER BY crmd.labourer_name
        LIMIT %s OFFSET %s
    """, (
        contractor,
        project,
        date,
        date,
        f"%{txt}%",
        page_len,
        start
    ))


@frappe.whitelist()
def get_filtered_labourers_by_work_type(doctype, txt, searchfield, start, page_len, filters):
    """
    Filter Labourer Names based on Contractor, Project, and Work Type.
    No creation allowed, date ignored.
    """
    contractor = filters.get("contractor")
    project = filters.get("project")
    work_type = filters.get("work_type")
    date = filters.get("date")

    if not all([contractor, project, work_type]):
        return []

    return frappe.db.sql("""
        SELECT DISTINCT crmd.labourer_name
        FROM `tabContractor Rate Master Details` crmd
        JOIN `tabContractor Rate Master Per Worker` crm
            ON crmd.parent = crm.name
        WHERE crm.contractor = %s
          AND crm.project = %s
          AND crmd.work_type = %s
          AND crm.effective_from <= %s
          AND (crm.effective_to IS NULL OR crm.effective_to >= %s)
          AND crmd.labourer_name LIKE %s
        ORDER BY crmd.labourer_name
        LIMIT %s OFFSET %s
    """, (
        contractor,
        project,
        work_type,
        date,
        date,
        f"%{txt}%",
        page_len,
        start
    ))

# fetch standard working hrs
@frappe.whitelist()
def get_standard_working_hours(contractor, project):
    return flt(
        frappe.db.get_value(
            "Contractor Labour Rate",
            {
                "contractor": contractor,
                "project": project,
                "docstatus": 1
            },
            "standard_working_hours"
        ) or 0
    )


# create material request from dla
@frappe.whitelist()
def create_material_request_from_dla(dla_name):
    """
    Creates Material Request for the DLA.
    Prefills only items with qty=1 and rate=total amounts.
    Other fields are manually entered by the user.
    """
    # Fetch DLA
    dla = frappe.get_doc("Daily Labour Attendance", dla_name)

    if getattr(dla, "material_request_created", 0):
        frappe.throw("Material Request already created for this Daily Labour Attendance")

    # Create MR doc
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Purchase"
    mr.custom_daily_labour_attendance = dla.name
    mr.schedule_date = today()

    # Items to add
    labour_items = [
        {"name": "Standard Labour", "amount": dla.total_standard_amount},
        {"name": "OT Labour", "amount": dla.total_ot_amount},
        {"name": "Incentive / Bonus Labour", "amount": dla.total_bonus_amount},
    ]

    for item in labour_items:
        if flt(item["amount"]) > 0:
            item_code = frappe.db.get_value("Item", {"item_name": item["name"]})
            if not item_code:
                frappe.throw(f"Item '{item['name']}' not found in Item Master")
            
            mr.append("items", {
                "item_code": item_code,
                "qty": 1,
                "rate": flt(item["amount"]),
                "amount": flt(item["amount"])
            })

    if not mr.items:
        frappe.throw("No labour amounts found to create Material Request")

    mr.insert()
    frappe.db.commit()  # Ensure MR exists in DB so route can open it

    return mr.name


# create bulk material request from multiple dlas
@frappe.whitelist()
def create_bulk_material_request(dla_names):
    if isinstance(dla_names, str):
        import json
        dla_names = json.loads(dla_names)

    if not dla_names:
        frappe.throw("No Daily Labour Attendance selected")

    total_standard = 0
    total_ot = 0
    total_bonus = 0

    for name in dla_names:
        dla = frappe.get_doc("Daily Labour Attendance", name)

        if dla.material_request_created:
            frappe.throw(f"DLA {name} already linked to a Material Request")

        total_standard += flt(dla.total_standard_amount)
        total_ot += flt(dla.total_ot_amount)
        total_bonus += flt(dla.total_bonus_amount)

    # Create MR
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Purchase"
    mr.schedule_date = today()

    items = [
        ("Standard Labour", total_standard),
        ("OT Labour", total_ot),
        ("Incentive / Bonus Labour", total_bonus)
    ]

    for item_name, amount in items:
        if amount > 0:
            item_code = frappe.db.get_value("Item", {"item_name": item_name})
            if not item_code:
                frappe.throw(f"Item '{item_name}' not found")

            mr.append("items", {
                "item_code": item_code,
                "qty": 1,
                "rate": amount,
                "amount": amount
            })

    if not mr.items:
        frappe.throw("No amounts found to create Material Request")

    mr.insert()

    # Lock DLAs + link MR
    for name in dla_names:
        frappe.db.set_value(
            "Daily Labour Attendance",
            name,
            {
                "material_request_created": 1,
                "material_request": mr.name
            }
        )

    frappe.db.commit()
    return mr.name

