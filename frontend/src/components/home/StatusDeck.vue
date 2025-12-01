<template>
  <div class="status-deck">
    <div class="status-pill" v-for="pill in pills" :key="pill.label">
      <p class="pill-label">{{ pill.label }}</p>
      <strong>{{ pill.value }}</strong>
    </div>
    <button class="btn ghost" :class="{ loading: isAdvancing }" @click="$emit('advance')" :disabled="isAdvancing">
      {{ isAdvancing ? '推进中…' : '推进一月' }}
    </button>
    <button class="btn primary" @click="$emit('enter-world')">进入城市</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  wealth: String,
  trust: [String, Number],
  stage: String,
  isAdvancing: Boolean
})

const pills = computed(() => ([
  { label: '财富主宰度', value: props.wealth || '-' },
  { label: '信任共鸣', value: `${props.trust ?? '--'} / 100` },
  { label: '人生时相', value: props.stage || '-' }
]))
</script>

<style scoped>
.status-deck {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
.status-pill {
  padding: 12px 16px;
  border-radius: 999px;
  background: var(--surface-strong);
  border: 1px solid color-mix(in srgb, var(--primary-400) 30%, transparent);
}
.pill-label {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}
strong {
  display: block;
  font-size: 16px;
}
.btn.loading {
  opacity: 0.7;
  pointer-events: none;
}
</style>
