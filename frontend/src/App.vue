<template>
  <div class="min-h-screen bg-white">
    <nav class="sticky top-0 z-50 bg-white border-b-4 border-black">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-bauhaus-red border-4 border-black flex items-center justify-center text-white font-black text-xl"
                 style="font-family: 'Poppins', sans-serif; box-shadow: 3px 3px 0px #000000;">
              408
            </div>
            <span class="text-2xl font-black uppercase tracking-tight" style="font-family: 'Poppins', sans-serif;">
              学习系统
            </span>
          </div>
          <div class="flex items-center gap-1">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              :class="['nav-link', { 'active': isActive(item.path) }]"
            >
              <span class="text-lg">{{ item.icon }}</span>
              <span>{{ item.name }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-10 px-6 lg:px-8">
      <router-view />
    </main>

    <footer class="bg-black text-white py-6 mt-20">
      <div class="max-w-7xl mx-auto px-6 lg:px-8 text-center">
        <p class="font-bold uppercase tracking-wider" style="font-family: 'Poppins', sans-serif;">408 学习系统 · Bauhaus Design</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()

const navItems = [
  { path: '/', name: '仪表盘', icon: '📊' },
  { path: '/subjects', name: '考纲', icon: '📚' },
  { path: '/lion', name: 'LION', icon: '🦁' },
  { path: '/lion-questions', name: '知识点问题', icon: '💡' },
  { path: '/questions', name: '选择题', icon: '✍️' },
  { path: '/plan', name: '规划', icon: '📅' }
]

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
