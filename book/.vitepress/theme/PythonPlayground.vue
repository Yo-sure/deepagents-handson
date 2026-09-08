<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { withBase } from 'vitepress'
const props = defineProps<{ kind?: string }>()
const snippets = {
  lookup: `teams = {"정산": "재무지원팀", "계정": "IT지원팀"}

def lookup_team(topic):
    return teams.get(topic.strip(), "등록된 업무가 없습니다")

topic = "정산"
print(lookup_team(topic))`,
  route: `def route(found, contact):
    if found and contact.strip():
        return "draft"
    return "ask"

print(route(True, ""))
print(route(True, "담당자@example.test"))`
}
const initial = snippets[props.kind as keyof typeof snippets] || snippets.lookup
const code = ref(initial)
const output = ref('입력이나 코드를 바꾸고 실행해 봅니다.')
const busy = ref(false)
let worker: Worker | undefined
let timer: ReturnType<typeof setTimeout> | undefined
function dispose() { clearTimeout(timer); worker?.terminate(); worker = undefined; busy.value = false }
function stop() { dispose(); output.value = '실행을 중단했습니다. 코드를 수정해 다시 실행할 수 있습니다.' }
function reset() { dispose(); code.value = initial; output.value = '처음 코드로 돌아왔습니다.' }
function run() {
  if (busy.value) return
  busy.value = true
  output.value = worker ? '실행 중…' : 'Python 준비 중… 처음에는 실행 환경을 내려받습니다.'
  const timeout = (ms: number) => { clearTimeout(timer); timer = setTimeout(() => { dispose(); output.value = '대기 시간이 초과됐습니다. 네트워크 또는 반복문을 확인하고 다시 실행해 주세요.' }, ms) }
  try {
    if (!worker) {
      worker = new Worker(withBase('/python-worker.js'), { type: 'module' })
      worker.onmessage = ({ data }) => {
        if (data.type === 'ready') { output.value = '실행 중…'; timeout(10000); return }
        clearTimeout(timer); busy.value = false; output.value = data.output
      }
      worker.onerror = () => { dispose(); output.value = 'Python 환경을 불러오지 못했습니다. 네트워크 연결을 확인한 뒤 다시 실행하거나 VS Code에서 확인해 주세요.' }
    }
    timeout(60000)
    worker.postMessage({ code: code.value })
  } catch { dispose(); output.value = '이 브라우저에서 실행 환경을 시작하지 못했습니다. VS Code에서 같은 코드를 실행할 수 있습니다.' }
}
onBeforeUnmount(dispose)
</script>
<template>
  <div class="python-playground">
    <strong>교재에서 Python 실행</strong>
    <p>작은 함수의 동작을 확인합니다. 실제 모델 호출은 VS Code 실습에서 진행합니다. 편집 내용은 새로고침하면 초기화됩니다.</p>
    <textarea v-model="code" aria-label="실행할 Python 코드" spellcheck="false" :rows="initial.split('\n').length + 1" />
    <div class="python-controls">
      <button @click="run" :disabled="busy">{{ busy ? '실행 중…' : 'Python 실행' }}</button>
      <button @click="stop" :disabled="!busy">중단</button>
      <button @click="reset">처음 코드</button>
    </div>
    <pre role="status" aria-live="polite">{{ output }}</pre>
  </div>
</template>
<style scoped>
.python-playground {border:1px solid #b8cec4; padding:20px; background:#f6faf7; margin:24px 0; border-radius:6px}
.python-playground p {font-size:14px; line-height:1.7}
.python-playground textarea {display:block; width:100%; box-sizing:border-box; padding:16px; resize:vertical; background:#fff; color:#25312e; border:1px solid #b9c6bf; font:15px/1.7 Consolas,monospace; tab-size:4}
.python-controls {display:flex;gap:10px;margin:12px 0}
.python-controls button {padding:8px 16px;background:#235d4a;color:white;border-radius:4px;cursor:pointer}
.python-controls button:disabled {opacity:.45;cursor:default}
.python-playground pre {white-space:pre-wrap;overflow-wrap:anywhere;max-height:260px;overflow:auto;background:white;color:#25312e;padding:14px;border:1px solid #dbe4dd;font:14px/1.7 Consolas,monospace}
</style>
