<template>
  <div id="tally-sidebar">
    <!-- 1. MASTERS SECTION -->
    <div class="sidebar-section">
      <div class="section-title-gold">MASTERS</div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/register/supplier')">
          <span class="label">Sugar Mills / Suppliers</span>
          <span class="key-gold">S</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/broker')">
          <span class="label">Brokers / Customers</span>
          <span class="key-gold">B</span>
        </div>
        <div class="sidebar-row" @click="navigate('/masters')">
          <span class="label">Items</span>
          <span class="key-gold">I</span>
        </div>
        <div class="sidebar-row" @click="navigate('/masters')">
          <span class="label">Masters Directory</span>
          <span class="key-gold">M</span>
        </div>
      </div>
    </div>

    <!-- 2. VOUCHERS SECTION -->
    <div class="sidebar-section">
      <div class="section-title-gold">VOUCHERS</div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/voucher/purchase')">
          <span class="label">Purchase</span>
          <span class="key-gold">F9</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/dispatch')">
          <span class="label">Dispatch</span>
          <span class="key-gold">F8</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/payment')">
          <span class="label">Payment Entry</span>
          <span class="key-gold">F5</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/receipt')">
          <span class="label">Receipt Entry</span>
          <span class="key-gold">F6</span>
        </div>
        <div class="sidebar-row" @click="navigate('/voucher/contra')">
          <span class="label">Contra / Bank Transfer</span>
          <span class="key-gold">F4</span>
        </div>
      </div>
    </div>

    <!-- 3. REPORTS SECTION -->
    <div class="sidebar-section">
      <div class="section-title-gold">REPORTS</div>
      <div class="sidebar-items-list">
        <div class="sidebar-row" @click="navigate('/register/purchase')">
          <span class="label">Purchase Register (Lots)</span>
          <span class="key-gold">P</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/dispatch')">
          <span class="label">Dispatch Register</span>
          <span class="key-gold">D</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/broker-outstanding')">
          <span class="label">Broker Receivables (Outstanding)</span>
          <span class="key-gold">R</span>
        </div>
        <div class="sidebar-row" @click="navigate('/register/supplier-outstanding')">
          <span class="label">Supplier Payables (Outstanding)</span>
          <span class="key-gold">O</span>
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
import { useRouter } from 'vue-router'

const router = useRouter()

const navigate = (route) => {
  if (route) {
    router.push(route)
  }
}
</script>

<style scoped>
#tally-sidebar {
  width: 280px;
  background: #081a33;
  color: #ffffff;
  padding: 16px 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-section {
  display: flex;
  flex-direction: column;
}

.section-title-gold {
  color: #facc15;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 0 20px 6px;
  border-bottom: 1px solid rgba(250, 204, 21, 0.35);
  margin-bottom: 6px;
}

.sidebar-items-list {
  display: flex;
  flex-direction: column;
}

.sidebar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 20px;
  cursor: pointer;
  transition: background 0.12s ease;
  user-select: none;
}

.sidebar-row:hover {
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-row .label {
  font-size: 13px;
  font-weight: 500;
  color: #f1f5f9;
  letter-spacing: 0.2px;
}

.sidebar-row .key-gold {
  color: #facc15;
  font-weight: 800;
  font-family: monospace;
  font-size: 13.5px;
}
</style>
