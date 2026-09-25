<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'

const props = defineProps({ id: String })
const run = ref(null)
const notFound = ref(false)

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch {
    notFound.value = true
  }
})
</script>

<template>
  <div class="page">
    <h1>记录 #{{ id }}</h1>
    <p v-if="notFound" class="warn">找不到该编号的记录。</p>
    <div v-else-if="run">
      <p>{{ run.wall_name }} → {{ run.roll_name }}</p>

      <h2>门洞</h2>
      <template v-if="run.result.door_widths && run.result.door_widths.length">
        <p>门宽：
          <span v-for="(w, i) in run.result.door_widths" :key="i">{{ w }}m<span v-if="i < run.result.door_widths.length - 1">、</span></span>
          （合计 {{ run.result.doors_total_m }}m）
        </p>
        <p>墙面周长扣门后有效周长 <strong>{{ run.result.effective_perimeter_m }}m</strong></p>
      </template>
      <p v-else-if="run.result.door_widths">无门洞（有效周长即墙面周长）</p>
      <p v-else class="warn">旧记录 · 无门信息（drops/卷数仍按写入时快照显示）</p>

      <h2>测算结果（写入时快照）</h2>
      <p>
        <strong>{{ run.result.rolls }} 卷</strong>
        · {{ run.result.drops }} 条 · 每条 {{ run.result.drop_len_m }}m
        · 每卷 {{ run.result.strips_per_roll }} 条
      </p>
      <p v-if="run.note">备注：{{ run.note }}</p>
      <p>{{ run.created_at }}</p>
      <DropStripBar :drops="run.result.drops" :drop-len="run.result.drop_len_m" :rolls="run.result.rolls" />
      <p class="hint">本记录为写入时快照，之后修改墙面门洞不会改写本条。</p>
    </div>
  </div>
</template>
