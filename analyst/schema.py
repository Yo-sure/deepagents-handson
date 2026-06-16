"""인박스 리서치 애널리스트 — 데이터 계약 (RecordV1).

전 챕터(Ch1~6)가 공유하는 단일 레코드 스키마. 문서 한 장을 멀티모달로 읽어
이 구조로 정규화하면, 이후 단계(분류·조사·브리프·검증)는 파일 포맷이 아니라
이 계약에만 의존한다 → "부품은 갈아끼우고, 계약은 재사용".

직렬화 키는 한글(판매처·금액 …)로 나간다(classified/*.json 가독성). 코드에서
다루는 식별자는 영문이라 도구·LLM JSON 스키마와 호환된다(별칭 alias로 매핑).
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

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(alias="이름", description="항목 이름")
    amount: float | None = Field(default=None, alias="금액", description="항목 금액(원). 없으면 null")
    qty: float | None = Field(default=None, alias="수량", description="수량. 없으면 null")


class RecordV1(BaseModel):
    """문서 한 장의 정규화 레코드. 멀티모달 추출의 목표 출력."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    merchant: str = Field(alias="판매처", description="판매처/발행처 이름")
    total: float = Field(default=0.0, alias="금액", description="총액(원). 통화는 currency 필드. 리포트 등 금액 없으면 0")
    currency: str = Field(default="KRW", alias="통화", description="ISO 4217 통화코드")
    doc_date: date | None = Field(default=None, alias="날짜", description="거래/발행일(ISO yyyy-mm-dd). 못 읽으면 null")
    doc_type: DocType = Field(alias="문서유형", description="문서 유형")
    items: list[LineItem] = Field(default_factory=list, alias="항목", description="개별 항목 목록")
    confidence: float = Field(alias="신뢰도", ge=0.0, le=1.0, description="추출 신뢰도 0~1")
    source_path: str = Field(alias="원본경로", description="원본 파일 경로(sample_inbox 기준)")


def schema_json() -> str:
    """LLM structured output용 JSON 스키마(한글 키). Ch1~2에서 프롬프트에 끼운다."""
    import json

    return json.dumps(RecordV1.model_json_schema(by_alias=True), ensure_ascii=False, indent=2)
