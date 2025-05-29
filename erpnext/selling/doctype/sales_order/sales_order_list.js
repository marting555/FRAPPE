frappe.listview_settings["Sales Order"] = {
	hide_name_column: true,
	onload: function (listview) {
		var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";

		listview.page.add_menu_item(__("Close"), function () {
			listview.call_for_selected_items(method, { status: "Closed" });
		});

		listview.page.add_menu_item(__("Re-open"), function () {
			listview.call_for_selected_items(method, { status: "Submitted" });
		});

		if (frappe.model.can_create("Sales Invoice")) {
			listview.page.add_action_item(__("Sales Invoice"), () => {
				erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Sales Invoice");
			});
		}

		if (frappe.model.can_create("Delivery Note")) {
			listview.page.add_action_item(__("Delivery Note"), () => {
				erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Delivery Note");
			});
		}

		if (frappe.model.can_create("Payment Entry")) {
			listview.page.add_action_item(__("Advance Payment"), () => {
				erpnext.bulk_transaction_processing.create(listview, "Sales Order", "Payment Entry");
			});
		}
	},

	refresh: function (listview) {
		// Hide the 3rd column (docstatus) in the list view using jQuery
		$("<style>.result .list-header-subject > div:nth-child(3), .result .list-row-container .list-row-col:nth-child(3) { display: none; }</style>").appendTo("head");
		$('[data-filter]').css("background-color", "whitesmoke");
		$('[data-filter="cancelled_status,=,Uncancelled"]').css("color", "green");
		$('[data-filter="cancelled_status,=,Cancelled"]').css("color", "tomato");

		$('[data-filter="fulfillment_status,=,Fulfilled"]').css("color", "green");
		$('[data-filter="fulfillment_status,=,Not Fulfilled"]').css("color", "tomato");
	}
};
