# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DemoDoctype1(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attach_image: DF.AttachImage | None
		attachment: DF.Attach | None
		demo: DF.Data | None
		fist_name: DF.Data
	# end: auto-generated types
	pass
