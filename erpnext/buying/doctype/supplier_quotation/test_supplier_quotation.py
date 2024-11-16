# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.tests.utils import FrappeTestCase
from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_quotation


class TestPurchaseOrder(FrappeTestCase):
	def test_make_purchase_order(self):
		from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order

		sq = frappe.copy_doc(test_records[0]).insert()

		self.assertRaises(frappe.ValidationError, make_purchase_order, sq.name)

		sq = frappe.get_doc("Supplier Quotation", sq.name)
		sq.submit()
		po = make_purchase_order(sq.name)

		self.assertEqual(po.doctype, "Purchase Order")
		self.assertEqual(len(po.get("items")), len(sq.get("items")))

		po.naming_series = "_T-Purchase Order-"

		for doc in po.get("items"):
			if doc.get("item_code"):
				doc.set("schedule_date", "2013-04-12")

		po.insert()

	# test make quotation from supplier quotation 
	def test_make_quotation(self):
		sq = frappe.copy_doc(test_records[0]).insert()
		sq = frappe.get_doc("Supplier Quotation", sq.name)
		sq.submit()
	
		qt = make_quotation(sq.name)
		qt.quotation_to = 'Customer'
		qt.customer_name = '_Test Customer'
		qt.submit()
		
		self.assertEqual(sq.doctype, "Supplier Quotation")
		self.assertEqual(qt.doctype, "Quotation")
		self.assertEqual(len(sq.get("items")), len(qt.get("items")))
		self.assertEqual(sq.get("items")[0].item_code, qt.get("items")[0].item_code)
		self.assertEqual(sq.get("items")[0].qty, qt.get("items")[0].qty)

test_records = frappe.get_test_records("Supplier Quotation")
