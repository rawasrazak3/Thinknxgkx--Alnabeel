import frappe
from frappe.utils import flt

#update budget on MR submit
def update_budget_on_mr_submit(doc, method):
    # Only for Purchase
    if doc.material_request_type != "Purchase":
        return

    for item in doc.items:
        if not item.project:
            continue

        update_item_budget(
            project=item.project,
            item_code=item.item_code,
            consumed_qty=item.qty
        )

#core budget update function
def update_item_budget(project, item_code, consumed_qty):
    ibd = frappe.db.sql(
        """
        SELECT
            ibd.name,
            ibd.budget_qty,
            ibd.consumed_qty,
            ibd.budget_rate
        FROM `tabItem Budget Detail` ibd
        INNER JOIN `tabQuantity Budget` qb
            ON qb.name = ibd.parent
        WHERE
            qb.project = %s
            AND qb.docstatus = 1
            AND ibd.item_code = %s
        """,
        (project, item_code),
        as_dict=True
    )

    if not ibd:
        frappe.throw(f"No approved Quantity Budget found for item {item_code}")

    ibd = ibd[0]

    new_consumed_qty = flt(ibd.consumed_qty) + flt(consumed_qty)
    consumed_amount = new_consumed_qty * flt(ibd.budget_rate)

    frappe.db.set_value(
        "Item Budget Detail",
        ibd.name,
        {
            "consumed_qty": new_consumed_qty,
            "consumed_amount": consumed_amount
        }
    )

#revert on MR cancel
def revert_budget_on_mr_cancel(doc, method):
    if doc.material_request_type != "Purchase":
        return

    for item in doc.items:
        if not item.project:
            continue

        revert_item_budget(
            project=item.project,
            item_code=item.item_code,
            qty=item.qty
        )

#revert function
def revert_item_budget(project, item_code, qty):
    ibd = frappe.db.sql(
        """
        SELECT
            ibd.name,
            ibd.consumed_qty,
            ibd.budget_rate
        FROM `tabItem Budget Detail` ibd
        INNER JOIN `tabQuantity Budget` qb
            ON qb.name = ibd.parent
        WHERE
            qb.project = %s
            AND qb.docstatus = 1
            AND ibd.item_code = %s
        """,
        (project, item_code),
        as_dict=True
    )

    if not ibd:
        return

    ibd = ibd[0]

    new_consumed_qty = max(
        flt(ibd.consumed_qty) - flt(qty),
        0
    )

    consumed_amount = new_consumed_qty * flt(ibd.budget_rate)

    frappe.db.set_value(
        "Item Budget Detail",
        ibd.name,
        {
            "consumed_qty": new_consumed_qty,
            "consumed_amount": consumed_amount
        }
    )

#Recalculate Quantity Budget
def update_quantity_budget_totals(quantity_budget_name):
    totals = frappe.db.sql(
        """
        SELECT
            SUM(consumed_qty) AS total_consumed_qty,
            SUM(consumed_amount) AS total_consumed_amount
        FROM `tabItem Budget Detail`
        WHERE parent = %s
        """,
        quantity_budget_name,
        as_dict=True
    )[0]

    frappe.db.set_value(
        "Quantity Budget",
        quantity_budget_name,
        {
            "total_consumed_qty": totals.total_consumed_qty or 0,
            "total_consumed_amount": totals.total_consumed_amount or 0
        }
    )
