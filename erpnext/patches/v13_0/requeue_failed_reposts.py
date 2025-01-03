import frappe
from frappe.utils import cstr


def execute():
	reposts = frappe.get_all(
		"Repost Item Valuation",
		["name", "modified", "error_log"],
		{"status": "Failed", "modified": [">", "2021-10-05"]},
	)

	for repost in reposts:
		if "check_freezing_date" in cstr(repost.error_log):
			frappe.db.set_value("Repost Item Valuation", repost.name, "status", "Queued")
