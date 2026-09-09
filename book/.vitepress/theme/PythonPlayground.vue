<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { withBase } from 'vitepress'
const props = defineProps<{ kind?: string }>()
const snippets = {
  "a2a-events": `# 이벤트 전달을 이해하기 위한 모형입니다. A2A SDK/서버는 실행하지 않습니다.
passed = False
events = [
    ("task", {"id": "task-1", "state": "submitted", "artifacts": []}),
    ("status", {"task_id": "task-1", "state": "working"}),
    ("artifact", {"task_id": "task-1", "result": {"passed": passed}}),
    ("status", {"task_id": "task-1", "state": "completed"}),
]

task = None
for kind, payload in events:
    if kind == "task":
        task = payload
    else:
        if task is None or payload["task_id"] != task["id"]:
            raise ValueError("갱신할 Task가 없습니다")
        if kind == "status":
            task["state"] = payload["state"]
        elif kind == "artifact":
            task["artifacts"].append(payload["result"])
    print(kind, "→", task)

print("최종 상태:", task["state"])
print("업무 통과:", task["artifacts"][0]["passed"])
`,
  lookup: `teams = {"정산": "재무지원팀", "계정": "IT지원팀"}

def lookup_team(topic):
    return teams.get(topic.strip(), "등록된 업무가 없습니다")

topic = "정산"
print(lookup_team(topic))`,
  validation: `from typing import Literal
from pydantic import BaseModel, ValidationError

class TeamInput(BaseModel):
    topic: Literal["정산", "계정"]

def find_team(topic: str) -> str:
    teams = {"정산": "재무지원팀", "계정": "IT지원팀"}
    return teams[topic]

try:
    request = TeamInput(topic="휴가")
except ValidationError:
    print("ValidationError: 허용하지 않은 업무입니다. 함수는 실행되지 않았습니다.")
else:
    print("입력 통과: 이제 담당 팀을 조회합니다.")
    print(find_team(request.topic))`,

}
const initial = snippets[props.kind as keyof typeof snippets] || snippets.lookup
const code = ref(initial)
const editorHost = ref<HTMLElement>()
const editorReady = ref(false)
let editor: import('@codemirror/view').EditorView | undefined
let unmounted = false
onMounted(async () => {
  try {
  const [{ EditorView, keymap, lineNumbers }, { EditorState }, { python }, { defaultKeymap, indentWithTab }, { oneDark }] = await Promise.all([
    import('@codemirror/view'), import('@codemirror/state'), import('@codemirror/lang-python'), import('@codemirror/commands'), import('@codemirror/theme-one-dark')
  ])
  if (unmounted || !editorHost.value) return
  editor = new EditorView({
    parent: editorHost.value,
    state: EditorState.create({ doc: code.value, extensions: [
      lineNumbers(), python(), oneDark, keymap.of([...defaultKeymap, indentWithTab]),
      EditorView.contentAttributes.of({ 'aria-label': '실행할 Python 코드' }),
      EditorView.updateListener.of(update => { if (update.docChanged) code.value = update.state.doc.toString() }),
      EditorView.theme({ '&': { fontSize: '15px' }, '.cm-scroller': { fontFamily: 'Consolas, monospace', lineHeight: '1.7', overflow: 'auto', maxHeight: '440px' }, '.cm-content': { padding: '16px 0' }, '.cm-gutters': { paddingRight: '8px' }, '&.cm-focused': { outline: '2px solid #438a75' } })
    ] })
  })
  editorReady.value = true
  } catch { output.value = '코드 색상을 불러오지 못했습니다. 아래 입력 칸에서 코드를 편집하고 실행할 수 있습니다.' }
})
const output = ref('입력이나 코드를 바꾸고 실행해 봅니다.')
const busy = ref(false)
let worker: Worker | undefined
let timer: ReturnType<typeof setTimeout> | undefined
function dispose() { clearTimeout(timer); worker?.terminate(); worker = undefined; busy.value = false }
function stop() { dispose(); output.value = '실행을 중단했습니다. 코드를 수정해 다시 실행할 수 있습니다.' }
function reset() { dispose(); code.value = initial; editor?.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: initial } }); output.value = '처음 코드로 돌아왔습니다.' }
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
      worker.onerror = () => { dispose(); output.value = 'Python 환경을 불러오지 못했습니다. 네트워크 연결을 확인한 뒤 다시 실행하거나, 실습 JupyterLab의 새 코드 셀에 위 코드를 복사해 실행하세요.' }
    }
    timeout(60000)
    worker.postMessage({ code: code.value, packages: props.kind === 'validation' ? ['pydantic'] : [] })
  } catch { dispose(); output.value = '이 브라우저에서 실행 환경을 시작하지 못했습니다. 실습 JupyterLab의 새 코드 셀에 위 코드를 복사해 실행하세요.' }
}
onBeforeUnmount(() => { unmounted = true; editor?.destroy(); dispose() })
</script>
<template>
  <div class="python-playground">
    <strong>교재에서 Python 실행</strong>
    <p>작은 함수의 동작을 확인합니다. 실제 모델 호출은 주피터 노트북에서 진행합니다. 편집 내용은 새로고침하면 초기화됩니다.</p>
    <div ref="editorHost" class="python-editor" v-show="editorReady" />
    <textarea v-if="!editorReady" v-model="code" aria-label="실행할 Python 코드" spellcheck="false" rows="9" />
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
.python-editor {border:1px solid #46544d;border-radius:4px;overflow:hidden;min-height:180px;background:#282c34}
.python-playground textarea {width:100%;padding:16px;background:#282c34;color:#e5e9f0;font:15px/1.7 Consolas,monospace}
.python-controls {display:flex;gap:10px;margin:12px 0}
.python-controls button {padding:8px 16px;background:#235d4a;color:white;border-radius:4px;cursor:pointer}
.python-controls button:disabled {opacity:.45;cursor:default}
.python-playground pre {white-space:pre-wrap;overflow-wrap:anywhere;max-height:260px;overflow:auto;background:white;color:#25312e;padding:14px;border:1px solid #dbe4dd;font:14px/1.7 Consolas,monospace}
</style>

