"""인박스 리서치 애널리스트 — 공유 데이터 계약.

전 챕터가 import하는 단일 진실:
    from analyst.schema import RecordV1, DocType, LineItem
    from analyst import paths
"""

from analyst import paths
from analyst.schema import SCHEMA_VERSION, DocType, LineItem, RecordV1

__all__ = ["RecordV1", "DocType", "LineItem", "SCHEMA_VERSION", "paths"]
