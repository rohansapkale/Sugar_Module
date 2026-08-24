<template>
  <div id="menu-panel">
    <div class="menu-section-label">{{ sectionTitle }}</div>
    <div
      v-for="(item, idx) in items"
      :key="idx"
      :class="['menu-item', { active: activeIndex === idx }]"
      @click="$emit('select', idx)"
    >
      <span class="key">{{ item.key }}</span>
      <span class="label">{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sectionTitle: {
    type: String,
    default: 'Menu'
  },
  items: {
    type: Array,
    default: () => []
  },
  activeIndex: {
    type: Number,
    default: 0
  }
})

defineEmits(['select'])
</script>
