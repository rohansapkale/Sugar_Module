<template>
  <div id="topbar">
    <!-- Left: Hamburger, Logo & Brand Title -->
    <div class="brand">
      <button class="hamburger-btn" title="Toggle Navigation Menu">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <img :src="logoUrl" alt="Logo" class="topbar-logo-img" />
      <strong>SUGAR DESK</strong> 
      <span class="company-sub-title">· {{ companyName }}</span>
    </div>

    <!-- Right: User Info, Date, Role, Theme & ERP Button -->
    <div class="meta">
      <span class="user-name">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="opacity: 0.9;">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
        {{ userName }}
      </span>
      
      <span class="today-date">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.9;">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        {{ formattedDate }}
      </span>

      <!-- Role Selector Dropdown Pill -->
      <div class="role-selector-pill">
        <span>Role: {{ activeRole }}</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
      
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
        <span v-if="isDarkMode" class="theme-label">
          <span style="color: #fbbf24; font-size: 13px;">☀️</span> Light
        </span>
        <span v-else class="theme-label">
          <span style="color: #facc15; font-size: 13px;">🌙</span> Dark
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useFrappeApi } from '../../composables/useFrappeApi'
import { useTheme } from '../../composables/useTheme'
import logoImg from '../../assets/logo.png'

const logoUrl = logoImg
const { bootState } = useFrappeApi()
const { isDarkMode, toggleTheme } = useTheme()

const companyName = computed(() => {
  return bootState.default_company || 'Rajendra Narahari Lokhande (Sugar Trading Division)'
})

const userName = computed(() => {
  return bootState.full_name || bootState.user || 'Guest'
})

const activeRole = computed(() => {
  if (bootState.roles && bootState.roles.includes('System Manager')) return 'Trading Admin'
  return 'Trading'
})

const formattedDate = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
})

const goToErpNext = () => {
  if (window.location.port === '8080') {
    window.location.href = `http://${window.location.hostname}:8001/desk/rajendra-narahari-lokhande`
  } else {
    window.location.href = '/desk/rajendra-narahari-lokhande'
  }
}
</script>

<style scoped>
.company-sub-title {
  color: #9fb8e8;
  font-weight: 400;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .company-sub-title {
    display: none;
  }
}

.hamburger-btn {
  background: transparent;
  border: none;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.topbar-logo-img {
  height: 28px;
  width: 28px;
  border-radius: 6px;
  object-fit: contain;
  background: #ffffff;
  padding: 1.5px;
  margin: 0 6px 0 3px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.role-selector-pill {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.role-selector-pill:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

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
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #f1f5f9;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  user-select: none;
}

.theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.45);
  transform: translateY(-1px);
}

.theme-label, .admin-label {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>
