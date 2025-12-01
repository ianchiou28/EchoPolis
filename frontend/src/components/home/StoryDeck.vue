<template>
  <section class="story-deck card glass">
    <header class="deck-head">
      <div>
        <p class="eyebrow">CITY STORYLINE</p>
        <h3>{{ situation?.title || '选择一个城区，唤醒城市事件' }}</h3>
      </div>
      <button class="btn soft" :disabled="isAiInvesting" @click="$emit('ai-invest')">
        {{ isAiInvesting ? 'AI 思考中…' : '求助 AI 投资' }}
      </button>
    </header>
    <div class="city-storyline">
      <div class="storyline-map">
        <span class="pulse" />
      </div>
      <div class="storyline-content">
        <p class="story-text">{{ situation?.description || '城市正在等待你的指令。' }}</p>
        <div class="options" v-if="options?.length">
          <article v-for="(option, idx) in options" :key="idx" class="option-card">
            <span class="chip">选项 {{ idx + 1 }}</span>
            <p>{{ option }}</p>
          </article>
        </div>
        <div class="event-feed" v-if="events?.length">
          <article v-for="event in events" :key="event.id" class="event-item" :class="event.type">
            <header>
              <span class="district-label">{{ labelOf(event.districtId) }}</span>
              <time>{{ formatTime(event.timestamp) }}</time>
            </header>
            <strong>{{ event.title }}</strong>
            <p>{{ event.description }}</p>
          </article>
        </div>
        <p v-else class="empty">城市仍在静默，去探索一个城区触发事件。</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  situation: Object,
  options: Array,
  events: { type: Array, default: () => [] },
  isAiInvesting: Boolean
})

const labelOf = (id) => ({
  finance: '金融高塔',
  tech: '未来科创区',
  housing: '新星住区',
  learning: '知识穹顶',
  leisure: '文娱街区',
  green: '绿色能源港'
}[id] || '未知城区')

const formatTime = (ts) => new Date(ts).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
</script>

<style scoped>
.story-deck {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.story-text {
  color: var(--text);
}
.options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.option-card {
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(59,130,246,0.35);
  background: rgba(2,6,23,0.65);
}
.event-feed {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.event-item {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(2,6,23,0.55);
}
.event-item.ai { border-color: var(--primary-400); }
.event-item.timeline { border-color: var(--info); }
.district-label {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.empty {
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 0.05em;
}
.city-storyline {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 16px;
}
.storyline-map {
  position: relative;
}
.storyline-map .pulse {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: var(--primary-400);
  box-shadow: 0 0 12px var(--primary-glow);
}
</style>
