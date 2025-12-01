<template>
  <div class="city-map-container" ref="container">
    <!-- 现代化俯视城市地图 -->
    <div class="city-grid">
      <!-- 背景网格动画 -->
      <div class="grid-lines"></div>
      
      <!-- 城市区域卡片 -->
      <div 
        v-for="district in cityDistricts" 
        :key="district.id"
        :class="['district-zone', district.id, { 
          'hovered': hoveredDistrict === district.id,
          'selected': selectedDistrictId === district.id 
        }]"
        :style="district.style"
        @mouseenter="hoveredDistrict = district.id"
        @mouseleave="hoveredDistrict = null"
        @click="handleDistrictClick(district)">
        
        <!-- 区域内容 -->
        <div class="district-content">
          <div class="district-icon">{{ district.icon }}</div>
          <div class="district-info">
            <h3 class="district-name">{{ district.name }}</h3>
            <p class="district-desc">{{ district.tagline }}</p>
          </div>
          
          <!-- 数据指标 -->
          <div class="district-stats">
            <div class="stat-bar">
              <span class="stat-label">活跃度</span>
              <div class="stat-progress">
                <div class="stat-fill" :style="{ width: (district.heat * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 辉光效果 -->
        <div class="district-glow" :style="{ background: district.glowColor }"></div>
        
        <!-- 网格纹理 -->
        <div class="district-pattern"></div>
      </div>
      
      <!-- 连接线动画 -->
      <svg class="connection-lines" viewBox="0 0 1200 800">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:rgba(59,130,246,0);stop-opacity:0" />
            <stop offset="50%" style="stop-color:rgba(59,130,246,0.6);stop-opacity:1" />
            <stop offset="100%" style="stop-color:rgba(59,130,246,0);stop-opacity:0" />
          </linearGradient>
        </defs>
        <g class="lines-group">
          <line x1="300" y1="250" x2="600" y2="200" stroke="url(#lineGradient)" stroke-width="2" class="connect-line" />
          <line x1="600" y1="200" x2="900" y2="280" stroke="url(#lineGradient)" stroke-width="2" class="connect-line" />
          <line x1="300" y1="450" x2="600" y2="500" stroke="url(#lineGradient)" stroke-width="2" class="connect-line" />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  districts: {
    type: Array,
    default: () => []
  },
  selectedDistrictId: String
})

const emit = defineEmits(['district-click'])

const container = ref(null)
const hoveredDistrict = ref(null)

// 现代化城市区域定义 - 俯视卡片布局
const cityDistricts = [
  {
    id: 'finance',
    name: '中央银行群',
    tagline: '流动性中枢 · 资本核心',
    icon: '🏦',
    color: '#3b82f6',
    glowColor: 'radial-gradient(circle, rgba(59,130,246,0.4) 0%, transparent 70%)',
    heat: 0.85,
    style: {
      gridArea: '2 / 2 / 4 / 4',
      '--district-color': '#3b82f6'
    }
  },
  {
    id: 'tech',
    name: '量化交易所',
    tagline: '算法驱动 · 科技前沿',
    icon: '💹',
    color: '#8b5cf6',
    glowColor: 'radial-gradient(circle, rgba(139,92,246,0.4) 0%, transparent 70%)',
    heat: 0.92,
    style: {
      gridArea: '1 / 4 / 3 / 6',
      '--district-color': '#8b5cf6'
    }
  },
  {
    id: 'housing',
    name: '房产中枢',
    tagline: '城市更新 · 资产配置',
    icon: '🏙️',
    color: '#f59e0b',
    glowColor: 'radial-gradient(circle, rgba(245,158,11,0.4) 0%, transparent 70%)',
    heat: 0.78,
    style: {
      gridArea: '2 / 6 / 4 / 8',
      '--district-color': '#f59e0b'
    }
  },
  {
    id: 'learning',
    name: '知识引擎院',
    tagline: '教育创新 · 成长设计',
    icon: '📚',
    color: '#14b8a6',
    glowColor: 'radial-gradient(circle, rgba(20,184,166,0.4) 0%, transparent 70%)',
    heat: 0.88,
    style: {
      gridArea: '4 / 2 / 6 / 4',
      '--district-color': '#14b8a6'
    }
  },
  {
    id: 'leisure',
    name: '文娱漫游区',
    tagline: '体验经济 · 文化消费',
    icon: '🎭',
    color: '#ec4899',
    glowColor: 'radial-gradient(circle, rgba(236,72,153,0.4) 0%, transparent 70%)',
    heat: 0.75,
    style: {
      gridArea: '4 / 4 / 6 / 6',
      '--district-color': '#ec4899'
    }
  },
  {
    id: 'green',
    name: '绿色能源港',
    tagline: '可持续 · 新能源',
    icon: '⚡',
    color: '#10b981',
    glowColor: 'radial-gradient(circle, rgba(16,185,129,0.4) 0%, transparent 70%)',
    heat: 0.82,
    style: {
      gridArea: '4 / 6 / 6 / 8',
      '--district-color': '#10b981'
    }
  }
]

const handleDistrictClick = (district) => {
  emit('district-click', district)
}
</script>

<style scoped>
.city-map-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: 
    radial-gradient(ellipse at 30% 40%, rgba(59,130,246,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, rgba(139,92,246,0.08) 0%, transparent 50%),
    linear-gradient(180deg, #0a0e27 0%, #030712 100%);
}

/* 城市网格布局 */
.city-grid {
  position: relative;
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 16px;
  padding: 80px 360px 180px 360px;
}

/* 背景网格动画 */
.grid-lines {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: grid-move 20s linear infinite;
}

@keyframes grid-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

/* 连接线动画 */
.connection-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.3;
}

.connect-line {
  stroke-dasharray: 5, 10;
  animation: line-flow 3s linear infinite;
}

@keyframes line-flow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -15; }
}

/* 区域卡片 */
.district-zone {
  position: relative;
  border-radius: 20px;
  background: 
    linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.8) 100%);
  border: 1px solid rgba(148,163,184,0.15);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 4px 20px rgba(0,0,0,0.3),
    inset 0 1px 0 rgba(255,255,255,0.05);
}

.district-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--district-color);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.district-zone:hover::before {
  opacity: 0.08;
}

.district-zone.selected::before {
  opacity: 0.15;
}

/* 区域辉光 */
.district-glow {
  position: absolute;
  inset: -50%;
  opacity: 0;
  transition: opacity 0.4s ease;
  filter: blur(40px);
  pointer-events: none;
}

.district-zone:hover .district-glow {
  opacity: 0.6;
}

.district-zone.selected .district-glow {
  opacity: 0.8;
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* 网格纹理 */
.district-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(45deg, rgba(255,255,255,0.02) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(255,255,255,0.02) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.02) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.02) 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
  pointer-events: none;
}

/* 区域内容 */
.district-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 20px;
  z-index: 1;
}

.district-icon {
  font-size: 48px;
  line-height: 1;
  margin-bottom: 12px;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.5));
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.district-zone:hover .district-icon {
  transform: scale(1.15) translateY(-4px);
  filter: drop-shadow(0 8px 20px var(--district-color));
}

.district-info {
  flex: 1;
}

.district-name {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 6px 0;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.5);
  transition: all 0.3s ease;
}

.district-zone:hover .district-name {
  color: var(--district-color);
  text-shadow: 0 0 20px var(--district-color);
}

.district-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  margin: 0;
  line-height: 1.4;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* 数据指标 */
.district-stats {
  margin-top: 16px;
}

.stat-bar {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-progress {
  height: 4px;
  background: rgba(15,23,42,0.8);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.stat-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--district-color), transparent);
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.stat-fill::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Hover效果增强 */
.district-zone:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: var(--district-color);
  box-shadow: 
    0 12px 40px rgba(0,0,0,0.4),
    0 0 0 1px var(--district-color),
    inset 0 1px 0 rgba(255,255,255,0.1);
}

.district-zone.selected {
  transform: translateY(-6px) scale(1.03);
  border-color: var(--district-color);
  box-shadow: 
    0 16px 50px rgba(0,0,0,0.5),
    0 0 40px var(--district-color),
    0 0 0 2px var(--district-color),
    inset 0 1px 0 rgba(255,255,255,0.15);
}

/* 响应式调整 */
@media (max-width: 1600px) {
  .city-grid {
    padding: 80px 280px 180px 280px;
  }
}

@media (max-width: 1400px) {
  .city-grid {
    padding: 80px 200px 180px 200px;
    gap: 12px;
  }
  
  .district-icon {
    font-size: 40px;
  }
  
  .district-name {
    font-size: 16px;
  }
}
</style>
