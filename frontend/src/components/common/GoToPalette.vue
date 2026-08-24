<template>
  <div v-if="isOpen" class="goto-overlay" @click.self="close">
    <div class="goto-box">
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        placeholder="Go To — Type a voucher, report, or master name..."
        autocomplete="off"
        @keydown="handleKeyDown"
      />
      <div class="goto-list">
        <div
          v-for="(item, idx) in filteredItems"
          :key="idx"
          :class="{ hi: activeIndex === idx }"
          @click="selectItem(item)"
          @mouseover="activeIndex = idx"
        >
          <span>{{ item.title }}</span>
          <span class="tag">{{ item.shortcut || item.category }}</span>
        </div>
        <div v-if="!filteredItems.length" style="padding: 14px; text-align: center; color: var(--muted);">
          No matching views found
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { globalUiState } from '../../composables/useKeyboardEngine'

const router = useRouter()
const isOpen = computed(() => globalUiState.isGoToOpen.value)
const query = ref('')
const activeIndex = ref(0)
const inputRef = ref(null)

const MENU_COMMANDS = [
  { title: 'Sugar Purchase Entry (New Voucher)', route: '/voucher/purchase', shortcut: 'F9', category: 'Voucher' },
  { title: 'Dispatch Entry (Sales & Deliveries)', route: '/voucher/dispatch', shortcut: 'F8', category: 'Voucher' },
  { title: 'Purchase Payment (Supplier Payment)', route: '/voucher/payment', shortcut: 'F5', category: 'Voucher' },
  { title: 'Broker Party Payment (Customer Receipt)', route: '/voucher/receipt', shortcut: 'F6', category: 'Voucher' },
  { title: 'Contra / Bank Transfer', route: '/voucher/contra', shortcut: 'F4', category: 'Voucher' },
  { title: 'Sugar Purchase Register (List of Purchases)', route: '/register/purchase', shortcut: 'L', category: 'Register' },
  { title: 'Dispatch Entry Register (List of Dispatches)', route: '/register/dispatch', shortcut: 'K', category: 'Register' },
  { title: 'Suppliers & Sugar Mills Register (List)', route: '/register/supplier', shortcut: 'U', category: 'Register' },
  { title: 'Sugar Brokers Register (List)', route: '/register/broker', shortcut: 'B', category: 'Register' },
  { title: 'Customer Parties Register (List)', route: '/register/customer', shortcut: 'C', category: 'Register' },
  { title: 'Broker Receivables Report (Pending Dues)', route: '/register/broker-outstanding', shortcut: 'O', category: 'Report' },
  { title: 'Supplier Payables Report (Pending Dues)', route: '/register/supplier-outstanding', shortcut: 'S', category: 'Report' },
  { title: 'Purchase Payment Register (Supplier Payments List)', route: '/register/payment', shortcut: 'Y', category: 'Register' },
  { title: 'Broker Party Payment Register (Receipts List)', route: '/register/receipt', shortcut: 'R', category: 'Register' },
  { title: 'Day Book & Transaction Audit Register', route: '/daybook', shortcut: 'F10', category: 'Report' },
  { title: 'Gateway of Sugar Module', route: '/', shortcut: 'Esc', category: 'Navigation' },
  { title: 'Masters Directory (Suppliers, Customers, Brokers, Items)', route: '/masters', shortcut: 'M', category: 'Masters' },
]

const filteredItems = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return MENU_COMMANDS
  return MENU_COMMANDS.filter(item =>
    item.title.toLowerCase().includes(q) ||
    item.category.toLowerCase().includes(q) ||
    (item.shortcut && item.shortcut.toLowerCase().includes(q))
  )
})

watch(isOpen, (val) => {
  if (val) {
    query.value = ''
    activeIndex.value = 0
    nextTick(() => {
      if (inputRef.value) inputRef.value.focus()
    })
  }
})

const close = () => {
  globalUiState.isGoToOpen.value = false
}

const selectItem = (item) => {
  close()
  if (item.route) router.push(item.route)
}

const handleKeyDown = (e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % filteredItems.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value - 1 + filteredItems.value.length) % filteredItems.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (filteredItems.value[activeIndex.value]) {
      selectItem(filteredItems.value[activeIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    close()
  }
}
</script>
