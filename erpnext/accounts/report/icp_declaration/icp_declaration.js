// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["ICP Declaration"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		}
	],
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		// Apply custom formatting if needed
		if (column.fieldname == "Net Amount" || column.fieldname == "Total VAT") {
			value = "<span style='font-weight: bold;'>" + value + "</span>";
		}
		
		return value;
	},
	
	onload: function(report) {
		report.page.add_inner_button(__('Download PDF'), function() {
			// Obtener los filtros actuales del reporte
			const filters = report.get_values();
			
			// Crear un título para el PDF
			const title = __("ICP Declaration") + ": " + 
				frappe.datetime.str_to_user(filters.from_date) + " - " + 
				frappe.datetime.str_to_user(filters.to_date);
			
			// Usar directamente los datos del reporte
			let rows_data = [];
			
			// Verificar si hay datos disponibles
			if (report.data && report.data.length) {
				rows_data = report.data.slice();
				
				// Calcular totales
				let net_amount_total = 0;
				let vat_total = 0;
				
				rows_data.forEach(row => {
					net_amount_total += flt(row["Net Amount"]) || 0;
					vat_total += flt(row["Total VAT"]) || 0;
				});
				
				// Agregar fila de totales
				let total_data = {};
				total_data["Customer Name"] = __("Total");
				total_data["VAT Identification Number"] = "";
				total_data["Net Amount"] = net_amount_total;
				total_data["Total VAT"] = vat_total;
				total_data["Invoice Type"] = "";
				total_data.is_total_row = true;
				
				rows_data.push(total_data);
			}
			
			// Generar el PDF usando frappe.render_grid
			frappe.ui.get_print_settings(false, (print_settings) => {
				frappe.render_grid({
					title: title,
					subtitle: __("Company") + ": " + filters.company,
					print_settings: print_settings,
					columns: report.get_columns_for_print(),
					data: rows_data,
					can_use_smaller_font: 1,
					report: true
				});
			});
		});
		
		// Agregar botón para exportar a Excel
		report.page.add_inner_button(__('Export to Excel'), function() {
			const filters = report.get_values();
			
			// Crear URL para descargar Excel
			const excel_params = {
				report_name: 'ICP Declaration',
				filters: JSON.stringify(filters),
				file_format_type: 'Excel',
				is_tree: false,
				include_indentation: 0
			};
			
			const url = '/api/method/frappe.desk.query_report.export_query?' + 
				$.param(excel_params);
			
			window.open(url);
		});
	}
};
