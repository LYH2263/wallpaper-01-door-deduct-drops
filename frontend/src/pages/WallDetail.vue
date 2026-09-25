<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
import DoorWidthList from '../components/DoorWidthList.vue'

const props = defineProps({ id: String })
const wall = ref(null)
const rolls = ref([])
const rollId = ref(1)
const doorWidths = ref([])
const savedMsg = ref('')
const error = ref('')
const noDoor = ref(null)
const withDoors = ref(null)

onMounted(async () => {
  const [w, d, rs] = await Promise.all([
    getJSON(`/api/walls/${props.id}`),
    getJSON(`/api/walls/${props.id}/doors`).catch(() => ({ items: [] })),
    getJSON('/api/rolls'),
  ])
  wall.value = w
  doorWidths.value = d.items.map((x) => x.width)
  rolls.value = rs.items.filter((r) => r.data_quality === 'clean')
  if (rolls.value.length) rollId.value = rolls.value[0].id
})

async function saveDoors() {
  savedMsg.value = ''
  error.value = ''
  try {
    const res = await putJSON(`/api/walls/${props.id}/doors`, { widths: doorWidths.value })
    doorWidths.value = res.items.map((x) => x.width)
    savedMsg.value = '门洞已保存'
  } catch (e) {
    error.value = e.message || String(e)
  }
}

async function compare() {
  savedMsg.value = ''
  error.value = ''
  noDoor.value = null
  withDoors.value = null
  try {
    const [a, b] = await Promise.all([
      postJSON('/api/estimate', { wall_id: Number(props.id), roll_id: rollId.value, save: false, door_widths: [] }),
      postJSON('/api/estimate', { wall_id: Number(props.id), roll_id: rollId.value, save: false, door_widths: doorWidths.value }),
    ])
    noDoor.value = a
    withDoors.value = b
  } catch (e) {
    error.value = e.message || String(e)
  }
}
</script>

<template>
  <div class="page" v-if="wall">
    <h1>{{ wall.name }}</h1>
    <p v-if="wall.data_quality === 'dirty'" class="warn">{{ wall.note }}</p>
    <p>周长 {{ wall.perimeter }} m，墙高 {{ wall.height }} m</p>

    <h2>门洞（米）</h2>
    <DoorWidthList v-model="doorWidths" />
    <button @click="saveDoors">保存门洞</button>
    <span v-if="savedMsg" style="margin-left: .5rem">{{ savedMsg }}</span>
    <p class="hint">门洞保存在本墙面上；已保存的测算记录是写入时快照，不会随这里修改而改变。</p>
    <p v-if="error" class="warn">{{ error }}</p>

    <h2>对照 drops</h2>
    <select v-model.number="rollId">
      <option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.id }} · 宽{{ r.width }}</option>
    </select>
    <button @click="compare">对照试算</button>
    <div v-if="withDoors">
      <p>
        无门 {{ noDoor.drops }} 条 / {{ noDoor.rolls }} 卷
        → 扣门后 <strong>{{ withDoors.drops }}</strong> 条 / <strong>{{ withDoors.rolls }}</strong> 卷
        （有效周长 {{ withDoors.effective_perimeter_m }}m）
      </p>
      <DropStripBar :drops="withDoors.drops" :drop-len="withDoors.drop_len_m" :rolls="withDoors.rolls" />
      <p>
        <router-link
          :to="`/drops?drops=${withDoors.drops}&dropLen=${withDoors.drop_len_m}&rolls=${withDoors.rolls}`"
        >展开示意</router-link>
      </p>
    </div>
  </div>
</template>
