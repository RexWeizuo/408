<template>
  <div class="fade-in">
    <div class="card mb-8">
      <h1 class="bauhaus-title mb-2">知识点列表</h1>
      <p class="bauhaus-subtitle">共 {{ knowledgePoints.length }} 个知识点</p>
    </div>

    <div class="grid gap-6">
      <div v-for="(kp, index) in knowledgePoints" :key="kp.id" class="card hover:bg-bauhaus-gray-100">
        <div class="flex items-start justify-between">
          <div class="flex items-start gap-5 flex-1">
            <div class="w-14 h-14 bg-bauhaus-blue border-4 border-black flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                 style="font-family: 'Poppins', sans-serif; box-shadow: 3px 3px 0px #000000;">
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <router-link :to="`/knowledge/${kp.id}`" class="text-xl font-black uppercase block truncate hover:text-bauhaus-blue" style="font-family: 'Poppins', sans-serif;">
                {{ kp.name }}
              </router-link>
              <p class="text-sm mt-2 line-clamp-2">{{ kp.content || '暂无内容，请先录入知识点内容' }}</p>
            </div>
          </div>

          <div class="flex gap-3 ml-6 flex-shrink-0">
            <router-link :to="`/questions?type=knowledge&kp=${kp.id}`" class="btn btn-primary text-xs px-4 py-2">
              知识点习题
            </router-link>
            <router-link :to="`/questions?type=choice&kp=${kp.id}`" class="btn btn-secondary text-xs px-4 py-2">
              选择题
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const chapterId = route.params.chapterId
const knowledgePoints = ref([])

onMounted(async () => {
  try { const r = await axios.get(`/api/knowledge-points/by-chapter/${chapterId}`); knowledgePoints.value = r.data } catch (e) { console.error(e) }
})
</script>
