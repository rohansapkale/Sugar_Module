<template>
  <div v-if="isOpen" class="modal-bg" @click.self="handleNo">
    <div class="modal-box">
      <div class="m-title">{{ data?.title || 'Accept Voucher?' }}</div>
      <div class="m-body" v-html="data?.body || 'Save changes?'"></div>
      <div class="m-foot">
        <div class="shortcut-tip">
          <kbd>Enter</kbd> / <kbd>Y</kbd> = Yes &nbsp;&nbsp; <kbd>Esc</kbd> / <kbd>N</kbd> = No
        </div>
        <div class="actions">
          <button style="padding: 4px 12px; margin-right: 8px; cursor: pointer;" @click="handleNo">No</button>
          <button style="padding: 4px 14px; background: var(--blue); color: #fff; border: none; border-radius: 3px; cursor: pointer;" @click="handleYes">Yes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { globalUiState, closeConfirm } from '../../composables/useKeyboardEngine'

const isOpen = computed(() => globalUiState.isConfirmModalOpen.value)
const data = computed(() => globalUiState.confirmModalData.value)

const handleYes = () => closeConfirm(true)
const handleNo = () => closeConfirm(false)
</script>
