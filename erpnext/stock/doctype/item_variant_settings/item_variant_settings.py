# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import typing

import frappe
from frappe import _
from frappe.model.document import Document
import erpnext
from frappe.utils import cstr


class ItemVariantSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.stock.doctype.variant_field.variant_field import VariantField

		allow_different_uom: DF.Check
		allow_rename_attribute_value: DF.Check
		do_not_update_variants: DF.Check
		fields: DF.Table[VariantField]
	# end: auto-generated types

	invalid_fields_for_copy_fields_in_variants: typing.ClassVar[list] = ["barcodes"]

	def set_default_fields(self):
		self.fields = []
		fields = frappe.get_meta("Item").fields
		exclude_fields = {
			"naming_series",
			"item_code",
			"item_name",
			"published_in_website",
			"standard_rate",
			"opening_stock",
			"image",
			"description",
			"variant_of",
			"valuation_rate",
			"barcodes",
			"has_variants",
			"attributes",
		}

		for d in fields:
			if (
				not d.no_copy
				and d.fieldname not in exclude_fields
				and d.fieldtype not in ["HTML", "Section Break", "Column Break", "Button", "Read Only"]
			):
				self.append("fields", {"field_name": d.fieldname})

	def remove_invalid_fields_for_copy_fields_in_variants(self):
		fields = [
			row
			for row in self.fields
			if row.field_name not in self.invalid_fields_for_copy_fields_in_variants
		]
		self.fields = fields
		self.save()

	def validate(self):
		for d in self.fields:
			if d.field_name in self.invalid_fields_for_copy_fields_in_variants:
				frappe.throw(
					_("Cannot set the field <b>{0}</b> for copying in variants").format(d.field_name)
				)
    
    
@frappe.whitelist()
@erpnext.sanitize_autocomplete_input
def get_item_fields(existing_fields):
	allow_fields = []
	field_label_map = {}

	exclude_field_types = [
		"HTML", "Section Break", "Column Break", "Button", "Read Only", "Tab Break"
	]

	exclude_fields = set(existing_fields or [])
	exclude_fields.update(
		[
			"naming_series",
			"item_code",
			"item_name",
			"published_in_website",
			"standard_rate",
			"opening_stock",
			"image",
			"variant_of",
			"valuation_rate",
			"barcodes",
			"has_variants",
			"attributes",
		]
    )

	item_meta = frappe.get_meta("Item")

	for field in item_meta.fields:
		field_label_map[field.fieldname] = _(cstr(field.label)) + f" ({field.fieldname})"

		if (
			field.fieldtype not in exclude_field_types and
			not field.no_copy and
			field.fieldname not in exclude_fields
		):
			allow_fields.append({
				"label": field_label_map[field.fieldname],
				"value": field.fieldname,
			})

	if not allow_fields:
		allow_fields.append({
			"label": _("No additional fields available"),
			"value": "",
		})

	return allow_fields
