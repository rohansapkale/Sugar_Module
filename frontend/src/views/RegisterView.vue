<template>
  <div id="main-layout">
    <div id="content-area">
      <!-- Header with Action -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
        <div>
          <div class="v-title" style="margin-bottom: 2px;">{{ registerTitle }}</div>
          <div style="font-size: 12.5px; color: var(--muted);">Live accounting &amp; trade register directly synced with Frappe database</div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="searchPlaceholder"
            style="width: 230px; padding: 6px 10px; font-size: 13px; border: 1px solid var(--blue); border-radius: 4px; outline: none; background: var(--input-bg); color: var(--text);"
            @input="filterDebounce"
          />

          <!-- Global Print Button -->
          <button
            class="btn-tool"
            title="Print Current Register / Report"
            @click="printCurrentRegister"
          >
            <span>🖨️</span> Print
          </button>

          <!-- Global Export CSV Button -->
          <button
            class="btn-tool"
            title="Export Current Register to CSV"
            @click="exportCurrentRegisterCSV"
          >
            <span>📥</span> Export CSV
          </button>

          <!-- New Voucher Shortcut Button -->
          <button
            v-if="currentConfig.entryRoute"
            style="padding: 7px 14px; background: var(--blue); color: #fff; border: none; border-radius: 4px; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            @click="openNewEntry"
          >
            <span>➕</span> New {{ currentConfig.entryLabel }} (<kbd style="background: rgba(255,255,255,0.2); border: none; color: #fff;">{{ currentConfig.fkCode }}</kbd>)
          </button>
        </div>
      </div>

      <!-- KPI Summary Cards for Standard Registers -->
      <div v-if="summary && !['broker-outstanding', 'supplier-outstanding'].includes(registerType)" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 16px;">
        <div class="summary-card">
          <div class="sc-label">{{ countKpiLabel }}</div>
          <div class="sc-val">{{ summary.total_count || 0 }}</div>
        </div>
        <div v-if="summary.total_qty !== undefined && summary.total_qty > 0" class="summary-card">
          <div class="sc-label">{{ qtyKpiLabel }}</div>
          <div class="sc-val" style="color: var(--blue);">{{ formatNumber(summary.total_qty) }} <span style="font-size: 11px; font-weight: normal; color: var(--muted);">Qtl</span></div>
        </div>
        <div v-if="summary.total_available_qty !== undefined && ['supplier', 'purchase'].includes(registerType)" class="summary-card">
          <div class="sc-label">Available Stock (Qtl)</div>
          <div class="sc-val" style="color: var(--green);">{{ formatNumber(summary.total_available_qty) }} <span style="font-size: 11px; font-weight: normal; color: var(--muted);">Qtl</span></div>
        </div>
        <div v-if="summary.total_amount !== undefined && summary.total_amount > 0" class="summary-card">
          <div class="sc-label">{{ amountKpiLabel }}</div>
          <div class="sc-val" style="color: var(--navy);">₹{{ formatCurrency(summary.total_amount) }}</div>
        </div>
        <div v-if="summary.total_paid !== undefined" class="summary-card">
          <div class="sc-label">Total Paid (₹)</div>
          <div class="sc-val" style="color: var(--green);">₹{{ formatCurrency(summary.total_paid) }}</div>
        </div>
        <div v-if="summary.total_remaining !== undefined && summary.total_remaining > 0" class="summary-card">
          <div class="sc-label">Total Payable Due (₹)</div>
          <div class="sc-val" style="color: var(--red);">₹{{ formatCurrency(summary.total_remaining) }}</div>
        </div>
        <div v-if="summary.total_balance !== undefined && summary.total_balance > 0" class="summary-card">
          <div class="sc-label">Total Outstanding Due (₹)</div>
          <div class="sc-val" style="color: var(--amber);">₹{{ formatCurrency(summary.total_balance) }}</div>
        </div>
      </div>

      <!-- KPI Summary Cards for Outstanding Reports -->
      <div v-else-if="summary && ['broker-outstanding', 'supplier-outstanding'].includes(registerType)" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 18px;">
        <div class="summary-card" style="border-left: 4px solid var(--red);">
          <div class="sc-label" style="color: var(--red);">Total Outstanding Due</div>
          <div class="sc-val" style="color: var(--red); font-size: 20px;">₹{{ formatCurrency(summary.total_outstanding) }}</div>
        </div>
        <div class="summary-card" style="border-left: 4px solid var(--navy);">
          <div class="sc-label">Total Billed Value</div>
          <div class="sc-val" style="color: var(--navy); font-size: 19px;">₹{{ formatCurrency(summary.total_billed) }}</div>
        </div>
        <div class="summary-card" style="border-left: 4px solid var(--green);">
          <div class="sc-label">{{ registerType === 'broker-outstanding' ? 'Total Collected' : 'Total Paid' }}</div>
          <div class="sc-val" style="color: var(--green); font-size: 19px;">₹{{ formatCurrency(summary.total_received || summary.total_paid) }}</div>
        </div>
        <div class="summary-card" style="border-left: 4px solid var(--amber);">
          <div class="sc-label">Pending Vouchers</div>
          <div class="sc-val" style="color: var(--amber); font-size: 19px;">{{ summary.total_pending_vouchers || 0 }} Vouchers</div>
        </div>
      </div>

      <!-- 1. Sugar Purchase List Table -->
      <table v-if="registerType === 'purchase' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 15%;">Voucher No</th>
            <th style="width: 10%;">Date</th>
            <th style="width: 22%;">Supplier (Sugar Mill)</th>
            <th style="width: 10%;">Grade</th>
            <th style="width: 10%; text-align: right;">Qty (Qtl)</th>
            <th style="width: 9%; text-align: right;">Rate (₹)</th>
            <th style="width: 12%; text-align: right;">Total Amount</th>
            <th style="width: 12%; text-align: right;">Available Qty</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
            @dblclick="openVoucher(r)"
          >
            <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ r.name }}</td>
            <td>{{ r.purchase_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.supplier }}</td>
            <td><span class="code-badge">{{ r.item || 'S-30' }}</span></td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.purchase_qty_quintal) }}</td>
            <td style="text-align: right; font-family: monospace;">₹{{ formatNumber(r.purchase_rate) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--navy);">₹{{ formatCurrency(r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">{{ formatNumber(r.available_qty_quintal) }} Qtl</td>
          </tr>
        </tbody>
      </table>

      <!-- 2. Dispatch Entry List Table -->
      <table v-else-if="registerType === 'dispatch' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 14%;">Dispatch ID</th>
            <th style="width: 10%;">Date</th>
            <th style="width: 20%;">Customer Party</th>
            <th style="width: 16%;">Broker</th>
            <th style="width: 10%; text-align: right;">Qty (Qtl)</th>
            <th style="width: 10%; text-align: right;">Rate (₹)</th>
            <th style="width: 10%; text-align: right;">Total Amount</th>
            <th style="width: 10%; text-align: right;">Balance Due</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
            @dblclick="openVoucher(r)"
          >
            <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ r.name }}</td>
            <td>{{ r.dispatch_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.customer_name }}</td>
            <td>{{ r.broker || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.dispatch_qty_quintal) }}</td>
            <td style="text-align: right; font-family: monospace;">₹{{ formatNumber(r.rate) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--navy);">₹{{ formatCurrency(r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(r.balance_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 3. Purchase Payment Register -->
      <table v-else-if="registerType === 'payment' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 15%;">Payment ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 22%;">Supplier (Sugar Mill)</th>
            <th style="width: 18%;">Sugar Purchase Ref</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 12%;">UTR / Ref No.</th>
            <th style="width: 12%; text-align: right;">Paid Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
          >
            <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ r.name }}</td>
            <td>{{ r.payment_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.supplier }}</td>
            <td style="font-family: monospace; color: var(--blue);">{{ r.sugar_purchase || '—' }}</td>
            <td><span class="code-badge">{{ r.mode_of_payment || 'Bank' }}</span></td>
            <td style="font-family: monospace;">{{ r.reference_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.paid_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 4. Broker Receipt Register -->
      <table v-else-if="registerType === 'receipt' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 15%;">Receipt ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 22%;">Customer Party</th>
            <th style="width: 18%;">Dispatch Ref</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 12%;">UTR / Ref No.</th>
            <th style="width: 12%; text-align: right;">Received Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
          >
            <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ r.name }}</td>
            <td>{{ r.receipt_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.customer }}</td>
            <td style="font-family: monospace; color: var(--blue);">{{ r.dispatch_entry || '—' }}</td>
            <td><span class="code-badge">{{ r.mode_of_payment || 'Bank' }}</span></td>
            <td style="font-family: monospace;">{{ r.reference_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.received_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 5. SUPPLIERS (SUGAR MILLS) REGISTER -->
      <table v-else-if="registerType === 'supplier' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 28%;">Sugar Mill (Supplier Name)</th>
            <th style="width: 14%;">Group / Type</th>
            <th style="width: 12%; text-align: right;">Total Lots</th>
            <th style="width: 15%; text-align: right;">Total Purchase Qty (Qtl)</th>
            <th style="width: 16%; text-align: right;">Total Purchases</th>
            <th style="width: 15%; text-align: right;">Available Stock</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
            @dblclick="openVoucher(r)"
          >
            <td style="font-weight: 700; color: var(--navy);">{{ r.supplier_name || r.name }}</td>
            <td><span class="code-badge">{{ r.supplier_group || 'Sugar Mill' }}</span></td>
            <td style="text-align: right; font-family: monospace;">{{ r.total_lots || 0 }} Lots</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--blue);">{{ formatNumber(r.total_purchase_qty || r.total_qty) }} Qtl</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700;">₹{{ formatCurrency(r.total_purchase_amount || r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">{{ formatNumber(r.available_stock) }} Qtl</td>
          </tr>
        </tbody>
      </table>

      <!-- 6. BROKERS REGISTER -->
      <table v-else-if="registerType === 'broker' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 25%;">Broker Name</th>
            <th style="width: 14%;">Mobile No</th>
            <th style="width: 14%;">City / State</th>
            <th style="width: 12%; text-align: right;">Total Dispatches</th>
            <th style="width: 15%; text-align: right;">Total Sold (Qtl)</th>
            <th style="width: 18%; text-align: right;">Total Sales Val (₹)</th>
            <th style="width: 16%; text-align: right;">Pending Balance (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
            @dblclick="openVoucher(r)"
          >
            <td style="font-weight: 700; color: var(--navy);">{{ r.broker_name || r.name }}</td>
            <td style="font-family: monospace;">{{ r.mobile_no || '—' }}</td>
            <td>{{ r.city || r.state || '—' }}</td>
            <td style="text-align: right; font-family: monospace;">{{ r.total_dispatches || 0 }} Dispatches</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--blue);">{{ formatNumber(r.total_sold_qty || r.total_qty) }} Qtl</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700;">₹{{ formatCurrency(r.total_sold_amount || r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(r.total_balance) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 7. CUSTOMERS REGISTER -->
      <table v-else-if="registerType === 'customer' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 30%;">Customer Party Name</th>
            <th style="width: 18%;">Group / Territory</th>
            <th style="width: 14%; text-align: right;">Total Dispatches</th>
            <th style="width: 16%; text-align: right;">Total Sold (Qtl)</th>
            <th style="width: 18%; text-align: right;">Total Sales Val (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
            @dblclick="openVoucher(r)"
          >
            <td style="font-weight: 700; color: var(--navy);">{{ r.customer_name || r.name }}</td>
            <td><span class="code-badge">{{ r.customer_group || r.territory || 'Customer Party' }}</span></td>
            <td style="text-align: right; font-family: monospace;">{{ r.total_dispatches || 0 }} Dispatches</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--blue);">{{ formatNumber(r.total_sold_qty || r.total_qty) }} Qtl</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700;">₹{{ formatCurrency(r.total_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 8. BROKER OUTSTANDING (RECEIVABLES) REPORT -->
      <div v-else-if="registerType === 'broker-outstanding' && groups.length">
        <div v-for="(g, gIdx) in groups" :key="g.broker_id || gIdx" style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; margin-bottom: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
          <!-- Broker Group Header -->
          <div style="background: var(--panel-soft); padding: 12px 16px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-size: 15px; font-weight: 700; color: var(--navy);">🤝 Broker: {{ g.broker_name }}</span>
              <span v-if="g.broker_mobile" style="font-size: 12px; color: var(--muted); margin-left: 10px;">📞 {{ g.broker_mobile }}</span>
              <span style="font-size: 12px; color: var(--muted); margin-left: 10px;">({{ g.total_dispatches }} Dispatches · {{ formatNumber(g.total_qty) }} Qtl)</span>
            </div>
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
              <span style="font-size: 12px; color: var(--muted);">Billed: <b>₹{{ formatCurrency(g.total_billed) }}</b></span>
              <span style="font-size: 12px; color: var(--green);">Received: <b>₹{{ formatCurrency(g.total_received) }}</b></span>
              <span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 700;">
                Due: ₹{{ formatCurrency(g.total_pending) }}
              </span>

              <!-- Individual Broker Actions: Print & CSV -->
              <button
                class="btn-action-small"
                title="Print Statement for this Broker"
                @click.stop="printBrokerStatement(g)"
              >
                🖨️ Print
              </button>
              <button
                class="btn-action-small"
                title="Export this Broker's Dispatches to CSV"
                @click.stop="exportBrokerCSV(g)"
              >
                📥 CSV
              </button>
            </div>
          </div>

          <!-- Pending Vouchers Table inside Group -->
          <table v-if="g.pending_vouchers && g.pending_vouchers.length" class="daybook-table" style="margin: 0;">
            <thead>
              <tr style="background: var(--panel);">
                <th style="width: 16%;">Dispatch No.</th>
                <th style="width: 11%;">Date</th>
                <th style="width: 25%;">Customer (Buyer)</th>
                <th style="width: 12%; text-align: right;">Qty (Qtl)</th>
                <th style="width: 12%; text-align: right;">Total Amount</th>
                <th style="width: 12%; text-align: right;">Received</th>
                <th style="width: 12%; text-align: right;">Balance Due</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pv in g.pending_vouchers" :key="pv.name" class="daybook-row">
                <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ pv.name }}</td>
                <td>{{ pv.dispatch_date || '—' }}</td>
                <td style="font-weight: 600;">{{ pv.customer_name }}</td>
                <td style="text-align: right; font-family: monospace;">{{ formatNumber(pv.dispatch_qty_quintal) }}</td>
                <td style="text-align: right; font-family: monospace;">₹{{ formatCurrency(pv.total_amount) }}</td>
                <td style="text-align: right; font-family: monospace; color: var(--green);">₹{{ formatCurrency(pv.paid_amount) }}</td>
                <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(pv.balance_amount) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else style="padding: 12px; text-align: center; color: var(--green); font-size: 12.5px; background: #f0fdf4;">
            ✔ All dispatches under this broker are fully paid &amp; settled!
          </div>
        </div>
      </div>

      <!-- 9. SUPPLIER OUTSTANDING (PAYABLES) REPORT -->
      <div v-else-if="registerType === 'supplier-outstanding' && groups.length">
        <div v-for="(g, gIdx) in groups" :key="g.supplier_id || gIdx" style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; margin-bottom: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
          <!-- Supplier Group Header -->
          <div style="background: var(--panel-soft); padding: 12px 16px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
              <span style="font-size: 15px; font-weight: 700; color: var(--navy);">🏭 Mill / Supplier: {{ g.supplier_name }}</span>
              <span style="font-size: 12px; color: var(--muted); margin-left: 10px;">({{ g.total_purchases }} Lots · {{ formatNumber(g.total_qty) }} Qtl)</span>
            </div>
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
              <span style="font-size: 12px; color: var(--muted);">Purchased: <b>₹{{ formatCurrency(g.total_billed) }}</b></span>
              <span style="font-size: 12px; color: var(--green);">Paid: <b>₹{{ formatCurrency(g.total_paid) }}</b></span>
              <span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 700;">
                Payable: ₹{{ formatCurrency(g.total_pending) }}
              </span>

              <!-- Individual Supplier Actions: Print & CSV -->
              <button
                class="btn-action-small"
                title="Print Statement for this Mill"
                @click.stop="printSupplierStatement(g)"
              >
                🖨️ Print
              </button>
              <button
                class="btn-action-small"
                title="Export this Mill's Lots to CSV"
                @click.stop="exportSupplierCSV(g)"
              >
                📥 CSV
              </button>
            </div>
          </div>

          <!-- Pending Lots Table inside Group -->
          <table v-if="g.pending_vouchers && g.pending_vouchers.length" class="daybook-table" style="margin: 0;">
            <thead>
              <tr style="background: var(--panel);">
                <th style="width: 18%;">Purchase Lot ID</th>
                <th style="width: 11%;">Date</th>
                <th style="width: 12%;">Grade</th>
                <th style="width: 12%; text-align: right;">Qty (Qtl)</th>
                <th style="width: 15%; text-align: right;">Lot Value</th>
                <th style="width: 15%; text-align: right;">Paid Amount</th>
                <th style="width: 17%; text-align: right;">Payable Balance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pv in g.pending_vouchers" :key="pv.name" class="daybook-row">
                <td style="font-family: monospace; font-weight: 700; color: var(--navy);">{{ pv.name }}</td>
                <td>{{ pv.purchase_date || '—' }}</td>
                <td><span class="code-badge">{{ pv.item || 'S-30' }}</span></td>
                <td style="text-align: right; font-family: monospace;">{{ formatNumber(pv.purchase_qty_quintal) }}</td>
                <td style="text-align: right; font-family: monospace;">₹{{ formatCurrency(pv.total_amount) }}</td>
                <td style="text-align: right; font-family: monospace; color: var(--green);">₹{{ formatCurrency(pv.paid_amount) }}</td>
                <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(pv.balance_amount) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else style="padding: 12px; text-align: center; color: var(--green); font-size: 12.5px; background: #f0fdf4;">
            ✔ All purchase lots for this sugar mill are fully paid &amp; settled!
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!records.length && !groups.length" style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 30px; text-align: center; color: var(--muted); margin-top: 20px;">
        <div style="font-size: 28px; margin-bottom: 8px;">📭</div>
        <p style="font-size: 14px; margin-bottom: 6px;">No records found for {{ registerTitle }}</p>
        <p style="font-size: 12.5px;">Click "New {{ currentConfig.entryLabel }}" or press <kbd>{{ currentConfig.fkCode }}</kbd> to record a new transaction.</p>
      </div>

      <!-- Bottom Hint Bar -->
      <div class="keyboard-hint" style="margin-top: 18px;">
        <span><kbd>↑</kbd> <kbd>↓</kbd> Select Row</span>
        <span><kbd>Enter</kbd> Open Voucher</span>
        <span><kbd>Esc</kbd> Return to Gateway</span>
        <span><kbd>Alt+G</kbd> Go To Search</span>
      </div>
    </div>

    <!-- Right Side Menu -->
    <MenuPanel
      section-title="Trade Registers"
      :items="registerMenuItems"
      :active-index="activeMenuIndex"
      @select="handleMenuSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import { downloadCSV, printFormattedHtml } from '../composables/useExport'
import MenuPanel from '../components/common/MenuPanel.vue'

const route = useRoute()
const router = useRouter()
const { getRegisterData, bootState } = useFrappeApi()

const registerType = computed(() => route.params.type || 'purchase')

const REGISTER_CONFIGS = {
  purchase: {
    voucherType: 'Sugar Purchase',
    title: 'Sugar Purchase Register (Lots)',
    entryLabel: 'Purchase Entry',
    entryRoute: '/voucher/purchase',
    fkCode: 'P',
  },
  dispatch: {
    voucherType: 'Dispatch Entry',
    title: 'Dispatch Entry Register (Sales / Deliveries)',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'D',
  },
  payment: {
    voucherType: 'Purchase Payment',
    title: 'Purchase Payment Register (Suppliers)',
    entryLabel: 'Payment Entry',
    entryRoute: '/voucher/payment',
    fkCode: 'Y',
  },
  receipt: {
    voucherType: 'Broker Party Payment',
    title: 'Broker Party Payment Register (Receipts)',
    entryLabel: 'Receipt Entry',
    entryRoute: '/voucher/receipt',
    fkCode: 'R',
  },
  supplier: {
    voucherType: 'Supplier',
    title: 'Sugar Mills / Suppliers Directory',
    entryLabel: 'Purchase Entry',
    entryRoute: '/voucher/purchase',
    fkCode: 'P',
  },
  broker: {
    voucherType: 'Broker',
    title: 'Sugar Brokers Directory',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'D',
  },
  customer: {
    voucherType: 'Customer',
    title: 'Customer Parties Directory',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'D',
  },
  'broker-outstanding': {
    voucherType: 'broker-outstanding',
    title: 'Broker / Customer Outstanding Receivables Report',
    entryLabel: 'Receipt Entry',
    entryRoute: '/voucher/receipt',
    fkCode: 'R',
  },
  'supplier-outstanding': {
    voucherType: 'supplier-outstanding',
    title: 'Supplier / Mill Outstanding Payables Report',
    entryLabel: 'Payment Entry',
    entryRoute: '/voucher/payment',
    fkCode: 'Y',
  },
}

const currentConfig = computed(() => REGISTER_CONFIGS[registerType.value] || REGISTER_CONFIGS.purchase)
const registerTitle = computed(() => currentConfig.value.title)
const companyName = computed(() => bootState.default_company || 'Mahalaxmi Sugar Mills Pvt. Ltd.')

const searchPlaceholder = computed(() => {
  switch (registerType.value) {
    case 'supplier': return 'Search Supplier...'
    case 'broker': return 'Search Broker...'
    case 'customer': return 'Search Customer Party...'
    case 'purchase': return 'Search Purchase Lot / Mill...'
    case 'dispatch': return 'Search Dispatch / Customer / Broker...'
    case 'payment': return 'Search Payment / Supplier...'
    case 'receipt': return 'Search Receipt / Customer / Broker...'
    case 'broker-outstanding': return 'Search Broker / Outstanding...'
    case 'supplier-outstanding': return 'Search Supplier / Payable...'
    default: return 'Search party, broker, voucher...'
  }
})

const countKpiLabel = computed(() => {
  switch (registerType.value) {
    case 'supplier': return 'Total Suppliers / Mills'
    case 'broker': return 'Total Brokers'
    case 'customer': return 'Total Customers'
    case 'purchase': return 'Total Purchase Lots'
    case 'dispatch': return 'Total Dispatches'
    case 'payment': return 'Total Payments'
    case 'receipt': return 'Total Receipts'
    default: return 'Total Records'
  }
})

const qtyKpiLabel = computed(() => {
  switch (registerType.value) {
    case 'supplier':
    case 'purchase':
      return 'Total Purchase Qty (Qtl)'
    case 'broker':
    case 'dispatch':
    case 'customer':
      return 'Total Sold Qty (Qtl)'
    default:
      return 'Total Qty (Qtl)'
  }
})

const amountKpiLabel = computed(() => {
  switch (registerType.value) {
    case 'supplier':
    case 'purchase':
      return 'Total Purchase Val (₹)'
    case 'broker':
    case 'dispatch':
    case 'customer':
      return 'Total Sales Val (₹)'
    default:
      return 'Total Amount (₹)'
  }
})

const records = ref([])
const groups = ref([])
const summary = ref({})
const activeRowIndex = ref(0)
const activeMenuIndex = ref(0)
const searchQuery = ref('')
let searchTimer = null

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (val) => {
  return Number(val || 0).toLocaleString('en-IN')
}

const loadData = async () => {
  const res = await getRegisterData(currentConfig.value.voucherType, searchQuery.value)
  if (res) {
    records.value = res.records || []
    groups.value = res.groups || []
    summary.value = res.summary || {}
    if (activeRowIndex.value >= records.value.length) {
      activeRowIndex.value = Math.max(0, records.value.length - 1)
    }
  }
}

const filterDebounce = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadData()
  }, 120)
}

watch(registerType, () => {
  searchQuery.value = ''
  loadData()
})

const openNewEntry = () => {
  const sel = records.value[activeRowIndex.value]
  if (registerType.value === 'broker') {
    const brokerName = sel ? (sel.broker_name || sel.name) : ''
    router.push({
      path: '/voucher/dispatch',
      query: brokerName ? { broker: brokerName } : {}
    })
  } else if (registerType.value === 'supplier') {
    const supplierName = sel ? (sel.supplier_name || sel.name) : ''
    router.push({
      path: '/voucher/purchase',
      query: supplierName ? { supplier: supplierName } : {}
    })
  } else if (registerType.value === 'customer') {
    const custName = sel ? (sel.customer_name || sel.name) : ''
    router.push({
      path: '/voucher/dispatch',
      query: custName ? { customer: custName } : {}
    })
  } else if (currentConfig.value.entryRoute) {
    router.push(currentConfig.value.entryRoute)
  }
}

const openVoucher = (row) => {
  if (!row || !row.name) return
  if (registerType.value === 'purchase') {
    showToast(`Opening ${row.name} (View Mode)`)
    router.push({ path: '/voucher/purchase', query: { id: row.name } })
  } else if (registerType.value === 'dispatch') {
    showToast(`Opening ${row.name} (View Mode)`)
    router.push({ path: '/voucher/dispatch', query: { id: row.name } })
  } else if (registerType.value === 'payment') {
    showToast(`Opening ${row.name} (View Mode)`)
    router.push({ path: '/voucher/payment', query: { id: row.name } })
  } else if (registerType.value === 'receipt') {
    showToast(`Opening ${row.name} (View Mode)`)
    router.push({ path: '/voucher/receipt', query: { id: row.name } })
  } else if (registerType.value === 'broker') {
    const bName = row.broker_name || row.name
    showToast(`Creating New Dispatch for Broker: ${bName}`)
    router.push({ path: '/voucher/dispatch', query: { broker: bName } })
  } else if (registerType.value === 'supplier') {
    const sName = row.supplier_name || row.name
    showToast(`Creating New Purchase from Supplier: ${sName}`)
    router.push({ path: '/voucher/purchase', query: { supplier: sName } })
  } else if (registerType.value === 'customer') {
    const cName = row.customer_name || row.name
    showToast(`Creating New Dispatch for Customer: ${cName}`)
    router.push({ path: '/voucher/dispatch', query: { customer: cName } })
  }
}

// -------------------------------------------------------------
// INDIVIDUAL BROKER EXPORT & PRINT (RECEIVABLES)
// -------------------------------------------------------------
const printBrokerStatement = (g) => {
  const rowsHtml = (g.pending_vouchers || []).map((pv) => `
    <tr>
      <td class="font-mono font-bold">${pv.name}</td>
      <td>${pv.dispatch_date || '—'}</td>
      <td class="font-bold">${pv.customer_name || '—'}</td>
      <td class="text-right font-mono">${formatNumber(pv.dispatch_qty_quintal)}</td>
      <td class="text-right font-mono">₹${formatCurrency(pv.total_amount)}</td>
      <td class="text-right font-mono val-green">₹${formatCurrency(pv.paid_amount)}</td>
      <td class="text-right font-mono font-bold val-red">₹${formatCurrency(pv.balance_amount)}</td>
    </tr>
  `).join('')

  const html = `
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
      <div style="font-size: 16px; font-weight: bold; color: #0f172a;">🤝 Broker: ${g.broker_name}</div>
      <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
        ${g.broker_mobile ? '📞 Mobile: ' + g.broker_mobile + ' · ' : ''}
        Total Dispatches: ${g.total_dispatches} · Total Quantity: ${formatNumber(g.total_qty)} Quintal
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-row">
        <div class="kpi-box" style="border-left: 4px solid #b91c1c;">
          <div class="kpi-label">Outstanding Due</div>
          <div class="kpi-val val-red">₹${formatCurrency(g.total_pending)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #0f172a;">
          <div class="kpi-label">Total Invoiced / Billed</div>
          <div class="kpi-val val-navy">₹${formatCurrency(g.total_billed)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #15803d;">
          <div class="kpi-label">Total Collected / Paid</div>
          <div class="kpi-val val-green">₹${formatCurrency(g.total_received)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #d97706;">
          <div class="kpi-label">Pending Invoices</div>
          <div class="kpi-val">${g.pending_vouchers ? g.pending_vouchers.length : 0} Vouchers</div>
        </div>
      </div>
    </div>

    <h3 style="font-size: 13px; color: #0f172a; margin-top: 18px; margin-bottom: 6px;">Itemized Pending Dispatch Entries</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 16%;">Dispatch No.</th>
          <th style="width: 12%;">Date</th>
          <th style="width: 24%;">Customer (Buyer)</th>
          <th style="width: 12%; text-align: right;">Qty (Qtl)</th>
          <th style="width: 12%; text-align: right;">Billed (₹)</th>
          <th style="width: 12%; text-align: right;">Received (₹)</th>
          <th style="width: 12%; text-align: right;">Balance Due (₹)</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml || '<tr><td colspan="7" class="text-center">All dispatches settled</td></tr>'}
      </tbody>
    </table>
  `

  printFormattedHtml(`Broker Outstanding Statement — ${g.broker_name}`, html, companyName.value)
}

const exportBrokerCSV = (g) => {
  const headers = ['Dispatch ID', 'Date', 'Customer Party', 'Broker Name', 'Qty (Quintal)', 'Total Billed (INR)', 'Received Amount (INR)', 'Balance Due (INR)']
  const rows = [headers]

  ;(g.pending_vouchers || []).forEach((pv) => {
    rows.push([
      pv.name,
      pv.dispatch_date || '',
      pv.customer_name || '',
      g.broker_name || '',
      pv.dispatch_qty_quintal || 0,
      pv.total_amount || 0,
      pv.paid_amount || 0,
      pv.balance_amount || 0,
    ])
  })

  // Summary Row
  rows.push([])
  rows.push(['TOTALS', '', '', '', g.total_qty || 0, g.total_billed || 0, g.total_received || 0, g.total_pending || 0])

  const safeName = (g.broker_name || 'Broker').replace(/[^a-zA-Z0-9_-]/g, '_')
  const dateStr = new Date().toISOString().slice(0, 10)
  downloadCSV(`Broker_Statement_${safeName}_${dateStr}.csv`, rows)
  showToast(`Exported CSV for Broker: ${g.broker_name}`)
}

// -------------------------------------------------------------
// INDIVIDUAL SUPPLIER EXPORT & PRINT (PAYABLES)
// -------------------------------------------------------------
const printSupplierStatement = (g) => {
  const rowsHtml = (g.pending_vouchers || []).map((pv) => `
    <tr>
      <td class="font-mono font-bold">${pv.name}</td>
      <td>${pv.purchase_date || '—'}</td>
      <td>${pv.item || 'S-30'}</td>
      <td class="text-right font-mono">${formatNumber(pv.purchase_qty_quintal)}</td>
      <td class="text-right font-mono">₹${formatCurrency(pv.total_amount)}</td>
      <td class="text-right font-mono val-green">₹${formatCurrency(pv.paid_amount)}</td>
      <td class="text-right font-mono font-bold val-red">₹${formatCurrency(pv.balance_amount)}</td>
    </tr>
  `).join('')

  const html = `
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px;">
      <div style="font-size: 16px; font-weight: bold; color: #0f172a;">🏭 Sugar Mill / Supplier: ${g.supplier_name}</div>
      <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
        Total Purchase Lots: ${g.total_purchases} · Total Quantity: ${formatNumber(g.total_qty)} Quintal
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-row">
        <div class="kpi-box" style="border-left: 4px solid #b91c1c;">
          <div class="kpi-label">Payable Due</div>
          <div class="kpi-val val-red">₹${formatCurrency(g.total_pending)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #0f172a;">
          <div class="kpi-label">Total Purchased Value</div>
          <div class="kpi-val val-navy">₹${formatCurrency(g.total_billed)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #15803d;">
          <div class="kpi-label">Total Paid Amount</div>
          <div class="kpi-val val-green">₹${formatCurrency(g.total_paid)}</div>
        </div>
        <div class="kpi-box" style="border-left: 4px solid #d97706;">
          <div class="kpi-label">Unpaid Lots</div>
          <div class="kpi-val">${g.pending_vouchers ? g.pending_vouchers.length : 0} Lots</div>
        </div>
      </div>
    </div>

    <h3 style="font-size: 13px; color: #0f172a; margin-top: 18px; margin-bottom: 6px;">Itemized Pending Purchase Lots</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 18%;">Purchase Lot ID</th>
          <th style="width: 12%;">Date</th>
          <th style="width: 12%;">Grade</th>
          <th style="width: 12%; text-align: right;">Qty (Qtl)</th>
          <th style="width: 15%; text-align: right;">Lot Value (₹)</th>
          <th style="width: 15%; text-align: right;">Paid (₹)</th>
          <th style="width: 16%; text-align: right;">Payable Balance (₹)</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml || '<tr><td colspan="7" class="text-center">All purchase lots settled</td></tr>'}
      </tbody>
    </table>
  `

  printFormattedHtml(`Supplier Outstanding Statement — ${g.supplier_name}`, html, companyName.value)
}

const exportSupplierCSV = (g) => {
  const headers = ['Purchase Lot ID', 'Date', 'Supplier / Mill', 'Grade Item', 'Qty (Quintal)', 'Total Value (INR)', 'Paid Amount (INR)', 'Payable Balance (INR)']
  const rows = [headers]

  ;(g.pending_vouchers || []).forEach((pv) => {
    rows.push([
      pv.name,
      pv.purchase_date || '',
      g.supplier_name || '',
      pv.item || 'S-30',
      pv.purchase_qty_quintal || 0,
      pv.total_amount || 0,
      pv.paid_amount || 0,
      pv.balance_amount || 0,
    ])
  })

  // Summary Row
  rows.push([])
  rows.push(['TOTALS', '', '', '', g.total_qty || 0, g.total_billed || 0, g.total_paid || 0, g.total_pending || 0])

  const safeName = (g.supplier_name || 'Supplier').replace(/[^a-zA-Z0-9_-]/g, '_')
  const dateStr = new Date().toISOString().slice(0, 10)
  downloadCSV(`Supplier_Statement_${safeName}_${dateStr}.csv`, rows)
  showToast(`Exported CSV for Mill: ${g.supplier_name}`)
}

// -------------------------------------------------------------
// GLOBAL PRINT & CSV EXPORT FOR CURRENT REGISTER / REPORT
// -------------------------------------------------------------
const printCurrentRegister = () => {
  if (registerType.value === 'broker-outstanding') {
    // Print full grouped broker receivables
    const groupsHtml = groups.value.map((g) => {
      const vRows = (g.pending_vouchers || []).map((pv) => `
        <tr>
          <td class="font-mono">${pv.name}</td>
          <td>${pv.dispatch_date || '—'}</td>
          <td>${pv.customer_name || '—'}</td>
          <td class="text-right font-mono">${formatNumber(pv.dispatch_qty_quintal)}</td>
          <td class="text-right font-mono">₹${formatCurrency(pv.total_amount)}</td>
          <td class="text-right font-mono val-green">₹${formatCurrency(pv.paid_amount)}</td>
          <td class="text-right font-mono val-red font-bold">₹${formatCurrency(pv.balance_amount)}</td>
        </tr>
      `).join('')

      return `
        <div style="margin-top: 14px; border: 1px solid #cbd5e1; border-radius: 4px; overflow: hidden;">
          <div style="background: #f1f5f9; padding: 6px 10px; font-weight: bold; display: flex; justify-content: space-between;">
            <span>🤝 Broker: ${g.broker_name} (${g.total_dispatches} Dispatches · ${formatNumber(g.total_qty)} Qtl)</span>
            <span class="val-red">Due: ₹${formatCurrency(g.total_pending)}</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Dispatch No</th>
                <th>Date</th>
                <th>Customer</th>
                <th class="text-right">Qty</th>
                <th class="text-right">Billed</th>
                <th class="text-right">Received</th>
                <th class="text-right">Balance Due</th>
              </tr>
            </thead>
            <tbody>${vRows || '<tr><td colspan="7" class="text-center">All settled</td></tr>'}</tbody>
          </table>
        </div>
      `
    }).join('')

    const html = `
      <div class="kpi-grid">
        <div class="kpi-row">
          <div class="kpi-box" style="border-left: 4px solid #b91c1c;">
            <div class="kpi-label">Total Outstanding Due</div>
            <div class="kpi-val val-red">₹${formatCurrency(summary.value.total_outstanding)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #0f172a;">
            <div class="kpi-label">Total Billed</div>
            <div class="kpi-val val-navy">₹${formatCurrency(summary.value.total_billed)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #15803d;">
            <div class="kpi-label">Total Collected</div>
            <div class="kpi-val val-green">₹${formatCurrency(summary.value.total_received)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #d97706;">
            <div class="kpi-label">Pending Vouchers</div>
            <div class="kpi-val">${summary.value.total_pending_vouchers || 0}</div>
          </div>
        </div>
      </div>
      ${groupsHtml}
    `
    printFormattedHtml(registerTitle.value, html, companyName.value)
    return
  }

  if (registerType.value === 'supplier-outstanding') {
    const groupsHtml = groups.value.map((g) => {
      const vRows = (g.pending_vouchers || []).map((pv) => `
        <tr>
          <td class="font-mono">${pv.name}</td>
          <td>${pv.purchase_date || '—'}</td>
          <td>${pv.item || 'S-30'}</td>
          <td class="text-right font-mono">${formatNumber(pv.purchase_qty_quintal)}</td>
          <td class="text-right font-mono">₹${formatCurrency(pv.total_amount)}</td>
          <td class="text-right font-mono val-green">₹${formatCurrency(pv.paid_amount)}</td>
          <td class="text-right font-mono val-red font-bold">₹${formatCurrency(pv.balance_amount)}</td>
        </tr>
      `).join('')

      return `
        <div style="margin-top: 14px; border: 1px solid #cbd5e1; border-radius: 4px; overflow: hidden;">
          <div style="background: #f1f5f9; padding: 6px 10px; font-weight: bold; display: flex; justify-content: space-between;">
            <span>🏭 Mill: ${g.supplier_name} (${g.total_purchases} Lots · ${formatNumber(g.total_qty)} Qtl)</span>
            <span class="val-red">Payable: ₹${formatCurrency(g.total_pending)}</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Lot ID</th>
                <th>Date</th>
                <th>Grade</th>
                <th class="text-right">Qty</th>
                <th class="text-right">Value</th>
                <th class="text-right">Paid</th>
                <th class="text-right">Payable Balance</th>
              </tr>
            </thead>
            <tbody>${vRows || '<tr><td colspan="7" class="text-center">All settled</td></tr>'}</tbody>
          </table>
        </div>
      `
    }).join('')

    const html = `
      <div class="kpi-grid">
        <div class="kpi-row">
          <div class="kpi-box" style="border-left: 4px solid #b91c1c;">
            <div class="kpi-label">Total Outstanding Payables</div>
            <div class="kpi-val val-red">₹${formatCurrency(summary.value.total_outstanding)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #0f172a;">
            <div class="kpi-label">Total Purchased</div>
            <div class="kpi-val val-navy">₹${formatCurrency(summary.value.total_billed)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #15803d;">
            <div class="kpi-label">Total Paid</div>
            <div class="kpi-val val-green">₹${formatCurrency(summary.value.total_paid)}</div>
          </div>
          <div class="kpi-box" style="border-left: 4px solid #d97706;">
            <div class="kpi-label">Unpaid Lots</div>
            <div class="kpi-val">${summary.value.total_pending_vouchers || 0}</div>
          </div>
        </div>
      </div>
      ${groupsHtml}
    `
    printFormattedHtml(registerTitle.value, html, companyName.value)
    return
  }

  // Standard Flat Registers
  let rowsHtml = ''
  let tableHeaders = ''

  if (registerType.value === 'purchase') {
    tableHeaders = '<th>Voucher No</th><th>Date</th><th>Supplier (Mill)</th><th>Grade</th><th class="text-right">Qty (Qtl)</th><th class="text-right">Rate (₹)</th><th class="text-right">Total (₹)</th><th class="text-right">Available Qtl</th>'
    rowsHtml = records.value.map(r => `<tr><td class="font-mono font-bold">${r.name}</td><td>${r.purchase_date || '—'}</td><td>${r.supplier}</td><td>${r.item || 'S-30'}</td><td class="text-right font-mono">${formatNumber(r.purchase_qty_quintal)}</td><td class="text-right font-mono">₹${formatNumber(r.purchase_rate)}</td><td class="text-right font-mono font-bold">₹${formatCurrency(r.total_amount)}</td><td class="text-right font-mono val-green font-bold">${formatNumber(r.available_qty_quintal)}</td></tr>`).join('')
  } else if (registerType.value === 'dispatch') {
    tableHeaders = '<th>Dispatch ID</th><th>Date</th><th>Customer</th><th>Broker</th><th class="text-right">Qty (Qtl)</th><th class="text-right">Rate (₹)</th><th class="text-right">Total (₹)</th><th class="text-right">Balance Due (₹)</th>'
    rowsHtml = records.value.map(r => `<tr><td class="font-mono font-bold">${r.name}</td><td>${r.dispatch_date || '—'}</td><td>${r.customer_name}</td><td>${r.broker || '—'}</td><td class="text-right font-mono">${formatNumber(r.dispatch_qty_quintal)}</td><td class="text-right font-mono">₹${formatNumber(r.rate)}</td><td class="text-right font-mono font-bold">₹${formatCurrency(r.total_amount)}</td><td class="text-right font-mono val-red font-bold">₹${formatCurrency(r.balance_amount)}</td></tr>`).join('')
  } else if (registerType.value === 'supplier') {
    tableHeaders = '<th>Sugar Mill Name</th><th>Group</th><th class="text-right">Lots</th><th class="text-right">Total Qty (Qtl)</th><th class="text-right">Total Purchases (₹)</th><th class="text-right">Stock (Qtl)</th>'
    rowsHtml = records.value.map(r => `<tr><td class="font-bold">${r.supplier_name || r.name}</td><td>${r.supplier_group || 'Sugar Mill'}</td><td class="text-right font-mono">${r.total_lots}</td><td class="text-right font-mono">${formatNumber(r.total_qty)}</td><td class="text-right font-mono font-bold">₹${formatCurrency(r.total_amount)}</td><td class="text-right font-mono val-green font-bold">${formatNumber(r.available_stock)}</td></tr>`).join('')
  } else if (registerType.value === 'broker') {
    tableHeaders = '<th>Broker ID</th><th>Broker Name</th><th>Mobile</th><th>City</th><th class="text-right">Dispatches Qtl</th><th class="text-right">Pending Due (₹)</th>'
    rowsHtml = records.value.map(r => `<tr><td class="font-mono font-bold">${r.name}</td><td class="font-bold">${r.broker_name || r.name}</td><td class="font-mono">${r.mobile_no || '—'}</td><td>${r.city || '—'}</td><td class="text-right font-mono">${formatNumber(r.total_qty)}</td><td class="text-right font-mono val-red font-bold">₹${formatCurrency(r.total_balance)}</td></tr>`).join('')
  } else {
    tableHeaders = '<th>Voucher No</th><th>Date</th><th>Party / Ledger</th><th>Mode</th><th class="text-right">Amount (₹)</th>'
    rowsHtml = records.value.map(r => `<tr><td class="font-mono font-bold">${r.name}</td><td>${r.payment_date || r.receipt_date || '—'}</td><td>${r.supplier || r.customer || '—'}</td><td>${r.mode_of_payment || 'Bank'}</td><td class="text-right font-mono font-bold">₹${formatCurrency(r.paid_amount || r.received_amount || r.total_amount)}</td></tr>`).join('')
  }

  const html = `
    <table>
      <thead><tr>${tableHeaders}</tr></thead>
      <tbody>${rowsHtml || '<tr><td colspan="8" class="text-center">No records found</td></tr>'}</tbody>
    </table>
  `
  printFormattedHtml(registerTitle.value, html, companyName.value)
}

const exportCurrentRegisterCSV = () => {
  const dateStr = new Date().toISOString().slice(0, 10)

  if (registerType.value === 'broker-outstanding') {
    const headers = ['Broker ID', 'Broker Name', 'Mobile', 'Dispatch ID', 'Date', 'Customer Party', 'Qty (Qtl)', 'Total Billed (INR)', 'Received (INR)', 'Balance Due (INR)']
    const rows = [headers]
    groups.value.forEach(g => {
      (g.pending_vouchers || []).forEach(pv => {
        rows.push([g.broker_id, g.broker_name, g.broker_mobile || '', pv.name, pv.dispatch_date || '', pv.customer_name || '', pv.dispatch_qty_quintal || 0, pv.total_amount || 0, pv.paid_amount || 0, pv.balance_amount || 0])
      })
    })
    downloadCSV(`Broker_Outstanding_Report_${dateStr}.csv`, rows)
    showToast('Exported Broker Outstanding Report to CSV')
    return
  }

  if (registerType.value === 'supplier-outstanding') {
    const headers = ['Supplier ID', 'Supplier Name', 'Purchase Lot ID', 'Date', 'Grade', 'Qty (Qtl)', 'Lot Value (INR)', 'Paid (INR)', 'Payable Balance (INR)']
    const rows = [headers]
    groups.value.forEach(g => {
      (g.pending_vouchers || []).forEach(pv => {
        rows.push([g.supplier_id, g.supplier_name, pv.name, pv.purchase_date || '', pv.item || 'S-30', pv.purchase_qty_quintal || 0, pv.total_amount || 0, pv.paid_amount || 0, pv.balance_amount || 0])
      })
    })
    downloadCSV(`Supplier_Outstanding_Report_${dateStr}.csv`, rows)
    showToast('Exported Supplier Outstanding Report to CSV')
    return
  }

  // Standard Registers CSV
  let headers = []
  let rows = []

  if (registerType.value === 'purchase') {
    headers = ['Voucher No', 'Date', 'Supplier (Mill)', 'Grade', 'Qty (Quintal)', 'Rate (INR)', 'Total Amount (INR)', 'Available Stock (Qtl)']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.purchase_date || '', r.supplier, r.item || 'S-30', r.purchase_qty_quintal || 0, r.purchase_rate || 0, r.total_amount || 0, r.available_qty_quintal || 0])
    })
  } else if (registerType.value === 'dispatch') {
    headers = ['Dispatch ID', 'Date', 'Customer Party', 'Broker', 'Qty (Quintal)', 'Rate (INR)', 'Total Amount (INR)', 'Balance Due (INR)']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.dispatch_date || '', r.customer_name, r.broker || '', r.dispatch_qty_quintal || 0, r.rate || 0, r.total_amount || 0, r.balance_amount || 0])
    })
  } else if (registerType.value === 'supplier') {
    headers = ['Supplier ID', 'Sugar Mill Name', 'Group', 'Total Lots', 'Total Qty (Qtl)', 'Total Purchases (INR)', 'Available Stock (Qtl)']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.supplier_name || r.name, r.supplier_group || 'Sugar Mill', r.total_lots || 0, r.total_qty || 0, r.total_amount || 0, r.available_stock || 0])
    })
  } else if (registerType.value === 'broker') {
    headers = ['Broker ID', 'Broker Name', 'Mobile No', 'City', 'Dispatches Qty (Qtl)', 'Pending Balance (INR)']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.broker_name || r.name, r.mobile_no || '', r.city || '', r.total_qty || 0, r.total_balance || 0])
    })
  } else if (registerType.value === 'customer') {
    headers = ['Customer ID', 'Customer Party Name', 'Customer Group', 'Territory']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.customer_name || r.name, r.customer_group || '', r.territory || ''])
    })
  } else {
    headers = ['Voucher ID', 'Date', 'Party', 'Reference', 'Mode', 'Amount (INR)']
    rows = [headers]
    records.value.forEach(r => {
      rows.push([r.name, r.payment_date || r.receipt_date || '', r.supplier || r.customer || '', r.reference_no || '', r.mode_of_payment || 'Bank', r.paid_amount || r.received_amount || r.total_amount || 0])
    })
  }

  const safeReg = registerType.value.replace(/[^a-zA-Z0-9_-]/g, '_')
  downloadCSV(`${safeReg}_Register_${dateStr}.csv`, rows)
  showToast(`Exported ${registerTitle.value} to CSV`)
}

const registerMenuItems = computed(() => [
  { key: 'P', label: 'Purchase Register', action: () => router.push('/register/purchase') },
  { key: 'D', label: 'Dispatch Register', action: () => router.push('/register/dispatch') },
  { key: 'Y', label: 'Payment Register', action: () => router.push('/register/payment') },
  { key: 'R', label: 'Receipt Register', action: () => router.push('/register/receipt') },
  { key: 'U', label: 'Suppliers / Mills List', action: () => router.push('/register/supplier') },
  { key: 'K', label: 'Brokers List', action: () => router.push('/register/broker') },
  { key: 'C', label: 'Customers List', action: () => router.push('/register/customer') },
  { key: 'O', label: 'Broker Receivables (Due)', action: () => router.push('/register/broker-outstanding') },
  { key: 'S', label: 'Supplier Payables (Due)', action: () => router.push('/register/supplier-outstanding') },
  { key: 'B', label: 'Day Book (F10)', action: () => router.push('/daybook') },
  { key: 'F7', label: 'Print Register', action: () => printCurrentRegister() },
  { key: 'E', label: 'Export to CSV', action: () => exportCurrentRegisterCSV() },
  { key: 'Esc', label: 'Gateway Menu', action: () => router.push('/') },
])

const handleMenuSelect = (idx) => {
  activeMenuIndex.value = idx
  registerMenuItems.value[idx].action()
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (records.value.length) {
      activeRowIndex.value = (activeRowIndex.value + 1) % records.value.length
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (records.value.length) {
      activeRowIndex.value = (activeRowIndex.value - 1 + records.value.length) % records.value.length
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (records.value[activeRowIndex.value]) {
      openVoucher(records.value[activeRowIndex.value])
    }
  } else if (e.key.toLowerCase() === 'u') {
    e.preventDefault()
    router.push('/register/supplier')
  } else if (e.key.toLowerCase() === 'k') {
    e.preventDefault()
    router.push('/register/broker')
  } else if (e.key.toLowerCase() === 'o') {
    e.preventDefault()
    router.push('/register/broker-outstanding')
  } else if (e.key.toLowerCase() === 's') {
    e.preventDefault()
    router.push('/register/supplier-outstanding')
  } else if (e.key.toLowerCase() === 'n') {
    e.preventDefault()
    openNewEntry()
  } else if (e.key === 'Escape') {
    e.preventDefault()
    router.push('/')
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.btn-tool {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
  user-select: none;
}

.btn-tool:hover {
  background: var(--panel-soft);
  border-color: var(--blue);
  color: var(--blue);
}

.btn-action-small {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--text);
  padding: 3px 9px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.btn-action-small:hover {
  background: var(--blue-soft);
  border-color: var(--blue);
  color: var(--blue);
}

.summary-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.sc-label {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.sc-val {
  font-size: 17px;
  font-weight: 700;
  margin-top: 3px;
  font-family: monospace, inherit;
}

.code-badge {
  background: var(--blue-soft);
  color: var(--blue);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11.5px;
  font-weight: 600;
  font-family: monospace;
}

.status-pill {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}
.status-pill.paid {
  background: #dcfce7;
  color: #166534;
}
.status-pill.partial {
  background: #fef3c7;
  color: #92400e;
}
.status-pill.unpaid {
  background: #fee2e2;
  color: #991b1b;
}
</style>
