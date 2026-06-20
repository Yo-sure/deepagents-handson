# analyst — 공유 데이터 계약

인박스 리서치 애널리스트의 **척추**. 전 챕터(Ch1~6)가 이 패키지 하나를 import해
같은 레코드 구조와 같은 디렉터리 규약 위에서 모듈을 만든다. 챕터 코드는 파일 포맷이
아니라 이 계약에만 의존하므로, 한 챕터의 산출물이 다음 챕터의 입력으로 그대로 흐른다.

```python
from analyst.schema import RecordV1, DocType, LineItem
from analyst import paths
```

## RecordV1 — 문서 한 장의 정규화 레코드

멀티모달 추출(영수증·명세서·계약·리포트 → 구조화)의 목표 출력. 코드 식별자는 영문,
직렬화 키는 한글이다(`classified/*.json` 가독성). 별칭으로 두 표현이 매핑된다.

| 필드(코드) | JSON 키 | 타입 | 설명 |
|---|---|---|---|
| `merchant` | 판매처 | str | 판매처/발행처 |
| `total` | 금액 | float | 총액(원). 리포트 등 금액 없으면 0 |
| `currency` | 통화 | str | ISO 4217 (기본 KRW) |
| `doc_date` | 날짜 | date \| None | 거래/발행일(ISO). 못 읽으면 null |
| `doc_type` | 문서유형 | DocType | 영수증 / 명세서 / 계약서 / 리포트 / 기타 |
| `items` | 항목 | list[LineItem] | 개별 항목(`이름`·`금액`·`수량`) |
| `confidence` | 신뢰도 | float | 추출 신뢰도 0~1 (모델 산출) |
| `source_path` | 원본경로 | str | 원본 파일 경로 |

```python
# LLM이 한글 키 JSON으로 답하면 그대로 파싱
r = RecordV1.model_validate(llm_json)
# classified/ 로 떨굴 때 한글 키로 직렬화
r.model_dump(by_alias=True, mode="json")
```

## 파이프라인 경로 (`analyst.paths`)

```
sample_inbox/  →  classified/  →  research_notes/  →  brief.md  →  verified_brief.md
   (입력)          (Ch2)            (Ch3)              (Ch4)        (Ch5)
```

입력 `sample_inbox/`만 저장소에 포함된다. 학생이 만드는 산출물은 모두 `workspace/`
아래에 떨어지며 git에 올라가지 않는다(`paths.ensure_workspace()`로 생성). `ANALYST_WORKSPACE`
환경변수로 위치를 바꿀 수 있다.

## sample_inbox — 멀티모달 입력 10건

5월 한 사람의 인박스(이미지 6 + PDF 4). **상호 참조**되도록 설계됨 — 카드명세서의
거래줄이 개별 영수증과 금액이 맞고, 은행명세서가 용역계약·세금계산서와 이어진다.
그래서 Ch3 fan-out 교차분석이 "명세서엔 있는데 영수증이 없는 89,000원"처럼 실제
조사거리를 갖는다.

| 파일 | 유형 | 형식 |
|---|---|---|
| receipt_starbucks · gs25 · taxi · restaurant · oliveyoung | 영수증 | png |
| invoice_photo | 명세서(세금계산서, 사진풍) | png |
| statement_card_2026-05 | 명세서(카드) | pdf |
| statement_bank_2026-05 | 명세서(은행) | pdf |
| contract_freelance | 계약서 | pdf |
| report_market | 리포트 | pdf |

`sample_inbox/_manifest.yaml`은 각 문서의 **정답(gold)** 이다 — 추출이 재현해야 할 값.
챕터에서 자기 추출 결과를 채점하는 기준으로 쓴다.

## 계약 자체검증

```bash
uv run python -m analyst.tests.test_contract
```
gold가 전부 RecordV1을 통과하는지, 금액=항목합인지, 카드명세서↔영수증이 일치하는지 확인한다.
