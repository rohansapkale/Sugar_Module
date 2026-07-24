// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.query_reports["Broker Ledger"] = {
    filters: [
        {
            fieldname: "broker",
            label: "Broker",
            fieldtype: "Link",
            options: "Broker"
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        }
    ]
};
