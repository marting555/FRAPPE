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
			
			// Usar directamente los datos del reporte - solo filas de datos, sin totales
			let rows_data = [];
			
			// Verificar si hay datos disponibles
			if (report.data && report.data.length) {
				// Filtrar para incluir solo filas de datos (no totales)
				rows_data = report.data.filter(row => 
					!row.is_total_row && row["Customer Name"] !== "Total"
				);
				
				// Calcular totales para mostrarlos por separado
				let net_amount_total = 0;
				let vat_total = 0;
				
				rows_data.forEach(row => {
					net_amount_total += flt(row["Net Amount"]) || 0;
					vat_total += flt(row["Total VAT"]) || 0;
				});
				
				// Crear un objeto de columnas personalizado para el PDF
				const columns = report.get_columns_for_print();
				
				// Generar el PDF con una estructura personalizada
				frappe.ui.get_print_settings(false, (print_settings) => {
					// Crear un contenedor para el reporte
					const $reportContainer = $('<div class="icp-declaration-pdf">');
					
					// Añadir encabezado
					$reportContainer.append(`
						<div class="pdf-header">
							<h2>${title}</h2>
							<p>${__("Company")}: ${filters.company}</p>
						</div>
					`);
					
					// Crear tabla de datos
					const $table = $('<table class="table table-bordered">').appendTo($reportContainer);
					
					// Añadir encabezados de columna
					const $thead = $('<thead>').appendTo($table);
					const $headerRow = $('<tr>').appendTo($thead);
					
					columns.forEach(col => {
						const $th = $(`<th class="${col.fieldtype === 'Currency' ? 'text-right' : ''}">${col.label}</th>`);
						$headerRow.append($th);
					});
					
					// Añadir filas de datos
					const $tbody = $('<tbody>').appendTo($table);
					
					rows_data.forEach(row => {
						const $tr = $('<tr>').appendTo($tbody);
						
						columns.forEach(col => {
							const fieldname = col.fieldname;
							let value = row[fieldname];
							
							if (col.fieldtype === 'Currency') {
								value = format_currency(value, frappe.defaults.get_default("currency"));
								$tr.append(`<td class="text-right">${value}</td>`);
							} else {
								$tr.append(`<td>${value || ''}</td>`);
							}
						});
					});
					
					// Añadir sección de totales separada y elegante
					$reportContainer.append(`
						<div class="totals-section">
							<div class="totals-row">
								<div class="totals-label">${__("Total Net Amount")}:</div>
								<div class="totals-value">${format_currency(net_amount_total, frappe.defaults.get_default("currency"))}</div>
							</div>
							<div class="totals-row">
								<div class="totals-label">${__("Total VAT")}:</div>
								<div class="totals-value">${format_currency(vat_total, frappe.defaults.get_default("currency"))}</div>
							</div>
						</div>
					`);
					
					// Añadir estilos CSS
					$reportContainer.append(`
						<style>
							.icp-declaration-pdf {
								font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
								padding: 15px;
							}
							.pdf-header {
								margin-bottom: 20px;
								text-align: center;
							}
							.pdf-header h2 {
								margin-bottom: 5px;
							}
							table {
								width: 100%;
								border-collapse: collapse;
								margin-bottom: 30px;
							}
							th, td {
								padding: 8px;
								border: 1px solid #ddd;
							}
							th {
								background-color: #f2f2f2;
								font-weight: bold;
							}
							.text-right {
								text-align: right;
							}
							.totals-section {
								margin-top: 20px;
								padding: 15px;
								background-color: #f9f9f9;
								border-top: 2px solid #ddd;
								border-bottom: 2px solid #ddd;
							}
							.totals-row {
								display: flex;
								justify-content: space-between;
								margin-bottom: 8px;
								padding: 5px 15px;
							}
							.totals-label {
								font-weight: bold;
								font-size: 14px;
							}
							.totals-value {
								font-weight: bold;
								font-size: 14px;
							}
						</style>
					`);
					
					// Generar el PDF con el contenido personalizado
					frappe.render_pdf(
						$reportContainer.prop('outerHTML'), 
						{
							title: title,
							orientation: 'landscape',
							print_settings: print_settings
						}
					);
				});
			} else {
				frappe.msgprint(__("No data to generate PDF"));
			}
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
