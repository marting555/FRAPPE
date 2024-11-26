frappe.query_reports["Bank Reconciliation Report"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "account",
            label: __("Bank Account"),
            fieldtype: "Link",
            options: "Account",
            reqd: 1,
            default: frappe.defaults.get_user_default("Company")
                ? locals[":Company"]?.[frappe.defaults.get_user_default("Company")]?.["default_bank_account"]
                : "",
            get_query: function () {
                let company = frappe.query_report.get_filter_value("company");
                return {
                    query: "erpnext.controllers.queries.get_account_list",
                    filters: {
                        account_type: ["in", ["Bank", "Cash"]],
                        is_group: 0,
                        disabled: 0,
                        company: company,
                    },
                };
            },
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
        }
        // {
        //     fieldname: "include_pos_transactions",
        //     label: __("Include POS Transactions"),
        //     fieldtype: "Check",
        // },
    ],
    "initial_depth": 0,
    "tree": true,

};
