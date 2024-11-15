# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.permissions import get_doctypes_with_read
from frappe.model.naming import parse_naming_series
from frappe.model.naming import NamingSeries

class CAI(Document):
	@frappe.whitelist()
	def get_transactions(self, arg=None):
		doctypes = list(set(frappe.db.sql_list("""select parent
				from `tabDocField` df where fieldname='naming_series'""")
			+ frappe.db.sql_list("""select dt from `tabCustom Field`
				where fieldname='naming_series'""")))

		doctypes = list(set(get_doctypes_with_read()).intersection(set(doctypes)))

		return {
			"transactions": doctypes
		}

	@frappe.whitelist()
	def get_prefix(self, arg=None):
		transaction = self.select_doc_for_series
		prefixes = ""
		options = ""
		try:
			options = self.get_options(transaction)
		except frappe.DoesNotExistError:
			frappe.msgprint(_('Unable to find DocType {0}').format(d))

		if options:
			prefixes = prefixes + "\n" + options

		prefixes.replace("\n\n", "\n")
		prefixes = prefixes.split("\n")
		prefixes = "\n".join(sorted(prefixes))

		return {
			"prefix": prefixes
		}

	@frappe.whitelist()
	def get_options(self, arg=None):
		if frappe.get_meta(arg or self.select_doc_for_series).get_field("naming_series"):
			return frappe.get_meta(arg or self.select_doc_for_series).get_field("naming_series").options
	
	def before_insert(self):
		cai = frappe.get_all("CAI", ["cai"], filters = { "status": "Active", "prefix": self.prefix})
		if len(cai) > 0:
			self.status = "Pending"
		else:
			self.status = "Active"
			new_current = int(self.initial_number) - 1
			name = self.parse_naming_series(self.prefix)

			# frappe.db.set_value("Series", name, "current", new_current, update_modified=False)

	@frappe.whitelist()
	def get_transactions_and_prefixes(self):
		transactions = self._get_transactions()
		prefixes = self._get_prefixes(transactions)

		return {"transactions": transactions, "prefixes": prefixes}

	def _get_transactions(self) -> list[str]:
		readable_doctypes = set(get_doctypes_with_read())

		standard = frappe.get_all("DocField", {"fieldname": "naming_series"}, "parent", pluck="parent")
		custom = frappe.get_all("Custom Field", {"fieldname": "naming_series"}, "dt", pluck="dt")

		return sorted(readable_doctypes.intersection(standard + custom))

	def _get_prefixes(self, doctypes) -> list[str]:
		"""Get all prefixes for naming series.

		- For all templates prefix is evaluated considering today's date
		- All existing prefix in DB are shared as is.
		"""
		series_templates = set()
		for d in doctypes:
			try:
				options = frappe.get_meta(d).get_naming_series_options()
				series_templates.update(options)
			except frappe.DoesNotExistError:
				frappe.msgprint(_("Unable to find DocType {0}").format(d))
				continue

		custom_templates = frappe.get_all(
			"DocType",
			fields=["autoname"],
			filters={
				"name": ("not in", doctypes),
				"autoname": ("like", "%.#%"),
				"module": ("not in", ["Core"]),
			},
		)
		if custom_templates:
			series_templates.update([d.autoname.rsplit(".", 1)[0] for d in custom_templates])

		return self._evaluate_and_clean_templates(series_templates)
	
	def _evaluate_and_clean_templates(self, series_templates: set[str]) -> list[str]:
		evalauted_prefix = set()

		series = frappe.qb.DocType("Series")
		prefixes_from_db = frappe.qb.from_(series).select(series.name).run(pluck=True)
		evalauted_prefix.update(prefixes_from_db)

		for series_template in series_templates:
			try:
				prefix = NamingSeries(series_template).get_prefix()
				if "{" in prefix:
					# fieldnames can't be evalauted, rely on data in DB instead
					continue
				evalauted_prefix.add(prefix)
			except Exception:
				frappe.clear_last_message()
				frappe.log_error(f"Invalid naming series {series_template}")

		return sorted(evalauted_prefix)
	
	def parse_naming_series(self, prefix):
		parts = prefix.split('.')
		if parts[-1] == "#" * len(parts[-1]):
			del parts[-1]

		pre = parse_naming_series(parts)
		return pre