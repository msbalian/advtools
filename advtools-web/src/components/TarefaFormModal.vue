<script setup>
import { ref, watch, onMounted } from 'vue'
import { Plus, X, Calendar, Flag, User, Briefcase } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'

const props = defineProps({
  show: Boolean,
  tarefa: {
    type: Object,
    default: () => ({
      titulo: '',
      descricao: '',
      status: 'Pendente',
      prioridade: 'Normal',
      data_vencimento: null,
      processo_id: null,
      responsavel_id: null
    })
  },
  processoId: {
    type: Number,
    default: null
  },
  isEditing: Boolean,
  isSubmitting: Boolean
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...props.tarefa })
const usuarios = ref([])

const loadUsuarios = async () => {
  try {
    const res = await apiFetch('/api/usuarios')
    if (res.ok) usuarios.value = await res.json()
  } catch (e) {
    console.error("Erro ao carregar usuários", e)
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    form.value = { ...props.tarefa }
    
    // Garantir que se estivermos em um processo, o ID seja passado
    if (props.processoId && !form.value.processo_id) {
        form.value.processo_id = props.processoId
    }
    
    // Formatar data para input datetime-local se existir
    if (form.value.data_vencimento) {
        const d = new Date(form.value.data_vencimento)
        form.value.data_vencimento = d.toISOString().slice(0, 16)
    }
  }
})

onMounted(loadUsuarios)

const handleSubmit = () => {
  emit('submit', { ...form.value })
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fade-in">
    <div class="bg-white rounded-[32px] shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in-up">
      <!-- Header -->
      <div class="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div>
          <h2 class="text-xl font-black text-slate-900 tracking-tight">
            {{ isEditing ? 'Editar Tarefa' : 'Nova Tarefa' }}
          </h2>
          <p class="text-xs text-slate-500 font-medium">Preencha os detalhes da atividade abaixo</p>
        </div>
        <button @click="$emit('close')" class="p-2 hover:bg-white rounded-full transition-colors text-slate-400 hover:text-slate-600 shadow-sm border border-transparent hover:border-slate-100">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-8 space-y-6">
        <!-- Vínculo com Processo (Informativo) -->
        <div v-if="tarefa?.processo" class="p-4 bg-primary-50 rounded-2xl border border-primary-100 flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-primary-600 shadow-sm">
            <Briefcase class="w-5 h-5" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-[9px] text-primary-400 font-black uppercase tracking-widest leading-none mb-1">Processo Vinculado</p>
            <p class="text-sm font-bold text-primary-800 truncate">{{ tarefa.processo.numero_processo || tarefa.processo.titulo }}</p>
          </div>
        </div>

        <!-- Título -->
        <div class="space-y-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
            Título da Tarefa *
          </label>
          <input v-model="form.titulo" type="text" required placeholder="Ex: Protocolar Petição Inicial"
                 class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-medium text-slate-900 shadow-inner">
        </div>

        <!-- Descrição -->
        <div class="space-y-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Descrição</label>
          <textarea v-model="form.descricao" rows="3" placeholder="Detalhes adicionais sobre a tarefa..."
                    class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-medium text-slate-900 resize-none shadow-inner"></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <!-- Prioridade -->
          <div class="space-y-2">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Flag class="w-3 h-3" /> Prioridade
            </label>
            <select v-model="form.prioridade" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-slate-700 shadow-inner appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%20fill%3D%22none%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cpath%20d%3D%22M5%207L10%2012L15%207%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22/%3E%3C/svg%3E')] bg-[length:20px_20px] bg-[right_1rem_center] bg-no-repeat">
              <option value="Baixa">Baixa</option>
              <option value="Normal">Normal</option>
              <option value="Alta">Alta</option>
              <option value="Urgente">Urgente</option>
            </select>
          </div>

          <!-- Data Vencimento -->
          <div class="space-y-2">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Calendar class="w-3 h-3" /> Prazo
            </label>
            <input v-model="form.data_vencimento" type="datetime-local"
                   class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-slate-700 shadow-inner">
          </div>
        </div>

        <!-- Responsável -->
        <div class="space-y-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
            <User class="w-3 h-3" /> Responsável
          </label>
          <select v-model="form.responsavel_id" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-slate-700 shadow-inner appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2220%22%20height%3D%2220%22%20viewBox%3D%220%200%2020%2020%22%20fill%3D%22none%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cpath%20d%3D%22M5%207L10%2012L15%207%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22/%3E%3C/svg%3E')] bg-[length:20px_20px] bg-[right_1rem_center] bg-no-repeat">
            <option :value="null">Não atribuído</option>
            <option v-for="user in usuarios" :key="user.id" :value="user.id">{{ user.nome }}</option>
          </select>
        </div>

        <!-- Footer Actions -->
        <div class="pt-4 flex items-center gap-3">
          <button type="button" @click="$emit('close')" 
                  class="flex-1 px-6 py-4 bg-slate-100 text-slate-600 font-black rounded-2xl hover:bg-slate-200 transition-all active:scale-95">
            Cancelar
          </button>
          <button type="submit" :disabled="isSubmitting"
                  class="flex-[2] px-6 py-4 bg-primary-600 text-white font-black rounded-2xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/20 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2">
            <Plus v-if="!isEditing" class="w-5 h-5" />
            {{ isSubmitting ? 'Salvando...' : (isEditing ? 'Salvar Alterações' : 'Criar Tarefa') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in { animation: fade-in 0.3s ease-out; }
.animate-fade-in-up { animation: fade-in-up 0.4s ease-out; }

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
