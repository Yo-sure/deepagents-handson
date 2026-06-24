"""인박스 리서치 애널리스트 — 데이터 계약 (RecordV1).

전 챕터(Ch1~6)가 공유하는 단일 레코드 스키마. 문서 한 장을 멀티모달로 읽어
이 구조로 정규화하면, 이후 단계(분류·조사·브리프·검증)는 파일 포맷이 아니라
이 계약에만 의존한다 → 계약을 지키면 모듈을 교체할 수 있다.

현지화는 출력 경계 한 곳에만 둔다. 코드·LLM 추출 스키마는 영문 식별자(merchant·
total …)로 깨끗하게 두고, 사람이 읽는 산출물(classified/*.json)을 저장할 때만
alias로 한글(판매처·총액 …)로 변형한다 — 즉 추출은 영문, 한글은 추출 후 변형이다.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0"


class DocType(str, Enum):
    """문서 유형. 값은 분류 결과 JSON에 그대로 기록된다."""

    receipt = "영수증"
    statement = "명세서"
    contract = "계약서"
    report = "리포트"
    other = "기타"


class LineItem(BaseModel):
    """문서 안의 개별 항목(영수증 품목, 명세서 거래줄 등)."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    name: str = Field(alias="이름", description="항목 이름")
    amount: float | None = Field(default=None, alias="단가", description="항목 1개 단가(원). 라인 총액이 아님. 없으면 null")
    qty: float | None = Field(default=None, alias="수량", description="수량. 없으면 null")


class RecordV1(BaseModel):
    """문서 한 장의 정규화 레코드. 멀티모달 추출의 목표 출력."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, extra="forbid")

    merchant: str = Field(alias="판매처", description="판매처/발행처 이름")
    total: float = Field(alias="총액", description="총액(원). 통화는 currency 필드. 리포트 등 금액 없으면 0을 명시")
    currency: str = Field(default="KRW", alias="통화", description="ISO 4217 통화코드")
    doc_date: date | None = Field(default=None, alias="날짜", description="거래/발행일(ISO yyyy-mm-dd). 못 읽으면 null")
    doc_type: DocType = Field(alias="문서유형", description="문서 유형")
    items: list[LineItem] = Field(alias="항목", description="개별 항목 목록. 항목이 없으면 []를 명시")
    confidence: float = Field(alias="신뢰도", ge=0.0, le=1.0, description="추출 신뢰도 0~1")
    source_path: str = Field(alias="원본경로", description="원본 파일 경로(sample_inbox 기준)")


def schema_json() -> str:
    """프롬프트 삽입용 JSON Schema(영문 키). LLM 추출 계약은 영문이다.

    한글은 추출이 아니라 저장(model_dump(by_alias=True))에서만 입혀진다.
    """
    import json

    return json.dumps(RecordV1.model_json_schema(by_alias=False), ensure_ascii=False, indent=2)
