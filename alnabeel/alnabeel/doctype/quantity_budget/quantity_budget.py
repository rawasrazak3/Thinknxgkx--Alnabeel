
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate
from erpnext.accounts.utils import get_fiscal_year


# =========================================================
# Quantity Budget DocType
# =========================================================

class QuantityBudget(Document):

    def validate(self):
        if self.revised_from:
            parent = frappe.get_doc("Quantity Budget", self.revised_from)
            if parent.docstatus != 1:
                frappe.throw(
                    _("You cannot revise a cancelled Quantity Budget")
                )
            self.recalculate_consumption()
        self.validate_against()
        self.validate_duplicate_budget()
        

    def on_cancel(self):
        self.recalculate_consumption()

    # -----------------------------------------------------
    def validate_against(self):
        if self.budget_against == "Project" and not self.project:
            frappe.throw(_("Project is mandatory"))
        if self.budget_against == "Cost Center" and not self.cost_center:
            frappe.throw(_("Cost Center is mandatory"))

    # -----------------------------------------------------
    # def validate_duplicate(self):
    #     filters = {
    #         "company": self.company,
    #         "fiscal_year": self.fiscal_year,
    #         "budget_against": self.budget_against,
    #         "docstatus": ("!=", 2),
    #         "name": ("!=", self.name),
    #     }

    #     if self.budget_against == "Project":
    #         filters["project"] = self.project
    #     else:
    #         filters["cost_center"] = self.cost_center

    #     if frappe.db.exists("Quantity Budget", filters):
    #         frappe.throw(_("Duplicate Quantity Budget exists"))

    def validate_duplicate_budget(self):
        # Allow revisions freely
        if self.revised_from:
            return

        filters = {
            "company": self.company,
            "fiscal_year": self.fiscal_year,
            "budget_against": self.budget_against,
            "docstatus": 1,
            "name": ["!=", self.name],
        }

        if self.budget_against == "Project":
            filters["project"] = self.project
        else:
            filters["cost_center"] = self.cost_center

        if frappe.db.exists("Quantity Budget", filters):
            frappe.throw(
                _("An active Quantity Budget already exists. Please revise it instead.")
            )

    # -----------------------------------------------------
    def recalculate_consumption(self):
        for row in self.item_budget_detail:
            consumed = get_total_consumption(
                company=self.company,
                fiscal_year=self.fiscal_year,
                item_code=row.item_code,
                account=row.account,
                budget_against=self.budget_against,
                against_value=self.project or self.cost_center,
            )

            row.consumed_qty = flt(consumed["qty"])
            row.consumed_amount = flt(consumed["amount"])
            row.balance_qty = flt(row.budget_qty) + flt(row.revised_budget_qty) - row.consumed_qty

    # -----------------------------------------------------
    def on_submit(self):
        self.cancel_previous_revision()
        self.recalculate_consumption()

    def cancel_previous_revision(self):
        if not self.revised_from:
            return

        prev = frappe.get_doc("Quantity Budget", self.revised_from)

        if prev.docstatus == 1:
            prev.flags.ignore_links = True
            prev.flags.ignore_permissions = True
            prev.cancel()


# ========================================================
# Recalculate QB Consumption on MR / PO Submit / Cancel
# ========================================================
def recalculate_from_doc(doc, method):
    """
    Recalculate Quantity Budget consumption when MR / PO is submitted or cancelled
    """

    fiscal_year = get_fiscal_year(
        getdate(doc.transaction_date), company=doc.company
    )[0]

    budgets = frappe.get_all(
        "Quantity Budget",
        filters={
            "company": doc.company,
            "fiscal_year": fiscal_year,
            "docstatus": 1,
        },
        pluck="name",
    )

    for name in budgets:
        qb = frappe.get_doc("Quantity Budget", name)
        qb.recalculate_consumption()
        qb.db_update_all()

# =========================================================
# TOTAL CONSUMPTION (MR + PO)
# =========================================================

def get_total_consumption(company, fiscal_year, item_code, account, budget_against, against_value):

    qty = 0
    amount = 0

    condition = "i.project = %s" if budget_against == "Project" else "i.cost_center = %s"
    values = [company, account, against_value]

    # ===============================
    # ACCOUNT BASED (No item_code)
    # ===============================
    if not item_code:

        mr = frappe.db.sql(f"""
            SELECT SUM(i.amount)
            FROM `tabMaterial Request Item` i
            JOIN `tabMaterial Request` m ON m.name = i.parent
            WHERE m.docstatus = 1
              AND m.company = %s
              AND i.expense_account = %s
              AND {condition}
        """, values)[0]

        amount += flt(mr[0])

        po = frappe.db.sql(f"""
            SELECT SUM(i.amount)
            FROM `tabPurchase Order Item` i
            JOIN `tabPurchase Order` p ON p.name = i.parent
            WHERE p.docstatus = 1
              AND p.company = %s
              AND i.expense_account = %s
              AND {condition}
        """, values)[0]

        amount += flt(po[0])

        return {"qty": 0, "amount": amount}

    # ===============================
    # ITEM BASED
    # ===============================
    values.insert(1, item_code)

    mr = frappe.db.sql(f"""
        SELECT SUM(i.qty), SUM(i.amount)
        FROM `tabMaterial Request Item` i
        JOIN `tabMaterial Request` m ON m.name = i.parent
        WHERE m.docstatus = 1
          AND m.company = %s
          AND i.item_code = %s
          AND i.expense_account = %s
          AND {condition}
    """, values)[0]

    qty += flt(mr[0])
    amount += flt(mr[1])

    po = frappe.db.sql(f"""
        SELECT SUM(i.qty), SUM(i.amount)
        FROM `tabPurchase Order Item` i
        JOIN `tabPurchase Order` p ON p.name = i.parent
        WHERE p.docstatus = 1
          AND p.company = %s
          AND i.item_code = %s
          AND i.expense_account = %s
          AND {condition}
    """, values)[0]

    qty += flt(po[0])
    amount += flt(po[1])

    return {"qty": qty, "amount": amount}

# =========================================================
# FETCH BUDGET ITEM (QTY + RATE + ACCOUNT)
# =========================================================

def get_budget_item(company, fiscal_year, item_code, budget_against, against_value):
    """
    Fetch the latest submitted Quantity Budget for an item, including revised qty/rate.
    Returns dict with budget_qty, budget_rate, budget_amount, consumed_qty, balance_qty.
    """

    # Determine filter for Project or Cost Center
    filters = {
        "company": company,
        "fiscal_year": fiscal_year,
        "docstatus": 1,
        "budget_against": budget_against,
    }
    if budget_against == "Project":
        filters["project"] = against_value
    else:
        filters["cost_center"] = against_value

    # Get latest submitted budget revision
    qb_list = frappe.get_all(
        "Quantity Budget",
        filters=filters,
        order_by="revision_no desc",
        limit=1,
        pluck="name"
    )

    if not qb_list:
        return None

    qb_name = qb_list[0]

    # Fetch Item Budget Detail for the latest budget
    item = frappe.get_all(
        "Item Budget Detail",
        filters={"parent": qb_name, "item_code": item_code},
        fields=[
            "budget_qty",
            "revised_budget_qty",
            "budget_rate",
            "revised_budget_rate",
            "consumed_qty",
            "consumed_amount"
        ],
        limit=1
    )

    if not item:
        return None

    item = item[0]

    # Use revised values if they exist
    budget_qty = flt(item.get("revised_budget_qty") + item.get("budget_qty"))
    budget_rate = flt(item.get("revised_budget_rate") or item.get("budget_rate"))
    budget_amount = budget_qty * budget_rate
    consumed_qty = flt(item.get("consumed_qty"))
    consumed_amount = flt(item.get("consumed_amount"))
    balance_qty = budget_qty - consumed_qty

    return {
        "budget_qty": budget_qty,
        "budget_rate": budget_rate,
        "budget_amount": budget_amount,
        "consumed_qty": consumed_qty,
        "consumed_amount": consumed_amount,
        "balance_qty": balance_qty,
        "latest_budget": qb_name
    }


# =========================================================
# VALIDATION 
# =========================================================
# def validate_quantity_budget(company, posting_date, row):
#     """
#     Validate item quantity against the latest revised Quantity Budget.
#     Updates row with budget_qty, budget_rate, amount, consumed_qty, balance_qty.
#     Throws error if projected qty exceeds budget.
#     """

#     # Normalize first (PMR → MR safe)
#     if row.project:
#         row.cost_center = None
#     elif row.cost_center:
#         row.project = None

#     # Only one of Project / Cost Center allowed
#     if row.project and row.cost_center:
#         frappe.throw(_("Only Project OR Cost Center is allowed"))

#     if not row.project and not row.cost_center:
#         frappe.throw(_("Either Project or Cost Center is mandatory"))

#     # Determine budget type
#     budget_against = "Project" if row.project else "Cost Center"
#     against_value = row.project or row.cost_center

#     # Get fiscal year
#     fiscal_year = get_fiscal_year(getdate(posting_date), company=company)[0]

#     # Fetch latest budget item (revised if exists)
#     budget = get_budget_item(company, fiscal_year, row.item_code, budget_against, against_value)

#     # if not budget:
#     #     frappe.throw(
#     #         _("No Quantity Budget found for Item {0} against {1} {2}").format(
#     #             row.item_code, budget_against, against_value
#     #         )
#     #     )

#     if not budget:
#         return


#     # Assign values to PMR / MR row
#     row.budget_qty = budget["budget_qty"]
#     row.rate = budget["budget_rate"]
#     row.amount = flt(row.qty) * row.rate
#     row.consumed_qty = budget["consumed_qty"]
#     row.balance_qty = budget["balance_qty"]

#     # Validate requested quantity
#     projected_qty = flt(row.qty) + flt(row.consumed_qty)
#     if projected_qty > flt(row.budget_qty):
#         frappe.throw(
#             _(
#                 "<b>Quantity Budget Exceeded</b><br>"
#                 "Item: {0}<br>"
#                 "Budget Qty: {1}<br>"
#                 "Consumed Qty: {2}<br>"
#                 "Requested Qty: {3}<br>"
#                 "Projected Qty: {4}"
#             ).format(
#                 row.item_code,
#                 row.budget_qty,
#                 row.consumed_qty,
#                 row.qty,
#                 projected_qty,
#             )
#         )

def validate_quantity_budget(company, posting_date, row):

    # --------------------------------
    # Normalize Project / Cost Center
    # --------------------------------
    if row.project:
        row.cost_center = None
    elif row.cost_center:
        row.project = None

    if row.project and row.cost_center:
        frappe.throw(_("Only Project OR Cost Center is allowed"))

    if not row.project and not row.cost_center:
        frappe.throw(_("Either Project or Cost Center is mandatory"))

    budget_against = "Project" if row.project else "Cost Center"
    against_value = row.project or row.cost_center

    fiscal_year = get_fiscal_year(getdate(posting_date), company=company)[0]

    # ==========================================================
    # ITEM BASED BUDGET (Quantity Validation)
    # ==========================================================
    if row.item_code:

        budget = get_budget_item(
            company,
            fiscal_year,
            row.item_code,
            budget_against,
            against_value
        )

        if budget:   

            row.budget_qty = budget["budget_qty"]
            row.rate = budget["budget_rate"]
            row.amount = flt(row.qty) * row.rate
            row.consumed_qty = budget["consumed_qty"]
            row.balance_qty = budget["balance_qty"]

            projected_qty = flt(row.qty) + flt(row.consumed_qty)

            if projected_qty > flt(row.budget_qty):
                frappe.throw(
                    _(
                        "<b>Quantity Budget Exceeded</b><br>"
                        "Item: {0}<br>"
                        "Budget Qty: {1}<br>"
                        "Consumed Qty: {2}<br>"
                        "Requested Qty: {3}<br>"
                        "Projected Qty: {4}"
                    ).format(
                        row.item_code,
                        row.budget_qty,
                        row.consumed_qty,
                        row.qty,
                        projected_qty,
                    )
                )

    # ==========================================================
    # ACCOUNT BASED BUDGET (Amount Validation Only)
    # ==========================================================
    if row.expense_account:

        qb_list = frappe.get_all(
            "Quantity Budget",
            filters={
                "company": company,
                "fiscal_year": fiscal_year,
                "docstatus": 1,
                "budget_against": budget_against,
                "project": against_value if budget_against == "Project" else None,
                "cost_center": against_value if budget_against == "Cost Center" else None,
            },
            order_by="revision_no desc",
            limit=1,
            pluck="name"
        )

        if not qb_list:
            return

        qb_name = qb_list[0]

        budget_row = frappe.get_all(
            "Item Budget Detail",
            filters={
                "parent": qb_name,
                "account": row.expense_account,
                "item_code": ["is", "not set"]
            },
            fields=[
                "budget_amount",
                "revised_budget_amount",
                "consumed_amount"
            ],
            limit=1
        )

        if not budget_row:
            return

        budget_row = budget_row[0]

        total_budget_amount = (
            flt(budget_row.get("budget_amount")) +
            flt(budget_row.get("revised_budget_amount"))
        )

        consumed_amount = flt(budget_row.get("consumed_amount"))
        projected_amount = consumed_amount + flt(row.amount)

        if projected_amount > total_budget_amount:
            frappe.throw(
                _(
                    "<b>Account Budget Exceeded</b><br>"
                    "Account: {0}<br>"
                    "Budget Amount: {1}<br>"
                    "Consumed Amount: {2}<br>"
                    "Requested Amount: {3}<br>"
                    "Projected Amount: {4}"
                ).format(
                    row.expense_account,
                    total_budget_amount,
                    consumed_amount,
                    row.amount,
                    projected_amount,
                )
            )


# =========================================================
# MATERIAL REQUEST HOOK
# =========================================================

def validate_material_request_budget(doc, method):
    for row in doc.items:
        validate_quantity_budget(doc.company, doc.transaction_date, row)


# =========================================================
# PURCHASE ORDER HOOK
# =========================================================

def validate_purchase_order_budget(doc, method):
    for row in doc.items:
        validate_quantity_budget(doc.company, doc.transaction_date, row)


# =========================================================
# GET ITEM BUDGET FOR PROJECT
# =========================================================

@frappe.whitelist()
def get_item_budget_for_project(project):
    """
    Return item-wise budget for a project (latest revision) for PMR table.
    Uses revised_qty and revised_rate if available.
    """
    # Get latest submitted Quantity Budget for the project
    qb_list = frappe.get_all(
        "Quantity Budget",
        filters={"project": project, "docstatus": 1},
        order_by="revision_no desc",
        limit=1,
        pluck="name"
    )

    if not qb_list:
        return []

    qb_name = qb_list[0]

    # Fetch all Item Budget Details
    items = frappe.get_all(
        "Item Budget Detail",
        filters={"parent": qb_name},
        fields=[
            "item_code",
            "item_name",
            "budget_qty",
            "revised_budget_qty",
            "budget_rate",
            "revised_budget_rate",
            "consumed_qty",
            "consumed_amount"
        ]
    )

    # Compute final budget qty/rate/amount/balance for PMR
    for item in items:
        item["budget_qty"] = flt(item.get("revised_budget_qty") + item.get("budget_qty"))
        item["budget_rate"] = flt(item.get("revised_budget_rate") or item.get("budget_rate"))
        item["budget_amount"] = item["budget_qty"] * item["budget_rate"]
        item["balance_qty"] = item["budget_qty"] - flt(item.get("consumed_qty"))

    return items

# ========================================================
# create revised budget
# ========================================================
# @frappe.whitelist()
# def create_revised_budget(budget_name):
#     old = frappe.get_doc("Quantity Budget", budget_name)

#     if old.docstatus != 1:
#         frappe.throw(_("Only submitted budgets can be revised"))

#     new = frappe.copy_doc(old)

#     new.revised_from = old.name        # immediate parent
#     new.revision_no = (old.revision_no or 0) + 1
#     new.docstatus = 0

#     new.flags.ignore_permissions = True
#     new.flags.ignore_links = True

#     new.insert()
#     return new.name

@frappe.whitelist()
def create_revised_budget(budget_name):

    old = frappe.get_doc("Quantity Budget", budget_name)

    if old.docstatus != 1:
        frappe.throw(_("Only submitted budgets can be revised"))

    new = frappe.copy_doc(old)

    new.revised_from = old.name
    new.revision_no = (old.revision_no or 0) + 1
    new.docstatus = 0

    # --------------------------------------------------
    # ACCUMULATE QTY & RATE INTO BASE FIELDS
    # --------------------------------------------------
    for row in new.item_budget_detail:

        # Add revised qty into budget qty
        row.budget_qty = flt(row.budget_qty) + flt(row.revised_budget_qty)

        # If revised rate exists, override rate
        if flt(row.revised_budget_rate):
            row.budget_rate = flt(row.revised_budget_rate)

         # Recalculate budget amount
        row.budget_amount = flt(row.budget_qty) * flt(row.budget_rate)

        # Clear revised fields for fresh editing
        row.revised_budget_qty = 0
        row.revised_budget_rate = 0
        row.revised_budget_amount = 0

    # --------------------------------------------------

    new.flags.ignore_permissions = True
    new.flags.ignore_links = True

    new.insert()

    return new.name
