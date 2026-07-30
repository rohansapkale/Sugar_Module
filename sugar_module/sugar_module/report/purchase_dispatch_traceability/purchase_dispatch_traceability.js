// Copyright (c) 2026, Rohan Sapkale and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Dispatch Traceability"] = {
    filters: [

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        },

        {
            fieldname: "supplier",
            label: "Supplier",
            fieldtype: "Link",
            options: "Supplier"
        },

        {
            fieldname: "broker",
            label: "Broker",
            fieldtype: "Link",
            options: "Broker"
        },

        {
            fieldname: "payment_status",
            label: "Payment Status",
            fieldtype: "Select",
            options: "\nPaid\nPartial\nUnpaid"
        }

    ]
};
