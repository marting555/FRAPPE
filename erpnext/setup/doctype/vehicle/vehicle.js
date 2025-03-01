// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle", {
	refresh: function (frm) {

		// Make the field editable if the value is 0
        if (frm.doc.last_odometer == 0) {
            frm.fields_dict['last_odometer'].df.read_only = 0;  // Make it editable
        } else {
            frm.fields_dict['last_odometer'].df.read_only = 1;  // Make it read-only
        }        
        frm.refresh_field('last_odometer'); // Refresh the field to apply the changes
		
	},
});
