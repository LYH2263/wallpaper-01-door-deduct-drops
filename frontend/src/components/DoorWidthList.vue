<script setup>
import { computed } from 'vue'

const widths = defineModel({ type: Array, default: () => [] })

const total = computed(() =>
  widths.value.reduce((s, w) => (s + (typeof w === 'number' && isFinite(w) ? w : 0)), 0)
)
const hasInvalid = computed(() =>
  widths.value.some((w) => typeof w !== 'number' || !isFinite(w) || w < 0)
)

function add() {
  widths.value = [...widths.value, 0]
}
function remove(index) {
  widths.value = widths.value.filter((_, i) => i !== index)
}
function update(index, value) {
  widths.value = widths.value.map((w, i) => (i === index ? value : w))
}
</script>

<template>
  <div class="door-list">
    <div v-for="(w, i) in widths" :key="i" class="door-row">
      <input
        type="number"
        min="0"
        step="0.01"
        :value="w"
        @input="update(i, Number($event.target.value))"
      />
      <span>m</span>
      <button type="button" @click="remove(i)">删除</button>
      <span v-if="typeof w !== 'number' || !isFinite(w) || w < 0" class="warn">门宽需为非负数</span>
    </div>
    <button type="button" @click="add">添加门洞</button>
    <p>门洞合计 <strong>{{ total.toFixed(2) }}</strong> m
      <span v-if="hasInvalid" class="warn">（存在无效门宽）</span></p>
  </div>
</template>
