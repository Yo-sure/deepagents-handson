"""인박스 리서치 애널리스트 — 공유 데이터 계약.

전 챕터가 import하는 단일 진실:
    from analyst.schema import RecordV1, DocType, LineItem
    from analyst import paths
"""

# 레포-로컬 .env를 한 번 로드한다. uv run은 .env를 자동 로드하지 않으므로,
# analyst를 import하는 모든 챕터 코드가 이 한 줄로 OPENROUTER_API_KEY 등을 환경에 올린다.
from dotenv import load_dotenv

load_dotenv()

from analyst import paths
from analyst.schema import SCHEMA_VERSION, DocType, LineItem, RecordV1

__all__ = ["RecordV1", "DocType", "LineItem", "SCHEMA_VERSION", "paths"]
