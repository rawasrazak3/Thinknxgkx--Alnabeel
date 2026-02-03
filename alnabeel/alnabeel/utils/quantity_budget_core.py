# import frappe
# from frappe.utils import flt
# from frappe import _

# def get_quantity_budget(item_code, company, fiscal_year, budget_against, against_value, exclude_doc=None):
#     """
#     Fetch approved Quantity Budget row and consumed quantities,
#     excluding a specific document (like the current PMR) to avoid double-counting.
#     """
#     # Fetch budget row
#     qb = frappe.db.sql("""
#         SELECT 
#             b.name,
#             d.budget_qty,
#             d.budget_amount,
#             b.monthly_distribution,
#             b.action_if_annual_budget_exceeded,
#             b.action_if_accumulated_monthly_budget_exceeded
#         FROM `tabQuantity Budget` b
#         JOIN `tabItem Budget Detail` d ON d.parent = b.name
#         WHERE
#             b.company = %s
#             AND b.fiscal_year = %s
#             AND b.docstatus = 1
#             AND b.{0} = %s
#             AND d.item_code = %s
#     """.format(budget_against),
#     (company, fiscal_year, against_value, item_code),
#     as_dict=True)

#     if not qb:
#         return None

#     qb = qb[0]

#     # Calculate consumed quantities excluding current document
#     consumed = frappe.db.sql("""
#         SELECT 
#             SUM(qty) as consumed_qty,
#             SUM(amount) as consumed_amount
#         FROM `tabMaterial Request Item`
#         WHERE item_code = %s
#             AND docstatus = 1
#             AND parent != %s
#     """, (item_code, exclude_doc or ""), as_dict=True)

#     qb['consumed_qty'] = flt(consumed[0].consumed_qty) if consumed and consumed[0].consumed_qty else 0
#     qb['consumed_amount'] = flt(consumed[0].consumed_amount) if consumed and consumed[0].consumed_amount else 0

#     return qb

import frappe
from frappe.utils import flt
from frappe import _


def get_budget_row(item_code, company, fiscal_year):
    row = frappe.db.sql("""
        SELECT
            d.name,
            d.budget_qty,
            d.revised_qty,
            d.consumed_qty
        FROM `tabQuantity Budget` b
        JOIN `tabItem Budget Detail` d ON d.parent = b.name
        WHERE
            b.company = %s
            AND b.fiscal_year = %s
            AND b.docstatus = 1
            AND d.item_code = %s
        ORDER BY b.modified DESC
        LIMIT 1
    """, (company, fiscal_year, item_code), as_dict=True)

    if not row:
        frappe.throw(_("No Quantity Budget found for Item {0}").format(item_code))

    return row[0]


def get_balance_qty(row):
    base_qty = flt(row.revised_qty) if row.revised_qty else flt(row.budget_qty)
    return base_qty - flt(row.consumed_qty)


def update_consumption(item_code, qty, company, fiscal_year, is_cancel=False):
    row = get_budget_row(item_code, company, fiscal_year)

    balance = get_balance_qty(row)

    if not is_cancel and qty > balance:
        frappe.throw(
            _("Quantity budget exceeded for Item {0}<br>"
              "Available: {1}, Requested: {2}")
            .format(item_code, balance, qty)
        )

    new_consumed = (
        flt(row.consumed_qty) - qty
        if is_cancel else
        flt(row.consumed_qty) + qty
    )

    frappe.db.set_value(
        "Item Budget Detail",
        row.name,
        "consumed_qty",
        new_consumed
    )


def on_mr_submit(doc, method=None):
    for row in doc.items:
        update_consumption(
            item_code=row.item_code,
            qty=row.qty,
            company=doc.company,
            fiscal_year=doc.fiscal_year
        )


def on_mr_cancel(doc, method=None):
    for row in doc.items:
        update_consumption(
            item_code=row.item_code,
            qty=row.qty,
            company=doc.company,
            fiscal_year=doc.fiscal_year,
            is_cancel=True
        )
