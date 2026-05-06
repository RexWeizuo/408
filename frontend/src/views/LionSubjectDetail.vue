<template>
  <div class="fade-in">
    <div class="mb-8">
      <router-link to="/lion" class="text-base font-black uppercase mb-4 inline-block hover:text-bauhaus-blue flex items-center gap-2 group" style="font-family: 'Poppins', sans-serif;">
        <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"></path>
        </svg>
        返回LION主页
      </router-link>

      <div class="card mt-6">
        <div class="flex items-center gap-4">
          <span class="text-5xl">{{ getLionIcon(subjectId) }}</span>
          <div>
            <h1 class="text-3xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">{{ subjectName }}</h1>
            <p class="text-base mt-1 font-medium">四级知识层级结构</p>
          </div>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <div v-for="(level1, idx1) in treeData" :key="level1.id" class="card">
        <div class="flex items-center cursor-pointer" @click="toggleLevel1(idx1)">
          <div class="w-14 h-14 bg-bauhaus-red border-4 border-black flex items-center justify-center text-white font-black text-xl mr-5 flex-shrink-0"
               style="font-family: 'Poppins', sans-serif; box-shadow: 3px 3px 0px #000000;">
            {{ idx1 + 1 }}
          </div>
          <div class="flex-1">
            <h3 class="text-xl font-black uppercase" style="font-family: 'Poppins', sans-serif;">
              {{ level1.name }}
            </h3>
          </div>
          <svg class="w-7 h-7 transition-transform" :class="{ 'rotate-90': level1.expanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
          </svg>
        </div>

        <div v-show="level1.expanded" class="mt-6 ml-16 space-y-4">
          <div v-for="(level2, idx2) in level1.children" :key="level2.id"
               class="p-5 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
            <div class="flex items-center cursor-pointer" @click="toggleLevel2(idx1, idx2)">
              <div class="w-10 h-10 bg-bauhaus-blue border-4 border-black flex items-center justify-center text-white font-bold mr-4 flex-shrink-0"
                   style="box-shadow: 3px 3px 0px #000000;">
                {{ idx2 + 1 }}
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-black uppercase" style="font-family: 'Poppins', sans-serif;">
                  {{ level2.name }}
                </h4>
              </div>
              <svg class="w-6 h-6 transition-transform" :class="{ 'rotate-90': level2.expanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
              </svg>
            </div>

            <div v-show="level2.expanded" class="mt-4 ml-11 space-y-3">
              <div v-for="(level3, idx3) in level2.children" :key="level3.id"
                   class="p-4 border-4 border-black hover:bg-bauhaus-gray-100 transition-colors">
                <div class="flex items-center cursor-pointer" @click="toggleLevel3(idx1, idx2, idx3)">
                  <span class="text-bauhaus-yellow mr-3 text-sm font-black">•</span>
                  <h5 class="font-black uppercase flex-1" style="font-family: 'Poppins', sans-serif;">
                    {{ level3.name }}
                  </h5>
                  <svg class="w-5 h-5 transition-transform" :class="{ 'rotate-90': level3.expanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7 7"></path>
                  </svg>
                </div>

                <div v-show="level3.expanded" class="mt-3 ml-6 space-y-2">
                  <div v-for="(level4, idx4) in level3.children" :key="level4.id"
                       class="p-3 border-3 border-black hover:bg-bauhaus-yellow transition-colors">
                    <p class="text-sm font-bold flex items-center gap-2">
                      <span class="text-bauhaus-blue font-black">▸</span>
                      <span>{{ level4.name }}</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
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
const subjectId = route.params.subjectId
const subjectName = ref('')
const treeData = ref([])

const lionIcons = { operating_system: '💻', computer_organization: '🔧', data_structure: '🌳', computer_network: '🌐' }
const getLionIcon = (id) => lionIcons[id] || '📘'

const toggleLevel1 = (idx) => { treeData.value[idx].expanded = !treeData.value[idx].expanded }
const toggleLevel2 = (l1idx, l2idx) => { treeData.value[l1idx].children[l2idx].expanded = !treeData.value[l1idx].children[l2idx].expanded }
const toggleLevel3 = (l1idx, l2idx, l3idx) => { treeData.value[l1idx].children[l2idx].children[l3idx].expanded = !treeData.value[l1idx].children[l2idx].children[l3idx].expanded }

onMounted(async () => {
  try {
    const r = await axios.get(`/api/lion/${subjectId}`)
    subjectName.value = r.data.name
    treeData.value = r.data.children.map(l1 => ({
      ...l1,
      expanded: false,
      children: l1.children.map(l2 => ({
        ...l2,
        expanded: false,
        children: l2.children.map(l3 => ({ ...l3, expanded: false }))
      }))
    }))
  } catch (e) { console.error(e) }
})
</script>
