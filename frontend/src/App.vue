<template>
  <div id="app">
    <TopBar />
    <ScreenTitle :title="currentTitle" :status="currentStatus" />
    <router-view />
    <FunctionKeyBar />

    <!-- Modals & Overlays -->
    <ConfirmModal />
    <GoToPalette />
    <HelpModal />
    <DateModal />
    <Toast />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useFrappeApi } from './composables/useFrappeApi'
import { useKeyboardEngine } from './composables/useKeyboardEngine'
import TopBar from './components/common/TopBar.vue'
import ScreenTitle from './components/common/ScreenTitle.vue'
import FunctionKeyBar from './components/common/FunctionKeyBar.vue'
import ConfirmModal from './components/common/ConfirmModal.vue'
import GoToPalette from './components/common/GoToPalette.vue'
import HelpModal from './components/common/HelpModal.vue'
import DateModal from './components/common/DateModal.vue'
import Toast from './components/common/Toast.vue'

const route = useRoute()
const { initBoot, bootState } = useFrappeApi()
useKeyboardEngine()

const currentTitle = computed(() => {
  if (route.name === 'Gateway') return `Gateway — ${bootState.default_company || 'Mahalaxmi Sugar Mills Pvt. Ltd.'}`
  if (route.name === 'DayBook') return 'Day Book & Transaction Audit Register'
  if (route.name === 'Masters') return 'Sugar Module Masters & Accounts'
  if (route.name === 'Register') {
    const type = route.params.type
    const titles = {
      purchase: 'Sugar Purchase Register — Full List of Purchases',
      dispatch: 'Dispatch Entry Register — Full List of Sales & Dispatches',
      payment: 'Purchase Payment Register — Supplier Payments List',
      receipt: 'Broker Party Payment Register — Customer Receipts List',
    }
    return titles[type] || 'Register List'
  }
  if (route.name === 'VoucherEntry') {
    const type = route.params.type
    const titles = {
      purchase: 'Accounting Voucher — Sugar Purchase (F9)',
      dispatch: 'Accounting Voucher — Dispatch Entry (Sales) (F8)',
      payment: 'Accounting Voucher — Purchase Payment (Supplier) (F5)',
      receipt: 'Accounting Voucher — Broker Party Payment (Receipt) (F6)',
      contra: 'Accounting Voucher — Contra / Bank Transfer (F4)',
    }
    return titles[type] || 'Accounting Voucher Entry'
  }
  return 'Sugar Desk'
})

const currentStatus = computed(() => {
  if (route.name === 'VoucherEntry') return 'Draft'
  return ''
})

onMounted(() => {
  initBoot()
})
</script>
