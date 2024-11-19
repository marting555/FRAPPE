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
    }
});


