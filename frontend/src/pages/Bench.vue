<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON, postJSON } from '../api'
import DropStripBar from '../components/DropStripBar.vue'
import DoorWidthList from '../components/DoorWidthList.vue'

const walls = ref([])
const rolls = ref([])
const wallId = ref(1)
const rollId = ref(1)
const doorWidths = ref([])
const base = ref(null)
const out = ref(null)
const error = ref('')
const savedId = ref(null)

onMounted(async () => {
  walls.value = (await getJSON('/api/walls')).items.filter((w) => w.data_quality === 'clean')
  rolls.value = (await getJSON('/api/rolls')).items.filter((r) => r.data_quality === 'clean')
  if (walls.value.length) wallId.value = walls.value[0].id
  if (rolls.value.length) rollId.value = rolls.value[0].id
})

watch(wallId, async (id) => {
  out.value = null
  base.value = null
  error.value = ''
  if (!id) return
  try {
    doorWidths.value = (await getJSON(`/api/walls/${id}/doors`)).items.map((d) => d.width)
  } catch (e) {
    doorWidths.value = []
  }
}, { immediate: true })

async function run(save) {
  error.value = ''
  out.value = null
  savedId.value = null
  try {
    if (save) {
      const [noDoor, saved] = await Promise.all([
        postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: false, door_widths: [] }),
        postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: true, door_widths: doorWidths.value }),
      ])
      base.value = noDoor
      out.value = saved
      savedId.value = saved.run_id
    } else {
      const [noDoor, withDoors] = await Promise.all([
        postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: false, door_widths: [] }),
        postJSON('/api/estimate', { wall_id: wallId.value, roll_id: rollId.value, save: false, door_widths: doorWidths.value }),
      ])
      base.value = noDoor
      out.value = withDoors
    }
  } catch (e) {
    error.value = e.message || String(e)
  }
}
</script>

<template>
  <div class="page">
    <h1>算卷工作台</h1>
    <select v-model.number="wallId">
      <option v-for="w in walls" :key="w.id" :value="w.id">{{ w.name }}（周长 {{ w.perimeter }}m）</option>
    </select>
    <select v-model.number="rollId">
      <option v-for="r in rolls" :key="r.id" :value="r.id">{{ r.id }} · 宽{{ r.width }}</option>
    </select>

    <h2>门洞（米）</h2>
    <DoorWidthList v-model="doorWidths" />
    <p class="hint">门洞随选墙带出，可在此临时增删改；点“保存”仅把当前门宽写入本次记录，不改动墙面。</p>

    <button @click="run(false)">试算</button>
    <button @click="run(true)">保存</button>

    <p v-if="error" class="warn">测算失败：{{ error }}</p>

    <div v-if="out">
      <h2>结果</h2>
      <p>
        墙面周长 {{ out.wall.perimeter }}m − 门洞合计 {{ out.doors_total_m }}m
        = 有效周长 <strong>{{ out.effective_perimeter_m }}m</strong>
      </p>
      <p>
        drops：扣门前 {{ base?.drops }} 条 → 扣门后 <strong>{{ out.drops }}</strong> 条
        · 每条 {{ out.drop_len_m }}m · 每卷 {{ out.strips_per_roll }} 条
      </p>
      <p><strong>{{ out.rolls }} 卷</strong></p>
      <DropStripBar :drops="out.drops" :drop-len="out.drop_len_m" :rolls="out.rolls" />
      <p v-if="savedId">
        已保存为编号 <router-link :to="`/history/${savedId}`">#{{ savedId }}</router-link>
      </p>
      <p>
        <router-link
          :to="`/drops?drops=${out.drops}&dropLen=${out.drop_len_m}&rolls=${out.rolls}`"
        >展开示意</router-link>
      </p>
    </div>
  </div>
</template>
