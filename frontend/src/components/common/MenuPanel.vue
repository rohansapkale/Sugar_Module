<template>
  <div id="tally-sidebar">
    <!-- Category Switcher Tabs at Top (M = Masters, V = Vouchers, R = Reports, ALL) -->
    <div class="category-tabs-container">
      <div
        :class="['cat-tab', { active: currentCategory === 'ALL' }]"
        @click="setCategory('ALL')"
        title="Show All Sections"
      >
        ALL
      </div>
      <div
        :class="['cat-tab', { active: currentCategory === 'MASTERS' }]"
        @click="setCategory('MASTERS')"
        title="Press 'M' for Masters"
      >
        MASTERS (M)
      </div>
      <div
        :class="['cat-tab', { active: currentCategory === 'VOUCHERS' }]"
        @click="setCategory('VOUCHERS')"
        title="Press 'V' for Vouchers"
      >
        VOUCHERS (V)
      </div>
      <div
        :class="['cat-tab', { active: currentCategory === 'REPORTS' }]"
        @click="setCategory('REPORTS')"
        title="Press 'R' for Reports"
      >
        REPORTS (R)
      </div>
    </div>

    <!-- 1. MASTERS SECTION -->
    <div v-if="currentCategory === 'ALL' || currentCategory === 'MASTERS'" class="sidebar-section">
      <div class="section-title-gold">
        <span>MASTERS</span>
        <span class="category-hint-badge">M</span>
      </div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/register/supplier')">
          <span class="label">Sugar Mills / Suppliers</span>
          <span class="key-gold">S</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/broker')">
          <span class="label">Brokers Directory</span>
          <span class="key-gold">B</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/customer')">
          <span class="label">Customer Parties</span>
          <span class="key-gold">C</span>
        </div>
        <div class="sidebar-row" @click="navigate('/masters')">
          <span class="label">Sugar Items &amp; Grades</span>
          <span class="key-gold">I</span>
        </div>
        <div class="sidebar-row" @click="navigate('/masters')">
          <span class="label">Masters Directory</span>
          <span class="key-gold">M</span>
        </div>
      </div>
    </div>

    <!-- 2. VOUCHERS SECTION (P, D, Y, R, T) -->
    <div v-if="currentCategory === 'ALL' || currentCategory === 'VOUCHERS'" class="sidebar-section">
      <div class="section-title-gold">
        <span>VOUCHERS</span>
        <span class="category-hint-badge">V</span>
      </div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/voucher/purchase')">
          <span class="label">Purchase</span>
          <span class="key-gold">P</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/dispatch')">
          <span class="label">Dispatch</span>
          <span class="key-gold">D</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/payment')">
          <span class="label">Payment Entry</span>
          <span class="key-gold">Y</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/receipt')">
          <span class="label">Receipt Entry</span>
          <span class="key-gold">R</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/contra')">
          <span class="label">Contra / Bank Transfer</span>
          <span class="key-gold">T</span>
        </div>
      </div>
    </div>

    <!-- 3. REPORTS SECTION -->
    <div v-if="currentCategory === 'ALL' || currentCategory === 'REPORTS'" class="sidebar-section">
      <div class="section-title-gold">
        <span>REPORTS</span>
        <span class="category-hint-badge">R</span>
      </div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/register/purchase')">
          <span class="label">Purchase Register (Lots)</span>
          <span class="key-gold">L</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/dispatch')">
          <span class="label">Dispatch Register</span>
          <span class="key-gold">K</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/broker-outstanding')">
          <span class="label">Broker Receivables (Outstanding)</span>
          <span class="key-gold">O</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/supplier-outstanding')">
          <span class="label">Supplier Payables (Outstanding)</span>
          <span class="key-gold">S</span>
        </div>
        <div class="sidebar-row" @click="navigate('/daybook')">
          <span class="label">Day Book &amp; Audit Register</span>
          <span class="key-gold">B</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { globalUiState, showToast } from '../../composables/useKeyboardEngine'

const router = useRouter()

const currentCategory = computed(() => {
  return globalUiState.activeSidebarCategory.value || 'ALL'
})

const setCategory = (cat) => {
  globalUiState.activeSidebarCategory.value = cat
  showToast(`Category: ${cat}`)
}

const navigate = (route) => {
  if (route) {
    router.push(route)
  }
}
</script>

<style scoped>
#tally-sidebar {
  width: 285px;
  background: #081a33;
  color: #ffffff;
  padding: 12px 0 20px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.category-tabs-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 0 14px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cat-tab {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.cat-tab:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  border-color: #facc15;
}

.cat-tab.active {
  background: #facc15;
  color: #081a33;
  border-color: #facc15;
  font-weight: 800;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
}

.section-title-gold {
  color: #facc15;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 0 18px 5px;
  border-bottom: 1px solid rgba(250, 204, 21, 0.35);
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-hint-badge {
  background: rgba(250, 204, 21, 0.2);
  color: #facc15;
  border: 1px solid rgba(250, 204, 21, 0.4);
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-family: monospace;
}

.sidebar-items-list {
  display: flex;
  flex-direction: column;
}

.sidebar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 18px;
  cursor: pointer;
  transition: background 0.12s ease;
  user-select: none;
}

.sidebar-row:hover {
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-row .label {
  font-size: 12.5px;
  font-weight: 500;
  color: #f1f5f9;
  letter-spacing: 0.2px;
}

.sidebar-row .key-gold {
  color: #facc15;
  font-weight: 800;
  font-family: monospace;
  font-size: 13px;
}
</style>
