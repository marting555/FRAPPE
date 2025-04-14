# Contributing to ERPNext

Thank you for considering contributing to ERPNext! This document outlines the process for contributing to the project and documents a specific contribution made to improve the user experience.

## How to Contribute

### 1. Set Up Your Development Environment

Follow these steps to set up your local development environment:

1. Fork the ERPNext repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/[your-username]/erpnext.git
   cd erpnext
   ```
3. Set up the development environment following the instructions in the [README.md](README.md) file

### 2. Find an Issue to Work On

1. Look for open issues on the [ERPNext GitHub Issues page](https://github.com/frappe/erpnext/issues)
2. Filter for issues labeled "good first issue" if you're a first-time contributor
3. Comment on the issue you want to work on to let others know you're addressing it

### 3. Create a Feature Branch

```bash
git checkout -b feat/[feature-name]
```

### 4. Make Your Changes

1. Implement your changes following ERPNext coding standards
2. Add tests if applicable
3. Run the tests to ensure your changes don't break existing functionality
4. Document your changes

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: Description of your changes"
```

Use [conventional commit messages](https://www.conventionalcommits.org/en/v1.0.0/) for clear and consistent commit history.

### 6. Push Your Changes and Create a Pull Request

```bash
git push origin feat/[feature-name]
```

Then create a pull request on GitHub from your forked repository.

## Example Contribution: Auto-populate Party Information in Payment Entry

### Issue Description

Issue #34794: "Auto populate Party information in Payment Entry when creating PE from Supplier/Customer Dashboard"

When users create a Payment Entry from the Customer or Supplier dashboard, they had to manually fill in party information that was already known from the context. This created unnecessary steps and reduced efficiency.

### Solution Implemented

1. Created a new function `get_payment_entry_from_party` in `payment_entry.py` to generate pre-populated Payment Entries when triggered from the party dashboard
2. Updated the Customer and Supplier JS files to use this function when creating Payment Entries
3. Ensured proper account selection based on payment type (Pay/Receive)

### Technical Details

The implementation adds:

1. A new server-side function in `erpnext/accounts/doctype/payment_entry/payment_entry.py`:
   ```python
   @frappe.whitelist()
   def get_payment_entry_from_party(party_type, party, company=None, payment_type=None):
       # Function creates a Payment Entry with pre-populated party information
   ```

2. Client-side integration in Customer and Supplier forms:
   ```javascript
   frm.add_custom_button(
       __("Payment Entry"),
       function () {
           frappe.call({
               method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry_from_party",
               args: {
                   party_type: "Customer", // or "Supplier"
                   party: frm.doc.name,
                   company: frm.doc.company
               },
               callback: function (r) {
                   if (r.message) {
                       const doc = frappe.model.sync(r.message)[0];
                       frappe.set_route("Form", doc.doctype, doc.name);
                   }
               }
           });
       },
       __("Create")
   );
   ```

### Benefits

1. Improved user experience by eliminating repetitive data entry
2. Reduced potential for errors in party information
3. Streamlined payment creation workflow

This contribution demonstrates attention to user experience, code quality, and follows ERPNext's development patterns and standards.

## Additional Resources

- [ERPNext Documentation](https://docs.erpnext.com/)
- [Frappe Framework Documentation](https://frappeframework.com/docs/v14/user/en)
- [ERPNext Developer Forum](https://discuss.erpnext.com/)
