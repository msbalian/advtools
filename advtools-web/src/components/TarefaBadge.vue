<script setup>
import { computed } from 'vue'
import { AlertCircle, Clock, CheckCircle2, XCircle } from 'lucide-vue-next'

const props = defineProps({
  type: {
    type: String,
    required: true, // 'status' ou 'prioridade'
  },
  value: {
    type: String,
    required: true,
  }
})

const config = computed(() => {
  if (props.type === 'status') {
    const statuses = {
      'Pendente': { color: 'bg-slate-100 text-slate-600 border-slate-200', icon: Clock },
      'Em Andamento': { color: 'bg-amber-100 text-amber-700 border-amber-200', icon: AlertCircle },
      'Concluída': { color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: CheckCircle2 },
      'Cancelada': { color: 'bg-red-100 text-red-700 border-red-200', icon: XCircle },
    }
    return statuses[props.value] || { color: 'bg-slate-100 text-slate-600 border-slate-200', icon: Clock }
  } else {
    // Prioridade
    const priorities = {
      'Baixa': { color: 'bg-slate-100 text-slate-600 border-slate-200', dot: 'bg-slate-400' },
      'Normal': { color: 'bg-sky-100 text-sky-700 border-sky-200', dot: 'bg-sky-500' },
      'Alta': { color: 'bg-orange-100 text-orange-700 border-orange-200', dot: 'bg-orange-500' },
      'Urgente': { color: 'bg-red-100 text-red-700 border-red-200', dot: 'bg-red-600' },
    }
    return priorities[props.value] || { color: 'bg-slate-100 text-slate-700 border-slate-200', dot: 'bg-slate-400' }
  }
})
</script>

<template>
  <span :class="['inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border transition-all', config.color]">
    <component v-if="props.type === 'status'" :is="config.icon" class="w-3 h-3" />
    <span v-else class="w-1.5 h-1.5 rounded-full" :class="config.dot"></span>
    {{ props.value }}
  </span>
</template>
