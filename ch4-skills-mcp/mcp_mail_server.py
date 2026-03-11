"""
Chapter 4 - MCP 메일 서버: MCP(Model Context Protocol)로 메일 API 연결

MCP 서버는 Agent가 외부 데이터에 접근할 수 있도록 표준화된 인터페이스를 제공합니다.
이 파일은 메일 시스템에 대한 MCP 서버를 구현합니다.

핵심 개념:
  - FastMCP: MCP 서버를 간결하게 만드는 고수준 API
  - @mcp.tool(): 함수를 MCP Tool로 등록하는 데코레이터
  - stdio transport: 표준 입출력을 통한 통신 (가장 간단한 방식)

실제 환경에서는 IMAP/SMTP로 메일 서버에 연결하지만,
학습 목적으로 Mock 데이터를 사용합니다.

실행 방법:
  python3 mcp_mail_server.py

  (단독 실행 시 stdio로 대기하며, Agent가 subprocess로 연결합니다)

필요 패키지:
  pip install "mcp[cli]"
"""

import json
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

# ============================================================
# 1. Mock 메일 데이터
# ============================================================
# 실제로는 IMAP 서버에서 가져오지만, 학습을 위해 하드코딩된 데이터를 사용합니다.
# 이 데이터가 MCP Tool을 통해 Agent에게 전달됩니다.

MOCK_EMAILS = [
    {
        "id": 1,
        "from": "김팀장 <teamlead@company.com>",
        "to": "me@company.com",
        "subject": "긴급: 서버 점검 안내",
        "body": (
            "내일(2월 23일) 오후 2시부터 4시까지 서버 점검이 예정되어 있습니다.\n"
            "작업 중인 내용을 반드시 저장해주세요.\n"
            "점검 중에는 사내 시스템 접속이 불가합니다."
        ),
        "date": (datetime.now() - timedelta(hours=1)).isoformat(),
        "read": False,
        "important": True,
        "labels": ["업무", "긴급"],
    },
    {
        "id": 2,
        "from": "HR팀 <hr@company.com>",
        "to": "all@company.com",
        "subject": "연말 워크숍 일정 안내",
        "body": (
            "12월 20일(금) 연말 워크숍이 진행됩니다.\n"
            "장소: 서울 강남 컨퍼런스홀\n"
            "참석 여부를 12월 15일까지 회신해주세요."
        ),
        "date": (datetime.now() - timedelta(hours=3)).isoformat(),
        "read": False,
        "important": False,
        "labels": ["전사공지"],
    },
    {
        "id": 3,
        "from": "박대리 <park@client.com>",
        "to": "me@company.com",
        "subject": "프로젝트 미팅 요청",
        "body": (
            "다음 주 화요일(2월 25일) 오전 10시에\n"
            "프로젝트 진행 상황 공유 미팅을 요청드립니다.\n"
            "장소: 고객사 회의실 또는 온라인\n"
            "안건: Q1 마일스톤 리뷰, 이슈 논의"
        ),
        "date": (datetime.now() - timedelta(hours=5)).isoformat(),
        "read": False,
        "important": True,
        "labels": ["고객사", "미팅"],
    },
    {
        "id": 4,
        "from": "DevOps Bot <noreply@ci.company.com>",
        "to": "dev-team@company.com",
        "subject": "[CI/CD] 빌드 #1247 성공",
        "body": (
            "main 브랜치 빌드가 성공적으로 완료되었습니다.\n"
            "커밋: abc1234 - feat: 사용자 프로필 API 추가\n"
            "배포 대상: staging 환경"
        ),
        "date": (datetime.now() - timedelta(hours=8)).isoformat(),
        "read": True,
        "important": False,
        "labels": ["자동알림"],
    },
    {
        "id": 5,
        "from": "이부장 <director@company.com>",
        "to": "me@company.com",
        "subject": "ASAP: 고객 보고서 검토 요청",
        "body": (
            "첨부된 고객 보고서를 오늘 중으로 검토해주세요.\n"
            "내일 오전 고객사 미팅 전에 최종본이 필요합니다.\n"
            "수정 사항이 있으면 오후 6시까지 회신 바랍니다."
        ),
        "date": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "read": False,
        "important": True,
        "labels": ["업무", "긴급"],
    },
]

# ============================================================
# 2. FastMCP 서버 생성
# ============================================================
# FastMCP는 MCP Python SDK의 고수준 API입니다.
# @mcp.tool() 데코레이터로 Tool을 간결하게 등록할 수 있습니다.
# (저수준 Server API는 @server.list_tools() + @server.call_tool()로 별도 라우팅이 필요합니다.)

mcp = FastMCP("mail-mcp-server")

# ============================================================
# 3. MCP Tool 정의
# ============================================================
# @mcp.tool() 데코레이터로 함수를 MCP Tool로 등록합니다.
# - 함수 이름이 Tool 이름이 됩니다.
# - docstring이 Tool 설명이 됩니다 (LLM이 이것을 보고 호출 여부를 결정).
# - 파라미터 타입 힌트가 Tool의 입력 스키마가 됩니다.
# - FastMCP에서는 str을 반환하면 자동으로 TextContent로 변환됩니다.


@mcp.tool()
async def check_inbox(filter: str = "unread") -> str:
    """메일함의 메일 목록을 확인합니다.

    사용 가능한 필터:
      - "unread": 읽지 않은 메일만 (기본값)
      - "important": 중요 메일만
      - "all": 모든 메일

    Args:
        filter: 메일 필터 조건
    """
    # 필터 조건에 따라 메일 목록을 필터링합니다
    if filter == "important":
        filtered = [e for e in MOCK_EMAILS if e["important"]]
    elif filter == "unread":
        filtered = [e for e in MOCK_EMAILS if not e["read"]]
    elif filter == "all":
        filtered = MOCK_EMAILS
    else:
        filtered = MOCK_EMAILS

    # 결과를 읽기 좋은 텍스트로 포맷팅합니다
    lines = [f"=== 메일함 ({filter}) - {len(filtered)}통 ===\n"]
    for email in filtered:
        # 중요 메일은 표시를 붙입니다
        importance_mark = "[중요] " if email["important"] else ""
        read_mark = "" if email["read"] else "[미읽음] "
        lines.append(
            f"  ID:{email['id']} | {read_mark}{importance_mark}"
            f"{email['from']} - {email['subject']}"
        )
        lines.append(f"         날짜: {email['date']}")
        lines.append(f"         라벨: {', '.join(email['labels'])}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_email_detail(email_id: int) -> str:
    """특정 메일의 상세 내용을 반환합니다.

    메일 ID를 지정하면 해당 메일의 전체 내용(발신자, 수신자, 제목, 본문 등)을
    반환합니다. check_inbox로 먼저 메일 목록을 확인한 후 사용하세요.

    Args:
        email_id: 조회할 메일의 ID 번호
    """
    # ID로 메일을 찾습니다
    email = None
    for e in MOCK_EMAILS:
        if e["id"] == email_id:
            email = e
            break

    if email is None:
        return f"오류: ID {email_id}에 해당하는 메일을 찾을 수 없습니다."

    # 상세 정보를 포맷팅합니다
    return (
        f"=== 메일 상세 (ID: {email['id']}) ===\n"
        f"발신자 : {email['from']}\n"
        f"수신자 : {email['to']}\n"
        f"제목   : {email['subject']}\n"
        f"날짜   : {email['date']}\n"
        f"라벨   : {', '.join(email['labels'])}\n"
        f"중요   : {'예' if email['important'] else '아니오'}\n"
        f"읽음   : {'예' if email['read'] else '아니오'}\n"
        f"\n--- 본문 ---\n"
        f"{email['body']}\n"
        f"--- 끝 ---"
    )


@mcp.tool()
async def search_emails(query: str) -> str:
    """메일을 키워드로 검색합니다.

    발신자, 제목, 본문에서 키워드를 검색하여 일치하는 메일 목록을 반환합니다.
    대소문자를 구분하지 않습니다.

    Args:
        query: 검색할 키워드 (발신자, 제목, 본문에서 검색)
    """
    query_lower = query.lower()

    # 발신자, 제목, 본문에서 키워드를 검색합니다
    results = []
    for email in MOCK_EMAILS:
        searchable = (
            email["from"].lower()
            + email["subject"].lower()
            + email["body"].lower()
        )
        if query_lower in searchable:
            results.append(email)

    if not results:
        return (
            f"'{query}' 검색 결과: 일치하는 메일이 없습니다.\n"
            f"다른 키워드로 시도해보세요."
        )

    # 검색 결과 포맷팅
    lines = [f"=== '{query}' 검색 결과 - {len(results)}건 ===\n"]
    for email in results:
        importance_mark = "[중요] " if email["important"] else ""
        lines.append(
            f"  ID:{email['id']} | {importance_mark}"
            f"{email['from']} - {email['subject']}"
        )
        # 본문에서 키워드가 포함된 부분을 미리보기로 보여줍니다
        body_lower = email["body"].lower()
        idx = body_lower.find(query_lower)
        if idx >= 0:
            start = max(0, idx - 20)
            end = min(len(email["body"]), idx + len(query) + 40)
            snippet = email["body"][start:end].replace("\n", " ")
            lines.append(f"         미리보기: ...{snippet}...")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# 4. Resource 정의 (참고용 — Tool과 별개의 MCP Primitive)
# ============================================================
# Resource는 클라이언트 앱이 컨텍스트로 주입하는 읽기 전용 데이터입니다.
# Tool과 달리 AI 모델이 직접 호출하지 않고, 클라이언트가 필요할 때 읽어갑니다.
# URI 템플릿의 {param}은 함수 인자로 매핑됩니다.


@mcp.resource("mail://inbox/stats")
def inbox_stats() -> str:
    """메일함 통계를 반환합니다 (읽기 전용 데이터)."""
    total = len(MOCK_EMAILS)
    unread = sum(1 for e in MOCK_EMAILS if not e["read"])
    important = sum(1 for e in MOCK_EMAILS if e["important"])
    return json.dumps({
        "total": total,
        "unread": unread,
        "important": important,
    }, ensure_ascii=False)


@mcp.resource("mail://email/{email_id}")
def email_resource(email_id: int) -> str:
    """특정 메일의 메타데이터를 반환합니다 (읽기 전용)."""
    for e in MOCK_EMAILS:
        if e["id"] == email_id:
            return json.dumps({
                "id": e["id"],
                "from": e["from"],
                "subject": e["subject"],
                "labels": e["labels"],
            }, ensure_ascii=False)
    return json.dumps({"error": f"ID {email_id} not found"})


# ============================================================
# 5. Prompt 정의 (참고용 — 사용자가 트리거하는 LLM 템플릿)
# ============================================================
# Prompt는 사용자가 슬래시 커맨드 등으로 직접 트리거하는 템플릿입니다.
# 클라이언트 UI에서 "/mail-summary" 같은 형태로 노출됩니다.


@mcp.prompt()
def mail_summary(filter: str = "important") -> str:
    """메일 요약 요청 프롬프트를 생성합니다."""
    return (
        f"메일함에서 {filter} 메일을 확인하고, "
        "각 메일의 핵심 내용을 3줄 이내로 요약해주세요. "
        "긴급한 메일이 있으면 먼저 표시해주세요."
    )


# ============================================================
# 6. 서버 실행 (stdio transport)
# ============================================================
# MCP는 여러 transport를 지원합니다:
#   - stdio: 표준 입출력 (subprocess로 연결, 가장 간단)
#   - SSE: Server-Sent Events (HTTP 기반, 원격 연결)
#   - Streamable HTTP: HTTP 스트리밍 (최신 방식)
#
# FastMCP의 mcp.run()은 기본적으로 stdio transport를 사용합니다.
# Agent가 이 스크립트를 subprocess로 실행하면,
# stdin/stdout을 통해 JSON-RPC 메시지를 주고받습니다.
#
# [Agent Process] <-- stdin/stdout --> [이 MCP Server Process]

if __name__ == "__main__":
    mcp.run()  # stdio transport (기본값)


# ============================================================
# 핵심 정리
# ============================================================
#
# MCP 3가지 Primitive:
#   - Tool (@mcp.tool): AI가 자율 호출, 부수 효과 가능
#   - Resource (@mcp.resource): 클라이언트가 읽기 전용 데이터 주입
#   - Prompt (@mcp.prompt): 사용자가 슬래시 커맨드로 트리거
#
# 프로토콜: JSON-RPC 2.0 (tools/list, tools/call 등)
# Transport: stdio (로컬), Streamable HTTP (프로덕션 권장)
#
# FastMCP 데코레이터 규칙:
#   - 함수 이름 -> Tool/Resource/Prompt 이름
#   - docstring -> 설명 (LLM이 참고)
#   - 타입 힌트 -> 입력 스키마 (자동 생성)
#   - str 반환 -> 자동으로 TextContent 변환
