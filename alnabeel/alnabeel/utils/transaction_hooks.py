
# from alnabeel.alnabeel.utils.quantity_budget_check import check_quantity_budget

# def check_budget(doc, method=None):
#     for item in doc.items:
#         if item.project:
#             check_quantity_budget(doc, item)

import frappe
from frappe import _
from alnabeel.alnabeel.utils.quantity_budget_consumption import check_and_update_budget


def check_quantity_budget(doc, method=None):
    if doc.doctype != "Material Request":
        return

    for item in doc.items:
        check_and_update_budget(
            item_code=item.item_code,
            company=doc.company,
            qty=item.qty
        )
