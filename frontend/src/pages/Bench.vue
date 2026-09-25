<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
import DoorsEditor from '../components/DoorsEditor.vue'
const walls = ref([]); const rolls = ref([]); const wallId = ref(1); const rollId = ref(1)
const doors = ref([]); const out = ref(null); const base = ref(null); const err = ref('')
onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter(w => w.data_quality==='clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
  syncDoors()
})
watch(wallId, syncDoors)
function syncDoors() {
  const w = walls.value.find(w => w.id === wallId.value)
  doors.value = (w?.doors || []).slice()
  out.value = null; base.value = null; err.value = ''
}
async function run(save) {
  err.value = ''
  try {
    const body = { wall_id: wallId.value, roll_id: rollId.value, door_widths: doors.value }
    out.value = await postJSON('/api/estimate', { ...body, save })
    base.value = await postJSON('/api/estimate', { ...body, save: false, door_widths: [] })
  } catch (e) { err.value = String(e); out.value = null; base.value = null }
}
async function saveDoors() {
  err.value = ''
  try {
    const w = await putJSON(`/api/walls/${wallId.value}/doors`, { doors: doors.value })
    const i = walls.value.findIndex(x => x.id === w.id)
    if (i >= 0) walls.value[i] = w
  } catch (e) { err.value = String(e) }
}
</script>
<template>
  <div class="page"><h1>算卷工作台</h1>
  <select v-model.number="wallId"><option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}</option></select>
  <select v-model.number="rollId"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <DoorsEditor v-model="doors" />
  <p>
    <button @click="run(false)">试算</button><button @click="run(true)">保存</button>
    <button @click="saveDoors">保存门洞到墙面</button>
  </p>
  <p v-if="err" class="warn">{{ err }}</p>
  <div v-if="out">
    <p v-if="base && base.drops !== out.drops">不扣门 {{ base.drops }} 条 / {{ base.rolls }} 卷 → 扣门后 {{ out.drops }} 条 / {{ out.rolls }} 卷</p>
    <p v-else-if="base">无门洞扣减，{{ out.drops }} 条与不扣门一致</p>
    <p>有效周长 {{ out.effective_perimeter_m }}m（门宽合计 {{ out.door_total_m }}m）</p>
    <strong>{{ out.rolls }} 卷</strong> · {{ out.drops }} 条 · 每条 {{ out.drop_len_m }}m
    <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" />
  </div>
  </div>
</template>
