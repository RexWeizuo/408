<template>
  <div class="fade-in">
    <div class="mb-10">
      <h1 class="bauhaus-title">LION层级大纲 🦁</h1>
      <p class="bauhaus-subtitle mt-3">四级知识体系，层层递进，全面掌握408核心内容</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <router-link v-for="subject in subjects" :key="subject.id" :to="`/lion/${subject.id}`" class="card group cursor-pointer">
        <div class="flex items-start justify-between mb-8">
          <span class="text-6xl">{{ getLionIcon(subject.id) }}</span>
          <span class="badge badge-yellow font-bold">{{ subject.children?.length || 0 }} 章</span>
        </div>

        <h3 class="text-2xl font-black uppercase mb-3" style="font-family: 'Poppins', sans-serif;">{{ subject.name }}</h3>
        <p class="text-base font-medium mb-6">四级知识结构，精细化复习</p>

        <div class="flex items-center text-sm font-black uppercase tracking-wider" style="font-family: 'Poppins', sans-serif;">
          <span>查看详情</span>
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
const lionIcons = { operating_system: '💻', computer_organization: '🔧', data_structure: '🌳', computer_network: '🌐' }
const getLionIcon = (id) => lionIcons[id] || '📘'

onMounted(async () => {
  try { const r = await axios.get('/api/lion/subjects'); subjects.value = r.data.subjects } catch (e) { console.error(e) }
})
</script>
