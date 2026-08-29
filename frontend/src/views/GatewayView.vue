<template>
  <div id="main-layout">
    <div id="content-area" style="background: var(--bg); padding: 18px 24px; overflow-y: auto;">
      <!-- Dashboard Top Header Section -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 14px;">
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

      <!-- UNIVERSAL GLOBAL SEARCH BAR (ABOVE KPI METRIC CARDS) -->
      <div class="dashboard-search-container" ref="searchContainerRef">
        <div class="dashboard-search-wrap">
          <div :class="['dashboard-search-box', { active: isSearchOpen }]">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>

            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              class="dashboard-search-input"
              placeholder="Search anything — masters, vouchers, references or reports..."
              autocomplete="off"
              @focus="onSearchFocus"
              @input="onSearchInput"
              @keydown="handleSearchKeyDown"
            />

            <div class="ctrl-g-badge" title="Press Ctrl+G to focus search" @click="focusSearchInput">
              Ctrl+G
            </div>
          </div>

          <div class="search-hint-text">
            <span>← Press <i>Ctrl+G</i> to focus search</span>
          </div>
        </div>

        <!-- Live Search Results Dropdown Overlay -->
        <div v-if="isSearchOpen && (searchResults.length > 0 || isSearching || (searchQuery.trim().length >= 1 && !isSearching))" class="search-dropdown-menu">
          <div class="search-dropdown-header">
            <span>🔍 Universal Database Results for "<b>{{ searchQuery }}</b>"</span>
            <span class="results-count">{{ searchResults.length }} items found</span>
          </div>

          <div v-if="isSearching" class="search-loading-row">
            <span class="spinner">⏳</span> Searching Frappe database...
          </div>

          <div v-else-if="searchResults.length === 0" class="search-empty-row">
            <span>No matching transactions, masters, or reports found</span>
          </div>

          <div v-else class="search-results-list">
            <div
              v-for="(item, idx) in searchResults"
              :key="item.id || idx"
              :class="['search-result-item', { active: activeResultIndex === idx }]"
              @mousedown.prevent="selectSearchResult(item)"
              @mouseover="activeResultIndex = idx"
            >
              <div class="res-icon">{{ item.icon || '📄' }}</div>
              <div class="res-body">
                <div class="res-title-row">
                  <span class="res-title">{{ item.title }}</span>
                  <span class="res-category-tag">{{ item.category }}</span>
                </div>
                <div class="res-subtitle">{{ item.subtitle }}</div>
              </div>
              <div class="res-action-hint">↵ Open</div>
            </div>
          </div>

          <div class="search-dropdown-footer">
            <span><kbd>↑</kbd> <kbd>↓</kbd> Navigate</span>
            <span><kbd>Enter</kbd> Open in View Mode</span>
            <span><kbd>Esc</kbd> Close</span>
          </div>
        </div>
      </div>

      <!-- Metric Cards Grid (Tiered 3-Row Layout) -->
      <div class="metrics-grid-container">
        <!-- Row 1: 4 Cards (Stock & Sales Quantities) -->
        <div class="metrics-grid-4">
          <!-- 1. Opening Stock -->
          <div class="metric-card">
            <div class="card-icon-box bg-green-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Opening Stock (Qty.)</div>
              <div class="card-value">{{ formatQty(metrics.opening_stock_qty) }} <span class="unit">Qtl</span></div>
            </div>
          </div>

          <!-- 2. Today's Purchases -->
          <div class="metric-card">
            <div class="card-icon-box bg-blue-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Today's Purchases (Qty.)</div>
              <div class="card-value">{{ formatQty(metrics.today_purchases_qty) }} <span class="unit">Qtl</span></div>
            </div>
          </div>

          <!-- 3. Total Sales -->
          <div class="metric-card">
            <div class="card-icon-box bg-orange-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2">
                <rect x="1" y="3" width="15" height="13"></rect>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                <circle cx="5.5" cy="18.5" r="2.5"></circle>
                <circle cx="18.5" cy="18.5" r="2.5"></circle>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Total Sales (Qty.)</div>
              <div class="card-value">{{ formatQty(metrics.total_sales_qty) }} <span class="unit">Qtl</span></div>
            </div>
          </div>

          <!-- 4. Closing Stock -->
          <div class="metric-card">
            <div class="card-icon-box bg-green-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Closing Stock (Qty.)</div>
              <div class="card-value">{{ formatQty(metrics.closing_stock_qty) }} <span class="unit">Qtl</span></div>
            </div>
          </div>
        </div>

        <!-- Row 2: 2 Cards (Valuations) -->
        <div class="metrics-grid-2">
          <!-- 5. Purchases Value -->
          <div class="metric-card">
            <div class="card-icon-box bg-purple-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#9333ea" stroke-width="2">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Purchases (Val.)</div>
              <div class="card-value">{{ formatCurrency(metrics.purchases_val) }}</div>
            </div>
          </div>

          <!-- 6. Sales Value -->
          <div class="metric-card">
            <div class="card-icon-box bg-teal-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0d9488" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Sales (Val.)</div>
              <div class="card-value">{{ formatCurrency(metrics.sales_val) }}</div>
            </div>
          </div>
        </div>

        <!-- Row 3: 4 Cards (Cashflow & Outstandings) -->
        <div class="metrics-grid-4">
          <!-- 7. Payments Received -->
          <div class="metric-card">
            <div class="card-icon-box bg-green-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 14 14"></polyline>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Payments Received</div>
              <div class="card-value">{{ formatCurrency(metrics.payments_received) }}</div>
            </div>
          </div>

          <!-- 8. Payments Made -->
          <div class="metric-card">
            <div class="card-icon-box bg-blue-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Payments Made</div>
              <div class="card-value">{{ formatCurrency(metrics.payments_made) }}</div>
            </div>
          </div>

          <!-- 9. Total Receivable -->
          <div class="metric-card">
            <div class="card-icon-box bg-cyan-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0891b2" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Total Receivable</div>
              <div class="card-value">{{ formatCurrency(metrics.total_receivable) }}</div>
            </div>
          </div>

          <!-- 10. Total Payable -->
          <div class="metric-card">
            <div class="card-icon-box bg-rose-light">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e11d48" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-label">Total Payable</div>
              <div class="card-value">{{ formatCurrency(metrics.total_payable) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tally Right Side Menu -->
    <MenuPanel />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast, globalUiState } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getGatewayMetrics, universalGlobalSearch } = useFrappeApi()

const selectedFY = ref('2026-27')
const activePeriod = ref('Today')

// Metrics Reactive State
const metrics = reactive({
  opening_stock_qty: 0,
  today_purchases_qty: 0,
  total_sales_qty: 0,
  closing_stock_qty: 0,
  purchases_val: 0,
  sales_val: 0,
  payments_received: 0,
  payments_made: 0,
  total_receivable: 0,
  total_payable: 0,
})

// -------------------------------------------------------------
// UNIVERSAL GLOBAL SEARCH STATE & METHODS
// -------------------------------------------------------------
const searchQuery = ref('')
const searchResults = ref([])
const isSearchOpen = ref(false)
const isSearching = ref(false)
const activeResultIndex = ref(0)
const searchInputRef = ref(null)
const searchContainerRef = ref(null)
let searchTimer = null

const onSearchFocus = () => {
  isSearchOpen.value = true
  if (searchQuery.value.trim().length >= 1) {
    executeSearch()
  }
}

const onSearchInput = () => {
  isSearchOpen.value = true
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    executeSearch()
  }, 120)
}

const executeSearch = async () => {
  const q = searchQuery.value.trim()
  if (!q) {
    searchResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true
  try {
    const res = await universalGlobalSearch(q)
    searchResults.value = res || []
    activeResultIndex.value = 0
  } catch (e) {
    console.error('Universal search error:', e)
  } finally {
    isSearching.value = false
  }
}

const focusSearchInput = () => {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
    searchInputRef.value.select()
    isSearchOpen.value = true
  }
}

const selectSearchResult = (item) => {
  if (!item) return
  isSearchOpen.value = false

  if (item.externalUrl) {
    window.location.href = item.externalUrl
  } else if (item.route) {
    router.push(item.route)
  }

  showToast(`Opening: ${item.title}`)
}

const handleSearchKeyDown = (e) => {
  if (!isSearchOpen.value || !searchResults.value.length) {
    if (e.key === 'Escape') {
      isSearchOpen.value = false
      if (searchInputRef.value) searchInputRef.value.blur()
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeResultIndex.value = (activeResultIndex.value + 1) % searchResults.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeResultIndex.value = (activeResultIndex.value - 1 + searchResults.value.length) % searchResults.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    selectSearchResult(searchResults.value[activeResultIndex.value])
  } else if (e.key === 'Escape') {
    e.preventDefault()
    isSearchOpen.value = false
    if (searchInputRef.value) searchInputRef.value.blur()
  }
}

const handleClickOutside = (e) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target)) {
    isSearchOpen.value = false
  }
}

// -------------------------------------------------------------
// METRIC FORMATTING HELPERS
// -------------------------------------------------------------
const formatQty = (val) => {
  const num = Number(val) || 0
  return num.toLocaleString('en-IN')
}

const formatCurrency = (val) => {
  const num = Number(val) || 0
  if (num >= 10000000) {
    return '₹ ' + (num / 10000000).toFixed(2) + ' Cr'
  } else if (num >= 100000) {
    return '₹ ' + (num / 100000).toFixed(2) + ' L'
  }
  return '₹ ' + num.toLocaleString('en-IN', { maximumFractionDigits: 2 })
}

const loadData = async () => {
  try {
    const res = await getGatewayMetrics(activePeriod.value)
    if (res) {
      metrics.opening_stock_qty = res.opening_stock_qty || 0
      metrics.today_purchases_qty = res.today_purchases_qty || 0
      metrics.total_sales_qty = res.total_sales_qty || 0
      metrics.closing_stock_qty = res.closing_stock_qty || 0
      metrics.purchases_val = res.purchases_val || 0
      metrics.sales_val = res.sales_val || 0
      metrics.payments_received = res.payments_received || 0
      metrics.payments_made = res.payments_made || 0
      metrics.total_receivable = res.total_receivable || 0
      metrics.total_payable = res.total_payable || 0
    }
  } catch (e) {
    console.error('Error loading gateway metrics:', e)
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

const handleKeyDown = (e) => {
  // 1. Ctrl+G / Ctrl+K / '/' to focus search input
  const isGKey = e.key === 'g' || e.key === 'G' || e.code === 'KeyG'
  const isKKey = e.key === 'k' || e.key === 'K' || e.code === 'KeyK'

  if ((e.ctrlKey && (isGKey || isKKey)) || (e.altKey && isGKey)) {
    e.preventDefault()
    e.stopPropagation()
    focusSearchInput()
    return
  }

  if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
    e.preventDefault()
    focusSearchInput()
    return
  }

  // If typing in input, ignore flat shortcuts
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return

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
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  document.removeEventListener('click', handleClickOutside)
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
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.fd-logo-text {
  color: #facc15;
  font-weight: 900;
  font-size: 16px;
  letter-spacing: -0.5px;
  line-height: 1;
}

.fd-leaf-icon {
  position: absolute;
  bottom: 2px;
  right: 2px;
}

.gateway-main-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--navy);
  margin: 0;
  letter-spacing: -0.3px;
}

body.dark-mode .gateway-main-title {
  color: #f8fafc;
}

.fy-selector-box {
  background: var(--card-bg);
  border: 1px solid var(--border);
  padding: 6px 14px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.fy-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 12.5px;
  color: var(--text);
  cursor: pointer;
}

.fy-range {
  font-size: 11px;
  color: var(--muted);
  margin-top: 1px;
}

.period-toggle-group {
  display: flex;
  background: #081a36;
  padding: 3px;
  border-radius: 6px;
  gap: 2px;
}

.period-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.period-btn.active {
  background: #ffffff;
  color: #081a36;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* DASHBOARD GLOBAL SEARCH BAR */
.dashboard-search-container {
  margin-bottom: 20px;
  position: relative;
  z-index: 50;
}

.dashboard-search-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-search-box {
  flex: 1;
  max-width: 620px;
  display: flex;
  align-items: center;
  background: var(--card-bg);
  border: 1px solid #16a34a;
  border-radius: 6px;
  padding: 7px 14px;
  gap: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

.dashboard-search-box.active,
.dashboard-search-box:focus-within {
  border-color: #22c55e;
  box-shadow: 0 4px 16px rgba(34, 197, 94, 0.18);
}

.dashboard-search-box .search-icon {
  stroke: #64748b;
  flex-shrink: 0;
}

.dashboard-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
  width: 100%;
}

.dashboard-search-input::placeholder {
  color: var(--muted);
  font-size: 12.5px;
}

.ctrl-g-badge {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #cbd5e1;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
  font-family: inherit;
  transition: all 0.15s ease;
}

body.dark-mode .ctrl-g-badge {
  background: #1e293b;
  color: #cbd5e1;
  border-color: #334155;
}

.ctrl-g-badge:hover {
  background: #e2e8f0;
  border-color: #94a3b8;
}

.search-hint-text {
  color: #16a34a;
  font-size: 13px;
  font-weight: 500;
  font-style: italic;
  white-space: nowrap;
}

body.dark-mode .search-hint-text {
  color: #4ade80;
}

/* SEARCH DROPDOWN OVERLAY */
.search-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  max-width: 620px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  overflow: hidden;
  max-height: 420px;
  display: flex;
  flex-direction: column;
}

body.dark-mode .search-dropdown-menu {
  background: #111c2e;
  border-color: #2b3d5c;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
}

.search-dropdown-header {
  padding: 8px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 11.5px;
  color: #475569;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

body.dark-mode .search-dropdown-header {
  background: #0f1827;
  border-color: #1e293b;
  color: #94a3b8;
}

.results-count {
  font-weight: 700;
  color: #2563eb;
  font-size: 11px;
}

.search-results-list {
  overflow-y: auto;
  max-height: 320px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.12s ease;
}

body.dark-mode .search-result-item {
  border-color: #1e293b;
}

.search-result-item:hover,
.search-result-item.active {
  background: #f0fdf4;
}

body.dark-mode .search-result-item:hover,
body.dark-mode .search-result-item.active {
  background: #142a1e;
}

.res-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.res-body {
  flex: 1;
  min-width: 0;
}

.res-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.res-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

body.dark-mode .res-title {
  color: #f8fafc;
}

.res-category-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

body.dark-mode .res-category-tag {
  background: #1e293b;
  color: #94a3b8;
}

.res-subtitle {
  font-size: 11.5px;
  color: #64748b;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

body.dark-mode .res-subtitle {
  color: #94a3b8;
}

.res-action-hint {
  font-size: 11px;
  color: #16a34a;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.search-result-item.active .res-action-hint,
.search-result-item:hover .res-action-hint {
  opacity: 1;
}

.search-loading-row,
.search-empty-row {
  padding: 20px;
  text-align: center;
  font-size: 12.5px;
  color: #64748b;
}

.search-dropdown-footer {
  padding: 6px 14px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 11px;
  color: #64748b;
  display: flex;
  gap: 14px;
}

body.dark-mode .search-dropdown-footer {
  background: #0f1827;
  border-color: #1e293b;
  color: #94a3b8;
}

/* METRICS GRID STYLES */
.metrics-grid-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metrics-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.metrics-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

@media (max-width: 1100px) {
  .metrics-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .metrics-grid-4,
  .metrics-grid-2 {
    grid-template-columns: 1fr;
  }
}

.metric-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bg-green-light { background: #dcfce7; }
.bg-blue-light { background: #dbeafe; }
.bg-orange-light { background: #ffedd5; }
.bg-purple-light { background: #f3e8ff; }
.bg-teal-light { background: #ccfbf1; }
.bg-cyan-light { background: #cffafe; }
.bg-rose-light { background: #ffe4e6; }

body.dark-mode .bg-green-light { background: rgba(22, 163, 74, 0.2); }
body.dark-mode .bg-blue-light { background: rgba(37, 99, 235, 0.2); }
body.dark-mode .bg-orange-light { background: rgba(234, 88, 12, 0.2); }
body.dark-mode .bg-purple-light { background: rgba(147, 51, 234, 0.2); }
body.dark-mode .bg-teal-light { background: rgba(13, 148, 136, 0.2); }
body.dark-mode .bg-cyan-light { background: rgba(8, 145, 178, 0.2); }
body.dark-mode .bg-rose-light { background: rgba(225, 29, 72, 0.2); }

.card-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.card-label {
  font-size: 12.5px;
  color: var(--muted);
  font-weight: 600;
  margin-bottom: 4px;
  white-space: nowrap;
}

.card-value {
  font-size: 19px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.1;
  white-space: nowrap;
}

.card-value .unit {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  margin-left: 2px;
}
</style>
