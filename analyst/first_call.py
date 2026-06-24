"""Ch0 Step 3 — 학생이 직접 보는 첫 LLM 호출.

키·경로·모델 라우팅이 제대로 잡혔는지 30초 안에 확인한다.
실행: uv run python3 analyst/first_call.py
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from pathlib import Path

load_dotenv(Path.cwd() / ".env")     # 레포 루트에서 실행한다고 못 박는다

llm = ChatOpenAI(
    model="google/gemini-3.1-flash-lite",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0,
    max_tokens=64,
    timeout=30,
    max_retries=1,
)
resp = llm.invoke("한 문장으로 자기소개 해줘")
print(resp.content)
print("→ model:", resp.response_metadata.get("model_name"))   # 실제 라우팅된 모델 확인
