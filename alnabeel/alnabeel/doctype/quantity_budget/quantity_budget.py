# Copyright (c) 2026, krishna and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class QuantityBudget(Document):
# 	pass

# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.utils import get_fiscal_year
# from erpnext.accounts.general_ledger import get_balance_on
from erpnext.accounts.utils import get_balance_on



# ---------------------------------------------------------
# Exceptions
# ---------------------------------------------------------
class BudgetError(frappe.ValidationError):
	pass


class DuplicateBudgetError(frappe.ValidationError):
	pass


# ---------------------------------------------------------
# Custom Budget List
# ---------------------------------------------------------
class QuantityBudget(Document):

	def validate(self):
		self.validate_items()
		self.validate_duplicate()
		self.validate_dimension_required()

	# -----------------------------------------------------
	# Validate child table (Item Budget Detail)
	# -----------------------------------------------------
	def validate_items(self):
		if not self.item_budget_detail:
			frappe.throw(_("Item Budget Detail table cannot be empty"))

		seen = set()

		for d in self.item_budget_detail:
			if not d.item_code:
				frappe.throw(_("Item Code is mandatory"))

			if d.item_code in seen:
				frappe.throw(
					_("Item {0} is entered more than once").format(d.item_code)
				)
			seen.add(d.item_code)

			# if not d.account:
			# 	frappe.throw(
			# 		_("Expense Account missing for Item {0}").format(d.item_code)
			# 	)

			if flt(d.budget_qty) <= 0:
				frappe.throw(
					_("Budget Quantity must be greater than zero for Item {0}")
					.format(d.item_code)
				)

			if flt(d.budget_amount) <= 0:
				frappe.throw(
					_("Budget Amount must be greater than zero for Item {0}")
					.format(d.item_code)
				)

	# -----------------------------------------------------
	# Prevent duplicate budgets (Item + FY + Dimension)
	# -----------------------------------------------------
	def validate_duplicate(self):
		items = [d.item_code for d in self.item_budget_detail]

		if not items:
			return

		conditions = ["cbl.company = %s", "cbl.fiscal_year = %s", "cbl.name != %s"]
		values = [self.company, self.fiscal_year, self.name]

		for dim in get_accounting_dimensions():
			val = self.get(dim.fieldname)
			if val:
				conditions.append(f"cbl.{dim.fieldname} = %s")
				values.append(val)

		query = f"""
			SELECT cbl.name, ibd.item_code
			FROM `tabCustom Budget List` cbl
			JOIN `tabItem Budget Detail` ibd ON ibd.parent = cbl.name
			WHERE cbl.docstatus < 2
			  AND ibd.item_code IN ({",".join(["%s"] * len(items))})
			  AND {" AND ".join(conditions)}
		"""

		existing = frappe.db.sql(query, values + items, as_dict=True)

		if existing:
			row = existing[0]
			frappe.throw(
				_("Budget already exists for Item {0} in Fiscal Year {1}")
				.format(row.item_code, self.fiscal_year),
				DuplicateBudgetError,
			)

	# -----------------------------------------------------
	# Dimension mandatory validation
	# -----------------------------------------------------
	def validate_dimension_required(self):
		for dim in get_accounting_dimensions():
			if dim.mandatory_for_budget and not self.get(dim.fieldname):
				frappe.throw(
					_("{0} is mandatory for Budget").format(dim.label)
				)


# ---------------------------------------------------------
# Budget Enforcement (Called from GL / Purchase / Stock)
# ---------------------------------------------------------
def validate_expense_against_budget(args):
	"""
	args must contain:
	company, fiscal_year, item_code, account,
	cost_center / project / dimensions,
	amount, posting_date, action
	"""

	if not args.get("item_code"):
		return

	budgets = get_matching_item_budgets(args)

	for b in budgets:
		actual = get_actual_expense(args, b)
		budget = get_budget_amount(b, args)

		if actual + flt(args.amount) > budget:
			action = b.action or "Stop"
			msg = _(
				"Budget exceeded for Item {0}<br>"
				"Budget: {1}<br>"
				"Actual + Requested: {2}"
			).format(
				args.item_code,
				frappe.format(budget),
				frappe.format(actual + flt(args.amount)),
			)

			if action == "Stop":
				frappe.throw(msg, BudgetError)
			elif action == "Warn":
				frappe.msgprint(msg, indicator="orange")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def get_matching_item_budgets(args):
	conditions = [
		"cbl.company = %(company)s",
		"cbl.fiscal_year = %(fiscal_year)s",
		"ibd.item_code = %(item_code)s",
		"ibd.account = %(account)s",
		"cbl.docstatus = 1",
	]

	for dim in get_accounting_dimensions():
		if args.get(dim.fieldname):
			conditions.append(f"cbl.{dim.fieldname} = %({dim.fieldname})s")

	query = f"""
		SELECT
			cbl.name,
			cbl.action,
			ibd.budget_amount
		FROM `tabCustom Budget List` cbl
		JOIN `tabItem Budget Detail` ibd
			ON ibd.parent = cbl.name
		WHERE {" AND ".join(conditions)}
	"""

	return frappe.db.sql(query, args, as_dict=True)


def get_actual_expense(args, budget):
	"""
	Uses GL Entry to get actual expense
	"""

	dim_conditions = []
	dim_values = {}

	for dim in get_accounting_dimensions():
		if args.get(dim.fieldname):
			dim_conditions.append(f"gle.{dim.fieldname} = %({dim.fieldname})s")
			dim_values[dim.fieldname] = args.get(dim.fieldname)

	query = f"""
		SELECT SUM(debit - credit)
		FROM `tabGL Entry` gle
		WHERE
			gle.company = %(company)s
			AND gle.account = %(account)s
			AND gle.posting_date <= %(posting_date)s
			AND gle.is_cancelled = 0
			{" AND ".join(dim_conditions)}
	"""

	return flt(
		frappe.db.sql(
			query,
			{
				"company": args.company,
				"account": args.account,
				"posting_date": args.posting_date,
				**dim_values,
			},
		)[0][0]
	)


def get_budget_amount(budget, args):
	return flt(budget.budget_amount)


# def validate_expense_against_project_budget_hook(doc, method):
#     for item in doc.items:
#         args = {
#             "project": doc.project,
#             "item_code": item.item_code,
#             "account": item.expense_account,
#         }
#         validate_expense_against_project_budget(args, expense_amount=item.amount)
