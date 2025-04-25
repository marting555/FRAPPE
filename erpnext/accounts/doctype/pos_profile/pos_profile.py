# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import get_link_to_form, now

from frappe.permissions import get_doctypes_with_read
from frappe.model.naming import parse_naming_series
from frappe.model.naming import NamingSeries


class POSProfile(Document):
	def validate(self):
		self.validate_default_profile()
		self.validate_all_link_fields()
		self.validate_duplicate_groups()
		self.validate_payment_methods()

	def validate_default_profile(self):
		for row in self.applicable_for_users:
			res = frappe.db.sql(
				"""select pf.name
				from
					`tabPOS Profile User` pfu, `tabPOS Profile` pf
				where
					pf.name = pfu.parent and pfu.user = %s and pf.name != %s and pf.company = %s
					and pfu.default=1 and pf.disabled = 0""",
				(row.user, self.name, self.company),
			)

			if row.default and res:
				msgprint(
					_("Already set default in pos profile {0} for user {1}, kindly disabled default").format(
						res[0][0], row.user
					),
					raise_exception=1,
				)
			elif not row.default and not res:
				msgprint(
					_(
						"User {0} doesn't have any default POS Profile. Check Default at Row {1} for this User."
					).format(row.user, row.idx)
				)

	def validate_all_link_fields(self):
		accounts = {
			"Account": [self.income_account, self.expense_account],
			"Cost Center": [self.cost_center],
			"Warehouse": [self.warehouse],
		}

		for link_dt, dn_list in accounts.items():
			for link_dn in dn_list:
				if link_dn and not frappe.db.exists(
					{"doctype": link_dt, "company": self.company, "name": link_dn}
				):
					frappe.throw(_("{0} does not belong to Company {1}").format(link_dn, self.company))

	def validate_duplicate_groups(self):
		item_groups = [d.item_group for d in self.item_groups]
		customer_groups = [d.customer_group for d in self.customer_groups]

		if len(item_groups) != len(set(item_groups)):
			frappe.throw(
				_("Duplicate item group found in the item group table"), title=_("Duplicate Item Group")
			)

		if len(customer_groups) != len(set(customer_groups)):
			frappe.throw(
				_("Duplicate customer group found in the cutomer group table"),
				title=_("Duplicate Customer Group"),
			)

	def validate_payment_methods(self):
		if not self.payments:
			frappe.throw(_("Payment methods are mandatory. Please add at least one payment method."))

		default_mode = [d.default for d in self.payments if d.default]
		if not default_mode:
			frappe.throw(_("Please select a default mode of payment"))

		if len(default_mode) > 1:
			frappe.throw(_("You can only select one mode of payment as default"))

		invalid_modes = []
		for d in self.payments:
			account = frappe.db.get_value(
				"Mode of Payment Account",
				{"parent": d.mode_of_payment, "company": self.company},
				"default_account",
			)

			if not account:
				invalid_modes.append(get_link_to_form("Mode of Payment", d.mode_of_payment))

		if invalid_modes:
			if invalid_modes == 1:
				msg = _("Please set default Cash or Bank account in Mode of Payment {}")
			else:
				msg = _("Please set default Cash or Bank account in Mode of Payments {}")
			frappe.throw(msg.format(", ".join(invalid_modes)), title=_("Missing Account"))

	def on_update(self):
		self.set_defaults()

	def on_trash(self):
		self.set_defaults(include_current_pos=False)

	def set_defaults(self, include_current_pos=True):
		frappe.defaults.clear_default("is_pos")

		if not include_current_pos:
			condition = " where pfu.name != '%s' and pfu.default = 1 " % self.name.replace("'", "'")
		else:
			condition = " where pfu.default = 1 "

		pos_view_users = frappe.db.sql_list(
			f"""select pfu.user
			from `tabPOS Profile User` as pfu {condition}"""
		)

		for user in pos_view_users:
			if user:
				frappe.defaults.set_user_default("is_pos", 1, user)
			else:
				frappe.defaults.set_global_default("is_pos", 1)

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
	
def get_item_groups(pos_profile):
	item_groups = []
	pos_profile = frappe.get_cached_doc("POS Profile", pos_profile)

	if pos_profile.get("item_groups"):
		# Get items based on the item groups defined in the POS profile
		for data in pos_profile.get("item_groups"):
			item_groups.extend(
				["%s" % frappe.db.escape(d.name) for d in get_child_nodes("Item Group", data.item_group)]
			)

	return list(set(item_groups))


def get_child_nodes(group_type, root):
	lft, rgt = frappe.db.get_value(group_type, root, ["lft", "rgt"])
	return frappe.db.sql(
		f""" Select name, lft, rgt from `tab{group_type}` where
			lft >= {lft} and rgt <= {rgt} order by lft""",
		as_dict=1,
	)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def pos_profile_query(doctype, txt, searchfield, start, page_len, filters):
	user = frappe.session["user"]
	company = filters.get("company") or frappe.defaults.get_user_default("company")

	args = {
		"user": user,
		"start": start,
		"company": company,
		"page_len": page_len,
		"txt": "%%%s%%" % txt,
	}

	pos_profile = frappe.db.sql(
		"""select pf.name
		from
			`tabPOS Profile` pf, `tabPOS Profile User` pfu
		where
			pfu.parent = pf.name and pfu.user = %(user)s and pf.company = %(company)s
			and (pf.name like %(txt)s)
			and pf.disabled = 0 limit %(page_len)s offset %(start)s""",
		args,
	)

	if not pos_profile:
		del args["user"]

		pos_profile = frappe.db.sql(
			"""select pf.name
			from
				`tabPOS Profile` pf left join `tabPOS Profile User` pfu
			on
				pf.name = pfu.parent
			where
				ifnull(pfu.user, '') = ''
				and pf.company = %(company)s
				and pf.name like %(txt)s
				and pf.disabled = 0""",
			args,
		)

	return pos_profile


@frappe.whitelist()
def set_default_profile(pos_profile, company):
	modified = now()
	user = frappe.session.user

	if pos_profile and company:
		frappe.db.sql(
			""" update `tabPOS Profile User` pfu, `tabPOS Profile` pf
			set
				pfu.default = 0, pf.modified = %s, pf.modified_by = %s
			where
				pfu.user = %s and pf.name = pfu.parent and pf.company = %s
				and pfu.default = 1""",
			(modified, user, user, company),
			auto_commit=1,
		)

		frappe.db.sql(
			""" update `tabPOS Profile User` pfu, `tabPOS Profile` pf
			set
				pfu.default = 1, pf.modified = %s, pf.modified_by = %s
			where
				pfu.user = %s and pf.name = pfu.parent and pf.company = %s and pf.name = %s
			""",
			(modified, user, user, company, pos_profile),
			auto_commit=1,
		)
