// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["TAX Declaration"] = {
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
		
		// Apply custom formatting for amounts
		if (column.fieldname == "amount") {
			value = "<span style='font-weight: bold;'>" + value + "</span>";
		}
		
		// Highlight the net payable/refundable amount
		if (data && data.rubric === "5c") {
			value = "<span style='font-weight: bold; color: " + 
				(data.amount >= 0 ? "red" : "green") + ";'>" + value + "</span>";
		}
		
		return value;
	},
	
	onload: function(report) {
		// Apply styles to make the table occupy 100% of the width
		setTimeout(function() {
			// Select the data table and apply styles
			$('.datatable').css({
				'width': '100%',
				'max-width': '100%'
			});
			
			// Adjust the table container
			$('.dt-scrollable').css({
				'width': '100%',
				'max-width': '100%'
			});
			
			// Adjust the main report container
			$('.report-wrapper').css({
				'width': '100%',
				'max-width': '100%'
			});
			
			// Ensure the header table also has full width
			$('.dt-header').css({
				'width': '100%',
				'max-width': '100%'
			});
			
			// Force recalculation of column widths
			if (report.datatable) {
				report.datatable.refresh();
			}
		}, 500);
		
		// Configure table adjustment when window size changes
		$(window).on('resize', function() {
			if (report.datatable) {
				report.datatable.refresh();
				
				// Readjust widths
				$('.datatable, .dt-scrollable, .report-wrapper, .dt-header').css({
					'width': '100%',
					'max-width': '100%'
				});
			}
		});
		
		// Add PDF download button
		report.page.add_inner_button(__('Download PDF'), function() {
			// Get current report filters
			const filters = report.get_values();
			
			// Create a title for the PDF
			const title = __("Tax Declaration") + ": " + 
				frappe.datetime.str_to_user(filters.from_date) + " - " + 
				frappe.datetime.str_to_user(filters.to_date);
			
			// Use report data directly
			let rows_data = [];
			
			// Check if data is available
			if (report.data && report.data.length) {
				// Filter to include only data rows (not totals)
				rows_data = report.data.filter(row => 
					!row.is_total_row && row.rubric !== "Total"
				);
				
				// Calculate totals
				let total_amount = 0;
				
				rows_data.forEach(row => {
					if (row.rubric === "5c") {
						total_amount = row.amount || 0;
					}
				});
				
				// Add an empty row to create space
				let empty_row = {};
				for (let col of report.get_columns_for_print()) {
					empty_row[col.fieldname] = "";
				}
				empty_row.is_empty_row = true;
				rows_data.push(empty_row);
				
				// Add total row
				let total_data = {};
				total_data.rubric = __("Total");
				total_data.description = __("Tax Payable/Refundable");
				total_data.amount = total_amount;
				total_data.is_total_row = true;
				rows_data.push(total_data);
			}
			
			// Generate PDF using frappe.render_grid
			frappe.ui.get_print_settings(false, (print_settings) => {
				frappe.render_grid({
					title: title,
					subtitle: __("Company") + ": " + filters.company,
					print_settings: print_settings,
					columns: report.get_columns_for_print(),
					data: rows_data,
					can_use_smaller_font: 1,
					report: true,
					// Custom function to format rows
					row_formatter: function(row, data) {
						if (data.is_empty_row) {
							row.css({
								'height': '20px',
								'border-left': 'none',
								'border-right': 'none'
							});
							row.find('td').css({
								'border-left': 'none',
								'border-right': 'none'
							});
						}
						if (data.is_total_row) {
							row.css({
								'background-color': '#f9f9f9',
								'font-weight': 'bold'
							});
						}
					}
				});
			});
		});
		
		// Add Excel export button
		report.page.add_inner_button(__('Export to Excel'), function() {
			// Simplified method to export to Excel
			const filters = report.get_values();
			
			// Create arguments for export
			const args = {
				cmd: 'frappe.desk.query_report.export_query',
				report_name: 'TAX Declaration',
				file_format_type: 'Excel',
				filters: JSON.stringify(filters),
				// Ensure visible_idx is an empty array instead of null
				visible_idx: JSON.stringify([]),
				include_indentation: 0,
				// Add additional parameters for CSV if needed
				csv_delimiter: ',',
				csv_quoting: '"'
			};
			
			// Open URL to download the file
			open_url_post(frappe.request.url, args);
		});
	},
	
	// Configuration for the data table
	get_datatable_options: function(options) {
		// Modify data table options
		options.layout = 'fluid'; // Change from 'fixed' to 'fluid'
		options.cellHeight = 40; // Increase cell height for better visualization
		
		// Adjust column widths
		options.columns.forEach(col => {
			if (col.id === 'rubric') {
				col.width = 80; // Make the rubric column narrower
			} else if (col.id === 'description') {
				col.width = 300; // Make the description column wider
			} else if (col.id === 'amount') {
				col.width = 150; // Set a fixed width for the amount column
			}
		});
		
		return options;
	},
	
	// Function that runs after rendering the table
	after_datatable_render(datatable) {
		// Add custom styling to the table
		datatable.$el.find('.dt-row').css({
			'border-bottom': '1px solid #f2f2f2'
		});
		
		// Add alternating row colors
		datatable.$el.find('.dt-row:nth-child(even)').css({
			'background-color': '#f9f9f9'
		});
	}
};
