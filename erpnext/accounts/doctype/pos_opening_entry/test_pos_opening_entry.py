# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

from erpnext.accounts.doctype.pos_invoice.test_pos_invoice import create_pos_invoice
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening
import frappe


class TestPOSOpeningEntry(unittest.TestCase):

	def test_pos_opening_to_pos_closing_TC_S_099(self):
		from erpnext.accounts.doctype.pos_closing_entry.test_pos_closing_entry import init_user_and_profile		
		test_user, pos_profile = init_user_and_profile()

		opening_entry = create_opening_entry(pos_profile=pos_profile, user=test_user.name)
		self.assertEqual(opening_entry.status, "Open")


		pos_inv1 = create_pos_invoice(rate=3500, do_not_submit=1)
		pos_inv1.append("payments", {"mode_of_payment": "Cash", "account": "Cash - _TC", "amount": 3500})
		pos_inv1.submit()

		pos_inv2 = create_pos_invoice(rate=3200, do_not_submit=1)
		pos_inv2.append("payments", {"mode_of_payment": "Cash", "account": "Cash - _TC", "amount": 3200})
		pos_inv2.submit()

		closing_enrty= make_closing_entry_from_opening(opening_entry)
		closing_enrty.submit()
		opening_entry.reload()
		self.assertEqual(opening_entry.status, "Closed")



def create_opening_entry(pos_profile, user):
	entry = frappe.new_doc("POS Opening Entry")
	entry.pos_profile = pos_profile.name
	entry.user = user
	entry.company = pos_profile.company
	entry.period_start_date = frappe.utils.get_datetime()

	balance_details = []
	for d in pos_profile.payments:
		balance_details.append(frappe._dict({"mode_of_payment": d.mode_of_payment}))

	entry.set("balance_details", balance_details)
	entry.submit()

	return entry
