import frappe
def execute(filters=None):
    columns = get_columns()

    payment_entries = get_payment_entries(filters)
    journal_entries = get_journal_entries(filters)
    bank_transactions = get_bank_transaction_entries(filters)

    data = (
        get_static_rows(bank_transactions, payment_entries, journal_entries,filters) 
        
    )

    return columns, data


def get_columns():
    """Define the columns for the report."""
    return [
        {"fieldname": "details", "label": "Details", "fieldtype": "Data", "width": 350},
        {"fieldname": "debit", "label": "Debit", "fieldtype": "Currency", "width": 200},
        {"fieldname": "credit", "label": "Credit", "fieldtype": "Currency", "width": 200},
        {"fieldname": "payment_document", "label": "DocType", "fieldtype": "Data", "width": 200},
        {"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 200}, 
        {"fieldname": "reference_no", "label": "Reference No", "fieldtype": "Data", "width": 200},
    ]


def get_static_rows(bank_transactions, payment_entries, journal_entries,filters):
    account_balance = get_account_balance(filters.get("account"), filters.get("from_date"))
    total_debit = account_balance["total_debit"]
    total_credit = account_balance["total_credit"]
    balance = account_balance["balance"]

    static_rows = [
        {
            "posting_date": None,
            "payment_document": None,
            "details": "<b>Balance as per ERPNext</b>",
            "debit": balance if balance > 0 else 0,  # Debit only if balance is positive
            "credit": abs(balance) if balance < 0 else 0,  # Credit only if balance is negative
            "reference_no": None,
        },
        {
            "posting_date": None,
            "payment_document": None,
            "details": "",
            "debit": None,
            "credit": None,
            "reference_no": None,
        },
        {
            "posting_date": None,
            "payment_document": None,
            "details": "<b>I. Adjustment of transactions missing in ERPNext which is reflecting in bank statement</b>",
            "debit": None,
            "credit": None,
            "reference_no": None,
        },
        {
            "posting_date": None,
            "payment_document": None,
            "details": '<font color="gray">Unreconciled deposits in bank statement not reflecting in ERPNext</font>',
            "debit": None,
            "credit": None,
            "reference_no": None,
            "indent": 0,
        }
    ]

    for transaction in bank_transactions:
        deposit = transaction.get('deposit', 0)
        if deposit != 0: 
            static_rows.append({
                "posting_date": f"{transaction.get('posting_date', '')}",
                "payment_document": f"{transaction.get('payment_document', '')}",
                "details": f"{transaction.get('name', '')}",
                "debit": f"{transaction.get('deposit', '')}",
                "credit": None,
                "reference_no":f"{transaction.get('reference_no', '')}",
                "indent": 1,
            })

    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": '<font color="gray">Unreconciled Withdrawals in bank statement not reflecting in ERPNext</font>',
        "debit": None,
        "credit": None,
        "reference_no": None,
        "indent": 0,
    })

    for transaction in bank_transactions:
        withdrawal = transaction.get('withdrawal', 0)
        if withdrawal != 0:
            static_rows.append({
                "posting_date": f"{transaction.get('posting_date', '')}",
                "payment_document": f"{transaction.get('payment_document', '')}",
                "details": f"{transaction.get('name', '')}",
                "debit": None,
                "credit": f"{transaction.get('withdrawal', '')}",
                "reference_no":f"{transaction.get('reference_no', '')}",
                "indent": 1,
            })

    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": "",
        "debit": None,
        "credit": None,
        "reference_no": None,
    })

    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": "<b>II. Adjustment of transactions missing in bank statement which is reflecting in ERPNext</b>",
        "debit": None,
        "credit": None,
        "reference_no": None,
        
    })

    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": '<font color="gray">Unreconciled deposits in ERPNext not reflecting in Bank Statement</font>',
        "debit": None,
        "credit": None,
        "reference_no": None,
        "indent": 0,
    })


    for payment in payment_entries:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': payment.get('payment_entry', '')})
        if connection == 0:
            credit = payment.get('credit', 0)
            payment_type = payment.get('payment_type', '') 
            if credit != 0 and payment_type == "Receive":
                static_rows.append({
                    "posting_date": f"{payment.get('posting_date', '')}",
                    "payment_document": f"{payment.get('payment_document', '')}",
                    "details": f"{payment.get('payment_entry', '')}",
                    "debit": None,
                    "credit":f"{payment.get('credit', '')}",
                    "reference_no":f"{payment.get('reference_no', '')}",
                    "indent": 1,
                })

    payments = frappe.get_all(
        "Payment Entry",
        filters={
            "paid_to": filters.get("account"), 
            "docstatus": 1,
            "payment_type": "Internal Transfer",
        },
        fields=[
            "'Payment Entry' AS payment_document",
            "name",
            "paid_to",
            "paid_amount",
            "posting_date",
            "reference_no",
        ],
    )


    unique_payment_names = set()

    for itpayment in payments:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': itpayment.get('name')})
        
        if connection == 0 and itpayment.get('name') not in unique_payment_names:
            static_rows.append({
                "posting_date": itpayment.get('posting_date', ''),
                "payment_document": itpayment.get('payment_document', ''),
                "details": itpayment.get('name', ''),
                "debit": None,
                "credit": itpayment.get('paid_amount', 0),
                "reference_no": itpayment.get('reference_no', None),
                "indent": 1,
            })
            unique_payment_names.add(itpayment.get('name'))




    for journal in journal_entries:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': journal.get('payment_entry', '')})
        if connection == 0:
            debit = journal.get('debit', 0) 
            if debit != 0: 
                static_rows.append({
                    "posting_date": f"{payment.get('posting_date', '')}",
                    "payment_document": f"{journal.get('payment_document', '')}",
                    "details": f"{journal.get('payment_entry', '')}",
                    "debit":None,
                    "credit": f"{journal.get('debit', '')}",
                    "doctype": None,
                    "reference_no":f"{journal.get('reference_no', '')}",
                    "indent": 1,
                })


    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": '<font color="gray">Unreconciled withdrawals in ERPNext not reflecting in bank statement</font>',
        "debit": None,
        "credit": None,
        "doctype": None,
        "reference_no": None,
        "indent": 0,
    })

    for payment in payment_entries:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': payment.get('payment_entry', '')})
        if connection == 0:
            debit = payment.get('debit', 0)
            payment_type = payment.get('payment_type', '')
            if debit != 0 and payment_type == "Pay":  
                static_rows.append({
                    "posting_date": f"{payment.get('posting_date', '')}",
                    "payment_document": f"{payment.get('payment_document', '')}", 
                    "details": f"{payment.get('payment_entry', '')}",
                    "debit": f"{payment.get('debit', '')}",
                    "credit": None,
                    "doctype": None,
                    "reference_no":f"{payment.get('reference_no', '')}",
                    "indent": 1,
                })

    payments = frappe.get_all("Payment Entry",filters={"paid_from": "IDFC Bank - PP Ltd", "docstatus": 1,"payment_type":"Internal Transfer"},fields=[
            "'Payment Entry' AS payment_document",
            "name",
            "paid_to",
            "paid_amount",
            "posting_date",
            "reference_no",
        ]
    )

    unique_payment_names = set()

    for itpayment in payments:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': itpayment.get('name')})
        if connection == 0 and itpayment.get('name') not in unique_payment_names:
            static_rows.append({
                "posting_date": itpayment.get('posting_date', ''),
                "payment_document": itpayment.get('payment_document', ''),
                "details": itpayment.get('name', ''),
                "debit": itpayment.get('paid_amount', 0),
                "credit": None,
                "reference_no": itpayment.get('reference_no', None),
                "indent": 1,
            })
            unique_payment_names.add(itpayment.get('name'))

    for journal in journal_entries:
        connection = frappe.db.count('Bank Transaction Payments', {'payment_entry': journal.get('payment_entry', '')})
        if connection == 0:
            credit = journal.get('credit', 0)
            if credit != 0:
                static_rows.append({
                    "posting_date": f"{journal.get('posting_date', '')}",
                    "payment_document": f"{journal.get('payment_document', '')}",
                    "details": f"{journal.get('payment_entry', '')}",
                    "debit": f"{journal.get('credit', '')}",
                    "credit": None,
                    "reference_no":f"{journal.get('reference_no', '')}",
                    "indent": 1,
                })

    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": "",
        "debit": None,
        "credit": None,
        "reference_no": None,
    })

    
    total_debit_in_rows = sum((float(row.get('debit') or 0)) for row in static_rows)
    total_credit = 0

    for row in static_rows:
        credit = row.get('credit', 0)
        if credit not in [None, ""]:
            credit = float(credit)
            if total_credit == 0:
                total_credit = -credit 
                print(f"Starting with credit (negative): {total_credit}")
            else:
                total_credit -= credit
                print(f"Subtracting credit: {credit}, New total: {total_credit}")



    static_rows.append({
        "posting_date": None,
        "payment_document": None,
        "details": "<b>Balance as per bank statement</b>",
        "debit": float(total_debit_in_rows) + float(total_credit),
        "credit": None,
        "reference_no": None,
    })


    return static_rows



def format_adjustment_data(entries, filters, adjustment_type):
    """Format data for specific adjustments."""
    formatted_data = []
    for entry in entries:
        formatted_data.append({
            "posting_date": entry.get("posting_date"),
            "payment_document": entry.get("payment_document"),
            "details": entry.get("details", ""),
            "debit": entry.get("debit"),
            "credit": entry.get("credit"),
            "reference_no": entry.get("reference_no"),
        })
    return formatted_data


def get_payment_entries(filters):
    """Fetch payment entries."""
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    return frappe.db.sql(
    """
    SELECT
        'Payment Entry' AS payment_document,
        name AS payment_entry,
        reference_no as reference_no,
        posting_date AS posting_date,
        paid_amount as debit,
        paid_amount as credit,
        posting_date,
        paid_from,
        paid_to,
        payment_type,

        COALESCE(party, CASE WHEN paid_from = %(account)s THEN paid_to ELSE paid_from END) AS details
    FROM `tabPayment Entry`
    WHERE
        (paid_from = %(account)s OR paid_to = %(account)s)
        AND docstatus = 1

    """,{"account": filters.get("account"), "from_date": filters.get("from_date"), "to_date": filters.get("to_date")},
    as_dict=True,
)




def get_journal_entries(filters):
    """Fetch journal entries."""
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    # Check if account filter is passed, if not raise an exception
    account = filters.get("account")
    if not account:
        frappe.throw("Account filter is required")

    # Ensure from_date and to_date are provided
    if not from_date or not to_date:
        frappe.throw("Both 'from_date' and 'to_date' are required filters")

    return frappe.db.sql(
        """
        SELECT
            'Journal Entry' AS payment_document,
            jv.posting_date AS posting_date,
            jv.name AS payment_entry,
            jvd.debit_in_account_currency AS debit,
            jvd.credit_in_account_currency AS credit,
            jvd.against_account AS details,
            jvd.account AS account,
            jv.cheque_no AS reference_no,
            jv.cheque_date AS ref_date,
            acc.account_type
        FROM
            `tabJournal Entry Account` jvd
        JOIN
            `tabJournal Entry` jv ON jvd.parent = jv.name
        LEFT JOIN `tabAccount` AS acc ON jvd.account = acc.name
        WHERE
            jv.docstatus = 1
            AND jvd.account = %(account)s
            AND jv.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """,
        {"account": account, "from_date": from_date, "to_date": to_date},
        as_dict=True,
    )


def get_bank_transaction_entries(filters):
    """Fetch unreconciled bank transactions."""
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Ensure from_date and to_date are provided
    if not from_date or not to_date:
        frappe.throw("Both 'from_date' and 'to_date' are required filters")

    # SQL query corrected
    return frappe.db.sql(
        """
        SELECT 
            'Bank Transaction' AS payment_document,
            name AS name,
            bank_account AS bank_account,
            deposit AS deposit,
            withdrawal AS withdrawal,
            date AS posting_date,  
            reference_number AS reference_no,             
            NULL AS details
        FROM 
            `tabBank Transaction`
        WHERE 
            status = 'Unreconciled'
            AND date BETWEEN %(from_date)s AND %(to_date)s
        """,
        {"from_date": from_date, "to_date": to_date},
        as_dict=True,
    )



def get_account_balance(account, from_date):
    """Fetch opening balances for the given account and calculate balance."""
    balance_data = frappe.db.sql("""
        SELECT 
            SUM(debit) AS total_debit, 
            SUM(credit) AS total_credit 
        FROM `tabGL Entry`
        WHERE account = %s
    """, (account,), as_dict=True)
    if balance_data and balance_data[0]:
        total_debit = balance_data[0].get('total_debit', 0)
        total_credit = balance_data[0].get('total_credit', 0)
    else:
        total_debit = 0
        total_credit = 0
    balance_query = frappe.db.sql("""
        SELECT 
            SUM(CASE WHEN debit > 0 THEN debit ELSE 0 END) - 
            SUM(CASE WHEN credit > 0 THEN credit ELSE 0 END) AS balance
        FROM `tabGL Entry`
        WHERE account = %s
    """, (account,), as_dict=True)
    balance = balance_query[0].get('balance', 0) if balance_query else 0
    return {
        "total_debit": total_debit,
        "total_credit": total_credit,
        "balance": balance
    }


