# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class POSSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.pos_field.pos_field import POSField
		from erpnext.accounts.doctype.pos_search_fields.pos_search_fields import POSSearchFields

		invoice_fields: DF.Table[POSField]
		pos_search_fields: DF.Table[POSSearchFields]
	# end: auto-generated types

	def validate(self):
		self.validate_invoice_fields()

	def validate_invoice_fields(self):
		invoice_fields_count = {}
		for d in self.invoice_fields:
			if invoice_fields_count.get(d.fieldname):
				frappe.throw(_("Each POSField in the POS Settings can only have one instance."))
			invoice_fields_count[d.fieldname] = 1
