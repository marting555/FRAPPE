# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import gzip
import json

import frappe
from frappe import _
from frappe.core.doctype.prepared_report.prepared_report import create_json_gz_file
from frappe.desk.form.load import get_attachments
from frappe.model.document import Document
from frappe.utils import add_days, get_link_to_form, nowtime, parse_json
from frappe.utils.background_jobs import enqueue

from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions


class StockClosingEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link | None
		from_date: DF.Date | None
		naming_series: DF.Literal["CBAL-.#####"]
		status: DF.Literal["Draft", "Queued", "In Progress", "Completed", "Failed", "Canceled"]
		to_date: DF.Date | None
	# end: auto-generated types

	def before_save(self):
		self.set_status()

	def set_status(self, save=False):
		self.status = "Queued"
		if self.docstatus == 2:
			self.status = "Canceled"

		if self.docstatus == 0:
			self.status = "Draft"

		if save:
			self.db_set("status", self.status)

	def validate(self):
		self.validate_duplicate()

	def validate_duplicate(self):
		table = frappe.qb.DocType("Stock Closing Entry")

		query = (
			frappe.qb.from_(table)
			.select(table.name)
			.where(
				(table.docstatus == 1)
				& (table.company == self.company)
				& (
					(table.from_date.between(self.from_date, self.to_date))
					| (table.to_date.between(self.from_date, self.to_date))
					| ((table.from_date >= self.from_date) & (table.to_date >= self.to_date))
				)
			)
		)

		for fieldname in ["warehouse", "item_code", "item_group", "warehouse_type"]:
			if self.get(fieldname):
				query = query.where(table[fieldname] == self.get(fieldname))

		query = query.run(as_dict=True)

		if query and query[0].name:
			name = get_link_to_form("Stock Closing Entry", query[0].name)
			frappe.throw(
				_("Stock Closing Entry {0} already exists for the selected date range").format(name),
				title=_("Duplicate Stock Closing Entry"),
			)

	def on_submit(self):
		self.set_status(save=True)
		self.enqueue_job()

	def on_cancel(self):
		self.set_status(save=True)
		self.remove_stock_closing()

	def remove_stock_closing(self):
		table = frappe.qb.DocType("Stock Closing Balance")
		frappe.qb.from_(table).delete().where(table.stock_closing_entry == self.name).run()

	@frappe.whitelist()
	def enqueue_job(self):
		self.db_set("status", "In Progress")
		enqueue(prepare_closing_stock_balance, name=self.name, queue="long", timeout=1500)
		frappe.msgprint(
			_(
				"Stock Closing Entry {0} has been queued for processing, system will take sometime to complete it."
			).format(self.name)
		)

	@frappe.whitelist()
	def regenerate_closing_balance(self):
		self.remove_stock_closing()
		# self.enqueue_job()
		self.create_stock_closing_balance_entries()

	def create_stock_closing_balance_entries(self):
		from erpnext.stock.utils import get_combine_datetime

		stk_cl_obj = StockClosing(self.company, self.from_date, self.to_date)

		entries = stk_cl_obj.get_stock_closing_entries()

		for row in entries:
			data = entries[row]

			if data.actual_qty == 0.0 and data.stock_value_difference == 0.0:
				continue

			new_doc = frappe.new_doc("Stock Closing Balance")
			new_doc.update(data)
			new_doc.posting_date = self.to_date
			new_doc.posting_time = nowtime()
			new_doc.posting_datetime = get_combine_datetime(self.to_date, new_doc.posting_time)
			new_doc.stock_closing_entry = self.name
			new_doc.company = self.company
			new_doc.save()

	def get_prepared_data(self):
		if attachments := get_attachments(self.doctype, self.name):
			attachment = attachments[0]
			attached_file = frappe.get_doc("File", attachment.name)

			data = gzip.decompress(attached_file.get_content())
			if data := json.loads(data.decode("utf-8")):
				data = data

			return parse_json(data)

		return frappe._dict({})


def prepare_closing_stock_balance(name):
	doc = frappe.get_doc("Stock Closing Entry", name)

	doc.db_set("status", "In Progress")

	try:
		doc.create_stock_closing_balance_entries()
		doc.db_set("status", "Completed")
	except Exception:
		doc.db_set("status", "Failed")
		doc.log_error(title="Stock Closing Entry Failed")


class StockClosing:
	def __init__(self, company, from_date, to_date, **kwargs):
		self.company = company
		self.from_date = from_date
		self.to_date = to_date
		self.kwargs = kwargs
		self.inv_dimensions = get_inventory_dimensions()
		self.last_closing_balance = self.get_last_stock_closing_entry()

	def get_stock_closing_entries(self):
		sl_entries = self.get_sle_entries()

		closing_stock = frappe._dict()
		for row in sl_entries:
			keys = self.get_keys(row)
			for data in keys:
				for fields, values in data.items():
					key = values

					if key in closing_stock:
						closing_stock[key].actual_qty += row.sabb_qty or row.actual_qty
						closing_stock[key].stock_value_difference += (
							row.sabb_stock_value_difference or row.stock_value_difference
						)

						if not row.actual_qty and row.qty_after_transaction:
							closing_stock[key].actual_qty = row.qty_after_transaction
					else:
						item_details = frappe.get_cached_value(
							"Item", row.item_code, ["item_group", "item_name", "stock_uom"], as_dict=1
						)

						inventory_dimension_key = ""
						if fields not in [("item_code", "warehouse"), ("item_code", "warehouse", "batch_no")]:
							inventory_dimension_key = json.dumps(fields)

						closing_stock[key] = frappe._dict(
							{
								"item_code": row.item_code,
								"warehouse": row.warehouse,
								"actual_qty": row.sabb_qty or row.actual_qty or row.qty_after_transaction,
								"stock_value_difference": (
									row.sabb_stock_value_difference or row.stock_value_difference
								),
								"item_group": item_details.item_group,
								"item_name": item_details.item_name,
								"stock_uom": item_details.stock_uom,
								"inventory_dimension_key": inventory_dimension_key,
								"batch_no": row.batch_no or row.sabb_batch_no,
							}
						)

						# To update dimensions
						for field in fields:
							if row.get(field):
								closing_stock[key][field] = row.get(field)

		return closing_stock

	def get_sle_entries(self):
		sl_entries = []
		if self.last_closing_balance:
			self.from_date = add_days(self.last_closing_balance.to_date, 1)
			sl_entries += self.get_entries(
				"Stock Closing Voucher",
				fields=[
					"item_code",
					"warehouse",
					"posting_date",
					"posting_time",
					"posting_datetime",
					"batch_no",
					"actual_qty",
					"valuation_rate",
					"stock_value",
					"stock_value_difference",
				],
				filters={
					"company": self.company,
					"closing_stock_balance": self.last_closing_balance.name,
				},
			)

		if not self.last_closing_balance:
			self.from_date = "1900-01-01"

		sl_entries += self.get_entries(
			"Stock Ledger Entry",
			fields=[
				"item_code",
				"warehouse",
				"posting_date",
				"posting_time",
				"posting_datetime",
				"batch_no",
				"actual_qty",
				"valuation_rate",
				"stock_value",
				"stock_value_difference",
				"qty_after_transaction",
				"stock_uom",
			],
			filters={
				"company": self.company,
				"posting_date": [self.from_date, self.to_date],
				"is_cancelled": 0,
				"docstatus": 1,
			},
		)

		return sl_entries

	def get_entries(self, doctype, fields, filters, **kwargs):
		"""Get Stock Ledger Entries for the given filters."""

		for dimension in self.inv_dimensions:
			if dimension.fieldname not in fields:
				fields.append(dimension.fieldname)

		table = frappe.qb.DocType(doctype)
		query = frappe.qb.from_(table).select(*fields).orderby(table.posting_datetime)

		if filters:
			for field, value in filters.items():
				if field == "posting_date":
					query = query.where(table[field].between(value[0], value[1]))
				elif isinstance(value, list) or isinstance(value, tuple):
					query = query.where(table[field].isin(value))
				else:
					query = query.where(table[field] == value)

		for key, value in kwargs.items():
			if value:
				if isinstance(value, list) or isinstance(value, tuple):
					query = query.where(table[key].isin(value))
				else:
					query = query.where(table[key] == value)

		if doctype == "Stock Ledger Entry":
			sabb_table = frappe.qb.DocType("Serial and Batch Entry")
			query = query.left_join(sabb_table).on(
				(sabb_table.parent == table.serial_and_batch_bundle) & (table.has_batch_no == 1)
			)
			query = query.select(sabb_table.batch_no.as_("sabb_batch_no"))
			query = query.select(sabb_table.qty.as_("sabb_qty"))
			query = query.select(sabb_table.stock_value_difference.as_("sabb_stock_value_difference"))

		return query.run(as_dict=True)

	def get_last_stock_closing_entry(self):
		entries = frappe.get_all(
			"Stock Closing Entry",
			fields=["name", "to_date"],
			filters={"company": self.company, "to_date": ["<", self.from_date], "docstatus": 1},
			order_by="to_date desc, creation desc",
			limit=1,
		)

		return entries[0] if entries else frappe._dict()

	def get_keys(self, row):
		keys = []

		keys.append({("item_code", "warehouse"): (row.item_code, row.warehouse)})

		if row.batch_no:
			keys.append(
				{("item_code", "warehouse", "batch_no"): (row.item_code, row.warehouse, row.batch_no)}
			)

		if row.sabb_batch_no:
			keys.append(
				{("item_code", "warehouse", "batch_no"): (row.item_code, row.warehouse, row.sabb_batch_no)}
			)

		dimensions_has_value = []
		dimension_values = []
		for dimension in self.inv_dimensions:
			if row.get(dimension.fieldname):
				keys.append(
					{
						("item_code", "warehouse", dimension.fieldname): (
							row.item_code,
							row.warehouse,
							row.get(dimension.fieldname),
						)
					}
				)

				dimensions_has_value.append(dimension.fieldname)
				dimension_values.append(row.get(dimension.fieldname))

		if dimensions_has_value and len(dimensions_has_value) > 1:
			keys.append(
				{
					("item_code", "warehouse", *dimensions_has_value): (
						row.item_code,
						row.warehouse,
						*dimension_values,
					)
				}
			)

		return keys

	def get_stock_closing_balance(self, kwargs):
		if not self.last_closing_balance:
			return []

		stock_closing_entry = self.last_closing_balance.name
		if isinstance(kwargs, dict):
			kwargs = frappe._dict(kwargs)

		table = frappe.qb.DocType("Stock Closing Balance")
		query = frappe.qb.from_(table).select("*").where(table.stock_closing_entry == stock_closing_entry)

		for key, value in kwargs.items():
			if isinstance(value, list) or isinstance(value, tuple):
				query = query.where(table[key].isin(value))
			else:
				query = query.where(table[key] == value)

		return query.run(as_dict=True)
