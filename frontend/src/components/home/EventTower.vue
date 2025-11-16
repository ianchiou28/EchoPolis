<template>
  <section class="event-tower">
    <article class="floating-card">
      <header>
        <p class="eyebrow">ASSET SNAPSHOT</p>
        <h3>财富结构</h3>
      </header>
      <ul>
        <li>现金 <strong>¥{{ cashDisplay }}</strong></li>
        <li>投资 <strong>¥{{ invested }}</strong></li>
        <li>被动收入 <strong class="up">+¥{{ (assets.cash ? monthlyIncome.toLocaleString('zh-CN') : '0') }}/月</strong></li>
      </ul>
    </article>
    <article class="floating-card">
      <header>
        <p class="eyebrow">CITY SIGNAL</p>
        <h3>即时提示</h3>
      </header>
      <p>{{ aiMonologue }}</p>
    </article>
    <article class="floating-card">
      <header>
        <p class="eyebrow">CITY LOG</p>
        <h3>最近事件</h3>
      </header>
      <ul class="event-log">
        <li v-for="evt in events.slice(0,5)" :key="evt.id">
          <span class="tag">{{ labelOf(evt.districtId) }}</span>
          <div>
            <strong>{{ evt.title }}</strong>
            <p>{{ evt.description }}</p>
          </div>
        </li>
        <li v-if="!events.length" class="empty">暂无城市日志</li>
      </ul>
    </article>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  events: { type: Array, default: () => [] },
  aiMonologue: { type: String, default: '' },
  assets: { type: Object, default: () => ({ cash: 0, investments: [] }) },
  monthlyIncome: { type: Number, default: 0 }
})

const invested = computed(() => {
  const list = Array.isArray(props.assets?.investments) ? props.assets.investments : []
  const total = list.reduce((sum, inv) => sum + (inv.amount || 0), 0)
  return total.toLocaleString('zh-CN')
})
const cashDisplay = computed(() => props.assets?.cash?.toLocaleString('zh-CN') || '0')
const labelOf = (id) => ({
  finance: '金融高塔',
  tech: '未来科创区',
  housing: '新星住区',
  learning: '知识穹顶',
  leisure: '文娱街区',
  green: '绿色能源港'
}[id] || '未知区')
</script>

<style scoped>
.event-tower {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.floating-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(2,6,23,0.8);
  border: 1px solid rgba(94,234,212,0.25);
}
ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.up { color: var(--success); }
.event-log {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.event-log li {
  display: flex;
  gap: 10px;
}
.tag {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(59,130,246,0.15);
}
.empty { color: var(--muted); }
</style>
