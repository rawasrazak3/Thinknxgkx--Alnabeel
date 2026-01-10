# import frappe
# from frappe.utils import flt

# def update_consumed_on_submit(doc, method):
#     for item in doc.items:
#         if not item.project:
#             continue

#         update_budget(item, item.qty)


# def update_consumed_on_cancel(doc, method):
#     for item in doc.items:
#         if not item.project:
#             continue

#         update_budget(item, -item.qty)


# def update_budget(item, qty_change):
#     budgets = frappe.db.get_all(
#         "Quantity Budget",
#         filters={
#             "project": item.project,
#             "docstatus": 1
#         },
#         pluck="name"
#     )

#     for budget in budgets:
#         rows = frappe.db.get_all(
#             "Item Budget Detail",
#             filters={
#                 "parent": budget,
#                 "item_code": item.item_code
#             },
#             fields=["name", "consumed_qty"]
#         )

#         for row in rows:
#             new_qty = flt(row.consumed_qty) + flt(qty_change)
#             if new_qty < 0:
#                 new_qty = 0

#             frappe.db.set_value(
#                 "Item Budget Detail",
#                 row.name,
#                 "consumed_qty",
#                 new_qty
#             )
