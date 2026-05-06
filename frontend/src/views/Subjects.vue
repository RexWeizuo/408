<template>
  <div class="fade-in">
    <div class="mb-10">
      <h1 class="bauhaus-title">选择考纲 📚</h1>
      <p class="bauhaus-subtitle mt-3">408四门专业课，全面覆盖助你成功</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <router-link v-for="subject in subjects" :key="subject.id" :to="`/subjects/${subject.id}`" class="card group cursor-pointer">
        <div class="flex items-start justify-between mb-8">
          <span class="text-6xl">{{ getSubjectIcon(subject.id) }}</span>
          <span class="badge badge-yellow">{{ subject.score }}分</span>
        </div>

        <h3 class="text-2xl font-black uppercase mb-3" style="font-family: 'Poppins', sans-serif;">{{ subject.name }}</h3>
        <p class="text-base font-medium mb-6">共 {{ subject.chapters.length }} 个章节</p>

        <div class="flex items-center text-sm font-black uppercase tracking-wider" style="font-family: 'Poppins', sans-serif;">
          <span>开始学习</span>
          <svg class="w-5 h-5 ml-2 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
          </svg>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const subjects = ref([])
const subjectIcons = { data_structure: '🌳', computer_organization: '🔧', operating_system: '💻', computer_network: '🌐' }
const getSubjectIcon = (id) => subjectIcons[id] || '📘'

onMounted(async () => {
  try { const r = await axios.get('/api/subjects'); subjects.value = r.data.subjects } catch (e) { console.error(e) }
})
</script>
