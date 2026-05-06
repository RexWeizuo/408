<template>
  <div class="fade-in space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-3xl">💡</span>
          <div>
            <h1 class="bauhaus-title">知识点问题</h1>
            <p class="bauhaus-subtitle mt-2">LION层级知识点问答题，深入学习每个小节</p>
          </div>
        </div>
      </div>
    </div>

    <div class="flex gap-3 flex-wrap">
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
      <p class="text-lg font-bold mb-4">暂无知识点问题</p>
      <p class="text-base">请先录入知识点相关的问答题</p>
    </div>

    <div v-else class="space-y-5">
      <template v-for="subject in filteredTreeData" :key="subject.subject_id">
        <!-- Level 0: Subject -->
        <div class="card">
          <div @click.stop="toggleNode('subject', subject.subject_id)"
               class="flex items-center cursor-pointer pb-4 border-b-4 border-black"
               :class="{ 'mb-6': isNodeExpanded('subject', subject.subject_id) }">
            <span class="text-3xl mr-4">{{ subject.icon }}</span>
            <span class="font-black uppercase text-xl flex-1" style="font-family: 'Poppins', sans-serif;">{{ subject.subject_name }}</span>
            <span class="badge badge-red mr-4 font-bold">{{ countSubjectQuestions(subject) }} 题</span>
            <svg class="w-7 h-7 transition-transform" :class="{ 'rotate-90': isNodeExpanded('subject', subject.subject_id) }"
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
            </svg>
          </div>

          <div v-show="isNodeExpanded('subject', subject.subject_id)" class="space-y-5">
            <template v-for="chapter in subject.chapters" :key="chapter.id">
              <!-- Level 1: Chapter -->
              <div class="border-l-4 border-bauhaus-blue pl-5 ml-2">
                <div @click.stop="toggleNode('chapter', chapter.id)"
                     class="flex items-center cursor-pointer pb-3 border-b-3 border-black mb-3"
                     :class="{ 'mb-4': isNodeExpanded('chapter', chapter.id) }">
                  <span class="text-xl mr-3">📗</span>
                  <span class="font-black uppercase text-lg flex-1" style="font-family: 'Poppins', sans-serif;">{{ chapter.name }}</span>
                  <span class="badge badge-blue mr-3 font-bold">{{ countChapterQuestions(chapter) }} 题</span>
                  <svg class="w-6 h-6 transition-transform" :class="{ 'rotate-90': isNodeExpanded('chapter', chapter.id) }"
                       fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
                  </svg>
                </div>

                <div v-show="isNodeExpanded('chapter', chapter.id)" class="space-y-3 pl-4">
                  <template v-for="section in chapter.sections" :key="section.id">
                    <!-- Level 2: Section -->
                    <div class="border-l-4 border-bauhaus-yellow pl-4 ml-2">
                      <div @click.stop="toggleNode('section', section.id)"
                           class="flex items-center cursor-pointer pb-2 border-b-3 border-black mb-2"
                           :class="{ 'mb-3': isNodeExpanded('section', section.id) }">
                        <span class="text-lg mr-2">📘</span>
                        <span class="font-black uppercase flex-1" style="font-family: 'Poppins', sans-serif;">{{ section.name }}</span>
                        <span class="badge badge-yellow mr-2 font-bold">{{ section.questions.length }} 题</span>
                        <svg class="w-5 h-5 transition-transform flex-shrink-0 ml-2" :class="{ 'rotate-90': isNodeExpanded('section', section.id) }"
                             fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
                        </svg>
                      </div>

                      <!-- Question Cards List -->
                      <div v-show="isNodeExpanded('section', section.id)" class="space-y-2 pl-3">
                        <template v-for="(q, qIndex) in section.questions" :key="q.id">
                          <!-- Question Card -->
                          <div class="question-card">
                            <div class="question-card-header">
                              <div class="question-card-info">
                                <span class="q-number">Q{{ qIndex + 1 }}</span>
                                <p class="q-text">{{ q.question }}</p>
                              </div>
                              <router-link :to="`/lion-questions/practice/${q.id}`"
                                           class="answer-btn">
                                答题
                              </router-link>
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
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

const countSectionQuestions = (section) => (section.questions || []).length
const countChapterQuestions = (chapter) => (chapter.sections || []).reduce((sum, s) => sum + countSectionQuestions(s), 0)
const countSubjectQuestions = (subject) => (subject.chapters || []).reduce((sum, ch) => sum + countChapterQuestions(ch), 0)

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

onMounted(async () => {
  try {
    const res = await axios.get('/api/lion-questions/tree')
    const subjects = res.data.subjects.map(s => ({
      subject_id: s.subject_id,
      subject_name: s.subject_name,
      ...getSubjectInfo(s.subject_id),
      chapters: s.level1s.map(l1 => ({
        id: l1.id,
        name: l1.name,
        sections: l1.level2s
      }))
    }))
    treeData.value = subjects

    const expandTarget = route.query.expand
    if (expandTarget) {
      for (const subj of subjects) {
        for (const ch of subj.chapters) {
          for (const sec of ch.sections) {
            if (sec.id === expandTarget) {
              expandedNodes.value.add(`subject:${subj.subject_id}`)
              expandedNodes.value.add(`chapter:${ch.id}`)
              expandedNodes.value.add(`section:${sec.id}`)
              activeSubject.value = subj.subject_id
              return
            }
          }
        }
      }
    }
  } catch (e) {
    console.error('获取问题失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.question-card {
  border: 3px solid #000;
  padding: 1rem;
  background-color: #fff;
  box-shadow: 3px 3px 0px #000;
  transition: all 0.15s ease;
}
.question-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 5px 5px 0px #000;
}

.question-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.question-card-info {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.q-number {
  display: flex; align-items: center; justify-content: center;
  width: 1.875rem; height: 1.875rem; border-radius: 0.25rem;
  font-size: 0.6875rem; font-weight: 800;
  background-color: #E3000B; color: white; flex-shrink: 0;
  font-family: 'Poppins', sans-serif;
}

.q-text {
  color: #000; font-size: 0.8125rem; line-height: 1.55; font-weight: 500;
  overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}

.answer-btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.25rem;
  font-size: 0.75rem; font-weight: 800;
  background-color: #003DA5; color: white;
  border: 3px solid #000; cursor: pointer;
  box-shadow: 2px 2px 0px #000;
  transition: all 0.15s ease; flex-shrink: 0;
  white-space: nowrap;
  font-family: 'Poppins', sans-serif; letter-spacing: 0.05em; text-transform: uppercase;
  text-decoration: none; text-align: center;
}
.answer-btn:hover {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0px #000;
}
</style>
