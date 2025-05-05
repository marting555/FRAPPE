# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

<<<<<<< HEAD
# test_records = frappe.get_test_records('Mode of Payment')
=======
import frappe
from frappe.tests import IntegrationTestCase
>>>>>>> 8067799692 (fix: update accounts on change of mode of payment in sales invoice payment (#47381))


class TestModeofPayment(unittest.TestCase):
	pass


def set_default_account_for_mode_of_payment(mode_of_payment, company, account):
	mode_of_payment.reload()
	if frappe.db.exists(
		"Mode of Payment Account", {"parent": mode_of_payment.mode_of_payment, "company": company}
	):
		frappe.db.set_value(
			"Mode of Payment Account",
			{"parent": mode_of_payment.mode_of_payment, "company": company},
			"default_account",
			account,
		)
		return

	mode_of_payment.append("accounts", {"company": company, "default_account": account})
	mode_of_payment.save()
