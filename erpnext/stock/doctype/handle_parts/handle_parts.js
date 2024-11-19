// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Handle Parts", {
    upload: async function (frm) {
        try {
            if (!frm.doc.excel) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __('Please select an Excel file to upload.'),
                    indicator: 'red',
                });
                return;
            }
            const data = await frappe.db.get_doc('Handle Parts Config');
            if (!data || !data.date_time_url_created) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __('The URL creation time is missing or invalid.'),
                    indicator: 'red',
                });
                return;
            }

            const urlCreatedTime = frappe.datetime.str_to_obj(data.date_time_url_created);
            const nowTime = frappe.datetime.now_datetime();

            const timeDifferenceInSeconds = frappe.datetime.get_diff(nowTime, urlCreatedTime, 'seconds');
            const timeDifferenceInHours = timeDifferenceInSeconds / 3600;

            if (timeDifferenceInHours > 1) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __('The URL creation time is more than 1 hour old. Please generate a new URL.'),
                    indicator: 'red',
                });
                return;
            }

            if (!data.submit_file_url || !data.binary_data) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __('File upload details are missing or incomplete.'),
                    indicator: 'red',
                });
                return;
            }

            const response = await fetch(data.submit_file_url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                },
                body: Uint8Array.from(atob(data.binary_data), c => c.charCodeAt(0))
            });

            if (response.ok) {
                frappe.msgprint({
                    title: __('Success'),
                    message: __('File uploaded successfully. The process will take 10 minutes or less to complete. You will be notified when the process is complete.'),
                    indicator: 'green',
                });
                frm.set_value('excel', "");
                frm.refresh_field('excel');
                frappe.db.set_value('Handle Parts Config', 'Handle Parts Config', 'binary_data', '');
            } else {
                const errorText = await response.text();
                console.error('Upload failed:', errorText);
                frappe.msgprint({
                    title: __('Error'),
                    message: __('File upload failed: ') + errorText,
                    indicator: 'red',
                });
            }
        } catch (error) {
            console.error("Error in upload function:", error);
            frappe.msgprint({
                title: __('Error'),
                message: __('An error occurred during the upload process.'),
                indicator: 'red',
            });
        }
    },
    product_bundle_errors: async function (frm) {
        const data = await frappe.db.get_doc('Handle Parts Config');
        if (!data || !data.product_bundle_errors_url) {
            frappe.msgprint({
                title: __('Validation Error'),
                message: __('The URL for product bundle errors is missing or invalid.'),
                indicator: 'red',
            });
            return;
        }

        const response = await fetch(data.product_bundle_errors_url);
        if (response.ok) {
            const errors = await response.json();
            const createdAt = errors.length > 0 ? errors[0].created_at : '';
            console.log("createdAt", createdAt, "-- ", errors[0].created_at);
            const title = __('Product Bundle Errors (Red items are not found, and the bundle was not created)');

            let dialog = new frappe.ui.Dialog({
                title: title,
                fields: [
                    {
                        label: __('Errors'),
                        fieldtype: 'HTML',
                        fieldname: 'errors_list',
                        options: generate_error_table(errors, createdAt)
                    }
                ]
            });
            dialog.$wrapper.modal({
                backdrop: "static",
                keyboard: false,
                size: "1024px"
            });

            dialog.show();
            dialog.$wrapper.find('.modal-dialog').css("width", "90%").css("max-width", "90%");
        }

    },

});

function generate_error_table(errors, createdAt) {
    let table_html = `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>TVS PN</th>
                    <th>Item Codes (tvs pn)</th>
                    <th>Quantities</th>
                </tr>
            </thead>
            <tbody>
    `;

    if (createdAt) {
        const formattedDate = new Date(createdAt).toLocaleString();
        table_html += `
            <tr style="background-color: #f8d7da; color: #721c24;">
                <td colspan="3"><strong>Information Created At: ${formattedDate}</strong></td>
            </tr>
        `;
    }

    errors.forEach(error => {
        let row_html = `
            <tr>
                <td>${error.new_item_code}</td>
                <td>
        `;

        let qty_html = '';
        error.items.forEach(item => {
            const row_style = item.found ? "" : "background-color: #f8d7da; color: #721c24;";

            row_html += `<span style="${row_style}">${item.item_code}</span><br>`;
            qty_html += `<span style="${row_style}">${item.qty}</span><br>`;
        });

        row_html += `</td><td>${qty_html}</td></tr>`;
        table_html += row_html;
    });

    table_html += `
            </tbody>
        </table>
    `;
    return table_html;
}



