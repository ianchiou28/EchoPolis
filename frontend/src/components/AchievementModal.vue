<template>
  <transition name="modal">
    <div class="achievement-overlay" @click="$emit('close')">
      <div class="achievement-modal" @click.stop>
        <div class="achievement-icon">
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
        
        <button class="confirm-btn" @click="$emit('close')">
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
  background: rgba(0,0,0,0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.achievement-modal {
  position: relative;
  width: 420px;
  max-width: 90vw;
  padding: 2.5rem 2rem;
  text-align: center;
  background: var(--term-panel-bg);
  border: 3px solid var(--term-accent);
  border-radius: 16px;
  box-shadow: 0 0 40px var(--term-accent-glow, rgba(255, 85, 0, 0.3));
  animation: achievement-pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes achievement-pop {
  0% {
    opacity: 0;
    transform: scale(0.8) translateY(30px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.achievement-icon {
  font-size: 64px;
  margin: 0 auto 1.25rem;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--term-bg);
  border-radius: 50%;
  border: 3px solid var(--term-accent);
}

.achievement-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--term-accent);
}

.achievement-name {
  margin: 0 0 0.75rem 0;
  font-size: 1.75rem;
  font-weight: 900;
  color: var(--term-text);
}

.achievement-desc {
  margin: 0 0 1.5rem 0;
  color: var(--term-text-secondary);
  font-size: 1rem;
  line-height: 1.5;
}

.achievement-reward {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  background: rgba(34, 197, 94, 0.15);
  border: 2px solid var(--term-success);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.reward-label {
  font-size: 0.9rem;
  color: var(--term-text-secondary);
}

.reward-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--term-success);
}

.achievement-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.75rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--term-text-secondary);
}

.stat-icon {
  font-size: 1.25rem;
}

.confirm-btn {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 700;
  background: var(--term-accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
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

.modal-leave-active .achievement-modal {
  animation: achievement-pop 0.2s ease reverse;
}
</style>
