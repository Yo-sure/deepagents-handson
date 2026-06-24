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
  },
}
