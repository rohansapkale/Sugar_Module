<template>
  <div id="main-layout">
    <div id="content-area">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div class="v-title" style="margin-bottom: 0;">
          Masters Directory — {{ currentTabLabel }}
        </div>
        <div style="width: 240px;">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search party / ledger..."
            style="width: 100%; padding: 6px 10px; font-size: 13px; border: 1px solid var(--blue); border-radius: 4px; outline: none;"
            @input="filterMasters"
          />
        </div>
      </div>

      <!-- Tab Buttons -->
      <div style="display: flex; gap: 8px; margin-bottom: 14px;">
        <button
          v-for="t in tabs"
          :key="t.type"
          :style="{
            padding: '6px 14px',
            fontSize: '13px',
            fontWeight: activeTab === t.type ? '700' : '500',
            background: activeTab === t.type ? 'var(--navy)' : 'var(--panel)',
            color: activeTab === t.type ? '#fff' : 'var(--text)',
            border: '1px solid var(--line)',
            borderRadius: '4px',
            cursor: 'pointer'
          }"
          @click="setTab(t.type)"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- Masters Table -->
      <table class="daybook-table">
        <thead>
          <tr>
            <th style="width: 30%;">Name / Code</th>
            <th style="width: 40%;">Display Label</th>
            <th style="width: 30%;">Category / Group</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, idx) in filteredItems" :key="item.id || idx" class="daybook-row">
            <td style="font-weight: 600; font-family: monospace;">{{ item.name }}</td>
            <td>{{ item.label }}</td>
            <td style="color: var(--muted);">{{ item.type || item.doctype }}</td>
          </tr>
          <tr v-if="!filteredItems.length">
            <td colspan="3" style="text-align: center; padding: 20px; color: var(--muted);">
              No records found for "{{ searchQuery }}"
            </td>
          </tr>
        </tbody>
      </table>

      <div class="keyboard-hint" style="margin-top: 18px;">
        <span><kbd>Esc</kbd> Return to Gateway</span>
        <span><kbd>Alt+G</kbd> Jump to Voucher</span>
      </div>
    </div>

    <!-- Right Side Menu -->
    <MenuPanel
      section-title="Masters Menu"
      :items="mastersMenuItems"
      :active-index="activeMenuIndex"
      @select="handleMenuSelect"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { searchLedgers } = useFrappeApi()

const activeTab = ref('Supplier')
const searchQuery = ref('')
const allItems = ref([])
const activeMenuIndex = ref(0)

const tabs = [
  { type: 'Supplier', label: 'Suppliers (Mills)' },
  { type: 'Customer', label: 'Customers (Buyers)' },
  { type: 'Broker', label: 'Brokers' },
  { type: 'Item', label: 'Items & Sugar Grades' },
  { type: 'Account', label: 'Bank & Cash Accounts' },
]

const currentTabLabel = computed(() => {
  const found = tabs.find(t => t.type === activeTab.value)
  return found ? found.label : 'Masters'
})

const filteredItems = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return allItems.value
  return allItems.value.filter(i =>
    i.name.toLowerCase().includes(q) ||
    i.label.toLowerCase().includes(q)
  )
})

const setTab = async (type) => {
  activeTab.value = type
  searchQuery.value = ''
  allItems.value = await searchLedgers('', type)
}

const mastersMenuItems = [
  { key: 'P', label: 'Sugar Purchase (F9)', action: () => router.push('/voucher/purchase') },
  { key: 'D', label: 'Dispatch Entry (F8)', action: () => router.push('/voucher/dispatch') },
  { key: 'B', label: 'Day Book (F10)', action: () => router.push('/daybook') },
  { key: 'Esc', label: 'Gateway Menu', action: () => router.push('/') },
]

const handleMenuSelect = (idx) => {
  activeMenuIndex.value = idx
  mastersMenuItems[idx].action()
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape') {
    e.preventDefault()
    router.push('/')
  }
}

onMounted(() => {
  setTab('Supplier')
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
