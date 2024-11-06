# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class WBSBudget(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.budget_account.budget_account import BudgetAccount
		from erpnext.accounts.doctype.wbs_budget_items.wbs_budget_items import WBSBudgetItems
		from frappe.types import DF

		accounts: DF.Table[BudgetAccount]
		action_if_accumulated_monthly_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_accumulated_monthly_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_mr: DF.Literal["", "Stop", "Warn", "Ignore"]
		action_if_annual_budget_exceeded_on_po: DF.Literal["", "Stop", "Warn", "Ignore"]
		amended_from: DF.Link | None
		applicable_on_booking_actual_expenses: DF.Check
		applicable_on_material_request: DF.Check
		applicable_on_purchase_order: DF.Check
		available_budget: DF.Currency
		budget_against: DF.Literal["", "Cost Center", "Project"]
		company: DF.Link | None
		cost_center: DF.Link | None
		fiscal_year: DF.Link | None
		from_date: DF.Date | None
		monthly_distribution: DF.Link | None
		project: DF.Link | None
		to_date: DF.Date | None
		wbs: DF.Link | None
		wbs_budget_items: DF.Table[WBSBudgetItems]
	# end: auto-generated types

	def on_submit(self):
		for item in self.accounts:
			budget_entry = frappe.new_doc("Budget Entry")
			budget_entry.name = self.name
			budget_entry.project = self.project
			budget_entry.company = self.company
			# budget_entry.posting_date = self.posting_date
			# budget_entry.document_datbudget_amounte = self.document_date

			if item.child_wbs:
				budget_entry.wbs = item.child_wbs

			if item.budget_amount:
				budget_entry.overall_credit = item.budget_amount

			wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
			if wbs.wbs_name:
				budget_entry.wbs_name = wbs.wbs_name

			if wbs.wbs_level:
				budget_entry.wbs_level = wbs.wbs_level
			
			budget_entry.voucher_no = self.name
			budget_entry.voucher_type = "WBS Budget"
			budget_entry.voucher_submit_date = now()

			budget_entry.insert()
			budget_entry.submit()

		update_wbs(self)

	def on_cancel(self):
		self.flags.ignore_links = True
		print("on cancel")

	def before_cancel(self):
		create_cancelled_budget_entries(self)		

def update_wbs(self):
	for row in self.accounts:
		wbs = frappe.get_doc("Work Breakdown Structure",row.child_wbs)
		if row.budget_amount:
			wbs.overall_budget += row.budget_amount
		wbs.save()

def create_cancelled_budget_entries(self):
	for item in self.accounts:
		budget_entry = frappe.new_doc("Budget Entry")
		budget_entry.name = self.name
		budget_entry.project = self.project
		budget_entry.company = self.company
		# budget_entry.posting_date = self.posting_date
		# budget_entry.document_datbudget_amounte = self.document_date

		if item.child_wbs:
			budget_entry.wbs = item.child_wbs

		if item.budget_amount:
			budget_entry.overall_debit = item.budget_amount

		wbs = frappe.get_doc("Work Breakdown Structure",item.child_wbs)
		if wbs.wbs_name:
			budget_entry.wbs_name = wbs.wbs_name

		if wbs.wbs_level:
			budget_entry.wbs_level = wbs.wbs_level
		
		budget_entry.voucher_no = self.name
		budget_entry.voucher_type = "WBS Budget"
		budget_entry.voucher_submit_date = now()

		budget_entry.insert()
		budget_entry.submit()

	update_wbs_after_cancellation(self)

def update_wbs_after_cancellation(self):
	for row in self.accounts:
		wbs = frappe.get_doc("Work Breakdown Structure",row.child_wbs)
		if row.budget_amount:
			wbs.overall_budget -= row.budget_amount
		wbs.save()

@frappe.whitelist()
def get_gl_accounts(wbs):
	child_wbs_records = frappe.get_all("Work Breakdown Structure", 
		filters= {"parent_work_breakdown_structure":wbs,"is_group":0},
		fields=["name","gl_account"]
	)
	return child_wbs_records