import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.utils import get_fiscal_year
from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty

class QuantityBudgetError(frappe.ValidationError):
    pass

class DuplicateBudgetError(frappe.ValidationError):
    pass

class QuantityBudget(Document):
    def validate(self):
        self.validate_budget_against()
        self.validate_duplicate()
        self.set_null_value()
        self.validate_items()
        self.update_consumed_amounts()  # fetch consumed qty/amount from MR/PO

    def validate_budget_against(self):
        if not self.get(frappe.scrub(self.budget_against)):
            frappe.throw(_("{0} is mandatory").format(self.budget_against))

    def validate_duplicate(self):
        budget_against_field = frappe.scrub(self.budget_against)
        budget_against = self.get(budget_against_field)

        items = [d.item_code for d in self.item_budget_detail] or []
        if not items:
            return

        existing_budget = frappe.db.sql(
            """
            SELECT b.name, ba.item_code FROM `tabQuantity Budget` b, `tabItem Budget Detail` ba
            WHERE ba.parent = b.name AND b.docstatus < 2
            AND b.company=%s AND b.{0}=%s AND b.fiscal_year=%s
            AND b.name!=%s AND ba.item_code IN ({1})
            """.format(budget_against_field, ",".join(["%s"] * len(items))),
            tuple([self.company, budget_against, self.fiscal_year, self.name] + items),
            as_dict=True
        )

        for d in existing_budget:
            frappe.throw(
                _("Another Quantity Budget '{0}' already exists for {1} '{2}' and Item '{3}'")
                .format(d.name, self.budget_against, budget_against, d.item_code),
                DuplicateBudgetError
            )

    def set_null_value(self):
        if self.budget_against == "Cost Center":
            self.project = None
        elif self.budget_against == "Project":
            self.cost_center = None

    def validate_items(self):
        for row in self.item_budget_detail:
            if flt(row.budget_qty) <= 0:
                frappe.throw(f"Budget Qty must be > 0 for Item {row.item_code}")
            if flt(row.consumed_qty) > flt(row.budget_qty):
                frappe.throw(f"Consumed Qty cannot exceed Budget Qty for Item {row.item_code}")

    def update_consumed_amounts(self):
        for row in self.item_budget_detail:
            consumed = self.get_budget_consumed(row)
            row.consumed_qty = consumed.get("consumed_qty", 0)
            row.consumed_amount = consumed.get("consumed_amount", 0)

    def get_budget_consumed(self, row):
        """
        Calculate consumed qty/amount from Material Requests and Purchase Orders.
        This calls a utility function that handles MR/PO logic.
        """
        if not self.fiscal_year or not self.company:
            return {"consumed_qty": 0, "consumed_amount": 0}

        # Call your utility function (you must implement this in utils/quantity_budget_consumption.py)
        return update_consumed_qty(
            item_code=row.item_code,
            company=self.company,
            fiscal_year=self.fiscal_year
        )


    def update_consumed_on_submit(doc, method):
        from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty
        for item in doc.items:
            update_consumed_qty(
                item_code=item.item_code,
                qty=item.qty,
                rate=item.rate,
                company=doc.company,
                fiscal_year=get_fiscal_year(doc.transaction_date or doc.posting_date)[0],
                budget_against="Project" if getattr(item, "project", None) else "Cost Center",
                against_value=getattr(item, "project", None) or getattr(item, "cost_center", None),
                is_cancel=False
            )

    def update_consumed_on_cancel(doc, method):
        from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty
        for item in doc.items:
            update_consumed_qty(
                item_code=item.item_code,
                qty=item.qty,
                rate=item.rate,
                company=doc.company,
                fiscal_year=get_fiscal_year(doc.transaction_date or doc.posting_date)[0],
                budget_against="Project" if getattr(item, "project", None) else "Cost Center",
                against_value=getattr(item, "project", None) or getattr(item, "cost_center", None),
                is_cancel=True
            )

@frappe.whitelist()
def get_item_budget_for_project(project):
    """
    Fetch Item Budget Detail table for a given project.
    """
    qb = frappe.get_all("Quantity Budget", filters={"project": project, "docstatus": 1}, fields=["name"])
    if not qb:
        return []

    qb_name = qb[0].name
    items = frappe.get_all(
        "Item Budget Detail",
        filters={"parent": qb_name},
        fields=["item_code", "item_name", "budget_qty", "budget_rate", "budget_amount", "consumed_qty", "consumed_amount"]
    )
    return items

