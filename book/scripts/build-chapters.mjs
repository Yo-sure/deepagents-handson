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
  { file: 'Chapter 4. Skills와 MCP 연계.md', slug: 'chapter-4' },
  { file: 'Chapter 5. A2A로 역할 분리.md', slug: 'chapter-5' },
  { file: 'Chapter 6. 통합 Demo와 Wrap-up.md', slug: 'chapter-6' },
]

// Obsidian → VitePress 최소 전처리. (Ch1은 이미 VitePress-native라 대부분 no-op)
function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function codeImportLabel(spec) {
  const pathWithRegion = spec.replace(/\{[^}]*\}\s*$/, '').trim()
  const [file, region] = pathWithRegion.split('#')
  const repoPath = file.replace(/^(\.\.\/)+/, '').replace(/^\.\//, '')
  return region ? `${repoPath} #${region}` : repoPath
}

function preprocess(src) {
  let s = src
  // PDF 시대 시계 마커 제거: <p align="right"><sub ...>⏱ ...</sub></p>
  s = s.replace(/<p align="right">\s*<sub[^>]*>[^<]*<\/sub>\s*<\/p>\n?/g, '')
  // <mark style="..."> → <mark> (VitePress는 인라인 style 허용하나 통일)
  s = s.replace(/<mark\s+style="[^"]*">/g, '<mark>')
  // VitePress 코드 임베드(<<< ../../path.py#region{python})는 렌더 후 경로가 사라진다.
  // 학생이 "이 코드는 어느 파일인가"를 바로 보도록, 임베드 직전에 repo 상대 경로 라벨을 붙인다.
  s = s.replace(/^<<<\s+([^\n]+)$/gm, (line, spec) => {
    return `<div class="code-file-label"><span>${escapeHtml(codeImportLabel(spec))}</span></div>\n\n${line}`
  })
  return s
}

await mkdir(DST, { recursive: true })
for (const { file, slug } of MIGRATED) {
  const raw = await readFile(resolve(SRC, file), 'utf8')
  await writeFile(resolve(DST, `${slug}.md`), preprocess(raw), 'utf8')
  console.log(`[build-chapters] ${file} → chapters/${slug}.md`)
}
console.log(`[build-chapters] ${MIGRATED.length}개 챕터 빌드 포함`)

const workshopPages = ['start', 'agent', 'langchain', 'graph', 'harness', 'mcp', 'a2a', 'wrap', 'engineering', 'build']
const workshopDst = resolve(__dirname, '../workshop')
await mkdir(workshopDst, { recursive: true })
for (let i = 0; i < workshopPages.length; i++) {
  const slug = workshopPages[i]
  let raw = await readFile(resolve(__dirname, `../../books/workshop/${slug}.md`), 'utf8')
  const workbook = await readFile(resolve(__dirname, '../../books/workshop/build.md'), 'utf8')
  const engineering = await readFile(resolve(__dirname, '../../books/workshop/engineering.md'), 'utf8')
  raw = raw.replace(/<!-- lesson-exercise:([\w-]+) -->/g, (_, id) => {
    const match = workbook.match(new RegExp(`<section class="slide" id="${id}">([\\s\\S]*?)</section>`))
    if (!match) throw new Error(`Missing exercise ${id}`)
    return match[1].replace(/^## /gm, '### ').replace(/<p class="section-time">.*?<\/p>/g, '')
      .replace(/\[수업으로 돌아가기[^\n]+/g, '')
      .replace(/\]\(#/g, '](./build#')
  })
  raw = raw.replace(/<!-- lesson-engineering:([\w-]+) -->/g, (_, id) => {
    const match = engineering.match(new RegExp(`<section class="slide" id="${id}">([\\s\\S]*?)</section>`))
    if (!match) throw new Error(`Missing engineering ${id}`)
    return `<div id="engineering-${id}">` + match[1].replace(/^## /gm, '### ')
      .replace(/<p class="section-time">.*?<\/p>/g, '').replace(/\]\(#/g, '](#engineering-') + '</div>'
  })
  if (/uv run|python -m|--build-student/.test(raw)) {
    throw new Error(`Workshop ${slug}: use the embedded runtime or a Jupyter cell for execution`)
  }
  // Keep diagram measurements independent from the surrounding Korean prose styles.
  raw = raw.replace(/```mermaid\r?\n/g, '```mermaid\n%%{init: {"theme": "base", "htmlLabels": false, "flowchart": { "useMaxWidth": false, "padding": 16, "rankSpacing": 36, "curve": "linear"}, "sequence": {"useMaxWidth": false, "wrap": true}, "themeVariables": {"fontSize": "17px", "fontFamily": "Segoe UI, Malgun Gothic, sans-serif", "primaryColor": "#f2f6f4", "primaryBorderColor": "#718b80", "primaryTextColor": "#25312e"}}}%%\n')
  const links = [i > 0 ? `<a href="./${workshopPages[i - 1]}">이전 모듈</a>` : '', '<a href="../toc">전체 목차</a>', i < workshopPages.length - 1 ? `<a href="./${workshopPages[i + 1]}">${workshopPages[i + 1] === 'engineering' ? '설계 확장' : '다음 모듈'}</a>` : ''].filter(Boolean)
  raw = raw.replace('<nav class="chapnav"><a href="../toc">전체 목차</a></nav>', `<nav class="chapnav">${links.join(' · ')}</nav>`)
  await writeFile(resolve(workshopDst, `${slug}.md`), preprocess(raw), 'utf8')
}

await mkdir(resolve(__dirname, '../public'), { recursive: true })
await writeFile(resolve(__dirname, '../public/python-worker.js'), await readFile(resolve(__dirname, '../.vitepress/theme/python-worker.js'), 'utf8'))
