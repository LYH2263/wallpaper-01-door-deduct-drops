<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
import DoorsEditor from '../components/DoorsEditor.vue'
const props = defineProps({ id: String })
const wall = ref(null); const doors = ref([]); const rolls = ref([]); const rollId = ref(null)
const withDoors = ref(null); const withoutDoors = ref(null); const err = ref('')
onMounted(async () => {
  wall.value = await getJSON(`/api/walls/${props.id}`)
  doors.value = (wall.value.doors || []).slice()
  rolls.value = (await getJSON('/api/rolls')).items.filter(r => r.data_quality==='clean')
  if (rolls.value.length) { rollId.value = rolls.value[0].id; await compare() }
})
async function compare() {
  err.value = ''
  if (!rollId.value) return
  try {
    const body = { wall_id: Number(props.id), roll_id: rollId.value, save: false }
    withDoors.value = await postJSON('/api/estimate', { ...body, door_widths: doors.value })
    withoutDoors.value = await postJSON('/api/estimate', { ...body, door_widths: [] })
  } catch (e) { err.value = String(e); withDoors.value = null; withoutDoors.value = null }
}
async function saveDoors() {
  err.value = ''
  try {
    wall.value = await putJSON(`/api/walls/${props.id}/doors`, { doors: doors.value })
    doors.value = (wall.value.doors || []).slice()
    await compare()
  } catch (e) { err.value = String(e) }
}
</script>
<template>
  <div class="page" v-if="wall"><h1>{{ wall.name }}</h1>
  <p v-if="wall.data_quality==='dirty'" class="warn">{{ wall.note }}</p>
  <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>
  <h2>门洞</h2>
  <DoorsEditor v-model="doors" />
  <p><button @click="saveDoors">保存门洞</button></p>
  <p v-if="err" class="warn">{{ err }}</p>
  <h2>幅数对照</h2>
  <select v-model.number="rollId" @change="compare"><option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.name }}</option></select>
  <button @click="compare">刷新对照</button>
  <div v-if="withDoors && withoutDoors">
    <p>不扣门 {{ withoutDoors.drops }} 条 / {{ withoutDoors.rolls }} 卷 → 扣门后 {{ withDoors.drops }} 条 / {{ withDoors.rolls }} 卷</p>
    <p>有效周长 {{ withDoors.effective_perimeter_m }}m（门宽合计 {{ withDoors.door_total_m }}m）</p>
    <DropStripBar :drops="withDoors.drops" :drop-len="withDoors.drop_len_m" :rolls="withDoors.rolls" />
  </div>
  </div>
</template>
