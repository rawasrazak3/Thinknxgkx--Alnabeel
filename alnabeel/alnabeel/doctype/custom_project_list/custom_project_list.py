# Copyright (c) 2026, krishna and contributors
# For license information, please see license.txt

# Copyright (c) 2026, Krishna
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProjectBudgetError(frappe.ValidationError):
	pass


class CustomProjectList(Document):

	def validate(self):
		self.validate_items()
		self.populate_item_defaults()
		self.calculate_rates()
		self.calculate_consumed()

	# --------------------------------
	# Item validations
	# --------------------------------
	def validate_items(self):
		seen = set()
		for d in self.item_budget_detail:
			if not d.item_code:
				frappe.throw(_("Item Code is mandatory"))

			if d.item_code in seen:
				frappe.throw(_("Duplicate Item {0}").format(d.item_code))

			seen.add(d.item_code)

	# --------------------------------
	# Fetch defaults
	# --------------------------------
	def populate_item_defaults(self):
		for d in self.item_budget_detail:

			if not d.cost_price:
				d.cost_price = (
					frappe.db.get_value(
						"Item Price",
						{"item_code": d.item_code, "buying": 1},
						"price_list_rate",
					)
					or 0
				)

			if not d.account:
				account = frappe.db.get_value(
					"Item Default",
					{"parent": d.item_code, "company": self.company},
					"expense_account",
				)

				if not account:
					account = frappe.db.get_value(
						"Company", self.company, "default_expense_account"
					)

				d.account = account

	# --------------------------------
	# Rate = amount / qty
	# --------------------------------
	def calculate_rates(self):
		for d in self.item_budget_detail:
			if flt(d.budget_qty) > 0:
				d.rate = flt(d.budget_amount) / flt(d.budget_qty)
			else:
				d.rate = 0

	# --------------------------------
	# Consumption (Project-wise)
	# --------------------------------
	def calculate_consumed(self):
		for d in self.item_budget_detail:
			d.consumed_qty = get_project_consumed_qty(
				self.name, d.item_code, d.account
			)
			d.consumed_amount = flt(d.consumed_qty) * flt(d.rate)
			d.budget_amount_remaining = (
				flt(d.budget_amount) - flt(d.consumed_amount)
			)


# ==========================================================
# 🔽 OUTSIDE CLASS — UTILITY FUNCTIONS
# ==========================================================

def validate_expense_against_project_budget(args, expense_amount=0):
	args = frappe._dict(args)

	if not args.project or not args.item_code or not args.account:
		return

	budget = frappe.db.sql(
		"""
		SELECT ibd.budget_amount
		FROM `tabCustom Project List` cp
		JOIN `tabItem Budget Detail` ibd ON ibd.parent = cp.name
		WHERE
			cp.name = %s
			AND cp.docstatus = 1
			AND ibd.item_code = %s
			AND ibd.account = %s
		""",
		(args.project, args.item_code, args.account),
		as_dict=True,
	)

	if not budget:
		return

	budget_amount = flt(budget[0].budget_amount)
	consumed = get_project_consumed_amount(args)
	total = consumed + flt(expense_amount)

	if total > budget_amount:
		frappe.throw(
			_(
				"Project Item Budget exceeded for Item {0}. "
				"Budget: {1}, Consumed: {2}"
			).format(args.item_code, budget_amount, total),
			ProjectBudgetError,
		)


def get_project_consumed_qty(project, item_code, account):
	res = frappe.db.sql(
		"""
		SELECT IFNULL(SUM(qty), 0)
		FROM `tabPurchase Invoice Item`
		WHERE
			project = %s
			AND item_code = %s
			AND expense_account = %s
			AND docstatus = 1
		""",
		(project, item_code, account),
	)

	return res[0][0] if res else 0


def get_project_consumed_amount(args):
	res = frappe.db.sql(
		"""
		SELECT IFNULL(SUM(amount), 0)
		FROM `tabPurchase Invoice Item`
		WHERE
			project = %s
			AND item_code = %s
			AND expense_account = %s
			AND docstatus = 1
		""",
		(args.project, args.item_code, args.account),
	)

	return res[0][0] if res else 0


# ==========================================================
# CREATE MATERIAL REQUEST FOR PROJECT
# ==========================================================

@frappe.whitelist()
def create_material_request(project, items):
    """
    items = [
        { "item_code": "...", "requested_qty": 10 }
    ]
    """
    project_doc = frappe.get_doc("Custom Project List", project)
    mr = frappe.new_doc("Material Request")
    mr.material_request_type = "Purchase"
    mr.project = project_doc.name
    mr.company = project_doc.company

    for i in items:
        item_doc = frappe.get_doc("Item", i["item_code"])
        balance_qty = flt(i.get("balance_qty", 0))
        requested_qty = flt(i.get("requested_qty", 0))

        if requested_qty > balance_qty:
            frappe.throw(_("Requested quantity for {0} exceeds available balance").format(i["item_code"]))

        mr.append("items", {
            "item_code": i["item_code"],
            "qty": requested_qty,
            "schedule_date": frappe.utils.nowdate(),
            "warehouse": item_doc.default_warehouse or frappe.db.get_value("Company", project_doc.company, "default_warehouse")
        })

    mr.insert()
    mr.submit()

    # Update consumed qty and amount in project
    for item in mr.items:
        update_project_consumed_qty_amount(project_doc.name, item.item_code, item.qty, item.rate)

    return mr.name


def update_project_consumed_qty_amount(project_name, item_code, qty, rate):
    """Update consumed qty and amount in Custom Project List"""
    project_doc = frappe.get_doc("Custom Project List", project_name)
    for d in project_doc.item_budget_detail:
        if d.item_code == item_code:
            d.consumed_qty = flt(d.consumed_qty) + flt(qty)
            d.consumed_amount = flt(d.consumed_amount) + flt(qty * d.rate)
            d.budget_amount_remaining = flt(d.budget_amount) - flt(d.consumed_amount)
    project_doc.save()


# ==========================================================
# MATERIAL REQUEST ON CANCEL
# ==========================================================

def material_request_on_cancel(doc, method):
    """Update project consumed qty and amount on MR cancel"""
    project_name = doc.project
    project_doc = frappe.get_doc("Custom Project List", project_name)

    for item in doc.items:
        for d in project_doc.item_budget_detail:
            if d.item_code == item.item_code:
                d.consumed_qty = flt(d.consumed_qty) - flt(item.qty)
                d.consumed_amount = flt(d.consumed_amount) - flt(item.qty * d.rate)
                d.budget_amount_remaining = flt(d.budget_amount) - flt(d.consumed_amount)
    project_doc.save()
