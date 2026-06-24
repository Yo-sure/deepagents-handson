---
name: inbox-brief
description: 분류된 인박스 레코드와 OKF 지식·조사 노트를 모아 월간 브리프(brief.md)를 작성한다. 사용자가 "이번 달 인박스 정리", "지출 브리프", "월간 요약"을 요청할 때 쓴다.
license: MIT
allowed-tools: read_file write_file ls
metadata:
  version: 0.2.0
  author: deepagents-handson
---

# 인박스 브리프 작성

분석가의 마지막 산출물은 사람이 30초 안에 읽는 한 장짜리 브리프다. 흩어진 레코드와
노트를 정해진 형식으로 묶는다.

## 입력
- `workspace/classified/*.json` — 정규화된 문서 레코드(RecordV1)
- `workspace/knowledge_base/*.md` — OKF 지식 항목(merchant·subscription·gap)
- `workspace/research_notes/*.md` — fan-out 조사 노트

## 절차
1. `ls workspace/classified`, `ls workspace/knowledge_base`, `ls workspace/research_notes`로 입력 파일명을 확인한다.
2. classified 레코드를 읽어 영수증 지출 합계와 카테고리를 집계한다.
3. knowledge_base에서 `type: gap`·`type: subscription` 항목만 읽어 모은다 — 이게 "짚을 점".
   `title`(또는 호환 필드 `name`)과 `amount`를 반드시 함께 가져온다.
4. 필요하면 `workspace/research_notes/card_reconcile.md`, `bank_reconcile.md`, `spend_summary.md`를 근거로 확인한다.
5. 아래 형식으로 `workspace/brief.md`를 쓴다. 한 화면을 넘기지 않는다.
6. 숫자는 반드시 레코드나 OKF 머리말에서 가져온다. 지어내지 않는다. 근거가 없으면 "확인 필요"로 남긴다.

## 도구 사용 규칙
- `glob`·`grep`으로 전체 workspace를 뒤지지 않는다. `ls`로 파일명을 보고 필요한 파일만 `read_file`한다.
- 읽는 범위는 `workspace/classified/*.json`, `workspace/knowledge_base/*.md`,
  `workspace/research_notes/*.md`, 그리고 필요할 때 `references/brief_format.md`로 제한한다.
- 마지막에는 반드시 `write_file`로 `workspace/brief.md`를 쓴다.

## 출력 형식
세부 형식과 예시는 `references/brief_format.md`를 따른다(필요할 때만 읽는다 — 점진 공개).

## 톤
담백하게 쓴다. 과장·이모지 남발·마케팅 어조를 피한다. 짚을 점은 사실과 금액으로 적는다.
