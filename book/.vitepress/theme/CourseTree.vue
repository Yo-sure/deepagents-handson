<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, withBase } from 'vitepress'
const route = useRoute()
const path = computed(() => route.path.replace(/^\/deepagents-handson/, '').replace(/\.html$/, '').replace(/\/$/, '') || '/')
const visible = computed(() => path.value === '/' || ['/toc', '/git-setup', '/updates'].includes(path.value) || path.value.startsWith('/workshop/'))
const open = ref(true)
const groups = [
  { title: '수업 순서', items: [
    ['시작 안내 · 환경설정', '/workshop/start'], ['01 Agent 입문', '/workshop/agent'],
    ['02 LangChain', '/workshop/langchain'], ['03 LangGraph', '/workshop/graph'],
    ['04 Harness · Loop', '/workshop/harness'], ['05 MCP', '/workshop/mcp'],
    ['06 A2A · ACP', '/workshop/a2a'], ['07 통합 · 정리', '/workshop/wrap'],
  ] },
  { title: '직접 완성하는 실습', items: [['내 업무 Agent 만들기', '/workshop/build']] },
  { title: '참고 자료', items: [['Loop · Graph Engineering', '/workshop/engineering'], ['Git으로 자료 받기', '/git-setup'], ['버전 · 참고 자료', '/updates']] },
]
const expanded = ref([true, true, false])
function revealCurrent() {
  groups.forEach((group, i) => { if (group.items.some(([, link]) => link === path.value)) expanded.value[i] = true })
}
watch(path, revealCurrent, { immediate: true })
onMounted(() => {
  try { open.value = localStorage.getItem('course-tree-open') !== 'false' } catch {}
})
function toggle() {
  open.value = !open.value
  try { localStorage.setItem('course-tree-open', String(open.value)) } catch {}
}
</script>

<template>
  <aside v-if="visible" class="course-tree" :data-open="open" aria-label="교재 탐색">
    <div class="course-tree-head">
      <span v-if="open">교재 목차</span>
      <button type="button" @click="toggle" :aria-expanded="open" aria-controls="course-tree-nav" :aria-label="open ? '교재 목차 접기' : '교재 목차 펼치기'" :title="open ? '교재 목차 접기' : '교재 목차 펼치기'">{{ open ? '‹' : '☰' }}</button>
    </div>
    <nav id="course-tree-nav" v-show="open" aria-label="교재 페이지">
      <a class="course-tree-overview" :href="withBase('/toc')" :aria-current="path === '/toc' ? 'page' : undefined">전체 목차 · 시간표</a>
      <section v-for="(group, index) in groups" :key="group.title">
        <button class="course-tree-group" type="button" :aria-expanded="expanded[index]" :aria-controls="'course-group-' + index" @click="expanded[index] = !expanded[index]">
          <span aria-hidden="true">{{ expanded[index] ? '⌄' : '›' }}</span>{{ group.title }}
        </button>
        <ul :id="'course-group-' + index" v-show="expanded[index]">
          <li v-for="[label, link] in group.items" :key="link">
            <a :href="withBase(link)" :aria-current="path === link ? 'page' : undefined">{{ label }}</a>
          </li>
        </ul>
      </section>
    </nav>
  </aside>
</template>

<style>
.course-tree { position: fixed; top: var(--vp-nav-height, 64px); bottom: 0; left: 0; width: 264px; z-index: 25; background: #f7f8f7; border-right: 1px solid #dce3e0; color: #34433e; font-family: Pretendard, sans-serif; overflow-y: auto; overscroll-behavior: contain; }
.course-tree[data-open="false"] { width: 48px; }
.course-tree-head { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; font-size: 15px; font-weight: 700; }
.course-tree-head button { width: 32px; height: 32px; border: 1px solid #dce3e0; border-radius: 5px; background: white; font-size: 24px; line-height: 1; cursor: pointer; }
.course-tree[data-open="false"] .course-tree-head { padding: 14px 8px; }
.course-tree[data-open="false"] .course-tree-head button { font-size: 19px; }
.course-tree nav { padding: 0 12px 24px; }
.course-tree a { display: block; padding: 9px 12px; border-radius: 4px; font-size: 14px; line-height: 1.5; text-decoration: none; }
.course-tree a:hover { background: #eaf0ed; }
.course-tree a[aria-current="page"] { color: #07594e; background: #e1eee8; font-weight: 700; box-shadow: inset 3px 0 #0f766e; }
.course-tree-overview { margin-bottom: 14px; }
.course-tree section { margin-top: 12px; }
.course-tree-group { display: flex; gap: 8px; align-items: center; width: 100%; padding: 8px; font-size: 13px; font-weight: 700; cursor: pointer; text-align: left; }
.course-tree-group span { width: 12px; font-size: 18px; }
.course-tree ul { padding: 0 0 0 12px; margin: 0 0 0 12px; border-left: 1px solid #dce3e0; list-style: none; }
.course-tree a:focus-visible, .course-tree button:focus-visible { outline: 2px solid #0f766e; outline-offset: 2px; }
.Layout:has(.course-tree) .VPContent { margin-left: 264px; width: calc(100% - 264px); min-width: 0; }
.Layout:has(.course-tree[data-open="false"]) .VPContent { margin-left: 48px; width: calc(100% - 48px); }
</style>
