<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DropStripBar from '../components/DropStripBar.vue'

const route = useRoute()
const demo = computed(() => ({
  drops: route.query.drops ? Number(route.query.drops) : 12,
  dropLen: route.query.dropLen ? Number(route.query.dropLen) : 2.7,
  rolls: route.query.rolls ? Number(route.query.rolls) : 4,
}))
</script>

<template>
  <div class="page">
    <h1>裁条预览</h1>
    <p v-if="!route.query.drops" class="hint">未选择测算结果，显示示例数据。</p>
    <DropStripBar v-bind="demo" />
  </div>
</template>
