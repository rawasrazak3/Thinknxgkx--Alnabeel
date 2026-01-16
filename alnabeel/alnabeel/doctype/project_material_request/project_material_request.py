# # Copyright (c) 2026, krishna and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe import _ 
# from frappe.utils import flt, today

# class ProjectMaterialRequest(Document):
#     def validate(self):
#         self.validate_request_qty()

#     def validate_request_qty(self):
#         for row in self.pmr_items:
#             if not row.select_item:
#                 continue

#             if flt(row.request_qty) <= 0:
#                 frappe.throw(
#                     _("Request Qty must be greater than 0 for Item {0}").format(row.item_code)
#                 )

#             if flt(row.request_qty) > flt(row.balance_qty):
#                 frappe.throw(
#                     _("Request Qty ({0}) cannot exceed Balance Qty ({1}) for Item {2}").format(
#                         row.request_qty, row.balance_qty, row.item_code
#                     )
#                 )


# # Fetch items from Quantity Budget
# @frappe.whitelist()
# def get_items_from_quantity_budget(project):
#     return frappe.db.sql(
#         """
#         SELECT
#             ibd.item_code,
#             ibd.item_name,
#             ibd.budget_qty,
#             IFNULL(ibd.consumed_qty, 0) AS consumed_qty,
#             (ibd.budget_qty - IFNULL(ibd.consumed_qty, 0)) AS balance_qty
#         FROM `tabQuantity Budget` qb
#         INNER JOIN `tabItem Budget Detail` ibd
#             ON ibd.parent = qb.name
#         WHERE qb.project = %s
#           AND qb.docstatus = 1
#         """,
#         project,
#         as_dict=True
#     )


# # Create Material Request from selected PMR items
# @frappe.whitelist()
# def create_material_request(pmr_name):
#     pmr = frappe.get_doc("Project Material Request", pmr_name)

#     # Validate request_qty before proceeding
#     pmr.validate_request_qty()

#     # Create Material Request
#     mr = frappe.new_doc("Material Request")
#     mr.material_request_type = "Material Issue"
#     mr.project = pmr.project
#     mr.set_warehouse = pmr.warehouse
#     mr.schedule_date = pmr.required_by_date

#     # Append only selected items
#     for row in pmr.pmr_items:
#         if row.select_item and flt(row.request_qty) > 0:
#             uom = frappe.db.get_value("Item", row.item_code, "stock_uom")
#             mr.append("items", {
#                 "item_code": row.item_code,
#                 "qty": row.request_qty,
#                 "uom": uom,
#                 "project": pmr.project,
#                 "t_warehouse": pmr.warehouse
#             })

#     if not mr.items:
#         frappe.throw(_("No items selected to create Material Request."))

#     mr.insert()
#     return mr.name


# Copyright (c) 2026, krishna and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class ProjectMaterialRequest(Document):

    def validate(self):
        # Do not allow changes after MR creation
        if self.mr_created:
            frappe.throw(_("Material Request already created. Document is locked."))

        self.validate_request_qty()

    def validate_request_qty(self):
        for row in self.pmr_items:
            if not row.select_item:
                continue

            if flt(row.request_qty) <= 0:
                frappe.throw(
                    _("Request Qty must be greater than 0 for Item {0}")
                    .format(row.item_code)
                )

            if flt(row.request_qty) > flt(row.balance_qty):
                frappe.throw(
                    _("Request Qty ({0}) cannot exceed Balance Qty ({1}) for Item {2}")
                    .format(row.request_qty, row.balance_qty, row.item_code)
                )


# ======================================================
# Fetch PMR items from Quantity Budget
# ======================================================
@frappe.whitelist()
def get_items_from_quantity_budget(project):
    return frappe.db.sql(
        """
        SELECT
            ibd.item_code,
            ibd.item_name,
            ibd.budget_qty,
            IFNULL(ibd.consumed_qty, 0) AS consumed_qty,
            (ibd.budget_qty - IFNULL(ibd.consumed_qty, 0)) AS balance_qty
        FROM `tabQuantity Budget` qb
        INNER JOIN `tabItem Budget Detail` ibd
            ON ibd.parent = qb.name
        WHERE qb.project = %s
          AND qb.docstatus = 1
        """,
        project,
        as_dict=True
    )


# ======================================================
# Create Material Request (ONE TIME ONLY)
# ======================================================
@frappe.whitelist()
def create_material_request(pmr_name):

    pmr = frappe.get_doc("Project Material Request", pmr_name)

    # HARD BLOCK duplicate MR creation
    if pmr.mr_created:
        frappe.throw(_("Material Request already created for this PMR."))

    pmr.validate_request_qty()

    # Create Material Request
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Material Issue"
    mr.project = pmr.project
    mr.set_warehouse = pmr.warehouse
    mr.schedule_date = pmr.required_by_date

    for row in pmr.pmr_items:
        if row.select_item and flt(row.request_qty) > 0:
            uom = frappe.db.get_value("Item", row.item_code, "stock_uom")

            mr.append("items", {
                "item_code": row.item_code,
                "qty": row.request_qty,
                "uom": uom,
                "project": pmr.project,
                "t_warehouse": pmr.warehouse
            })

    if not mr.items:
        frappe.throw(_("No items selected to create Material Request."))

    # Insert MR
    mr.insert(ignore_permissions=True)
    mr.submit()
    
    # Lock PMR permanently
    pmr.db_set("mr_created", 1)
    pmr.db_set("material_request", mr.name)

    return mr.name
