<template>
  <transition-group name="float" tag="div" class="floating-text-container">
    <div
      v-for="text in floatingTexts"
      :key="text.id"
      :class="['floating-text', text.type]"
      :style="{
        left: text.x + 'px',
        top: text.y + 'px'
      }"
      @animationend="removeText(text.id)"
    >
      {{ text.content }}
    </div>
  </transition-group>
</template>

<script setup>
import { ref } from 'vue'

const floatingTexts = ref([])
let textIdCounter = 0

// 添加飘字
const addFloatingText = (content, x, y, type = 'neutral') => {
  const id = textIdCounter++
  floatingTexts.value.push({
    id,
    content,
    x,
    y,
    type
  })
  
  // 2秒后自动移除
  setTimeout(() => {
    removeText(id)
  }, 2000)
}

// 移除飘字
const removeText = (id) => {
  const index = floatingTexts.value.findIndex(t => t.id === id)
  if (index > -1) {
    floatingTexts.value.splice(index, 1)
  }
}

// 暴露方法供父组件调用
defineExpose({
  addFloatingText
})
</script>

<style scoped>
.floating-text-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 9999;
}

.floating-text {
  position: fixed;
  pointer-events: none;
  font-weight: 700;
  font-size: 28px;
  text-shadow: 0 0 15px currentColor, 0 2px 4px rgba(0,0,0,0.8);
  animation: float-up 2s ease-out forwards;
  white-space: nowrap;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

.floating-text.positive {
  color: #10b981;
  text-shadow: 
    0 0 15px #10b981,
    0 0 30px rgba(16,185,129,0.5),
    0 2px 4px rgba(0,0,0,0.8);
}

.floating-text.negative {
  color: #ef4444;
  text-shadow: 
    0 0 15px #ef4444,
    0 0 30px rgba(239,68,68,0.5),
    0 2px 4px rgba(0,0,0,0.8);
}

.floating-text.neutral {
  color: #3b82f6;
  text-shadow: 
    0 0 15px #3b82f6,
    0 0 30px rgba(59,130,246,0.5),
    0 2px 4px rgba(0,0,0,0.8);
}

@keyframes float-up {
  0% {
    opacity: 0;
    transform: translateY(0) scale(0.8);
  }
  10% {
    opacity: 1;
    transform: translateY(-10px) scale(1);
  }
  80% {
    opacity: 1;
    transform: translateY(-40px) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-60px) scale(0.9);
  }
}

.float-enter-active {
  animation: float-up 2s ease-out;
}
</style>
