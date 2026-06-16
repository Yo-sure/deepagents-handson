<script setup>
import { ref } from 'vue'
const props = defineProps({ question: { type: String, required: true }, options: { type: Array, required: true } })
const picked = ref(null)
const answered = ref(false)
function choose(i) { picked.value = i; answered.value = true }
</script>

<template>
  <div class="quiz">
    <p class="quiz-q">❓ {{ question }}</p>
    <button v-for="(opt, i) in options" :key="i" class="quiz-opt"
      :class="{ picked: picked === i, correct: answered && opt.correct, wrong: answered && picked === i && !opt.correct }"
      @click="choose(i)">{{ opt.text }}</button>
    <p v-if="answered" class="quiz-fb">{{ options[picked].correct ? '✅ 정답입니다!' : '❌ 다시 생각해 보세요.' }}</p>
  </div>
</template>

<style scoped>
.quiz { border: 1px solid var(--vp-c-divider); border-radius: 12px; padding: 16px 20px; margin: 24px 0; background: var(--vp-c-bg-soft); }
.quiz-q { font-weight: 600; margin: 0 0 12px; }
.quiz-opt { display: block; width: 100%; text-align: left; padding: 10px 14px; margin: 6px 0; border: 1px solid var(--vp-c-divider); border-radius: 8px; background: var(--vp-c-bg); cursor: pointer; transition: all 0.15s; }
.quiz-opt:hover { border-color: var(--vp-c-brand-1); }
.quiz-opt.picked { border-color: var(--vp-c-brand-1); }
.quiz-opt.correct { border-color: #16a34a; background: #16a34a22; }
.quiz-opt.wrong { border-color: #dc2626; background: #dc262622; }
.quiz-fb { margin: 12px 0 0; font-weight: 600; }
</style>
