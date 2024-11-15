// Copyright (c) 2021, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('CAI', {
    onload: function(frm) {
        frm.events.get_transactions(frm);
    },

    get_transactions: function(frm) {
        frappe.call({
            method: "get_transactions_and_prefixes",
			doc: frm.doc,
            callback: function(r) {
                frm.set_df_property("select_doc_for_series", "options", r.message.transactions);
            }
        });
    },

    get_prefix: function(frm) {
        frappe.call({
            method: "get_prefix",
			doc: frm.doc,
            callback: function(r) {
                frm.set_df_property("prefix", "options", r.message.prefix);
            }
        });
    },

    select_doc_for_series: function(frm) {
        frappe.call({
            method: "get_prefix",
			doc: frm.doc,
            callback: function(r) {
                frm.set_df_property("prefix", "options", r.message.prefix);
            }
        });
    }
});