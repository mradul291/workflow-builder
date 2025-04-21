// Copyright (c) 2025, Mradul Mishra and contributors
// For license information, please see license.txt

frappe.ui.form.on("ToDo Template", {
  onload(frm) {
    console.log(frm.doc.due_date);
  },
});
