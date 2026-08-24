<template>
  <div id="main-layout">
    <div id="content-area">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div class="v-title" style="margin-bottom: 0;">
          Day Book &amp; Audit Register — {{ activeFilterLabel }}
        </div>
        <div style="font-size: 13px; color: var(--muted);">
          Total Records: <strong style="color: var(--navy);">{{ entries.length }}</strong>
        </div>
      </div>

      <!-- Unified Transactions Table -->
      <table v-if="entries.length" class="daybook-table">
        <thead>
          <tr>
            <th style="width: 100px;">Date</th>
            <th style="width: 150px;">Voucher Type</th>
            <th style="width: 220px;">Account / Party</th>
            <th>Details / Ref</th>
            <th style="width: 110px; text-align: right;">Debit (₹)</th>
            <th style="width: 110px; text-align: right;">Credit (₹)</th>
            <th style="width: 90px; text-align: center;">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in entries"
            :key="row.id || idx"
            :class="['daybook-row', { hi: activeRowIndex === idx }]"
            @click="selectRow(idx)"
            @dblclick="openVoucher(row)"
          >
            <td style="font-family: monospace; font-size: 12.5px;">{{ row.date }}</td>
            <td>
              <span style="font-weight: 600;">{{ row.voucher_type }}</span>
              <span style="font-size: 11px; margin-left: 5px; color: var(--amber); font-weight: 700;">{{ row.fk_code }}</span>
            </td>
            <td style="font-weight: 600;">{{ row.particulars }}</td>
            <td style="color: var(--muted); font-size: 12.5px;">{{ row.details }}</td>
            <td style="text-align: right; font-family: monospace; font-weight: 600; color: var(--green);">
              {{ row.debit ? formatCurrency(row.debit) : '-' }}
            </td>
            <td style="text-align: right; font-family: monospace; font-weight: 600; color: var(--red);">
              {{ row.credit ? formatCurrency(row.credit) : '-' }}
            </td>
            <td style="text-align: center;">
              <span :class="['status-badge', (row.status || 'Draft').toLowerCase()]" style="font-size: 10px;">
                {{ row.status || 'Draft' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 30px; text-align: center; color: var(--muted); margin-top: 20px;">
        <div style="font-size: 28px; margin-bottom: 8px;">📭</div>
        <p style="font-size: 14px; margin-bottom: 6px;">No records found for the current filter</p>
        <p style="font-size: 12.5px;">Press <kbd>F9</kbd> for Purchase, <kbd>F8</kbd> for Dispatch, or <kbd>F4</kbd> to change filter.</p>
      </div>

      <div class="keyboard-hint" style="margin-top: 18px;">
        <span><kbd>↑</kbd> <kbd>↓</kbd> Browse Rows</span>
        <span><kbd>Enter</kbd> Open Voucher</span>
        <span><kbd>F2</kbd> Filter by Date</span>
        <span><kbd>F4</kbd> Filter by Type</span>
        <span><kbd>Esc</kbd> Return to Gateway</span>
      </div>
    </div>

    <!-- Right Side Menu -->
    <MenuPanel
      section-title="Day Book Menu"
      :items="daybookMenuItems"
      :active-index="activeMenuIndex"
      @select="handleMenuSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { globalUiState, showToast } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getDayBook } = useFrappeApi()

const entries = ref([])
const activeRowIndex = ref(0)
const activeMenuIndex = ref(0)
const selectedFilterType = ref(null)
const selectedFilterDate = ref('')

const activeFilterLabel = computed(() => {
  const parts = []
  if (selectedFilterType.value) parts.push(selectedFilterType.value)
  else parts.push('All Transactions')
  if (selectedFilterDate.value) parts.push(selectedFilterDate.value)
  else parts.push('(Recent)')
  return parts.join(' — ')
})

const formatCurrency = (val) => {
  return Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const loadEntries = async () => {
  entries.value = await getDayBook(selectedFilterDate.value, selectedFilterType.value)
  if (activeRowIndex.value >= entries.value.length) {
    activeRowIndex.value = Math.max(0, entries.value.length - 1)
  }
}

const selectRow = (idx) => {
  activeRowIndex.value = idx
}

const openVoucher = (row) => {
  showToast(`Opening ${row.voucher_type} (${row.name})`)
  if (row.voucher_type === 'Sugar Purchase') router.push('/voucher/purchase')
  else if (row.voucher_type === 'Dispatch Entry') router.push('/voucher/dispatch')
  else if (row.voucher_type === 'Purchase Payment') router.push('/voucher/payment')
  else if (row.voucher_type === 'Broker Party Payment') router.push('/voucher/receipt')
  else router.push('/voucher/purchase')
}

const daybookMenuItems = [
  { key: 'F2', label: 'Filter by Date', action: () => { globalUiState.isDateModalOpen.value = true } },
  { key: 'F4', label: 'Filter by Type', action: () => toggleTypeFilter() },
  { key: 'A', label: 'Show All Records', action: () => showAll() },
  { key: 'P', label: 'New Purchase (F9)', action: () => router.push('/voucher/purchase') },
  { key: 'D', label: 'New Dispatch (F8)', action: () => router.push('/voucher/dispatch') },
  { key: 'Y', label: 'New Payment (F5)', action: () => router.push('/voucher/payment') },
  { key: 'Esc', label: 'Gateway Menu', action: () => router.push('/') },
]

const toggleTypeFilter = () => {
  const types = [null, 'Sugar Purchase', 'Dispatch Entry', 'Purchase Payment', 'Broker Party Payment']
  const curIdx = types.indexOf(selectedFilterType.value)
  selectedFilterType.value = types[(curIdx + 1) % types.length]
  showToast(`Filter: ${selectedFilterType.value || 'All Types'}`)
  loadEntries()
}

const showAll = () => {
  selectedFilterType.value = null
  selectedFilterDate.value = ''
  showToast('Showing all recent transactions')
  loadEntries()
}

const handleMenuSelect = (idx) => {
  activeMenuIndex.value = idx
  daybookMenuItems[idx].action()
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (entries.value.length) {
      activeRowIndex.value = (activeRowIndex.value + 1) % entries.value.length
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (entries.value.length) {
      activeRowIndex.value = (activeRowIndex.value - 1 + entries.value.length) % entries.value.length
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (entries.value[activeRowIndex.value]) {
      openVoucher(entries.value[activeRowIndex.value])
    }
  } else if (e.key === 'Escape') {
    e.preventDefault()
    router.push('/')
  }
}

onMounted(() => {
  loadEntries()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
