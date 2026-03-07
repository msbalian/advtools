<script setup>
import { ref, watch, onMounted, computed } from 'vue'
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
      cliente_id: null,
      processo_id: null,
      responsavel_id: null
    })
  },
  processoId: {
    type: Number,
    default: null
  },
  clienteId: {
    type: Number,
    default: null
  },
  isEditing: Boolean,
  isSubmitting: Boolean
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...props.tarefa })
const usuarios = ref([])
const clientes = ref([])
const processos = ref([])
const searchCliente = ref('')
const searchProcesso = ref('')
const showClienteDropdown = ref(false)
const showProcessoDropdown = ref(false)

const loadUsuarios = async () => {
  try {
    const res = await apiFetch('/api/usuarios')
    if (res.ok) usuarios.value = await res.json()
  } catch (e) {
    console.error("Erro ao carregar usuários", e)
  }
}

const loadClientes = async () => {
  try {
    const res = await apiFetch('/api/clientes')
    if (res.ok) clientes.value = await res.json()
  } catch (e) {
    console.error("Erro ao carregar clientes", e)
  }
}

const loadProcessos = async () => {
  try {
    const res = await apiFetch('/api/processos')
    if (res.ok) processos.value = await res.json()
  } catch (e) {
    console.error("Erro ao carregar processos", e)
  }
}

const filteredClientes = computed(() => {
  if (!searchCliente.value) return clientes.value
  const s = searchCliente.value.toLowerCase()
  return clientes.value.filter(c => 
    c.nome.toLowerCase().includes(s) || 
    (c.documento && c.documento.includes(s))
  )
})

const filteredProcessos = computed(() => {
  let list = processos.value
  
  // Se tiver cliente selecionado, filtra apenas os dele
  if (form.value.cliente_id) {
    list = list.filter(p => p.cliente_id === form.value.cliente_id)
  }
  
  if (!searchProcesso.value) return list
  const s = searchProcesso.value.toLowerCase()
  return list.filter(p => 
    (p.numero_processo && p.numero_processo.includes(s)) || 
    (p.titulo && p.titulo.toLowerCase().includes(s))
  )
})

const selectedClienteNome = computed(() => {
  const c = clientes.value.find(c => c.id === form.value.cliente_id)
  return c ? c.nome : ''
})

const selectedProcessoNome = computed(() => {
  const p = processos.value.find(p => p.id === form.value.processo_id)
  return p ? (p.numero_processo ? `${p.numero_processo} - ${p.titulo}` : p.titulo) : ''
})

const selectCliente = (cliente) => {
  form.value.cliente_id = cliente.id
  searchCliente.value = cliente.nome
  showClienteDropdown.value = false
  // Ao trocar o cliente, limpa o processo se ele não pertencer ao novo cliente
  if (form.value.processo_id) {
    const proc = processos.value.find(p => p.id === form.value.processo_id)
    if (proc && proc.cliente_id !== cliente.id) {
      form.value.processo_id = null
      searchProcesso.value = ''
    }
  }
}

const selectProcesso = (processo) => {
  form.value.processo_id = processo.id
  form.value.cliente_id = processo.cliente_id
  searchProcesso.value = processo.numero_processo ? `${processo.numero_processo} - ${processo.titulo}` : processo.titulo
  showProcessoDropdown.value = false
  
  // Se selecionou processo, automaticamente seleciona o cliente dele
  if (!form.value.cliente_id && processo.cliente_id) {
      const c = clientes.value.find(c => c.id === processo.cliente_id)
      if (c) searchCliente.value = c.nome
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    form.value = { ...props.tarefa }
    
    // Contexto de Cliente
    if (props.clienteId && !form.value.cliente_id) {
        form.value.cliente_id = props.clienteId
    }

    // Contexto de Processo
    if (props.processoId && !form.value.processo_id) {
        form.value.processo_id = props.processoId
        const proc = processos.value.find(p => p.id === props.processoId)
        if (proc && !form.value.cliente_id) {
            form.value.cliente_id = proc.cliente_id
        }
    }
    
    // Sincronizar busca com IDs existentes
    if (form.value.cliente_id) {
        const c = clientes.value.find(c => c.id === form.value.cliente_id)
        if (c) searchCliente.value = c.nome
    } else {
        searchCliente.value = ''
    }

    if (form.value.processo_id) {
        const p = processos.value.find(p => p.id === form.value.processo_id)
        if (p) searchProcesso.value = p.numero_processo ? `${p.numero_processo} - ${p.titulo}` : p.titulo
    } else {
        searchProcesso.value = ''
    }
    
    // Formatar data para input datetime-local se existir
    if (form.value.data_vencimento) {
        const d = new Date(form.value.data_vencimento)
        form.value.data_vencimento = d.toISOString().slice(0, 16)
    }
  }
})

onMounted(() => {
    loadUsuarios()
    loadClientes()
    loadProcessos()
    
    // Fechar dropdowns ao clicar fora
    window.addEventListener('click', (e) => {
        if (!e.target.closest('.relative')) {
            showClienteDropdown.value = false
            showProcessoDropdown.value = false
        }
    })
})

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
        <!-- Vínculo com Cliente e Processo (Searchers) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Busca de Cliente -->
          <div class="space-y-2 relative">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <User class="w-3 h-3" /> Cliente
            </label>
            <div class="relative">
              <input v-model="searchCliente" type="text" 
                     @focus="showClienteDropdown = true"
                     placeholder="Buscar cliente..."
                     class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-slate-700 shadow-inner">
              <button v-if="form.cliente_id" @click="form.cliente_id = null; searchCliente = ''; form.processo_id = null; searchProcesso = ''" 
                      type="button" class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-red-500">
                <X class="w-4 h-4" />
              </button>
            </div>
            
            <!-- Dropdown Clientes -->
            <div v-if="showClienteDropdown && filteredClientes.length > 0" 
                 class="absolute z-[110] left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-white border border-slate-200 rounded-2xl shadow-xl animate-fade-in">
              <button v-for="c in filteredClientes" :key="c.id" type="button"
                      @click="selectCliente(c)"
                      class="w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0 flex flex-col">
                <span class="font-bold text-slate-900">{{ c.nome }}</span>
                <span class="text-[10px] text-slate-500">{{ c.documento || 'Sem documento' }}</span>
              </button>
            </div>
          </div>

          <!-- Busca de Processo -->
          <div class="space-y-2 relative">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
              <Briefcase class="w-3 h-3" /> Processo
            </label>
            <div class="relative">
              <input v-model="searchProcesso" type="text"
                     @focus="showProcessoDropdown = true"
                     placeholder="Buscar processo..."
                     class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-primary-500 transition-all font-bold text-slate-700 shadow-inner">
              <button v-if="form.processo_id" @click="form.processo_id = null; searchProcesso = ''" 
                      type="button" class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-red-500">
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Dropdown Processos -->
            <div v-if="showProcessoDropdown && filteredProcessos.length > 0" 
                 class="absolute z-[110] left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-white border border-slate-200 rounded-2xl shadow-xl animate-fade-in">
              <button v-for="p in filteredProcessos" :key="p.id" type="button"
                      @click="selectProcesso(p)"
                      class="w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0 flex flex-col">
                <span v-if="p.numero_processo" class="text-[10px] text-primary-500 font-black">{{ p.numero_processo }}</span>
                <span class="font-bold text-slate-900">{{ p.titulo }}</span>
              </button>
            </div>
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
