// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
frappe.ui.form.on("Project", {
	setup(frm) {
		frm.make_methods = {
			'Timesheet': () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			'Purchase Order': () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			'Purchase Receipt': () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			'Purchase Invoice': () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return {};
			return {
				"customer": frm.doc.customer,
				"project_name": frm.doc.name
			};
		};

		frm.set_query('customer', 'erpnext.controllers.queries.customer_query');

		frm.set_query("user", "users", function () {
			return {
				query: "erpnext.projects.doctype.project.project.get_users_for_project"
			};
		});

		// sales order
		frm.set_query('sales_order', function () {
			var filters = {
				'project': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			};
		});

		frm.set_query('quotations', function() {
			var filters = [
				['status', '=', 'Draft']
			]

			return {
				filters,
			}
		})

		frm.set_query('sales_invoice', function() {
			const filters = [
				['status','=','Unpaid']
			]
			return { filters }
		})

		frappe.realtime.off("docinfo_update");
		frappe.realtime.on('docinfo_update', (data) => {
			if (data.key === "attachment_logs") {
				insertCarousel(frm)
			}
		})
	},

	refresh: async function (frm) {
		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));
			frm.trigger('show_dashboard');
		}
		
		installQuotationItems(frm)
		installChat(frm);
		insertCarousel(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Create quotation"),  async () => {
				let new_doc = await frappe.model.get_new_doc("Quotation");
				new_doc.quotation_to = 'Customer';
				new_doc.party_name = frm.doc.customer;
				new_doc.project_name = frm.doc.name;
				frappe.ui.form.make_quick_entry('Quotation', null, null, new_doc);
			})
		}

		frm.trigger("set_custom_buttons");
	},
	create_duplicate: function(frm) {
		return new Promise(resolve => {
			frappe.prompt('Project Name', (data) => {
				frappe.xcall('erpnext.projects.doctype.project.project.create_duplicate_project',
					{
						prev_doc: frm.doc,
						project_name: data.value
					}).then(() => {
					frappe.set_route('Form', "Project", data.value);
					frappe.show_alert(__("Duplicate project has been created"));
				});
				resolve();
			});
		});
	},

	set_status: function(frm, status) {
		frappe.confirm(__('Set Project and all Tasks to status {0}?', [status.bold()]), () => {
			frappe.xcall('erpnext.projects.doctype.project.project.set_project_status',
				{project: frm.doc.name, status: status}).then(() => {
				frm.reload_doc();
			});
		});
	},

});

let instaling = false;
async function installChat(frm) {
	if (document.querySelector('#chat-container')){
		document.querySelector('#chat-container').remove();
	}
	frm.page.container.removeClass("full-width");
	if(instaling) return;
	instaling = true;
	if (!frm.is_new()){
		const {0: conversation} = await frappe.db.get_list('Conversation',{
			filters: [['from', '=', frm.doc.custom_customers_phone_number]],
			fields: ["*"]
		});
		
		if(!conversation) {
			instaling = false;
			return;
		};
		const chatContainer = document.createElement('div')

		const button = document.createElement('button')
		button.classList.add('btn','btn-default','ellipsis')
		button.textContent = 'Toggle WhatsApp'
		button.addEventListener('click', ()=>{
			if(chatContainer.style.display === 'none'){
				chatContainer.style.display = 'block';
			} else {
				chatContainer.style.display = 'none';
			}
		})
		
		document.querySelector('#custom_actions')
			.innerHTML = '';
		document.querySelector('#custom_actions')
			.appendChild(button)

		chatContainer.id = 'chat-container'
		const chat = document.createElement('erp-chat')
		const section = document.querySelector('#page-Project > div.container.page-body > div.page-wrapper > div > div.row.layout-main')
		
		const {aws_url} = await frappe.db.get_doc('Whatsapp Config')
		chat.setAttribute('url', aws_url)
		chat.setAttribute('user-name', frappe.user.full_name())
		
		frappe.realtime.on(`msg-${conversation.name}`, (data) => {
			chat._instance.exposed.addMessage(data); 
		})
		frappe.require('erp-whatsapp-chat.bundle.js')
			.then(() => {
				chatContainer.appendChild(chat)
				section.appendChild(chatContainer)
				setTimeout(() => {
					chat._instance.exposed.setFrappe(frappe)
          chat._instance.exposed.setConversation(conversation)
				}, 100);
			})


		frm.page.container.addClass("full-width");
	}
	instaling = false;
}

let is_quotation_installed = false;
function installQuotationItems(frm) {
    if (frm.is_new()) return;
    if (is_quotation_installed) return;
    
    const container = document.querySelector('div[data-fieldname="customer_details"] .section-body');
    if (!container) {
        return;
    }
    
    // Eliminar el componente existente si está presente
    const existingComponent = container.querySelector("erp-quotation-items");
    if (existingComponent) {
        container.removeChild(existingComponent);
    }
    
    is_quotation_installed = true;
    
    // Crear un contenedor adicional para manejar el desbordamiento
    const wrapper = document.createElement("div");
    wrapper.style.width = '100%';  // Ajusta al tamaño del contenedor
    wrapper.style.overflow = 'auto';  // Permite el scroll si es necesario
    
    frappe.require("erp-quotation-items.bundle.js").then(() => {
        const element = document.createElement("erp-quotation-items");
        element.style.width = '100%';  // Asegura que el componente no exceda el contenedor
        element.style.maxWidth = '100%';  // Evita que el componente se expanda más allá del contenedor
        element.style.boxSizing = 'border-box';  // Incluye padding y border en el ancho total
        element.style.display = 'block';  // Asegura que el componente se comporte como un bloque
        
        // Añadir el componente al contenedor wrapper
        wrapper.appendChild(element);
        container.appendChild(wrapper);
        
        // Forzar un redibujado del contenedor
        container.style.overflow = 'hidden';  // Establecer overflow a hidden
        container.offsetHeight;  // Forzar un reflujo
        container.style.overflow = 'auto';  // Restaurar overflow a auto
        
        setTimeout(() => {
            element._instance.exposed.setFrappe(frappe);
            element._instance.exposed.setProjectName(frm.doc.name);
			element._instance.exposed.setUserSession(frappe.session)
            is_quotation_installed = false;
        }, 100);
    }).catch((err) => {
        console.error("Error loading erp-quotation-items", err);
        is_quotation_installed = false;
    });
}

function open_form(frm, doctype, child_doctype, parentfield) {
	frappe.model.with_doctype(doctype, () => {
		let new_doc = frappe.model.get_new_doc(doctype);

		// add a new row and set the project
		let new_child_doc = frappe.model.get_new_doc(child_doctype);
		new_child_doc.project = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];
		new_doc.project = frm.doc.name;

		frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});

}

let touchTimeout;
async function insertCarousel(frm) {
	frappe.require('glider.bundle.js', () => {
		setTimeout(() => {
			frappe.db.get_list("File", {
				filters: [
					['attached_to_name', 'in', frm.doc.name],
					['attached_to_doctype', '=', "Project"]
				],
				fields: ["file_url", "file_type"],
				limit: 10
			}).then((attachments) => {
				const tracker = document.querySelector('.glider-track')
				const container = document.querySelector('.glider-contain')
				const gliderEl = document.querySelector('.glider')

				const glider = new Glider(gliderEl, {
					slidesToShow: 1,
					draggable: true,
					dots: '.dots',
					arrows: {
						prev: '.glider-prev',
						next: '.glider-next'
					},
					responsive: [
						{
							breakpoint: 600,
							settings: {
								slidesToShow: 2,
								slidesToScroll: 2,
								duration: 0.25
							}
						}, {
							breakpoint: 1024,
							settings: {
								slidesToShow: 5,
								slidesToScroll: 5,
								duration: 0.25
							}
						}
					]
				})

				//remove all items
				if (tracker && glider) {
					for (let index = 0; index < tracker.childElementCount; index++) {
						glider.removeItem(index)
					}
				}

				if (attachments && attachments.length > 0 && glider) {
					container.style = 'height: auto;overflow:hidden;'

					for (const attachment of attachments) {
						const el = createAttachmentElement(attachment)
						if (el) {
							setListeners(el, attachment)
							glider.addItem(el)
						}
					}

				} else {
					container.style = 'height: 0;overflow:hidden;'
					console.log('No attachments found for this project.');
				}
			})
		}, 3000)// if this time is less than 3 sec it'll be render a wrong carousel
	})
}

function setListeners(el, attachment) {
	let element = el

	if(attachment.file_type === "MOV" || attachment.file_type === "MP4") return null
	if (attachment.file_type === 'PDF' || attachment.file_url === 'TXT') {
		element = el.querySelector('#touch-overlay')
	}
	element.addEventListener('touchstart', (e) => handleTouchStart(e, attachment))
	element.addEventListener('touchend', handleTouchEnd)

}

function createAttachmentElement(attachment) {
	let el;

	switch(attachment.file_type){
		case "PDF":
		case "TXT":
			el = document.createElement('div')
			el.style = `width: 100%;overflow: hidden; position: relative;`
			el.innerHTML = `<iframe src="${attachment.file_url}" frameborder="0" class="glider-iframe"></iframe> <div id="touch-overlay"></div>`
			break;
		case "MOV":
			case "MP4":
			el = document.createElement('video')
			el.className = 'video-container'
			el.setAttribute('controls', 'true')
			el.setAttribute('src',attachment.file_url)
			break;
		default:
			el = document.createElement('img')
			el.setAttribute('src', attachment.file_url)
	}

	return el
}


function handleTouchStart(e, attachment) {
	touchTimeout = setTimeout(() => {
		const attachmentContainer = document.querySelector('#selected-attachment')
		const el = createAttachmentElement(attachment)
		attachmentContainer.addEventListener('touchend', handleTouchEnd)
		attachmentContainer.appendChild(el)
		attachmentContainer.removeAttribute('hidden')
	}, 1000)
}

function handleTouchEnd(e) {
	clearTimeout(touchTimeout)
	const attachmentContainer = document.querySelector('#selected-attachment')
	if (attachmentContainer) {
		attachmentContainer.innerHTML = ``
		attachmentContainer.setAttribute('hidden', "true")
	}
}

