<template>
  <div class="foot-bar">
    <div>
      <p class="eyebrow">TIMELINE SYNC</p>
      <strong>{{ timeLabel }}</strong>
    </div>
    <button class="btn" @click="$emit('enter-world')">进入城市视图继续探索</button>
  </div>
</template>

<script setup>
const { timeLabel } = defineProps({
  timeLabel: String
})
</script>

<style scoped>
.foot-bar {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
