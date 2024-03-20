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
	async before_render(){
		const { auto_move_paused }  = await frappe.db.get_doc('Queue Settings')
		setTimeout(() => {
			const exists = document.querySelector("#page-List\\/Project\\/List > div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end #queue-freeze")
			if (!exists){
				const container = document.querySelector('#page-List\\/Project\\/List > div.page-head.flex > div > div > div.flex.col.page-actions.justify-content-end')
				const input = document.createElement('input')
				const label = document.createElement('label')
				label.setAttribute('style', 'margin: 0')
				label.setAttribute('id', 'queue-freeze')
				label.innerText = ' freeze queue positions '
				label.appendChild(input)
				input.setAttribute('type', 'checkbox')
				if (auto_move_paused) {
					input.setAttribute('checked', 'checked')
				}
				container.prepend(label);
				input.addEventListener('change', (event) => {
					frappe.db.set_value('Queue Settings', 'Queue Settings','auto_move_paused', auto_move_paused? 0 : 1)
					.then(()=> {
						frappe.msgprint(__('Status updated successfully'));
					})
				})
			}
		}, 1500)
	}
};

const installErpCalendar = async () => {
	const el = document.createElement('erp-calendar')
	const {aws_url} = await frappe.db.get_doc('Whatsapp Config')
	el.setAttribute('url', location.origin);
	el.setAttribute('aws_url', aws_url)
	if(!document.querySelector('erp-calendar')){
		frappe.require('erp-calendar.bundle.js').then(() => {
			document.querySelector('body').appendChild(el)
		})
	}
}


navigation.addEventListener("navigatesuccess", async () => {
	if (/\/project\.*/.test(location.pathname)){
		await installErpCalendar()
	} else {
		document.querySelector('erp-calendar')?.remove()
	}
})

