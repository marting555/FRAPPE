# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AccountBalanceRecord(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link | None
		balance: DF.Currency
		from_date: DF.Date | None
		to_date: DF.Date | None
		total_credit: DF.Currency
		total_debit: DF.Currency
	# end: auto-generated types
	pass
