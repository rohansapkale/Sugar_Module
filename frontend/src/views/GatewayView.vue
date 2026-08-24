<template>
  <div id="main-layout">
    <div id="content-area">
      <div style="max-width: 780px; padding: 10px 0;">
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px;">
          <div style="background: var(--navy); color: #fff; width: 44px; height: 44px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 22px;">
            🌾
          </div>
          <div>
            <h2 style="font-size: 18px; color: var(--navy); margin-bottom: 2px;">Gateway of Sugar Module</h2>
            <p style="font-size: 13px; color: var(--muted);">Tally-style keyboard accounting, vouchers &amp; live trade register desk</p>
          </div>
        </div>

        <!-- Row 1: Trade Registers & Master Directories -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 12px;">
          <div
            style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; transition: all 0.15s ease;"
            @click="router.push('/register/purchase')"
          >
            <div style="font-size: 11px; color: var(--muted); text-transform: uppercase;">Sugar Purchases 📋</div>
            <div style="font-size: 20px; font-weight: 700; color: var(--navy); margin-top: 4px;">{{ stats.sugar_purchases_count }}</div>
            <div style="font-size: 11px; color: var(--blue); margin-top: 2px;">Press <kbd>L</kbd> for list</div>
          </div>
          <div
            style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; transition: all 0.15s ease;"
            @click="router.push('/register/dispatch')"
          >
            <div style="font-size: 11px; color: var(--muted); text-transform: uppercase;">Dispatches 📋</div>
            <div style="font-size: 20px; font-weight: 700; color: var(--blue); margin-top: 4px;">{{ stats.dispatches_count }}</div>
            <div style="font-size: 11px; color: var(--blue); margin-top: 2px;">Press <kbd>K</kbd> for list</div>
          </div>
          <div
            style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; transition: all 0.15s ease;"
            @click="router.push('/register/supplier')"
          >
            <div style="font-size: 11px; color: var(--muted); text-transform: uppercase;">Sugar Mills / Suppliers 🏭</div>
            <div style="font-size: 20px; font-weight: 700; color: var(--green); margin-top: 4px;">{{ stats.suppliers_count }}</div>
            <div style="font-size: 11px; color: var(--green); margin-top: 2px;">Press <kbd>U</kbd> for mills</div>
          </div>
          <div
            style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; transition: all 0.15s ease;"
            @click="router.push('/register/broker')"
          >
            <div style="font-size: 11px; color: var(--muted); text-transform: uppercase;">Brokers 🤝</div>
            <div style="font-size: 20px; font-weight: 700; color: var(--amber); margin-top: 4px;">{{ stats.brokers_count }}</div>
            <div style="font-size: 11px; color: var(--amber); margin-top: 2px;">Press <kbd>B</kbd> for brokers</div>
          </div>
        </div>

        <!-- Row 2: Outstanding Financial Reports (Receivables & Payables) -->
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 18px;">
          <div
            style="background: #fff8f8; border: 1px solid #fecaca; border-radius: 6px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; display: flex; justify-content: space-between; align-items: center;"
            @click="router.push('/register/broker-outstanding')"
          >
            <div>
              <div style="font-size: 11px; color: var(--red); text-transform: uppercase; font-weight: 700;">Broker Receivables Report ⚠️</div>
              <div style="font-size: 15px; font-weight: 700; color: var(--red); margin-top: 2px;">Track Pending Dues from Brokers</div>
            </div>
            <div style="font-size: 11px; color: var(--red);">Press <kbd>O</kbd></div>
          </div>
          <div
            style="background: #fefce8; border: 1px solid #fde047; border-radius: 6px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); cursor: pointer; display: flex; justify-content: space-between; align-items: center;"
            @click="router.push('/register/supplier-outstanding')"
          >
            <div>
              <div style="font-size: 11px; color: var(--amber); text-transform: uppercase; font-weight: 700;">Supplier Payables Report 🏭</div>
              <div style="font-size: 15px; font-weight: 700; color: var(--amber); margin-top: 2px;">Track Outstanding Money to Mills</div>
            </div>
            <div style="font-size: 11px; color: var(--amber);">Press <kbd>S</kbd></div>
          </div>
        </div>

        <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 18px 20px; margin-bottom: 20px; line-height: 1.7; font-size: 13.5px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);">
          <p style="margin-bottom: 10px;">
            <strong>Welcome to Sugar Desk.</strong> Directly connected with your Frappe <code>sugar_module</code> database. Use single-key shortcuts or function keys to navigate rapidly without mouse interaction.
          </p>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px;">
            <div style="background: var(--blue-soft); padding: 10px 14px; border-radius: 4px; border-left: 3px solid var(--blue);">
              <div style="font-weight: 700; color: var(--navy); font-size: 13px;">⚡ Direct Vouchers</div>
              <div style="font-size: 12px; color: var(--muted); margin-top: 3px;">
                Press <kbd>P</kbd> (<kbd>F9</kbd>) for Purchase, <kbd>D</kbd> (<kbd>F8</kbd>) for Dispatch, <kbd>Y</kbd> (<kbd>F5</kbd>) for Payment.
              </div>
            </div>
            <div style="background: var(--amber-light); padding: 10px 14px; border-radius: 4px; border-left: 3px solid var(--amber);">
              <div style="font-weight: 700; color: var(--amber); font-size: 13px;">📋 Registers &amp; Reports</div>
              <div style="font-size: 12px; color: var(--muted); margin-top: 3px;">
                Press <kbd>U</kbd> for Suppliers, <kbd>B</kbd> for Brokers, <kbd>O</kbd> for Receivables, <kbd>S</kbd> for Payables.
              </div>
            </div>
          </div>
        </div>

        <div style="background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 14px 18px; font-size: 12.5px; color: var(--muted);">
          <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div>🏢 <strong>Company:</strong> {{ defaultCompany }}</div>
            <div>👤 <strong>User:</strong> {{ currentUser }}</div>
            <div>🔄 <strong>Status:</strong> Connected to Frappe DB</div>
          </div>
        </div>
      </div>
    </div>

    <MenuPanel
      section-title="Gateway of Sugar"
      :items="menuItems"
      :active-index="activeIndex"
      @select="handleSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../composables/useFrappeApi'
import { showToast } from '../composables/useKeyboardEngine'
import MenuPanel from '../components/common/MenuPanel.vue'

const router = useRouter()
const { bootState, getMastersSummary } = useFrappeApi()

const defaultCompany = computed(() => bootState.default_company || 'Rajendra Narahari Lokhande')
const currentUser = computed(() => bootState.full_name || bootState.user || 'Administrator')

const activeIndex = ref(0)
const stats = reactive({
  suppliers_count: 0,
  customers_count: 0,
  brokers_count: 0,
  items_count: 0,
  sugar_purchases_count: 0,
  dispatches_count: 0,
})

const loadStats = async () => {
  try {
    const s = await getMastersSummary()
    if (s) Object.assign(stats, s)
  } catch (e) {
    console.error('Failed to load stats:', e)
  }
}

const menuItems = [
  { key: 'P', label: 'Sugar Purchase Entry (F9)', action: () => router.push('/voucher/purchase') },
  { key: 'D', label: 'Dispatch Entry (F8)', action: () => router.push('/voucher/dispatch') },
  { key: 'Y', label: 'Purchase Payment (F5)', action: () => router.push('/voucher/payment') },
  { key: 'R', label: 'Broker Receipt (F6)', action: () => router.push('/voucher/receipt') },
  { key: 'L', label: 'Sugar Purchase List (Register)', action: () => router.push('/register/purchase') },
  { key: 'K', label: 'Dispatch Entry List (Register)', action: () => router.push('/register/dispatch') },
  { key: 'U', label: 'Suppliers / Sugar Mills List', action: () => router.push('/register/supplier') },
  { key: 'B', label: 'Brokers Directory List', action: () => router.push('/register/broker') },
  { key: 'C', label: 'Customer Parties List', action: () => router.push('/register/customer') },
  { key: 'O', label: 'Broker Receivables (Outstanding)', action: () => router.push('/register/broker-outstanding') },
  { key: 'S', label: 'Supplier Payables (Outstanding)', action: () => router.push('/register/supplier-outstanding') },
  { key: 'F10', label: 'Day Book & Audit Register', action: () => router.push('/daybook') },
  { key: 'M', label: 'Masters Directory', action: () => router.push('/masters') },
  { key: 'Q', label: 'Quit / Refresh', action: () => { loadStats(); showToast('Data refreshed') } },
]

const handleSelect = (idx) => {
  activeIndex.value = idx
  menuItems[idx].action()
}

const handleKeyDown = (e) => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % menuItems.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value - 1 + menuItems.length) % menuItems.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    handleSelect(activeIndex.value)
  } else {
    const pressedKey = e.key.toUpperCase()
    const hitIndex = menuItems.findIndex(m => m.key === pressedKey)
    if (hitIndex !== -1) {
      e.preventDefault()
      handleSelect(hitIndex)
    }
  }
}

onMounted(() => {
  loadStats()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
