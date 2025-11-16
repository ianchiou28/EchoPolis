<template>
  <div class="game-shell" :class="{ 'game-shell--free': layout === 'free' }">
    <div class="glow-orb glow-orb--left" />
    <div class="glow-orb glow-orb--right" />
    <header class="game-shell__top panel-frame">
      <div class="game-shell__brand">
        <div class="logo-orb" />
        <div class="brand-text">
          <div class="brand-title">EchoPolis</div>
          <div class="brand-sub">AI 金融人生 · 策略养成实验场</div>
        </div>
      </div>
      <div class="game-shell__top-right">
        <slot name="top-right" />
      </div>
    </header>

    <main v-if="layout !== 'free'" :class="['game-shell__body', `game-shell__body--${layout}`]">
      <section class="game-shell__left panel-frame panel-frame--primary">
        <slot name="left" />
      </section>
      <section class="game-shell__center panel-frame">
        <slot name="center" />
      </section>
      <section class="game-shell__right panel-frame">
        <slot name="right" />
      </section>
    </main>
    <main v-else class="game-shell__canvas">
      <slot name="canvas" />
    </main>
    
    <section v-if="layout !== 'free'" class="game-shell__chat panel-frame">
      <slot name="chat" />
    </section>
  </div>
</template>

<script setup>
const props = defineProps({
  layout: { type: String, default: 'triple' }
})
</script>

<style scoped>
.game-shell {
  position: relative;
  min-height: 100vh;
  padding: 18px 26px 80px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background:
    radial-gradient(circle at 0% 0%, rgba(59,130,246,0.18), transparent 60%),
    radial-gradient(circle at 100% 100%, rgba(16,185,129,0.14), transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(236,72,153,0.12), transparent 55%),
    var(--bg-gradient);
}

.game-shell__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(15,23,42,0.85);
  border-bottom: 1px solid rgba(148,163,184,0.2);
  z-index: 1000;
  position: relative;
}

.game-shell--free {
  min-height: 100vh;
  padding: 0;
}

.game-shell__canvas {
  position: relative;
  flex: 1;
  min-height: 100vh;
  overflow: hidden;
}

.game-shell__brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-orb {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background:
    radial-gradient(circle at 30% 20%, #60a5fa, transparent 60%),
    radial-gradient(circle at 70% 80%, #22c55e, transparent 60%),
    radial-gradient(circle at 50% 50%, #1e293b 0, #020617 55%);
  box-shadow:
    0 0 20px rgba(96,165,250,0.55),
    0 0 34px rgba(45,212,191,0.45);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.brand-sub {
  font-size: 11px;
  opacity: 0.82;
}

.game-shell__top-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.game-shell__body {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(520px, 1.6fr) minmax(280px, 360px);
  gap: var(--shell-grid-gap);
  margin-top: 20px;
}

.game-shell__body--single {
  grid-template-columns: 1fr;
}

.game-shell__body--single .game-shell__center,
.game-shell__body--single .game-shell__right {
  display: none;
}

.game-shell__left,
.game-shell__center,
.game-shell__right {
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.game-shell__center {
  border: 1px solid rgba(59,130,246,0.3);
  background:
    radial-gradient(circle at 20% 0%, rgba(59,130,246,0.2), transparent 60%),
    linear-gradient(180deg, rgba(15,23,42,0.95), rgba(15,23,42,0.85));
}

.game-shell__bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-radius: 18px;
}

.game-shell__chat {
  min-height: 200px;
  border-radius: 24px;
  padding: 0;
}

@media (max-width: 1120px) {
  .game-shell__body {
    grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
    grid-template-rows: auto auto;
    grid-template-areas:
      'left right'
      'center center';
    gap: 14px;
  }
  .game-shell__left { grid-area: left; }
  .game-shell__center { grid-area: center; }
  .game-shell__right { grid-area: right; }
}

@media (max-width: 768px) {
  .game-shell {
    padding: 10px 10px 14px;
  }
  .game-shell__body {
    display: flex;
    flex-direction: column;
  }
}
</style>
