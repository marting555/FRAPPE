# Guía rápida para instalar ERPNext con datos de prueba

Este documento explica cómo preparar un entorno local utilizando **bench** en Ubuntu y cómo poblar la base de datos con ejemplos mínimos para la empresa **Ansimaq**.

## 1. Instalación de dependencias

```bash
sudo apt update
sudo apt install git python3-dev python3-pip mariadb-server redis-server nodejs npm
pip3 install frappe-bench
```

## 2. Creación del entorno Bench

```bash
bench init ansimaq-bench
cd ansimaq-bench
bench get-app erpnext
```

## 3. Creación del sitio

```bash
bench new-site ansimaq.local
bench --site ansimaq.local install-app erpnext
```

Sigue las instrucciones en pantalla para definir el usuario **Administrator** y la contraseña de MariaDB.

## 4. Arranque del servidor de desarrollo

```bash
bench start
```

El sistema quedará accesible en `http://localhost:8000`. Al iniciar sesión con el usuario **Administrator**, se abrirá el asistente de configuración. Utiliza **Ansimaq** como nombre de la empresa y selecciona la opción *"Cargar datos de ejemplo"* para que se creen algunos registros automáticamente.

## 5. Poblar con ejemplos adicionales

Tras completar el asistente, puedes agregar datos extra desde la consola de frappe:

```bash
bench --site ansimaq.local console
```

Dentro de la consola ejecuta:

```python
import frappe

# Cliente de ejemplo
frappe.get_doc({
    "doctype": "Customer",
    "customer_name": "Ansimaq S.A.",
    "customer_type": "Company"
}).insert()

# Artículo de ejemplo
frappe.get_doc({
    "doctype": "Item",
    "item_code": "ANS-001",
    "item_name": "Servicio Demo",
    "stock_uom": "Unit"
}).insert()

# Factura de ejemplo
invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": "Ansimaq S.A.",
    "items": [{"item_code": "ANS-001", "qty": 1, "rate": 100}]
})
invoice.insert()
frappe.db.commit()
```

Con estos pasos el front‑end y el back‑end estarán listos para usarse juntos desde `bench start`.
