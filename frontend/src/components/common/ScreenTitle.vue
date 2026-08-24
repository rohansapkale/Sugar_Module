<template>
  <div id="screen-title-bar">
    <div class="title-text">
      {{ title }}
    </div>
    <div v-if="status" :class="['status-badge', status.toLowerCase()]">
      {{ status }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: 'Gateway of Sugar'
  },
  status: {
    type: String,
    default: ''
  }
})
</script>
