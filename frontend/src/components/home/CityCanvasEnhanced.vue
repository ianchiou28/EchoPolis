<template>
  <div class="city-canvas-container" ref="container">
    <canvas ref="canvas" @mousemove="onMouseMove" @click="onClick"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  districts: {
    type: Array,
    default: () => []
  },
  selectedDistrictId: String
})

const emit = defineEmits(['district-click'])

const container = ref(null)
const canvas = ref(null)
let ctx = null
let animationFrameId = null
let hoveredDistrict = null

// 城市区域定义 (等距视角) - 优化布局减少遮挡
const cityBuildings = [
  {
    id: 'finance',
    name: '中央银行群',
    icon: '🏦',
    color: '#3b82f6',
    position: { x: 320, y: 250 },
    size: { width: 120, height: 180 },
    depth: 80
  },
  {
    id: 'tech',
    name: '量化交易所',
    icon: '💹',
    color: '#8b5cf6',
    position: { x: 700, y: 150 },
    size: { width: 140, height: 200 },
    depth: 90
  },
  {
    id: 'housing',
    name: '房产中枢',
    icon: '🏙️',
    color: '#f59e0b',
    position: { x: 950, y: 300 },
    size: { width: 130, height: 170 },
    depth: 85
  },
  {
    id: 'learning',
    name: '知识引擎院',
    icon: '📚',
    color: '#14b8a6',
    position: { x: 520, y: 100 },
    size: { width: 110, height: 160 },
    depth: 75
  },
  {
    id: 'leisure',
    name: '文娱漫游区',
    icon: '🎭',
    color: '#ec4899',
    position: { x: 750, y: 400 },
    size: { width: 125, height: 155 },
    depth: 80
  },
  {
    id: 'green',
    name: '绿色能源港',
    icon: '⚡',
    color: '#10b981',
    position: { x: 280, y: 450 },
    size: { width: 115, height: 150 },
    depth: 70
  }
]

const setupCanvas = () => {
  if (!canvas.value || !container.value) return
  
  const dpr = window.devicePixelRatio || 1
  const rect = container.value.getBoundingClientRect()
  
  canvas.value.width = rect.width * dpr
  canvas.value.height = rect.height * dpr
  canvas.value.style.width = `${rect.width}px`
  canvas.value.style.height = `${rect.height}px`
  
  ctx = canvas.value.getContext('2d')
  ctx.scale(dpr, dpr)
}

// 绘制等距建筑
const drawIsometricBuilding = (building, isHovered, isSelected) => {
  if (!ctx) return
  
  const { x, y } = building.position
  const { width, height } = building.size
  const depth = building.depth
  
  ctx.save()
  
  // 建筑主体 (等距视角)
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + width / 2, y - depth / 2)
  ctx.lineTo(x + width, y)
  ctx.lineTo(x + width / 2, y + depth / 2)
  ctx.closePath()
  
  // 渐变填充
  const gradient = ctx.createLinearGradient(x, y - depth, x, y + depth)
  gradient.addColorStop(0, building.color + '80')
  gradient.addColorStop(1, building.color + '40')
  ctx.fillStyle = gradient
  ctx.fill()
  
  // 边框
  ctx.strokeStyle = building.color
  ctx.lineWidth = isSelected ? 3 : (isHovered ? 2 : 1)
  ctx.stroke()
  
  // 建筑立面
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x, y + height)
  ctx.lineTo(x + width / 2, y + height + depth / 2)
  ctx.lineTo(x + width / 2, y + depth / 2)
  ctx.closePath()
  
  const faceGradient = ctx.createLinearGradient(x, y, x, y + height)
  faceGradient.addColorStop(0, building.color + '60')
  faceGradient.addColorStop(1, building.color + '20')
  ctx.fillStyle = faceGradient
  ctx.fill()
  ctx.strokeStyle = building.color
  ctx.lineWidth = 1
  ctx.stroke()
  
  // 右侧面
  ctx.beginPath()
  ctx.moveTo(x + width / 2, y + depth / 2)
  ctx.lineTo(x + width / 2, y + height + depth / 2)
  ctx.lineTo(x + width, y + height)
  ctx.lineTo(x + width, y)
  ctx.closePath()
  
  const sideGradient = ctx.createLinearGradient(x + width / 2, y, x + width, y)
  sideGradient.addColorStop(0, building.color + '40')
  sideGradient.addColorStop(1, building.color + '30')
  ctx.fillStyle = sideGradient
  ctx.fill()
  ctx.strokeStyle = building.color
  ctx.stroke()
  
  // 发光效果
  if (isHovered || isSelected) {
    ctx.shadowColor = building.color
    ctx.shadowBlur = isSelected ? 30 : 20
    ctx.shadowOffsetX = 0
    ctx.shadowOffsetY = 0
    
    ctx.beginPath()
    ctx.moveTo(x, y)
    ctx.lineTo(x + width / 2, y - depth / 2)
    ctx.lineTo(x + width, y)
    ctx.lineTo(x + width / 2, y + depth / 2)
    ctx.closePath()
    ctx.strokeStyle = building.color
    ctx.lineWidth = 2
    ctx.stroke()
  }
  
  // 图标
  ctx.shadowBlur = 0
  ctx.font = '32px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = '#ffffff'
  ctx.fillText(building.icon, x + width / 2, y + 30)
  
  // 名称
  if (isHovered) {
    ctx.font = 'bold 14px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.shadowColor = 'rgba(0,0,0,0.8)'
    ctx.shadowBlur = 4
    ctx.fillText(building.name, x + width / 2, y - 20)
  }
  
  ctx.restore()
}

// 绘制背景网格
const drawGrid = () => {
  if (!ctx || !canvas.value) return
  
  const width = canvas.value.width / (window.devicePixelRatio || 1)
  const height = canvas.value.height / (window.devicePixelRatio || 1)
  
  ctx.save()
  ctx.strokeStyle = 'rgba(59, 130, 246, 0.1)'
  ctx.lineWidth = 1
  
  const gridSize = 50
  for (let x = 0; x < width; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
    ctx.stroke()
  }
  
  for (let y = 0; y < height; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }
  
  ctx.restore()
}

// 主渲染循环
const render = () => {
  if (!ctx || !canvas.value) return
  
  const width = canvas.value.width / (window.devicePixelRatio || 1)
  const height = canvas.value.height / (window.devicePixelRatio || 1)
  
  // 清空画布
  ctx.clearRect(0, 0, width, height)
  
  // 绘制背景渐变
  const bgGradient = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, Math.max(width, height) / 2)
  bgGradient.addColorStop(0, 'rgba(10, 14, 39, 0.95)')
  bgGradient.addColorStop(1, 'rgba(3, 7, 18, 0.98)')
  ctx.fillStyle = bgGradient
  ctx.fillRect(0, 0, width, height)
  
  // 绘制网格
  drawGrid()
  
  // 按深度排序绘制建筑
  const sorted = [...cityBuildings].sort((a, b) => a.position.y - b.position.y)
  
  sorted.forEach(building => {
    const isHovered = hoveredDistrict === building.id
    const isSelected = props.selectedDistrictId === building.id
    drawIsometricBuilding(building, isHovered, isSelected)
  })
  
  animationFrameId = requestAnimationFrame(render)
}

// 鼠标交互 - 按渲染顺序反向检测
const onMouseMove = (event) => {
  const rect = canvas.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // 按Y坐标排序，从后往前检测（与渲染顺序相反）
  const sorted = [...cityBuildings].sort((a, b) => b.position.y - a.position.y)
  
  let found = null
  for (const building of sorted) {
    if (isPointInBuilding(x, y, building)) {
      found = building.id
      break
    }
  }
  
  if (found !== hoveredDistrict) {
    hoveredDistrict = found
    canvas.value.style.cursor = found ? 'pointer' : 'default'
  }
}

const onClick = (event) => {
  const rect = canvas.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // 按Y坐标排序，从后往前检测（点击最上层的建筑）
  const sorted = [...cityBuildings].sort((a, b) => b.position.y - a.position.y)
  
  for (const building of sorted) {
    if (isPointInBuilding(x, y, building)) {
      emit('district-click', building)
      break
    }
  }
}

// 点击检测 - 更精确的等距视角碰撞检测
const isPointInBuilding = (px, py, building) => {
  const { x, y } = building.position
  const { width, height } = building.size
  const depth = building.depth
  
  // 扩大可点击区域，包括顶部菱形和图标区域
  // 顶部菱形区域
  const topCenterX = x + width / 2
  const topY = y - depth / 2
  
  // 检测顶部菱形
  if (py >= topY - 30 && py <= y + depth / 2 + 20) {
    const distToCenter = Math.abs(px - topCenterX)
    const allowedWidth = (width / 2) + 30
    if (distToCenter <= allowedWidth) {
      return true
    }
  }
  
  // 检测建筑主体（立面）
  if (py >= y && py <= y + height + depth) {
    if (px >= x - 15 && px <= x + width + 15) {
      return true
    }
  }
  
  return false
}

const handleResize = () => {
  setupCanvas()
}

onMounted(() => {
  setupCanvas()
  render()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>

<style scoped>
.city-canvas-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
