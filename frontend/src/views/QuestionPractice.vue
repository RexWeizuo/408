<template>
  <div class="max-w-5xl mx-auto fade-in space-y-8">
    <div v-if="loading" class="card text-center py-16">
      <p class="text-lg font-bold">题目加载中...</p>
    </div>

    <div v-else-if="question" class="space-y-8">
      <div class="card">
        <div class="flex items-center gap-3 mb-6 pb-4 border-b-4 border-black">
          <span class="badge badge-yellow font-bold">难度 {{ question.difficulty }}</span>
          <span class="badge badge-blue font-bold">选择题</span>
        </div>

        <h2 class="text-2xl font-black leading-relaxed mb-8 uppercase" style="font-family: 'Poppins', sans-serif;">
          {{ question.question }}
        </h2>

        <div class="space-y-4 mb-8">
          <div v-for="option in question.options" :key="option"
               @click="selectAnswer(option[0])"
               :class="['option-card', { 'selected': selectedAnswer === option[0] }]">
            <div class="w-12 h-12 border-4 border-black flex items-center justify-center font-black text-lg flex-shrink-0"
                 :class="selectedAnswer === option[0] ? 'bg-bauhaus-yellow' : 'bg-white'"
                 style="box-shadow: 3px 3px 0px #000000;">
              {{ option[0] }}
            </div>
            <span :class="['text-base font-medium', selectedAnswer === option[0] ? 'font-black' : '']">
              {{ option.substring(2) }}
            </span>
          </div>
        </div>

        <div class="mb-8">
          <label class="block text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">
            详细解题过程（选填）
          </label>
          <textarea v-model="userProcess" placeholder="写下你的详细解题过程..." class="input resize-none" rows="4"></textarea>
        </div>

        <button @click="submitAnswer"
                :disabled="!selectedAnswer || submitted"
                :class="['btn w-full py-4 text-base font-black uppercase tracking-wider', submitted ? (isCorrect ? 'bg-bauhaus-blue text-white' : 'bg-bauhaus-gray-300') : 'btn-primary', 'disabled:opacity-50 disabled:cursor-not-allowed']"
                style="font-family: 'Poppins', sans-serif;">
          <span v-if="submitted && isCorrect">✅ 回答正确！</span>
          <span v-else-if="submitted && !isCorrect">❌ 已提交答案</span>
          <span v-else>提交答案</span>
        </button>
      </div>

      <div v-if="showResult" class="card fade-in">
        <div class="text-center mb-8">
          <div :class="['w-28 h-28 mx-auto flex items-center justify-center text-6xl mb-4 border-4 border-black',
            isCorrect ? 'bg-bauhaus-blue' : 'bg-bauhaus-red']"
               style="box-shadow: 4px 4px 0px #000000;">
            {{ isCorrect ? '🎉' : '💪' }}
          </div>
          <h3 :class="['text-3xl font-black uppercase', isCorrect ? '' : '']" style="font-family: 'Poppins', sans-serif;">
            {{ isCorrect ? '太棒了，回答正确！' : '回答错误，继续加油！' }}
          </h3>
        </div>

        <div class="p-6 bg-bauhaus-gray-100 border-4 border-black mb-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="text-2xl">✅</span>
            <p class="text-lg font-black uppercase" style="font-family: 'Poppins', sans-serif;">正确答案: <span>{{ question.answer }}</span></p>
          </div>

          <div v-if="!isCorrect" class="p-4 bg-bauhaus-red text-white border-4 border-black mb-4">
            <p class="font-bold">你的答案: <span class="font-black">{{ selectedAnswer }}</span></p>
          </div>

          <div class="mt-6">
            <p class="font-black text-base mb-3 uppercase tracking-wide" style="font-family: 'Poppins', sans-serif;">
              💡 详细解析:
            </p>
            <p class="leading-relaxed text-base">{{ question.explanation }}</p>
          </div>
        </div>

        <div class="flex gap-4">
          <router-link :to="`/knowledge/${question.knowledge_point_id}`" class="btn btn-primary flex-1 py-3 font-black uppercase">
            📖 查看相关知识点
          </router-link>
          <router-link to="/questions" class="btn btn-secondary flex-1 py-3 font-black uppercase">
            🔙 返回题目列表
          </router-link>
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
const questionId = route.params.questionId
const question = ref(null)
const selectedAnswer = ref('')
const userProcess = ref('')
const showResult = ref(false)
const isCorrect = ref(false)
const loading = ref(true)
const submitted = ref(false)

const selectAnswer = (o) => {
  if (!submitted.value) selectedAnswer.value = o
}

const submitAnswer = async () => {
  if (!selectedAnswer.value || submitted.value) return
  try {
    const r = await axios.post('/api/answers/', { question_id: parseInt(questionId), user_answer: selectedAnswer.value, user_process: userProcess.value })
    isCorrect.value = r.data.is_correct
    showResult.value = true
    submitted.value = true
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  try {
    const r = await axios.get(`/api/questions/${questionId}`)
    question.value = r.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>
