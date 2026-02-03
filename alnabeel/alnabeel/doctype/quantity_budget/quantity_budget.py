
# from erpnext.accounts.doctype.budget import budget
# import frappe
# from frappe import _
# from frappe.model.document import Document
# from frappe.utils import flt
# from erpnext.accounts.utils import get_fiscal_year
# from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty

# class QuantityBudgetError(frappe.ValidationError):
#     pass

# class DuplicateBudgetError(frappe.ValidationError):
#     pass

# class QuantityBudget(Document):
#     def validate(self):
#         self.validate_budget_against()
#         self.validate_duplicate()
#         self.set_null_value()
#         self.validate_items()
#         self.update_consumed_amounts()  # fetch consumed qty/amount from MR/PO

#     def validate_budget_against(self):
#         if not self.get(frappe.scrub(self.budget_against)):
#             frappe.throw(_("{0} is mandatory").format(self.budget_against))

#     def validate_duplicate(self):
#         budget_against_field = frappe.scrub(self.budget_against)
#         budget_against = self.get(budget_against_field)

#         items = [d.item_code for d in self.item_budget_detail] or []
#         if not items:
#             return

#         existing_budget = frappe.db.sql(
#             """
#             SELECT b.name, ba.item_code FROM `tabQuantity Budget` b, `tabItem Budget Detail` ba
#             WHERE ba.parent = b.name AND b.docstatus < 2
#             AND b.company=%s AND b.{0}=%s AND b.fiscal_year=%s
#             AND b.name!=%s AND ba.item_code IN ({1})
#             """.format(budget_against_field, ",".join(["%s"] * len(items))),
#             tuple([self.company, budget_against, self.fiscal_year, self.name] + items),
#             as_dict=True
#         )

#         for d in existing_budget:
#             frappe.throw(
#                 _("Another Quantity Budget '{0}' already exists for {1} '{2}' and Item '{3}'")
#                 .format(d.name, self.budget_against, budget_against, d.item_code),
#                 DuplicateBudgetError
#             )

#     def set_null_value(self):
#         if self.budget_against == "Cost Center":
#             self.project = None
#         elif self.budget_against == "Project":
#             self.cost_center = None

#     def validate_items(self):
#         for row in self.item_budget_detail:
#             if flt(row.budget_qty) <= 0:
#                 frappe.throw(f"Budget Qty must be > 0 for Item {row.item_code}")
#             if flt(row.consumed_qty) > flt(row.budget_qty):
#                 frappe.throw(f"Consumed Qty cannot exceed Budget Qty for Item {row.item_code}")

            
#         item = frappe.db.get_value(
#             "Item Budget Detail",
#             {"parent": budget[0].name, "item_code": row.item_code},
#             ["budget_qty", "consumed_qty"],
#             as_dict=True
#         )
#         if not item:
#             return

#         balance = flt(item.budget_qty) - flt(item.consumed_qty)

#         if row.qty > balance:
#             frappe.throw(
#                 _("Quantity Budget exceeded for Item {0}. Balance Qty: {1}").format(row.item_code, balance)
#             )

#              # Update Balance Qty
#             row.balance_qty = flt(row.budget_qty) - flt(row.consumed_qty)

#     def update_consumed_amounts(self):
#         for row in self.item_budget_detail:
#             consumed = self.get_budget_consumed(row)
#             row.consumed_qty = consumed.get("consumed_qty", 0)
#             row.consumed_amount = consumed.get("consumed_amount", 0)
#              # Update Balance Qty
#             row.balance_qty = flt(row.budget_qty) - row.consumed_qty

#     def get_budget_consumed(self, row):
#         if not self.fiscal_year or not self.company:
#             return {"consumed_qty": 0, "consumed_amount": 0}

#         budget_against = self.budget_against

#         if budget_against == "Project":
#             against_value = self.project
#         else:
#             against_value = self.cost_center

#         if not against_value:
#             return {"consumed_qty": 0, "consumed_amount": 0}

#         return update_consumed_qty(
#             item_code=row.item_code,
#             company=self.company,
#             fiscal_year=self.fiscal_year,
#             budget_against=budget_against,
#             against_value=against_value
#         )


#     def update_consumed_on_submit(doc, method):
#         from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty
#         for item in doc.items:
#             update_consumed_qty(
#                 item_code=item.item_code,
#                 qty=item.qty,
#                 rate=item.rate,
#                 company=doc.company,
#                 fiscal_year=get_fiscal_year(doc.transaction_date or doc.posting_date)[0],
#                 budget_against="Project" if getattr(item, "project", None) else "Cost Center",
#                 against_value=getattr(item, "project", None) or getattr(item, "cost_center", None),
#                 is_cancel=False
#             )

#     def update_consumed_on_cancel(doc, method):
#         from alnabeel.alnabeel.utils.quantity_budget_consumption import update_consumed_qty
#         for item in doc.items:
#             update_consumed_qty(
#                 item_code=item.item_code,
#                 qty=item.qty,
#                 rate=item.rate,
#                 company=doc.company,
#                 fiscal_year=get_fiscal_year(doc.transaction_date or doc.posting_date)[0],
#                 budget_against="Project" if getattr(item, "project", None) else "Cost Center",
#                 against_value=getattr(item, "project", None) or getattr(item, "cost_center", None),
#                 is_cancel=True
#             )

# @frappe.whitelist()
# def get_item_budget_for_project(project):
#     """
#     Fetch Item Budget Detail table for a given project.
#     """
#     qb = frappe.get_all("Quantity Budget", filters={"project": project, "docstatus": 1}, fields=["name"])
#     if not qb:
#         return []

#     qb_name = qb[0].name
#     items = frappe.get_all(
#         "Item Budget Detail",
#         filters={"parent": qb_name},
#         fields=["item_code", "item_name", "budget_qty","account", "budget_rate", "budget_amount", "consumed_qty", "consumed_amount","balance_qty"]
#     )
#     return items

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_months
from erpnext.accounts.utils import get_fiscal_year

# =====================================================
# Exceptions
# =====================================================
class QuantityBudgetError(frappe.ValidationError):
    pass

class DuplicateBudgetError(frappe.ValidationError):
    pass


# =====================================================
# Quantity Budget DocType
# =====================================================
class QuantityBudget(Document):

    def validate(self):
        self.validate_duplicate()
        self.set_null_values()
        self.update_consumed_values()

    def on_submit(self):
        self.update_consumed_values()

    def on_cancel(self):
        self.reverse_consumed_values()

    # -------------------------------------------------
    # Duplicate Budget Check
    # -------------------------------------------------
    def validate_duplicate(self):
        budget_against_field = frappe.scrub(self.budget_against)
        against_value = self.get(budget_against_field)

        items = [d.item_code for d in self.item_budget_detail] or []
        if not items:
            return

        existing = frappe.db.sql(
            f"""
            SELECT b.name, d.item_code
            FROM `tabQuantity Budget` b
            INNER JOIN `tabItem Budget Detail` d ON d.parent = b.name
            WHERE b.docstatus < 2
              AND b.company = %s
              AND b.{budget_against_field} = %s
              AND b.fiscal_year = %s
              AND b.name != %s
              AND d.item_code IN ({','.join(['%s'] * len(items))})
            """,
            tuple([self.company, against_value, self.fiscal_year, self.name] + items),
            as_dict=True
        )

        for d in existing:
            frappe.throw(
                _("Duplicate Quantity Budget {0} exists for Item {1}")
                .format(d.name, d.item_code),
                DuplicateBudgetError
            )

    # def validate_duplicate(self):
    #     budget_against_field = frappe.scrub(self.budget_against)
    #     against_value = self.get(budget_against_field)

    #     items = [d.item_code for d in self.item_budget_detail] or []
    #     if not items:
    #         return

    #     # If this is a revised budget, ignore the original parent in the check
    #     parent_name_to_ignore = getattr(self, "revised_from", self.name)

    #     existing = frappe.db.sql(
    #         f"""
    #         SELECT b.name, d.item_code
    #         FROM `tabQuantity Budget` b
    #         INNER JOIN `tabItem Budget Detail` d ON d.parent = b.name
    #         WHERE b.docstatus = 1
    #         AND b.company = %s
    #         AND b.{budget_against_field} = %s
    #         AND b.fiscal_year = %s
    #         AND b.name != %s
    #         AND d.item_code IN ({','.join(['%s'] * len(items))})
    #         """,
    #         tuple([self.company, against_value, self.fiscal_year, parent_name_to_ignore] + items),
    #         as_dict=True
    #     )

    #     for d in existing:
    #         frappe.throw(
    #             _("Duplicate Quantity Budget {0} exists for Item {1}").format(d.name, d.item_code),
    #             DuplicateBudgetError
    #         )


    # -------------------------------------------------
    # Set Null Values
    # -------------------------------------------------
    def set_null_values(self):
        if self.budget_against == "Cost Center":
            self.project = None
        else:
            self.cost_center = None

    # -------------------------------------------------
    # Update / Reverse Consumption
    # -------------------------------------------------
    def update_consumed_values(self):
        for row in self.item_budget_detail:
            consumed = get_total_consumption(
                company=self.company,
                fiscal_year=self.fiscal_year,
                account=row.account,
                item_code=row.item_code,
                budget_against=self.budget_against,
                against_value=self.project or self.cost_center
            )
            row.consumed_qty = consumed["qty"]
            row.consumed_amount = consumed["amount"]
            row.balance_qty = flt(row.budget_qty) - row.consumed_qty

    def reverse_consumed_values(self):
        self.update_consumed_values()

# =====================================================
# GET REVISED BUDGET FOR VALIDATION
# =====================================================
# def get_budget_for_validation(company, posting_date, account, item_code=None, budget_against=None, against_value=None):
#     """
#     Returns the latest budget row for validation.
#     Uses revised budget if exists, otherwise original budget.
#     """
#     fiscal_year = get_fiscal_year(posting_date, company=company)[0]

#     # Get submitted budgets ordered by revision_no DESC
#     budgets = frappe.get_all(
#         "Quantity Budget",
#         filters={
#             "company": company,
#             "fiscal_year": fiscal_year,
#             "docstatus": 1
#         },
#         fields=["name", "budget_against", "project", "cost_center", "revision_no"],
#         order_by="revision_no desc"
#     )

#     for b in budgets:
#         # Check budget_against
#         if budget_against == "Project" and b.project != against_value:
#             continue
#         if budget_against == "Cost Center" and b.cost_center != against_value:
#             continue

#         row = None
#         if item_code:
#             # Item-level budget
#             rows = frappe.get_all(
#                 "Item Budget Detail",
#                 filters={"parent": b.name, "account": account, "item_code": item_code},
#                 fields=[
#                     "budget_qty", "budget_rate", "budget_amount",
#                     "revised_budget_qty", "revised_budget_rate", "revised_budget_amount",
#                     "consumed_qty", "consumed_amount"
#                 ]
#             )
#             if rows:
#                 row = rows[0]
#         else:
#             # Account-level budget
#             rows = frappe.get_all(
#                 "Item Budget Detail",
#                 filters={"parent": b.name, "account": account},
#                 fields=[
#                     "budget_amount", "revised_budget_amount",
#                     "consumed_amount"
#                 ]
#             )
#             if rows:
#                 row = rows[0]
        
#         if row:
#             # Use revised budget if available
#             budget_qty = row.get("revised_budget_qty") or row.get("budget_qty") or 0
#             budget_rate = row.get("revised_budget_rate") or row.get("budget_rate") or 0
#             budget_amount = row.get("revised_budget_amount") or (flt(budget_qty) * flt(budget_rate)) or row.get("budget_amount")
            
#             consumed_qty = flt(row.get("consumed_qty") or 0)
#             consumed_amount = flt(row.get("consumed_amount") or 0)

#             return {
#                 "budget_qty": budget_qty,
#                 "budget_rate": budget_rate,
#                 "budget_amount": budget_amount,
#                 "consumed_qty": consumed_qty,
#                 "consumed_amount": consumed_amount
#             }

#     return None

# def validate_quantity_budget(company, posting_date, account, qty=0, amount=0, item_code=None, budget_against=None, against_value=None, action="Stop"):
#     """
#     Validates if quantity/amount is within budget.
#     Stops or warns based on `action`.
#     """
#     budget_row = get_budget_for_validation(company, posting_date, account, item_code, budget_against, against_value)

#     if not budget_row:
#         # No budget found → skip validation
#         return

#     projected_qty = flt(budget_row["consumed_qty"]) + flt(qty)
#     projected_amount = flt(budget_row["consumed_amount"]) + flt(amount)

#     exceeded_qty = item_code and projected_qty > flt(budget_row["budget_qty"])
#     exceeded_amt = projected_amount > flt(budget_row["budget_amount"])

#     if exceeded_qty or exceeded_amt:
#         msg = _(
#             f"<b>Quantity Budget Exceeded</b><br>"
#             f"Account: {account}<br>"
#             f"{'Item: ' + item_code + '<br>' if item_code else ''}"
#             f"Budget Qty: {budget_row.get('budget_qty', '-')}, Projected Qty: {projected_qty}<br>"
#             f"Budget Amount: {budget_row.get('budget_amount', '-')}, Projected Amount: {projected_amount}"
#         )

#         if action == "Stop":
#             frappe.throw(msg, QuantityBudgetError)
#         elif action == "Warn":
#             frappe.msgprint(msg, indicator="orange")

# =====================================================
# CORE ERPNext-STYLE VALIDATION (MR / PO)
# =====================================================
def validate_quantity_budget(company, posting_date, account, item_code, qty, amount, action="Stop"):

    if action == "Ignore":
        return

    fiscal_year = get_fiscal_year(posting_date, company=company)[0]

    budgets = frappe.get_all(
        "Quantity Budget",
        filters={
            "company": company,
            "fiscal_year": fiscal_year,
            "docstatus": 1,

        },
        fields=["name", "budget_against", "project", "cost_center"]
    )

    for b in budgets:
        against_value = b.project if b.budget_against == "Project" else b.cost_center

        row = frappe.get_all(
            "Item Budget Detail",
            filters={
                "parent": b.name,
                "account": account,
                "item_code": item_code
            },
            fields=[
                "budget_qty",
                "budget_amount",
                "consumed_qty",
                "consumed_amount"
            ]
        )

        if not row:
            continue

        row = row[0]

        projected_qty = flt(row.consumed_qty) + flt(qty)
        projected_amt = flt(row.consumed_amount) + flt(amount)

        accumulated_amt = get_accumulated_monthly_budget(
            row.budget_amount, posting_date, fiscal_year
        )

        if projected_qty > flt(row.budget_qty) :
            msg = _(
                f"<b>Quantity Budget Exceeded</b><br>"
                f"Account: {account}<br>"
                f"Item: {item_code}<br>"
                f"Budget Qty: {row.budget_qty}, Projected Qty: {projected_qty}<br>"
                f"Accumulated Budget: {accumulated_amt}<br>"
                f"Projected Amount: {projected_amt}"
            )

            if action == "Stop":
                frappe.throw(msg, QuantityBudgetError)
            else:
                frappe.msgprint(msg, indicator="orange")


# =====================================================
# ACTUAL + MR + PO CONSUMPTION (ERPNext STYLE)
# =====================================================

def get_total_consumption(company, fiscal_year, account, item_code, budget_against, against_value):

    qty = 0
    amount = 0

    condition = ""
    values = [company, account, item_code]

    if budget_against == "Project":
        condition = " AND i.project = %s "
        values.append(against_value)
    elif budget_against == "Cost Center":
        condition = " AND i.cost_center = %s "
        values.append(against_value)

    # ---------------------------
    # Material Request
    # ---------------------------
    mr = frappe.db.sql(
        f"""
        SELECT SUM(i.qty), SUM(i.amount)
        FROM `tabMaterial Request Item` i
        INNER JOIN `tabMaterial Request` m ON m.name = i.parent
        WHERE m.docstatus = 1
          AND m.company = %s
          AND i.expense_account = %s
          AND i.item_code = %s
          {condition}
        """,
        tuple(values)
    )[0]

    qty += flt(mr[0])
    amount += flt(mr[1])

    # ---------------------------
    # Purchase Order
    # ---------------------------
    po = frappe.db.sql(
        f"""
        SELECT SUM(i.qty), SUM(i.amount)
        FROM `tabPurchase Order Item` i
        INNER JOIN `tabPurchase Order` p ON p.name = i.parent
        WHERE p.docstatus = 1
          AND p.company = %s
          AND i.expense_account = %s
          AND i.item_code = %s
          {condition}
        """,
        tuple(values)
    )[0]

    qty += flt(po[0])
    amount += flt(po[1])

    # ---------------------------
    # Actual Expense (GL)
    # ---------------------------
    gl = frappe.db.sql(
        """
        SELECT SUM(debit - credit)
        FROM `tabGL Entry`
        WHERE docstatus = 1
          AND company = %s
          AND account = %s
          AND fiscal_year = %s
        """,
        (company, account, fiscal_year)
    )[0]

    amount += flt(gl[0])

    return {"qty": qty, "amount": amount}

# =====================================================
# RECALCULATE CONSUMPTION FOR QB
# =====================================================
def recalculate_consumption(self):
    for row in self.item_budget_detail:
        consumed = get_total_consumption(
            company=self.company,
            fiscal_year=self.fiscal_year,
            account=row.account,
            item_code=row.item_code,
            budget_against=self.budget_against,
            against_value=self.project or self.cost_center
        )

        row.consumed_qty = flt(consumed["qty"])
        row.consumed_amount = flt(consumed["amount"])
        row.balance_qty = flt(row.budget_qty) - row.consumed_qty


def recalculate_quantity_budget(company, posting_date):
    fiscal_year = get_fiscal_year(posting_date, company=company)[0]

    budgets = frappe.get_all(
        "Quantity Budget",
        filters={
            "company": company,
            "fiscal_year": fiscal_year,
            "docstatus": 1
        },
        pluck="name"
    )

    for name in budgets:
        qb = frappe.get_doc("Quantity Budget", name)
        qb.update_consumed_values()
        qb.db_update_all()   # IMPORTANT


def on_submit_material_request(doc, method):
    recalculate_quantity_budget(doc.company, doc.transaction_date)

def on_cancel_material_request(doc, method):
    recalculate_quantity_budget(doc.company, doc.transaction_date)

def on_submit_purchase_order(doc, method):
    recalculate_quantity_budget(doc.company, doc.transaction_date)

def on_cancel_purchase_order(doc, method):
    recalculate_quantity_budget(doc.company, doc.transaction_date)



# =====================================================
# ACCUMULATED MONTHLY LOGIC
# =====================================================
def get_accumulated_monthly_budget(annual_budget, posting_date, fiscal_year):

    start_date = frappe.get_cached_value(
        "Fiscal Year", fiscal_year, "year_start_date"
    )

    months = 0
    dt = start_date
    while dt <= getdate(posting_date):
        months += 1
        dt = add_months(dt, 1)

    return flt(annual_budget) * (months / 12)


# =====================================================
# HOOK METHODS (MR / PO)
# =====================================================
def validate_material_request_budget(doc, method):
    for row in doc.items:
        validate_quantity_budget(
            company=doc.company,
            posting_date=doc.transaction_date,
            account=row.expense_account,
            item_code=row.item_code,
            qty=row.qty,
            amount=row.amount,
            action=doc.get("budget_action") or "Stop"
        )

def validate_purchase_order_budget(doc, method):
    for row in doc.items:
        validate_quantity_budget(
            company=doc.company,
            posting_date=doc.transaction_date,
            account=row.expense_account,
            item_code=row.item_code,
            qty=row.qty,
            amount=row.amount,
            action=doc.get("budget_action") or "Stop"
        )


# =====================================================
# REVISE BUDGET
# =====================================================
import frappe

@frappe.whitelist()
def create_revised_budget(budget_name):
    """
    Create a revised Quantity Budget from an existing submitted budget.
    """
    # Fetch old budget
    old_budget = frappe.get_doc("Quantity Budget", budget_name)

    # Get new revision number
    new_revision_no = (old_budget.revision_no or 0) + 1

    # Create new draft budget
    new_budget = frappe.new_doc("Quantity Budget")
    new_budget.update({
        "company": old_budget.company,
        "fiscal_year": old_budget.fiscal_year,
        "budget_against": old_budget.budget_against,
        "project": old_budget.project,
        "cost_center": old_budget.cost_center,
        "revision_no": new_revision_no,
        "revised_from": old_budget.name,
        "docstatus": 0
    })

    # Copy item rows
    for row in old_budget.item_budget_detail:
        revised_qty = row.balance_qty        # default copy
        revised_rate = row.budget_rate 
        new_row = {
            "item_code": row.item_code,
            "item_name": row.item_name,
            "account": row.account,
            "budget_qty": row.budget_qty,
            "budget_rate": row.budget_rate,
            "budget_amount": row.budget_amount,
            "revised_budget_qty": revised_qty,
            "revised_budget_rate": revised_rate,
            "revised_budget_amount": revised_qty * revised_rate,
            "consumed_qty": row.consumed_qty,
            "consumed_amount": row.consumed_amount,
            "balance_qty": row.budget_qty - row.consumed_qty
        }
        new_budget.append("item_budget_detail", new_row)

    new_budget.insert(ignore_permissions=True)
    frappe.msgprint(f"Revised Budget Created: {new_budget.name}")
    return new_budget.name


def compute_revised_amount(doc, method):
    for row in doc.item_budget_detail:
        if row.revised_budget_qty and row.revised_budget_rate:
            row.revised_budget_amount = flt(row.revised_budget_qty) * flt(row.revised_budget_rate)
        else:
            row.revised_budget_amount = 0

# =====================================================
# get_item_budget_for_project
# =====================================================
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
        fields=["item_code", "item_name", "budget_qty","account", "budget_rate", "budget_amount", "consumed_qty", "consumed_amount","balance_qty", "revised_budget_qty", "revised_budget_rate", "revised_budget_amount"]
    )
    return items
