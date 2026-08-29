<template>
  <div id="main-layout">
    <div id="content-area">
      <!-- Header Section -->
      <div class="v-header-section">
        <div>
          <div class="v-title">{{ isReadOnly ? `View ${currentConfig.title}` : currentConfig.title }}</div>
          <div style="font-size: 12.5px; margin-top: 3px; display: flex; align-items: center; gap: 8px;">
            <span v-if="isReadOnly" class="status-pill readonly-status">
              🔒 View Mode (Uneditable / Submitted) — {{ voucherId }}
            </span>
            <span v-else style="color: var(--navy); font-weight: 600;">
              Status: <span style="font-family: monospace; color: var(--blue);">Draft / New</span>
            </span>
          </div>
        </div>

        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <!-- Print Voucher Button -->
          <button
            v-if="isReadOnly"
            type="button"
            class="btn-header-tool"
            title="Print this Voucher Document"
            @click="printSingleVoucher"
          >
            <span>🖨️</span> Print Voucher
          </button>

          <!-- New Voucher Button (when in View Mode) -->
          <button
            v-if="isReadOnly"
            type="button"
            class="btn-header-tool"
            title="Create New Voucher"
            @click="createNewVoucher"
          >
            <span>➕</span> New Voucher
          </button>

          <!-- Register Navigation Shortcuts -->
          <button
            v-if="voucherType === 'purchase'"
            type="button"
            class="btn-header-tool"
            @click="router.push('/register/purchase')"
          >
            📋 Purchases List (<kbd>Esc</kbd>)
          </button>
          <button
            v-else-if="voucherType === 'dispatch'"
            type="button"
            class="btn-header-tool"
            @click="router.push('/register/dispatch')"
          >
            📋 Dispatches List (<kbd>Esc</kbd>)
          </button>
          <button
            v-else-if="voucherType === 'payment'"
            type="button"
            class="btn-header-tool"
            @click="router.push('/register/payment')"
          >
            📋 Payments List (<kbd>Esc</kbd>)
          </button>
          <button
            v-else-if="voucherType === 'receipt'"
            type="button"
            class="btn-header-tool"
            @click="router.push('/register/receipt')"
          >
            📋 Receipts List (<kbd>Esc</kbd>)
          </button>
        </div>
      </div>

      <!-- Base Meta Fields -->
      <div class="field-grid">
        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
          <label>Voucher Date</label>
          <div class="input-control-wrap">
            <input
              ref="field_date"
              v-model="form.date"
              type="date"
              data-field="date"
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @keydown="handleFieldKeyDown($event, 'date')"
            />
          </div>
        </div>

        <div class="field-row disabled">
          <label>Company</label>
          <div class="input-control-wrap">
            <input type="text" :value="defaultCompany" readonly disabled />
          </div>
        </div>
      </div>

      <!-- 1. SUGAR PURCHASE (F9) -->
      <div v-if="voucherType === 'purchase'">
        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
          <label>Supplier (Sugar Mill)</label>
          <div class="input-control-wrap">
            <input
              ref="field_supplier"
              v-model="form.supplier"
              type="text"
              placeholder="Select sugar mill / supplier..."
              autocomplete="off"
              data-field="supplier"
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @focus="onLedgerFocus('supplier', 'Supplier')"
              @input="onLedgerInput('supplier', 'Supplier')"
              @keydown="handleFieldKeyDown($event, 'supplier')"
            />
            <LedgerDropdown
              v-if="!isReadOnly && activeDropdownField === 'supplier'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Sugar Item / Grade</label>
            <div class="input-control-wrap">
              <input
                ref="field_item"
                v-model="form.item"
                type="text"
                placeholder="Select item (e.g. S-302526, M30)..."
                autocomplete="off"
                data-field="item"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('item', 'Item')"
                @input="onLedgerInput('item', 'Item')"
                @keydown="handleFieldKeyDown($event, 'item')"
              />
              <LedgerDropdown
                v-if="!isReadOnly && activeDropdownField === 'item'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Qty (Quintals)</label>
            <div class="input-control-wrap">
              <input
                ref="field_qty"
                v-model.number="form.purchase_qty_quintal"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="qty"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @input="calcPurchaseTotal"
                @keydown="handleFieldKeyDown($event, 'qty')"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Purchase Rate (₹/Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_rate"
                v-model.number="form.purchase_rate"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="rate"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @input="calcPurchaseTotal"
                @keydown="handleFieldKeyDown($event, 'rate')"
              />
            </div>
          </div>

          <div class="field-row disabled">
            <label>Total Sugar Amount</label>
            <div class="input-control-wrap">
              <input type="text" :value="'₹' + formatCurrency(form.total_amount)" readonly disabled style="font-weight: 700; color: var(--navy);" />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. DISPATCH ENTRY (F8) -->
      <div v-else-if="voucherType === 'dispatch'">
        <!-- Sugar Purchase Lot Selector -->
        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
          <label>Source Sugar Purchase</label>
          <div class="input-control-wrap">
            <input
              ref="field_sugar_purchase"
              v-model="form.sugar_purchase"
              type="text"
              placeholder="Select source Sugar Purchase lot (Mill / Voucher No)..."
              autocomplete="off"
              data-field="sugar_purchase"
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @focus="onLedgerFocus('sugar_purchase', 'Sugar Purchase')"
              @input="onLedgerInput('sugar_purchase', 'Sugar Purchase')"
              @keydown="handleFieldKeyDown($event, 'sugar_purchase')"
            />
            <LedgerDropdown
              v-if="!isReadOnly && activeDropdownField === 'sugar_purchase'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <!-- Selected Purchase Lot Live Stock Info Banner -->
        <div v-if="selectedPurchaseLot" style="background: var(--panel-soft); border-left: 3px solid var(--blue); padding: 8px 12px; margin-bottom: 12px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
          <span>🏭 Mill: <strong style="color: var(--navy);">{{ selectedPurchaseLot.supplier }}</strong> · Grade: <strong>{{ selectedPurchaseLot.item }}</strong> · Lot Qty: <strong>{{ selectedPurchaseLot.purchase_qty_quintal }} Qtl</strong></span>
          <span>Stock Available: <strong style="color: var(--green); font-size: 13.5px;">{{ selectedPurchaseLot.available_qty_quintal }} Qtl</strong></span>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Customer Party</label>
            <div class="input-control-wrap">
              <input
                ref="field_customer"
                v-model="form.customer_name"
                type="text"
                placeholder="Select customer party..."
                autocomplete="off"
                data-field="customer_name"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('customer_name', 'Customer')"
                @input="onLedgerInput('customer_name', 'Customer')"
                @keydown="handleFieldKeyDown($event, 'customer_name')"
              />
              <LedgerDropdown
                v-if="!isReadOnly && activeDropdownField === 'customer_name'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Broker Name</label>
            <div class="input-control-wrap">
              <input
                ref="field_broker"
                v-model="form.broker"
                type="text"
                placeholder="Select broker..."
                autocomplete="off"
                data-field="broker"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('broker', 'Broker')"
                @input="onLedgerInput('broker', 'Broker')"
                @keydown="handleFieldKeyDown($event, 'broker')"
              />
              <LedgerDropdown
                v-if="!isReadOnly && activeDropdownField === 'broker'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Vehicle No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_vehicle_no"
                v-model="form.vehicle_no"
                type="text"
                placeholder="e.g. MH19CZ1234"
                data-field="vehicle_no"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @keydown="handleFieldKeyDown($event, 'vehicle_no')"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Sugar Item / Grade</label>
            <div class="input-control-wrap">
              <input
                ref="field_item"
                v-model="form.item"
                type="text"
                placeholder="Grade (S-30, M30)..."
                data-field="item"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @keydown="handleFieldKeyDown($event, 'item')"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Dispatch Qty (Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_qty"
                v-model.number="form.dispatch_qty_quintal"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="qty"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @input="calcDispatchTotal"
                @keydown="handleFieldKeyDown($event, 'qty')"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Rate (₹/Qtl)</label>
            <div class="input-control-wrap">
              <input
                ref="field_rate"
                v-model.number="form.rate"
                type="number"
                step="0.01"
                placeholder="0.00"
                data-field="rate"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @input="calcDispatchTotal"
                @keydown="handleFieldKeyDown($event, 'rate')"
              />
            </div>
          </div>
        </div>

        <div class="field-row disabled">
          <label>Total Dispatch Amount</label>
          <div class="input-control-wrap">
            <input type="text" :value="'₹' + formatCurrency(form.total_amount)" readonly disabled style="font-weight: 700; color: var(--navy);" />
          </div>
        </div>
      </div>

      <!-- 3. PURCHASE PAYMENT (F5) -->
      <div v-else-if="voucherType === 'payment'">
        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
          <label>Source Sugar Purchase</label>
          <div class="input-control-wrap">
            <input
              ref="field_sugar_purchase_pay"
              v-model="form.sugar_purchase"
              type="text"
              placeholder="Select Sugar Purchase lot being paid..."
              autocomplete="off"
              data-field="sugar_purchase_pay"
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @focus="onLedgerFocus('sugar_purchase_pay', 'Sugar Purchase')"
              @input="onLedgerInput('sugar_purchase_pay', 'Sugar Purchase')"
              @keydown="handleFieldKeyDown($event, 'sugar_purchase_pay')"
            />
            <LedgerDropdown
              v-if="!isReadOnly && activeDropdownField === 'sugar_purchase_pay'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Sugar Mill (Supplier)</label>
            <div class="input-control-wrap">
              <input
                ref="field_supplier"
                v-model="form.supplier"
                type="text"
                placeholder="Sugar Mill Name..."
                data-field="supplier"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('supplier', 'Supplier')"
                @input="onLedgerInput('supplier', 'Supplier')"
                @keydown="handleFieldKeyDown($event, 'supplier')"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Bank / Cash Account</label>
            <div class="input-control-wrap">
              <input
                ref="field_bank"
                v-model="form.bank_account"
                type="text"
                placeholder="Select Bank / Cash Account..."
                data-field="bank_account"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('bank_account', 'Account')"
                @input="onLedgerInput('bank_account', 'Account')"
                @keydown="handleFieldKeyDown($event, 'bank_account')"
              />
              <LedgerDropdown
                v-if="!isReadOnly && activeDropdownField === 'bank_account'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Payment Mode</label>
            <div class="input-control-wrap">
              <input
                ref="field_mode"
                v-model="form.payment_mode"
                type="text"
                placeholder="RTGS, NEFT, Cheque, UPI..."
                data-field="payment_mode"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @keydown="handleFieldKeyDown($event, 'payment_mode')"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>UTR / Ref No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_utr"
                v-model="form.utr_no"
                type="text"
                placeholder="UTR / Ref No."
                data-field="utr_no"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @keydown="handleFieldKeyDown($event, 'utr_no')"
              />
            </div>
          </div>
        </div>

        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
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
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @keydown="handleFieldKeyDown($event, 'paid_amount')"
            />
          </div>
        </div>
      </div>

      <!-- 4. BROKER RECEIPT (F6) -->
      <div v-else-if="voucherType === 'receipt'">
        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
          <label>Source Dispatch Entry</label>
          <div class="input-control-wrap">
            <input
              ref="field_dispatch_entry"
              v-model="form.dispatch_entry"
              type="text"
              placeholder="Select Dispatch Entry being received..."
              autocomplete="off"
              data-field="dispatch_entry"
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @focus="onLedgerFocus('dispatch_entry', 'Dispatch Entry')"
              @input="onLedgerInput('dispatch_entry', 'Dispatch Entry')"
              @keydown="handleFieldKeyDown($event, 'dispatch_entry')"
            />
            <LedgerDropdown
              v-if="!isReadOnly && activeDropdownField === 'dispatch_entry'"
              :matches="dropdownMatches"
              :active-index="dropdownIndex"
              @select="selectDropdownMatch"
              @hover="dropdownIndex = $event"
            />
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Customer Party</label>
            <div class="input-control-wrap">
              <input
                ref="field_customer"
                v-model="form.customer_name"
                type="text"
                placeholder="Customer Party..."
                data-field="customer_name"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('customer_name', 'Customer')"
                @input="onLedgerInput('customer_name', 'Customer')"
                @keydown="handleFieldKeyDown($event, 'customer_name')"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Broker Name</label>
            <div class="input-control-wrap">
              <input
                ref="field_broker"
                v-model="form.broker"
                type="text"
                placeholder="Broker Name..."
                data-field="broker"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('broker', 'Broker')"
                @input="onLedgerInput('broker', 'Broker')"
                @keydown="handleFieldKeyDown($event, 'broker')"
              />
            </div>
          </div>
        </div>

        <div class="field-grid">
          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>Deposit Account (Bank/Cash)</label>
            <div class="input-control-wrap">
              <input
                ref="field_bank"
                v-model="form.bank_account"
                type="text"
                placeholder="Select Bank / Cash Account..."
                data-field="bank_account"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @focus="onLedgerFocus('bank_account', 'Account')"
                @input="onLedgerInput('bank_account', 'Account')"
                @keydown="handleFieldKeyDown($event, 'bank_account')"
              />
              <LedgerDropdown
                v-if="!isReadOnly && activeDropdownField === 'bank_account'"
                :matches="dropdownMatches"
                :active-index="dropdownIndex"
                @select="selectDropdownMatch"
                @hover="dropdownIndex = $event"
              />
            </div>
          </div>

          <div :class="['field-row', { 'readonly-row': isReadOnly }]">
            <label>UTR / Ref No.</label>
            <div class="input-control-wrap">
              <input
                ref="field_utr"
                v-model="form.utr_no"
                type="text"
                placeholder="UTR / Ref No."
                data-field="utr_no"
                :readonly="isReadOnly"
                :disabled="isReadOnly"
                @keydown="handleFieldKeyDown($event, 'utr_no')"
              />
            </div>
          </div>
        </div>

        <div :class="['field-row', { 'readonly-row': isReadOnly }]">
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
              :readonly="isReadOnly"
              :disabled="isReadOnly"
              @keydown="handleFieldKeyDown($event, 'paid_amount')"
            />
          </div>
        </div>
      </div>

      <!-- Narration Section -->
      <div :class="['field-row', { 'readonly-row': isReadOnly }]" style="margin-top: 14px;">
        <label>Narration</label>
        <div class="input-control-wrap">
          <textarea
            ref="field_narration"
            v-model="form.narration"
            rows="2"
            placeholder="Enter narration notes for this voucher..."
            data-field="narration"
            :readonly="isReadOnly"
            :disabled="isReadOnly"
            @keydown="handleNarrationKeyDown"
          ></textarea>
        </div>
      </div>

      <!-- Action & Accept Bar -->
      <div v-if="!isReadOnly" style="display: flex; justify-content: flex-end; margin-top: 16px;">
        <button
          type="button"
          class="btn-save-voucher"
          @click="promptAcceptVoucher"
        >
          <span>💾</span> Save &amp; Accept Voucher (Enter)
        </button>
      </div>

      <div v-else style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px;">
        <div style="color: var(--muted); font-size: 12.5px;">
          Press <kbd>Esc</kbd> to return to Register list.
        </div>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn-tool" @click="printSingleVoucher">
            <span>🖨️</span> Print Voucher
          </button>
          <button type="button" class="btn-save-voucher" @click="createNewVoucher">
            <span>➕</span> New Voucher Entry
          </button>
        </div>
      </div>

      <!-- Keyboard Cues Hint -->
      <div class="keyboard-hint" style="margin-top: 16px;">
        <span><kbd>Tab</kbd> / <kbd>Enter</kbd> Navigate</span>
        <span><kbd>Esc</kbd> {{ isReadOnly ? 'Return to Register' : 'Clear / Discard' }}</span>
        <span v-if="!isReadOnly"><kbd>Enter</kbd> on Narration → <b>Accept</b></span>
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
import { printFormattedHtml } from '../composables/useExport'
import MenuPanel from '../components/common/MenuPanel.vue'
import LedgerDropdown from '../components/common/LedgerDropdown.vue'

const route = useRoute()
const router = useRouter()
const { bootState, searchLedgers, saveVoucher, getVoucherDetails } = useFrappeApi()

const voucherType = computed(() => route.params.type || 'purchase')
const voucherId = computed(() => route.query.id || '')
const isReadOnly = computed(() => !!voucherId.value)
const defaultCompany = computed(() => bootState.default_company || 'Rajendra Narahari Lokhande')

const VOUCHER_CONFIGS = {
  purchase: { title: 'Sugar Purchase Voucher (P)', doctype: 'Sugar Purchase', registerRoute: '/register/purchase' },
  dispatch: { title: 'Dispatch Entry Voucher (D)', doctype: 'Dispatch Entry', registerRoute: '/register/dispatch' },
  payment: { title: 'Purchase Payment Voucher (Y)', doctype: 'Purchase Payment', registerRoute: '/register/payment' },
  receipt: { title: 'Broker Party Payment (Receipt) (R)', doctype: 'Broker Party Payment', registerRoute: '/register/receipt' },
  contra: { title: 'Contra / Bank Transfer (T)', doctype: 'Account', registerRoute: '/register/purchase' },
}

const currentConfig = computed(() => VOUCHER_CONFIGS[voucherType.value] || VOUCHER_CONFIGS.purchase)

// Form State
const selectedPurchaseLot = ref(null)
const activeDropdownField = ref(null)
const dropdownMatches = ref([])
const dropdownIndex = ref(0)
let searchTimer = null

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
  return base
})

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatNumber = (val) => {
  return Number(val || 0).toLocaleString('en-IN')
}

// Side Menu Items
const voucherMenuItems = [
  { key: 'P', label: 'Purchase', route: '/voucher/purchase' },
  { key: 'D', label: 'Dispatch', route: '/voucher/dispatch' },
  { key: 'Y', label: 'Payment Entry', route: '/voucher/payment' },
  { key: 'R', label: 'Receipt Entry', route: '/voucher/receipt' },
  { key: 'T', label: 'Contra / Bank Transfer', route: '/voucher/contra' },
  { key: 'L', label: 'Purchase List', route: '/register/purchase' },
  { key: 'K', label: 'Dispatch List', route: '/register/dispatch' },
  { key: 'B', label: 'Day Book', route: '/daybook' },
  { key: 'Esc', label: 'Gateway Menu', route: '/' },
]

const activeVoucherIndex = computed(() => {
  return voucherMenuItems.findIndex(m => m.route === `/voucher/${voucherType.value}`)
})

const handleVoucherSelect = (idx) => {
  router.push(voucherMenuItems[idx].route)
}

// -------------------------------------------------------------
// LOAD EXISTING VOUCHER DETAILS FOR READ-ONLY VIEW
// -------------------------------------------------------------
const loadVoucherData = async () => {
  if (!voucherId.value) return

  try {
    const doc = await getVoucherDetails(currentConfig.value.doctype, voucherId.value)
    if (doc) {
      if (voucherType.value === 'purchase') {
        form.date = doc.purchase_date || doc.date || form.date
        form.supplier = doc.supplier || ''
        form.item = doc.item || 'S-30'
        form.purchase_qty_quintal = doc.purchase_qty_quintal || 0
        form.purchase_rate = doc.purchase_rate || 0
        form.total_amount = doc.total_amount || 0
        form.narration = doc.narration || doc.remarks || ''
      } else if (voucherType.value === 'dispatch') {
        form.date = doc.dispatch_date || doc.date || form.date
        form.sugar_purchase = doc.sugar_purchase || ''
        form.customer_name = doc.customer_name || doc.customer || ''
        form.broker = doc.broker || ''
        form.vehicle_no = doc.vehicle_no || ''
        form.item = doc.item || 'S-30'
        form.dispatch_qty_quintal = doc.dispatch_qty_quintal || 0
        form.rate = doc.rate || 0
        form.total_amount = doc.total_amount || 0
        form.narration = doc.narration || ''
      } else if (voucherType.value === 'payment') {
        form.date = doc.payment_date || doc.date || form.date
        form.sugar_purchase = doc.sugar_purchase || ''
        form.supplier = doc.supplier || ''
        form.bank_account = doc.bank_account || doc.paid_from || ''
        form.payment_mode = doc.mode_of_payment || 'RTGS'
        form.utr_no = doc.reference_no || ''
        form.paid_amount = doc.paid_amount || 0
        form.narration = doc.narration || ''
      } else if (voucherType.value === 'receipt') {
        form.date = doc.receipt_date || doc.date || form.date
        form.dispatch_entry = doc.dispatch_entry || ''
        form.customer_name = doc.customer_name || doc.customer || ''
        form.broker = doc.broker || ''
        form.bank_account = doc.bank_account || doc.paid_to || ''
        form.payment_mode = doc.mode_of_payment || 'Bank'
        form.utr_no = doc.reference_no || ''
        form.paid_amount = doc.received_amount || 0
        form.narration = doc.narration || ''
      }
      showToast(`Viewing ${voucherId.value} (Read-Only)`)
    }
  } catch (e) {
    showToast(`Failed to load voucher: ${e.message}`)
  }
}

const createNewVoucher = () => {
  router.push({ path: `/voucher/${voucherType.value}`, query: {} })
}

// -------------------------------------------------------------
// PRINT SINGLE VOUCHER
// -------------------------------------------------------------
const printSingleVoucher = () => {
  let detailsHtml = ''

  if (voucherType.value === 'purchase') {
    detailsHtml = `
      <table style="width: 100%; border-collapse: collapse; margin-top: 14px;">
        <thead>
          <tr>
            <th>Item / Sugar Grade</th>
            <th class="text-right">Quantity (Quintals)</th>
            <th class="text-right">Rate (₹/Qtl)</th>
            <th class="text-right">Total Amount (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="font-bold">${form.item}</td>
            <td class="text-right font-mono">${formatNumber(form.purchase_qty_quintal)} Qtl</td>
            <td class="text-right font-mono">₹${formatNumber(form.purchase_rate)}</td>
            <td class="text-right font-mono font-bold">₹${formatCurrency(form.total_amount)}</td>
          </tr>
        </tbody>
      </table>
    `
  } else if (voucherType.value === 'dispatch') {
    detailsHtml = `
      <table style="width: 100%; border-collapse: collapse; margin-top: 14px;">
        <thead>
          <tr>
            <th>Grade Item</th>
            <th>Vehicle No</th>
            <th>Broker</th>
            <th class="text-right">Quantity (Qtl)</th>
            <th class="text-right">Rate (₹)</th>
            <th class="text-right">Total Amount (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="font-bold">${form.item}</td>
            <td>${form.vehicle_no || '—'}</td>
            <td>${form.broker || '—'}</td>
            <td class="text-right font-mono">${formatNumber(form.dispatch_qty_quintal)} Qtl</td>
            <td class="text-right font-mono">₹${formatNumber(form.rate)}</td>
            <td class="text-right font-mono font-bold">₹${formatCurrency(form.total_amount)}</td>
          </tr>
        </tbody>
      </table>
    `
  } else {
    detailsHtml = `
      <table style="width: 100%; border-collapse: collapse; margin-top: 14px;">
        <thead>
          <tr>
            <th>Payment Mode</th>
            <th>UTR / Reference No</th>
            <th>Account</th>
            <th class="text-right">Total Amount (₹)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="font-bold">${form.payment_mode}</td>
            <td>${form.utr_no || '—'}</td>
            <td>${form.bank_account || '—'}</td>
            <td class="text-right font-mono font-bold">₹${formatCurrency(form.paid_amount)}</td>
          </tr>
        </tbody>
      </table>
    `
  }

  const html = `
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px 16px; margin-bottom: 14px;">
      <div style="display: flex; justify-content: space-between; font-size: 13px;">
        <div>
          <strong>Voucher ID:</strong> <span class="font-mono font-bold">${voucherId.value || 'NEW'}</span><br>
          <strong>Party:</strong> ${form.supplier || form.customer_name || '—'}
        </div>
        <div style="text-align: right;">
          <strong>Date:</strong> ${form.date}<br>
          <strong>Company:</strong> ${defaultCompany.value}
        </div>
      </div>
    </div>

    ${detailsHtml}

    <div style="margin-top: 14px; padding: 10px; background: #f8fafc; border-radius: 4px; font-size: 12px;">
      <strong>Narration:</strong> ${form.narration || 'No notes provided.'}
    </div>
  `

  printFormattedHtml(`${currentConfig.value.title} — ${voucherId.value || 'Voucher'}`, html, defaultCompany.value)
}

// -------------------------------------------------------------
// TYPEAHEAD & DROPDOWN HANDLING (DISABLED IN READ-ONLY)
// -------------------------------------------------------------
const onLedgerFocus = (fieldName, doctype) => {
  if (isReadOnly.value) return
  activeDropdownField.value = fieldName
  searchLedgersList('', doctype)
}

const onLedgerInput = (fieldName, doctype) => {
  if (isReadOnly.value) return
  activeDropdownField.value = fieldName
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    const q = form[fieldName] || ''
    searchLedgersList(q, doctype)
  }, 100)
}

const searchLedgersList = async (q, doctype) => {
  if (isReadOnly.value) return
  const matches = await searchLedgers(q, doctype)
  dropdownMatches.value = matches
  dropdownIndex.value = 0
}

const selectDropdownMatch = (item) => {
  if (isReadOnly.value || !item) return
  const fieldName = activeDropdownField.value

  if (fieldName === 'supplier') {
    form.supplier = item.name
  } else if (fieldName === 'item') {
    form.item = item.name
  } else if (fieldName === 'customer_name') {
    form.customer = item.name
    form.customer_name = item.label || item.name
  } else if (fieldName === 'broker') {
    form.broker = item.name
  } else if (fieldName === 'sugar_purchase' || fieldName === 'sugar_purchase_pay') {
    form.sugar_purchase = item.name
    if (item.supplier) form.supplier = item.supplier
    if (item.item) form.item = item.item
    if (item.available_qty_quintal !== undefined) {
      selectedPurchaseLot.value = item
    }
    if (fieldName === 'sugar_purchase_pay' && item.total_amount) {
      form.paid_amount = item.total_amount
    }
  } else if (fieldName === 'dispatch_entry') {
    form.dispatch_entry = item.name
    if (item.customer) {
      form.customer = item.customer
      form.customer_name = item.customer_name || item.customer
    }
    if (item.broker) form.broker = item.broker
    if (item.balance_amount !== undefined) form.paid_amount = item.balance_amount
  } else if (fieldName === 'bank_account') {
    form.bank_account = item.name
  }

  activeDropdownField.value = null
  advanceFieldFrom(fieldName)
}

// -------------------------------------------------------------
// FIELD KEYDOWN NAVIGATION
// -------------------------------------------------------------
const getFieldSequence = () => {
  if (voucherType.value === 'purchase') {
    return ['date', 'supplier', 'item', 'qty', 'rate', 'narration']
  }
  if (voucherType.value === 'dispatch') {
    return ['date', 'sugar_purchase', 'customer_name', 'broker', 'vehicle_no', 'item', 'qty', 'rate', 'narration']
  }
  if (voucherType.value === 'payment') {
    return ['date', 'sugar_purchase_pay', 'supplier', 'bank_account', 'payment_mode', 'utr_no', 'paid_amount', 'narration']
  }
  if (voucherType.value === 'receipt') {
    return ['date', 'dispatch_entry', 'customer_name', 'broker', 'bank_account', 'utr_no', 'paid_amount', 'narration']
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
  }
}

const handleFieldKeyDown = (e, fieldName) => {
  if (isReadOnly.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      router.push(currentConfig.value.registerRoute || '/register/purchase')
    }
    return
  }

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

  if (e.key === 'Enter') {
    e.preventDefault()
    activeDropdownField.value = null
    advanceFieldFrom(fieldName)
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

const handleNarrationKeyDown = (e) => {
  if (isReadOnly.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      router.push(currentConfig.value.registerRoute || '/register/purchase')
    }
    return
  }

  if (e.key === 'Enter') {
    e.preventDefault()
    promptAcceptVoucher()
  } else if (e.key === 'Escape') {
    e.preventDefault()
    retreatFieldFrom('narration')
  }
}

const promptAcceptVoucher = () => {
  if (isReadOnly.value) return

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
        router.push(currentConfig.value.registerRoute || '/daybook')
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

watch([() => route.params.type, () => route.query.id], () => {
  if (voucherId.value) {
    loadVoucherData()
  } else {
    // Reset form for fresh voucher entry
    form.supplier = ''
    form.customer = ''
    form.customer_name = ''
    form.broker = ''
    form.sugar_purchase = ''
    form.dispatch_entry = ''
    form.vehicle_no = ''
    form.narration = ''
    selectedPurchaseLot.value = null
  }
})

onMounted(() => {
  calcPurchaseTotal()
  calcDispatchTotal()
  if (voucherId.value) {
    loadVoucherData()
  } else {
    nextTick(() => {
      const seq = getFieldSequence()
      const firstField = seq[1] || 'date'
      const el = document.querySelector(`[data-field="${firstField}"]`)
      if (el) el.focus()
    })
  }
})
</script>

<style scoped>
.btn-header-tool {
  padding: 6px 12px;
  background: var(--panel);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
}

.btn-header-tool:hover {
  background: var(--panel-soft);
  border-color: var(--blue);
  color: var(--blue);
}

.btn-save-voucher {
  padding: 8px 18px;
  background: var(--blue);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

.btn-save-voucher:hover {
  background: #1d4ed8;
}

.readonly-status {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
}

.readonly-row input,
.readonly-row textarea {
  background: var(--panel-soft) !important;
  color: var(--text) !important;
  border-color: var(--line) !important;
  cursor: default !important;
  font-weight: 600 !important;
}

.readonly-row input:focus,
.readonly-row textarea:focus {
  border-color: var(--line) !important;
  box-shadow: none !important;
}
</style>
