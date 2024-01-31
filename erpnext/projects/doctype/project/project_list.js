frappe.listview_settings['Project'] = {
	add_fields: ["status", "priority", "is_active", "percent_complete", "expected_end_date", "project_name"],
	filters:[["status","=", "Open"]],
	get_indicator: function(doc) {
		if(doc.status=="Open" && doc.percent_complete) {
			return [__("{0}%", [cint(doc.percent_complete)]), "orange", "percent_complete,>,0|status,=,Open"];
		} else {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	},
	before_render: async () => {
		const page = frappe.pages['List/Project/List'].page;
		const { auto_move_paused }  = await frappe.db.get_doc('Queue Settings')

		page.add_menu_item(__(`Queue line move is ${auto_move_paused? 'Paused' : 'Runing'} <br> "Click to change"`), () => {		
			frappe.confirm(__(`Please consfirm you want to <b>${auto_move_paused? 'Unpause': 'Pause'}</b> the queue auto move.`), () => {
				frappe.db.set_value('Queue Settings', 'Queue Settings','auto_move_paused', auto_move_paused? 0 : 1)
				location.reload()
			})
		})
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

