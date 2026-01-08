# Copyright (c) 2026, krishna and Contributors
# See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestQuantityBudget(FrappeTestCase):
# 	pass

# Copyright (c) 2026, krishna and Contributors
# See license.txt

# Copyright (c) 2025
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.utils import get_fiscal_year


# -------------------------------
# Exceptions
# -------------------------------

class BudgetError(frappe.ValidationError):
	pass


class DuplicateBudgetError(frappe.ValidationError):
	pass


# -------------------------------
# Custom Budget List
# -------------------------------

class QuantityBudget(Document):

	def validate(self):
		self.validate_mandatory()
		self.validate_duplicate()
		self.populate_item_defaults()
		self.calculate_rates()
		self.calculate_consumed()
		self.set_null_value()

	# ---------------------------
	# Basic validations
	# ---------------------------

	def validate_mandatory(self):
		if not self.company or not self.fiscal_year:
			frappe.throw(_("Company and Fiscal Year are mandatory"))

		if not self.item_budget_detail:
			frappe.throw(_("At least one Item Budget Detail row is required"))

	def set_null_value(self):
		if self.budget_against == "Cost Center":
			self.project = None
		else:
			self.cost_center = None

	# ---------------------------
	# Duplicate check
	# ---------------------------

	def validate_duplicate(self):
		items = [d.item_code for d in self.item_budget_detail if d.item_code]

		if not items:
			return

		existing = frappe.db.sql(
			"""
			SELECT cbd.name, ibd.item_code
			FROM `tabCustom Budget List` cbd
			JOIN `tabItem Budget Detail` ibd ON ibd.parent = cbd.name
			WHERE
				cbd.docstatus < 2
				AND cbd.company = %s
				AND cbd.fiscal_year = %s
				AND cbd.name != %s
				AND ibd.item_code IN ({})
			""".format(",".join(["%s"] * len(items))),
			(self.company, self.fiscal_year, self.name, *items),
			as_dict=True,
		)

		if existing:
			d = existing[0]
			frappe.throw(
				_("Budget already exists for Item {0} in Fiscal Year {1}")
				.format(d.item_code, self.fiscal_year),
				DuplicateBudgetError,
			)

	# ---------------------------
	# Item defaults
	# ---------------------------

	def populate_item_defaults(self):
		for d in self.item_budget_detail:
			if not d.item_code:
				continue

			# Cost Price
			if not d.cost_price:
				d.cost_price = frappe.db.get_value(
					"Item Price",
					{
						"item_code": d.item_code,
						"buying": 1,
					},
					"price_list_rate",
				) or 0

			# Expense Account
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

	# ---------------------------
	# Rate calculation
	# ---------------------------

	def calculate_rates(self):
		for d in self.item_budget_detail:
			if flt(d.budget_qty) > 0 and flt(d.budget_amount) > 0:
				d.rate = flt(d.budget_amount) / flt(d.budget_qty)
			else:
				d.rate = 0

	# ---------------------------
	# Consumed Qty & Amount
	# ---------------------------

	def calculate_consumed(self):
		for d in self.item_budget_detail:
			d.consumed_qty = get_consumed_qty(
				self, d.item_code, d.account
			)
			d.consumed_amount = flt(d.consumed_qty) * flt(d.rate)
			d.budget_amount_remaining = flt(d.budget_amount) - flt(d.consumed_amount)


# =====================================================
# Budget Enforcement (called from MR / PO / JE)
# =====================================================

def validate_expense_against_custom_budget(args, expense_amount=0):
	args = frappe._dict(args)

	if not args.fiscal_year:
		args.fiscal_year = get_fiscal_year(args.posting_date, company=args.company)[0]

	if not args.item_code or not args.account:
		return

	budgets = frappe.db.sql(
		"""
		SELECT
			cbd.name,
			ibd.budget_amount,
			ibd.budget_qty,
			ibd.rate
		FROM `tabCustom Budget List` cbd
		JOIN `tabItem Budget Detail` ibd ON ibd.parent = cbd.name
		WHERE
			cbd.company = %s
			AND cbd.fiscal_year = %s
			AND ibd.item_code = %s
			AND ibd.account = %s
			AND cbd.docstatus = 1
		""",
		(args.company, args.fiscal_year, args.item_code, args.account),
		as_dict=True,
	)

	for budget in budgets:
		consumed_amount = get_consumed_amount(args)
		total = consumed_amount + expense_amount

		if total > flt(budget.budget_amount):
			frappe.throw(
				_("Item Budget exceeded for Item {0}. Budget: {1}, Consumed: {2}")
				.format(
					args.item_code,
					budget.budget_amount,
					total,
				),
				BudgetError,
			)


# =====================================================
# Helpers
# =====================================================

def get_consumed_qty(parent_doc, item_code, account):
	result = frappe.db.sql(
		"""
		SELECT IFNULL(SUM(qty), 0)
		FROM `tabPurchase Invoice Item`
		WHERE
			item_code = %s
			AND expense_account = %s
			AND docstatus = 1
		""",
		(item_code, account),
	)

	return result[0][0] if result else 0


def get_consumed_amount(args):
	result = frappe.db.sql(
		"""
		SELECT IFNULL(SUM(amount), 0)
		FROM `tabPurchase Invoice Item`
		WHERE
			item_code = %s
			AND expense_account = %s
			AND docstatus = 1
		""",
		(args.item_code, args.account),
	)

	return result[0][0] if result else 0
