<template>
  <div id="main-layout">
    <div id="content-area">
      <!-- Header with Action -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
          <div class="v-title" style="margin-bottom: 2px;">{{ registerTitle }}</div>
          <div style="font-size: 12.5px; color: var(--muted);">Live audit list directly synced with Frappe database</div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search voucher, party, item..."
            style="width: 240px; padding: 6px 10px; font-size: 13px; border: 1px solid var(--blue); border-radius: 4px; outline: none; background: #fff;"
            @input="filterDebounce"
          />
          <button
            style="padding: 7px 14px; background: var(--blue); color: #fff; border: none; border-radius: 4px; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            @click="openNewEntry"
          >
            <span>➕</span> New {{ currentConfig.entryLabel }} (<kbd style="background: rgba(255,255,255,0.2); border: none; color: #fff;">{{ currentConfig.fkCode }}</kbd>)
          </button>
        </div>
      </div>

      <!-- KPI Summary Cards -->
      <div v-if="summary" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 16px;">
        <div class="summary-card">
          <div class="sc-label">Total Vouchers</div>
          <div class="sc-val">{{ summary.total_count || 0 }}</div>
        </div>
        <div v-if="summary.total_qty !== undefined" class="summary-card">
          <div class="sc-label">Total Qty (Qtl)</div>
          <div class="sc-val" style="color: var(--blue);">{{ formatNumber(summary.total_qty) }}</div>
        </div>
        <div v-if="summary.total_available_qty !== undefined" class="summary-card">
          <div class="sc-label">Available Stock (Qtl)</div>
          <div class="sc-val" style="color: var(--green);">{{ formatNumber(summary.total_available_qty) }}</div>
        </div>
        <div v-if="summary.total_amount !== undefined" class="summary-card">
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

      <!-- Sugar Purchase List Table -->
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

      <!-- Dispatch Entry List Table -->
      <table v-else-if="registerType === 'dispatch' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 14%;">Dispatch ID</th>
            <th style="width: 10%;">Date</th>
            <th style="width: 20%;">Customer Party</th>
            <th style="width: 16%;">Broker</th>
            <th style="width: 12%;">Vehicle No</th>
            <th style="width: 10%; text-align: right;">Qty (Qtl)</th>
            <th style="width: 9%; text-align: right;">Rate (₹)</th>
            <th style="width: 12%; text-align: right;">Total (₹)</th>
            <th style="width: 11%; text-align: right;">Balance (₹)</th>
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
            <td style="color: var(--muted);">{{ r.broker_name || r.broker || 'Direct' }}</td>
            <td style="font-family: monospace;">{{ r.vehicle_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600;">{{ formatNumber(r.dispatch_qty_quintal) }}</td>
            <td style="text-align: right; font-family: monospace;">₹{{ formatNumber(r.rate) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--navy);">₹{{ formatCurrency(r.total_amount) }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600; color: var(--amber);">₹{{ formatCurrency(r.balance_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Purchase Payment List Table -->
      <table v-else-if="registerType === 'payment' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 16%;">Payment ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 25%;">Supplier</th>
            <th style="width: 18%;">Sugar Purchase Ref</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 14%;">UTR / Ref No</th>
            <th style="width: 14%; text-align: right;">Paid Amount (₹)</th>
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
            <td style="font-family: monospace; font-size: 12px; color: var(--muted);">{{ r.sugar_purchase || '—' }}</td>
            <td><span class="code-badge">{{ r.payment_mode || 'NEFT' }}</span></td>
            <td style="font-family: monospace;">{{ r.utr_no || r.reference_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.paid_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Broker Party Payment List Table -->
      <table v-else-if="registerType === 'receipt' && records.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 16%;">Receipt ID</th>
            <th style="width: 11%;">Date</th>
            <th style="width: 25%;">Customer</th>
            <th style="width: 18%;">Broker</th>
            <th style="width: 10%;">Mode</th>
            <th style="width: 14%;">UTR / Cheque No</th>
            <th style="width: 14%; text-align: right;">Received Amount (₹)</th>
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
            <td style="color: var(--muted);">{{ r.broker_name || r.broker || '—' }}</td>
            <td><span class="code-badge">{{ r.payment_mode || 'NEFT' }}</span></td>
            <td style="font-family: monospace;">{{ r.utr_no || '—' }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 700; color: var(--green);">₹{{ formatCurrency(r.paid_amount) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else-if="!records.length" style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 30px; text-align: center; color: var(--muted); margin-top: 20px;">
        <div style="font-size: 28px; margin-bottom: 8px;">📋</div>
        <p style="font-size: 14px; margin-bottom: 6px;">No records found in this register</p>
        <button
          style="padding: 6px 14px; background: var(--blue); color: #fff; border: none; border-radius: 4px; font-size: 13px; font-weight: 600; cursor: pointer; margin-top: 8px;"
          @click="openNewEntry"
        >
          Create First Entry ({{ currentConfig.fkCode }})
        </button>
      </div>

      <div class="keyboard-hint" style="margin-top: 18px;">
        <span><kbd>↑</kbd> <kbd>↓</kbd> Browse List</span>
        <span><kbd>Enter</kbd> Open Voucher</span>
        <span><kbd>N</kbd> / <kbd>{{ currentConfig.fkCode }}</kbd> New Entry</span>
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
}

const currentConfig = computed(() => REGISTER_CONFIGS[registerType.value] || REGISTER_CONFIGS.purchase)
const registerTitle = computed(() => currentConfig.value.title)

const records = ref([])
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
  router.push(currentConfig.value.entryRoute)
}

const openVoucher = (row) => {
  showToast(`Opening voucher ${row.name}`)
  openNewEntry()
}

const registerMenuItems = [
  { key: 'N', label: `New ${currentConfig.value.entryLabel} (${currentConfig.value.fkCode})`, action: openNewEntry },
  { key: 'P', label: 'Purchase Register', action: () => router.push('/register/purchase') },
  { key: 'D', label: 'Dispatch Register', action: () => router.push('/register/dispatch') },
  { key: 'Y', label: 'Payment Register', action: () => router.push('/register/payment') },
  { key: 'R', label: 'Receipt Register', action: () => router.push('/register/receipt') },
  { key: 'B', label: 'Day Book (All)', action: () => router.push('/daybook') },
  { key: 'Esc', label: 'Gateway Menu', action: () => router.push('/') },
]

const handleMenuSelect = (idx) => {
  activeMenuIndex.value = idx
  registerMenuItems[idx].action()
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
  } else if (e.key.toLowerCase() === 'n') {
    e.preventDefault()
    openNewEntry()
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
</style>
