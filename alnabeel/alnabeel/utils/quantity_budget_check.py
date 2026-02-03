# # # # from datetime import date
# # # # import frappe
# # # # from frappe.utils import flt
# # # # from frappe import _
# # # # from erpnext.accounts.utils import get_fiscal_year
# # # # from alnabeel.alnabeel.utils.quantity_budget_core import get_quantity_budget
# # # # from alnabeel.alnabeel.utils.monthly_distribution import get_monthly_budget


# # # # def check_quantity_budget(doc, item):
# # # #     doc_date = (
# # # #         doc.get("posting_date")
# # # #         or doc.get("transaction_date")
# # # #         or doc.get("schedule_date")
# # # #     )
# # # #     if not doc_date:
# # # #         return

# # # #     fiscal_year = get_fiscal_year(doc_date)[0]

# # # #     budget_against = "project" if item.project else "cost_center"
# # # #     against_value = item.project or item.cost_center

# # # #     qb = get_quantity_budget(
# # # #         item_code=item.item_code,
# # # #         company=doc.company,
# # # #         fiscal_year=fiscal_year,
# # # #         budget_against=budget_against,
# # # #         against_value=against_value
# # # #     )
# # # #     if not qb:
# # # #         return

# # # #     # QUANTITY CHECK
# # # #     new_qty = flt(item.qty)
# # # #     total_consumed_qty = flt(qb.consumed_qty) + new_qty

# # # #     allowed_qty = flt(
# # # #         qb.revised_budget_qty if qb.revised_budget_qty else qb.budget_qty
# # # #     )

# # # #     if allowed_qty and total_consumed_qty > allowed_qty:
# # # #         action = qb.action_if_annual_budget_exceeded or "Stop"
# # # #         _handle_action(action, item.item_code, "Quantity Budget")

# # # #     # AMOUNT CHECK
# # # #     new_amount = flt(item.qty) * flt(item.rate)
# # # #     total_consumed_amount = flt(qb.consumed_amount) + new_amount

# # # #     allowed_amount = flt(
# # # #         qb.revised_budget_amount if qb.revised_budget_amount else qb.budget_amount
# # # #     )

# # # #     if allowed_amount and total_consumed_amount > allowed_amount:
# # # #         action = qb.action_if_annual_budget_exceeded or "Stop"
# # # #         _handle_action(action, item.item_code, "Amount Budget")


# # # # def _handle_action(action, item_code, label):
# # # #     if action == "Stop":
# # # #         frappe.throw(_("{0} exceeded for Item {1}").format(label, item_code))
# # # #     elif action == "Warn":
# # # #         frappe.msgprint(_("{0} exceeded for Item {1}").format(label, item_code))


# # # import frappe
# # # from frappe.utils import flt
# # # from frappe import _
# # # from erpnext.accounts.utils import get_fiscal_year
# # # from alnabeel.alnabeel.utils.quantity_budget_core import get_quantity_budget
# # # from alnabeel.alnabeel.utils.monthly_distribution import get_monthly_budget


# # # def check_quantity_budget(doc, item, on_submit=False):
# # #     """
# # #     on_submit = False  -> Warn
# # #     on_submit = True   -> Stop
# # #     """

# # #     doc_date = (
# # #         doc.get("posting_date")
# # #         or doc.get("transaction_date")
# # #         or doc.get("schedule_date")
# # #     )
# # #     if not doc_date:
# # #         return

# # #     fiscal_year = get_fiscal_year(doc_date)[0]

# # #     budget_against = "project" if item.project else "cost_center"
# # #     against_value = item.project or item.cost_center

# # #     qb = get_quantity_budget(
# # #         item_code=item.item_code,
# # #         company=doc.company,
# # #         fiscal_year=fiscal_year,
# # #         budget_against=budget_against,
# # #         against_value=against_value
# # #     )

# # #     if not qb:
# # #         return

# # #     # --------------------------------------------------
# # #     # EFFECTIVE ANNUAL BUDGET (Revised > Original)
# # #     # --------------------------------------------------
# # #     effective_budget_qty = flt(
# # #         qb.revised_budget_qty if qb.revised_budget_qty > 0 else qb.budget_qty
# # #     )

# # #     effective_budget_amount = flt(
# # #         qb.revised_budget_amount if qb.revised_budget_amount > 0 else qb.budget_amount
# # #     )

# # #     new_qty = flt(item.qty)
# # #     new_amount = flt(item.qty) * flt(item.rate)

# # #     action = "Stop" if on_submit else "Warn"

# # #     # --------------------------------------------------
# # #     # ANNUAL QUANTITY CHECK
# # #     # --------------------------------------------------
# # #     if effective_budget_qty:
# # #         total_qty = flt(qb.consumed_qty) + new_qty
# # #         if total_qty > effective_budget_qty:
# # #             _handle_action(
# # #                 action,
# # #                 item.item_code,
# # #                 "Annual Quantity Budget"
# # #             )

# # #     # --------------------------------------------------
# # #     # ANNUAL AMOUNT CHECK
# # #     # --------------------------------------------------
# # #     if effective_budget_amount:
# # #         total_amount = flt(qb.consumed_amount) + new_amount
# # #         if total_amount > effective_budget_amount:
# # #             _handle_action(
# # #                 action,
# # #                 item.item_code,
# # #                 "Annual Amount Budget"
# # #             )

# # #     # --------------------------------------------------
# # #     # MONTHLY BUDGET CHECK
# # #     # --------------------------------------------------
# # #     monthly_budget = get_monthly_budget(
# # #         quantity_budget=qb.name,
# # #         posting_date=doc_date
# # #     )

# # #     if not monthly_budget:
# # #         return

# # #     # MONTHLY QUANTITY CHECK
# # #     if flt(monthly_budget.budget_qty):
# # #         monthly_total_qty = flt(monthly_budget.consumed_qty) + new_qty
# # #         if monthly_total_qty > flt(monthly_budget.budget_qty):
# # #             _handle_action(
# # #                 action,
# # #                 item.item_code,
# # #                 "Monthly Quantity Budget"
# # #             )

# # #     # MONTHLY AMOUNT CHECK
# # #     if flt(monthly_budget.budget_amount):
# # #         monthly_total_amount = flt(monthly_budget.consumed_amount) + new_amount
# # #         if monthly_total_amount > flt(monthly_budget.budget_amount):
# # #             _handle_action(
# # #                 action,
# # #                 item.item_code,
# # #                 "Monthly Amount Budget"
# # #             )


# # # def _handle_action(action, item_code, label):
# # #     if action == "Stop":
# # #         frappe.throw(
# # #             _("{0} exceeded for Item {1}").format(label, item_code)
# # #         )
# # #     else:
# # #         frappe.msgprint(
# # #             _("{0} exceeded for Item {1}").format(label, item_code),
# # #             indicator="orange"
# # #         )
# # import frappe
# # from frappe.utils import flt
# # from frappe import _
# # from erpnext.accounts.utils import get_fiscal_year
# # from alnabeel.alnabeel.utils.quantity_budget_core import get_quantity_budget
# # from alnabeel.alnabeel.utils.monthly_distribution import get_monthly_budget


# # def check_quantity_budget(doc, item, on_submit=False):
# #     """
# #     Check Quantity Budget for a Material Request / Project Material Request.

# #     - Handles Item-based and Account-based rows
# #     - Annual & Monthly Qty/Amount check
# #     - on_submit=True -> Stop, on_submit=False -> Warn
# #     """
# #     doc_date = doc.get("posting_date") or doc.get("transaction_date") or doc.get("schedule_date")
# #     if not doc_date:
# #         return

# #     fiscal_year = get_fiscal_year(doc_date)[0]
# #     action = "Stop" if on_submit else "Warn"

# #     # -------------------------------
# #     # Detect Item vs Account Based
# #     # -------------------------------
# #     is_account_based = not item.get("item_code") and (item.get("account") or item.get("expense_account"))
# #     item_code_for_budget = item.get("item_code") if not is_account_based else "ACCOUNT_ITEM"

# #     # -------------------------------
# #     # Determine Budget Against
# #     # -------------------------------
# #     budget_against = "project" if item.get("project") else "cost_center"
# #     against_value = item.get("project") or item.get("cost_center")

# #     if is_account_based:
# #         budget_against = "account"
# #         against_value = item.get("account") or item.get("expense_account")

# #     # -------------------------------
# #     # Fetch Quantity Budget
# #     # -------------------------------
# #     qb = get_quantity_budget(
# #         item_code=item.get("item_code") if not is_account_based else None,
# #         company=doc.company,
# #         fiscal_year=fiscal_year,
# #         budget_against=budget_against,
# #         against_value=against_value,
# #         exclude_doc=doc.name  # exclude current PMR
# #     )

# #     if not qb:
# #         return

# #     # -------------------------------
# #     # Effective Budget Values
# #     # -------------------------------
# #     effective_budget_qty = flt(qb.revised_budget_qty if flt(qb.revised_budget_qty) > 0 else qb.budget_qty)
# #     effective_budget_amount = flt(qb.revised_budget_amount if flt(qb.revised_budget_amount) > 0 else qb.budget_amount)

# #     # -------------------------------
# #     # Current Item Qty & Amount
# #     # -------------------------------
# #     current_qty = flt(item.get("qty")) if not is_account_based else 0
# #     current_amount = flt(item.get("amount") or (flt(item.get("qty")) * flt(item.get("rate"))))

# #     # -------------------------------
# #     # Annual Quantity Check (exclude current MR from consumed)
# #     # -------------------------------
# #     annual_consumed_qty = flt(qb.consumed_qty)  # past consumption only
# #     if current_qty > 0 and (annual_consumed_qty + current_qty) > effective_budget_qty:
# #         _handle_action(action, item_code_for_budget, "Annual Quantity Budget")

# #     # -------------------------------
# #     # Annual Amount Check
# #     # -------------------------------
# #     annual_consumed_amount = flt(qb.consumed_amount)
# #     if current_amount > 0 and (annual_consumed_amount + current_amount) > effective_budget_amount:
# #         _handle_action(action, item_code_for_budget, "Annual Amount Budget")

# #     # -------------------------------
# #     # Monthly Budget Check
# #     # -------------------------------
# #     monthly_budget = get_monthly_budget(
# #         budget_amount = effective_budget_amount,
# #         monthly_distribution = qb.monthly_distribution,
# #         posting_date = doc_date
# #     )

# #     if monthly_budget:
# #         # Monthly Quantity Check
# #         monthly_budget_qty = flt(monthly_budget.get("budget_qty", 0))
# #         monthly_consumed_qty = flt(monthly_budget.get("consumed_qty", 0))
# #         if current_qty > 0 and (monthly_consumed_qty + current_qty) > monthly_budget_qty:
# #             _handle_action(action, item_code_for_budget, "Monthly Quantity Budget")

# #         # Monthly Amount Check
# #         monthly_budget_amount = flt(monthly_budget.get("budget_amount", 0))
# #         monthly_consumed_amount = flt(monthly_budget.get("consumed_amount", 0))
# #         if current_amount > 0 and (monthly_consumed_amount + current_amount) > monthly_budget_amount:
# #             _handle_action(action, item_code_for_budget, "Monthly Amount Budget")


# # def _handle_action(action, item_code, label):
# #     """
# #     Handle Stop or Warn based on action type
# #     """
# #     if action == "Stop":
# #         frappe.throw(_("{0} exceeded for Item {1}").format(label, item_code))
# #     else:
# #         frappe.msgprint(
# #             _("{0} exceeded for Item {1}").format(label, item_code),
# #             indicator="orange"
# #         )

# # # ------------------------------------------------
# # # check_item_budget_exceeded
# # # ------------------------------------------------
# # def check_item_budget_exceeded(row, balance_qty):
# #     if flt(row.request_qty) > flt(balance_qty):
# #         frappe.throw(
# #             _("Quantity Budget exceeded for Item {0}. Balance Qty: {1}")
# #             .format(row.item_code, balance_qty),
# #             frappe.ValidationError
# #         )




# import frappe
# from frappe.utils import flt
# from frappe import _
# from erpnext.accounts.utils import get_fiscal_year
# from alnabeel.alnabeel.utils.quantity_budget_core import get_quantity_budget
# from alnabeel.alnabeel.utils.monthly_distribution import get_monthly_budget

# def check_quantity_budget(doc, item, on_submit=False):
#     """
#     Checks Annual & Monthly Quantity/Amount budgets
#     """
#     doc_date = doc.get("posting_date") or doc.get("transaction_date") or doc.get("schedule_date")
#     if not doc_date:
#         return

#     fiscal_year = get_fiscal_year(doc_date)[0]
#     action = "Stop" if on_submit else "Warn"

#     budget_against = "project" if item.get("project") else "cost_center"
#     against_value = item.get("project") or item.get("cost_center")
#     item_code_for_budget = item.get("item_code")

#     qb = get_quantity_budget(
#         item_code=item.get("item_code"),
#         company=doc.company,
#         fiscal_year=fiscal_year,
#         budget_against=budget_against,
#         against_value=against_value,
#         exclude_doc=doc.name
#     )

#     if not qb:
#         return

#     effective_qty = flt(qb.revised_budget_qty if flt(qb.revised_budget_qty) > 0 else qb.budget_qty)
#     effective_amount = flt(qb.revised_budget_amount if flt(qb.revised_budget_amount) > 0 else qb.budget_amount)

#     current_qty = flt(item.get("qty"))
#     current_amount = flt(item.get("qty") * flt(item.get("rate")))

#     # Annual Checks
#     if effective_qty and (qb['consumed_qty'] + current_qty) > effective_qty:
#         _handle_action(action, item_code_for_budget, "Annual Quantity Budget")

#     if effective_amount and (qb['consumed_amount'] + current_amount) > effective_amount:
#         _handle_action(action, item_code_for_budget, "Annual Amount Budget")

#     # Monthly Checks
#     monthly_budget = get_monthly_budget(
#         budget_amount=effective_amount,
#         monthly_distribution=qb.monthly_distribution,
#         posting_date=doc_date
#     )

#     if monthly_budget:
#         if current_qty and (monthly_budget['consumed_qty'] + current_qty) > flt(monthly_budget['budget_qty']):
#             _handle_action(action, item_code_for_budget, "Monthly Quantity Budget")
#         if current_amount and (monthly_budget['consumed_amount'] + current_amount) > flt(monthly_budget['budget_amount']):
#             _handle_action(action, item_code_for_budget, "Monthly Amount Budget")


# def _handle_action(action, item_code, label):
#     if action=="Stop":
#         frappe.throw(_("{0} exceeded for Item {1}").format(label, item_code))
#     else:
#         frappe.msgprint(_("{0} exceeded for Item {1}").format(label, item_code), indicator="orange")



import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from alnabeel.alnabeel.utils.quantity_budget_core import get_quantity_budget
from alnabeel.alnabeel.utils.quantity_budget_consumption import get_consumed_qty
from alnabeel.alnabeel.utils.monthly_distribution import get_monthly_budget

def check_quantity_budget(doc, item, on_submit=False):
    posting_date = getattr(doc, "posting_date", None) \
    or getattr(doc, "transaction_date", None) \
    or getattr(doc, "schedule_date", None)

    fy = get_fiscal_year(posting_date)[0]

    budget = get_quantity_budget(
        item_code=item.item_code,
        company=doc.company,
        fiscal_year=fy,
        budget_against="project",
        against_value=item.project
    )

    if not budget:
        return

    consumed = get_consumed_qty(
        item.item_code,
        doc.company,
        posting_date,
        "Project",
        item.project
    )

    effective_qty = (
        flt(budget.revised_budget_qty)
        if flt(budget.revised_budget_qty) > 0
        else flt(budget.budget_qty)
    )

    balance_qty = effective_qty - consumed["consumed_qty"]

    if item.qty > balance_qty:
        frappe.throw(
            _("Budget exceeded for Item {0}. Remaining Qty: {1}")
            .format(item.item_code, balance_qty)
        )

    monthly_limit = get_monthly_budget(
        effective_qty,
        budget.monthly_distribution,
        posting_date
    )

    if item.qty > monthly_limit:
        frappe.throw(
            _("Monthly budget exceeded for Item {0}")
            .format(item.item_code)
        )
