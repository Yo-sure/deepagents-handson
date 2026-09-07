<script setup lang="ts">
import { computed, ref, watch } from 'vue'
const props = defineProps<{ kind: string }>()
const selected = ref(0)
watch(() => props.kind, () => { selected.value = 0 })
type Scenario = { label: string; steps: string[][]; note: string; decision?: { benefit: string; cost: string; fit: string } }
type Lesson = { title: string; hint: string; scenarios: Scenario[] }
const examples: Record<string, Lesson> = {
  "start": {
    "title": "오늘 실습에서 오가는 것",
    "hint": "교재를 읽는 창과 코드를 실행하는 창을 구분합니다.",
    "scenarios": [
      {
        "label": "준비부터 첫 결과까지",
        "steps": [
          [
            "자료 받기",
            "workshop 폴더를 편집기에서 엽니다."
          ],
          [
            "실행 준비",
            "터미널에서 라이브러리와 .env를 준비합니다."
          ],
          [
            "실제 모델 호출",
            "제공 예제로 정산 규정을 조회합니다."
          ],
          [
            "결과 확인",
            "runs/langchain.json을 편집기에서 엽니다."
          ]
        ],
        "note": "교재 웹사이트는 안내서입니다. 실습 명령은 workshop 폴더의 터미널에서 실행합니다."
      }
    ]
  },
  "agent": {
    "title": "같은 문의, 다른 실행 방식",
    "hint": "정산 담당 팀을 묻는 상황입니다. 모델이 고르는 부분을 비교합니다.",
    "scenarios": [
      {
        "label": "단발 응답",
        "steps": [
          [
            "입력",
            "질문과 필요한 규정을 함께 제공합니다."
          ],
          [
            "모델",
            "제공된 내용으로 답변을 작성합니다."
          ],
          [
            "종료",
            "이 예시에는 외부 조회가 없습니다."
          ]
        ],
        "note": "필요한 자료가 이미 있다면 한 번의 응답으로 충분할 수 있습니다.",
        "decision": {
          "benefit": "구성과 확인이 단순합니다. 이 예시처럼 한 번 호출하면 여러 번 호출하는 흐름보다 지연·비용을 줄이기 쉽습니다.",
          "cost": "입력에 없는 규정을 스스로 조회하는 단계가 없습니다. 필요한 자료를 먼저 제공해야 합니다.",
          "fit": "자료가 이미 있고 요약·분류처럼 한 번에 끝낼 수 있는 업무"
        }
      },
      {
        "label": "고정 workflow",
        "steps": [
          [
            "코드",
            "질문이 오면 항상 규정을 조회합니다."
          ],
          [
            "조회 함수",
            "담당 팀과 규정을 반환합니다."
          ],
          [
            "모델",
            "반환된 규정을 문장으로 설명합니다."
          ]
        ],
        "note": "어느 단계로 갈지는 개발자가 정한 순서가 결정합니다.",
        "decision": {
          "benefit": "필수 조회나 승인 단계를 코드로 정해 실행 경로를 확인하기 쉽습니다.",
          "cost": "예외가 늘어나면 분기도 직접 관리해야 합니다. 정해 놓지 않은 상황에는 대응이 제한됩니다.",
          "fit": "정산 처리처럼 순서와 필수 조건이 명확한 업무"
        }
      },
      {
        "label": "ReAct 방식",
        "steps": [
          [
            "모델의 선택",
            "정산 규정을 조회할 도구를 고릅니다."
          ],
          [
            "프로그램 실행",
            "도구를 실행하고 결과를 모델에 돌려줍니다."
          ],
          [
            "다음 선택",
            "결과를 보고 추가 조회·질문·답변 중 선택합니다."
          ]
        ],
        "note": "마지막 답변만 비교하지 말고, 다음 행동을 누가 선택하는지 봅니다.",
        "decision": {
          "benefit": "결과를 보고 도구나 다음 행동을 바꿀 수 있어 경로를 미리 정하기 어려운 문제에 유연합니다.",
          "cost": "도구 선택을 잘못하거나 불필요하게 반복할 수 있습니다. 호출 비용·지연과 종료 조건을 관리해야 합니다.",
          "fit": "조사처럼 필요한 정보와 단계 수가 실행 중에 달라지는 업무"
        }
      }
    ]
  },
  "langchain": {
    "title": "내 코드가 모델의 답변으로 이어지는 과정",
    "hint": "조회 결과가 달라지면 답변에 사용할 근거도 달라집니다.",
    "scenarios": [
      {
        "label": "계정 문의",
        "steps": [
          [
            "모델 요청",
            "lookup_policy(topic=\"계정\")"
          ],
          [
            "내 조회 함수",
            "found=true · P-02 · IT지원팀"
          ],
          [
            "모델 응답",
            "조회한 팀과 정책 ID를 근거로 안내"
          ]
        ],
        "note": "예시 응답의 요약입니다. 실제 모델의 문장은 실행마다 달라질 수 있습니다."
      },
      {
        "label": "없는 업무",
        "steps": [
          [
            "모델 요청",
            "lookup_policy(topic=\"없는업무\")"
          ],
          [
            "내 조회 함수",
            "found=false · policy=null"
          ],
          [
            "기대하는 응답",
            "등록된 규정이 없으므로 추가 확인 안내"
          ]
        ],
        "note": "정책이 없다는 정상 조회 결과와 함수 실행 오류는 다릅니다."
      }
    ]
  },
  "graph": {
    "title": "입력을 바꾸면 어느 경로로 갈까요?",
    "hint": "아래 경로는 course/graph_lab.py의 기본 그래프를 읽어 구성했습니다.",
    "scenarios": [
      {
        "label": "정책·연락처 있음",
        "steps": [
          [
            "lookup",
            "정책 ID가 있고 회신 대상도 있습니다."
          ],
          [
            "draft · 선택된 경로",
            "답변 초안을 작성합니다."
          ],
          [
            "END",
            "이번 실행을 끝냅니다."
          ]
        ],
        "note": "경로: lookup → draft. 이 기본 예제에는 review 노드가 없습니다."
      },
      {
        "label": "연락처 없음",
        "steps": [
          [
            "lookup",
            "정책은 찾았지만 회신 대상이 없습니다."
          ],
          [
            "ask · 선택된 경로",
            "업무 주제와 회신 대상을 확인합니다."
          ],
          [
            "END",
            "질문을 남기고 이번 실행을 끝냅니다."
          ]
        ],
        "note": "경로: lookup → ask. draft는 실행하지 않습니다."
      },
      {
        "label": "정책 없음",
        "steps": [
          [
            "lookup",
            "찾은 정책 ID가 없습니다."
          ],
          [
            "ask · 선택된 경로",
            "추가 정보를 요청합니다."
          ],
          [
            "END",
            "근거 없는 초안을 만들지 않습니다."
          ]
        ],
        "note": "연락처가 있어도 정책이 없으면 ask로 갑니다. 직접 완성하기의 제공 그래프에는 별도로 review가 추가됩니다."
      }
    ]
  },
  "harness": {
    "title": "업무 Agent의 반복과 코딩 Agent의 반복",
    "hint": "두 반복은 작업 대상이 다릅니다. 무엇을 고치는지 봅니다.",
    "scenarios": [
      {
        "label": "업무 답변을 고침",
        "steps": [
          [
            "입력",
            "정책을 근거로 만든 답변 초안"
          ],
          [
            "검사",
            "팀명과 정책 ID가 있는지 확인"
          ],
          [
            "수정",
            "피드백으로 답변을 다시 작성"
          ],
          [
            "종료",
            "통과·변화 없음·수정 상한에서 종료"
          ]
        ],
        "note": "이 흐름은 제공된 refine_answer 예제의 범위를 요약합니다."
      },
      {
        "label": "Codex·Claude Code 활용",
        "steps": [
          [
            "작업 지시",
            "버그 재현 입력과 기대 결과를 전달"
          ],
          [
            "코드 수정",
            "코딩 Agent가 관련 파일을 변경"
          ],
          [
            "검사 결과 확인",
            "테스트 결과와 변경 내용을 비교"
          ],
          [
            "다음 결정",
            "재수정하거나 검토를 마치고 종료"
          ]
        ],
        "note": "제품 화면이 아닌 활용 절차의 설명용 도식입니다. 다음 작업 선정·권한·중단 기준을 어떻게 구성할지가 Harness·Loop 수업의 질문입니다."
      }
    ]
  },
  "mcp": {
    "title": "도구를 찾는 것과 실행하는 것은 다릅니다",
    "hint": "요청과 응답이 오가는 두 단계를 구분합니다.",
    "scenarios": [
      {
        "label": "1. 도구 목록",
        "steps": [
          [
            "클라이언트",
            "사용 가능한 도구 목록 요청"
          ],
          [
            "서버",
            "도구 이름·설명·입력 형식 반환"
          ],
          [
            "확인",
            "lookup_policy가 있음을 확인"
          ]
        ],
        "note": "목록을 받은 것만으로 정산 규정을 조회한 것은 아닙니다."
      },
      {
        "label": "2. 도구 실행",
        "steps": [
          [
            "클라이언트",
            "lookup_policy에 topic=정산 전달"
          ],
          [
            "서버의 함수",
            "정산 규정을 조회"
          ],
          [
            "반환 결과",
            "P-01과 재무지원팀을 응답에서 확인"
          ]
        ],
        "note": "이 단계의 결과를 Agent에 돌려주면 답변의 근거로 사용할 수 있습니다."
      }
    ]
  },
  "a2a": {
    "title": "늦게 온 통과 결과를 받아도 될까요?",
    "hint": "현재 초안은 v2입니다. 같은 요청에 대한 결과라고 가정합니다.",
    "scenarios": [
      {
        "label": "v1 결과가 늦게 도착",
        "steps": [
          [
            "현재 초안",
            "내용을 수정하여 v2가 됨"
          ],
          [
            "도착한 결과",
            "completed · version=1 · passed=true"
          ],
          [
            "우리 판단 · held",
            "현재 버전과 달라 보류"
          ]
        ],
        "note": "상대 작업은 끝났지만 v2의 검토 결과는 아닙니다."
      },
      {
        "label": "v2 검토 통과",
        "steps": [
          [
            "현재 초안",
            "검토를 요청한 v2"
          ],
          [
            "도착한 결과",
            "completed · version=2 · passed=true"
          ],
          [
            "우리 판단 · accepted",
            "요청 ID와 버전까지 일치하면 수용"
          ]
        ],
        "note": "completed뿐 아니라 요청 ID·버전·passed를 함께 확인합니다."
      },
      {
        "label": "아직 검토 중",
        "steps": [
          [
            "현재 초안",
            "검토를 요청한 v2"
          ],
          [
            "현재 상태",
            "working"
          ],
          [
            "우리 판단 · pending",
            "완료 결과를 기다림"
          ]
        ],
        "note": "작업이 시작됐다는 응답을 검토 통과로 처리하지 않습니다."
      }
    ]
  },
  "wrap": {
    "title": "하루 동안 연결한 부품 한눈에 보기",
    "hint": "직접 완성하기의 통합 실행 순서입니다.",
    "scenarios": [
      {
        "label": "통합 실행",
        "steps": [
          [
            "1 · 학생 MCP 도구",
            "업무 규정을 조회"
          ],
          [
            "2 · 제공 Graph + 학생 분기",
            "정보가 충분한지 판단"
          ],
          [
            "3 · 학생 LangChain Agent",
            "규정을 근거로 초안 작성"
          ],
          [
            "4 · 제공 수정 루프",
            "초안 검사와 제한된 수정"
          ],
          [
            "5 · 제공 A2A 서버",
            "원격 검토 결과 전달"
          ],
          [
            "6 · 학생 수용 함수",
            "요청·버전·통과 여부 확인"
          ]
        ],
        "note": "정보가 부족하면 2단계에서 질문하고 끝납니다. 이 그림은 정보가 충분한 경로이며 실제 메일을 보내지는 않습니다."
      }
    ]
  }
}
const lesson = computed(() => examples[props.kind])
const scene = computed(() => lesson.value.scenarios[selected.value] || lesson.value.scenarios[0])
</script>
<template>
  <figure v-if="lesson" class="course-visual" :id="'visual-' + kind">
    <figcaption><span>설명용 시각 자료 · 실제 실행 화면 아님</span><strong>{{ lesson.title }}</strong></figcaption>
    <p class="visual-hint">{{ lesson.hint }}</p>
    <div v-if="lesson.scenarios.length > 1" class="visual-choices" role="group" :aria-label="lesson.title + ' 조건 선택'">
      <button v-for="(item, i) in lesson.scenarios" :key="item.label" type="button" :aria-pressed="selected === i" @click="selected = i">{{ item.label }}</button>
    </div>
    <div aria-live="polite" aria-atomic="true">
      <ol class="visual-steps">
        <li v-for="(step, i) in scene.steps" :key="i"><span class="visual-number" aria-hidden="true">{{ i + 1 }}</span><div><strong>{{ step[0] }}</strong><p>{{ step[1] }}</p></div></li>
      </ol>
      <p class="visual-note">{{ scene.note }}</p>
      <dl v-if="scene.decision" class="choice-guide">
        <div><dt>장점</dt><dd>{{ scene.decision.benefit }}</dd></div>
        <div><dt>감수할 점</dt><dd>{{ scene.decision.cost }}</dd></div>
        <div><dt>이럴 때 선택</dt><dd>{{ scene.decision.fit }}</dd></div>
      </dl>
    </div>
  </figure>
</template>
