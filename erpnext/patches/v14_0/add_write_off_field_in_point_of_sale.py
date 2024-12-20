import frappe


def execute():
	if not frappe.db.exists(
		"POS Field",
		{"parent": "POS Settings", "parentfield": "invoice_fields", "fieldname": "write_off_amount"},
		"write_off_amount",
	):
		setting_doc = frappe.get_doc("POS Settings")
		field_property = {}

		for field in frappe.get_meta("POS Invoice").fields:
			if field.fieldname == "write_off_amount":
				field_property = {
					"label": field.label,
					"fieldname": field.fieldname,
					"reqd": field.reqd,
					"options": field.options,
					"fieldtype": field.fieldtype,
					"default_value": field.default,
				}

		if field_property:
			setting_doc.append("invoice_fields", field_property)
			setting_doc.save()
