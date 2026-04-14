<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Search, 
  Filter, 
  Plus, 
  MoreVertical,
  Calendar,
  User as UserIcon,
  Briefcase,
  ChevronRight,
  User,
  Menu,
  Trash2,
  X,
  Check
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import TarefaBadge from '../components/TarefaBadge.vue'
import TarefaFormModal from '../components/TarefaFormModal.vue'
import TarefaCard from '../components/TarefaCard.vue'

const router = useRouter()
const route = useRoute()

// State
const sidebarOpen = ref(false)
const escritorio = ref(null)
const currentUser = ref(null)
const tarefas = ref([])
const usuarios = ref([])
const clientes = ref([])
const loading = ref(true)

// UI State
const notification = ref({ show: false, message: '', type: 'success' })
const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'danger' })

// Filters
const filterStatus = ref('')
const filterResponsavel = ref('')
const filterCliente = ref('')
const filterSearch = ref('')

// Modal State
const showTarefaModal = ref(false)
const isEditingTarefa = ref(false)
const isSubmittingTarefa = ref(false)
const selectedTarefa = ref(null)

const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'danger') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}

const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const carregarDadosIniciais = async () => {
    loading.value = true
    try {
        const [resEsc, resUser, resUsuarios, resClientes] = await Promise.all([
            apiFetch('/api/escritorio'),
            apiFetch('/api/me'),
            apiFetch('/api/usuarios'),
            apiFetch('/api/clientes')
        ])
        
        if (resEsc.ok) escritorio.value = await resEsc.json()
        if (resUser.ok) currentUser.value = await resUser.json()
        if (resUsuarios.ok) usuarios.value = await resUsuarios.json()
        if (resClientes.ok) clientes.value = await resClientes.json()
        
        await carregarTarefas()
        
        // Se vier com parâmetro ?edit=ID, abre o modal de edição
        if (route.query.edit) {
            const tarefaId = Number(route.query.edit)
            const tarefa = tarefas.value.find(t => t.id === tarefaId)
            if (tarefa) {
                editarTarefa(tarefa)
            } else {
                // Se não estiver na lista (pode ser antiga ou de outro escritório), busca individualmente
                try {
                    const res = await apiFetch(`/api/tarefas/${tarefaId}`)
                    if (res.ok) {
                        const tFull = await res.json()
                        editarTarefa(tFull)
                    }
                } catch (e) {
                    console.error("Erro ao buscar tarefa para edição automática", e)
                }
            }
        }
    } catch (e) {
        console.error("Erro ao carregar dados iniciais", e)
    } finally {
        loading.value = false
    }
}

const carregarTarefas = async () => {
    let url = '/api/tarefas?'
    if (filterStatus.value) url += `status=${filterStatus.value}&`
    if (filterResponsavel.value) url += `responsavel_id=${filterResponsavel.value}&`
    if (filterCliente.value) url += `cliente_id=${filterCliente.value}&`
    
    try {
        const res = await apiFetch(url)
        if (res.ok) {
            tarefas.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar tarefas", e)
    }
}

// Watchers for filters
watch([filterStatus, filterResponsavel, filterCliente], () => {
    carregarTarefas()
})

const tarefasFiltradas = computed(() => {
    if (!filterSearch.value) return tarefas.value
    const search = filterSearch.value.toLowerCase()
    return tarefas.value.filter(t => 
        t.titulo.toLowerCase().includes(search) || 
        (t.descricao && t.descricao.toLowerCase().includes(search))
    )
})

const abrirNovaTarefa = () => {
    isEditingTarefa.value = false
    selectedTarefa.value = {
        titulo: '',
        descricao: '',
        status: 'Pendente',
        prioridade: 'Normal',
        data_vencimento: null,
        cliente_id: null,
        processo_id: null,
        responsavel_id: null
    }
    showTarefaModal.value = true
}

const editarTarefa = (tarefa) => {
    isEditingTarefa.value = true
    selectedTarefa.value = { ...tarefa }
    showTarefaModal.value = true
}

const handleTarefaSubmit = async (dados) => {
    isSubmittingTarefa.value = true
    try {
        const method = isEditingTarefa.value ? 'PATCH' : 'POST'
        const url = isEditingTarefa.value ? `/api/tarefas/${dados.id}` : '/api/tarefas'
        
        const res = await apiFetch(url, {
            method,
            body: JSON.stringify(dados)
        })

        if (res.ok) {
            showMessage(isEditingTarefa.value ? "Tarefa atualizada!" : "Tarefa criada!", "success")
            showTarefaModal.value = false
            await carregarTarefas()
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao salvar tarefa", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão.", "error")
    } finally {
        isSubmittingTarefa.value = false
    }
}

const deleteTarefa = (tarefaId) => {
    confirmAction(
        "Tem certeza que deseja excluir esta tarefa?",
        async () => {
            try {
                const res = await apiFetch(`/api/tarefas/${tarefaId}`, { method: 'DELETE' })
                if (res.ok) {
                    showMessage("Tarefa excluída com sucesso!")
                    await carregarTarefas()
                } else {
                    showMessage("Erro ao excluir tarefa.", "error")
                }
            } catch (e) {
                showMessage("Erro de conexão.", "error")
            }
        },
        "Excluir Tarefa",
        "danger"
    )
}

const toggleTarefaStatus = async (tarefa) => {
    const newStatus = tarefa.status === 'Concluída' ? 'Pendente' : 'Concluída'
    try {
        const res = await apiFetch(`/api/tarefas/${tarefa.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        })
        if (res.ok) {
            tarefa.status = newStatus
            showMessage(newStatus === 'Concluída' ? "Tarefa concluída! 🎉" : "Tarefa reaberta.")
            await carregarTarefas()
        }
    } catch (e) {
        showMessage("Erro ao atualizar status", "error")
    }
}

onMounted(carregarDadosIniciais)

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
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <!-- Header -->
      <header class="bg-white border-b border-slate-200 px-4 sm:px-8 py-5 flex flex-col gap-4 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 text-slate-500">
               <Menu class="w-6 h-6" />
            </button>
            <div>
              <h1 class="text-2xl font-bold text-slate-900 flex items-center gap-3">
                <CheckCircle2 class="w-7 h-7 text-primary-600" />
                Tarefas e Prazos
              </h1>
              <p class="text-slate-500 text-sm">Gestão centralizada de atividades do escritório</p>
            </div>
          </div>
          <button @click="abrirNovaTarefa" class="btn-primary flex items-center gap-2">
            <Plus class="w-5 h-5" /> Nova Tarefa
          </button>
        </div>

        <!-- Filters Bar -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end mt-2 bg-slate-50 p-4 rounded-2xl border border-slate-100">
          <div>
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 ml-1">Buscar</label>
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input v-model="filterSearch" type="text" placeholder="Título ou descrição..." class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition-all" />
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 ml-1">Responsável</label>
            <select v-model="filterResponsavel" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition-all">
              <option value="">Todos os Membros</option>
              <option :value="currentUser?.id">Minhas Tarefas</option>
              <option v-for="u in usuarios.filter(u => u.id !== currentUser?.id)" :key="u.id" :value="u.id">{{ u.nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 ml-1">Cliente</label>
            <select v-model="filterCliente" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition-all">
              <option value="">Todos os Clientes</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 ml-1">Status</label>
            <select v-model="filterStatus" class="w-full px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 outline-none transition-all">
              <option value="">Qualquer Status</option>
              <option value="Pendente">Pendente</option>
              <option value="Em Andamento">Em Andamento</option>
              <option value="Concluída">Concluída</option>
              <option value="Cancelada">Cancelada</option>
            </select>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-8">
        <!-- Notification Toast -->
        <div v-if="notification.show" 
             :class="[notification.type === 'success' ? 'bg-emerald-600' : 'bg-red-600']"
             class="fixed top-8 right-8 z-[1001] px-6 py-3 rounded-2xl text-white font-bold shadow-2xl flex items-center gap-3 animate-fade-in-down">
          <CheckCircle2 v-if="notification.type === 'success'" class="w-5 h-5" />
          <AlertCircle v-else class="w-5 h-5" />
          {{ notification.message }}
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
          <div class="w-12 h-12 border-4 border-primary-100 border-t-primary-600 rounded-full animate-spin mb-4"></div>
          <p class="text-slate-500 font-medium">Carregando tarefas...</p>
        </div>

        <div v-else-if="tarefasFiltradas.length === 0" class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
          <div class="h-20 w-20 bg-slate-50 rounded-full flex items-center justify-center mb-6">
            <CheckCircle2 class="w-10 h-10 text-slate-300" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">Nenhuma tarefa encontrada</h3>
          <p class="text-slate-500 max-w-xs text-center">Tente ajustar seus filtros ou crie uma nova tarefa para começar.</p>
          <button @click="abrirNovaTarefa" class="mt-6 btn-secondary">Nova Tarefa</button>
        </div>

        <div v-else class="grid grid-cols-1 gap-4">
          <TarefaCard 
            v-for="tarefa in tarefasFiltradas" 
            :key="tarefa.id" 
            :tarefa="tarefa"
            @edit="editarTarefa"
            @delete="deleteTarefa"
            @toggle-status="toggleTarefaStatus"
          />
        </div>
      </main>

      <!-- Modal -->
      <TarefaFormModal
        :show="showTarefaModal"
        :tarefa="selectedTarefa"
        :isEditing="isEditingTarefa"
        :isSubmitting="isSubmittingTarefa"
        @close="showTarefaModal = false"
        @submit="handleTarefaSubmit"
      />

      <!-- Confirm Dialog -->
      <div v-if="confirmDialog.show" class="fixed inset-0 z-[1002] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up border border-slate-200">
          <div class="text-center">
            <div :class="['mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4', confirmDialog.type === 'primary' ? 'bg-primary-100' : 'bg-red-100']">
              <CheckCircle2 v-if="confirmDialog.type === 'primary'" class="h-6 w-6 text-primary-600" />
              <Trash2 v-else class="h-6 w-6 text-red-600" />
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
            <p class="text-sm text-slate-500 mb-6">{{ confirmDialog.message }}</p>
            <div class="flex gap-3 justify-center">
              <button @click="confirmDialog.show = false" class="px-5 py-2 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-colors">Cancelar</button>
              <button @click="executeConfirm" :class="['px-5 py-2 rounded-xl font-bold text-white transition-all', confirmDialog.type === 'primary' ? 'bg-primary-600 hover:bg-primary-700' : 'bg-red-600 hover:bg-red-700']">
                  Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-primary {
  @apply bg-primary-600 text-white px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/20 active:scale-95 text-sm;
}
.btn-secondary {
  @apply bg-white text-slate-700 border border-slate-200 px-5 py-2.5 rounded-xl font-bold flex items-center gap-2 hover:bg-slate-50 transition-all active:scale-95 text-sm;
}

.animate-fade-in-down { animation: fade-in-down 0.4s ease-out-back; }
.animate-fade-in-up { animation: fade-in-up 0.4s ease-out; }

@keyframes fade-in-down {
  0% { opacity: 0; transform: translateY(-20px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
