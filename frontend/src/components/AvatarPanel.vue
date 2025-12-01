<template>
  <div class="avatar-panel card glass">
    <div class="avatar" :class="[`mood-${mood}`]">
      <!-- Hair / headshape -->
      <div class="hair"></div>
      <div class="head">
        <!-- Eyes -->
        <div class="eye left">
          <div class="pupil" :style="pupilStyle"></div>
        </div>
        <div class="eye right">
          <div class="pupil" :style="pupilStyle"></div>
        </div>
        <!-- Eyebrows -->
        <div class="brow left"></div>
        <div class="brow right"></div>
        <!-- Mouth -->
        <div class="mouth"></div>
        <!-- Cheeks -->
        <div class="cheek left"></div>
        <div class="cheek right"></div>
      </div>
      <!-- Body -->
      <div class="body">
        <div class="neck"></div>
        <div class="torso">
          <div class="glow"></div>
        </div>
        <div class="hand left"></div>
        <div class="hand right"></div>
      </div>
    </div>
    <div class="caption">
      <div class="name">{{ name }}</div>
      <div class="subtitle">情绪：{{ moodLabel }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mood: { type: String, default: 'neutral' }, // ecstatic|happy|neutral|worried|sad|despair
  name: { type: String, default: 'Echo' }
})

const moodLabel = computed(() => ({
  ecstatic: '狂喜',
  happy: '开心',
  neutral: '平静',
  worried: '担忧',
  sad: '难过',
  despair: '崩溃'
})[props.mood] || '平静')

const pupilStyle = computed(() => {
  // Tiny drift for a living feel
  const x = Math.random() * 2 - 1
  const y = Math.random() * 2 - 1
  return { transform: `translate(${x}px, ${y}px)` }
})
</script>

<style scoped>
.avatar-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 18px;
  width: 320px;
}

.avatar {
  position: relative;
  width: 220px;
  height: 260px;
  filter: drop-shadow(0 8px 24px rgba(0,0,0,.25));
  transition: transform .35s var(--ease-standard), filter .35s var(--ease-standard);
}

.avatar:hover { transform: translateY(-2px); }

/* Head */
.head {
  position: absolute;
  left: 50%;
  top: 35px;
  width: 160px;
  height: 160px;
  transform: translateX(-50%);
  background: radial-gradient(120px 120px at 50% 40%, #ffc8b0 0%, #ffb79a 60%, #f0a189 100%);
  border-radius: 48% 52% 46% 54% / 58% 56% 44% 42%;
  border: 1px solid #e79a82;
}

.hair {
  position: absolute;
  left: 50%;
  top: 15px;
  transform: translateX(-50%);
  width: 175px;
  height: 90px;
  background: linear-gradient(180deg, #2f3a62, #1f2848);
  border-radius: 50% 50% 35% 35% / 60% 60% 40% 40%;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,.25));
}

.eye {
  position: absolute;
  top: 62px;
  width: 26px;
  height: 26px;
  background: #fff;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(0,0,0,.1);
}
.eye.left { left: 40px; }
.eye.right { right: 40px; }
.pupil {
  position: absolute;
  left: 50%; top: 50%;
  width: 10px; height: 10px; background: #1c243f; border-radius: 50%;
  transform: translate(-50%, -50%);
}

.brow { position: absolute; top: 48px; width: 36px; height: 8px; border-radius: 6px; background: #1c243f; }
.brow.left { left: 28px; }
.brow.right { right: 28px; }

.mouth {
  position: absolute;
  left: 50%; bottom: 42px;
  width: 54px; height: 28px;
  transform: translateX(-50%);
  border: 4px solid #1c243f;
  border-top: none;
  border-radius: 0 0 80px 80px;
  background: linear-gradient(180deg, transparent 0, transparent 60%, #f06060 60%);
}

.cheek { position: absolute; top: 104px; width: 22px; height: 12px; background: #ff9b9b55; border-radius: 12px; }
.cheek.left { left: 26px; }
.cheek.right { right: 26px; }

/* Body */
.body { position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 180px; height: 140px; }
.neck { position: absolute; top: -8px; left: 50%; transform: translateX(-50%); width: 28px; height: 18px; background: #ffb79a; border-radius: 0 0 12px 12px; }
.torso { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); width: 180px; height: 120px; border-radius: 24px; background: linear-gradient(135deg, #3b476f, #2a355c); overflow: hidden; border: 1px solid #2a3050; }
.torso .glow { position: absolute; inset: 0; background: radial-gradient(120px 90px at 50% 10%, #7aa7ff22, transparent 70%); }
.hand { position: absolute; bottom: 12px; width: 34px; height: 34px; border-radius: 50%; background: #ffb79a; filter: drop-shadow(0 2px 6px rgba(0,0,0,.2)); }
.hand.left { left: 12px; }
.hand.right { right: 12px; }

/* Mood variants */
/* Ecstatic */
.mood-ecstatic .brow.left { transform: rotate(-18deg) translateY(-6px); width: 40px; }
.mood-ecstatic .brow.right { transform: rotate(18deg) translateY(-6px); width: 40px; }
.mood-ecstatic .mouth { height: 36px; border-radius: 0 0 90px 90px; }
.mood-ecstatic .cheek { background: #ff7a7a77; }
.mood-ecstatic { filter: drop-shadow(0 12px 30px rgba(34,197,94,.35)); }

/* Happy */
.mood-happy .brow.left { transform: rotate(-10deg) translateY(-3px); }
.mood-happy .brow.right { transform: rotate(10deg) translateY(-3px); }
.mood-happy .mouth { height: 30px; }
.mood-happy { filter: drop-shadow(0 10px 26px rgba(96,165,250,.35)); }

/* Neutral */
.mood-neutral .brow { opacity: .9; }
.mood-neutral .mouth { height: 20px; }

/* Worried */
.mood-worried .brow.left { transform: rotate(12deg) translateY(2px); }
.mood-worried .brow.right { transform: rotate(-12deg) translateY(2px); }
.mood-worried .mouth { height: 12px; border-top: 4px solid #1c243f; border-bottom: none; border-radius: 80px 80px 0 0; }
.mood-worried { filter: drop-shadow(0 8px 20px rgba(251,191,36,.25)); }

/* Sad */
.mood-sad .brow.left { transform: rotate(16deg) translateY(4px); }
.mood-sad .brow.right { transform: rotate(-16deg) translateY(4px); }
.mood-sad .mouth { height: 12px; border-top: 4px solid #1c243f; border-bottom: none; border-radius: 100px 100px 0 0; }
.mood-sad .cheek { background: #8aa0ff33; }
.mood-sad { filter: grayscale(.1) drop-shadow(0 6px 18px rgba(59,130,246,.25)); }

/* Despair */
.mood-despair { filter: grayscale(.25) drop-shadow(0 4px 14px rgba(244,63,94,.25)); }
.mood-despair .brow.left { transform: rotate(24deg) translateY(6px); }
.mood-despair .brow.right { transform: rotate(-24deg) translateY(6px); }
.mood-despair .mouth { width: 46px; height: 8px; border-top: 4px solid #1c243f; border-bottom: none; border-radius: 100px; background: transparent; }

.caption { margin-top: 14px; text-align: center; }
.name { font-weight: 700; color: var(--text); }
.subtitle { font-size: 12px; color: var(--muted); }
</style>

