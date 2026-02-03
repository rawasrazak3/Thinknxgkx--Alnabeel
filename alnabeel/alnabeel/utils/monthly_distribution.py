# import frappe
# from frappe.utils import flt

# # def get_monthly_budget(budget_amount, monthly_distribution, posting_date):
# #     """Return allowed monthly budget based on distribution"""
# #     if not monthly_distribution:
# #         return flt(budget_amount) / 12

# #     md = frappe.get_doc("Monthly Distribution", monthly_distribution)
# #     month = posting_date.strftime("%B").lower()

# #     percent = flt(md.get(month))
# #     return flt(budget_amount) * (percent / 100)

# def get_monthly_budget(budget_amount, monthly_distribution, posting_date):
#     """Return allowed monthly budget based on distribution"""
#     if not monthly_distribution:
#         budget = flt(budget_amount) / 12
#     else:
#         md = frappe.get_doc("Monthly Distribution", monthly_distribution)
#         month = posting_date.strftime("%B").lower()
#         percent = flt(md.get(month))
#         budget = flt(budget_amount) * (percent / 100)

#     return {
#         "budget_qty": budget,        # allowed monthly quantity
#         "budget_amount": budget,     # allowed monthly amount (can be same as qty for now)
#         "consumed_qty": 0,           # you can calculate from MR if needed
#         "consumed_amount": 0         # same here
#     }


import frappe
from frappe.utils import flt

def get_monthly_budget(budget_qty, monthly_distribution, posting_date):
    if not monthly_distribution:
        return flt(budget_qty) / 12

    md = frappe.get_doc("Monthly Distribution", monthly_distribution)
    month = posting_date.strftime("%B").lower()
    percent = flt(md.get(month))

    return flt(budget_qty) * percent / 100
