# Entorno Docker para ERPNext y Ansimaq

Esta guía explica cómo iniciar ERPNext en contenedores utilizando **docker compose** y cómo poblar una base de datos de ejemplo para la empresa **Ansimaq**.

## Requisitos previos

- Docker y docker compose instalados en el sistema.

## 1. Preparación

1. Clona este repositorio y ubícate en la carpeta raiz.
2. Ejecuta `docker compose up` para descargar las imágenes y crear los contenedores.
3. La primera vez se creará un sitio llamado `ansimaq.local` con la contraseña de administrador `admin` y la de MariaDB `root`.
4. Una vez completado el proceso, ERPNext quedará disponible en `http://localhost:8000`.

## 2. Poblar datos de ejemplo

Para agregar algunos registros de demostración ejecuta la consola de frappe dentro del contenedor:

```bash
docker compose exec frappe bench --site ansimaq.local execute scripts.ansimaq_populate.run
```

Este comando creará un cliente, un artículo y una factura de ejemplo.

Con esto el front-end y el back-end quedarán listos para probar la instalación de **Ansimaq** usando contenedores.
