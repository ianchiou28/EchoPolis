<template>
  <section class="avatar-tower card glass">
    <header class="tower-head">
      <p class="eyebrow">ECHO AVATAR</p>
      <h2>{{ avatar?.name || 'Echo' }}</h2>
      <p class="subtitle">{{ avatar?.mbti_type || 'INTJ' }} · 共鸣 {{ avatar?.trust_level ?? 50 }}</p>
    </header>
    <AvatarPanel :name="avatar?.name || 'Echo'" :mood="mood" />
    <div class="stats">
      <article v-for="stat in stats" :key="stat.label" class="stat-card" :class="stat.accent">
        <p class="label">{{ stat.label }}</p>
        <p class="value">{{ stat.value }}</p>
      </article>
    </div>
    <div class="time-chip">
      <p>{{ timeLabel }}</p>
      <span>{{ lifeStage }}</span>
    </div>
    <div class="ai-reflect">
      <h3>城市独白</h3>
      <p>{{ aiReflection }}</p>
    </div>
  </section>
</template>

<script setup>
import AvatarPanel from '../AvatarPanel.vue'
const props = defineProps({
  avatar: Object,
  mood: String,
  stats: { type: Array, default: () => [] },
  lifeStage: String,
  timeLabel: String,
  aiReflection: String
})
const { avatar, mood, stats, lifeStage, timeLabel, aiReflection } = props
</script>

<style scoped>
.avatar-tower {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.tower-head {
  text-align: center;
}
.subtitle {
  color: var(--muted);
}
.stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.stat-card {
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.stat-card.up .value { color: var(--success); }
.stat-card.neutral .value { color: var(--text); }
.time-chip {
  padding: 12px;
  border-radius: 14px;
  background: var(--surface-strong);
  display: flex;
  justify-content: space-between;
}
.ai-reflect {
  padding: 16px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}
</style>
