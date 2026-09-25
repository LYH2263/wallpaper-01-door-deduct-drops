<script setup>
const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])
function set(i, v) {
  const next = props.modelValue.slice()
  next[i] = Number.isFinite(v) ? v : 0
  emit('update:modelValue', next)
}
function add() { emit('update:modelValue', [...props.modelValue, 0.9]) }
function remove(i) { emit('update:modelValue', props.modelValue.filter((_, j) => j !== i)) }
</script>
<template>
  <div class="doors-editor">
    <span v-for="(d, i) in modelValue" :key="i" class="door-chip">
      门宽
      <input type="number" step="0.05" min="0" :value="d" @input="set(i, parseFloat($event.target.value))" />
      m
      <button type="button" @click="remove(i)">×</button>
    </span>
    <button type="button" @click="add">+ 门洞</button>
    <span v-if="modelValue.length" class="door-total">
      合计 {{ modelValue.reduce((a, b) => a + (b || 0), 0).toFixed(2) }} m
    </span>
    <span v-else class="door-total">无门洞</span>
  </div>
</template>
