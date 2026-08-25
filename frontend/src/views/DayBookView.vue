<template>
  <div id="main-layout">
    <div id="content-area">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
        <div>
          <div class="v-title" style="margin-bottom: 0;">
            Day Book &amp; Audit Register — {{ activeFilterLabel }}
          </div>
          <div style="font-size: 12.5px; color: var(--muted);">Live chronological journal audit stream across all voucher entries</div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <div style="font-size: 13px; color: var(--muted); margin-right: 6px;">
            Total Records: <strong style="color: var(--navy);">{{ entries.length }}</strong>
          </div>

          <!-- Print Day Book Button -->
          <button
            class="btn-tool"
            title="Print Formatted Day Book"
            @click="printDayBook"
          >
            <span>🖨️</span> Print Day Book
          </button>

          <!-- Export Day Book CSV Button -->
          <button
            class="btn-tool"
            title="Export Day Book to CSV"
            @click="exportDayBookCSV"
          >
            <span>📥</span> Export CSV
          </button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { globalUiState, showToast } from '../composables/useKeyboardEngine'
import { downloadCSV, printFormattedHtml } from '../composables/useExport'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { getDayBook, bootState } = useFrappeApi()

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

// -------------------------------------------------------------
// PRINT & CSV EXPORT FOR DAY BOOK
// -------------------------------------------------------------
const printDayBook = () => {
  let totalDebit = 0
  let totalCredit = 0

  const rowsHtml = entries.value.map((r) => {
    totalDebit += Number(r.debit || 0)
    totalCredit += Number(r.credit || 0)
    return `
      <tr>
        <td class="font-mono">${r.date}</td>
        <td class="font-bold">${r.voucher_type}</td>
        <td class="font-bold">${r.particulars}</td>
        <td>${r.details || '—'}</td>
        <td class="text-right font-mono val-green">${r.debit ? '₹' + formatCurrency(r.debit) : '—'}</td>
        <td class="text-right font-mono val-red">${r.credit ? '₹' + formatCurrency(r.credit) : '—'}</td>
        <td class="text-center font-bold">${r.status || 'Draft'}</td>
      </tr>
    `
  }).join('')

  const html = `
    <div style="margin-bottom: 12px; font-size: 13px; color: #475569;">
      <strong>Filter Scope:</strong> ${activeFilterLabel.value} · <strong>Total Records:</strong> ${entries.value.length}
    </div>
    <table>
      <thead>
        <tr>
          <th style="width: 12%;">Date</th>
          <th style="width: 18%;">Voucher Type</th>
          <th style="width: 24%;">Account / Party</th>
          <th style="width: 20%;">Details / Narration</th>
          <th style="width: 13%; text-align: right;">Debit (₹)</th>
          <th style="width: 13%; text-align: right;">Credit (₹)</th>
          <th style="width: 10%; text-align: center;">Status</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml || '<tr><td colspan="7" class="text-center">No transactions recorded</td></tr>'}
      </tbody>
      <tfoot>
        <tr style="background: #f1f5f9; font-weight: bold;">
          <td colspan="4" class="text-right">TOTAL TRANSACTION TURNOVER:</td>
          <td class="text-right font-mono val-green">₹${formatCurrency(totalDebit)}</td>
          <td class="text-right font-mono val-red">₹${formatCurrency(totalCredit)}</td>
          <td></td>
        </tr>
      </tfoot>
    </table>
  `
  printFormattedHtml(`Day Book & Audit Register (${activeFilterLabel.value})`, html, bootState.default_company || 'Mahalaxmi Sugar Mills Pvt. Ltd.')
}

const exportDayBookCSV = () => {
  const headers = ['Date', 'Voucher Type', 'Particulars / Account', 'Details / Narration', 'Debit (INR)', 'Credit (INR)', 'Status']
  const rows = [headers]
  let totalDebit = 0
  let totalCredit = 0

  entries.value.forEach((r) => {
    const d = Number(r.debit || 0)
    const c = Number(r.credit || 0)
    totalDebit += d
    totalCredit += c
    rows.push([r.date, r.voucher_type, r.particulars, r.details || '', d, c, r.status || 'Draft'])
  })

  rows.push([])
  rows.push(['TOTALS', '', '', '', totalDebit, totalCredit, ''])

  const dateStr = new Date().toISOString().slice(0, 10)
  downloadCSV(`Day_Book_${dateStr}.csv`, rows)
  showToast('Exported Day Book to CSV')
}

const daybookMenuItems = [
  { key: 'F2', label: 'Filter by Date', action: () => { globalUiState.isDateModalOpen.value = true } },
  { key: 'F4', label: 'Filter by Type', action: () => toggleTypeFilter() },
  { key: 'A', label: 'Show All Records', action: () => showAll() },
  { key: 'P', label: 'New Purchase (F9)', action: () => router.push('/voucher/purchase') },
  { key: 'D', label: 'New Dispatch (F8)', action: () => router.push('/voucher/dispatch') },
  { key: 'Y', label: 'New Payment (F5)', action: () => router.push('/voucher/payment') },
  { key: 'F7', label: 'Print Day Book', action: () => printDayBook() },
  { key: 'E', label: 'Export to CSV', action: () => exportDayBookCSV() },
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

<style scoped>
.btn-tool {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
  user-select: none;
}

.btn-tool:hover {
  background: var(--panel-soft);
  border-color: var(--blue);
  color: var(--blue);
}
</style>
