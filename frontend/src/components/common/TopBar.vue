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

const { bootState } = useFrappeApi()

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
</script>
