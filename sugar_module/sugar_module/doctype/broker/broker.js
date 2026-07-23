// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Broker", {
// 	refresh(frm) {

// 	},
// });
frappe.listview_settings["Broker"] = {
    add_fields: ["status"],

    get_indicator: function(doc) {
        if (doc.status === "Active") {
            return ["Active", "green", "status,=,Active"];
        }

        return ["Inactive", "red", "status,=,Inactive"];
    }
};
