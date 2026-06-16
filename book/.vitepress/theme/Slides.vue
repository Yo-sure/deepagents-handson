<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const props = defineProps({ slides: { type: Array, required: true } })
const i = ref(0)
function next() { if (i.value < props.slides.length - 1) i.value++ }
function prev() { if (i.value > 0) i.value-- }
function go(n) { i.value = n }
function onKey(e) { if (e.key === 'ArrowRight') next(); if (e.key === 'ArrowLeft') prev() }
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="deck-x">
    <div class="stage">
      <Transition name="sl" mode="out-in">
        <div class="card" :key="i">
          <div class="emoji">{{ slides[i].emoji }}</div>
          <h3 class="title">{{ slides[i].title }}</h3>
          <p class="text" v-html="slides[i].text"></p>
        </div>
      </Transition>
    </div>
    <div class="ctrl">
      <button class="nav" :disabled="i === 0" @click="prev">‹ 이전</button>
      <div class="dots"><span v-for="(s, n) in slides" :key="n" class="dot" :class="{ on: n === i }" @click="go(n)" /></div>
      <button class="nav" :disabled="i === slides.length - 1" @click="next">다음 ›</button>
    </div>
    <p class="hint">← → 방향키로도 넘길 수 있어요 · {{ i + 1 }} / {{ slides.length }}</p>
  </div>
</template>

<style scoped>
.deck-x { border: 1px solid var(--vp-c-divider); border-radius: 16px; margin: 28px 0; padding: 8px; background: linear-gradient(160deg, var(--vp-c-bg-soft), var(--vp-c-bg)); }
.stage { min-height: 220px; display: flex; align-items: center; justify-content: center; padding: 24px; }
.card { text-align: center; max-width: 560px; }
.emoji { font-size: 64px; line-height: 1; margin-bottom: 12px; }
.title { font-size: 22px; margin: 0 0 10px; border: 0; padding: 0; }
.text { font-size: 16px; color: var(--vp-c-text-2); margin: 0; }
.ctrl { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px 4px; }
.nav { padding: 6px 14px; border-radius: 8px; cursor: pointer; border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg); }
.nav:disabled { opacity: 0.35; cursor: default; }
.dots { display: flex; gap: 8px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--vp-c-divider); cursor: pointer; transition: all 0.2s; }
.dot.on { background: var(--vp-c-brand-1); transform: scale(1.3); }
.hint { text-align: center; font-size: 12px; color: var(--vp-c-text-3); margin: 6px 0 8px; }
.sl-enter-active, .sl-leave-active { transition: all 0.25s ease; }
.sl-enter-from { opacity: 0; transform: translateX(24px); }
.sl-leave-to { opacity: 0; transform: translateX(-24px); }
</style>
