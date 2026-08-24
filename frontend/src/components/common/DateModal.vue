<template>
  <div v-if="isOpen" class="modal-bg" @click.self="close">
    <div class="modal-box" style="max-width: 380px;">
      <div class="m-title">Change Current Date (F2)</div>
      <div class="m-body">
        <label style="display: block; margin-bottom: 8px; font-size: 13px; color: var(--muted);">Select Working Date:</label>
        <input
          ref="dateInputRef"
          v-model="selectedDate"
          type="date"
          style="width: 100%; padding: 8px 10px; font-size: 14px; border: 1px solid var(--blue); border-radius: 4px; outline: none;"
          @keydown.enter.prevent="saveDate"
          @keydown.esc.prevent="close"
        />
      </div>
      <div class="m-foot">
        <div><kbd>Enter</kbd> = Apply &nbsp;&nbsp; <kbd>Esc</kbd> = Cancel</div>
        <button style="padding: 4px 14px; background: var(--blue); color: #fff; border: none; border-radius: 3px; cursor: pointer;" @click="saveDate">Set Date</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { globalUiState, showToast } from '../../composables/useKeyboardEngine'
import { useFrappeApi } from '../../composables/useFrappeApi'

const { bootState } = useFrappeApi()
const isOpen = computed(() => globalUiState.isDateModalOpen.value)
const selectedDate = ref(bootState.today || new Date().toISOString().split('T')[0])
const dateInputRef = ref(null)

watch(isOpen, (val) => {
  if (val) {
    selectedDate.value = bootState.today || new Date().toISOString().split('T')[0]
    nextTick(() => {
      if (dateInputRef.value) dateInputRef.value.focus()
    })
  }
})

const close = () => {
  globalUiState.isDateModalOpen.value = false
}

const saveDate = () => {
  if (selectedDate.value) {
    bootState.today = selectedDate.value
    showToast(`Working date changed to ${selectedDate.value}`)
  }
  close()
}
</script>
