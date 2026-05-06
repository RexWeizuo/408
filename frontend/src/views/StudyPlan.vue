<template>
  <div class="fade-in space-y-8">
    <div class="mb-10">
      <h1 class="bauhaus-title">学习规划 📅</h1>
      <p class="bauhaus-subtitle mt-3">科学规划，高效备考，距离成功更进一步</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card text-center group cursor-pointer hover:bg-bauhaus-gray-100">
        <div class="bauhaus-shape-square mx-auto mb-6 text-4xl">⏰</div>
        <p class="text-sm font-bold uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">距离考试还有</p>
        <p class="stat-number">{{ daysToExam }}</p>
        <p class="text-base mt-2 font-black">天</p>
      </div>

      <div class="card text-center group cursor-pointer hover:bg-bauhaus-gray-100">
        <div class="bauhaus-circle mx-auto mb-6 bg-bauhaus-yellow text-4xl">📚</div>
        <p class="text-sm font-bold uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">本周学习天数</p>
        <p class="stat-number">{{ weeklyStats.study_days || 0 }}</p>
        <p class="text-base mt-2 font-black">天</p>
      </div>

      <div class="card text-center group cursor-pointer hover:bg-bauhaus-gray-100">
        <div class="bauhaus-shape-triangle mx-auto mb-6"></div>
        <p class="text-sm font-bold uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">本周正确率</p>
        <p class="stat-number">{{ weeklyStats.average_correct_rate?.toFixed(1) || 0 }}%</p>
      </div>
    </div>

    <div class="card">
      <div class="bauhaus-section-title mb-8">本周学习统计</div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div class="p-6 border-4 border-black text-center">
          <p class="text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">学习天数</p>
          <p class="text-5xl font-black">{{ weeklyStats.study_days || 0 }}</p>
        </div>

        <div class="p-6 border-4 border-black text-center">
          <p class="text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">学习时长</p>
          <p class="text-5xl font-black">{{ ((weeklyStats.total_time_spent || 0) / 60).toFixed(0) }}</p>
        </div>

        <div class="p-6 border-4 border-black text-center">
          <p class="text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">新学知识点</p>
          <p class="text-5xl font-black">{{ weeklyStats.new_knowledge_points || 0 }}</p>
        </div>

        <div class="p-6 border-4 border-black text-center">
          <p class="text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">复习知识点</p>
          <p class="text-5xl font-black">{{ weeklyStats.reviewed_knowledge_points || 0 }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center justify-between mb-8 pb-4 border-b-4 border-black">
        <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">遗忘曲线复习提醒</h3>
        <span v-if="todayReviews.length > 0" class="badge badge-red font-bold">{{ todayReviews.length }} 项待复习</span>
      </div>

      <div v-if="todayReviews.length === 0" class="text-center py-12">
        <p class="text-lg font-bold">今天没有需要复习的内容</p>
        <p class="text-base mt-2">继续保持，学习状态很好！</p>
      </div>

      <div v-else class="space-y-5 max-h-96 overflow-y-auto pr-2">
        <div v-for="review in todayReviews" :key="review.record_id"
             class="p-6 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
          <div class="flex justify-between items-center">
            <div class="flex-1">
              <p class="text-lg font-black uppercase mb-2" style="font-family: 'Poppins', sans-serif;">
                {{ review.knowledge_point_name }}
              </p>
              <p class="text-base font-medium">已复习 {{ review.review_count }} 次</p>
            </div>
            <div class="flex items-center gap-6">
              <div class="text-right">
                <p class="text-xs font-black uppercase mb-1" style="font-family: 'Poppins', sans-serif;">掌握度</p>
                <p class="text-2xl font-black">{{ (review.mastery_level * 100).toFixed(0) }}%</p>
              </div>
              <router-link :to="`/knowledge/${review.knowledge_point_id}`" class="btn btn-primary px-6 py-3 font-black uppercase">
                去复习
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="bauhaus-section-title mb-8">薄弱知识点（需要加强）</div>

      <div v-if="weeklyStats.weak_points?.length > 0" class="space-y-4">
        <div v-for="wpId in weeklyStats.weak_points" :key="wpId" class="p-4 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
          <router-link :to="`/knowledge/${wpId}`" class="flex items-center justify-between">
            <span class="text-lg font-black uppercase" style="font-family: 'Poppins', sans-serif;">{{ getKnowledgePointName(wpId) }}</span>
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"></path>
            </svg>
          </router-link>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <p class="text-lg font-bold mb-2">暂无薄弱知识点</p>
        <p class="text-base">继续保持，你的学习状态很棒！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const examDate = new Date('2026-12-19')
const daysToExam = ref(Math.ceil((examDate - new Date()) / (1000 * 60 * 60 * 24)))
const weeklyStats = ref({})
const todayReviews = ref([])
const knowledgePoints = ref({})

const getUrgencyClass = (u) => u === 'overdue' ? 'bg-bauhaus-red' : u === 'due_today' ? 'bg-bauhaus-yellow' : 'bg-bauhaus-blue'
const getMasteryColor = (m) => m >= 0.9 ? '' : m >= 0.7 ? '' : m >= 0.5 ? '' : ''
const getKnowledgePointName = (id) => knowledgePoints.value[id] || id

onMounted(async () => {
  try {
    const [w, r, k] = await Promise.all([
      axios.get('/api/study/weekly-stats'),
      axios.get('/api/study/today-reviews'),
      axios.get('/api/knowledge-points/')
    ])
    weeklyStats.value = w.data
    todayReviews.value = r.data
    k.data.forEach(kp => { knowledgePoints.value[kp.id] = kp.name })
  } catch (e) { console.error(e) }
})
</script>
