<template>
  <div class="city-top-down-container">
    <!-- 全息背景层 -->
    <div class="map-background">
      <div class="holographic-grid"></div>
      <div class="scan-line"></div>
      <div class="vignette"></div>
      <!-- 动态粒子背景 (可选) -->
      <div class="particles"></div>
    </div>

    <!-- 3D 场景容器 -->
    <div class="scene-3d-wrapper">
      <!-- SVG 交互地图层 -->
      <svg 
        class="interaction-layer"
        viewBox="0 0 1920 1080" 
        preserveAspectRatio="xMidYMid slice"
        @click="handleBackgroundClick"
      >
        <defs>
          <!-- 高级霓虹滤镜 -->
          <filter id="neon-glow-intense" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
            <feGaussianBlur stdDeviation="10" result="coloredBlurLarge"/>
            <feMerge>
              <feMergeNode in="coloredBlurLarge"/>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>

          <!-- 区域填充渐变 (模拟全息光体) -->
          <linearGradient id="holo-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="currentColor" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="currentColor" stop-opacity="0.05"/>
          </linearGradient>
          
          <!-- 扫描线纹理 -->
          <pattern id="scan-lines" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
            <rect x="0" y="0" width="4" height="1" fill="currentColor" opacity="0.3"/>
          </pattern>
        </defs>

        <!-- 装饰性轨道环 -->
        <g class="orbital-rings">
          <circle cx="960" cy="540" r="300" class="ring ring-inner" />
          <circle cx="960" cy="540" r="550" class="ring ring-middle" />
          <circle cx="960" cy="540" r="800" class="ring ring-outer" />
        </g>

        <!-- 道路网络 (数据流) -->
        <g class="roads-layer">
          <path 
            v-for="(road, index) in roads" 
            :key="`road-${index}`"
            :d="road.d"
            class="main-road"
          />
        </g>

        <!-- 共鸣波纹 (当有回响时触发) -->
        <g class="resonance-layer" v-if="lastEchoLocation">
          <circle 
            :cx="lastEchoLocation.x" 
            :cy="lastEchoLocation.y" 
            r="0" 
            class="resonance-wave"
            :stroke="lastEchoColor"
          />
        </g>

        <!-- 区域区块 -->
        <g class="zones-layer">
          <g 
            v-for="zone in zones" 
            :key="zone.id"
            class="district-zone"
            :class="{ 'is-active': activeZoneId === zone.id }"
            @click.stop="handleZoneClick(zone)"
            @mouseenter="hoverZoneId = zone.id"
            @mouseleave="hoverZoneId = null"
            :style="{ color: zone.color }"
          >
            <!-- 区域光晕背景 -->
            <path 
              :d="zone.path" 
              class="zone-glow"
              :fill="zone.color"
            />

            <!-- 区域主体 (底部投影) -->
            <path 
              :d="zone.path" 
              class="zone-base"
              :stroke="zone.color"
              fill="url(#holo-gradient)"
            />
            
            <!-- 区域纹理覆盖 (扫描线) -->
            <path 
              :d="zone.path" 
              fill="url(#scan-lines)" 
              class="zone-texture"
            />

            <!-- 悬浮标签连接线 -->
            <polyline
              v-if="activeZoneId === zone.id || hoverZoneId === zone.id"
              :points="`${zone.center.x},${zone.center.y} ${zone.labelPos.x},${zone.labelPos.y}`"
              class="connector-line"
              :stroke="zone.color"
            />

            <!-- 区域中心图标/核心 -->
            <circle 
              :cx="zone.center.x" 
              :cy="zone.center.y" 
              r="6" 
              :fill="zone.color"
              class="zone-core"
            />
            
            <!-- 3D 锚点光柱 (纯视觉) -->
            <circle 
              :cx="zone.center.x" 
              :cy="zone.center.y" 
              r="20" 
              fill="none"
              :stroke="zone.color"
              stroke-width="1"
              opacity="0.3"
              class="zone-anchor-ring"
            />
          </g>
        </g>
      </svg>

      <!-- UI 悬浮层 (跟随 3D 变换) -->
      <div class="ui-overlay">
        <Transition name="tech-slide">
          <div 
            v-if="activeZone" 
            class="zone-info-card"
            :class="activeZone.cardClass || 'pop-up'"
            :style="{ 
              left: (activeZone.labelPos.x / 19.2) + '%', 
              top: (activeZone.labelPos.y / 10.8) + '%',
              '--theme-color': activeZone.color
            }"
          >
            <!-- 动态边框 -->
            <div class="card-border-anim"></div>
            
            <div class="card-header">
              <div class="header-top">
                <span class="zone-code">SEC-{{ activeZone.id.toString().padStart(2, '0') }}</span>
                <div class="status-badge">
                  <span class="pulse-dot" :style="{ background: activeZone.color }"></span>
                  运行中
                </div>
              </div>
              <h3>{{ activeZone.name }}</h3>
            </div>

            <div class="card-body">
              <div class="stat-row">
                <span class="stat-label">系统负载</span>
                <div class="stat-bar-container">
                  <div class="stat-bar" :style="{ width: activeZone.stats.load + '%', background: activeZone.color }"></div>
                </div>
                <span class="stat-value">{{ activeZone.stats.load }}%</span>
              </div>
              
              <div class="stat-row">
                <span class="stat-label">信任同步</span>
                <div class="stat-bar-container">
                  <div class="stat-bar" :style="{ width: activeZone.stats.trust + '%', background: activeZone.color }"></div>
                </div>
                <span class="stat-value">{{ activeZone.stats.trust }}%</span>
              </div>

              <p class="zone-desc">{{ activeZone.description }}</p>
            </div>

            <div class="card-footer">
              <button class="access-btn" @click="enterZone(activeZone)">
                <span class="btn-text">接入神经网</span>
                <span class="btn-icon">→</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useGameStore } from '@/stores/game'

const props = defineProps({
  districts: { type: Array, default: () => [] },
  selectedDistrictId: { type: [Number, String], default: null },
  // 新增：用于触发共鸣效果
  echoTrigger: { type: Object, default: null } 
})

const emit = defineEmits(['district-click'])

const gameStore = useGameStore()
const internalActiveZoneId = ref(null)
const hoverZoneId = ref(null)
const lastEchoLocation = ref(null)
const lastEchoColor = ref('#fff')

// 监听外部选择
watch(() => props.selectedDistrictId, (newVal) => {
  internalActiveZoneId.value = newVal
}, { immediate: true })

// 监听回响触发
watch(() => props.echoTrigger, (newVal) => {
  if (newVal && newVal.districtId) {
    triggerResonance(newVal.districtId)
  }
})

function triggerResonance(districtId) {
  const zone = zones.value.find(z => z.id === districtId)
  if (zone) {
    lastEchoLocation.value = zone.center
    lastEchoColor.value = zone.color
    // 动画结束后清除
    setTimeout(() => {
      lastEchoLocation.value = null
    }, 2000)
  }
}

// 静态布局数据
const ZONE_LAYOUT = {
  finance: {
    path: "M 880 460 L 1040 460 L 1080 540 L 1040 620 L 880 620 L 840 540 Z",
    center: { x: 960, y: 540 },
    labelPos: { x: 960, y: 580 },
    cardClass: 'pop-up',
    defaultName: '中央指挥枢纽',
    defaultDesc: '城市的大脑。处理所有行政指令与AI核心运算。',
    color: '#3b82f6'
  },
  green: { // 原工业
    path: "M 500 650 L 700 650 L 700 750 L 800 750 L 800 850 L 600 850 L 600 750 L 500 750 Z",
    center: { x: 650, y: 750 },
    labelPos: { x: 780, y: 650 },
    cardClass: 'pop-up',
    defaultName: '工业制造矩阵',
    defaultDesc: '自动化生产线与能源反应堆集群。',
    color: '#f59e0b'
  },
  housing: { // 原居住
    path: "M 1150 150 L 1450 150 L 1450 350 L 1350 350 L 1350 450 L 1050 450 L 1050 250 L 1150 250 Z",
    center: { x: 1250, y: 300 },
    labelPos: { x: 1000, y: 450 },
    cardClass: 'pop-down',
    defaultName: '居民生活蜂巢',
    defaultDesc: '高密度居住单元，公民的栖息地。',
    color: '#10b981'
  },
  learning: { // 原科研
    path: "M 560 200 L 760 150 L 860 300 L 710 450 L 510 350 Z",
    center: { x: 680, y: 290 },
    labelPos: { x: 780, y: 450 },
    cardClass: 'pop-down',
    defaultName: '科研神经网络',
    defaultDesc: '前沿技术研发中心与量子实验室。',
    color: '#8b5cf6'
  },
  leisure: { // 原娱乐
    path: "M 1100 650 L 1400 650 L 1450 800 L 1250 950 L 1050 800 Z",
    center: { x: 1250, y: 770 },
    labelPos: { x: 1140, y: 650 },
    cardClass: 'pop-up',
    defaultName: '娱乐全息港',
    defaultDesc: '感官体验中心与虚拟现实剧场。',
    color: '#ec4899'
  }
}

// 合并动态数据
const zones = computed(() => {
  // 如果没有传入 districts，使用默认布局生成基础数据
  const districtData = props.districts.length > 0 ? props.districts : []
  
  return Object.entries(ZONE_LAYOUT).map(([id, layout]) => {
    const dynamicData = districtData.find(d => d.id === id) || {}
    
    return {
      id,
      ...layout,
      name: dynamicData.name || layout.defaultName,
      description: dynamicData.tagline || layout.defaultDesc,
      stats: {
        load: Math.round((dynamicData.heat || 0.5) * 100),
        trust: Math.round((dynamicData.prosperity || 0.5) * 100)
      }
    }
  })
})

// 装饰性道路 (重新连接新坐标)
const roads = [
  { d: "M 960 540 L 650 750" }, // Center to Industry
  { d: "M 960 540 L 1250 300" }, // Center to Residential
  { d: "M 960 540 L 680 290" }, // Center to Research
  { d: "M 960 540 L 1250 770" }, // Center to Entertainment
  { d: "M 650 750 Q 960 900 1250 770" }, // Outer ring bottom
  { d: "M 680 290 Q 960 150 1250 300" }, // Outer ring top
]

const activeZone = computed(() => {
  return zones.value.find(z => z.id === internalActiveZoneId.value)
})

function handleZoneClick(zone) {
  if (internalActiveZoneId.value === zone.id) {
    internalActiveZoneId.value = null
    emit('district-click', null)
  } else {
    internalActiveZoneId.value = zone.id
    emit('district-click', zone)
  }
}

function handleBackgroundClick() {
  internalActiveZoneId.value = null
  emit('district-click', null)
}

function enterZone(zone) {
  console.log('Accessing neural link:', zone.name)
  emit('district-click', zone)
}
</script>

<style scoped>
.city-top-down-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #02040a;
  font-family: 'Rajdhani', sans-serif;
  /* 移除容器级 perspective，避免与内部 3D 变换冲突导致闪烁 */
  /* transform: translate3d(0, 0, 0); */
}

/* --- 背景层 --- */
.map-background {
  position: absolute;
  inset: 0;
  background: #02040a; /* 纯黑底色，避免渐变导致的条带 */
  z-index: 0;
  overflow: hidden;
}

/* 星空背景 - 移除旋转动画以解决闪烁 */
.map-background::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(1.5px 1.5px at 20px 30px, rgba(255,255,255,0.8), transparent),
    radial-gradient(1.5px 1.5px at 40px 70px, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 50px 160px, rgba(255,255,255,0.7), transparent),
    radial-gradient(1.5px 1.5px at 90px 40px, rgba(255,255,255,0.8), transparent),
    radial-gradient(2px 2px at 130px 80px, rgba(255,255,255,0.6), transparent);
  background-size: 250px 250px;
  opacity: 0.4;
}

/* 3D 全息网格效果 - 强力显形版 */
.holographic-grid {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  
  /* 使用更亮的颜色和更粗的线条 */
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.5) 2px, transparent 2px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.5) 2px, transparent 2px);
  background-size: 120px 120px; /* 网格格变大一点 */
  
  /* 调整 3D 参数，减小倾斜角度以匹配 2D 区域 */
  transform: perspective(1000px) rotateX(30deg) scale(1.4);
  transform-origin: center center;
  
  animation: grid-scroll 20s linear infinite;
  opacity: 0.5; /* 稍微降低亮度，不要抢夺前景注意力 */
  pointer-events: none;
  
  /* 添加底部渐变遮罩，让远处柔和消失，避免生硬边缘 */
  mask-image: linear-gradient(to bottom, transparent 0%, black 30%, black 80%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 30%, black 80%, transparent 100%);
  opacity: 0.3; /* 降低背景亮度，突出前景区域 */
}

@keyframes grid-scroll {
  0% { background-position: 0 0; }
  100% { background-position: 0 100px; }
}

.orbital-rings .ring {
  fill: none;
  stroke: rgba(59, 130, 246, 0.1);
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.ring-inner { stroke-dasharray: 10 20; animation: rotate-cw 60s linear infinite; }
.ring-middle { stroke-dasharray: 5 15; animation: rotate-ccw 80s linear infinite; }
.ring-outer { stroke-dasharray: 20 40; animation: rotate-cw 120s linear infinite; opacity: 0.5; }

@keyframes rotate-cw { to { transform: rotate(360deg); transform-origin: 960px 540px; } }
@keyframes rotate-ccw { to { transform: rotate(-360deg); transform-origin: 960px 540px; } }

/* --- 3D 场景容器 --- */
.scene-3d-wrapper {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  /* 与背景网格保持一致的 3D 变换 */
  transform: perspective(1000px) rotateX(30deg) scale(1.4);
  transform-style: preserve-3d;
  pointer-events: none; /* 让点击穿透到 SVG */
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* --- 交互层 --- */
.interaction-layer {
  position: absolute;
  width: 100%;
  height: 100%;
  /* SVG 本身不需要再次变换，因为它在 wrapper 里 */
  pointer-events: auto; /* 恢复交互 */
  overflow: visible; /* 允许 3D 元素溢出 */
}

.main-road {
  fill: none;
  stroke: rgba(59, 130, 246, 0.4); /* 更亮的道路 */
  stroke-width: 3;
  stroke-dasharray: 15 15;
  filter: drop-shadow(0 0 5px rgba(59, 130, 246, 0.5));
  animation: data-flow 2s linear infinite;
}

@keyframes data-flow {
  to { stroke-dashoffset: -30; }
}

/* 区域样式 - 全息投影风格 */
.district-zone {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.zone-base {
  /* 底部投影/基座 */
  stroke-width: 2;
  stroke-dasharray: 0; /* 实线 */
  transition: all 0.3s ease;
  filter: drop-shadow(0 0 10px currentColor);
}

.zone-glow {
  /* 内部发光 */
  fill-opacity: 0;
  filter: url(#neon-glow-intense);
  transition: fill-opacity 0.3s ease;
  opacity: 0.3;
}

.zone-texture {
  /* 扫描线纹理 */
  opacity: 0.5;
  pointer-events: none;
}

.zone-core {
  opacity: 0.8;
  transition: all 0.3s ease;
  stroke: rgba(255,255,255,0.8);
  stroke-width: 1px;
  filter: drop-shadow(0 0 5px currentColor);
}

.zone-anchor-ring {
  transform-box: fill-box;
  transform-origin: center;
  animation: spin-slow 10s linear infinite;
}

@keyframes spin-slow {
  to { transform: rotate(360deg); }
}

/* 悬停状态 */
.district-zone:hover .zone-base {
  stroke-width: 4;
  fill-opacity: 0.4; /* 增加填充亮度 */
}

.district-zone:hover .zone-glow {
  fill-opacity: 0.3;
  opacity: 1;
}

.district-zone:hover .zone-core {
  r: 8;
  opacity: 1;
  filter: drop-shadow(0 0 15px currentColor);
}

/* 激活状态 */
.district-zone.is-active .zone-base {
  stroke-width: 4;
  fill-opacity: 0.6;
}

.district-zone.is-active .zone-glow {
  fill-opacity: 0.5;
  opacity: 1;
}

.connector-line {
  fill: none;
  stroke-width: 2;
  stroke-dasharray: 10 5;
  animation: draw-line 1s linear infinite;
  opacity: 0.8;
}

@keyframes draw-line { to { stroke-dashoffset: -15; } }

/* 共鸣波纹动画 */
.resonance-wave {
  fill: none;
  stroke-width: 4;
  opacity: 0;
  animation: ripple 2s ease-out forwards;
}

@keyframes ripple {
  0% { r: 0; opacity: 0.8; stroke-width: 4; }
  100% { r: 500; opacity: 0; stroke-width: 0; }
}

/* --- UI 卡片 --- */
.ui-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 10;
  /* 保持在 3D 空间中 */
  transform-style: preserve-3d;
}

.zone-info-card {
  position: absolute;
  width: 340px;
  /* 提高不透明度，使用深色背景防止透视干扰 */
  background: rgba(2, 4, 10, 0.95);
  /* 降低模糊半径，提高渲染清晰度 */
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2px;
  pointer-events: auto;
  color: #fff;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 90% 100%, 0 100%);
  
  /* 关键：反向旋转以直立显示，并添加悬浮动画 */
  /* 默认向上弹出 (pop-up) */
  /* 先沿 Z 轴抬起 (translateZ) 避免穿模，再旋转直立 */
  transform: translate(-50%, -100%) translateZ(50px) rotateX(-30deg) scale(0.8); 
  transform-origin: bottom center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.8); 
  
  /* 稍微抬起一点，避免穿模 */
  margin-top: -20px; 
  
  /* 确保在 3D 空间中最上层 */
  z-index: 100;
}

/* 向下弹出变体 */
.zone-info-card.pop-down {
  /* 向下弹出的卡片需要抬得更高，因为下方的地图平面在 3D 空间中更靠近观众 */
  transform: translate(-50%, 0) translateZ(200px) rotateX(-30deg) scale(0.8);
  transform-origin: top center;
  margin-top: 20px;
}

.card-border-anim {
  position: absolute;
  inset: 0;
  border: 1px solid var(--theme-color);
  opacity: 0.5;
  clip-path: polygon(0 0, 100% 0, 100% 85%, 90% 100%, 0 100%);
  pointer-events: none;
}

.card-header {
  background: rgba(255, 255, 255, 0.03);
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.zone-code {
  font-family: monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 1px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--theme-color);
  font-weight: 600;
  text-transform: uppercase;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  box-shadow: 0 0 5px currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

.card-header h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
}

.card-body {
  padding: 20px;
}

.stat-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
}

.stat-label {
  width: 70px;
  color: rgba(255, 255, 255, 0.6);
}

.stat-bar-container {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 12px;
  position: relative;
}

.stat-bar {
  height: 100%;
  box-shadow: 0 0 8px currentColor;
  position: relative;
}

.stat-bar::after {
  content: '';
  position: absolute;
  right: 0;
  top: -2px;
  width: 2px;
  height: 8px;
  background: #fff;
}

.stat-value {
  width: 40px;
  text-align: right;
  font-family: monospace;
  font-weight: bold;
  color: var(--theme-color);
}

.zone-desc {
  margin-top: 16px;
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.7);
}

.card-footer {
  padding: 0 20px 20px;
}

.access-btn {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--theme-color);
  color: var(--theme-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.access-btn:hover {
  background: var(--theme-color);
  color: #000;
  box-shadow: 0 0 20px var(--theme-color);
}

/* 动画 */
.tech-slide-enter-active,
.tech-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
}

.tech-slide-enter-from,
.tech-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, transparent, rgba(59, 130, 246, 0.1) 50%, transparent);
  animation: scan 8s linear infinite;
  pointer-events: none;
  opacity: 0.5;
}

@keyframes scan {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 100%;
  }
}
</style>