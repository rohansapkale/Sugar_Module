<template>
  <div class="dropdown-menu-list" ref="dropdownRef">
    <div class="dropdown-header">
      <span>⚡ Live DB ({{ matches.length }} options)</span>
      <span class="tip">↑↓ browse · Enter pick</span>
    </div>

    <div v-if="matches && matches.length" class="dropdown-items-scroll">
      <div
        v-for="(m, i) in matches"
        :key="m.id || m.name || i"
        :class="['item', { hi: activeIndex === i }]"
        @mousedown.prevent="$emit('select', m)"
        @mouseover="$emit('hover', i)"
      >
        <div class="item-main">
          <span class="name">{{ m.label || m.name }}</span>
          <span v-if="m.name && m.label !== m.name" class="code-tag">[{{ m.name }}]</span>
        </div>
        <span v-if="m.type || m.doctype" class="subtag">{{ m.type || m.doctype }}</span>
      </div>
    </div>

    <div v-else class="empty-dropdown">
      <span>No matching records in Frappe DB</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  matches: {
    type: Array,
    default: () => []
  },
  activeIndex: {
    type: Number,
    default: 0
  }
})

defineEmits(['select', 'hover'])

const dropdownRef = ref(null)

watch(() => props.activeIndex, (newVal) => {
  nextTick(() => {
    if (!dropdownRef.value) return
    const scrollContainer = dropdownRef.value.querySelector('.dropdown-items-scroll')
    if (!scrollContainer) return
    const activeEl = scrollContainer.children[newVal]
    if (activeEl) {
      activeEl.scrollIntoView({ block: 'nearest' })
    }
  })
})
</script>

<style scoped>
.dropdown-header {
  padding: 5px 10px;
  background: var(--navy);
  color: #9fb8e8;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
}

.dropdown-header .tip {
  color: #ffd479;
  font-family: monospace;
}

.dropdown-items-scroll {
  max-height: 200px;
  overflow-y: auto;
}

.item-main {
  display: flex;
  align-items: center;
  gap: 6px;
}

.code-tag {
  font-size: 11px;
  color: var(--muted);
  font-family: monospace;
}

.item.hi .code-tag {
  color: #dbe8ff;
}

.empty-dropdown {
  padding: 12px 14px;
  font-size: 12.5px;
  color: var(--muted);
  text-align: center;
}
</style>
