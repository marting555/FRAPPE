// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Resumen diario"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("Desde"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("Hasta"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"serie",
			"label": __("Serie"),
			"fieldtype": "Link",
			"options": "Daily summary series",
			"reqd": 1
		},
		{
			"fieldname":"company",
			"label": __("Compañia"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1
		}
	]
};
