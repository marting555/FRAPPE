// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.query_reports["WBS Summary Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		
		{
			fieldname: "wbs_name",
			label: __("WBS"),
			fieldtype: "Data",
		},
	],
	"tree": true,
	"name_field": "parent",
	"parent_field": "karigar",
	"initial_depth": 0,
};

