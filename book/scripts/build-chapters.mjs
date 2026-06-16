// books/md/Chapter N.md → book/chapters/<slug>.md (마이그레이션 완료분만 빌드 포함)
// 미완료 March 원고는 제외 — Obsidian 전용 문법이 빌드를 깨지 않도록.
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const SRC = resolve(__dirname, '../../books/md')
const DST = resolve(__dirname, '../chapters')

// 마이그레이션 완료된 챕터만 등록 (다음 사이클마다 추가)
const MIGRATED = [
  { file: 'Chapter 0. 환경 셋업.md', slug: 'chapter-0' },
  { file: 'Chapter 1. Kick-off & Agent 패러다임.md', slug: 'chapter-1' },
  { file: 'Chapter 2. LangChain LangGraph Agent와 Harness 구조.md', slug: 'chapter-2' },
  { file: 'Chapter 3. DeepAgents와 Harness 실습.md', slug: 'chapter-3' },
]

// Obsidian → VitePress 최소 전처리. (Ch1은 이미 VitePress-native라 대부분 no-op)
function preprocess(src) {
  let s = src
  // PDF 시대 시계 마커 제거: <p align="right"><sub ...>⏱ ...</sub></p>
  s = s.replace(/<p align="right">\s*<sub[^>]*>[^<]*<\/sub>\s*<\/p>\n?/g, '')
  // <mark style="..."> → <mark> (VitePress는 인라인 style 허용하나 통일)
  s = s.replace(/<mark\s+style="[^"]*">/g, '<mark>')
  return s
}

await mkdir(DST, { recursive: true })
for (const { file, slug } of MIGRATED) {
  const raw = await readFile(resolve(SRC, file), 'utf8')
  await writeFile(resolve(DST, `${slug}.md`), preprocess(raw), 'utf8')
  console.log(`[build-chapters] ${file} → chapters/${slug}.md`)
}
console.log(`[build-chapters] ${MIGRATED.length}개 챕터 빌드 포함`)
