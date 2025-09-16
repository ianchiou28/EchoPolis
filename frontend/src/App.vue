<template>
  <div id="app">
    <header class="header">
      <h1>🌆 Echopolis - 回声都市</h1>
      <p>一个超个人化AI驱动的社会金融模拟器</p>
    </header>
    <router-view />
  </div>
</template>

<script setup>
// Vue 3 Composition API
</script>

<style scoped>
.header {
  text-align: center;
  color: white;
  padding: 20px 0;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.header h1 {
  margin: 0;
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.header p {
  margin: 10px 0 0 0;
  opacity: 0.9;
  font-size: 1.1em;
}
</style>