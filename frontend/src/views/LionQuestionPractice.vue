<template>
  <div class="max-w-5xl mx-auto fade-in space-y-8" :key="questionId">
    <div v-if="loading" class="card text-center py-16">
      <p class="text-lg font-bold">题目加载中...</p>
    </div>

    <div v-else-if="question" class="space-y-8">
      <div class="card">
        <div class="flex items-center gap-3 mb-6 pb-4 border-b-4 border-black">
          <span class="badge badge-yellow font-bold">问答题</span>
          <span class="badge badge-blue font-bold">{{ sectionName }}</span>
          <span class="ml-auto text-sm font-bold text-gray-500">Q{{ currentIdx + 1 }} / {{ totalQuestions }}</span>
        </div>

        <h2 class="text-2xl font-black leading-relaxed mb-8 uppercase" style="font-family: 'Poppins', sans-serif;">
          {{ question.question }}
        </h2>

        <div class="mb-8">
          <label class="block text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">
            📝 我的回答
          </label>
          <textarea v-model="editUserAnswer"
                    placeholder="在此输入你的回答..."
                    class="input resize-none"
                    rows="8"></textarea>
          <button @click="confirmUserAnswer"
                  :disabled="userUnchanged || savingUser"
                  :class="['btn mt-2 py-2 text-sm font-black uppercase', userUnchanged ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-primary']"
                  style="font-family: 'Poppins', sans-serif;">
            {{ savingUser ? '保存中...' : (userSaved ? '✅ 已确认' : '确认修改') }}
          </button>
        </div>

        <button @click="toggleReference"
                :class="['btn w-full py-4 text-base font-black uppercase tracking-wider', showRef ? 'btn-secondary' : 'btn-primary']"
                style="font-family: 'Poppins', sans-serif;">
          {{ showRef ? '隐藏参考答案' : '查看参考答案 ✅' }}
        </button>

        <div v-show="showRef" class="mt-6 fade-in">
          <label class="block text-sm font-black uppercase tracking-wider mb-3" style="font-family: 'Poppins', sans-serif;">
            ✅ 参考答案
          </label>
          <textarea v-model="editReferenceAnswer"
                    placeholder="在此输入或查看参考答案..."
                    class="input resize-none"
                    rows="10"></textarea>
          <button @click="confirmReferenceAnswer"
                  :disabled="refUnchanged || savingRef"
                  :class="['btn mt-2 py-2 text-sm font-black uppercase', refUnchanged ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-primary']"
                  style="font-family: 'Poppins', sans-serif;">
            {{ savingRef ? '保存中...' : (refSaved ? '✅ 已确认' : '确认修改') }}
          </button>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <button @click="goToPrev"
                :disabled="!hasPrev"
                :class="['btn py-3 font-black uppercase flex items-center justify-center gap-2', hasPrev ? 'btn-secondary' : 'btn-secondary opacity-50 cursor-not-allowed']">
          ⬅️ 上一题
        </button>

        <button @click="goBackToSection"
                class="btn btn-primary py-3 font-black uppercase flex items-center justify-center gap-2">
          📍 返回小节
        </button>

        <button @click="goToNext"
                :disabled="!hasNext"
                :class="['btn py-3 font-black uppercase flex items-center justify-center gap-2', hasNext ? 'btn-primary' : 'btn-secondary opacity-50 cursor-not-allowed']">
          下一题 ➡️
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const questionId = ref(null)
const question = ref(null)
const showRef = ref(false)
const loading = ref(true)
const sectionName = ref('')
const prevQuestionId = ref(null)
const nextQuestionId = ref(null)
const currentIdx = ref(0)
const totalQuestions = ref(0)

const editUserAnswer = ref('')
const editReferenceAnswer = ref('')
const userSaved = ref(false)
const refSaved = ref(false)
const savingUser = ref(false)
const savingRef = ref(false)

const userUnchanged = computed(() => editUserAnswer.value === (question.value?.user_answer || ''))
const refUnchanged = computed(() => editReferenceAnswer.value === (question.value?.reference_answer || ''))
const hasPrev = computed(() => prevQuestionId.value !== null && prevQuestionId.value !== undefined)
const hasNext = computed(() => nextQuestionId.value !== null && nextQuestionId.value !== undefined)

const goToPrev = () => {
  if (hasPrev.value) {
    const targetId = prevQuestionId.value
    questionId.value = null
    router.push(`/lion-questions/practice/${targetId}`)
  }
}

const goToNext = () => {
  if (hasNext.value) {
    const targetId = nextQuestionId.value
    questionId.value = null
    router.push(`/lion-questions/practice/${targetId}`)
  }
}

const goBackToSection = () => {
  router.push({ path: '/lion-questions', query: { expand: question.value?.level2_id } })
}

const toggleReference = () => {
  showRef.value = !showRef.value
}

const confirmUserAnswer = async () => {
  if (!question.value) return
  savingUser.value = true
  try {
    await axios.put(`/api/lion-questions/${question.value.id}`, {
      user_answer: editUserAnswer.value,
      reference_answer: question.value.reference_answer
    })
    question.value.user_answer = editUserAnswer.value
    userSaved.value = true
    setTimeout(() => { userSaved.value = false }, 1500)
  } catch (e) {
    console.error('保存失败:', e)
  } finally {
    savingUser.value = false
  }
}

const confirmReferenceAnswer = async () => {
  if (!question.value) return
  savingRef.value = true
  try {
    await axios.put(`/api/lion-questions/${question.value.id}`, {
      user_answer: question.value.user_answer,
      reference_answer: editReferenceAnswer.value
    })
    question.value.reference_answer = editReferenceAnswer.value
    refSaved.value = true
    setTimeout(() => { refSaved.value = false }, 1500)
  } catch (e) {
    console.error('保存失败:', e)
  } finally {
    savingRef.value = false
  }
}

async function loadQuestion() {
  loading.value = true
  question.value = null
  userSaved.value = false
  refSaved.value = false
  showRef.value = false

  try {
    const r = await axios.get(`/api/lion-questions/${questionId.value}`)
    question.value = r.data
    editUserAnswer.value = r.data.user_answer || ''
    editReferenceAnswer.value = r.data.reference_answer || ''

    if (r.data.level2_id) {
      const treeRes = await axios.get('/api/lion-questions/tree')
      let sectionQuestions = []
      for (const subj of treeRes.data.subjects) {
        for (const ch of subj.level1s) {
          for (const sec of ch.level2s) {
            if (sec.id === r.data.level2_id) {
              sectionName.value = sec.name
              sectionQuestions = sec.questions.map(q => q.id)
              break
            }
          }
        }
      }

      totalQuestions.value = sectionQuestions.length
      const idx = sectionQuestions.indexOf(Number(questionId.value))
      currentIdx.value = idx
      prevQuestionId.value = idx > 0 ? sectionQuestions[idx - 1] : null
      nextQuestionId.value = idx < sectionQuestions.length - 1 ? sectionQuestions[idx + 1] : null
    } else {
      totalQuestions.value = 1
      currentIdx.value = 0
      prevQuestionId.value = null
      nextQuestionId.value = null
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  questionId.value = route.params.questionId
  loadQuestion()
})

watch(() => route.params.questionId, (newId) => {
  if (newId && newId !== questionId.value) {
    questionId.value = newId
    loadQuestion()
  }
})
</script>
