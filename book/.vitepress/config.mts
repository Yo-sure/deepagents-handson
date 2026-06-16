import { withMermaid } from 'vitepress-plugin-mermaid'

// Obsidian 임베드 전처리: ![[images/x.png|320]] / ![[Pasted image ....png]] → 표준 이미지
function obsidianEmbeds(md: any) {
  md.core.ruler.before('normalize', 'obsidian_embeds', (state: any) => {
    state.src = state.src.replace(
      /!\[\[(?:[^\]|]*\/)?([^\]|/]+?\.(?:png|jpe?g|gif|svg|webp))(?:\|(\d+))?\]\]/gi,
      (_m: string, file: string, w?: string) => {
        const url = `/images/${file.trim()}`
        return w ? `<img src="${url}" width="${w}" alt="">` : `![](${url})`
      }
    )
    return true
  })
}

export default withMermaid({
  title: 'AI Agent 개발',
  description: '인박스 리서치 애널리스트를 만드는 8시간 핸즈온 — 2026 Edition',
  lang: 'ko-KR',
  cleanUrls: true,
  vite: { server: { port: 5174, strictPort: false } },
  markdown: { config: obsidianEmbeds, lineNumbers: true },
  themeConfig: {
    nav: [
      { text: '홈', link: '/' },
      { text: '교재', link: '/toc' },
      { text: '🎨 디자인', link: '/concept' },
    ],
    sidebar: [
      {
        text: '교재 (2026 Edition)',
        items: [
          { text: '소개', link: '/' },
          { text: 'Ch0 · 환경 셋업', link: '/chapters/chapter-0' },
          { text: 'Ch1 · Kick-off & Agent 패러다임', link: '/chapters/chapter-1' },
          { text: 'Ch2 · LangGraph 하네스', link: '/chapters/chapter-2' },
          { text: 'Ch3 · DeepAgents 하네스', link: '/chapters/chapter-3' },
          { text: 'Ch4 · Skills · MCP · 지식', link: '/chapters/chapter-4' },
          { text: 'Ch5 · A2A 역할 분리', link: '/chapters/chapter-5' },
          { text: 'Ch6 · 통합 캡스톤', link: '/chapters/chapter-6' },
        ],
      },
    ],
    search: { provider: 'local' },
    outline: { label: '목차', level: [2, 3] },
    darkModeSwitchLabel: '다크 모드',
    sidebarMenuLabel: '메뉴',
    returnToTopLabel: '맨 위로',
    docFooter: { prev: '이전', next: '다음' },
  },
})
