# Database Configuration for ERPNext

This guide provides detailed instructions on how to configure MariaDB and PostgreSQL databases for ERPNext.

## Configuring MariaDB

1. **Install MariaDB**

   Follow the installation instructions for your operating system on the [MariaDB website](https://mariadb.com/kb/en/getting-installing-and-upgrading-mariadb/).

2. **Create a Database and User**

   Open a terminal and run the following commands to create a database and user for ERPNext:

   ```sh
   mysql -u root -p
   ```

   ```sql
   CREATE DATABASE erpnext;
   CREATE USER 'erpnext'@'localhost' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON erpnext.* TO 'erpnext'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Configure MariaDB for ERPNext**

   Edit the MariaDB configuration file (usually located at `/etc/mysql/my.cnf` or `/etc/mysql/mariadb.conf.d/50-server.cnf`) and add the following settings under the `[mysqld]` section:

   ```ini
   [mysqld]
   character-set-server = utf8mb4
   collation-server = utf8mb4_unicode_ci
   ```

   Restart the MariaDB service to apply the changes:

   ```sh
   sudo systemctl restart mariadb
   ```

## Configuring PostgreSQL

1. **Install PostgreSQL**

   Follow the installation instructions for your operating system on the [PostgreSQL website](https://www.postgresql.org/download/).

2. **Create a Database and User**

   Open a terminal and run the following commands to create a database and user for ERPNext:

   ```sh
   sudo -i -u postgres
   ```

   ```sql
   CREATE DATABASE erpnext;
   CREATE USER erpnext WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE erpnext TO erpnext;
   ```

3. **Configure PostgreSQL for ERPNext**

   Edit the PostgreSQL configuration file (usually located at `/etc/postgresql/<version>/main/postgresql.conf`) and add the following settings:

   ```ini
   client_encoding = utf8
   ```

   Restart the PostgreSQL service to apply the changes:

   ```sh
   sudo systemctl restart postgresql
   ```

## Connecting ERPNext to the Database

1. **Update the `site_config.json` file**

   Edit the `site_config.json` file located in the `sites` directory of your ERPNext installation and update the database settings:

   For MariaDB:

   ```json
   {
     "db_name": "erpnext",
     "db_password": "password",
     "db_type": "mariadb"
   }
   ```

   For PostgreSQL:

   ```json
   {
     "db_name": "erpnext",
     "db_password": "password",
     "db_type": "postgres"
   }
   ```

2. **Restart ERPNext**

   Restart the ERPNext service to apply the changes:

   ```sh
   sudo systemctl restart erpnext
   ```

By following these steps, you can configure MariaDB and PostgreSQL databases for ERPNext and connect the application to the database.
