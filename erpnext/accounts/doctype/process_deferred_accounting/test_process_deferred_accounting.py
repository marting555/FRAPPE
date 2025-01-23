# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe

from erpnext.accounts.doctype.account.test_account import create_account
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import (
	check_gl_entries,
	create_sales_invoice,
)
from erpnext.stock.doctype.item.test_item import create_item


class TestProcessDeferredAccounting(unittest.TestCase):
	def test_creation_of_ledger_entry_on_submit(self):
		"""test creation of gl entries on submission of document"""
		change_acc_settings(acc_frozen_upto="2023-05-31", book_deferred_entries_based_on="Months")

		deferred_account = create_account(
			account_name="Deferred Revenue for Accounts Frozen",
			parent_account="Current Liabilities - _TC",
			company="_Test Company",
		)

		item = create_item("_Test Item for Deferred Accounting")
		item.enable_deferred_revenue = 1
		item.deferred_revenue_account = deferred_account
		item.no_of_months = 12
		item.save()

		si = create_sales_invoice(
			item=item.name, rate=3000, update_stock=0, posting_date="2023-07-01", do_not_submit=True
		)
		si.items[0].enable_deferred_revenue = 1
		si.items[0].service_start_date = "2023-05-01"
		si.items[0].service_end_date = "2023-07-31"
		si.items[0].deferred_revenue_account = deferred_account
		si.save()
		si.submit()

		process_deferred_accounting = frappe.get_doc(
			dict(
				doctype="Process Deferred Accounting",
				posting_date="2023-07-01",
				start_date="2023-05-01",
				end_date="2023-06-30",
				type="Income",
			)
		)

		process_deferred_accounting.insert()
		process_deferred_accounting.submit()

		expected_gle = [
			["Debtors - _TC", 3000, 0.0, "2023-07-01"],
			[deferred_account, 0.0, 3000, "2023-07-01"],
			["Sales - _TC", 0.0, 1000, "2023-06-30"],
			[deferred_account, 1000, 0.0, "2023-06-30"],
			["Sales - _TC", 0.0, 1000, "2023-06-30"],
			[deferred_account, 1000, 0.0, "2023-06-30"],
		]

		check_gl_entries(self, si.name, expected_gle, "2023-07-01")
		change_acc_settings()

	def test_auto_deferred_expense_entries_TC_ACC_092(self):
		"""Test automatic deferred expense entries on submission and monthly write-off."""
		from erpnext.accounts.doctype.purchase_invoice.test_purchase_invoice import make_purchase_invoice
		# Step 1: Set Accounting Settings
		change_acc_settings(acc_frozen_upto="2023-05-31", book_deferred_entries_based_on="Months")
		deferred_account = create_account(
			account_name="Deferred Expense", parent_account="Current Assets - _TC", company="_Test Company"
		)

		acc_settings = frappe.get_doc("Accounts Settings", "Accounts Settings")
		acc_settings.book_deferred_entries_via_journal_entry = 1
		acc_settings.submit_journal_entries = 1
		acc_settings.save()

		item = create_item("_Test Item for Deferred Accounting", is_purchase_item=True)
		item.enable_deferred_expense = 1
		item.item_defaults[0].deferred_expense_account = deferred_account
		item.save()

		pi = make_purchase_invoice(item=item.name, qty=1, rate=100, do_not_save=True)
		pi.set_posting_time = 1
		pi.posting_date = "2023-07-01"
		pi.items[0].enable_deferred_expense = 1
		pi.items[0].service_start_date = "2023-05-01"
		pi.items[0].service_end_date = "2023-07-31"
		pi.items[0].deferred_expense_account = deferred_account
		pi.save()
		pi.submit()

		process_deferred_expense = frappe.get_doc(
			dict(
				doctype="Process Deferred Accounting",
				posting_date="2023-07-01",
				start_date="2023-05-01",
				end_date="2023-06-30",
				type="Expense",
				company="_Test Company",
			)
		)

		process_deferred_expense.insert()
		process_deferred_expense.submit()
		# Step 5: Check Initial General Ledger Entry
		initial_gle = [
			[deferred_account, 6000, 0.0, "2023-07-01"],
			["Creditors - _TC", 0.0, 6000, "2023-07-01"],
		]
		check_gl_entries(self, pi.name, initial_gle, "2023-07-01")

		# Step 6: Process Deferred Expense Entries for the First Month
		process_deferred_expense = frappe.get_doc(
			dict(
				doctype="Process Deferred Accounting",
				posting_date="2023-07-31",
				start_date="2023-05-01",
				end_date="2023-06-30",
				type="Expense",
			)
		)

		process_deferred_expense.insert()
		process_deferred_expense.submit()

		# Step 7: Check Monthly Write-Off General Ledger Entry
		monthly_gle = [
			["Expense - _TC", 1000, 0.0, "2023-07-31"],
			[deferred_account, 0.0, 1000, "2023-07-31"],
		]
		check_gl_entries(self, pi.name, monthly_gle, "2023-07-31")

		# Step 8: Verify No Unexpected GL Entries
		remaining_months_gle = [
			["Expense - _TC", 1000, 0.0, "2023-08-31"],
			[deferred_account, 0.0, 1000, "2023-08-31"],
			["Expense - _TC", 1000, 0.0, "2023-09-30"],
			[deferred_account, 0.0, 1000, "2023-09-30"],
			["Expense - _TC", 1000, 0.0, "2023-10-31"],
			[deferred_account, 0.0, 1000, "2023-10-31"],
			["Expense - _TC", 1000, 0.0, "2023-11-30"],
			[deferred_account, 0.0, 1000, "2023-11-30"],
			["Expense - _TC", 1000, 0.0, "2023-12-31"],
			[deferred_account, 0.0, 1000, "2023-12-31"],
		]
		for idx, month_end_date in enumerate([
			"2023-08-31",
			"2023-09-30",
			"2023-10-31",
			"2023-11-30",
			"2023-12-31",
		]):
			check_gl_entries(self, pi.name, remaining_months_gle[idx * 2 : idx * 2 + 2], month_end_date)

		change_acc_settings()

	def test_auto_deferred_revenue_TC_ACC_093(self):
		"""Test auto deffered revenue on monthly basis."""
		change_acc_settings(acc_frozen_upto="2023-05-31", book_deferred_entries_based_on="Months")

		deferred_account = create_account(
			account_name="Deferred Revenue for Accounts Frozen",
			parent_account="Current Liabilities - _TC",
			company="_Test Company",
		)

		item = create_item("_Test Item for Deferred Accounting")
		item.enable_deferred_revenue = 1
		item.deferred_revenue_account = deferred_account
		item.no_of_months = 12
		item.save()

		si = create_sales_invoice(
			item=item.name, rate=3000, update_stock=0, posting_date="2023-07-01", do_not_submit=True
		)
		si.items[0].enable_deferred_revenue = 1
		si.items[0].service_start_date = "2023-05-01"
		si.items[0].service_end_date = "2023-07-31"
		si.items[0].deferred_revenue_account = deferred_account
		si.save()
		si.submit()

		process_deferred_accounting = frappe.get_doc(
			dict(
				doctype="Process Deferred Accounting",
				posting_date="2023-07-01",
				start_date="2023-05-01",
				end_date="2023-06-30",
				type="Income",
			)
		)

		process_deferred_accounting.insert()
		process_deferred_accounting.submit()

		expected_gle = [
			["Debtors - _TC", 3000, 0.0, "2023-07-01"],
			[deferred_account, 0.0, 3000, "2023-07-01"],
			["Sales - _TC", 0.0, 1000, "2023-06-30"],
			[deferred_account, 1000, 0.0, "2023-06-30"],
			["Sales - _TC", 0.0, 1000, "2023-06-30"],
			[deferred_account, 1000, 0.0, "2023-06-30"],
		]

		check_gl_entries(self, si.name, expected_gle, "2023-07-01")
		change_acc_settings()


	def test_pda_submission_and_cancellation(self):
		pda = frappe.get_doc(
			dict(
				doctype="Process Deferred Accounting",
				posting_date="2019-01-01",
				start_date="2019-01-01",
				end_date="2019-01-31",
				type="Income",
			)
		)
		pda.submit()
		pda.cancel()


def change_acc_settings(acc_frozen_upto="", book_deferred_entries_based_on="Days"):
	acc_settings = frappe.get_doc("Accounts Settings", "Accounts Settings")
	acc_settings.acc_frozen_upto = acc_frozen_upto
	acc_settings.book_deferred_entries_based_on = book_deferred_entries_based_on
	acc_settings.save()
