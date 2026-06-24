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
  // GitHub Pages 프로젝트 페이지: https://yo-sure.github.io/deepagents-handson/
  base: '/deepagents-handson/',
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: '/deepagents-handson/favicon.svg' }]],
  cleanUrls: true,
  // .lec은 의도된 라이트 에디토리얼(크림 페이퍼) 디자인 — 다크 토큰셋이 없어
  // 토글을 두면 본문은 그대로인 '반쪽 어둠'이 된다. 토글 자체를 제거해 일관성 확보.
  appearance: false,
  vite: {
    server: { port: 5174, strictPort: false, allowedHosts: true },
    preview: { port: 5174, host: true, allowedHosts: true },
  },
  markdown: { config: obsidianEmbeds, lineNumbers: true },
  mermaid: {
    theme: 'base',
    themeVariables: {
      fontFamily: 'inherit',
      fontSize: '15px',
      primaryTextColor: '#1b2a3a',
      nodeTextColor: '#1b2a3a',
      lineColor: '#6b7a72',
      edgeLabelBackground: '#ffffff',
      // xychart(막대·꺾은선) 팔레트 — 기본 크림색(#FFF4DD)은 연배경에서 대비가 낮아
      // 얇은 선이 폰에서 사라진다. .lec 청록 팔레트로 채도를 올려 폰 가독 확보.
      xyChart: {
        plotColorPalette: '#0d9488, #d97706, #6b4fa3',
        backgroundColor: '#eef3f1',
        titleColor: '#1b2a3a',
        xAxisLabelColor: '#1b2a3a',
        yAxisLabelColor: '#1b2a3a',
        xAxisTitleColor: '#1b2a3a',
        yAxisTitleColor: '#1b2a3a',
      },
    },
  },
  themeConfig: {
    nav: [
      { text: '홈', link: '/' },
      { text: '교재', link: '/toc' },
      { text: 'GitHub', link: 'https://github.com/Yo-sure/deepagents-handson' },
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
