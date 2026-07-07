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
    }
  },
}
