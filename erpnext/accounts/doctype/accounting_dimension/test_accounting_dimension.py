# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
import unittest

import frappe
from frappe.tests import IntegrationTestCase

from erpnext.accounts.doctype.journal_entry.test_journal_entry import make_journal_entry
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice

EXTRA_TEST_RECORD_DEPENDENCIES = ["Cost Center", "Location", "Warehouse", "Department"]


class TestAccountingDimension(IntegrationTestCase):
	def setUp(self):
		create_dimension()

	def test_dimension_against_sales_invoice(self):
		si = create_sales_invoice(do_not_save=1)

		si.location = "Block 1"
		si.append(
			"items",
			{
				"item_code": "_Test Item",
				"warehouse": "_Test Warehouse - _TC",
				"qty": 1,
				"rate": 100,
				"income_account": "Sales - _TC",
				"expense_account": "Cost of Goods Sold - _TC",
				"cost_center": "_Test Cost Center - _TC",
				"department": "_Test Department - _TC",
				"location": "Block 1",
			},
		)

		si.save()
		si.submit()

		gle = frappe.get_doc("GL Entry", {"voucher_no": si.name, "account": "Sales - _TC"})

		self.assertEqual(gle.get("department"), "_Test Department - _TC")

	def test_dimension_against_journal_entry(self):
		je = make_journal_entry("Sales - _TC", "Sales Expenses - _TC", 500, save=False)
		je.accounts[0].update({"department": "_Test Department - _TC"})
		je.accounts[1].update({"department": "_Test Department - _TC"})

		je.accounts[0].update({"location": "Block 1"})
		je.accounts[1].update({"location": "Block 1"})

		je.save()
		je.submit()

		gle = frappe.get_doc("GL Entry", {"voucher_no": je.name, "account": "Sales - _TC"})
		gle1 = frappe.get_doc("GL Entry", {"voucher_no": je.name, "account": "Sales Expenses - _TC"})
		self.assertEqual(gle.get("department"), "_Test Department - _TC")
		self.assertEqual(gle1.get("department"), "_Test Department - _TC")

	def test_mandatory(self):
		si = create_sales_invoice(do_not_save=1)
		si.append(
			"items",
			{
				"item_code": "_Test Item",
				"warehouse": "_Test Warehouse - _TC",
				"qty": 1,
				"rate": 100,
				"income_account": "Sales - _TC",
				"expense_account": "Cost of Goods Sold - _TC",
				"cost_center": "_Test Cost Center - _TC",
				"location": "",
			},
		)

		si.save()
		self.assertRaises(frappe.ValidationError, si.submit)

	def tearDown(self):
		disable_dimension()
		frappe.flags.accounting_dimensions_details = None
		frappe.flags.dimension_filter_map = None

	def test_company_level_accounting_dimension_validation(self):
		company = frappe.new_doc("Company")
		company.company_name = "_Test New Company"
		company.abbr = "TNC"
		company.default_currency = "INR"
		company.country = "India"
		company.save()

		cost_center = frappe.get_doc(
			{
				"doctype": "Cost Center",
				"cost_center_name": "Main - TNC",
				"parent_cost_center": "_Test New Company - TNC",
				"is_group": 0,
				"company": "_Test New Company",
			}
		)
		cost_center.save()

		company1 = frappe.new_doc("Company")
		company1.company_name = "_Test Demo Company"
		company1.abbr = "TDC"
		company1.default_currency = "INR"
		company1.country = "India"
		company1.save()

		cost_center1 = frappe.get_doc(
			{
				"doctype": "Cost Center",
				"cost_center_name": "Main - TDC",
				"parent_cost_center": "_Test Demo Company - TDC",
				"is_group": 0,
				"company": "_Test Demo Company",
			}
		)
		cost_center1.save()

		si = create_sales_invoice(
			company="_Test New Company", customer="_Test Customer", cost_center="Main - TDC", do_not_save=True
		)
		self.assertRaises(frappe.ValidationError, si.save)

		si.update({"cost_center": "Main - TNC"})
		si.get("items")[0].update({"cost_center": "Main - TDC"})
		self.assertRaises(frappe.ValidationError, si.save)


def create_dimension():
	frappe.set_user("Administrator")

	if not frappe.db.exists("Accounting Dimension", {"document_type": "Department"}):
		dimension = frappe.get_doc(
			{
				"doctype": "Accounting Dimension",
				"document_type": "Department",
			}
		)
		dimension.append(
			"dimension_defaults",
			{
				"company": "_Test Company",
				"reference_document": "Department",
				"default_dimension": "_Test Department - _TC",
			},
		)
		dimension.insert()
		dimension.save()
	else:
		dimension = frappe.get_doc("Accounting Dimension", "Department")
		dimension.disabled = 0
		dimension.save()

	if not frappe.db.exists("Accounting Dimension", {"document_type": "Location"}):
		dimension1 = frappe.get_doc(
			{
				"doctype": "Accounting Dimension",
				"document_type": "Location",
			}
		)

		dimension1.append(
			"dimension_defaults",
			{
				"company": "_Test Company",
				"reference_document": "Location",
				"default_dimension": "Block 1",
				"mandatory_for_bs": 1,
			},
		)

		dimension1.insert()
		dimension1.save()
	else:
		dimension1 = frappe.get_doc("Accounting Dimension", "Location")
		dimension1.disabled = 0
		dimension1.save()


def disable_dimension():
	dimension1 = frappe.get_doc("Accounting Dimension", "Department")
	dimension1.disabled = 1
	dimension1.save()

	dimension2 = frappe.get_doc("Accounting Dimension", "Location")
	dimension2.disabled = 1
	dimension2.save()
