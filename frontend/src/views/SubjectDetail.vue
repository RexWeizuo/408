<template>
  <div class="fade-in">
    <div class="card mb-8">
      <div class="flex items-center gap-4">
        <span class="text-5xl">{{ getSubjectIcon(subjectId) }}</span>
        <div>
          <h1 class="text-3xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">{{ subjectName }}</h1>
          <p class="text-base mt-1 font-medium">共 {{ chapters.length }} 个章节</p>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <router-link v-for="(chapter, index) in chapters" :key="chapter.id" :to="`/subjects/${subjectId}/chapters/${chapter.id}`" class="card group block hover:bg-bauhaus-gray-100">
        <div class="flex items-center">
          <div class="w-16 h-16 bg-bauhaus-red border-4 border-black flex items-center justify-center text-white font-black text-xl mr-6 flex-shrink-0"
               style="font-family: 'Poppins', sans-serif; box-shadow: 3px 3px 0px #000000;">
            {{ index + 1 }}
          </div>

          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-black uppercase truncate" style="font-family: 'Poppins', sans-serif;">{{ chapter.name }}</h3>
            <p class="text-sm mt-1">{{ chapter.knowledge_point_count || '多个' }} 个知识点</p>
          </div>

          <div class="ml-6 flex items-center gap-4">
            <div class="w-36">
              <div class="progress-bar">
                <div class="progress-bar-fill" :style="{ width: (chapter.progress || 0) + '%' }"></div>
              </div>
              <p class="text-xs font-black mt-1.5 text-right">{{ chapter.progress || 0 }}%</p>
            </div>
            <svg class="w-7 h-7 group-hover:translate-x-1.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"></path>
            </svg>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const subjectId = route.params.subjectId
const chapters = ref([])
const subjectName = ref('')

const names = { data_structure: '数据结构', computer_organization: '计算机组成原理', operating_system: '操作系统', computer_network: '计算机网络' }
const icons = { data_structure: '🌳', computer_organization: '🔧', operating_system: '💻', computer_network: '🌐' }
const getSubjectIcon = (id) => icons[id] || '📘'

onMounted(async () => {
  subjectName.value = names[subjectId] || subjectId
  try { const r = await axios.get('/api/subjects'); const s = r.data.subjects.find(s => s.id === subjectId); if (s) chapters.value = s.chapters } catch (e) { console.error(e) }
})
</script>
