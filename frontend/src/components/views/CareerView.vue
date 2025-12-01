<template>
  <div class="view-container">
    <div class="view-header">
      <h2>职业发展 // CAREER_PATH</h2>
      <div class="header-line"></div>
    </div>

    <div class="content-grid">
      <!-- Left: Current Career -->
      <div class="col-left">
        <div class="archive-card">
          <div class="archive-header">当前职业</div>
          <div class="archive-body">
            <div v-if="currentJob" class="job-display">
              <div class="job-title">{{ currentJob.title }}</div>
              <div class="job-company">{{ currentJob.industry }} · {{ currentJob.level_name }}</div>
              <div class="job-stats">
                <div class="stat">
                  <span class="stat-label">月薪</span>
                  <span class="stat-value salary">¥{{ formatNumber(currentJob.salary) }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">工龄</span>
                  <span class="stat-value">{{ currentJob.months || 0 }}个月</span>
                </div>
                <div class="stat">
                  <span class="stat-label">绩效</span>
                  <span class="stat-value">{{ currentJob.performance || 'B' }}</span>
                </div>
              </div>
              <button class="term-btn danger" @click="resignJob" v-if="currentJob.job_id">
                辞职 RESIGN
              </button>
            </div>
            <div v-else class="empty-state">
              暂无工作，请在下方申请职位
            </div>
          </div>
        </div>

        <!-- Skills -->
        <div class="archive-card flex-grow">
          <div class="archive-header">我的技能</div>
          <div class="archive-body scrollable">
            <div v-if="mySkills.length === 0" class="empty-state">暂无技能</div>
            <div v-for="skill in mySkills" :key="skill.id" class="skill-row">
              <div class="skill-info">
                <span class="skill-icon">{{ skill.icon }}</span>
                <span class="skill-name">{{ skill.name }}</span>
              </div>
              <div class="skill-level">Lv.{{ skill.level }}</div>
            </div>
            
            <div class="section-title" v-if="availableSkills.length > 0">可学习技能</div>
            <div v-for="skill in availableSkills" :key="skill.id" class="skill-row learnable">
              <div class="skill-info">
                <span class="skill-icon">{{ skill.icon }}</span>
                <div>
                  <div class="skill-name">{{ skill.name }}</div>
                  <div class="skill-cost">学费: ¥{{ formatNumber(skill.cost) }}</div>
                </div>
              </div>
              <button class="term-btn small" @click="learnSkill(skill.id)">学习</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Jobs & Side Business -->
      <div class="col-right">
        <!-- Available Jobs -->
        <div class="archive-card">
          <div class="archive-header">
            <span>招聘市场</span>
            <div class="filter-tabs">
              <span v-for="ind in industries" :key="ind.id"
                :class="['tab', { active: currentIndustry === ind.id }]"
                @click="currentIndustry = ind.id">{{ ind.name }}</span>
            </div>
          </div>
          <div class="archive-body scrollable" style="max-height: 200px;">
            <div v-for="job in filteredJobs" :key="job.id" class="job-row">
              <div class="job-info">
                <div class="job-name">{{ job.title }}</div>
                <div class="job-req">要求: {{ job.requirements || '无' }}</div>
              </div>
              <div class="job-salary">
                <div class="salary-range">¥{{ formatNumber(job.base_salary) }}/月</div>
                <button class="term-btn small" @click="applyJob(job.id)" 
                  :disabled="!canApply(job)">申请</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Side Business -->
        <div class="archive-card flex-grow">
          <div class="archive-header">副业收入</div>
          <div class="archive-body scrollable">
            <div v-if="mySideBusiness" class="side-business-active">
              <div class="sb-header">
                <span class="sb-icon">{{ mySideBusiness.icon }}</span>
                <div>
                  <div class="sb-name">{{ mySideBusiness.name }}</div>
                  <div class="sb-income">月收入: ¥{{ formatNumber(mySideBusiness.income) }}</div>
                </div>
              </div>
            </div>
            
            <div class="section-title">可选副业</div>
            <div v-for="sb in sideBusiness" :key="sb.id" class="sb-row">
              <div class="sb-info">
                <span class="sb-icon">{{ sb.icon }}</span>
                <div>
                  <div class="sb-name">{{ sb.name }}</div>
                  <div class="sb-desc">{{ sb.description }}</div>
                  <div class="sb-stats">
                    <span>启动资金: ¥{{ formatNumber(sb.startup_cost) }}</span>
                    <span>预期收入: ¥{{ formatNumber(sb.min_income) }}-{{ formatNumber(sb.max_income) }}/月</span>
                  </div>
                </div>
              </div>
              <button class="term-btn small" @click="startBusiness(sb.id)"
                :disabled="mySideBusiness !== null">开始</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const currentJob = ref(null)
const mySkills = ref([])
const availableSkills = ref([])
const jobs = ref([])
const sideBusiness = ref([])
const mySideBusiness = ref(null)
const currentIndustry = ref('all')

const industries = [
  { id: 'all', name: '全部' },
  { id: '科技', name: '科技' },
  { id: '金融', name: '金融' },
  { id: '制造', name: '制造' },
  { id: '医疗', name: '医疗' },
  { id: '零售', name: '零售' }
]

const filteredJobs = computed(() => {
  if (currentIndustry.value === 'all') return jobs.value
  return jobs.value.filter(j => j.industry === currentIndustry.value)
})

const formatNumber = (n) => Number(n || 0).toLocaleString('zh-CN')

const getSessionId = () => {
  try {
    const char = localStorage.getItem('currentCharacter')
    return char ? JSON.parse(char).id : null
  } catch { return null }
}

const canApply = (job) => {
  // Check if player meets requirements
  return true
}

const loadCareerData = async () => {
  const sessionId = getSessionId()
  
  // Load current career
  if (sessionId) {
    try {
      const res = await fetch(`/api/career/current/${sessionId}`)
      const data = await res.json()
      if (data.success) currentJob.value = data.career
    } catch (e) {
      console.error('加载职业失败:', e)
    }
  }
  
  // Load available jobs
  try {
    const res = await fetch('/api/career/jobs')
    jobs.value = res.ok ? await res.json() : []
  } catch (e) {
    // Fallback data
    jobs.value = [
      { id: 'tech_1', title: '初级程序员', industry: '科技', base_salary: 8000, requirements: '无' },
      { id: 'tech_3', title: '高级程序员', industry: '科技', base_salary: 20000, requirements: '编程Lv2' },
      { id: 'finance_1', title: '银行柜员', industry: '金融', base_salary: 6000, requirements: '无' },
      { id: 'finance_3', title: '投资分析师', industry: '金融', base_salary: 25000, requirements: '投资Lv2' }
    ]
  }
  
  // Load skills
  try {
    const res = await fetch('/api/career/skills')
    const allSkills = res.ok ? await res.json() : []
    availableSkills.value = allSkills
  } catch (e) {
    availableSkills.value = [
      { id: 'programming', name: '编程', icon: '💻', cost: 5000 },
      { id: 'investing', name: '投资', icon: '📈', cost: 8000 },
      { id: 'management', name: '管理', icon: '👔', cost: 10000 },
      { id: 'marketing', name: '营销', icon: '📣', cost: 6000 }
    ]
  }
  
  // Load side businesses
  try {
    const res = await fetch('/api/career/side-businesses')
    sideBusiness.value = res.ok ? await res.json() : []
  } catch (e) {
    sideBusiness.value = [
      { id: 'content', name: '自媒体', icon: '📱', description: '运营短视频账号', startup_cost: 2000, min_income: 500, max_income: 5000 },
      { id: 'freelance', name: '接单设计', icon: '🎨', description: '接平面设计单', startup_cost: 5000, min_income: 2000, max_income: 8000 },
      { id: 'tutor', name: '家教', icon: '📚', description: '辅导学生功课', startup_cost: 0, min_income: 1000, max_income: 4000 }
    ]
  }
}

const applyJob = async (jobId) => {
  const sessionId = getSessionId()
  if (!sessionId) return alert('请先选择角色')
  
  try {
    const res = await fetch('/api/career/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, job_id: jobId })
    })
    const data = await res.json()
    if (data.success) {
      alert('申请成功！')
      loadCareerData()
    } else {
      alert(data.message || '申请失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const resignJob = async () => {
  if (!confirm('确定要辞职吗？')) return
  const sessionId = getSessionId()
  try {
    const res = await fetch('/api/career/resign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    })
    const data = await res.json()
    if (data.success) {
      currentJob.value = null
      loadCareerData()
    }
  } catch (e) {
    console.error(e)
  }
}

const learnSkill = async (skillId) => {
  const sessionId = getSessionId()
  if (!sessionId) return alert('请先选择角色')
  
  try {
    const res = await fetch('/api/career/learn-skill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, skill_id: skillId })
    })
    const data = await res.json()
    alert(data.message || (data.success ? '学习成功！' : '学习失败'))
    if (data.success) loadCareerData()
  } catch (e) {
    console.error(e)
  }
}

const startBusiness = async (businessId) => {
  const sessionId = getSessionId()
  if (!sessionId) return alert('请先选择角色')
  
  try {
    const res = await fetch('/api/career/start-side-business', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, business_id: businessId })
    })
    const data = await res.json()
    alert(data.message || (data.success ? '开始副业！' : '启动失败'))
    if (data.success) loadCareerData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadCareerData()
})
</script>

<style scoped>
.view-container {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.view-header h2 { font-size: 24px; font-weight: 900; margin: 0 0 8px 0; }
.header-line { height: 2px; background: var(--term-border); margin-bottom: 24px; }

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.col-left, .col-right {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.flex-grow { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.scrollable { flex: 1; overflow-y: auto; }

/* Archive Card */
.archive-card { background: var(--term-panel-bg); border: 2px solid var(--term-border); }
.archive-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background: rgba(0,0,0,0.03);
  border-bottom: 1px solid var(--term-border);
  font-weight: 700; font-size: 12px; text-transform: uppercase;
}
.archive-body { padding: 16px; }

/* Filter Tabs */
.filter-tabs { display: flex; gap: 4px; }
.tab { font-size: 10px; padding: 2px 6px; cursor: pointer; border: 1px solid var(--term-border); }
.tab.active { background: var(--term-accent); color: #000; border-color: var(--term-accent); }

/* Job Display */
.job-display { text-align: center; }
.job-title { font-size: 24px; font-weight: 900; margin-bottom: 4px; }
.job-company { font-size: 12px; color: var(--term-text-secondary); margin-bottom: 16px; }
.job-stats { display: flex; justify-content: center; gap: 24px; margin-bottom: 16px; }
.stat { text-align: center; }
.stat-label { display: block; font-size: 10px; color: var(--term-text-secondary); }
.stat-value { font-size: 18px; font-weight: 700; }
.stat-value.salary { color: var(--term-success); }

/* Skill Row */
.skill-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; border: 1px solid var(--term-border); margin-bottom: 8px;
}
.skill-row.learnable { background: rgba(0,0,0,0.02); }
.skill-info { display: flex; align-items: center; gap: 10px; }
.skill-icon { font-size: 20px; }
.skill-name { font-weight: 700; }
.skill-cost { font-size: 11px; color: var(--term-accent); }
.skill-level { font-weight: 700; color: var(--term-accent); }

/* Job Row */
.job-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; border: 1px solid var(--term-border); margin-bottom: 8px;
}
.job-name { font-weight: 700; }
.job-req { font-size: 11px; color: var(--term-text-secondary); }
.salary-range { font-weight: 700; color: var(--term-success); margin-bottom: 4px; text-align: right; }

/* Side Business */
.side-business-active {
  padding: 16px; background: rgba(16, 185, 129, 0.1);
  border: 2px solid var(--term-success); margin-bottom: 16px;
}
.sb-header { display: flex; align-items: center; gap: 12px; }
.sb-icon { font-size: 32px; }
.sb-name { font-weight: 700; font-size: 16px; }
.sb-income { color: var(--term-success); font-weight: 700; }

.sb-row {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 12px; border: 1px solid var(--term-border); margin-bottom: 8px;
}
.sb-info { display: flex; gap: 10px; flex: 1; }
.sb-desc { font-size: 11px; color: var(--term-text-secondary); }
.sb-stats { font-size: 10px; color: var(--term-accent); display: flex; gap: 12px; margin-top: 4px; }

.section-title {
  font-size: 11px; font-weight: 700; color: var(--term-text-secondary);
  margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 1px dashed var(--term-border);
}

/* Buttons */
.term-btn { padding: 8px 16px; font-weight: 700; border: 2px solid #000; cursor: pointer; }
.term-btn.small { padding: 4px 12px; font-size: 11px; }
.term-btn.danger { background: #ef4444; color: #fff; }
.term-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.empty-state { text-align: center; padding: 40px 20px; color: var(--term-text-secondary); }

@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; }
}
</style>
