<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="log-modal">
      <div class="modal-header">
        <span class="modal-title">{{ title }}</span>
        <button class="close-btn" @click="$emit('close')">X</button>
      </div>
      
      <div class="modal-content custom-scrollbar">
        <div class="log-meta" v-if="meta">
          <span v-for="(val, key) in meta" :key="key" class="meta-tag">
            {{ key }}: {{ val }}
          </span>
        </div>
        
        <div class="log-body">
          <slot></slot>
        </div>
        
        <div class="log-footer">
          [ END OF LOG ]
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: 'SYSTEM_LOG'
  },
  meta: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['close'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  backdrop-filter: blur(4px);
}

.log-modal {
  width: 600px;
  max-width: 90vw;
  background: var(--term-panel-bg);
  border: 2px solid var(--term-border);
  box-shadow: 8px 8px 0 rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

[data-theme='dark'] .log-modal {
  border-color: var(--term-accent);
  box-shadow: 8px 8px 0 var(--term-accent);
}

.modal-header {
  background: var(--term-border);
  color: #FFF;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-mono);
}

[data-theme='dark'] .modal-header {
  background: var(--term-accent);
  color: #000;
}

.modal-title {
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.close-btn {
  background: transparent;
  border: 1px solid #FFF;
  color: #FFF;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-family: var(--font-mono);
  display: flex;
  align-items: center;
  justify-content: center;
}

[data-theme='dark'] .close-btn {
  border-color: #000;
  color: #000;
}

.close-btn:hover {
  background: #FFF;
  color: #000;
}

.modal-content {
  padding: 24px;
  overflow-y: auto;
}

.log-meta {
  margin-bottom: 20px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-tag {
  background: rgba(0,0,0,0.1);
  padding: 2px 8px;
  font-size: 10px;
  font-family: var(--font-mono);
  border: 1px solid var(--term-border);
}

[data-theme='dark'] .meta-tag {
  background: rgba(255,255,255,0.1);
  border-color: var(--term-text);
}

.log-body {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.log-footer {
  text-align: center;
  font-family: var(--font-mono);
  font-size: 10px;
  opacity: 0.5;
  letter-spacing: 2px;
}
</style>
