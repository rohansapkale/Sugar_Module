// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Dispatch Entry", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Dispatch Entry", {

    sugar_purchase: function(frm) {

        if (!frm.doc.sugar_purchase) return;

        frappe.db.get_value(
            "Sugar Purchase",
            frm.doc.sugar_purchase,
            ["item"]
        ).then(r => {

            frm.set_value("item", r.message.item);

        });

    }

});
