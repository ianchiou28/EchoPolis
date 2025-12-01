<template>
  <div class="view-container">
    <div class="view-header">
      <h2>档案库 // ARCHIVES</h2>
      <div class="header-line"></div>
    </div>

    <div class="archives-content">
      <div class="archive-card full-height">
        <div class="archive-header">通讯记录</div>
        <div class="archive-body scrollable chat-history">
          <div v-if="!messages.length" class="empty-state">
            暂无通讯记录
          </div>
          <div v-else class="message-list">
            <div v-for="(msg, index) in messages" :key="index" :class="['message-item', msg.role]">
              <div class="msg-meta">
                <span class="role">{{ msg.role === 'user' ? 'USER' : 'ECHO' }}</span>
                <span class="time">{{ formatDate(msg.timestamp) }}</span>
              </div>
              <div class="msg-content">{{ msg.text }}</div>
              <div class="msg-reflection" v-if="msg.reflection">
                <span class="prefix">>> 思考:</span> {{ msg.reflection }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useGameStore } from '../../stores/game'

const gameStore = useGameStore()
const messages = computed(() => gameStore.chatMessages)

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view-header h2 {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 8px 0;
  color: var(--term-text);
}

.header-line {
  height: 2px;
  background: var(--term-border);
  margin-bottom: 24px;
}

.archives-content {
  flex: 1;
  overflow: hidden;
}

.full-height {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  padding: 12px;
  border: 1px solid var(--term-border);
  max-width: 80%;
}

.message-item.user {
  align-self: flex-end;
  background: rgba(0,0,0,0.05);
  border-color: var(--term-text-secondary);
}

.message-item.ai {
  align-self: flex-start;
  background: rgba(255, 85, 0, 0.05);
  border-color: var(--term-accent);
}

.msg-meta {
  font-size: 10px;
  color: var(--term-text-secondary);
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
}

.msg-content {
  font-size: 13px;
  line-height: 1.4;
}

.msg-reflection {
  margin-top: 8px;
  font-size: 11px;
  color: var(--term-text-secondary);
  font-style: italic;
  border-top: 1px dashed var(--term-border);
  padding-top: 4px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--term-text-secondary);
}
</style>
