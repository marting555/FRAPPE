// Budget Transfer
frappe.ui.form.on("Budget Transfer", {
    onload: function(frm) {
        frm.savecancel = function(btn, callback, on_error){ console.log("jiiri");return frm._cancel(btn, callback, on_error, false);}
    },
    
    from_wbs: function(frm) {
        // Check if 'from_wbs' field has a value
        if (frm.doc.from_wbs) {
            // Fetch 'wbs_name' and 'wbs_level' from the selected Work Breakdown Structure
            frappe.db.get_value("Work Breakdown Structure", frm.doc.from_wbs, ["wbs_name", "wbs_level","original_budget","overall_budget","available_budget"], (r) => {
                if (r) {
                    frm.set_value("from_wbs_name", r.wbs_name);
                    frm.set_value("from_wbs_level", r.wbs_level);
					frm.set_value("fr_og_bgt", r.original_budget);
                    frm.set_value("fr_oa_bgt", r.overall_budget);
                    frm.set_value("fr_av_bgt", r.available_budget);
                }
            });
        } else {
            // Clear the fields if 'from_wbs' is not set
            frm.set_value("from_wbs_name", null);
            frm.set_value("from_wbs_level", null);
			frm.set_value("fr_og_bgt", null);
            frm.set_value("fr_oa_bgt", null);
            frm.set_value("fr_av_bgt", null);
        }
    },
	to_wbs: function(frm) {
        // Check if 'from_wbs' field has a value
        if (frm.doc.to_wbs) {
            // Fetch 'wbs_name' and 'wbs_level' from the selected Work Breakdown Structure
            frappe.db.get_value("Work Breakdown Structure", frm.doc.to_wbs, ["wbs_name", "wbs_level","original_budget","overall_budget","available_budget"], (r) => {
                if (r) {
                    frm.set_value("to_wbs_name", r.wbs_name);
                    frm.set_value("to_wbs_level", r.wbs_level);
					frm.set_value("to_og_bgt", r.original_budget);
                    frm.set_value("to_oa_bgt", r.overall_budget);
                    frm.set_value("to_wbs_available_budget", r.available_budget);
                }
            });
        } else {
            // Clear the fields if 'from_wbs' is not set
            frm.set_value("to_wbs_name", null);
            frm.set_value("to_wbs_level", null);
			frm.set_value("to_og_bgt", null);
            frm.set_value("to_oa_bgt", null);
            frm.set_value("to_wbs_available_budget", null);
        }
    },
});