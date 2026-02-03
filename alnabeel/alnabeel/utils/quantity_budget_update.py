import frappe
from frappe.utils import flt

def update_budget_and_pmr_on_mr_submit(mr, pmr_name):
    """
    Updates:
    1. Quantity Budget consumed & balance
    2. PMR table balance_qty
    """

    pmr = frappe.get_doc("Project Material Request", pmr_name)

    for mr_row in mr.items:
        if not mr_row.item_code or not mr_row.qty:
            continue

        # ---------------------------
        # UPDATE QUANTITY BUDGET
        # ---------------------------
        qb = frappe.db.sql("""
            SELECT d.name as row_name, d.budget_qty, d.consumed_qty
            FROM `tabQuantity Budget` b
            JOIN `tabQuantity Budget Item` d ON d.parent = b.name
            WHERE b.docstatus = 1
              AND b.company = %s
              AND b.project = %s
              AND d.item_code = %s
            LIMIT 1
        """, (
            mr.company,
            mr_row.project,
            mr_row.item_code
        ), as_dict=True)

        if qb:
            qb = qb[0]
            new_consumed = flt(qb.consumed_qty) + flt(mr_row.qty)
            new_balance = flt(qb.budget_qty) - new_consumed

            frappe.db.set_value(
                "Quantity Budget Item",
                qb.row_name,
                {
                    "consumed_qty": new_consumed,
                    "balance_qty": new_balance
                }
            )

        # ---------------------------
        # UPDATE PMR BALANCE QTY
        # ---------------------------
        for pmr_row in pmr.items:
            if pmr_row.item_code == mr_row.item_code:
                pmr_row.balance_qty = flt(pmr_row.balance_qty) - flt(mr_row.qty)

    pmr.save(ignore_permissions=True)
