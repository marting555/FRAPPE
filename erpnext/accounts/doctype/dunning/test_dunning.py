# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
<<<<<<< HEAD

import unittest

import frappe
=======
import json

import frappe
from frappe.model import mapper
from frappe.tests import IntegrationTestCase, UnitTestCase
>>>>>>> 3b613c44a6 (chore: added test for `Fetch Overdue Payments` in dunning)
from frappe.utils import add_days, nowdate, today

from erpnext.accounts.doctype.dunning.dunning import calculate_interest_and_amount
from erpnext.accounts.doctype.payment_entry.test_payment_entry import get_payment_entry
from erpnext.accounts.doctype.purchase_invoice.test_purchase_invoice import (
	unlink_payment_on_cancel_of_invoice,
)
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import (
	create_sales_invoice_against_cost_center,
)


class TestDunning(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		create_dunning_type()
		create_dunning_type_with_zero_interest_rate()
		unlink_payment_on_cancel_of_invoice()

	@classmethod
	def tearDownClass(self):
		unlink_payment_on_cancel_of_invoice(0)

	def test_dunning(self):
		dunning = create_dunning()
		amounts = calculate_interest_and_amount(
			dunning.outstanding_amount, dunning.rate_of_interest, dunning.dunning_fee, dunning.overdue_days
		)
		self.assertEqual(round(amounts.get("interest_amount"), 2), 0.44)
		self.assertEqual(round(amounts.get("dunning_amount"), 2), 20.44)
		self.assertEqual(round(amounts.get("grand_total"), 2), 120.44)

	def test_dunning_with_zero_interest_rate(self):
		dunning = create_dunning_with_zero_interest_rate()
		amounts = calculate_interest_and_amount(
			dunning.outstanding_amount, dunning.rate_of_interest, dunning.dunning_fee, dunning.overdue_days
		)
		self.assertEqual(round(amounts.get("interest_amount"), 2), 0)
		self.assertEqual(round(amounts.get("dunning_amount"), 2), 20)
		self.assertEqual(round(amounts.get("grand_total"), 2), 120)

	def test_gl_entries(self):
		dunning = create_dunning()
		dunning.submit()
		gl_entries = frappe.db.sql(
			"""select account, debit, credit
			from `tabGL Entry` where voucher_type='Dunning' and voucher_no=%s
			order by account asc""",
			dunning.name,
			as_dict=1,
		)
		self.assertTrue(gl_entries)
		expected_values = dict(
			(d[0], d) for d in [["Debtors - _TC", 20.44, 0.0], ["Sales - _TC", 0.0, 20.44]]
		)
		for gle in gl_entries:
			self.assertEqual(expected_values[gle.account][0], gle.account)
			self.assertEqual(expected_values[gle.account][1], gle.debit)
			self.assertEqual(expected_values[gle.account][2], gle.credit)

	def test_payment_entry(self):
		dunning = create_dunning()
		dunning.submit()
		pe = get_payment_entry("Dunning", dunning.name)
		pe.reference_no = "1"
		pe.reference_date = nowdate()
		pe.paid_from_account_currency = dunning.currency
		pe.paid_to_account_currency = dunning.currency
		pe.source_exchange_rate = 1
		pe.target_exchange_rate = 1
		pe.insert()
		pe.submit()
<<<<<<< HEAD
		si_doc = frappe.get_doc("Sales Invoice", dunning.sales_invoice)
		self.assertEqual(si_doc.outstanding_amount, 0)
=======

		for overdue_payment in dunning.overdue_payments:
			outstanding_amount = frappe.get_value(
				"Sales Invoice", overdue_payment.sales_invoice, "outstanding_amount"
			)
			self.assertEqual(outstanding_amount, 0)

		dunning.reload()
		self.assertEqual(dunning.status, "Resolved")

	def test_fetch_overdue_payments(self):
		"""
		Create SI with overdue payment. Check if overdue payment is fetched in Dunning.
		"""
		si1 = create_sales_invoice_against_cost_center(
			posting_date=add_days(today(), -1 * 6),
			qty=1,
			rate=100,
		)

		si2 = create_sales_invoice_against_cost_center(
			posting_date=add_days(today(), -1 * 6),
			qty=1,
			rate=300,
		)

		dunning = create_dunning_from_sales_invoice(si1.name)
		dunning.overdue_payments = []

		method = "erpnext.accounts.doctype.sales_invoice.sales_invoice.create_dunning"
		updated_dunning = mapper.map_docs(method, json.dumps([si1.name, si2.name]), dunning)

		self.assertEqual(len(updated_dunning.overdue_payments), 2)

		self.assertEqual(updated_dunning.overdue_payments[0].sales_invoice, si1.name)
		self.assertEqual(updated_dunning.overdue_payments[0].outstanding, si1.outstanding_amount)

		self.assertEqual(updated_dunning.overdue_payments[1].sales_invoice, si2.name)
		self.assertEqual(updated_dunning.overdue_payments[1].outstanding, si2.outstanding_amount)

	def test_dunning_and_payment_against_partially_due_invoice(self):
		"""
		Create SI with first installment overdue. Check impact of Dunning and Payment Entry.
		"""
		create_payment_terms_template_for_dunning()
		sales_invoice = create_sales_invoice_against_cost_center(
			posting_date=add_days(today(), -1 * 6),
			qty=1,
			rate=100,
			do_not_submit=True,
		)
		sales_invoice.payment_terms_template = "_Test 50-50 for Dunning"
		sales_invoice.submit()
		dunning = create_dunning_from_sales_invoice(sales_invoice.name)

		self.assertEqual(len(dunning.overdue_payments), 1)
		self.assertEqual(dunning.overdue_payments[0].payment_term, "_Test Payment Term 1 for Dunning")

		dunning.submit()
		pe = get_payment_entry("Dunning", dunning.name)
		pe.reference_no, pe.reference_date = "2", nowdate()
		pe.insert()
		pe.submit()
		sales_invoice.load_from_db()
		dunning.load_from_db()

		self.assertEqual(sales_invoice.status, "Partly Paid")
		self.assertEqual(sales_invoice.payment_schedule[0].outstanding, 0)
		self.assertEqual(dunning.status, "Resolved")

		# Test impact on cancellation of PE
		pe.cancel()
		sales_invoice.reload()
		dunning.reload()

		self.assertEqual(sales_invoice.status, "Overdue")
		self.assertEqual(dunning.status, "Unresolved")
>>>>>>> 3b613c44a6 (chore: added test for `Fetch Overdue Payments` in dunning)


def create_dunning():
	posting_date = add_days(today(), -20)
	due_date = add_days(today(), -15)
	sales_invoice = create_sales_invoice_against_cost_center(
		posting_date=posting_date, due_date=due_date, status="Overdue"
	)
	dunning_type = frappe.get_doc("Dunning Type", "First Notice")
	dunning = frappe.new_doc("Dunning")
	dunning.sales_invoice = sales_invoice.name
	dunning.customer_name = sales_invoice.customer_name
	dunning.outstanding_amount = sales_invoice.outstanding_amount
	dunning.debit_to = sales_invoice.debit_to
	dunning.currency = sales_invoice.currency
	dunning.company = sales_invoice.company
	dunning.posting_date = nowdate()
	dunning.due_date = sales_invoice.due_date
	dunning.dunning_type = "First Notice"
	dunning.rate_of_interest = dunning_type.rate_of_interest
	dunning.dunning_fee = dunning_type.dunning_fee
	dunning.save()
	return dunning


def create_dunning_with_zero_interest_rate():
	posting_date = add_days(today(), -20)
	due_date = add_days(today(), -15)
	sales_invoice = create_sales_invoice_against_cost_center(
		posting_date=posting_date, due_date=due_date, status="Overdue"
	)
	dunning_type = frappe.get_doc("Dunning Type", "First Notice with 0% Rate of Interest")
	dunning = frappe.new_doc("Dunning")
	dunning.sales_invoice = sales_invoice.name
	dunning.customer_name = sales_invoice.customer_name
	dunning.outstanding_amount = sales_invoice.outstanding_amount
	dunning.debit_to = sales_invoice.debit_to
	dunning.currency = sales_invoice.currency
	dunning.company = sales_invoice.company
	dunning.posting_date = nowdate()
	dunning.due_date = sales_invoice.due_date
	dunning.dunning_type = "First Notice with 0% Rate of Interest"
	dunning.rate_of_interest = dunning_type.rate_of_interest
	dunning.dunning_fee = dunning_type.dunning_fee
	dunning.save()
	return dunning


def create_dunning_type():
	dunning_type = frappe.new_doc("Dunning Type")
	dunning_type.dunning_type = "First Notice"
	dunning_type.start_day = 10
	dunning_type.end_day = 20
	dunning_type.dunning_fee = 20
	dunning_type.rate_of_interest = 8
	dunning_type.append(
		"dunning_letter_text",
		{
			"language": "en",
			"body_text": "We have still not received payment for our invoice ",
			"closing_text": "We kindly request that you pay the outstanding amount immediately, including interest and late fees.",
		},
	)
	dunning_type.save()


def create_dunning_type_with_zero_interest_rate():
	dunning_type = frappe.new_doc("Dunning Type")
	dunning_type.dunning_type = "First Notice with 0% Rate of Interest"
	dunning_type.start_day = 10
	dunning_type.end_day = 20
	dunning_type.dunning_fee = 20
	dunning_type.rate_of_interest = 0
	dunning_type.append(
		"dunning_letter_text",
		{
			"language": "en",
			"body_text": "We have still not received payment for our invoice ",
			"closing_text": "We kindly request that you pay the outstanding amount immediately, and late fees.",
		},
	)
	dunning_type.save()
