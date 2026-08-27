# 🌾 STANDARD OPERATING PROCEDURE (SOP)
## Sugar Module & Sugar Desk ERP System

**Document Ref:** SOP-SM-2026-V1  
**Effective Date:** August 27, 2026  
**Company:** Rajendra Narahari Lokhande (Sugar Trading Division)  
**System Platform:** Frappe v16 + Sugar Desk Keyboard ERP  
**Target Audience:** Trade Operators, Dispatch Managers, Accounts Personnel, System Admins  

---

## 1. PURPOSE & SCOPE
This Standard Operating Procedure (SOP) defines the operational workflow for recording sugar procurement, allocating customer sales dispatches against specific mill purchase lots, processing supplier disbursements and broker receipts, tracking outstanding receivables/payables, and auditing financial ledgers in **Sugar Desk**.

---

## 2. ROLES & RESPONSIBILITIES

| Role | Designation | Key Responsibilities |
| :--- | :--- | :--- |
| **Trade Operator** | Data Entry / Procurement | Records Sugar Purchase contracts (<kbd>F9</kbd>) and verifies mill lot inwarding. |
| **Dispatch Manager** | Logistics / Sales | Issues Dispatch Entries (<kbd>F8</kbd>), verifies available lot stock, assigns vehicles & brokers. |
| **Accounts Executive** | Finance & Billing | Processes Supplier RTGS/NEFT Payments (<kbd>F5</kbd>) and Customer/Broker Receipts (<kbd>F6</kbd>). |
| **Finance Head / Auditor** | Audit & Control | Reviews Day Book (<kbd>F10</kbd>), monitors Broker Receivables (<kbd>O</kbd>) & Supplier Payables (<kbd>S</kbd>). |
| **System Administrator** | IT Operations | Maintains bench server availability, ports, user roles, and database backups. |

---

## 3. STEP-BY-STEP STANDARD OPERATING PROCEDURES

### SOP-01: Sugar Purchase Lot Inwarding (<kbd>F9</kbd> / <kbd>P</kbd>)
1. **Initiate Entry:** Press <kbd>F9</kbd> or <kbd>P</kbd> from the Gateway dashboard to open the **Sugar Purchase Voucher** screen.
2. **Date Selection:** Confirm or edit the Voucher Date.
3. **Supplier Selection:** In the **Supplier (Sugar Mill)** field, type the Mill Name (e.g. `Yedeshwari Sugar`) and select from dropdown.
4. **Item Grade:** Select the Sugar Grade Item (e.g. `M-30`, `S-30`, `SS-30`).
5. **Quantity & Rate:**
   - Enter **Purchase Qty (Quintals)**.
   - Enter **Purchase Rate (₹/Qtl)**.
   - Total Lot Amount is calculated automatically (`Qty * Rate`).
6. **Narration:** Enter contract terms, Sauda number, or delivery terms.
7. **Accept & Save:** Press <kbd>Enter</kbd> on narration or click **Save & Accept Voucher**.
8. **System Result:**
   - New `Sugar Purchase` document is created in Frappe.
   - `available_qty_quintal` is automatically initialized equal to the purchased quantity.

---

### SOP-02: Sugar Sales Dispatch & Lot Allocation (<kbd>F8</kbd> / <kbd>D</kbd>)
1. **Initiate Entry:** Press <kbd>F8</kbd> or <kbd>D</kbd> to open **Dispatch Entry Voucher**.
2. **Select Source Sugar Purchase Lot:**
   - In **Source Sugar Purchase**, start typing to search available lots.
   - Available lots appear in **descending order** with live stock tags (e.g. `[Stock: 3,800 Qtl]`).
   - Selecting a lot automatically loads the **Mill Name**, **Sugar Grade**, and **Available Stock Banner**.
3. **Customer Party & Broker:**
   - Enter/select the **Customer Party (Buyer)**.
   - Enter/select the **Broker Name**.
4. **Transport Details:**
   - Input the **Vehicle Number** (e.g. `MH19CZ1234`).
5. **Quantity & Rate:**
   - Enter **Dispatch Qty (Quintals)** (must not exceed available stock).
   - Enter **Sales Rate (₹/Qtl)**.
   - Total Dispatch Value and Balance Due are automatically calculated.
6. **Accept & Save:** Press <kbd>Enter</kbd> on narration to save.
7. **System Result:**
   - `Dispatch Entry` is generated with `balance_amount = total_amount`.
   - The source `Sugar Purchase` lot's `available_qty_quintal` is automatically reduced by the dispatched quantity.

---

### SOP-03: Supplier Disbursement / Purchase Payment (<kbd>F5</kbd> / <kbd>Y</kbd>)
1. **Initiate Entry:** Press <kbd>F5</kbd> or <kbd>Y</kbd> to open **Purchase Payment Voucher**.
2. **Select Source Purchase Lot:** Select the specific Sugar Purchase lot being paid.
   - Automatically populates the Supplier (Mill Name), Grade, and default Paid Amount.
3. **Select Bank/Cash Account:** Select your paying Bank or Cash account.
4. **Payment Mode & UTR:**
   - Select Payment Mode (`RTGS`, `NEFT`, `Cheque`, `UPI`, `Cash`).
   - Enter the Bank UTR / Cheque Reference Number.
5. **Confirm Amount:** Verify/adjust the **Paid Amount (₹)**.
6. **Accept & Save:** Press <kbd>Enter</kbd> on narration to record payment.
7. **System Result:** Updates the Sugar Purchase lot payment balance and reduces payable dues to that Sugar Mill.

---

### SOP-04: Customer / Broker Receipt Recording (<kbd>F6</kbd> / <kbd>R</kbd>)
1. **Initiate Entry:** Press <kbd>F6</kbd> or <kbd>R</kbd> to open **Broker Party Payment (Receipt)**.
2. **Select Source Dispatch Entry:**
   - Choose the Dispatch Entry voucher against which the buyer is paying.
   - Auto-populates Customer Party, Broker, and the exact remaining Balance Due.
3. **Deposit Account & UTR:**
   - Select receiving Bank Account.
   - Enter UTR / Cheque Number.
4. **Received Amount:** Enter the actual amount collected.
5. **Accept & Save:** Press <kbd>Enter</kbd> to complete.
6. **System Result:** Reduces customer balance due and updates broker ledger.

---

### SOP-05: Outstanding Receivables & Payables Monitoring
1. **Broker Receivables Report (<kbd>O</kbd>):**
   - Press <kbd>O</kbd> from Gateway or open `/register/broker-outstanding`.
   - Review KPI totals: Total Outstanding Due, Total Billed, Total Collected, Pending Vouchers.
   - Expand individual broker cards to view unpaid dispatches.
   - **Action:** Click **`🖨️ Print`** on any broker to generate a formal Statement of Account for collection, or click **`📥 CSV`** to export.
2. **Supplier Payables Report (<kbd>S</kbd>):**
   - Press <kbd>S</kbd> from Gateway or open `/register/supplier-outstanding`.
   - Review total money owed to sugar mills.
   - **Action:** Click **`🖨️ Print`** or **`📥 CSV`** on any sugar mill to view/export itemised unpaid purchase lots.

---

### SOP-06: Daily Audit & Day Book Reconciliation (<kbd>F10</kbd>)
1. **Open Day Book:** Press <kbd>F10</kbd> or click **Day Book** from Gateway.
2. **Date Filtering:** Press <kbd>F2</kbd> to filter transactions for a specific trading day.
3. **Type Filtering:** Press <kbd>F4</kbd> to isolate Purchases, Dispatches, Payments, or Receipts.
4. **Reconcile:** Verify that all debits and credits balance with bank statements.
5. **Print / Export:**
   - Press <kbd>F7</kbd> or click **`🖨️ Print Day Book`** for signed audit records.
   - Click **`📥 Export CSV`** to archive records into Excel.

---

### SOP-07: Viewing Existing Vouchers in Read-Only Mode
1. **Navigate to Register:** Press <kbd>L</kbd> for Purchases, <kbd>K</kbd> for Dispatches, <kbd>Y</kbd> for Payments, <kbd>R</kbd> for Receipts.
2. **Open Record:** Click or double-click any row in the register table.
3. **Read-Only Lock:**
   - Voucher opens with banner: `🔒 View Mode (Uneditable / Submitted) — {Voucher ID}`.
   - All fields are uneditable with zero dropdown menus appearing.
4. **Actions:**
   - Click **`🖨️ Print Voucher`** to generate a trade invoice/voucher copy.
   - Click **`➕ New Voucher`** to record a new transaction.
   - Press <kbd>Esc</kbd> to return to the Register list.

---

### SOP-08: Two-Way Navigation & ERPNext Interoperability
1. **Switching to ERPNext:** Click **`⚡ getMyErp`** on the top navigation bar (or type `getMyErp` in <kbd>Alt+G</kbd>) to navigate to `/desk/rajendra-narahari-lokhande`.
2. **Returning to Sugar Desk:** Inside ERPNext, click **`🌾 Sugar Desk`** on the top navbar or press <kbd>Alt+S</kbd>.

---

### SOP-09: Server Recovery & Troubleshooting
If the server encounters port conflicts or process locks:
```bash
# Clean all ports and restart bench in one command
/home/frappe/frappe-bench-v16/fix_bench.sh --start
```
If file permissions need verification:
```bash
chown -R frappe:frappe /home/frappe/frappe-bench-v16/
```

---

## 4. MASTER KEYBOARD SHORTCUT QUICK REFERENCE

| Key | Function | Scope |
| :---: | :--- | :--- |
| <kbd>Alt+G</kbd> / <kbd>Ctrl+K</kbd> | Tally **Go To** Command Search Palette | Universal |
| <kbd>F9</kbd> / <kbd>P</kbd> | New **Sugar Purchase** Voucher Entry | Universal / Gateway |
| <kbd>F8</kbd> / <kbd>D</kbd> | New **Dispatch Entry** Voucher | Universal / Gateway |
| <kbd>F5</kbd> / <kbd>Y</kbd> | New **Purchase Payment** (Supplier) | Universal / Gateway |
| <kbd>F6</kbd> / <kbd>R</kbd> | New **Broker Receipt** (Customer) | Universal / Gateway |
| <kbd>F4</kbd> | New **Contra** (Bank Transfer) | Universal / Gateway |
| <kbd>L</kbd> | Open **Sugar Purchases Register** | Gateway / Registers |
| <kbd>K</kbd> | Open **Dispatch Entries Register** | Gateway / Registers |
| <kbd>U</kbd> | Open **Sugar Mills / Suppliers Directory** | Gateway / Registers |
| <kbd>B</kbd> | Open **Sugar Brokers Directory** | Gateway / Registers |
| <kbd>C</kbd> | Open **Customer Parties Directory** | Gateway / Registers |
| <kbd>O</kbd> | Open **Broker Receivables Outstanding Report** | Universal / Gateway |
| <kbd>S</kbd> | Open **Supplier Payables Outstanding Report** | Universal / Gateway |
| <kbd>F10</kbd> | Open **Day Book & Audit Register** | Universal |
| <kbd>Esc</kbd> | Return to **Gateway / Register** | Universal |

---

## 5. DOCUMENT REVISION HISTORY

| Version | Date | Description of Change | Author / Approver |
| :--- | :--- | :--- | :--- |
| **v1.0** | 2026-08-27 | Initial standard operating procedure release | ERP Project Team |
