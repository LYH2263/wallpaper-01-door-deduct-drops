<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template>
  <div class="page"><h1>记录</h1>
  <ul>
    <li v-for="r in items" :key="r.id">
      <router-link :to="`/history/${r.id}`">#{{ r.id }}</router-link>
      {{ r.wall_name }} → {{ r.result?.rolls }} 卷 · {{ r.result?.drops }} 条
      <template v-if="r.result?.door_widths?.length">
        （门宽合计 {{ r.result.doors_total_m }}m → 有效周长 {{ r.result.effective_perimeter_m }}m）
      </template>
    </li>
  </ul></div>
</template>
