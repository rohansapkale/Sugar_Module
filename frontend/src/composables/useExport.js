/**
 * Export & Print Utilities for Sugar Desk
 */

export function downloadCSV(filename, rows) {
  if (!rows || !rows.length) return
  const processRow = (row) => {
    return row
      .map((val) => {
        if (val === null || val === undefined) return '""'
        let str = String(val).replace(/"/g, '""')
        return `"${str}"`
      })
      .join(',')
  }

  const csvContent = rows.map(processRow).join('\r\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename.endsWith('.csv') ? filename : `${filename}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export function printFormattedHtml(title, htmlContent, companyName = 'Mahalaxmi Sugar Mills Pvt. Ltd.') {
  const printWindow = window.open('', '_blank', 'width=950,height=750')
  if (!printWindow) {
    alert('Please allow popups to open the print view.')
    return
  }
  const dateStr = new Date().toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      color: #0f172a;
      padding: 24px;
      margin: 0;
      font-size: 12.5px;
      line-height: 1.45;
    }
    .print-header {
      border-bottom: 2px solid #132b4e;
      padding-bottom: 12px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    .company-title {
      font-size: 18px;
      font-weight: 800;
      color: #132b4e;
    }
    .report-title {
      font-size: 14px;
      font-weight: 700;
      color: #2563eb;
      margin-top: 3px;
    }
    .print-meta {
      font-size: 11px;
      color: #64748b;
      text-align: right;
    }
    .kpi-grid {
      display: table;
      width: 100%;
      margin-bottom: 14px;
      border-collapse: separate;
      border-spacing: 10px 0;
    }
    .kpi-row {
      display: table-row;
    }
    .kpi-box {
      display: table-cell;
      border: 1px solid #cbd5e1;
      padding: 8px 12px;
      border-radius: 4px;
      background: #f8fafc;
      width: 25%;
    }
    .kpi-label {
      font-size: 10px;
      color: #64748b;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
    }
    .kpi-val {
      font-size: 15px;
      font-weight: 800;
      margin-top: 3px;
    }
    .val-red { color: #b91c1c; }
    .val-green { color: #15803d; }
    .val-blue { color: #1d4ed8; }
    .val-navy { color: #0f172a; }
    
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      margin-bottom: 14px;
      font-size: 11.5px;
    }
    th {
      background: #0f172a;
      color: #ffffff;
      text-align: left;
      padding: 6px 8px;
      font-weight: 600;
      border: 1px solid #0f172a;
    }
    td {
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
    }
    tr:nth-child(even) td {
      background: #f8fafc;
    }
    .text-right { text-align: right; }
    .text-center { text-align: center; }
    .font-mono { font-family: monospace; }
    .font-bold { font-weight: bold; }
    .footer {
      margin-top: 24px;
      font-size: 10.5px;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
      padding-top: 8px;
      text-align: center;
    }
    @media print {
      body { padding: 0; }
      @page { margin: 12mm 10mm 12mm 10mm; }
    }
  </style>
</head>
<body>
  <div class="print-header">
    <div>
      <div class="company-title">🌾 ${companyName}</div>
      <div class="report-title">${title}</div>
    </div>
    <div class="print-meta">
      <div><strong>Printed:</strong> ${dateStr}</div>
      <div>Sugar Desk Trade &amp; Financial Ledger</div>
    </div>
  </div>

  ${htmlContent}

  <div class="footer">
    Sugar Desk ERP · Generated from Frappe Database · Authorized Audit Copy
  </div>

  <script>
    window.onload = function() {
      setTimeout(function() {
        window.print();
      }, 300);
    };
  <\/script>
</body>
</html>`

  printWindow.document.open()
  printWindow.document.write(fullHtml)
  printWindow.document.close()
}
