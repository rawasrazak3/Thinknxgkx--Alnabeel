import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):

    return [
        {
            "label": _(filters.get("budget_against")),
            "fieldname": "dimension",
            "fieldtype": "Link",
            "options": filters.get("budget_against"),
            "width": 150,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 150,
        },
        {
            "label": _("Budget Rate"),
            "fieldname": "budget_rate",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Budget Qty"),
            "fieldname": "budget_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Consumed Qty"),
            "fieldname": "consumed_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Variance Qty"),
            "fieldname": "variance_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Budget Amount"),
            "fieldname": "budget_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Consumed Amount"),
            "fieldname": "consumed_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Variance Amount"),
            "fieldname": "variance_amount",
            "fieldtype": "Currency",
            "width": 140,
        },
    ]


def get_data(filters):

    budget_against_value = filters.get("budget_against")
    dimension_field = "project" if budget_against_value == "Project" else "cost_center"

    conditions = ["qb.docstatus = 1"]
    values = {}

    conditions.append("qb.budget_against = %(budget_against)s")
    values["budget_against"] = budget_against_value

    if filters.get("company"):
        conditions.append("qb.company = %(company)s")
        values["company"] = filters.get("company")

    if filters.get("from_fiscal_year") and filters.get("to_fiscal_year"):
        conditions.append("""
            qb.fiscal_year BETWEEN %(from_fiscal_year)s
            AND %(to_fiscal_year)s
        """)
        values["from_fiscal_year"] = filters.get("from_fiscal_year")
        values["to_fiscal_year"] = filters.get("to_fiscal_year")

    if filters.get("budget_against_filter"):
        conditions.append(f"qb.{dimension_field} IN %(dimension_filter)s")
        values["dimension_filter"] = tuple(filters.get("budget_against_filter"))

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            qb.{dimension_field} as dimension,
            ibd.item_code,
            ibd.item_name,
            ibd.account,
            ibd.budget_rate,
            SUM(ibd.budget_qty) as budget_qty,
            SUM(ibd.consumed_qty) as consumed_qty,
            SUM(ibd.budget_amount) as budget_amount,
            SUM(ibd.consumed_amount) as consumed_amount
        FROM
            `tabQuantity Budget` qb
        JOIN
            `tabItem Budget Detail` ibd
            ON ibd.parent = qb.name
        WHERE
            {where_clause}
        GROUP BY
            qb.{dimension_field},
            ibd.item_code,
            ibd.item_name,
            ibd.account
        ORDER BY
            qb.{dimension_field}, ibd.item_code
    """

    records = frappe.db.sql(query, values, as_dict=1)

    data = []

    for r in records:
        variance_qty = flt(r.budget_qty) - flt(r.consumed_qty)
        variance_amount = flt(r.budget_amount) - flt(r.consumed_amount)

        data.append({
            "dimension": r.dimension,
            "item_code": r.item_code,
            "item_name": r.item_name,
            "account": r.account,
            "budget_rate": r.budget_rate,
            "budget_qty": r.budget_qty,
            "consumed_qty": r.consumed_qty,
            "variance_qty": variance_qty,
            "budget_amount": r.budget_amount,
            "consumed_amount": r.consumed_amount,
            "variance_amount": variance_amount,
        })

    return data
