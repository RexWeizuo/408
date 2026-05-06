import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'

import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Subjects from './views/Subjects.vue'
import SubjectDetail from './views/SubjectDetail.vue'
import ChapterDetail from './views/ChapterDetail.vue'
import KnowledgePointDetail from './views/KnowledgePointDetail.vue'
import QuestionList from './views/QuestionList.vue'
import QuestionPractice from './views/QuestionPractice.vue'
import StudyPlan from './views/StudyPlan.vue'
import LionSubjects from './views/LionSubjects.vue'
import LionSubjectDetail from './views/LionSubjectDetail.vue'
import LionQuestions from './views/LionQuestions.vue'
import LionQuestionPractice from './views/LionQuestionPractice.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/subjects', component: Subjects },
  { path: '/subjects/:subjectId', component: SubjectDetail },
  { path: '/subjects/:subjectId/chapters/:chapterId', component: ChapterDetail },
  { path: '/knowledge/:kpId', component: KnowledgePointDetail },
  { path: '/lion', component: LionSubjects },
  { path: '/lion/:subjectId', component: LionSubjectDetail },
  { path: '/lion-questions', component: LionQuestions },
  { path: '/lion-questions/practice/:questionId', component: LionQuestionPractice },
  { path: '/questions', component: QuestionList },
  { path: '/questions/practice/:questionId', component: QuestionPractice },
  { path: '/plan', component: StudyPlan }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
