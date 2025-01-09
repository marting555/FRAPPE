import frappe

from erpnext.accounts.utils import sync_auto_reconcile_config


def execute():
	"""
	Set default Cron Interval and Queue size
	"""
	frappe.db.set_single_value("Accounts Settings", "cron_interval", 15)
	frappe.db.set_single_value("Accounts Settings", "queue_size", 5)
	sync_auto_reconcile_config()
