
# import frappe
# from frappe.utils import flt
# from erpnext.accounts.utils import get_fiscal_year

# def get_consumed_qty(item_code, company, posting_date, budget_against, against_value):
#     fy = get_fiscal_year(posting_date, company=company)[0]
#     fy_doc = frappe.get_doc("Fiscal Year", fy)

#     total_qty = 0
#     total_amount = 0

#     for table, parent, date_field, qty_field, amt_field, project_field in [
#         ("Material Request Item", "Material Request", "transaction_date", "qty", "rate", "project"),
#         ("Purchase Order Item", "Purchase Order", "transaction_date", "qty", "amount", "project"),
#     ]:
#         q = f"""
#             SELECT SUM(i.{qty_field}) qty, SUM(i.{amt_field}) amount
#             FROM `tab{table}` i
#             JOIN `tab{parent}` p ON p.name=i.parent
#             WHERE p.docstatus=1
#               AND p.company=%s
#               AND p.{date_field} BETWEEN %s AND %s
#               AND i.item_code=%s
#               AND i.{project_field}=%s
#         """

#         res = frappe.db.sql(q, (
#             company,
#             fy_doc.year_start_date,
#             fy_doc.year_end_date,
#             item_code,
#             against_value
#         ), as_dict=True)[0]

#         total_qty += flt(res.qty)
#         total_amount += flt(res.amount)

#     return {
#         "consumed_qty": total_qty,
#         "consumed_amount": total_amount
#     }


import frappe
from frappe.utils import flt, getdate, get_last_day
from erpnext.accounts.utils import get_fiscal_year
from frappe import _

def update_consumed_qty(item_code, company, fiscal_year, budget_against=None, against_value=None, is_cancel=False, qty=None, rate=None):
    """
    Calculate consumed quantity and amount for a given item from Material Requests (MR) and Purchase Orders (PO)
    and optionally update Quantity Budget child table.

    Parameters:
        item_code (str): Item code
        company (str): Company
        fiscal_year (str): Fiscal year
        budget_against (str): "Project" or "Cost Center"
        against_value (str): Value of Project / Cost Center
        is_cancel (bool): True if the MR/PO is being cancelled
        qty (float): Quantity from current MR/PO
        rate (float): Rate from current MR/PO

    Returns:
        dict: {"consumed_qty": float, "consumed_amount": float}
    """
    consumed_qty = 0.0
    consumed_amount = 0.0

    # ---------------- Material Requests ----------------
    mr_condition = f"child.item_code = '{item_code}' AND parent.docstatus = 1 AND parent.company = '{company}'"
    if budget_against and against_value:
        mr_condition += f" AND child.{budget_against.lower()} = '{against_value}'"

    mr_data = frappe.db.sql(
        f"""
        SELECT SUM(child.stock_qty) AS total_qty, SUM(child.amount) AS total_amount
        FROM `tabMaterial Request Item` child, `tabMaterial Request` parent
        WHERE child.parent = parent.name
        AND {mr_condition}
        """, as_dict=True
    )
    if mr_data:
        consumed_qty += flt(mr_data[0].total_qty)
        consumed_amount += flt(mr_data[0].total_amount)

    # ---------------- Purchase Orders (Unbilled) ----------------
    po_condition = f"child.item_code = '{item_code}' AND parent.docstatus = 1 AND parent.company = '{company}'"
    if budget_against and against_value:
        po_condition += f" AND child.{budget_against.lower()} = '{against_value}'"

    po_data = frappe.db.sql(
    f"""
    SELECT SUM(child.qty) AS total_qty, 
           SUM(child.amount) AS total_amount
    FROM `tabPurchase Order Item` child, `tabPurchase Order` parent
    WHERE child.parent = parent.name
    AND {po_condition}
    """, as_dict=True
)

    if po_data:
        consumed_qty += flt(po_data[0].total_qty)
        consumed_amount += flt(po_data[0].total_amount)

    # ---------------- Include Current Transaction ----------------
    if qty and rate:
        if is_cancel:
            consumed_qty -= flt(qty)
            consumed_amount -= flt(qty) * flt(rate)
        else:
            consumed_qty += flt(qty)
            consumed_amount += flt(qty) * flt(rate)

    return {
        "consumed_qty": flt(consumed_qty),
        "consumed_amount": flt(consumed_amount)
    }


def get_item_budget_consumed(item_code, company, fiscal_year, budget_against=None, against_value=None):
    """
    Helper function to fetch only consumed quantities from MR and PO for Quantity Budget child table
    """
    data = update_consumed_qty(
        item_code=item_code,
        company=company,
        fiscal_year=fiscal_year,
        budget_against=budget_against,
        against_value=against_value
    )
    return data



@frappe.whitelist()
def get_project_budget(project):
    """
    Fetch the Item Budget Detail table for a given project
    """
    # Get Quantity Budget linked to the project
    qb_list = frappe.get_all("Quantity Budget", filters={"project": project, "docstatus": 1}, fields=["name"])
    if not qb_list:
        return []

    qb_name = qb_list[0].name

    # Get child table data
    items = frappe.get_all(
        "Item Budget Detail",
        filters={"parent": qb_name},
        fields=["item_code", "item_name", "budget_qty", "budget_rate", "budget_amount", "account"]
    )

    return items