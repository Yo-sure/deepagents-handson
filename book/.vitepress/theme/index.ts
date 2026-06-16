import DefaultTheme from 'vitepress/theme'
import Slides from './Slides.vue'
import Quiz from './Quiz.vue'
import ConceptGraph from './ConceptGraph.vue'
import './style.css'
import './concept.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('Slides', Slides)
    app.component('Quiz', Quiz)
    app.component('ConceptGraph', ConceptGraph)
  },
}
