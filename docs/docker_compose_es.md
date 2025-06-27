# Configuración rápida con Docker Compose

Este documento explica cómo iniciar **ERPNext** utilizando *Docker Compose* sin instalar `bench` en tu sistema.

## Requisitos previos

- Tener instalado [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/).
- Clonar este repositorio en tu entorno local.

## Archivo `docker-compose.yml`

Crea un archivo `docker-compose.yml` en la raíz del proyecto con el siguiente contenido básico:

```yaml
version: '3.7'
services:
  backend:
    image: frappe/erpnext:edge
    environment:
      - SITE_NAME=site.local
      - DB_ROOT_USER=root
      - MYSQL_ROOT_PASSWORD=frappe
      - ADMIN_PASSWORD=admin
      - INSTALL_APPS=erpnext
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    ports:
      - "8000:8000"

  frontend:
    image: frappe/erpnext-nginx:edge
    depends_on:
      - backend
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    ports:
      - "80:80"

volumes:
  sites:
```

Este ejemplo crea un sitio llamado `site.local` y configura las contraseñas de la base de datos y del usuario administrador mediante variables de entorno.

## Puesta en marcha

1. Construye y levanta los contenedores:
   ```bash
   docker compose up -d
   ```
2. Una vez finalizado el proceso, accede a `http://localhost` en tu navegador y continúa con la configuración inicial.

## Notas adicionales

- No es necesario instalar `bench` en el host; todas las dependencias se resuelven dentro de los contenedores.
- Los datos del sitio se almacenan en el volumen `sites`, lo que permite conservar la información entre reinicios.
- Puedes editar el código desde **Visual Studio Code** y reiniciar los contenedores para aplicar los cambios en el front‑end y back‑end de manera conjunta.

