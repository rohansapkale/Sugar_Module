<template>
  <div id="topbar">
    <!-- Left: Hamburger & Brand Title -->
    <div class="brand">
      <button class="hamburger-btn" title="Toggle Navigation Menu">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <strong>SUGAR DESK</strong> 
      <span class="company-sub-title">· {{ companyName }}</span>
    </div>

    <!-- CENTER: Universal Global Search Bar (Search Literally Anything) -->
    <div class="global-search-center-wrap" ref="searchContainerRef">
      <div :class="['search-input-box', { active: isSearchOpen }]">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>

        <input
          ref="globalSearchInputRef"
          v-model="searchQuery"
          type="text"
          class="global-search-input"
          placeholder="Search anything (Voucher ID, Mill, Buyer, Broker, Veh No, UTR, Report)..."
          autocomplete="off"
          @focus="onSearchFocus"
          @input="onSearchInput"
          @keydown="handleSearchKeyDown"
        />

        <div v-if="!searchQuery" class="search-kbd-hint" title="Press / or Ctrl+K to search">
          <span>/</span>
        </div>
        <button
          v-else
          class="search-clear-btn"
          title="Clear search"
          @click="clearSearch"
        >
          ✕
        </button>
      </div>

      <!-- Live Search Results Dropdown Overlay -->
      <div v-if="isSearchOpen && (searchResults.length > 0 || isSearching || (searchQuery.trim().length >= 1 && !isSearching))" class="search-dropdown-menu">
        <div class="search-dropdown-header">
          <span>🔍 Universal Results for "<b>{{ searchQuery }}</b>"</span>
          <span class="results-count">{{ searchResults.length }} items found</span>
        </div>

        <div v-if="isSearching" class="search-loading-row">
          <span class="spinner">⏳</span> Searching Frappe database...
        </div>

        <div v-else-if="searchResults.length === 0" class="search-empty-row">
          <span>No matching transactions, masters, or reports found</span>
        </div>

        <div v-else class="search-results-list">
          <div
            v-for="(item, idx) in searchResults"
            :key="item.id || idx"
            :class="['search-result-item', { active: activeResultIndex === idx }]"
            @mousedown.prevent="selectSearchResult(item)"
            @mouseover="activeResultIndex = idx"
          >
            <div class="res-icon">{{ item.icon || '📄' }}</div>
            <div class="res-body">
              <div class="res-title-row">
                <span class="res-title">{{ item.title }}</span>
                <span class="res-category-tag">{{ item.category }}</span>
              </div>
              <div class="res-subtitle">{{ item.subtitle }}</div>
            </div>
            <div class="res-action-hint">↵ Open</div>
          </div>
        </div>

        <div class="search-dropdown-footer">
          <span><kbd>↑</kbd> <kbd>↓</kbd> Navigate</span>
          <span><kbd>Enter</kbd> Open in View Mode</span>
          <span><kbd>Esc</kbd> Close</span>
        </div>
      </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFrappeApi } from '../../composables/useFrappeApi'
import { showToast } from '../../composables/useKeyboardEngine'
import { useTheme } from '../../composables/useTheme'

const router = useRouter()
const { bootState, universalGlobalSearch } = useFrappeApi()
const { isDarkMode, toggleTheme } = useTheme()

const searchQuery = ref('')
const searchResults = ref([])
const isSearchOpen = ref(false)
const isSearching = ref(false)
const activeResultIndex = ref(0)
const globalSearchInputRef = ref(null)
const searchContainerRef = ref(null)
let searchTimer = null

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

// -------------------------------------------------------------
// UNIVERSAL GLOBAL SEARCH LOGIC
// -------------------------------------------------------------
const onSearchFocus = () => {
  isSearchOpen.value = true
  if (searchQuery.value.trim().length >= 1) {
    executeSearch()
  }
}

const onSearchInput = () => {
  isSearchOpen.value = true
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    executeSearch()
  }, 120)
}

const executeSearch = async () => {
  const q = searchQuery.value.trim()
  if (!q) {
    searchResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true
  try {
    const res = await universalGlobalSearch(q)
    searchResults.value = res || []
    activeResultIndex.value = 0
  } catch (e) {
    console.error('Universal search error:', e)
  } finally {
    isSearching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  isSearchOpen.value = false
}

const selectSearchResult = (item) => {
  if (!item) return
  isSearchOpen.value = false

  if (item.externalUrl) {
    window.location.href = item.externalUrl
  } else if (item.route) {
    router.push(item.route)
  }

  showToast(`Opening: ${item.title}`)
}

const handleSearchKeyDown = (e) => {
  if (!isSearchOpen.value || !searchResults.value.length) {
    if (e.key === 'Escape') {
      isSearchOpen.value = false
      if (globalSearchInputRef.value) globalSearchInputRef.value.blur()
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeResultIndex.value = (activeResultIndex.value + 1) % searchResults.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeResultIndex.value = (activeResultIndex.value - 1 + searchResults.value.length) % searchResults.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    selectSearchResult(searchResults.value[activeResultIndex.value])
  } else if (e.key === 'Escape') {
    e.preventDefault()
    isSearchOpen.value = false
    if (globalSearchInputRef.value) globalSearchInputRef.value.blur()
  }
}

// Global hotkey to focus search: '/' or 'Ctrl+K'
const handleWindowKeyDown = (e) => {
  // If user presses '/' when not typing in any other input
  if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
    e.preventDefault()
    if (globalSearchInputRef.value) {
      globalSearchInputRef.value.focus()
      globalSearchInputRef.value.select()
    }
    return
  }

  // Ctrl+K
  if (e.ctrlKey && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault()
    if (globalSearchInputRef.value) {
      globalSearchInputRef.value.focus()
      globalSearchInputRef.value.select()
    }
  }
}

const handleClickOutside = (e) => {
  if (searchContainerRef.value && !searchContainerRef.value.contains(e.target)) {
    isSearchOpen.value = false
  }
}

const goToErpNext = () => {
  if (window.location.port === '8080') {
    window.location.href = `http://${window.location.hostname}:8001/desk/rajendra-narahari-lokhande`
  } else {
    window.location.href = '/desk/rajendra-narahari-lokhande'
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleWindowKeyDown)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleWindowKeyDown)
  document.removeEventListener('click', handleClickOutside)
})
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

/* CENTER UNIVERSAL GLOBAL SEARCH BAR */
.global-search-center-wrap {
  flex: 1;
  max-width: 520px;
  margin: 0 16px;
  position: relative;
}

.search-input-box {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 6px;
  padding: 5px 12px;
  gap: 8px;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input-box:hover,
.search-input-box.active {
  background: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.search-input-box.active .search-icon,
.search-input-box:hover .search-icon {
  stroke: #2563eb;
}

.search-icon {
  stroke: #cbd5e1;
  flex-shrink: 0;
  transition: stroke 0.15s ease;
}

.global-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 12.5px;
  color: #ffffff;
  font-weight: 500;
  width: 100%;
}

.search-input-box.active .global-search-input,
.search-input-box:hover .global-search-input {
  color: #0f172a !important;
}

.global-search-input::placeholder {
  color: #94a3b8;
  font-size: 12px;
}

.search-kbd-hint {
  background: rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-family: monospace;
  font-weight: 700;
  pointer-events: none;
}

.search-input-box.active .search-kbd-hint,
.search-input-box:hover .search-kbd-hint {
  background: #f1f5f9;
  color: #475569;
  border-color: #cbd5e1;
}

.search-clear-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
}

.search-clear-btn:hover {
  color: #dc2626;
}

/* SEARCH DROPDOWN MENU */
.search-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
  z-index: 1000;
  overflow: hidden;
  max-height: 440px;
  display: flex;
  flex-direction: column;
}

body.dark-mode .search-dropdown-menu {
  background: #111c2e;
  border-color: #2b3d5c;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
}

.search-dropdown-header {
  padding: 8px 14px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 11.5px;
  color: #475569;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

body.dark-mode .search-dropdown-header {
  background: #0f1827;
  border-color: #1e293b;
  color: #94a3b8;
}

.results-count {
  font-weight: 700;
  color: #2563eb;
  font-size: 11px;
}

.search-results-list {
  overflow-y: auto;
  max-height: 340px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.12s ease;
}

body.dark-mode .search-result-item {
  border-color: #1e293b;
}

.search-result-item:hover,
.search-result-item.active {
  background: #eff6ff;
}

body.dark-mode .search-result-item:hover,
body.dark-mode .search-result-item.active {
  background: #1a2a44;
}

.res-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.res-body {
  flex: 1;
  min-width: 0;
}

.res-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.res-title {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

body.dark-mode .res-title {
  color: #f8fafc;
}

.res-category-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

body.dark-mode .res-category-tag {
  background: #1e293b;
  color: #94a3b8;
}

.res-subtitle {
  font-size: 11.5px;
  color: #64748b;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

body.dark-mode .res-subtitle {
  color: #94a3b8;
}

.res-action-hint {
  font-size: 11px;
  color: #2563eb;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.15s ease;
}

.search-result-item.active .res-action-hint,
.search-result-item:hover .res-action-hint {
  opacity: 1;
}

.search-loading-row,
.search-empty-row {
  padding: 24px;
  text-align: center;
  font-size: 13px;
  color: #64748b;
}

.search-dropdown-footer {
  padding: 6px 14px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 11px;
  color: #64748b;
  display: flex;
  gap: 14px;
}

body.dark-mode .search-dropdown-footer {
  background: #0f1827;
  border-color: #1e293b;
  color: #94a3b8;
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
