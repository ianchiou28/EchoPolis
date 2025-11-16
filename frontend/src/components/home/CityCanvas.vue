<template>
  <section class="city-canvas">
    <div class="sky gradient" :style="parallaxStyles.gradient" />
    <div class="sky stars" :style="parallaxStyles.stars" />
    <div class="skyline skyline--far" :style="parallaxStyles.far" />
    <div class="skyline skyline--mid" :style="parallaxStyles.mid" />
    <div class="skyline skyline--front" :style="parallaxStyles.front" />
    <div class="city-glow" />
    <div class="city-metrics">
      <article v-for="metric in skylineMetrics" :key="metric.label" class="metric">
        <p class="metric-label">{{ metric.label }}</p>
        <strong :class="metric.accent">{{ metric.value }}</strong>
        <small>{{ metric.desc }}</small>
      </article>
    </div>
    <div class="district-row">
      <button
        v-for="district in districts"
        :key="district.id"
        :class="['district-chip', { active: district.id === selectedId }]"
        @click="$emit('select', district)"
      >
        <span>{{ district.name }}</span>
        <small>{{ district.tagline }}</small>
      </button>
    </div>
    <div v-if="isLoading" class="loading-overlay">生成事件中…</div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  assets: { type: Object, required: true },
  monthlyIncome: { type: Number, default: 0 },
  parallax: { type: Object, default: () => ({ x: 0, y: 0 }) },
  districts: { type: Array, default: () => [] },
  selectedId: String,
  isLoading: Boolean
})

const skylineMetrics = computed(() => ([
  {
    label: '总资产',
    value: `¥${props.assets.total.toLocaleString('zh-CN')}`,
    desc: 'CITY NAV',
    accent: 'up'
  },
  {
    label: '现金流',
    value: `¥${props.assets.cash.toLocaleString('zh-CN')}`,
    desc: 'LIQUIDITY',
    accent: 'neutral'
  },
  {
    label: '被动收入/月',
    value: `+¥${props.monthlyIncome.toLocaleString('zh-CN')}`,
    desc: 'PASSIVE INFLOW',
    accent: 'up'
  }
]))

const parallaxStyles = computed(() => {
  const { x, y } = props.parallax || { x: 0, y: 0 }
  const make = (mult) => ({ transform: `translate3d(${x * mult}px, ${y * mult}px, 0)` })
  return {
    gradient: make(10),
    stars: make(15),
    far: make(20),
    mid: make(30),
    front: make(40)
  }
})
</script>

<style scoped>
.city-canvas {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  height: 320px;
  background: var(--panel-overlay);
  border: 1px solid color-mix(in srgb, var(--primary-400) 35%, transparent);
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}
.sky, .skyline, .city-glow {
  position: absolute;
  inset: 0;
}
.sky.gradient {
  background: radial-gradient(circle at 20% 0%, rgba(59,130,246,0.25), transparent 55%),
              radial-gradient(circle at 80% 10%, rgba(14,165,233,0.25), transparent 60%);
}
.sky.stars {
  background-image: radial-gradient(rgba(255,255,255,0.4) 1px, transparent 1px);
  background-size: 80px 80px;
  opacity: 0.4;
}
.skyline {
  background-repeat: repeat-x;
  background-position: bottom center;
  opacity: 0.7;
}
.skyline--far {
  background-image: linear-gradient(180deg, rgba(2,6,23,0) 0%, rgba(2,6,23,0.5) 60%, rgba(2,6,23,0.85) 100%),
    url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 200"%3E%3Cpath d="M0 180 L60 180 L60 120 L120 120 L120 160 L200 160 L200 80 L260 80 L260 180 L340 180 L340 110 L420 110 L420 180 L520 180 L520 90 L600 90 L600 180 L700 180 L700 130 L780 130 L780 180 L880 180 L880 100 L960 100 L960 180 L1040 180 L1040 140 L1120 140 L1120 180 L1200 180 L1200 200 L0 200 Z" fill="%2306172c"/%3E%3C/svg%3E');
}
.skyline--mid {
  background-image: linear-gradient(180deg, rgba(2,6,23,0) 0%, rgba(2,6,23,0.6) 70%, rgba(2,6,23,0.95) 100%),
    url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220"%3E%3Cpath d="M0 200 L80 200 L80 140 L160 140 L160 190 L230 190 L230 100 L320 100 L320 200 L420 200 L420 120 L500 120 L500 200 L620 200 L620 150 L700 150 L700 200 L820 200 L820 90 L900 90 L900 200 L1000 200 L1000 160 L1100 160 L1100 200 L1200 200 L1200 220 L0 220 Z" fill="%230b1f3b"/%3E%3C/svg%3E');
}
.skyline--front {
  background-image: linear-gradient(180deg, rgba(2,6,23,0.2) 0%, rgba(2,6,23,0.85) 80%, rgba(2,6,23,1) 100%),
    url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 240"%3E%3Cpath d="M0 220 L100 220 L100 150 L200 150 L200 210 L320 210 L320 120 L440 120 L440 220 L560 220 L560 160 L680 160 L680 220 L800 220 L800 130 L920 130 L920 220 L1040 220 L1040 170 L1160 170 L1160 220 L1200 220 L1200 240 L0 240 Z" fill="%2311294f"/%3E%3C/svg%3E');
}
.city-glow {
  background: radial-gradient(circle at 50% 100%, rgba(59,130,246,0.5), transparent 60%);
}
.city-metrics {
  position: absolute;
  top: 24px;
  left: 24px;
  display: flex;
  gap: 14px;
}
.metric {
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(2,6,23,0.75);
  border: 1px solid rgba(148,163,184,0.3);
}
.metric-label {
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.metric strong.up { color: var(--success); }
.metric strong.neutral { color: var(--text); }
.metric small {
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  opacity: 0.7;
}
.district-row {
  position: absolute;
  bottom: 18px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}
.district-chip {
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.4);
  background: rgba(2,6,23,0.7);
  color: var(--text-strong);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.district-chip::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent, rgba(59,130,246,0.25), transparent);
  transform: translateX(-100%);
  transition: transform 0.4s ease;
}
.district-chip:hover::after,
.district-chip.active::after {
  transform: translateX(0);
}
.district-chip.active {
  border-color: var(--primary-400);
  background: rgba(59,130,246,0.35);
}
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(6px);
  background: rgba(2,6,23,0.6);
  font-weight: 700;
}
</style>
