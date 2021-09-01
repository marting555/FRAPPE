# Copyright (c) 2021, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
<<<<<<< HEAD


def execute():
	frappe.reload_doc("accounts", "doctype", "Tax Withholding Rate")

	if frappe.db.has_column("Tax Withholding Rate", "fiscal_year"):
		tds_category_rates = frappe.get_all("Tax Withholding Rate", fields=["name", "fiscal_year"])

		fiscal_year_map = {}
		fiscal_year_details = frappe.get_all(
			"Fiscal Year", fields=["name", "year_start_date", "year_end_date"]
		)

		for d in fiscal_year_details:
			fiscal_year_map.setdefault(d.name, d)

		for rate in tds_category_rates:
			from_date = fiscal_year_map.get(rate.fiscal_year).get("year_start_date")
			to_date = fiscal_year_map.get(rate.fiscal_year).get("year_end_date")

			frappe.db.set_value(
				"Tax Withholding Rate", rate.name, {"from_date": from_date, "to_date": to_date}
			)
=======
from erpnext.accounts.utils import get_fiscal_year

def execute():
	frappe.reload_doc('accounts', 'doctype', 'Tax Withholding Rate')

	if frappe.db.has_column('Tax Withholding Rate', 'fiscal_year'):
		tds_category_rates = frappe.get_all('Tax Withholding Rate', fields=['name', 'fiscal_year'])

		fiscal_year_map = {}
		for rate in tds_category_rates:
			if not fiscal_year_map.get(rate.fiscal_year):
				fiscal_year_map[rate.fiscal_year] = get_fiscal_year(fiscal_year=rate.fiscal_year)

<<<<<<< HEAD
		frappe.db.set_value('Tax Withholding Rate', rate.name, {
			'from_date': from_date,
			'to_date': to_date
		})
>>>>>>> 5e10e10329 (feat: Validity dates in Tax Withholding Rates)
=======
			from_date = fiscal_year_map.get(rate.fiscal_year)[1]
			to_date = fiscal_year_map.get(rate.fiscal_year)[2]

			frappe.db.set_value('Tax Withholding Rate', rate.name, {
				'from_date': from_date,
				'to_date': to_date
			})
>>>>>>> b6d0b17ed6 (fix: Linting and patch fixes)
