<template>
  <div v-if="isOpen" class="modal-bg" @click.self="close">
    <div class="modal-box" style="max-width: 540px;">
      <div class="m-title">Keyboard Shortcuts & Navigation Help (F1)</div>
      <div class="m-body" style="font-size: 13px; line-height: 1.7;">
        <p style="margin-bottom: 8px;"><b>Voucher Data Entry:</b></p>
        <ul style="padding-left: 20px; margin-bottom: 12px;">
          <li><kbd>Tab</kbd> or <kbd>Enter</kbd> — Move to next field</li>
          <li><kbd>Shift + Tab</kbd> — Move to previous field</li>
          <li><kbd>↑</kbd> / <kbd>↓</kbd> — Highlight ledger in typeahead dropdown</li>
          <li><kbd>Enter</kbd> in dropdown — Select ledger and auto-advance</li>
          <li><kbd>Enter</kbd> on Narration — Prompt to <b>Accept Voucher</b></li>
          <li><kbd>Esc</kbd> — Clear current field &gt; Step back &gt; Discard to Gateway</li>
        </ul>

        <p style="margin-bottom: 8px;"><b>Direct Function Keys:</b></p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px; font-family: monospace;">
          <div><kbd>F4</kbd> Contra</div>
          <div><kbd>F5</kbd> Payment</div>
          <div><kbd>F6</kbd> Receipt</div>
          <div><kbd>F7</kbd> Sauda / Journal</div>
          <div><kbd>F8</kbd> Dispatch Entry</div>
          <div><kbd>F9</kbd> Sugar Purchase</div>
          <div><kbd>F10</kbd> Day Book</div>
          <div><kbd>Alt+G</kbd> Go To Search</div>
        </div>
      </div>
      <div class="m-foot">
        <div>Press <kbd>Esc</kbd> or <kbd>Enter</kbd> to close</div>
        <button style="padding: 4px 14px; background: var(--blue); color: #fff; border: none; border-radius: 3px; cursor: pointer;" @click="close">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { globalUiState } from '../../composables/useKeyboardEngine'

const isOpen = computed(() => globalUiState.isHelpOpen.value)
const close = () => {
  globalUiState.isHelpOpen.value = false
}
</script>
