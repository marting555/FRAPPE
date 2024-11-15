frappe.ui.form.on("GL Closing", {
    refresh: function(frm) {
        frm.set_query("account", "gl_closing_details", function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            }
        })
    },
    company: function(frm) {
        if (frm.doc.company) {  // Check if company field has a value
            fetch_accounts(frm);
            console.log("Company field set to:", frm.doc.company);
        } else {
            console.log("No company selected.");
        }
    },
    before_save: function(frm) {
    }
});

function fetch_accounts(frm) {
    if (!frm.doc.company) {
        console.log("No company set, skipping account fetch.");
        return;  // Stop execution if company is not set
    }

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Account",
            filters: {
                'is_group': 0,
                'company': frm.doc.company  // Use the company filter to fetch accounts for the selected company
            },
            fields: ["name"],
            limit_page_length: 0  // Remove the limit or set to 0 for no limit
        },
        callback: function(r) {
            if (r.message) {
                frm.clear_table("gl_closing_details");
                r.message.forEach(function(account) {
                    var row = frm.add_child("gl_closing_details");
                    row.account = account.name;  // Set the account name in the child table
                    row.closed = 1;  // Set default value for 'closed' field
                });
                frm.refresh_field("gl_closing_details");
            } else {
                console.log("No accounts found for the selected company.");
            }
        }
    });
}
