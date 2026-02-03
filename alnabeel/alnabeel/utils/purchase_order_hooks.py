# from frappe.utils import flt
# from erpnext.accounts.utils import get_fiscal_year
# from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty

# # ------------------ On Submit ------------------
# def on_submit_purchase_order(doc, method):
#     # Determine fiscal year from posting date
#     fy = get_fiscal_year(doc.transaction_date or doc.schedule_date or doc.posting_date)[0]

#     for item in doc.items:
#         # Skip items without a project
#         if not item.project:
#             continue

#         update_consumed_qty(
#             item_code=item.item_code,
#             qty=item.qty,
#             rate=item.rate,
#             company=doc.company,
#             fiscal_year=fy,
#             budget_against="Project",
#             against_value=item.project,
#             is_cancel=False
#         )

# # ------------------ On Cancel ------------------
# def on_cancel_purchase_order(doc, method):
#     # Determine fiscal year from posting date
#     fy = get_fiscal_year(doc.transaction_date or doc.schedule_date or doc.posting_date)[0]

#     for item in doc.items:
#         if not item.project:
#             continue

#         update_consumed_qty(
#             item_code=item.item_code,
#             qty=item.qty,
#             rate=item.rate,
#             company=doc.company,
#             fiscal_year=fy,
#             budget_against="Project",
#             against_value=item.project,
#             is_cancel=True
#         )


from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty

# ------------------ On Submit ------------------
def on_submit_purchase_order(doc, method):
    # Determine fiscal year from posting date
    fy = get_fiscal_year(doc.transaction_date or doc.schedule_date or doc.posting_date)[0]

    for item in doc.items:
        # Skip items without a project
        if not item.project:
            continue

        update_consumed_qty(
            item_code=item.item_code,
            qty=item.qty,
            rate=item.rate,
            company=doc.company,
            fiscal_year=fy,
            budget_against="Project",
            against_value=item.project,
            is_cancel=False
        )

# ------------------ On Cancel ------------------
def on_cancel_purchase_order(doc, method):
    # Determine fiscal year from posting date
    fy = get_fiscal_year(doc.transaction_date or doc.schedule_date or doc.posting_date)[0]

    for item in doc.items:
        if not item.project:
            continue

        update_consumed_qty(
            item_code=item.item_code,
            qty=item.qty,
            rate=item.rate,
            company=doc.company,
            fiscal_year=fy,
            budget_against="Project",
            against_value=item.project,
            is_cancel=True
        )