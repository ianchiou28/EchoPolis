<template>
  <div class="city-map glass-panel">
    <div class="map-header">
      <div class="map-title">Echo City Grid</div>
      <div class="map-sub">选择一个城区，触发对应的金融事件</div>
    </div>
    <div class="map-grid">
      <button
        v-for="district in districts"
        :key="district.id"
        class="district"
        :class="{ active: props.activeZone === district.id }"
        @click="$emit('select', district)"
      >
        <span class="district-name">{{ district.name }}</span>
        <span class="district-tag">{{ district.tagline }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { toRefs } from 'vue'

const props = defineProps({
  activeZone: { type: String, default: '' }
})

const districts = [
  { id: 'finance', name: '金融高塔', tagline: '资产配置 / 对冲策略' },
  { id: 'tech', name: '未来科创区', tagline: '科技初创 / AI 投资' },
  { id: 'housing', name: '新星住区', tagline: '地产 / 租赁 / 长期持有' },
  { id: 'learning', name: '知识穹顶', tagline: '教育 / 个人成长' },
  { id: 'leisure', name: '文娱街区', tagline: '消费 / 体验经济' },
  { id: 'green', name: '绿色能源港', tagline: '能源 / ESG / 可持续' }
]
</script>

<style scoped>
.city-map {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.map-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.map-title {
  font-size: 14px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(226,232,240,0.9);
}
.map-sub {
  font-size: 12px;
  color: rgba(148,163,184,0.9);
}

.map-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.district {
  position: relative;
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 16px;
  padding: 14px;
  background: rgba(15,23,42,0.8);
  text-align: left;
  color: inherit;
  cursor: pointer;
  transition: border-color 200ms ease, transform 200ms ease, box-shadow 200ms ease;
}

.district::after {
  content: '';
  position: absolute;
  inset: 8px;
  border-radius: 12px;
  border: 1px dashed rgba(148,163,184,0.2);
  pointer-events: none;
}

.district:hover,
.district.active {
  border-color: rgba(94,234,212,0.6);
  box-shadow: 0 8px 25px rgba(14,165,233,0.2);
  transform: translateY(-3px);
  background: linear-gradient(160deg, rgba(59,130,246,0.25), rgba(56,189,248,0.15));
}

.district-name {
  font-weight: 700;
  margin-bottom: 6px;
}

.district-tag {
  font-size: 12px;
  color: rgba(148,163,184,0.85);
}
</style>
