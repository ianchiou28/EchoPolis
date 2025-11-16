<template>
  <div id="app-shell">
    <div class="game-bg" />
    <div class="city-skyline" />
    <div class="game-grid-overlay" />
    <router-view />
  </div>
</template>

<script setup>
</script>

<style scoped>
#app-shell {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}
</style>
