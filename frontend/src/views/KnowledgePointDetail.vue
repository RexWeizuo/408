<template>
  <div class="max-w-5xl mx-auto fade-in space-y-8">
    <div class="card">
      <div class="flex items-center gap-4 mb-8">
        <div class="bauhaus-shape-square text-3xl">📖</div>
        <div>
          <h2 class="text-2xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">知识点详情</h2>
          <p class="text-base mt-1 font-medium">学习和掌握这个知识点</p>
        </div>
      </div>

      <h3 class="text-xl font-black uppercase mb-6 pb-4 border-b-4 border-black" style="font-family: 'Poppins', sans-serif;">
        {{ knowledgePoint.name }}
      </h3>

      <div v-if="knowledgePoint.content" class="p-6 bg-white border-4 border-black">
        <div v-html="renderMarkdown(knowledgePoint.content)"></div>
      </div>

      <div v-else class="text-center py-16 bg-bauhaus-gray-100 border-4 border-black">
        <p class="text-6xl mb-4">📝</p>
        <p class="text-lg font-bold mb-2">暂无内容</p>
        <p class="text-base">请先录入知识点内容</p>
      </div>
    </div>

    <!-- 知识点习题 -->
    <div class="card">
      <div class="flex items-center justify-between mb-6 pb-4 border-b-4 border-black">
        <div class="flex items-center gap-3">
          <span class="text-2xl">📖</span>
          <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">知识点习题</h3>
        </div>
        <span class="badge badge-red">{{ knowledgeQuestions.length }} 题</span>
      </div>

      <div v-if="knowledgeQuestions.length === 0" class="text-center py-10">
        <p class="text-lg font-bold">暂无知识点习题</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="q in knowledgeQuestions" :key="q.id" class="p-5 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
          <div class="flex items-start justify-between">
            <p class="font-bold flex-1 pr-4">{{ q.question }}</p>
            <router-link :to="`/questions/practice/${q.id}`" class="btn btn-primary text-xs px-4 py-2 flex-shrink-0">答题</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 选择题 -->
    <div class="card">
      <div class="flex items-center justify-between mb-6 pb-4 border-b-4 border-black">
        <div class="flex items-center gap-3">
          <span class="text-2xl">☑️</span>
          <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">选择题</h3>
        </div>
        <span class="badge badge-blue">{{ choiceQuestions.length }} 题</span>
      </div>

      <div v-if="choiceQuestions.length === 0" class="text-center py-10">
        <p class="text-lg font-bold">暂无选择题</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="q in choiceQuestions" :key="q.id" class="p-5 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
          <div class="flex items-start justify-between">
            <div class="flex-1 pr-4">
              <p class="font-bold mb-3">{{ q.question }}</p>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="opt in q.options" :key="opt" class="px-4 py-2 bg-bauhaus-gray-100 border-3 border-black text-sm font-medium">{{ opt }}</div>
              </div>
            </div>
            <router-link :to="`/questions/practice/${q.id}`" class="btn btn-primary text-xs px-4 py-2 flex-shrink-0 ml-4">答题</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'

const route = useRoute()
const kpId = route.params.kpId
const knowledgePoint = ref({})
const questions = ref([])

const knowledgeQuestions = computed(() => questions.value.filter(q => q.type === 'knowledge'))
const choiceQuestions = computed(() => questions.value.filter(q => q.type === 'choice'))
const renderMarkdown = (c) => marked(c)

onMounted(async () => {
  try {
    const kp = await axios.get(`/api/knowledge-points/${kpId}`)
    knowledgePoint.value = kp.data
    const q = await axios.get(`/api/questions/?knowledge_point_id=${kpId}`)
    questions.value = q.data
  } catch (e) { console.error(e) }
})
</script>
