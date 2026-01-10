# # Copyright (c) 2026, krishna and Contributors
# # See license.txt

# import frappe
# import unittest


# class TestQuantityBudget(unittest.TestCase):
# # ---------------------------
# # Quantity Budget Creation Test
# # ---------------------------
#     def setUp(self):
#         self.company = frappe.get_all("Company", pluck="name")[0]
#         self.fiscal_year = frappe.get_all("Fiscal Year", pluck="name")[0]
#         self.project = frappe.get_all("Project", pluck="name")[0]
#         self.item = frappe.get_all("Item", pluck="name")[0]

#     def test_quantity_budget_creation(self):
#         doc = frappe.get_doc({
#             "doctype": "Quantity Budget",
#             "company": self.company,
#             "fiscal_year": self.fiscal_year,
#             "budget_against": "Project",
#             "project": self.project,
#             "item_budget_detail": [
#                 {
#                     "item_code": self.item,
#                     "rate": 100,
#                     "budget_qty": 10
#                 }
#             ]
#         })
#         doc.insert()
#         self.assertEqual(doc.item_budget_detail[0].budget_amount, 1000)

# # -------------------------------------------
# # Duplicate Quantity Budget Validation Test
# # -------------------------------------------
#     def test_duplicate_quantity_budget(self):
#         frappe.get_doc({
#             "doctype": "Quantity Budget",
#             "company": self.company,
#             "fiscal_year": self.fiscal_year,
#             "budget_against": "Project",
#             "project": self.project,
#             "item_budget_detail": [
#                 {
#                     "item_code": self.item,
#                     "rate": 50,
#                     "budget_qty": 5
#                 }
#             ]
#         }).insert()

#         doc = frappe.get_doc({
#             "doctype": "Quantity Budget",
#             "company": self.company,
#             "fiscal_year": self.fiscal_year,
#             "budget_against": "Project",
#             "project": self.project,
#             "item_budget_detail": [
#                 {
#                     "item_code": self.item,
#                     "rate": 60,
#                     "budget_qty": 6
#                 }
#             ]
#         })

#         self.assertRaises(frappe.ValidationError, doc.insert)

# # -------------------------------------------
# # Duplicate Item in Child Table Test
# # -------------------------------------------
#     def test_duplicate_item_in_child_table(self):
#         doc = frappe.get_doc({
#             "doctype": "Quantity Budget",
#             "company": self.company,
#             "fiscal_year": self.fiscal_year,
#             "budget_against": "Project",
#             "project": self.project,
#             "item_budget_detail": [
#                 {"item_code": self.item, "rate": 100, "budget_qty": 5},
#                 {"item_code": self.item, "rate": 100, "budget_qty": 3},
#             ]
#         })

#         self.assertRaises(frappe.ValidationError, doc.insert)

# # -------------------------------------------
# # Zero or Negative Budget Qty Validation Test
# # -------------------------------------------
#     def test_invalid_budget_qty(self):
#         doc = frappe.get_doc({
#             "doctype": "Quantity Budget",
#             "company": self.company,
#             "fiscal_year": self.fiscal_year,
#             "budget_against": "Project",
#             "project": self.project,
#             "item_budget_detail": [
#                 {"item_code": self.item, "rate": 100, "budget_qty": 0}
#             ]
#         })

#         self.assertRaises(frappe.ValidationError, doc.insert)
