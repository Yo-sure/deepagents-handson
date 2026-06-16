<script setup>
import { computed } from 'vue'
const props = defineProps({
  title: { type: String, default: '' },
  nodes: { type: Array, required: true }, // { id, label, sub, type, x, y }
  edges: { type: Array, default: () => [] }, // { from, to, label }
  width: { type: Number, default: 1000 },
  height: { type: Number, default: 600 },
})
const NW = 178, NH = 70, HUBW = 210, HUBH = 92
const sizeOf = (n) => (n.type === 'hub' ? { w: HUBW, h: HUBH } : { w: NW, h: NH })
const byId = computed(() => Object.fromEntries(props.nodes.map((n) => [n.id, n])))
const laidEdges = computed(() => props.edges.map((e) => {
  const a = byId.value[e.from], b = byId.value[e.to]
  if (!a || !b) return null
  return { ...e, x1: a.x, y1: a.y, x2: b.x, y2: b.y, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 }
}).filter(Boolean))
const laidNodes = computed(() => props.nodes.map((n) => {
  const { w, h } = sizeOf(n); return { ...n, w, h, bx: n.x - w / 2, by: n.y - h / 2 }
}))
</script>

<template>
  <figure class="cg">
    <figcaption v-if="title" class="cg-cap">{{ title }}</figcaption>
    <svg :viewBox="`0 0 ${width} ${height}`" class="cg-svg" role="img">
      <g class="cg-edges">
        <line v-for="(e, i) in laidEdges" :key="'l' + i" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" class="cg-line" />
      </g>
      <foreignObject v-for="(e, i) in laidEdges" :key="'el' + i" :x="e.mx - 75" :y="e.my - 15" width="150" height="30">
        <div class="cg-elabel"><span>{{ e.label }}</span></div>
      </foreignObject>
      <foreignObject v-for="n in laidNodes" :key="n.id" :x="n.bx" :y="n.by" :width="n.w" :height="n.h">
        <div class="cg-node" :class="n.type"><strong>{{ n.label }}</strong><span v-if="n.sub">{{ n.sub }}</span></div>
      </foreignObject>
    </svg>
  </figure>
</template>

<style scoped>
.cg { margin: 24px 0; padding: 18px; background: #fffdf7; border: 1px solid #d9cdb9; border-radius: 8px; box-shadow: 0 24px 80px rgba(27,31,29,.12); }
.cg-cap { font-weight: 900; font-size: 14px; color: #0b3b35; margin: 2px 4px 10px; }
.cg-svg { width: 100%; height: auto; display: block; overflow: visible; }
.cg-line { stroke: #b9ad97; stroke-width: 2; stroke-dasharray: 4 5; }
.cg-elabel { display: grid; place-items: center; height: 100%; }
.cg-elabel span { font-size: 11px; font-weight: 800; color: #5b524a; background: #f6f1e7; border: 1px solid #d9cdb9; border-radius: 999px; padding: 3px 9px; white-space: nowrap; }
.cg-node { height: 100%; display: grid; align-content: center; gap: 3px; padding: 8px 12px; border-radius: 9px; text-align: center; background: #f8fbff; border: 2px solid rgba(49,95,156,.34); }
.cg-node strong { font-size: 14px; color: #18201f; line-height: 1.15; }
.cg-node span { font-size: 11px; color: #66706b; line-height: 1.3; }
.cg-node.hub { color: #fffdf7; background: linear-gradient(135deg, rgba(11,59,53,.98), rgba(15,118,110,.95)); border-color: rgba(255,253,247,.25); box-shadow: 0 16px 40px rgba(11,59,53,.3); }
.cg-node.hub strong { color: #fffdf7; font-family: Georgia, serif; font-size: 22px; }
.cg-node.hub span { color: rgba(255,253,247,.8); }
.cg-node.skill { background:#eafaf4; border-color: rgba(15,118,110,.4); } .cg-node.skill strong { color:#0f766e; }
.cg-node.tool { background:#f0f5fc; border-color: rgba(49,95,156,.4); } .cg-node.tool strong { color:#315f9c; }
.cg-node.knowledge { background:#fdf4e3; border-color: rgba(224,159,62,.5); } .cg-node.knowledge strong { color:#8a5a12; }
.cg-node.memory { background:#f4f0fa; border-color: rgba(107,79,163,.42); } .cg-node.memory strong { color:#6b4fa3; }
.cg-node.user { background:#fbeeee; border-color: rgba(166,61,64,.4); } .cg-node.user strong { color:#a63d40; }
.cg-node.llm { background:#eef7f1; border-color: rgba(11,59,53,.4); } .cg-node.llm strong { color:#0b3b35; }
</style>
