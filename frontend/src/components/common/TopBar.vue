<template>
  <div id="topbar">
    <div class="brand">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path>
        <path d="M6 6h10"></path>
        <path d="M6 10h10"></path>
        <path d="M6 14h6"></path>
      </svg>
      <strong>SUGAR DESK</strong> 
      <span>· {{ companyName }}</span>
    </div>
    <div class="meta">
      <span class="user-name">👤 {{ userName }}</span>
      <span class="today-date">📅 {{ formattedDate }}</span>
      
      <!-- getMyErp Button -->
      <button
        class="admin-desk-btn"
        title="Go to ERPNext Desk (getMyErp)"
        @click="goToErpNext"
      >
        <span class="admin-label">⚡ getMyErp</span>
      </button>

      <!-- Dark / Light Mode Toggle Button -->
      <button
        class="theme-toggle-btn"
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        @click="toggleTheme"
      >
        <span v-if="isDarkMode" class="theme-label">☀️ Light</span>
        <span v-else class="theme-label">🌙 Dark</span>
      </button>

      <span class="goto-hint" @click="openGoTo">
        <b>Alt+G</b> Go To
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useFrappeApi } from '../../composables/useFrappeApi'
import { globalUiState } from '../../composables/useKeyboardEngine'
import { useTheme } from '../../composables/useTheme'

const { bootState } = useFrappeApi()
const { isDarkMode, toggleTheme } = useTheme()

const companyName = computed(() => {
  return bootState.default_company || 'Mahalaxmi Sugar Mills Pvt. Ltd.'
})

const userName = computed(() => {
  return bootState.full_name || bootState.user || 'Administrator'
})

const formattedDate = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
})

const openGoTo = () => {
  globalUiState.isGoToOpen.value = true
}

const goToErpNext = () => {
  if (window.location.port === '8080') {
    window.location.href = `http://${window.location.hostname}:8001/desk/rajendra-narahari-lokhande`
  } else {
    window.location.href = '/desk/rajendra-narahari-lokhande'
  }
}
</script>

<style scoped>
.admin-desk-btn {
  background: #2563eb;
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: #fff;
  padding: 4px 11px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
  user-select: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.admin-desk-btn:hover {
  background: #1d4ed8;
  border-color: #fff;
  transform: translateY(-1px);
}

.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s ease;
  user-select: none;
}

.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.45);
  transform: translateY(-1px);
}

.theme-label, .admin-label {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
