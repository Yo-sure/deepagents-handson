<script setup>
import { computed, ref } from 'vue'
import questions from './wrapQuestions.json'
const props = defineProps({ questionIds: { type: Array, default: () => questions.map((_, i) => i) } })
const selectedIds = props.questionIds
const deck = ref([...selectedIds])
const position = ref(0)
const picks = ref({})
const finished = ref(false)
const retry = ref(false)
const id = computed(() => deck.value[position.value])
const current = computed(() => questions[id.value])
const answered = computed(() => picks.value[id.value] !== undefined)
const correct = computed(() => selectedIds.filter(i => picks.value[i] === questions[i].answer).length)
const wrong = computed(() => selectedIds.filter(i => picks.value[i] !== undefined && picks.value[i] !== questions[i].answer))
function choose(i) { if (!answered.value) picks.value[id.value] = i }
function next() { if (position.value + 1 === deck.value.length) finished.value = true; else position.value++ }
function restart(onlyWrong = false) {
  const ids = onlyWrong ? [...wrong.value] : [...selectedIds]
  if (!ids.length) return
  if (onlyWrong) ids.forEach(i => delete picks.value[i]); else picks.value = {}
  deck.value = ids; position.value = 0; finished.value = false; retry.value = onlyWrong
}
</script>

<template>
  <div class="wrap-quiz">
    <div class="quiz-status"><strong>{{ retry ? '틀린 문제 다시 풀기' : '오늘의 개념 퀴즈' }}</strong><span>정답 {{ correct }} / {{ selectedIds.length }}</span></div>
    <template v-if="!finished">
      <p class="quiz-count">카드 {{ position + 1 }} / {{ deck.length }} · {{ current.topic }}</p>
      <progress :value="position + (answered ? 1 : 0)" :max="deck.length" aria-label="현재 퀴즈 진행률" />
      <fieldset :key="id">
        <legend>{{ current.question }}</legend>
        <button v-for="(option, i) in current.options" :key="i" type="button" class="answer"
          :disabled="answered" :class="{ right: answered && i === current.answer, wrong: answered && picks[id] === i && i !== current.answer }"
          @click="choose(i)">
          <span class="answer-number">{{ i + 1 }}</span>{{ option }}
          <strong v-if="answered && i === current.answer"> · 정답</strong>
          <strong v-else-if="answered && picks[id] === i"> · 내가 고른 답</strong>
        </button>
      </fieldset>
      <div class="explanation" aria-live="polite" aria-atomic="true">
        <template v-if="answered"><strong>{{ picks[id] === current.answer ? '맞았습니다.' : '다시 짚어 봅시다.' }}</strong><p>{{ current.why }}</p><a :href="'./' + current.link" target="_blank" rel="noopener">관련 개념 다시 읽기 ↗</a></template>
        <p v-else>답을 고른 뒤 해설을 확인합니다.</p>
      </div>
      <div class="quiz-actions"><button type="button" :disabled="position === 0" @click="position--">이전 카드</button><button type="button" :disabled="!answered" @click="next">{{ position + 1 === deck.length ? '결과 보기' : '다음 카드' }}</button></div>
    </template>
    <div v-else class="quiz-result" aria-live="polite">
      <h3>{{ wrong.length ? '헷갈린 개념을 한 번 더 확인해 봅시다.' : `${selectedIds.length}개 개념을 모두 맞혔습니다.` }}</h3>
      <p>정답 {{ correct }}개 · 다시 볼 문제 {{ wrong.length }}개</p>
      <p v-if="retry">처음 풀이와 이번 재도전 결과를 합친 현재 기록입니다.</p>
      <div class="quiz-actions"><button v-if="wrong.length" type="button" @click="restart(true)">틀린 {{ wrong.length }}문제 다시 풀기</button><button type="button" @click="restart()">전체 다시 풀기</button></div>
    </div>
  </div>
</template>

<style scoped>
.wrap-quiz { margin: 28px 0; padding: clamp(18px, 3vw, 32px); border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); }
.quiz-status, .quiz-actions { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.quiz-count { font-size: 14px; color: var(--vp-c-text-2); }
progress { width: 100%; height: 7px; accent-color: var(--vp-c-brand-1); margin-bottom: 24px; }
fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
legend { font-size: 22px; font-weight: 700; line-height: 1.6; margin-bottom: 18px; }
.answer { display: block; width: 100%; text-align: left; padding: 15px; margin: 10px 0; border: 1px solid var(--vp-c-divider); border-radius: 8px; background: var(--vp-c-bg); color: var(--vp-c-text-1); line-height: 1.7; }
.answer-number { display: inline-block; margin-right: 12px; font-weight: 700; }
button { cursor: pointer; font: inherit; }
button:focus-visible, a:focus-visible { outline: 3px solid var(--vp-c-brand-1); outline-offset: 3px; }
.answer:not(:disabled):hover { border-color: var(--vp-c-brand-1); }
.answer.right { border: 2px solid #23835c; background: #23835c18; }
.answer.wrong { border: 2px solid #c55a36; background: #c55a3612; }
.answer:disabled { cursor: default; }
.explanation { margin: 24px 0; padding: 16px; background: var(--vp-c-bg); border-left: 3px solid var(--vp-c-brand-1); }
.explanation p { margin: 8px 0; }
.quiz-actions button { padding: 10px 18px; border: 1px solid var(--vp-c-brand-1); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-brand-1); }
.quiz-actions button:disabled { opacity: .45; cursor: default; }
@media (max-width: 600px) { legend { font-size: 19px; } .answer { padding: 12px; } }
</style>
