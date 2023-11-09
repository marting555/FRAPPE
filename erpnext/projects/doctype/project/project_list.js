frappe.listview_settings['Project'] = {
	add_fields: ["status", "priority", "is_active", "percent_complete", "expected_end_date", "project_name"],
	filters:[["status","=", "Open"]],
	get_indicator: function(doc) {
		if(doc.status=="Open" && doc.percent_complete) {
			return [__("{0}%", [cint(doc.percent_complete)]), "orange", "percent_complete,>,0|status,=,Open"];
		} else {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	}
};
const el = document.createElement('erp-calendar')
el.setAttribute('url', location.origin);
const add = () => {
	if(!document.querySelector('erp-calendar')){
		frappe.require('erp-calendar.bundle.js').then(() => {
			document.querySelector('body').appendChild(el)
		})
	}
}

navigation.addEventListener("navigatesuccess", () => {
	if (/\/project\.*/.test(location.pathname)){
		add()
	} else {
		document.querySelector('erp-calendar')?.remove()
	}
})

