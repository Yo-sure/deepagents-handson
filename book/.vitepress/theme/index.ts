import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import ScrollProgress from './ScrollProgress.vue'
import Slides from './Slides.vue'
import Quiz from './Quiz.vue'
import ConceptGraph from './ConceptGraph.vue'
import './style.css'
import './concept.css'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'layout-top': () => h(ScrollProgress),
  }),
  enhanceApp({ app }) {
    app.component('Slides', Slides)
    app.component('Quiz', Quiz)
    app.component('ConceptGraph', ConceptGraph)

    // 입력 미리보기 갤러리 이미지를 클릭하면 전체화면으로 확대(의존성 없는 라이트박스).
    if (typeof window !== 'undefined') {
      const close = () => document.querySelector('.img-zoom-overlay')?.remove()
      document.addEventListener('click', (e) => {
        const t = e.target as HTMLElement
        if (t?.tagName === 'IMG' && t.closest('.inbox-gallery')) {
          const src = (t as HTMLImageElement).currentSrc || (t as HTMLImageElement).src
          const ov = document.createElement('div')
          ov.className = 'img-zoom-overlay'
          const big = document.createElement('img')
          big.src = src
          big.alt = (t as HTMLImageElement).alt || ''
          ov.appendChild(big)
          ov.addEventListener('click', close)
          document.body.appendChild(ov)
          requestAnimationFrame(() => ov.classList.add('open'))
        }
      })
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close() })

      // 실습 명령을 클릭=복사 칩으로. 명령처럼 생긴 인라인 <code>에 .cmd를 붙여 전 챕터 자동 적용.
      const CMD = /^(uv run |bash |python3? |npm |sudo |source |git clone)/
      const tagCmds = () => {
        document.querySelectorAll<HTMLElement>('.lec :not(pre) > code').forEach((c) => {
          if (!c.classList.contains('cmd') && CMD.test((c.textContent || '').trim())) {
            c.classList.add('cmd')
            c.setAttribute('title', '클릭하면 복사')
          }
        })
      }
      const copyText = (text: string) => {
        if (navigator.clipboard?.writeText) { navigator.clipboard.writeText(text); return }
        const ta = document.createElement('textarea')
        ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'
        document.body.appendChild(ta); ta.select()
        try { document.execCommand('copy') } catch {}
        ta.remove()
      }
      document.addEventListener('click', (e) => {
        const c = (e.target as HTMLElement)?.closest?.('code.cmd') as HTMLElement | null
        if (!c) return
        copyText((c.textContent || '').trim())
        c.classList.add('copied')
        setTimeout(() => c.classList.remove('copied'), 1200)
      })
      // 최초 + 라우트 전환(콘텐츠 교체) 때마다 재태깅. class 변경은 childList를 안 건드려 루프 없음.
      let re: ReturnType<typeof setTimeout>
      const obs = new MutationObserver(() => { clearTimeout(re); re = setTimeout(tagCmds, 60) })
      obs.observe(document.documentElement, { childList: true, subtree: true })
      setTimeout(tagCmds, 0)
    }
  },
}
