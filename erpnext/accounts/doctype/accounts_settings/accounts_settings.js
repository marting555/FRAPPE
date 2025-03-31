// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Settings", {
	refresh: function (frm) {},
	enable_immutable_ledger: function (frm) {
		if (!frm.doc.enable_immutable_ledger) {
			return;
		}

		let msg = __("Enabling this will change the way how cancelled transactions are handled.");
		msg += " ";
		msg += __("Please enable only if the understand the effects of enabling this.");
		msg += "<br>";
		msg += __("Do you still want to enable immutable ledger?");

		frappe.confirm(
			msg,
			() => {},
			() => {
				frm.set_value("enable_immutable_ledger", 0);
			}
		);
	},
	validate: async function (frm) {
		const use_sales_invoice_in_pos = await frappe.db.get_single_value(
			"Accounts Settings",
			"use_sales_invoice_in_pos"
		);
		const pos_opening_entry_count = await frappe.db.count("POS Opening Entry", {
			filters: { docstatus: 1, status: "Open" },
		});

		if (frm.doc.use_sales_invoice_in_pos != use_sales_invoice_in_pos && pos_opening_entry_count > 0) {
			frappe.throw(
				__("{0} can be enabled/disabled only if all the POS Profiles are closed.", [
					__("Use Sales Invoice").bold(),
				])
			);
		}
	},
});
