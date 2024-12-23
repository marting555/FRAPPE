import frappe
from frappe import _

from erpnext.buying.doc_events.create_entry import (
	create_address,
	create_bank_account,
	create_contact,
	create_supplier,
)
from erpnext.buying.doc_events.create_ldc_entry import create_ldc


def create_vendor_entry(self):
	if self.docstatus == 1:
		supplier = frappe.db.exists("Supplier", self.vendor_name)
		if not supplier:
			# create supplier
			supplier = create_supplier(self)
			# create address
			address = create_address(self, supplier)
			# create contact
			contact = create_contact(self, supplier)
			# create bank account
			bank_acc = create_bank_account(self)
			# create LDC entry
			if self.lower_tds_deduction_applicable == "Yes":
				ldc_entry = create_ldc(self, supplier)
				if ldc_entry:
					frappe.msgprint(
						_(
							"The following documents are created <br><ol><li>Supplier: {0}</li><li>Address: {1}</li><li>Contact: {2}</li><li>Bank: {3}</li></li><li>LDC: {4}</li></ol>"
						).format(supplier, address, contact, bank_acc, ldc_entry)
					)
			else:
				frappe.msgprint(
					_(
						"The following documents are created <br><ol><li>Supplier: {0}</li><li>Address: {1}</li><li>Contact: {2}</li><li>Bank: {3}</li></ol>"
					).format(supplier, address, contact, bank_acc)
				)
		else:
			frappe.throw(_("Supplier already exists in the system"))
