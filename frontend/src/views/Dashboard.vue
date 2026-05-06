<template>
  <div class="fade-in space-y-8">
    <div class="mb-10">
      <h1 class="bauhaus-title">欢迎回来 👋</h1>
      <p class="bauhaus-subtitle mt-3">今天也是充满希望的一天，继续你的408学习之旅吧！</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="card group cursor-pointer">
        <div class="flex items-center justify-between mb-6">
          <div class="bauhaus-shape-square text-3xl">📖</div>
          <span class="badge badge-yellow">今日</span>
        </div>
        <p class="text-sm font-bold uppercase tracking-wider mb-2" style="font-family: 'Poppins', sans-serif;">新学知识点</p>
        <p class="stat-number">{{ dashboard.today_new_count }}</p>
      </div>

      <div class="card group cursor-pointer">
        <div class="flex items-center justify-between mb-6">
          <div class="bauhaus-shape-circle text-3xl">🔄</div>
          <span class="badge badge-blue">复习</span>
        </div>
        <p class="text-sm font-bold uppercase tracking-wider mb-2" style="font-family: 'Poppins', sans-serif;">今日复习</p>
        <p class="stat-number">{{ dashboard.today_review_count }}</p>
      </div>

      <div class="card group cursor-pointer">
        <div class="flex items-center justify-between mb-6">
          <div style="width: 80px; height: 80px; background-color: #FFD700; border: 4px solid #000000; display: inline-flex; align-items: center; justify-content: center; font-size: 32px;" class="text-3xl">✍️</div>
          <span class="badge badge-red">练习</span>
        </div>
        <p class="text-sm font-bold uppercase tracking-wider mb-2" style="font-family: 'Poppins', sans-serif;">今日练习</p>
        <p class="stat-number">{{ dashboard.today_question_count }}</p>
      </div>

      <div class="card group cursor-pointer">
        <div class="flex items-center justify-between mb-6">
          <div class="bauhaus-shape-square bg-bauhaus-yellow text-3xl">🎯</div>
          <span class="badge badge-black">进度</span>
        </div>
        <p class="text-sm font-bold uppercase tracking-wider mb-2" style="font-family: 'Poppins', sans-serif;">完成进度</p>
        <p class="stat-number">{{ dashboard.today_completed_percentage.toFixed(0) }}%</p>
        <div class="progress-bar mt-4">
          <div class="progress-bar-fill" :style="{ width: dashboard.today_completed_percentage + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="card">
        <div class="flex items-center justify-between mb-6 pb-4 border-b-4 border-black">
          <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">待复习提醒</h3>
          <span class="badge badge-red">{{ dashboard.urgent_reviews.length }} 项</span>
        </div>

        <div v-if="dashboard.urgent_reviews.length === 0" class="text-center py-12">
          <p class="text-lg font-bold">暂无紧急复习任务</p>
        </div>

        <div v-else class="space-y-4 max-h-80 overflow-y-auto pr-2">
          <div v-for="review in dashboard.urgent_reviews" :key="review.record_id"
               class="p-5 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-bold text-base">{{ review.knowledge_point_name }}</p>
                <p class="text-sm mt-1">已复习 {{ review.review_count }} 次</p>
              </div>
              <span :class="['badge', getMasteryBadge(review.mastery_level)]">
                {{ (review.mastery_level * 100).toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center justify-between mb-6 pb-4 border-b-4 border-black">
          <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">薄弱知识点</h3>
          <span class="badge badge-red">{{ dashboard.weak_points.length }} 项</span>
        </div>

        <div v-if="dashboard.weak_points.length === 0" class="text-center py-12">
          <p class="text-lg font-bold">暂无薄弱知识点，继续保持！</p>
        </div>

        <div v-else class="space-y-4 max-h-80 overflow-y-auto pr-2">
          <router-link v-for="point in dashboard.weak_points" :key="point.knowledge_point_id"
                       :to="`/knowledge/${point.knowledge_point_id}`"
                       class="block p-5 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
            <div class="flex justify-between items-center">
              <span class="font-bold">{{ point.name }}</span>
              <span class="badge badge-red">{{ (point.mastery_level * 100).toFixed(0) }}%</span>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="bauhaus-section-title mb-8">科目进度</div>

      <div class="space-y-6">
        <div v-for="subject in dashboard.subject_progress" :key="subject.subject_id" class="p-6 border-4 border-black">
          <div class="flex justify-between items-center mb-4">
            <div class="flex items-center gap-4">
              <span class="text-3xl">{{ getSubjectIcon(subject.subject_id) }}</span>
              <h4 class="text-lg font-black uppercase" style="font-family: 'Poppins', sans-serif;">{{ getSubjectName(subject.subject_id) }}</h4>
            </div>
            <span class="text-sm font-black">{{ getSubjectCompletion(subject).toFixed(0) }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar-fill" :style="{ width: getSubjectCompletion(subject) + '%' }"></div>
          </div>
          <p class="text-sm mt-3 font-bold">平均正确率: {{ getSubjectAvgCorrectRate(subject).toFixed(1) }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const dashboard = ref({
  today_new_count: 0, today_review_count: 0, today_question_count: 0,
  today_completed_percentage: 0, subject_progress: [], urgent_reviews: [], weak_points: []
})

const subjectNames = { data_structure: '数据结构', computer_organization: '计算机组成原理', operating_system: '操作系统', computer_network: '计算机网络' }
const subjectIcons = { data_structure: '🌳', computer_organization: '🔧', operating_system: '💻', computer_network: '🌐' }
const getSubjectName = (id) => subjectNames[id] || id
const getSubjectIcon = (id) => subjectIcons[id] || '📘'
const getMasteryBadge = (m) => m >= 0.9 ? 'badge-blue' : m >= 0.7 ? 'badge-yellow' : m >= 0.5 ? 'badge-yellow' : 'badge-red'
const getSubjectCompletion = (s) => !s.chapters?.length ? 0 : s.chapters.reduce((a, c) => a + c.completion_percentage, 0) / s.chapters.length
const getSubjectAvgCorrectRate = (s) => !s.chapters?.length ? 0 : s.chapters.reduce((a, c) => a + c.average_correct_rate, 0) / s.chapters.length

onMounted(async () => {
  try { const r = await axios.get('/api/study/dashboard'); dashboard.value = r.data } catch (e) { console.error(e) }
})
</script>
