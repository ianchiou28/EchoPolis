<template>
  <transition name="modal">
    <div class="achievement-overlay" @click="$emit('close')">
      <div class="achievement-modal glass-panel-enhanced" @click.stop>
        <div class="achievement-glow"></div>
        
        <div class="achievement-icon pulse-ring">
          {{ achievement.icon }}
        </div>
        
        <h2 class="achievement-title">
          🎉 成就解锁！
        </h2>
        
        <h3 class="achievement-name">
          {{ achievement.name }}
        </h3>
        
        <p class="achievement-desc">
          {{ achievement.description }}
        </p>
        
        <div class="achievement-reward" v-if="achievement.reward">
          <span class="reward-label">奖励</span>
          <span class="reward-value">{{ achievement.reward }}</span>
        </div>
        
        <div class="achievement-stats">
          <div class="stat">
            <span class="stat-icon">🏆</span>
            <span>{{ achievement.rarity }}</span>
          </div>
          <div class="stat">
            <span class="stat-icon">⭐</span>
            <span>{{ achievement.points }} 点</span>
          </div>
        </div>
        
        <button class="btn primary large" @click="$emit('close')">
          太棒了！
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  achievement: {
    type: Object,
    required: true
  }
})

defineEmits(['close'])
</script>

<style scoped>
.achievement-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(10px);
}

.achievement-modal {
  position: relative;
  width: 500px;
  max-width: 90vw;
  padding: 48px 40px;
  text-align: center;
  overflow: hidden;
  animation: achievement-pop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes achievement-pop {
  0% {
    opacity: 0;
    transform: scale(0.5) translateY(100px);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.achievement-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59,130,246,0.3), transparent 70%);
  animation: glow-pulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glow-pulse {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.achievement-icon {
  font-size: 80px;
  margin: 0 auto 24px;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(139,92,246,0.3));
  border-radius: 50%;
  border: 3px solid rgba(59,130,246,0.5);
  position: relative;
  z-index: 1;
}

.achievement-title {
  margin: 0 0 16px 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
}

.achievement-name {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  position: relative;
  z-index: 1;
}

.achievement-desc {
  margin: 0 0 24px 0;
  color: rgba(148,163,184,0.9);
  font-size: 15px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.achievement-reward {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 24px;
  background: rgba(16,185,129,0.2);
  border: 1px solid rgba(16,185,129,0.4);
  border-radius: 12px;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.reward-label {
  font-size: 14px;
  color: rgba(148,163,184,0.8);
}

.reward-value {
  font-size: 18px;
  font-weight: 700;
  color: #10b981;
}

.achievement-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 32px;
  position: relative;
  z-index: 1;
}

.stat {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(148,163,184,0.9);
}

.stat-icon {
  font-size: 20px;
}

.btn.large {
  padding: 14px 48px;
  font-size: 16px;
  font-weight: 700;
  position: relative;
  z-index: 1;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .achievement-modal {
  animation: achievement-pop 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.modal-leave-active .achievement-modal {
  animation: achievement-pop 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) reverse;
}
</style>
