import os
import json
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as make_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
import frappe


def after_migrate():
	create_custom_fields()

def create_custom_fields():
	CUSTOM_FIELDS = {}
	print("Creating/Updating Custom Fields For Erpnext....")
	path = os.path.join(os.path.dirname(__file__), "erpnext/buying/custom_fields")
	for file in os.listdir(path):
		with open(os.path.join(path, file), "r") as f:
			CUSTOM_FIELDS.update(json.load(f))
	make_custom_fields(CUSTOM_FIELDS)