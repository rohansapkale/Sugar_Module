<template>
  <div id="main-layout">
    <div id="content-area" style="background: var(--bg); padding: 18px 24px;">
      <!-- Dashboard Top Header Section -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 14px;">
        <!-- Left: Brand Logo & Title -->
        <div style="display: flex; align-items: center; gap: 14px;">
          <div class="fd-brand-badge">
            <span class="fd-logo-text">FD</span>
            <svg class="fd-leaf-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 20A7 7 0 0 1 4 13c0-4.418 3.582-8 8-8s8 3.582 8 8a7 7 0 0 1-7 7z"></path>
              <line x1="12" y1="9" x2="12" y2="15"></line>
            </svg>
          </div>
          <div>
            <h1 class="gateway-main-title">Gateway of Sugar</h1>
            <div class="gateway-subtitle">Tally-style ERP wrapper for Sugar Trading Business</div>
          </div>
        </div>

        <!-- Right: Financial Year & Period Toggle Buttons -->
        <div style="display: flex; align-items: center; gap: 14px;">
          <div class="fy-selector-box">
            <div class="fy-label">
              <span>Financial Year : {{ selectedFY }}</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div class="fy-range">1 Apr 2026 – 31 Mar 2027</div>
          </div>

          <!-- Period Toggle: Today / MTD -->
          <div class="period-toggle-group">
            <button
              :class="['period-btn', { active: activePeriod === 'Today' }]"
              @click="setPeriod('Today')"
            >
              Today
            </button>
            <button
              :class="['period-btn', { active: activePeriod === 'MTD' }]"
              @click="setPeriod('MTD')"
            >
              MTD
            </button>
          </div>
        </div>
      </div>

      <!-- Metric Cards Grid (Tiered 3-Row Layout) -->
      <div class="dashboard-grid-container">
        
        <!-- ROW 1: Quantities (Opening Stock, Today's Purchases, Total Sales) -->
        <div class="metrics-row-3">
          <!-- Card 1: Opening Stock -->
          <div class="metric-card" @click="router.push('/register/purchase')">
            <div class="icon-wrap green-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Opening Stock</div>
              <div class="card-value">
                <span class="val-num">{{ formatNumber(metrics.opening_stock) }}</span>
                <span class="val-unit">Qtl</span>
              </div>
            </div>
          </div>

          <!-- Card 2: Today's Purchases (Qty) -->
          <div class="metric-card" @click="router.push('/register/purchase')">
            <div class="icon-wrap blue-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Today's Purchases (Qty)</div>
              <div class="card-value">
                <span class="val-num">{{ formatNumber(metrics.today_purchases_qty) }}</span>
                <span class="val-unit">Qtl</span>
              </div>
            </div>
          </div>

          <!-- Card 3: Total Sales (Qty) -->
          <div class="metric-card" @click="router.push('/register/dispatch')">
            <div class="icon-wrap orange-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
                <path d="M4 4l6-2 6 6 4-2"></path>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Total Sales (Qty)</div>
              <div class="card-value">
                <span class="val-num">{{ formatNumber(metrics.total_sales_qty) }}</span>
                <span class="val-unit">Qtl</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ROW 2: Stock & Values (Closing Stock, Total Purchases Val, Total Sales Val) -->
        <div class="metrics-row-3">
          <!-- Card 4: Closing Stock (Qty.) -->
          <div class="metric-card" @click="router.push('/register/purchase')">
            <div class="icon-wrap green-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                <polyline points="2 17 12 22 22 17"></polyline>
                <polyline points="2 12 12 17 22 12"></polyline>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Closing Stock (Qty.)</div>
              <div class="card-value">
                <span class="val-num">{{ formatNumber(metrics.closing_stock) }}</span>
                <span class="val-unit">Qtl</span>
              </div>
            </div>
          </div>

          <!-- Card 5: Total Purchases (Value) -->
          <div class="metric-card" @click="router.push('/register/purchase')">
            <div class="icon-wrap purple-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Total Purchases (Value)</div>
              <div class="card-value">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.total_purchases_val).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.total_purchases_val).unit }}</span>
              </div>
            </div>
          </div>

          <!-- Card 6: Total Sales (Value) -->
          <div class="metric-card" @click="router.push('/register/dispatch')">
            <div class="icon-wrap amber-pastel">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label">Total Sales (Value)</div>
              <div class="card-value">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.total_sales_val).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.total_sales_val).unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ROW 3: Financial Cash Flows (Received, Paid, Receivable, Payable) -->
        <div class="metrics-row-4">
          <!-- Card 7: Total Payments Received -->
          <div class="metric-card mini" @click="router.push('/register/receipt')">
            <div class="icon-wrap green-pastel mini">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label mini">Total Payments Received</div>
              <div class="card-value mini">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.payments_received).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.payments_received).unit }}</span>
              </div>
            </div>
          </div>

          <!-- Card 8: Total Payments Made -->
          <div class="metric-card mini" @click="router.push('/register/payment')">
            <div class="icon-wrap red-pastel mini">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                <path d="M7 15h0M2 10h20"></path>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label mini">Total Payments Made</div>
              <div class="card-value mini">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.payments_made).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.payments_made).unit }}</span>
              </div>
            </div>
          </div>

          <!-- Card 9: Total Receivable -->
          <div class="metric-card mini highlight-purple" @click="router.push('/register/broker-outstanding')">
            <div class="icon-wrap purple-pastel mini circle">
              <span style="font-weight: 800; font-size: 14px; color: #9333ea;">₹</span>
            </div>
            <div class="metric-content">
              <div class="card-label mini">Total Receivable</div>
              <div class="card-value mini">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.total_receivable).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.total_receivable).unit }}</span>
              </div>
            </div>
          </div>

          <!-- Card 10: Total Payable -->
          <div class="metric-card mini" @click="router.push('/register/supplier-outstanding')">
            <div class="icon-wrap indigo-pastel mini">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div class="metric-content">
              <div class="card-label mini">Total Payable</div>
              <div class="card-value mini">
                <span class="val-currency">₹</span>
                <span class="val-num">{{ formatIndianValue(metrics.total_payable).num }}</span>
                <span class="val-unit">{{ formatIndianValue(metrics.total_payable).unit }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Right Side Menu Panel (Classic Tally Navy & Gold Theme) -->
    <MenuPanel
      :active-index="activeIndex"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast, globalUiState } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getGatewayMetrics } = useFrappeApi()

const selectedFY = ref('2026-27')
const activePeriod = ref('Today')
const activeIndex = ref(0)

const metrics = reactive({
  opening_stock: 0,
  today_purchases_qty: 0,
  total_sales_qty: 0,
  closing_stock: 0,
  total_purchases_val: 0,
  total_sales_val: 0,
  payments_received: 0,
  payments_made: 0,
  total_receivable: 0,
  total_payable: 0,
})

const formatNumber = (val) => {
  return Number(val || 0).toLocaleString('en-IN')
}

const formatIndianValue = (amount) => {
  const num = Number(amount || 0)
  if (num >= 10000000) {
    return { num: (num / 10000000).toFixed(2), unit: 'Cr' }
  } else if (num >= 100000) {
    return { num: (num / 100000).toFixed(2), unit: 'L' }
  } else if (num >= 1000) {
    return { num: (num / 1000).toFixed(2), unit: 'K' }
  }
  return { num: num.toFixed(2), unit: '' }
}

const loadData = async () => {
  try {
    const res = await getGatewayMetrics(activePeriod.value)
    if (res) {
      Object.assign(metrics, res)
    }
  } catch (e) {
    console.warn('Could not load live gateway metrics:', e)
  }
}

const setPeriod = (p) => {
  activePeriod.value = p
  showToast(`Filter: ${p}`)
  loadData()
}

// Global Menu items matching the sidebar
const flatMenuItems = [
  // Categories
  { key: 'M', action: () => { globalUiState.activeSidebarCategory.value = 'MASTERS'; showToast('🏛️ Masters (M)') } },
  { key: 'V', action: () => { globalUiState.activeSidebarCategory.value = 'VOUCHERS'; showToast('📝 Vouchers (V)') } },
  { key: 'R', action: () => { globalUiState.activeSidebarCategory.value = 'REPORTS'; showToast('📊 Reports (R)') } },
  // Vouchers (P, D, Y, R, T)
  { key: 'P', action: () => router.push('/voucher/purchase') },
  { key: 'D', action: () => router.push('/voucher/dispatch') },
  { key: 'Y', action: () => router.push('/voucher/payment') },
  { key: 'T', action: () => router.push('/voucher/contra') },
  // Masters
  { key: 'S', action: () => router.push('/register/supplier') },
  { key: 'B', action: () => router.push('/register/broker') },
  { key: 'C', action: () => router.push('/register/customer') },
  { key: 'I', action: () => router.push('/masters') },
  // Reports
  { key: 'L', action: () => router.push('/register/purchase') },
  { key: 'K', action: () => router.push('/register/dispatch') },
  { key: 'O', action: () => router.push('/register/broker-outstanding') },
  { key: 'F10', action: () => router.push('/daybook') },
]

const handleSelect = (idx) => {
  activeIndex.value = idx
  if (flatMenuItems[idx]) {
    flatMenuItems[idx].action()
  }
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return

  const key = e.key.toUpperCase()
  const found = flatMenuItems.find(m => m.key === key)
  if (found) {
    e.preventDefault()
    found.action()
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
.fd-brand-badge {
  background: #081a36;
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 2px 8px rgba(8, 26, 54, 0.25);
}

.fd-logo-text {
  font-weight: 900;
  font-size: 16px;
  color: #ffd479;
  letter-spacing: -0.5px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.fd-leaf-icon {
  position: absolute;
  bottom: 4px;
  right: 5px;
}

.gateway-main-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.2px;
  margin: 0;
}

.gateway-subtitle {
  font-size: 12.5px;
  color: var(--muted);
  margin-top: 2px;
}

.fy-selector-box {
  text-align: right;
}

.fy-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--navy);
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.fy-range {
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 1px;
}

.period-toggle-group {
  display: flex;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.period-btn {
  padding: 5px 14px;
  font-size: 12px;
  font-weight: 600;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.15s ease;
}

.period-btn.active {
  background: #081a36;
  color: #ffffff;
}

/* Dashboard Cards Layout */
.dashboard-grid-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metrics-row-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.metrics-row-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
  border-color: var(--blue);
}

.metric-card.mini {
  padding: 12px 14px;
  gap: 12px;
}

.icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-wrap.mini {
  width: 38px;
  height: 38px;
  border-radius: 8px;
}

.icon-wrap.circle {
  border-radius: 50%;
}

.green-pastel { background: #eef8f1; }
.blue-pastel { background: #eff6ff; }
.orange-pastel { background: #fff7ed; }
.purple-pastel { background: #f5f3ff; }
.amber-pastel { background: #fefce8; }
.red-pastel { background: #fef2f2; }
.indigo-pastel { background: #eef2ff; }

.metric-content {
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
}

.card-label.mini {
  font-size: 11.5px;
}

.card-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 4px;
}

.card-value.mini {
  margin-top: 2px;
}

.val-currency {
  font-size: 18px;
  font-weight: 700;
  color: var(--navy);
}

.val-num {
  font-size: 24px;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.5px;
}

.card-value.mini .val-num {
  font-size: 17px;
}

.val-unit {
  font-size: 14px;
  font-weight: 600;
  color: var(--muted);
  margin-left: 2px;
}

.card-value.mini .val-unit {
  font-size: 12px;
}
</style>
