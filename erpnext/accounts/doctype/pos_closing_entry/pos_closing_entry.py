# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder import functions as fn
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import flt, get_datetime

from erpnext.accounts.doctype.pos_invoice_merge_log.pos_invoice_merge_log import (
	consolidate_pos_invoices,
	unconsolidate_pos_invoices,
)
from erpnext.controllers.status_updater import StatusUpdater


class POSClosingEntry(StatusUpdater):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.pos_closing_entry_detail.pos_closing_entry_detail import (
			POSClosingEntryDetail,
		)
		from erpnext.accounts.doctype.pos_closing_entry_taxes.pos_closing_entry_taxes import (
			POSClosingEntryTaxes,
		)
		from erpnext.accounts.doctype.pos_invoice_reference.pos_invoice_reference import POSInvoiceReference
		from erpnext.accounts.doctype.sales_invoice_reference.sales_invoice_reference import (
			SalesInvoiceReference,
		)

		amended_from: DF.Link | None
		company: DF.Link
		error_message: DF.SmallText | None
		grand_total: DF.Currency
		net_total: DF.Currency
		payment_reconciliation: DF.Table[POSClosingEntryDetail]
		period_end_date: DF.Datetime
		period_start_date: DF.Datetime
		pos_invoices: DF.Table[POSInvoiceReference]
		pos_opening_entry: DF.Link
		pos_profile: DF.Link
		posting_date: DF.Date
		posting_time: DF.Time
		sales_invoices: DF.Table[SalesInvoiceReference]
		status: DF.Literal["Draft", "Submitted", "Queued", "Failed", "Cancelled"]
		taxes: DF.Table[POSClosingEntryTaxes]
		total_quantity: DF.Float
		user: DF.Link
	# end: auto-generated types

	def validate(self):
		self.set_posting_date_and_time()
		self.fetch_invoice_doctype_in_pos()
		self.validate_pos_opening_entry()
		self.validate_invoice_mode()

	def set_posting_date_and_time(self):
		self.posting_date = self.posting_date or frappe.utils.nowdate()
		self.posting_time = self.posting_time or frappe.utils.nowtime()

	def fetch_invoice_doctype_in_pos(self):
		self.invoice_doctype_in_pos = frappe.db.get_single_value(
			"Accounts Settings", "invoice_doctype_in_pos"
		)

	def validate_pos_opening_entry(self):
		if frappe.db.get_value("POS Opening Entry", self.pos_opening_entry, "status") != "Open":
			frappe.throw(_("Selected POS Opening Entry should be open."), title=_("Invalid Opening Entry"))

	def validate_invoice_mode(self):
		if self.invoice_doctype_in_pos == "POS Invoice":
			self.validate_duplicate_pos_invoices()
			self.validate_pos_invoices()

		if self.invoice_doctype_in_pos == "Sales Invoice":
			if len(self.pos_invoices) != 0:
				frappe.throw(_("POS Invoices can't be added when Sales Invoice is enabled"))

		self.validate_duplicate_sales_invoices()
		self.validate_sales_invoices()

	def validate_duplicate_pos_invoices(self):
		pos_occurences = {}
		for idx, inv in enumerate(self.pos_invoices, 1):
			pos_occurences.setdefault(inv.pos_invoice, []).append(idx)

		error_list = []
		for key, value in pos_occurences.items():
			if len(value) > 1:
				error_list.append(
					_("{0} is added multiple times on rows: {1}").format(frappe.bold(key), frappe.bold(value))
				)

		if error_list:
			frappe.throw(error_list, title=_("Duplicate POS Invoices found"), as_list=True)

	def validate_pos_invoices(self):
		invalid_rows = []
		for d in self.pos_invoices:
			invalid_row = {"idx": d.idx}
			pos_invoice = frappe.db.get_values(
				"POS Invoice",
				d.pos_invoice,
				["consolidated_invoice", "pos_profile", "docstatus", "owner"],
				as_dict=1,
			)[0]
			if pos_invoice.consolidated_invoice:
				invalid_row.setdefault("msg", []).append(_("POS Invoice is already consolidated"))
				invalid_rows.append(invalid_row)
				continue
			if pos_invoice.pos_profile != self.pos_profile:
				invalid_row.setdefault("msg", []).append(
					_("POS Profile doesn't match {}").format(frappe.bold(self.pos_profile))
				)
			if pos_invoice.docstatus != 1:
				invalid_row.setdefault("msg", []).append(_("POS Invoice is not submitted"))
			if pos_invoice.owner != self.user:
				invalid_row.setdefault("msg", []).append(
					_("POS Invoice isn't created by user {}").format(frappe.bold(self.owner))
				)

			if invalid_row.get("msg"):
				invalid_rows.append(invalid_row)

		if not invalid_rows:
			return

		error_list = []
		for row in invalid_rows:
			for msg in row.get("msg"):
				error_list.append(_("Row #{}: {}").format(row.get("idx"), msg))

		frappe.throw(error_list, title=_("Invalid POS Invoices"), as_list=True)

	def validate_duplicate_sales_invoices(self):
		sales_invoice_occurrences = {}
		for idx, inv in enumerate(self.sales_invoices, 1):
			sales_invoice_occurrences.setdefault(inv.sales_invoice, []).append(idx)

		error_list = []
		for key, value in sales_invoice_occurrences.items():
			if len(value) > 1:
				error_list.append(
					_("{0} is added multiple times on rows: {1}").format(frappe.bold(key), frappe.bold(value))
				)

		if error_list:
			frappe.throw(error_list, title=_("Duplicate Sales Invoices found"), as_list=True)

	def validate_sales_invoices(self):
		invalid_rows = []
		for d in self.sales_invoices:
			invalid_row = {"idx": d.idx}
			sales_invoice = frappe.db.get_values(
				"Sales Invoice",
				d.sales_invoice,
				[
					"pos_profile",
					"docstatus",
					"is_pos",
					"owner",
					"is_created_using_pos",
					"is_consolidated",
					"pos_closing_entry",
				],
				as_dict=1,
			)[0]
			if sales_invoice.pos_closing_entry:
				invalid_row.setdefault("msg", []).append(_("Sales Invoice is already consolidated"))
				invalid_rows.append(invalid_row)
				continue
			if sales_invoice.is_pos == 0:
				invalid_row.setdefault("msg", []).append(_("Sales Invoice does not have Payments"))
			if sales_invoice.is_created_using_pos == 0:
				invalid_row.setdefault("msg", []).append(_("Sales Invoice is not created using POS"))
			if sales_invoice.pos_profile != self.pos_profile:
				invalid_row.setdefault("msg", []).append(
					_("POS Profile doesn't match {}").format(frappe.bold(self.pos_profile))
				)
			if sales_invoice.docstatus != 1:
				invalid_row.setdefault("msg", []).append(_("Sales Invoice is not submitted"))
			if sales_invoice.owner != self.user:
				invalid_row.setdefault("msg", []).append(
					_("Sales Invoice isn't created by user {}").format(frappe.bold(self.owner))
				)

			if invalid_row.get("msg"):
				invalid_rows.append(invalid_row)

		if not invalid_rows:
			return

		error_list = []
		for row in invalid_rows:
			for msg in row.get("msg"):
				error_list.append(_("Row #{}: {}").format(row.get("idx"), msg))

		frappe.throw(error_list, title=_("Invalid Sales Invoices"), as_list=True)

	@frappe.whitelist()
	def get_payment_reconciliation_details(self):
		currency = frappe.get_cached_value("Company", self.company, "default_currency")
		return frappe.render_template(
			"erpnext/accounts/doctype/pos_closing_entry/closing_voucher_details.html",
			{"data": self, "currency": currency},
		)

	def on_submit(self):
		consolidate_pos_invoices(closing_entry=self)
		frappe.publish_realtime(
			f"poe_{self.pos_opening_entry}_closed",
			self,
			docname=f"POS Opening Entry/{self.pos_opening_entry}",
		)

		self.update_sales_invoices_closing_entry()

	def on_cancel(self):
		unconsolidate_pos_invoices(closing_entry=self)

		self.update_sales_invoices_closing_entry(cancel=True)

	@frappe.whitelist()
	def retry(self):
		consolidate_pos_invoices(closing_entry=self)

	def update_opening_entry(self, for_cancel=False):
		opening_entry = frappe.get_doc("POS Opening Entry", self.pos_opening_entry)
		opening_entry.pos_closing_entry = self.name if not for_cancel else None
		opening_entry.set_status()
		opening_entry.save()

	def update_sales_invoices_closing_entry(self, cancel=False):
		for d in self.sales_invoices:
			frappe.db.set_value(
				"Sales Invoice", d.sales_invoice, "pos_closing_entry", self.name if not cancel else None
			)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
	cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"], as_list=1)
	return [c for c in cashiers_list]


@frappe.whitelist()
def get_invoices(start, end, pos_profile, user):
	invoice_doctype = frappe.db.get_single_value("Accounts Settings", "invoice_doctype_in_pos")

	SalesInvoice = DocType("Sales Invoice")
	sales_inv_query = (
		frappe.qb.from_(SalesInvoice)
		.select(
			SalesInvoice.name,
			fn.Timestamp(SalesInvoice.posting_date, SalesInvoice.posting_time).as_("timestamp"),
			ConstantColumn("Sales Invoice").as_("doctype"),
		)
		.where(
			(SalesInvoice.owner == user)
			& (SalesInvoice.docstatus == 1)
			& (SalesInvoice.is_pos == 1)
			& (SalesInvoice.pos_profile == pos_profile)
			& (SalesInvoice.is_created_using_pos == 1)
			& fn.IfNull(SalesInvoice.pos_closing_entry, "").eq("")
		)
	)

	query = sales_inv_query

	if invoice_doctype == "POS Invoice":
		POSInvoice = DocType("POS Invoice")
		pos_inv_query = (
			frappe.qb.from_(POSInvoice)
			.select(
				POSInvoice.name,
				fn.Timestamp(POSInvoice.posting_date, POSInvoice.posting_time).as_("timestamp"),
				ConstantColumn("POS Invoice").as_("doctype"),
			)
			.where(
				(POSInvoice.owner == user)
				& (POSInvoice.docstatus == 1)
				& (POSInvoice.pos_profile == pos_profile)
				& fn.IfNull(POSInvoice.consolidated_invoice, "").eq("")
			)
		)
		query = query + pos_inv_query

	sql_query, params = query.walk()
	data = frappe.db.sql(sql_query, params, as_dict=1)

	data = [d for d in data if get_datetime(start) <= get_datetime(d.timestamp) <= get_datetime(end)]
	# need to get taxes and payments so can't avoid get_doc
	data = [frappe.get_doc(d.doctype, d.name).as_dict() for d in data]
	return data


def make_closing_entry_from_opening(opening_entry):
	closing_entry = frappe.new_doc("POS Closing Entry")
	closing_entry.pos_opening_entry = opening_entry.name
	closing_entry.period_start_date = opening_entry.period_start_date
	closing_entry.period_end_date = frappe.utils.get_datetime()
	closing_entry.pos_profile = opening_entry.pos_profile
	closing_entry.user = opening_entry.user
	closing_entry.company = opening_entry.company
	closing_entry.grand_total = 0
	closing_entry.net_total = 0
	closing_entry.total_quantity = 0

	invoices = get_invoices(
		closing_entry.period_start_date,
		closing_entry.period_end_date,
		closing_entry.pos_profile,
		closing_entry.user,
	)

	pos_invoices = []
	sales_invoices = []
	taxes = []
	payments = []
	for detail in opening_entry.balance_details:
		payments.append(
			frappe._dict(
				{
					"mode_of_payment": detail.mode_of_payment,
					"opening_amount": detail.opening_amount,
					"expected_amount": detail.opening_amount,
				}
			)
		)

	for d in invoices:
		invoice = "pos_invoice" if d.doctype == "POS Invoice" else "sales_invoice"
		data = frappe._dict(
			{
				invoice: d.name,
				"posting_date": d.posting_date,
				"grand_total": d.grand_total,
				"customer": d.customer,
			}
		)
		if d.doctype == "POS Invoice":
			pos_invoices.append(data)
		else:
			sales_invoices.append(data)

	for d in invoices:
		closing_entry.grand_total += flt(d.grand_total)
		closing_entry.net_total += flt(d.net_total)
		closing_entry.total_quantity += flt(d.total_qty)

		for t in d.taxes:
			existing_tax = [tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate]
			if existing_tax:
				existing_tax[0].amount += flt(t.tax_amount)
			else:
				taxes.append(
					frappe._dict({"account_head": t.account_head, "rate": t.rate, "amount": t.tax_amount})
				)

		for p in d.payments:
			existing_pay = [pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]
			if existing_pay:
				existing_pay[0].expected_amount += flt(p.amount)
			else:
				payments.append(
					frappe._dict(
						{
							"mode_of_payment": p.mode_of_payment,
							"opening_amount": 0,
							"expected_amount": p.amount,
						}
					)
				)

	closing_entry.set("pos_invoices", pos_invoices)
	closing_entry.set("sales_invoices", sales_invoices)
	closing_entry.set("payment_reconciliation", payments)
	closing_entry.set("taxes", taxes)

	return closing_entry
