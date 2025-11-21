<template>
  <div class="view-container">
    <div class="view-header">
      <h2>世界构建 // WORLD_BUILD</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Macro Indicators -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">宏观经济指标</div>
          <div class="archive-body">
            <div class="macro-grid">
              <div class="macro-item">
                <div class="label">市场指数</div>
                <div class="value">{{ indicators.market_idx?.toLocaleString() || '---' }}</div>
                <div class="trend" :class="indicators.market_trend === 'up' ? 'up' : 'down'">
                  {{ indicators.market_trend === 'up' ? '▲' : '▼' }} 趋势
                </div>
              </div>
              <div class="macro-item">
                <div class="label">通货膨胀率</div>
                <div class="value">{{ indicators.inflation }}%</div>
              </div>
              <div class="macro-item">
                <div class="label">基准利率</div>
                <div class="value">{{ indicators.interest }}%</div>
              </div>
            </div>
          </div>
        </div>

        <div class="archive-card flex-grow">
          <div class="archive-header">区域概览</div>
          <div class="archive-body district-list scrollable">
            <div 
              v-for="district in districts" 
              :key="district.id" 
              class="district-item"
              @click="selectDistrict(district)">
              <div class="d-icon">{{ district.icon }}</div>
              <div class="d-info">
                <div class="d-name">{{ district.name }}</div>
                <div class="d-tag">{{ district.tagline }}</div>
              </div>
              <div class="d-status">
                <span class="status-dot"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Map Placeholder / Details -->
      <div class="col-right">
        <div class="archive-card full-height">
          <div class="archive-header">区域详情</div>
          <div class="archive-body map-container">
            <div class="map-placeholder">
              <div class="grid-overlay"></div>
              <div class="center-text">
                <h3>{{ selectedDistrict?.name || '选择区域查看详情' }}</h3>
                <p>{{ selectedDistrict?.tagline }}</p>
                <div v-if="selectedDistrict" class="district-actions">
                  <button class="term-btn primary" :disabled="gameStore.isLoadingDistrict" @click="enterDistrict">
                    {{ gameStore.isLoadingDistrict ? '进入中...' : '进入区域' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGameStore } from '../../stores/game'
import { useRouter } from 'vue-router'

const gameStore = useGameStore()
const router = useRouter()

const indicators = computed(() => gameStore.macroIndicators || {})
const districts = computed(() => gameStore.districts)
const selectedDistrict = ref(null)

const selectDistrict = (d) => {
  selectedDistrict.value = d
}

const enterDistrict = () => {
  if (selectedDistrict.value) {
    gameStore.exploreDistrict(selectedDistrict.value.id)
  }
}

onMounted(() => {
  gameStore.loadMacroIndicators()
})
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
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
  flex-shrink: 0;
}

.content-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow: hidden;
  min-height: 0;
}

.full-height {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.flex-grow {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.scrollable {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* Macro Grid */
.macro-grid {
  display: grid;
  gap: 16px;
}

.macro-item {
  border: 1px solid var(--term-border);
  padding: 12px;
  background: rgba(0,0,0,0.02);
}

.macro-item .label {
  font-size: 10px;
  color: var(--term-text-secondary);
  margin-bottom: 4px;
}

.macro-item .value {
  font-size: 20px;
  font-weight: 900;
}

.trend {
  font-size: 10px;
  font-weight: bold;
}
.trend.up { color: var(--term-success); }
.trend.down { color: #F44336; }

/* District List */
.district-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.district-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.district-item:hover {
  background: rgba(0,0,0,0.05);
  border-color: var(--term-border);
}

.d-icon { font-size: 20px; }

.d-info { flex: 1; }

.d-name { font-weight: 800; font-size: 12px; }
.d-tag { font-size: 10px; color: var(--term-text-secondary); }

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--term-success);
  border-radius: 50%;
}

/* Map Placeholder */
.map-container {
  flex: 1;
  background: #000;
  position: relative;
  overflow: hidden;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-image: 
    linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 40px 40px;
}

.center-text {
  text-align: center;
  background: var(--term-panel-bg);
  padding: 24px;
  border: 2px solid var(--term-accent);
  color: var(--term-text);
}

.center-text h3 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.district-actions {
  margin-top: 16px;
}
</style>
