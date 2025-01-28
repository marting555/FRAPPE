// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Queue Settings", {
  validate: function (frm) {
    const cars_per_day = Number(frm.doc.cars_per_day)
    if (cars_per_day <= 0 || !Number.isInteger(cars_per_day)) {
      frappe.msgprint(__('The value for {0} must be greater than 0.', [__('Cars per Day')]));
      frappe.validated = false;
    }
  }
});
