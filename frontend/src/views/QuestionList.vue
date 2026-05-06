<template>
  <div class="fade-in space-y-8">
    <div class="mb-10">
      <h1 class="bauhaus-title">选择题 ✍️</h1>
      <p class="bauhaus-subtitle mt-3">按科目和章节分类，系统练习巩固知识</p>
    </div>

    <div class="flex gap-3 flex-wrap mb-8">
      <button v-for="s in subjectList" :key="s.id" @click="activeSubject = activeSubject === s.id ? null : s.id"
        :class="['btn text-sm font-bold uppercase tracking-wider', activeSubject === s.id ? 'btn-primary' : 'btn-secondary']"
        style="font-family: 'Poppins', sans-serif;">
        <span>{{ s.icon }}</span><span>{{ s.name }}</span>
      </button>
    </div>

    <div v-if="loading" class="card text-center py-16">
      <p class="text-lg font-bold">加载中...</p>
    </div>

    <div v-else-if="treeData.length === 0" class="card text-center py-16">
      <p class="text-lg font-bold mb-4">暂无选择题</p>
      <p class="text-base">请先录入选择题</p>
    </div>

    <div v-else class="space-y-6">
      <template v-for="subject in filteredTreeData" :key="subject.subject_id">
        <!-- Subject Level -->
        <div class="card">
          <div @click="toggleNode('subject', subject.subject_id)"
               class="flex items-center cursor-pointer pb-4 border-b-4 border-black"
               :class="{ 'mb-6': isNodeExpanded('subject', subject.subject_id) }">
            <span class="text-3xl mr-4">{{ subject.icon }}</span>
            <span class="font-black uppercase text-xl flex-1" style="font-family: 'Poppins', sans-serif;">{{ subject.name }}</span>
            <span class="badge badge-red mr-4 font-bold">{{ countQuestions(subject) }} 题</span>
            <svg class="w-7 h-7 transition-transform" :class="{ 'rotate-90': isNodeExpanded('subject', subject.subject_id) }"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
            </svg>
          </div>

          <div v-show="isNodeExpanded('subject', subject.subject_id)" class="space-y-5">
            <template v-for="chapter in subject.chapters" :key="chapter.chapter_id">
              <!-- Chapter Level -->
              <div class="border-l-4 border-bauhaus-blue pl-5 ml-2">
                <div @click="toggleNode('chapter', chapter.chapter_id)"
                     class="flex items-center cursor-pointer pb-3 border-b-3 border-black mb-3"
                     :class="{ 'mb-4': isNodeExpanded('chapter', chapter.chapter_id) }">
                  <span class="text-xl mr-3">☑️</span>
                  <span class="font-black uppercase text-lg flex-1" style="font-family: 'Poppins', sans-serif;">{{ chapter.chapter_name }}</span>
                  <span class="badge badge-blue mr-3 font-bold">{{ countChapterQuestions(chapter) }} 题</span>
                  <svg class="w-6 h-6 transition-transform" :class="{ 'rotate-90': isNodeExpanded('chapter', chapter.chapter_id) }"
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
                  </svg>
                </div>

                <div v-show="isNodeExpanded('chapter', chapter.chapter_id)" class="space-y-3 pl-4">
                  <template v-for="kp in chapter.knowledge_points" :key="kp.knowledge_point_id">
                    <!-- Knowledge Point Level -->
                    <div class="border-l-4 border-bauhaus-yellow pl-4 ml-2">
                      <div @click="toggleNode('kp', kp.knowledge_point_id)"
                           class="flex items-center cursor-pointer pb-2 border-b-3 border-black mb-2"
                           :class="{ 'mb-3': isNodeExpanded('kp', kp.knowledge_point_id) }">
                        <span class="text-lg mr-2">📖</span>
                        <span class="font-black uppercase flex-1" style="font-family: 'Poppins', sans-serif;">{{ kp.knowledge_point_name }}</span>
                        <span class="badge badge-yellow mr-2 font-bold">{{ kp.questions.length }} 题</span>
                        <router-link :to="`/knowledge/${kp.knowledge_point_id}`" @click.stop
                                     class="btn btn-secondary text-xs px-3 py-1.5 mx-2">查看知识点</router-link>
                        <button @click.stop="practiceAll(kp.questions)" class="btn btn-primary text-xs px-3 py-1.5">开始练习</button>
                        <svg class="w-5 h-5 transition-transform flex-shrink-0 ml-2" :class="{ 'rotate-90': isNodeExpanded('kp', kp.knowledge_point_id) }"
                             fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
                        </svg>
                      </div>

                      <!-- Questions List -->
                      <div v-show="isNodeExpanded('kp', kp.knowledge_point_id)" class="space-y-2 pl-3">
                        <div v-for="q in kp.questions" :key="q.id" class="border-4 border-black p-4 hover:bg-bauhaus-gray-100 transition-colors">
                          <div class="flex items-start justify-between gap-4">
                            <div class="flex-1 min-w-0">
                              <p class="font-black mb-3">{{ q.question }}</p>
                              <div class="grid grid-cols-2 gap-2">
                                <div v-for="opt in q.options" :key="opt" class="px-3 py-2 bg-white border-3 border-black text-sm">{{ opt }}</div>
                              </div>
                            </div>
                            <router-link :to="`/questions/practice/${q.id}`" class="btn btn-primary text-xs px-4 py-2 flex-shrink-0 mt-auto">答题</router-link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeSubject = ref(null)
const loading = ref(true)
const treeData = ref([])
const expandedNodes = ref(new Set())

const subjectList = [
  { id: 'data_structure', name: '数据结构', icon: '🌳' },
  { id: 'computer_organization', name: '组成原理', icon: '🔧' },
  { id: 'operating_system', name: '操作系统', icon: '💻' },
  { id: 'computer_network', name: '计算机网络', icon: '🌐' }
]

const getSubjectInfo = (subjectId) => {
  return subjectList.find(s => s.id === subjectId) || { icon: '📚', name: subjectId }
}

const filteredTreeData = computed(() => {
  if (!activeSubject.value) return treeData.value
  return treeData.value.filter(s => s.subject_id === activeSubject.value)
})

const countQuestions = (subject) => {
  return subject.chapters.reduce((sum, ch) => {
    return sum + ch.knowledge_points.reduce((s, kp) => s + kp.questions.length, 0)
  }, 0)
}

const countChapterQuestions = (chapter) => {
  return chapter.knowledge_points.reduce((sum, kp) => sum + kp.questions.length, 0)
}

const getNodeKey = (type, id) => `${type}:${id}`

const toggleNode = (type, id) => {
  const key = getNodeKey(type, id)
  const newSet = new Set(expandedNodes.value)
  if (newSet.has(key)) {
    newSet.delete(key)
  } else {
    newSet.add(key)
  }
  expandedNodes.value = newSet
}

const isNodeExpanded = (type, id) => expandedNodes.value.has(getNodeKey(type, id))

const practiceAll = (questions) => {
  if (questions.length > 0) {
    router.push(`/questions/practice/${questions[0].id}`)
  }
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/questions/grouped?type=choice')
    const subjects = res.data.subjects.map(s => ({
      subject_id: s.subject_id,
      ...getSubjectInfo(s.subject_id),
      chapters: s.chapters
    }))
    treeData.value = subjects
  } catch (e) {
    console.error('获取题目失败:', e)
  } finally {
    loading.value = false
  }
})
</script>
