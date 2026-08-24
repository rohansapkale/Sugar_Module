<template>
  <div id="main-layout">
    <div id="content-area">
      <!-- Header with Action -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
          <div class="v-title" style="margin-bottom: 2px;">{{ registerTitle }}</div>
          <div style="font-size: 12.5px; color: var(--muted);">Live accounting &amp; trade register directly synced with Frappe database</div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search party, broker, voucher..."
            style="width: 240px; padding: 6px 10px; font-size: 13px; border: 1px solid var(--blue); border-radius: 4px; outline: none; background: var(--input-bg); color: var(--text);"
            @input="filterDebounce"
          />
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
      <div v-if="summary && !['broker-outstanding', 'supplier-outstanding'].includes(registerType)" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 16px;">
        <div class="summary-card">
          <div class="sc-label">Total {{ ['supplier', 'broker', 'customer'].includes(registerType) ? 'Masters' : 'Vouchers' }}</div>
          <div class="sc-val">{{ summary.total_count || 0 }}</div>
        </div>
        <div v-if="summary.total_qty !== undefined && summary.total_qty > 0" class="summary-card">
          <div class="sc-label">Total Qty (Qtl)</div>
          <div class="sc-val" style="color: var(--blue);">{{ formatNumber(summary.total_qty) }}</div>
        </div>
        <div v-if="summary.total_available_qty !== undefined" class="summary-card">
          <div class="sc-label">Available Stock (Qtl)</div>
          <div class="sc-val" style="color: var(--green);">{{ formatNumber(summary.total_available_qty) }}</div>
        </div>
        <div v-if="summary.total_amount !== undefined && summary.total_amount > 0" class="summary-card">
          <div class="sc-label">Total Amount (₹)</div>
          <div class="sc-val" style="color: var(--navy);">₹{{ formatCurrency(summary.total_amount) }}</div>
        </div>
        <div v-if="summary.total_paid !== undefined" class="summary-card">
          <div class="sc-label">Total Paid (₹)</div>
          <div class="sc-val" style="color: var(--green);">₹{{ formatCurrency(summary.total_paid) }}</div>
        </div>
        <div v-if="summary.total_remaining !== undefined && summary.total_remaining > 0" class="summary-card">
          <div class="sc-label">Remaining (₹)</div>
          <div class="sc-val" style="color: var(--red);">₹{{ formatCurrency(summary.total_remaining) }}</div>
        </div>
        <div v-if="summary.total_balance !== undefined && summary.total_balance > 0" class="summary-card">
          <div class="sc-label">Pending Balance (₹)</div>
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
            <th style="width: 9%; text-align: right;">Qty (Qtl)</th>
            <th style="width: 11%; text-align: right;">Total (₹)</th>
            <th style="width: 10%; text-align: right;">Balance (₹)</th>
            <th style="width: 10%; text-align: center;">Status</th>
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
            <td style="color: var(--muted);">{{ r.broker_name || r.broker || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.dispatch_qty_quintal) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700;">₹{{ formatCurrency(r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(r.balance_amount) }}</td>
            <td style="text-align: center;">
              <span :class="['status-pill', r.payment_status === 'Paid' ? 'paid' : (r.payment_status === 'Partially Paid' ? 'partial' : 'unpaid')]">
                {{ r.payment_status || 'Unpaid' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 3. Purchase Payment List Table -->
      <table v-else-if="registerType === 'payment' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 15%;">Payment ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 25%;">Supplier (Sugar Mill)</th>
            <th style="width: 18%;">Sugar Purchase Ref</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 10%;">UTR No.</th>
            <th style="width: 11%; text-align: right;">Paid Amount</th>
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
            <td>{{ r.payment_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.supplier }}</td>
            <td style="font-family: monospace; font-size: 11.5px; color: var(--blue);">{{ r.sugar_purchase || '—' }}</td>
            <td><span class="code-badge">{{ r.payment_mode || 'NEFT' }}</span></td>
            <td style="font-family: monospace; font-size: 11.5px;">{{ r.utr_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.paid_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 4. Broker Party Payment (Receipt) List Table -->
      <table v-else-if="registerType === 'receipt' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 15%;">Receipt ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 24%;">Customer Party</th>
            <th style="width: 18%;">Dispatch Ref</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 11%;">UTR No.</th>
            <th style="width: 11%; text-align: right;">Received (₹)</th>
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
            <td>{{ r.payment_date || '—' }}</td>
            <td style="font-weight: 600;">{{ r.customer }}</td>
            <td style="font-family: monospace; font-size: 11.5px; color: var(--blue);">{{ r.dispatch_entry || '—' }}</td>
            <td><span class="code-badge">{{ r.payment_mode || 'NEFT' }}</span></td>
            <td style="font-family: monospace; font-size: 11.5px;">{{ r.utr_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.paid_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 5. SUPPLIERS / MILLS REGISTER -->
      <table v-else-if="registerType === 'supplier' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 25%;">Supplier / Mill Name</th>
            <th style="width: 15%;">Group / Type</th>
            <th style="width: 15%; text-align: center;">Total Lots</th>
            <th style="width: 15%; text-align: right;">Total Qty (Qtl)</th>
            <th style="width: 15%; text-align: right;">Total Purchases (₹)</th>
            <th style="width: 15%; text-align: right;">Available Stock</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(r, idx) in records"
            :key="r.name || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="activeRowIndex = idx"
          >
            <td style="font-weight: 700; color: var(--navy);">{{ r.supplier_name || r.name }}</td>
            <td><span class="code-badge">{{ r.supplier_group || 'Sugar Mill' }}</span></td>
            <td style="text-align: center; font-weight: 600;">{{ r.total_lots || 0 }} Lots</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.total_qty) }} Qtl</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700;">₹{{ formatCurrency(r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">{{ formatNumber(r.available_stock) }} Qtl</td>
          </tr>
        </tbody>
      </table>

      <!-- 6. BROKERS REGISTER -->
      <table v-else-if="registerType === 'broker' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 18%;">Broker ID</th>
            <th style="width: 25%;">Broker Name</th>
            <th style="width: 15%;">Mobile No</th>
            <th style="width: 14%;">City / State</th>
            <th style="width: 14%; text-align: right;">Dispatches Qty</th>
            <th style="width: 14%; text-align: right;">Pending Balance</th>
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
            <td style="font-weight: 700;">{{ r.broker_name || r.name }}</td>
            <td style="font-family: monospace;">{{ r.mobile_no || '—' }}</td>
            <td>{{ r.city || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.total_qty) }} Qtl</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(r.total_balance) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- 7. CUSTOMERS REGISTER -->
      <table v-else-if="registerType === 'customer' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 25%;">Customer ID</th>
            <th style="width: 35%;">Customer Party Name</th>
            <th style="width: 20%;">Customer Group</th>
            <th style="width: 20%;">Territory</th>
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
            <td style="font-weight: 700;">{{ r.customer_name || r.name }}</td>
            <td><span class="code-badge">{{ r.customer_group || 'All Customer Groups' }}</span></td>
            <td>{{ r.territory || 'India' }}</td>
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
            <div style="display: flex; gap: 16px; align-items: center;">
              <span style="font-size: 12px; color: var(--muted);">Billed: <b>₹{{ formatCurrency(g.total_billed) }}</b></span>
              <span style="font-size: 12px; color: var(--green);">Received: <b>₹{{ formatCurrency(g.total_received) }}</b></span>
              <span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 700;">
                Due: ₹{{ formatCurrency(g.total_pending) }}
              </span>
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
            <div style="display: flex; gap: 16px; align-items: center;">
              <span style="font-size: 12px; color: var(--muted);">Purchased: <b>₹{{ formatCurrency(g.total_billed) }}</b></span>
              <span style="font-size: 12px; color: var(--green);">Paid: <b>₹{{ formatCurrency(g.total_paid) }}</b></span>
              <span style="background: #fee2e2; color: #991b1b; padding: 4px 10px; border-radius: 4px; font-size: 13px; font-weight: 700;">
                Payable: ₹{{ formatCurrency(g.total_pending) }}
              </span>
            </div>
          </div>

          <!-- Pending Vouchers Table inside Group -->
          <table v-if="g.pending_vouchers && g.pending_vouchers.length" class="daybook-table" style="margin: 0;">
            <thead>
              <tr style="background: var(--panel);">
                <th style="width: 20%;">Purchase Lot ID</th>
                <th style="width: 11%;">Date</th>
                <th style="width: 10%;">Grade</th>
                <th style="width: 11%; text-align: right;">Qty (Qtl)</th>
                <th style="width: 16%; text-align: right;">Lot Value (₹)</th>
                <th style="width: 16%; text-align: right;">Paid (₹)</th>
                <th style="width: 16%; text-align: right;">Payable Balance (₹)</th>
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
                <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--red);">₹{{ formatCurrency(pv.remaining_amount) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else style="padding: 12px; text-align: center; color: var(--green); font-size: 12.5px; background: #f0fdf4;">
            ✔ All sugar purchases with this mill are completely cleared &amp; paid!
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!records.length && !groups.length" style="padding: 40px 20px; text-align: center; color: var(--muted); background: var(--panel); border: 1px dashed var(--line); border-radius: 6px;">
        <div style="font-size: 28px; margin-bottom: 8px;">📂</div>
        <div style="font-size: 15px; font-weight: 600; color: var(--navy);">No records found in this register</div>
        <div style="font-size: 12.5px; margin-top: 4px;">{{ searchQuery ? 'Try adjusting your search query.' : 'Transactions will appear here as soon as you record them in Frappe.' }}</div>
        <button
          v-if="currentConfig.entryRoute"
          style="margin-top: 14px; padding: 7px 16px; background: var(--blue); color: #fff; border: none; border-radius: 4px; font-size: 13px; font-weight: 600; cursor: pointer;"
          @click="openNewEntry"
        >
          Create First Entry ({{ currentConfig.fkCode }})
        </button>
      </div>

      <div class="keyboard-hint" style="margin-top: 18px;">
        <span><kbd>↑</kbd> <kbd>↓</kbd> Browse List</span>
        <span><kbd>U</kbd> Suppliers List</span>
        <span><kbd>B</kbd> Brokers List</span>
        <span><kbd>O</kbd> Broker Receivables</span>
        <span><kbd>S</kbd> Supplier Payables</span>
        <span><kbd>Esc</kbd> Return to Gateway</span>
      </div>
    </div>

    <!-- Right Side Menu -->
    <MenuPanel
      section-title="Register Menu"
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
import MenuPanel from '../components/common/MenuPanel.vue'

const route = useRoute()
const router = useRouter()
const { getRegisterData } = useFrappeApi()

const registerType = computed(() => route.params.type || 'purchase')

const REGISTER_CONFIGS = {
  purchase: {
    voucherType: 'Sugar Purchase',
    title: 'Sugar Purchase Register (List of Purchases)',
    entryLabel: 'Sugar Purchase',
    entryRoute: '/voucher/purchase',
    fkCode: 'F9',
  },
  dispatch: {
    voucherType: 'Dispatch Entry',
    title: 'Dispatch Entry Register (List of Dispatches)',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'F8',
  },
  payment: {
    voucherType: 'Purchase Payment',
    title: 'Purchase Payment Register (Supplier Payments)',
    entryLabel: 'Payment',
    entryRoute: '/voucher/payment',
    fkCode: 'F5',
  },
  receipt: {
    voucherType: 'Broker Party Payment',
    title: 'Broker Party Payment Register (Receipts)',
    entryLabel: 'Receipt',
    entryRoute: '/voucher/receipt',
    fkCode: 'F6',
  },
  supplier: {
    voucherType: 'Supplier',
    title: 'Suppliers & Sugar Mills Register (List)',
    entryLabel: 'Sugar Purchase',
    entryRoute: '/voucher/purchase',
    fkCode: 'F9',
  },
  broker: {
    voucherType: 'Broker',
    title: 'Sugar Brokers Register (List)',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'F8',
  },
  customer: {
    voucherType: 'Customer',
    title: 'Customer Parties Register (List)',
    entryLabel: 'Dispatch Entry',
    entryRoute: '/voucher/dispatch',
    fkCode: 'F8',
  },
  'broker-outstanding': {
    voucherType: 'broker-outstanding',
    title: 'Broker / Customer Outstanding Receivables Report',
    entryLabel: 'Receipt',
    entryRoute: '/voucher/receipt',
    fkCode: 'F6',
  },
  'supplier-outstanding': {
    voucherType: 'supplier-outstanding',
    title: 'Supplier / Mill Outstanding Payables Report',
    entryLabel: 'Payment',
    entryRoute: '/voucher/payment',
    fkCode: 'F5',
  },
}

const currentConfig = computed(() => REGISTER_CONFIGS[registerType.value] || REGISTER_CONFIGS.purchase)
const registerTitle = computed(() => currentConfig.value.title)

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
  if (currentConfig.value.entryRoute) {
    router.push(currentConfig.value.entryRoute)
  }
}

const openVoucher = (row) => {
  showToast(`Opening voucher ${row.name}`)
  openNewEntry()
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
