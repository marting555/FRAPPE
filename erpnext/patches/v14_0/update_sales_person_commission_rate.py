import frappe
import re

def execute():
	number_format = frappe.db.get_default("number_format")
	if number_format in ["#.###,##", "#,###", "# ###,##"]:

		sales_persons = frappe.get_all("Sales Person",
			fields=["commission_rate", "name"]
		)

		for sp in sales_persons:
			if not sp.commission_rate:
				sp.commission_rate = 0
			commission_rate = str(sp.commission_rate).replace(",", ".")
			if not re.fullmatch(r'^[0-9]+(\.[0-9]+)?$', str(commission_rate)):
				commission_rate = 0
			frappe.db.set_value("Sales Person", sp.name, "commission_rate", commission_rate)
