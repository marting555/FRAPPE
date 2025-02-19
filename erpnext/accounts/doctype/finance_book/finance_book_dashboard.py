import frappe
from frappe import _


def get_data():
	non_standard_fieldnames = {"Company": "default_finance_book"}
	transactions = [
			{"items": ["Company"]},
			{"items": ["Journal Entry"]},
		]
	
	if "assets" in frappe.get_installed_apps():
		non_standard_fieldnames.update({"Asset": "default_finance_book"})
		transactions.insert(0, {"label": _("Assets"), "items": ["Asset", "Asset Value Adjustment"]})

	return {
		"fieldname": "finance_book",
		"non_standard_fieldnames": non_standard_fieldnames,
		"transactions": transactions,
	}
