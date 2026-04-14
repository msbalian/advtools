<script setup>
import { computed } from 'vue'
import { Calendar, User as UserIcon, Briefcase, Trash2, Check, ChevronRight, Sparkles, X } from 'lucide-vue-next'
import TarefaBadge from './TarefaBadge.vue'

const props = defineProps({
  tarefa: {
    type: Object,
    required: true
  },
  showProcessInfo: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['edit', 'delete', 'toggle-status', 'aprovar-ia', 'descartar-ia'])

const formatData = (data) => {
    if (!data) return 'Sem prazo'
    return new Date(data).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const isOverdue = computed(() => {
    if (!props.tarefa.data_vencimento) return false
    return new Date(props.tarefa.data_vencimento) < new Date() && props.tarefa.status !== 'Concluída'
})
</script>

<template>
  <div class="bg-white p-5 rounded-3xl border border-slate-200 hover:border-primary-300 hover:shadow-xl hover:shadow-primary-500/10 transition-all cursor-pointer group flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden">
    
    <!-- Barra Lateral de Prioridade -->
    <div :class="['absolute left-0 top-0 bottom-0 w-1.5 transition-all', 
       tarefa.prioridade === 'Urgente' ? 'bg-red-500' : 
       tarefa.prioridade === 'Alta' ? 'bg-orange-500' : 
       tarefa.prioridade === 'Normal' ? 'bg-sky-500' : 'bg-slate-300']"></div>

    <div class="flex items-start gap-4 flex-1">
      <!-- Checkbox Custom -->
      <button @click.stop="emit('toggle-status', tarefa)" 
              :class="['mt-1 w-8 h-8 rounded-xl border-2 flex items-center justify-center transition-all flex-shrink-0', 
              tarefa.status === 'Concluída' ? 'bg-emerald-500 border-emerald-500 text-white shadow-lg shadow-emerald-500/30' : 'bg-white border-slate-200 text-slate-200 hover:border-primary-500']">
         <Check class="w-5 h-5" />
      </button>

      <div @click="emit('edit', tarefa)" class="min-w-0 flex-1">
        <div class="flex items-center gap-3 mb-1.5">
          <h3 :class="['text-base font-black truncate group-hover:text-primary-600 transition-colors leading-tight', tarefa.status === 'Concluída' ? 'text-slate-400 line-through' : 'text-slate-900']">
            {{ tarefa.titulo }}
          </h3>
          <div class="flex gap-2">
            <TarefaBadge type="status" :value="tarefa.status" />
            <TarefaBadge type="prioridade" :value="tarefa.prioridade" />
          </div>
        </div>
        
        <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
          <div class="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Calendar class="w-3.5 h-3.5" />
            <span :class="{'text-red-600 font-bold': isOverdue}">
              {{ formatData(tarefa.data_vencimento) }}
            </span>
          </div>
          
          <div v-if="showProcessInfo && tarefa.processo" class="flex items-center gap-1.5 text-xs text-primary-600 font-bold bg-primary-50 px-2 py-0.5 rounded-lg border border-primary-100">
            <Briefcase class="w-3.5 h-3.5" />
            <span class="truncate max-w-[250px]">Proc: {{ tarefa.processo.numero_processo || tarefa.processo.titulo }}</span>
          </div>

          <div v-if="tarefa.cliente || (tarefa.processo && tarefa.processo.cliente)" class="flex items-center gap-1.5 text-xs text-slate-500">
            <UserIcon class="w-3.5 h-3.5" />
            <span class="truncate max-w-[150px] font-medium">{{ (tarefa.cliente || tarefa.processo?.cliente).nome }}</span>
          </div>
        </div>
        <p v-if="tarefa.descricao" class="mt-2 text-xs text-slate-500 font-medium line-clamp-1">{{ tarefa.descricao }}</p>
      </div>
    </div>

    <div class="flex items-center justify-between lg:justify-end gap-8 pl-12 lg:pl-0 border-t lg:border-t-0 border-slate-50 pt-4 lg:pt-0">
      <div class="flex items-center gap-2">
        <div class="flex flex-col items-end">
          <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest leading-none mb-1">Responsável</span>
          <span class="text-xs font-bold text-slate-700">{{ tarefa.responsavel?.nome || 'Não atribuído' }}</span>
        </div>
        <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700 text-[10px] font-black shadow-sm">
          {{ tarefa.responsavel?.nome?.charAt(0).toUpperCase() || '?' }}
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <template v-if="tarefa.status === 'Sugestão (IA)'">
           <button @click.stop="emit('aprovar-ia', tarefa)" 
                   class="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-[10px] font-black rounded-lg border border-indigo-100 hover:bg-indigo-500 hover:text-white transition-all flex items-center gap-1.5 shadow-sm">
              <Sparkles class="w-3 h-3" /> APROVAR
           </button>
           <button @click.stop="emit('descartar-ia', tarefa.id)" 
                   class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all">
              <X class="w-4 h-4" />
           </button>
        </template>
        <template v-else>
           <button @click.stop="emit('delete', tarefa.id)" class="p-2 hover:bg-red-50 rounded-xl text-slate-300 hover:text-red-600 transition-colors">
             <Trash2 class="w-5 h-5" />
           </button>
           <ChevronRight @click.stop="emit('edit', tarefa)" class="w-5 h-5 text-slate-300 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
        </template>
      </div>
    </div>
  </div>
</template>
