<template>
  <div class="scroll-progress" :style="{ top: `${top}px` }" aria-hidden="true">
    <div class="scroll-progress__bar" :style="{ transform: `scaleX(${progress})` }" />
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vitepress'

const route = useRoute()
const progress = ref(0)
const top = ref(0)

function updateProgress() {
  const doc = document.documentElement
  const max = doc.scrollHeight - window.innerHeight
  const nav = document.querySelector('.VPNavBar') ?? document.querySelector('.VPNav')
  const navBottom = nav?.getBoundingClientRect().bottom ?? 0
  const fallback = Number.parseFloat(getComputedStyle(doc).getPropertyValue('--vp-nav-height')) || 0
  top.value = Math.max(0, Math.round((navBottom || fallback) - 3))
  progress.value = max > 0 ? Math.min(Math.max(window.scrollY / max, 0), 1) : 0
}

onMounted(() => {
  updateProgress()
  window.addEventListener('scroll', updateProgress, { passive: true })
  window.addEventListener('resize', updateProgress)
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
  window.removeEventListener('resize', updateProgress)
})

watch(
  () => route.path,
  () => nextTick(updateProgress)
)
</script>

<style scoped>
.scroll-progress {
  position: fixed;
  left: 0;
  z-index: 60;
  width: 100%;
  height: 3px;
  background: rgba(217, 205, 185, 0.45);
  pointer-events: none;
}

.scroll-progress__bar {
  width: 100%;
  height: 100%;
  transform-origin: left center;
  background: linear-gradient(90deg, #e09f3e, #0f766e);
  box-shadow: 0 1px 8px rgba(15, 118, 110, 0.25);
}

@media print {
  .scroll-progress {
    display: none;
  }
}
</style>
