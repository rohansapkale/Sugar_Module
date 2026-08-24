<template>
  <div id="fkbar">
    <div
      v-for="fk in keys"
      :key="fk.key"
      class="fk"
      @click="triggerKey(fk.key)"
    >
      <b>{{ fk.key }}</b> {{ fk.label }}
    </div>
  </div>
</template>

<script setup>
import { useKeyboardEngine } from '../../composables/useKeyboardEngine'

const { handleFunctionKey } = useKeyboardEngine()

const keys = [
  { key: 'F1', label: 'Help' },
  { key: 'F2', label: 'Date' },
  { key: 'F4', label: 'Contra' },
  { key: 'F5', label: 'Payment' },
  { key: 'F6', label: 'Receipt' },
  { key: 'F8', label: 'Dispatch' },
  { key: 'F9', label: 'Purchase' },
  { key: 'F10', label: 'Day Book' },
  { key: 'Esc', label: 'Quit / Back' }
]

const triggerKey = (key) => {
  if (key === 'Esc') {
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
  } else {
    handleFunctionKey(key)
  }
}
</script>
