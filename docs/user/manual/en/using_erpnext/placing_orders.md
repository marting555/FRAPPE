# Placing Orders, Managing Sales, Deliveries, and Inventories in ERPNext

## Placing Orders

1. **Navigate to the Sales Order Module**:
   - Go to the ERPNext dashboard.
   - Click on the "Sales" module.
   - Select "Sales Order".

2. **Create a New Sales Order**:
   - Click on the "New" button.
   - Fill in the customer details, item details, and other relevant information.
   - Save the sales order.

3. **Submit the Sales Order**:
   - After saving, click on the "Submit" button to finalize the order.

## Managing Sales

1. **Sales Invoices**:
   - Navigate to the "Sales Invoice" module.
   - Create a new sales invoice by linking it to the sales order.
   - Fill in the necessary details and submit the invoice.

2. **Sales Reports**:
   - Go to the "Sales Analytics" module.
   - Generate reports to analyze sales performance.

## Managing Deliveries

1. **Delivery Notes**:
   - Navigate to the "Delivery Note" module.
   - Create a new delivery note by linking it to the sales order.
   - Fill in the delivery details and submit the note.

2. **Track Deliveries**:
   - Use the "Delivery Analytics" module to track and manage deliveries.

## Managing Inventories

1. **Stock Entries**:
   - Navigate to the "Stock Entry" module.
   - Create new stock entries for incoming and outgoing stock.
   - Fill in the necessary details and submit the entries.

2. **Inventory Reports**:
   - Go to the "Stock Analytics" module.
   - Generate reports to analyze inventory levels and movements.

## Linking Necessary Databases for Sales Management

1. **Database Configuration**:
   - Ensure that the ERPNext instance is connected to the appropriate database (e.g., MariaDB or PostgreSQL).
   - Configure the database settings in the `site_config.json` file.

2. **Database Linking**:
   - Link the sales order, sales invoice, delivery note, and stock entry modules to the database.
   - Ensure that all data is stored and retrieved correctly from the database.

3. **Database Maintenance**:
   - Regularly back up the database to prevent data loss.
   - Perform routine maintenance tasks such as optimizing tables and checking for errors.
