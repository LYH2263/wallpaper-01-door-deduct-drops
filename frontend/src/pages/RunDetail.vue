<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
const props = defineProps({ id: String })
const run = ref(null); const err = ref('')
onMounted(async () => {
  try { run.value = await getJSON(`/api/runs/${props.id}`) } catch (e) { err.value = String(e) }
})
</script>
<template>
  <div class="page" v-if="run"><h1>测算 #{{ run.id }}</h1>
  <p>{{ run.wall_name }} × {{ run.roll_name }} · {{ run.created_at }}<template v-if="run.note"> · {{ run.note }}</template></p>
  <p v-if="run.result?.door_widths?.length">
    门宽 {{ run.result.door_widths.join(' + ') }} m（合计 {{ run.result.door_total_m }} m），有效周长 {{ run.result.effective_perimeter_m }} m
  </p>
  <p v-else-if="run.result?.effective_perimeter_m != null">无门洞扣减，有效周长 {{ run.result.effective_perimeter_m }} m</p>
  <p><strong>{{ run.result?.rolls }} 卷</strong> · {{ run.result?.drops }} 条 · 每条 {{ run.result?.drop_len_m }}m</p>
  <DropStripBar :drops="run.result?.drops" :drop-len="run.result?.drop_len_m" :rolls="run.result?.rolls" />
  </div>
  <div class="page" v-else><h1>测算</h1><p class="warn">记录不存在或加载失败</p></div>
</template>
