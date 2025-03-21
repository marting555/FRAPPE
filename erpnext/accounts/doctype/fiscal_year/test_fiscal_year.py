# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import unittest

import frappe
from frappe.utils import now_datetime
from datetime import date

test_ignore = ["Company"]


class TestFiscalYear(unittest.TestCase):
	def test_extra_year(self):
		if frappe.db.exists("Fiscal Year", "_Test Fiscal Year 2000"):
			frappe.delete_doc("Fiscal Year", "_Test Fiscal Year 2000")

		fy = frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": "_Test Fiscal Year 2000",
				"year_end_date": "2002-12-31",
				"year_start_date": "2000-04-01",
			}
		)

		self.assertRaises(frappe.exceptions.InvalidDates, fy.insert)


def test_record_generator():
	test_records = [
		{
			"doctype": "Fiscal Year",
			"year": "_Test Short Fiscal Year 2011",
			"is_short_year": 1,
			"year_start_date": "2011-04-01",
			"year_end_date": "2011-12-31",
		}
	]

	start = 2012
	end = now_datetime().year + 25
	for year in range(start, end):
		test_records.append(
			{
				"doctype": "Fiscal Year",
				"year": f"_Test Fiscal Year {year}",
				"year_start_date": f"{year}-01-01",
				"year_end_date": f"{year}-12-31",
			}
		)

	return test_records


test_records = test_record_generator()

def create_fiscal_year(company=None):
	today = date.today()
	if today.month >= 4:  # Fiscal year starts in April
		start_date = date(today.year, 4, 1)
		end_date = date(today.year + 1, 3, 31)
	else:
		start_date = date(today.year - 1, 4, 1)
		end_date = date(today.year, 3, 31)
	if company != None:
		company = company
	else:
		create_company()
		company="_Test Company MR"
	fy_list = frappe.db.get_all("Fiscal Year", {"year_start_date":start_date, "year_end_date": end_date}, pluck='name')
	for i in fy_list:
		if frappe.db.get_value("Fiscal Year Company", {'parent': i}, 'company') == "_Test Company MR":
			frappe.msgprint(f"Fiscal Year already exists for {company}", alert=True)
			return
	
	existing_fiscal_years = frappe.db.sql(
			"""select name from `tabFiscal Year`
			where (
				(%(year_start_date)s between year_start_date and year_end_date)
				or (%(year_end_date)s between year_start_date and year_end_date)
				or (year_start_date between %(year_start_date)s and %(year_end_date)s)
				or (year_end_date between %(year_start_date)s and %(year_end_date)s)
			)""",
			{
				"year_start_date": start_date,
				"year_end_date": end_date,
			},
			as_dict=True,
		)
	
	#fix for overlapping fiscal year
	if existing_fiscal_years != []:
		for fiscal_years in existing_fiscal_years:
			fy_doc = frappe.get_doc("Fiscal Year",fiscal_years.get("name"))
			if not frappe.db.exists("Fiscal Year Company", {"company": company}):
				fy_doc.append("companies", {"company": company})
				fy_doc.save()
	else:
		fy_doc = frappe.new_doc("Fiscal Year")
		fy_doc.year = "2025 PO"
		fy_doc.year_start_date = start_date
		fy_doc.year_end_date = end_date
		fy_doc.append("companies", {"company": company})
		fy_doc.insert()
		fy_doc.submit()


def create_company():
	frappe.set_user("Administrator")
	if not frappe.db.exists("Company", "_Test Company"):
		frappe.get_doc({
			"doctype": "Company",
			"company_name": "_Test Company",
			"company_type": "Company",
			"default_currency": "INR",
			"company_email": "test@example.com",
			"abbr":"_TC"
		}).insert(ignore_permissions=True)
		
