import "@tvsgroup/erp-calendar";

(async () => {
    const el = document.createElement('erp-calendar')
    const {aws_url} = await frappe.db.get_doc('Whatsapp Config')
    console.log(aws_url)
    el.setAttribute('url', location.origin);
    el.setAttribute('aws_url', aws_url)
    if(!document.querySelector('erp-calendar')){
      document.querySelector('body').appendChild(el)

      setTimeout(() => {
        el._instance.exposed.setFrappe(frappe)
      }, 100);
    }
  
})()