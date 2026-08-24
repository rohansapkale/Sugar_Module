<template>
  <div id="main-layout">
    <div id="content-area">
      <div class="v-header-section">
        <div>
          <div class="v-title">{{ currentConfig.title }}</div>
          <div style="font-size: 12.5px; color: var(--navy); font-weight: 600; margin-top: 2px;">
            Status: <span style="font-family: monospace; color: var(--blue);">Draft / New</span>
          </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <button
            v-if="voucherType === 'purchase'"
            type="button"
            style="padding: 6px 12px; background: #eef3fc; color: var(--navy); border: 1px solid var(--blue); border-radius: 4px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            @click="router.push('/register/purchase')"
          >
            📋 Purchases List (<kbd style="background: var(--navy); color: #fff; padding: 1px 5px; border-radius: 3px; font-size: 11px;">Alt+L</kbd>)
          </button>
          <button
            v-else-if="voucherType === 'dispatch'"
            type="button"
            style="padding: 6px 12px; background: #eef3fc; color: var(--navy); border: 1px solid var(--blue); border-radius: 4px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            @click="router.push('/register/dispatch')"
          >
            📋 Dispatches List (<kbd style="background: var(--navy); color: #fff; padding: 1px 5px; border-radius: 3px; font-size: 11px;">Alt+L</kbd>)
          </button>
          <button
            v-else-if="voucherType === 'payment'"
            type="button"
            style="padding: 6px 12px; background: #eef3fc; color: var(--navy); border: 1px solid var(--blue); border-radius: 4px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            @click="router.push('/register/payment')"
          >
            📋 Payments List (<kbd style="background: var(--navy); color: #fff; padding: 1px 5px; border-radius: 3px; font-size: 11px;">Alt+L</kbd>)
          </button>
        </div>
      </div>

      <!-- Base Meta Fields -->
      <div class="field-grid">
        <div class="field-row">
          <label>Voucher Date</label>
          <div class="input-control-wrap">
            <input
              ref="field_date"
              v-model="form.date"
              type="date"
              data-field="date"
              @keydown="handleFieldKeyDown($event, 'date')"
            />
          </div>
        </div>

        <div class="field-row disabled">
          <label>Company</label>
          <div class="input-control-wrap">
            <input type="text" :value="defaultCompany" readonly />
          </div>
        </div>
      </div>

      <!-- 1. SUGAR PURCHASE (F9) -->
      <div v-if="voucherType === 'purchase'">
        <div class="field-row">
          <label>Supplier (Sugar Mill)</label>
          <div class="input-control-wrap">
            <input
              ref="field_supplier"
              v-model="form.supplier"
              type="text"
              placeholder="Select sugar mill / supplier..."
              autocomplete="off"
              data-field="supplier"
              @focus="onLedgerFocus('supplier', 'Supplier')"
              @input="onLedgerInput('supplier', 'Supplier')"
              @keydown="handleFieldKeyDown($event, 'supplier')"
            />
            <LedgerDropdown
              v-if="activeDropdownField === 'supplier'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Sugar Item / Grade</label>
            <div class="input-control-wrap">
              <input
                ref="field_item"
                v-model="form.item"
                type="text"
                placeholder="Select item (e.g. S-302526, M30)..."
                autocomplete="off"
                data-field="item"
                @focus="onLedgerFocus('item', 'Item')"
                @input="onLedgerInput('item', 'Item')"
                @keydown="handleFieldKeyDown($event, 'item')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'item'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Qty (Quintals)</label>
            <div class="input-control-wrap">
              <input
                ref="field_qty"
                v-model.number="form.purchase_qty_quintal"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="qty"
                @input="calcPurchaseTotal"
                @keydown="handleFieldKeyDown($event, 'qty')"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Purchase Rate (₹/Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_rate"
                v-model.number="form.purchase_rate"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="rate"
                @input="calcPurchaseTotal"
                @keydown="handleFieldKeyDown($event, 'rate')"
              />
            </div>
          </div>

          <div class="field-row disabled">
            <label>Total Sugar Amount</label>
            <div class="input-control-wrap">
              <input type="text" :value="formatCurrency(form.total_amount)" readonly style="font-weight: 700; color: var(--navy);" />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. DISPATCH ENTRY (F8) -->
      <div v-else-if="voucherType === 'dispatch'">
        <!-- Sugar Purchase Lot Selector -->
        <div class="field-row">
          <label>Source Sugar Purchase</label>
          <div class="input-control-wrap">
            <input
              ref="field_sugar_purchase"
              v-model="form.sugar_purchase"
              type="text"
              placeholder="Select source Sugar Purchase lot (Mill / Voucher No)..."
              autocomplete="off"
              data-field="sugar_purchase"
              @focus="onLedgerFocus('sugar_purchase', 'Sugar Purchase')"
              @input="onLedgerInput('sugar_purchase', 'Sugar Purchase')"
              @keydown="handleFieldKeyDown($event, 'sugar_purchase')"
            />
            <LedgerDropdown
              v-if="activeDropdownField === 'sugar_purchase'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <!-- Selected Purchase Lot Live Stock Info Banner -->
        <div v-if="selectedPurchaseLot" style="background: #edf3fd; border-left: 3px solid var(--blue); padding: 8px 12px; margin-bottom: 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
          <span>🏭 Mill: <strong style="color: var(--navy);">{{ selectedPurchaseLot.supplier }}</strong> · Grade: <strong>{{ selectedPurchaseLot.item }}</strong> · Lot Qty: <strong>{{ selectedPurchaseLot.purchase_qty_quintal }} Qtl</strong></span>
          <span>Stock Available: <strong style="color: var(--green); font-size: 13.5px;">{{ selectedPurchaseLot.available_qty_quintal }} Qtl</strong></span>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Customer Party</label>
            <div class="input-control-wrap">
              <input
                ref="field_customer"
                v-model="form.customer_name"
                type="text"
                placeholder="Select customer party..."
                autocomplete="off"
                data-field="customer_name"
                @focus="onLedgerFocus('customer_name', 'Customer')"
                @input="onLedgerInput('customer_name', 'Customer')"
                @keydown="handleFieldKeyDown($event, 'customer_name')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'customer_name'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Broker Name</label>
            <div class="input-control-wrap">
              <input
                ref="field_broker"
                v-model="form.broker"
                type="text"
                placeholder="Select broker..."
                autocomplete="off"
                data-field="broker"
                @focus="onLedgerFocus('broker', 'Broker')"
                @input="onLedgerInput('broker', 'Broker')"
                @keydown="handleFieldKeyDown($event, 'broker')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'broker'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Vehicle No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_vehicle_no"
                v-model="form.vehicle_no"
                type="text"
                placeholder="e.g. MH19CZ1234"
                data-field="vehicle_no"
                @keydown="handleFieldKeyDown($event, 'vehicle_no')"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Sugar Item</label>
            <div class="input-control-wrap">
              <input
                ref="field_item"
                v-model="form.item"
                type="text"
                placeholder="Select item..."
                autocomplete="off"
                data-field="item"
                @focus="onLedgerFocus('item', 'Item')"
                @input="onLedgerInput('item', 'Item')"
                @keydown="handleFieldKeyDown($event, 'item')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'item'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Dispatch Qty (Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_qty"
                v-model.number="form.dispatch_qty_quintal"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="qty"
                @input="calcDispatchTotal"
                @keydown="handleFieldKeyDown($event, 'qty')"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Sale Rate (₹/Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_rate"
                v-model.number="form.rate"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="rate"
                @input="calcDispatchTotal"
                @keydown="handleFieldKeyDown($event, 'rate')"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 3. PURCHASE PAYMENT (F5) -->
      <div v-else-if="voucherType === 'payment'">
        <div class="field-grid">
          <div class="field-row">
            <label>Bank / Cash Account</label>
            <div class="input-control-wrap">
              <input
                ref="field_bank"
                v-model="form.bank_account"
                type="text"
                placeholder="Select Bank / Cash A/c..."
                autocomplete="off"
                data-field="bank_account"
                @focus="onLedgerFocus('bank_account', 'Account')"
                @input="onLedgerInput('bank_account', 'Account')"
                @keydown="handleFieldKeyDown($event, 'bank_account')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'bank_account'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Supplier (Paid To)</label>
            <div class="input-control-wrap">
              <input
                ref="field_supplier"
                v-model="form.supplier"
                type="text"
                placeholder="Select supplier/mill..."
                autocomplete="off"
                data-field="supplier"
                @focus="onLedgerFocus('supplier', 'Supplier')"
                @input="onLedgerInput('supplier', 'Supplier')"
                @keydown="handleFieldKeyDown($event, 'supplier')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'supplier'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Payment Mode</label>
            <div class="input-control-wrap">
              <select
                ref="field_mode"
                v-model="form.payment_mode"
                data-field="payment_mode"
                @keydown="handleFieldKeyDown($event, 'payment_mode')"
              >
                <option value="RTGS">RTGS</option>
                <option value="NEFT">NEFT</option>
                <option value="IMPS">IMPS</option>
                <option value="UPI">UPI</option>
                <option value="Cheque">Cheque</option>
                <option value="Cash">Cash</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <label>UTR / Ref No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_utr"
                v-model="form.utr_no"
                type="text"
                placeholder="e.g. UTR / Ref No."
                data-field="utr_no"
                @keydown="handleFieldKeyDown($event, 'utr_no')"
              />
            </div>
          </div>
        </div>

        <div class="field-row">
          <label>Paid Amount (₹)</label>
          <div class="input-control-wrap">
            <input
              ref="field_paid_amount"
              v-model.number="form.paid_amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              style="font-size: 15px; font-weight: 700; color: var(--navy);"
              data-field="paid_amount"
              @keydown="handleFieldKeyDown($event, 'paid_amount')"
            />
          </div>
        </div>
      </div>

      <!-- 4. BROKER PARTY PAYMENT (RECEIPT) (F6) -->
      <div v-else-if="voucherType === 'receipt'">
        <!-- Dispatch Entry Reference Selector -->
        <div class="field-row">
          <label>Source Dispatch Entry</label>
          <div class="input-control-wrap">
            <input
              ref="field_dispatch_entry"
              v-model="form.dispatch_entry"
              type="text"
              placeholder="Select Dispatch Entry (DIS-ENT-... / Party / Broker)..."
              autocomplete="off"
              data-field="dispatch_entry"
              @focus="onLedgerFocus('dispatch_entry', 'Dispatch Entry')"
              @input="onLedgerInput('dispatch_entry', 'Dispatch Entry')"
              @keydown="handleFieldKeyDown($event, 'dispatch_entry')"
            />
            <LedgerDropdown
              v-if="activeDropdownField === 'dispatch_entry'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <!-- Selected Dispatch Entry Live Info Banner -->
        <div v-if="selectedDispatchEntry" style="background: #edf3fd; border-left: 3px solid var(--blue); padding: 8px 12px; margin-bottom: 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
          <span>🚚 Customer: <strong style="color: var(--navy);">{{ selectedDispatchEntry.customer_name }}</strong> · Broker: <strong>{{ selectedDispatchEntry.broker || 'Direct' }}</strong> · Total: <strong>₹{{ formatCurrency(selectedDispatchEntry.total_amount) }}</strong></span>
          <span>Balance Due: <strong style="color: var(--gold); font-size: 13.5px;">₹{{ formatCurrency(selectedDispatchEntry.balance_amount) }}</strong></span>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Bank / Cash Account</label>
            <div class="input-control-wrap">
              <input
                ref="field_bank"
                v-model="form.bank_account"
                type="text"
                placeholder="Select Bank / Cash A/c..."
                autocomplete="off"
                data-field="bank_account"
                @focus="onLedgerFocus('bank_account', 'Account')"
                @input="onLedgerInput('bank_account', 'Account')"
                @keydown="handleFieldKeyDown($event, 'bank_account')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'bank_account'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div class="field-row">
            <label>Customer Party</label>
            <div class="input-control-wrap">
              <input
                ref="field_customer"
                v-model="form.customer"
                type="text"
                placeholder="Select customer..."
                autocomplete="off"
                data-field="customer"
                @focus="onLedgerFocus('customer', 'Customer')"
                @input="onLedgerInput('customer', 'Customer')"
                @keydown="handleFieldKeyDown($event, 'customer')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === 'customer'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div class="field-row">
            <label>Payment Mode</label>
            <div class="input-control-wrap">
              <select
                ref="field_mode"
                v-model="form.payment_mode"
                data-field="payment_mode"
                @keydown="handleFieldKeyDown($event, 'payment_mode')"
              >
                <option value="NEFT">NEFT</option>
                <option value="RTGS">RTGS</option>
                <option value="IMPS">IMPS</option>
                <option value="UPI">UPI</option>
                <option value="Cheque">Cheque</option>
                <option value="Cash">Cash</option>
              </select>
            </div>
          </div>

          <div class="field-row">
            <label>UTR / Ref No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_utr"
                v-model="form.utr_no"
                type="text"
                placeholder="UTR / Ref No."
                data-field="utr_no"
                @keydown="handleFieldKeyDown($event, 'utr_no')"
              />
            </div>
          </div>
        </div>

        <div class="field-row">
          <label>Received Amount (₹)</label>
          <div class="input-control-wrap">
            <input
              ref="field_paid_amount"
              v-model.number="form.paid_amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              style="font-size: 15px; font-weight: 700; color: var(--navy);"
              data-field="paid_amount"
              @keydown="handleFieldKeyDown($event, 'paid_amount')"
            />
          </div>
        </div>
      </div>

      <!-- Dynamic Particulars Table Grid -->
      <table class="grid">
        <thead>
          <tr>
            <th style="width: 65%;">Particulars / Additional Ledger</th>
            <th style="width: 35%; text-align: right;">Amount (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in form.additional_rows" :key="idx">
            <td class="cell-wrap">
              <input
                :ref="el => setRowRef(el, idx, 'ledger')"
                v-model="row.ledger"
                type="text"
                placeholder="Type additional ledger name (Freight, Commission, etc.)..."
                autocomplete="off"
                @focus="onLedgerFocus(`row-${idx}-ledger`, 'Account')"
                @input="onLedgerInput(`row-${idx}-ledger`, 'Account')"
                @keydown="handleRowKeyDown($event, idx, 'ledger')"
              />
              <LedgerDropdown
                v-if="activeDropdownField === `row-${idx}-ledger`"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </td>
            <td class="amt">
              <input
                :ref="el => setRowRef(el, idx, 'amount')"
                v-model.number="row.amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                @keydown="handleRowKeyDown($event, idx, 'amount')"
              />
            </td>
          </tr>
          <tr class="total">
            <td>Grand Total (₹)</td>
            <td class="amt">{{ formatCurrency(grandTotal) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Narration Section -->
      <div class="field-row" style="margin-top: 14px;">
        <label>Narration</label>
        <div class="input-control-wrap">
          <textarea
            ref="field_narration"
            v-model="form.narration"
            rows="2"
            placeholder="Enter narration notes for this voucher..."
            data-field="narration"
            @keydown="handleNarrationKeyDown"
          ></textarea>
        </div>
      </div>

      <!-- Keyboard Cues Hint -->
      <div class="keyboard-hint">
        <span><kbd>Tab</kbd> / <kbd>Enter</kbd> Next Field</span>
        <span><kbd>Shift+Tab</kbd> Prev Field</span>
        <span><kbd>↑</kbd> <kbd>↓</kbd> Dropdown Nav</span>
        <span><kbd>Esc</kbd> Clear / Discard</span>
        <span><kbd>Enter</kbd> on Narration → <b>Accept</b></span>
      </div>
    </div>

    <!-- Side Menu Panel for Switch Voucher -->
    <MenuPanel
      section-title="Voucher Type"
      :items="voucherMenuItems"
      :active-index="activeVoucherIndex"
      @select="handleVoucherSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast, openConfirm } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'
import LedgerDropdown from '../components/common/LedgerDropdown.vue'

const route = useRoute()
const router = useRouter()
const { bootState, searchLedgers, saveVoucher } = useFrappeApi()

const voucherType = computed(() => route.params.type || 'purchase')
const defaultCompany = computed(() => bootState.default_company || 'Rajendra Narahari Lokhande')

const VOUCHER_CONFIGS = {
  purchase: { title: 'Sugar Purchase Voucher (F9)', doctype: 'Sugar Purchase' },
  dispatch: { title: 'Dispatch Entry Voucher (F8)', doctype: 'Dispatch Entry' },
  payment: { title: 'Purchase Payment Voucher (F5)', doctype: 'Purchase Payment' },
  receipt: { title: 'Broker Party Payment (Receipt) (F6)', doctype: 'Broker Party Payment' },
  contra: { title: 'Contra / Bank Transfer (F4)', doctype: 'Account' },
}

const currentConfig = computed(() => VOUCHER_CONFIGS[voucherType.value] || VOUCHER_CONFIGS.purchase)

// Form State
const selectedPurchaseLot = ref(null)
const selectedDispatchEntry = ref(null)

const form = reactive({
  date: new Date().toISOString().split('T')[0],
  sugar_purchase: '',
  dispatch_entry: '',
  supplier: '',
  customer: '',
  customer_name: '',
  broker: '',
  bank_account: '',
  item: 'S-302526',
  purchase_qty_quintal: 100,
  purchase_rate: 4000,
  total_amount: 400000,
  dispatch_qty_quintal: 50,
  rate: 4200,
  vehicle_no: '',
  payment_mode: 'RTGS',
  utr_no: '',
  paid_amount: 0,
  additional_rows: [{ ledger: '', amount: '' }],
  narration: '',
})

// Calculations
const calcPurchaseTotal = () => {
  form.total_amount = (form.purchase_qty_quintal || 0) * (form.purchase_rate || 0)
}

const calcDispatchTotal = () => {
  form.total_amount = (form.dispatch_qty_quintal || 0) * (form.rate || 0)
}

const grandTotal = computed(() => {
  let base = 0
  if (voucherType.value === 'purchase' || voucherType.value === 'dispatch') {
    base = form.total_amount || 0
  } else if (voucherType.value === 'payment' || voucherType.value === 'receipt') {
    base = form.paid_amount || 0
  }
  const additional = form.additional_rows.reduce((sum, r) => sum + (parseFloat(r.amount) || 0), 0)
  return base + additional
})

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Side Menu Items
const voucherMenuItems = [
  { key: 'F4', label: 'Contra', route: '/voucher/contra' },
  { key: 'F5', label: 'Payment', route: '/voucher/payment' },
  { key: 'F6', label: 'Receipt', route: '/voucher/receipt' },
  { key: 'F8', label: 'Dispatch', route: '/voucher/dispatch' },
  { key: 'F9', label: 'Purchase', route: '/voucher/purchase' },
  { key: 'L', label: 'Purchase List', route: '/register/purchase' },
  { key: 'K', label: 'Dispatch List', route: '/register/dispatch' },
  { key: 'B', label: 'Day Book (F10)', route: '/daybook' },
]

const activeVoucherIndex = computed(() => {
  const map = { contra: 0, payment: 1, receipt: 2, dispatch: 3, purchase: 4 }
  return map[voucherType.value] ?? 4
})

const handleVoucherSelect = (idx) => {
  router.push(voucherMenuItems[idx].route)
}

// Dropdown Autocomplete
const activeDropdownField = ref(null)
const dropdownMatches = ref([])
const dropdownIndex = ref(0)
let searchDebounce = null

const onLedgerFocus = async (fieldName, doctype) => {
  activeDropdownField.value = fieldName
  dropdownIndex.value = 0
  let query = ''
  if (fieldName.startsWith('row-')) {
    const idx = parseInt(fieldName.split('-')[1])
    query = form.additional_rows[idx]?.ledger || ''
  } else {
    query = form[fieldName] || ''
  }
  const matches = await searchLedgers(query, doctype)
  dropdownMatches.value = matches
}

const onLedgerInput = (fieldName, doctype) => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(async () => {
    let q = ''
    if (fieldName.startsWith('row-')) {
      const idx = parseInt(fieldName.split('-')[1])
      q = form.additional_rows[idx]?.ledger || ''
    } else {
      q = form[fieldName] || ''
    }
    const matches = await searchLedgers(q, doctype)
    dropdownMatches.value = matches
    dropdownIndex.value = 0
  }, 80)
}

const selectDropdownMatch = (match) => {
  const fieldName = activeDropdownField.value
  if (!fieldName) return

  if (fieldName.startsWith('row-')) {
    const idx = parseInt(fieldName.split('-')[1])
    form.additional_rows[idx].ledger = match.name
  } else {
    form[fieldName] = match.name
    if (fieldName === 'sugar_purchase' && match.details) {
      selectedPurchaseLot.value = match.details
      if (match.details.item) form.item = match.details.item
    } else if (fieldName === 'dispatch_entry' && match.details) {
      selectedDispatchEntry.value = match.details
      if (match.details.customer_name) form.customer = match.details.customer_name
      if (match.details.broker) form.broker = match.details.broker
      if (match.details.balance_amount !== undefined) form.paid_amount = match.details.balance_amount
    }
  }

  activeDropdownField.value = null
  dropdownMatches.value = []
  advanceFieldFrom(fieldName)
}

// Field sequence
const rowRefs = reactive({})
const setRowRef = (el, idx, key) => {
  if (!rowRefs[idx]) rowRefs[idx] = {}
  rowRefs[idx][key] = el
}

const getFieldSequence = () => {
  if (voucherType.value === 'purchase') {
    return ['date', 'supplier', 'item', 'qty', 'rate', 'narration']
  } else if (voucherType.value === 'dispatch') {
    return ['date', 'sugar_purchase', 'customer_name', 'broker', 'vehicle_no', 'item', 'qty', 'rate', 'narration']
  } else if (voucherType.value === 'payment') {
    return ['date', 'bank_account', 'supplier', 'payment_mode', 'utr_no', 'paid_amount', 'narration']
  } else if (voucherType.value === 'receipt') {
    return ['date', 'dispatch_entry', 'bank_account', 'customer', 'payment_mode', 'utr_no', 'paid_amount', 'narration']
  }
  return ['date', 'narration']
}

const advanceFieldFrom = (currentField) => {
  const seq = getFieldSequence()
  const idx = seq.indexOf(currentField)
  if (idx !== -1 && idx < seq.length - 1) {
    const nextField = seq[idx + 1]
    const el = document.querySelector(`[data-field="${nextField}"]`)
    if (el) el.focus()
  }
}

const retreatFieldFrom = (currentField) => {
  const seq = getFieldSequence()
  const idx = seq.indexOf(currentField)
  if (idx > 0) {
    const prevField = seq[idx - 1]
    const el = document.querySelector(`[data-field="${prevField}"]`)
    if (el) el.focus()
  } else {
    openConfirm(
      'Quit Voucher?',
      'Discard current voucher and return to Gateway?',
      () => router.push('/'),
      () => {}
    )
  }
}

const handleFieldKeyDown = (e, fieldName) => {
  if (activeDropdownField.value === fieldName && dropdownMatches.value.length) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      dropdownIndex.value = (dropdownIndex.value + 1) % dropdownMatches.value.length
      return
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      dropdownIndex.value = (dropdownIndex.value - 1 + dropdownMatches.value.length) % dropdownMatches.value.length
      return
    } else if (e.key === 'Enter') {
      e.preventDefault()
      selectDropdownMatch(dropdownMatches.value[dropdownIndex.value])
      return
    }
  }

  if (e.key === 'Enter' || (e.key === 'Tab' && !e.shiftKey)) {
    e.preventDefault()
    activeDropdownField.value = null
    advanceFieldFrom(fieldName)
  } else if (e.key === 'Tab' && e.shiftKey) {
    e.preventDefault()
    retreatFieldFrom(fieldName)
  } else if (e.key === 'Escape') {
    e.preventDefault()
    if (activeDropdownField.value) {
      activeDropdownField.value = null
      return
    }
    if (form[fieldName]) {
      form[fieldName] = ''
    } else {
      retreatFieldFrom(fieldName)
    }
  }
}

const handleRowKeyDown = (e, idx, col) => {
  if (col === 'ledger' && activeDropdownField.value === `row-${idx}-ledger` && dropdownMatches.value.length) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      dropdownIndex.value = (dropdownIndex.value + 1) % dropdownMatches.value.length
      return
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      dropdownIndex.value = (dropdownIndex.value - 1 + dropdownMatches.value.length) % dropdownMatches.value.length
      return
    } else if (e.key === 'Enter') {
      e.preventDefault()
      selectDropdownMatch(dropdownMatches.value[dropdownIndex.value])
      return
    }
  }

  if (e.key === 'Enter') {
    e.preventDefault()
    activeDropdownField.value = null
    if (col === 'ledger') {
      if (rowRefs[idx]?.amount) rowRefs[idx].amount.focus()
    } else if (col === 'amount') {
      if (idx === form.additional_rows.length - 1 && form.additional_rows[idx].amount) {
        form.additional_rows.push({ ledger: '', amount: '' })
        nextTick(() => {
          if (rowRefs[idx + 1]?.ledger) rowRefs[idx + 1].ledger.focus()
        })
      } else {
        const el = document.querySelector('[data-field="narration"]')
        if (el) el.focus()
      }
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    if (activeDropdownField.value) {
      activeDropdownField.value = null
      return
    }
    const el = document.querySelector('[data-field="narration"]')
    if (el) el.focus()
  }
}

const handleNarrationKeyDown = (e) => {
  if (e.key === 'Enter') {
    e.preventDefault()
    promptAcceptVoucher()
  } else if (e.key === 'Escape') {
    e.preventDefault()
    retreatFieldFrom('narration')
  }
}

const promptAcceptVoucher = () => {
  const title = `Accept ${currentConfig.value.title}?`
  const party = form.supplier || form.customer_name || form.customer || form.bank_account || 'Ledger'
  const totalStr = formatCurrency(grandTotal.value)
  const body = `Save this <b>${currentConfig.value.title}</b> for <b>${party}</b> with Total <b>₹${totalStr}</b> to Frappe?`

  openConfirm(
    title,
    body,
    async () => {
      try {
        const res = await saveVoucher(currentConfig.value.doctype, {
          ...form,
          company: defaultCompany.value,
          grand_total: grandTotal.value,
        }, 1)

        showToast(`✅ ${res.message || 'Saved successfully'}`)
        router.push('/daybook')
      } catch (err) {
        showToast(`⚠️ Save error: ${err.message}`)
      }
    },
    () => {
      const el = document.querySelector('[data-field="narration"]')
      if (el) el.focus()
    }
  )
}

onMounted(() => {
  calcPurchaseTotal()
  calcDispatchTotal()
  nextTick(() => {
    const seq = getFieldSequence()
    const firstField = seq[1] || 'date'
    const el = document.querySelector(`[data-field="${firstField}"]`)
    if (el) el.focus()
  })
})
</script>
