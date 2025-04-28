// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Variant Settings", {
	setup: function(frm) {
		frm.fields_dict.fields.grid.get_field("field_name").get_query = function () {
			const existing_fields = frm.doc.fields.map((row) => row.field_name);

			return {
				query: "erpnext.stock.doctype.item_variant_settings.item_variant_settings.get_item_fields",
				params: {
					existing_fields: existing_fields,
				}
			};
		};
	},
});
