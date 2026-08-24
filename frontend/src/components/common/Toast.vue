<template>
  <div v-if="visible" class="toast-hud">
    <span class="icon">⚡</span>
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { globalUiState } from '../../composables/useKeyboardEngine'

const visible = computed(() => globalUiState.toastVisible.value)
const message = computed(() => globalUiState.toastMessage.value)
</script>
