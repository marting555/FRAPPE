# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EmployeeEmergencyContacts(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		emergency_phone_number: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		person_to_be_contacted: DF.Data | None
		relation: DF.Data | None
	# end: auto-generated types

	pass
