import frappe


def execute():
<<<<<<< HEAD
	frappe.reload_doc("maintenance", "doctype", "Maintenance Schedule Detail")
	frappe.db.sql(
		"""
		UPDATE `tabMaintenance Schedule Detail`
		SET completion_status = 'Pending'
		WHERE docstatus < 2
	"""
	)
=======
	frappe.db.sql("""
		UPDATE `tabMaintenance Schedule Detail`
		SET completion_status = 'Pending'
		WHERE docstatus < 2
	""")
>>>>>>> cc143bca0d (fix: Maintenance Schedule child table status for legacy data (#27554))
