# Copyright (c) 2024, VINOD GAJJALA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PaymentReconciliationRecord(Document):
	def on_cancel(self):
		frappe.throw(_("Cancelling records is not allowed."))