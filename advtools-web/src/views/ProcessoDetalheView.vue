<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import ProcessoForm from '../components/ProcessoForm.vue'
import FileExplorer from '../components/FileExplorer.vue'
import TarefaBadge from '../components/TarefaBadge.vue'
import TarefaFormModal from '../components/TarefaFormModal.vue'
import {
  ArrowLeft,
  Scale,
  Gavel,
  History,
  Users,
  BookOpen,
  RefreshCw,
  Calendar,
  ShieldAlert,
  MapPin,
  ExternalLink,
  ChevronDown,
  LogOut,
  Menu,
  X,
  Plus,
  Trash2,
  Pencil,
  AlertCircle,
  CheckCircle2,
  Clock,
  Briefcase,
  FileText,
  Sparkles,
  BadgeDollarSign,
  FolderPlus,
  FilePlus,
  Download,
  Folder,
  ChevronRight,
  FileUp,
  FileSearch,
  Wand2,
  CheckSquare,
  Check,
  Edit2,
  User
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

// UI State
const sidebarOpen = ref(false)
const showProfileMenu = ref(false)
const isLoading = ref(true)
const isUpdating = ref(false)
const isSaving = ref(false)
const showEditForm = ref(false)
const activeTab = ref('resumo')
const notification = ref({ show: false, message: '', type: 'success' })

// Data State
const processo = ref(null)
const escritorio = ref(null)
const currentUser = ref(null)

// Pastas e Documentos
const pastas = ref([])
const documentos = ref([])
const tarefas = ref([])
const showTarefaModal = ref(false)
const isEditingTarefa = ref(false)
const isSubmittingTarefa = ref(false)
const selectedTarefa = ref(null)
const currentFolderId = ref(-1)
const breadcrumbs = ref([{ id: -1, nome: 'Raiz' }])
const isUploadingDoc = ref(false)
const fileInput = ref(null)
const isOrganizing = ref(false)
const progressModalOpen = ref(false)
const currentJobId = ref(null)
const jobProgress = ref({ status: '', progress: 0, message: '' })

const isNew = computed(() => route.params.id === 'novo')

const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'danger' })
const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'danger') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const carregarDados = async () => {
    isLoading.value = true
    try {
        const [resEsc, resUser] = await Promise.all([
            apiFetch('/api/escritorio'),
            apiFetch('/api/me')
        ])
        
        if (resEsc.ok) escritorio.value = await resEsc.json()
        if (resUser.ok) currentUser.value = await resUser.json()

        if (isNew.value) {
            processo.value = {
                titulo: '',
                numero_processo: '',
                tribunal: '',
                grau: 'G1',
                polo: 'Autor',
                status: 'Ativo',
                prioridade: 'Normal',
                cliente_id: route.query.cliente_id ? Number(route.query.cliente_id) : null
            }
            showEditForm.value = true
        } else {
            const resProc = await apiFetch(`/api/processos/${route.params.id}`)
            if (resProc.ok) {
                processo.value = await resProc.json()
                // As tarefas já vêm no processo por causa do relacionamento e schema
                tarefas.value = processo.value.tarefas || []
            } else {
                throw new Error("Processo não encontrado")
            }
        }
    } catch (e) {
        console.error("Erro ao carregar dados", e)
        showMessage("Erro ao carregar dados. Retornando...", "error")
        setTimeout(() => router.push('/processos'), 2000)
    } finally {
        isLoading.value = false
    }
}

const handleSaveProcesso = async (formData) => {
    isSaving.value = true
    try {
        const method = isNew.value ? 'POST' : 'PATCH'
        const url = isNew.value ? '/api/processos' : `/api/processos/${processo.value.id}`
        
        const res = await apiFetch(url, {
            method,
            body: JSON.stringify(formData)
        })

        if (res.ok) {
            const savedProc = await res.json()
            showMessage(isNew.value ? "Processo criado com sucesso!" : "Processo atualizado!", "success")
            
            if (isNew.value) {
                router.push(`/processos/${savedProc.id}`)
            } else {
                processo.value = savedProc
                showEditForm.value = false
            }
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao salvar processo.", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão.", "error")
    } finally {
        isSaving.value = false
    }
}

const handleAtualizarDataJud = async () => {
    if (!processo.value?.numero_processo || isNew.value) return
    isUpdating.value = true
    try {
        const res = await apiFetch(`/api/processos/${processo.value.id}/atualizar-datajud`, {
            method: 'POST'
        })
        if (res.ok) {
            processo.value = await res.json()
            showMessage("Processo atualizado com dados do Tribunal!", "success")
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao atualizar.", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão.", "error")
    } finally {
        isUpdating.value = false
    }
}

const handleDeleteProcesso = () => {
    confirmAction(
        'Tem certeza que deseja excluir este processo judicial? Esta ação não poderá ser desfeita.',
        async () => {
            try {
                const res = await apiFetch(`/api/processos/${processo.value.id}`, { method: 'DELETE' })
                if (res.ok) {
                    showMessage("Processo excluído com sucesso!")
                    setTimeout(() => router.push('/processos'), 1500)
                } else {
                    const err = await res.json()
                    showMessage(err.detail || "Erro ao excluir processo.", "error")
                }
            } catch (e) {
                showMessage("Erro de conexão.", "error")
            }
        },
        'Excluir Processo',
        'danger'
    )
}

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

const formatDate = (dateStr, includeTime = false) => {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    if (includeTime) {
        return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    }
    return d.toLocaleDateString('pt-BR')
}

// Lógica de Tarefas
const openNewTarefa = () => {
    isEditingTarefa.value = false
    selectedTarefa.value = {
        titulo: '',
        descricao: '',
        status: 'Pendente',
        prioridade: 'Normal',
        data_vencimento: null,
        cliente_id: processo.value.cliente_id,
        processo_id: Number(route.params.id),
        responsavel_id: null
    }
    showTarefaModal.value = true
}

const openEditTarefa = (tarefa) => {
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
            // Recarregar tarefas
            const resT = await apiFetch(`/api/tarefas?processo_id=${route.params.id}`)
            if (resT.ok) tarefas.value = await resT.json()
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

const deleteTarefa = async (id) => {
    confirmAction("Tem certeza que deseja excluir esta tarefa?", async () => {
        try {
            const res = await apiFetch(`/api/tarefas/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Tarefa excluída!")
                tarefas.value = tarefas.value.filter(t => t.id !== id)
            } else {
                showMessage("Erro ao excluir tarefa", "error")
            }
        } catch (e) {
            showMessage("Erro de conexão.", "error")
        }
    }, "Excluir Tarefa", "danger")
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
        }
    } catch (e) {
        showMessage("Erro ao atualizar status", "error")
    }
}

// Watch for route changes (e.g. from /novo to /:id)
watch(() => route.params.id, (newId) => {
    if (newId) carregarDados()
})

onMounted(carregarDados)

const tabs = [
    { id: 'resumo', name: 'Resumo', icon: Scale },
    { id: 'timeline', name: 'Movimentações', icon: History },
    { id: 'tarefas', name: 'Tarefas', icon: CheckSquare },
    { id: 'partes', name: 'Partes e Assuntos', icon: Users },
    { id: 'documentos', name: 'Documentos', icon: FileText }
]
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex relative">
    
    <!-- Toast -->
    <div v-if="notification.show" 
         :class="['fixed top-4 right-4 z-[100] px-6 py-3 rounded-lg shadow-lg text-white font-medium flex items-center gap-3 transition-all animate-fade-in-down', 
                  notification.type === 'error' ? 'bg-red-600' : 'bg-emerald-600']">
        <component :is="notification.type === 'error' ? AlertCircle : CheckCircle2" class="w-5 h-5 flex-shrink-0" />
        <span>{{ notification.message }}</span>
    </div>

    <Sidebar :escritorio="escritorio" :usuario="currentUser" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col overflow-hidden">
      
      <!-- Top Header -->
      <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-30">
        <div class="flex items-center gap-4">
          <button @click="sidebarOpen = true" class="md:hidden p-2 text-slate-500 hover:text-slate-700">
            <Menu class="w-6 h-6" />
          </button>
          <button @click="router.push('/processos')" class="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors text-sm font-bold">
            <ArrowLeft class="w-4 h-4" /> Voltar
          </button>
        </div>

        <div class="flex items-center gap-4">
          <div class="relative">
            <button @click="showProfileMenu = !showProfileMenu" class="flex items-center gap-2 p-1.5 rounded-full hover:bg-slate-100 transition-colors focus:outline-none">
               <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700">
                 <span class="text-xs font-bold">{{ currentUser?.nome?.charAt(0).toUpperCase() }}</span>
               </div>
               <ChevronDown class="hidden md:block w-4 h-4 text-slate-400" />
            </button>
            <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-slate-100 py-1 z-50">
              <button @click="handleLogout" class="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50">
                <LogOut class="mr-3 h-4 w-4" /> Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div v-if="isLoading" class="animate-pulse space-y-8">
           <div class="h-32 bg-white rounded-[40px] shadow-sm ring-1 ring-slate-100"></div>
           <div class="h-96 bg-white rounded-[40px] shadow-sm ring-1 ring-slate-100"></div>
        </div>

        <div v-else-if="processo" class="space-y-6 animate-fade-in-up">
           
           <div v-if="isNew" class="mb-6">
              <h1 class="text-3xl font-black text-slate-900 leading-tight">Cadastrar Novo Processo</h1>
              <p class="text-slate-500 font-medium">Preencha os dados abaixo para o cadastro manual.</p>
           </div>

           <!-- Hero Header Card (Only if not new or not editing main info) -->
           <div v-if="!isNew && !showEditForm" class="bg-white rounded-[40px] shadow-sm ring-1 ring-slate-200 overflow-hidden group">
              <div class="h-2 bg-gradient-to-r from-primary-500 via-indigo-500 to-primary-600"></div>
              <div class="p-8 sm:flex sm:items-center sm:justify-between gap-8">
                 <div class="flex items-start gap-6">
                    <div class="w-20 h-20 rounded-[30px] bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center text-slate-400 shadow-inner group-hover:scale-105 transition-transform duration-500">
                       <Gavel class="w-10 h-10" />
                    </div>
                    <div>
                       <div class="flex items-center gap-3 mb-1">
                          <span class="text-[10px] bg-emerald-100 text-emerald-700 font-black px-2 py-0.5 rounded-full uppercase tracking-widest">{{ processo.status }}</span>
                          <span class="text-[10px] bg-primary-50 text-primary-700 font-bold px-2 py-0.5 rounded-full uppercase tracking-widest">{{ processo.grau }}</span>
                       </div>
                       <h1 class="text-3xl font-black text-slate-900 leading-tight">{{ processo.titulo }}</h1>
                       <div class="flex items-center gap-2 mt-2">
                          <span class="text-primary-600 font-black tracking-tight text-lg">{{ processo.numero_processo || 'NÃO INFORMADO' }}</span>
                          <span class="text-slate-300">|</span>
                          <span class="text-slate-500 font-bold text-sm uppercase">{{ processo.tribunal || 'INTERNAL' }}</span>
                       </div>
                    </div>
                 </div>
                 <div class="mt-6 sm:mt-0 flex gap-3">
                    <button v-if="processo.numero_processo"
                            @click="handleAtualizarDataJud" 
                            :disabled="isUpdating"
                            class="px-6 py-3 bg-indigo-50 text-indigo-700 font-black rounded-2xl hover:bg-indigo-100 transition-all flex items-center gap-2 border border-indigo-200 shadow-sm shadow-indigo-500/10 active:scale-95 disabled:opacity-50">
                       <RefreshCw :class="['w-5 h-5', isUpdating ? 'animate-spin' : '']" />
                       {{ isUpdating ? 'Sincronizando...' : 'Atualizar DataJud' }}
                    </button>
                    <button @click="showEditForm = true" class="p-3 bg-white text-slate-400 border border-slate-200 rounded-2xl hover:bg-slate-50 hover:text-primary-600 transition-all" title="Editar Processo">
                       <Pencil class="w-6 h-6" />
                    </button>
                    <button @click="handleDeleteProcesso" class="p-3 bg-white text-slate-400 border border-slate-200 rounded-2xl hover:bg-red-50 hover:text-red-600 transition-all" title="Excluir Processo">
                       <Trash2 class="w-6 h-6" />
                    </button>
                 </div>
              </div>
           </div>

           <!-- Multi-purpose Form Section -->
           <div v-if="isNew || showEditForm" class="animate-fade-in-up">
              <ProcessoForm 
                :modelValue="processo" 
                :isEditing="!isNew" 
                :isSubmitting="isSaving"
                @submit="handleSaveProcesso"
                @cancel="isNew ? router.push('/processos') : showEditForm = false"
              />
           </div>

           <template v-else>
              <!-- Tabs Navigation -->
              <div class="flex flex-wrap gap-2 p-1 bg-slate-200/50 rounded-2xl w-full sm:w-fit">
                 <button v-for="tab in tabs" 
                         :key="tab.id"
                         @click="activeTab = tab.id"
                         :class="[activeTab === tab.id ? 'bg-white text-primary-700 shadow-md font-black' : 'text-slate-500 hover:text-slate-800 font-bold', 'flex-1 sm:flex-none px-6 py-2.5 rounded-xl text-xs transition-all flex items-center justify-center sm:justify-start gap-2']">
                    <component :is="tab.icon" class="w-4 h-4" />
                    {{ tab.name }}
                 </button>
              </div>

              <!-- Tab Content: Resumo -->
              <div v-show="activeTab === 'resumo'" class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up">
                 <!-- Detail Grid -->
                 <div class="lg:col-span-2 space-y-6">
                    <div class="bg-white p-8 rounded-[40px] shadow-sm ring-1 ring-slate-100">
                       <h3 class="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                          <BookOpen class="w-5 h-5 text-primary-500" /> Detalhes do Processo
                       </h3>
                       <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-8">
                          <div v-for="field in [
                             { label: 'Classe Processual', val: processo.classe_nome, icon: Briefcase },
                             { label: 'Órgão Julgador', val: processo.orgao_julgador_nome, icon: Gavel },
                             { label: 'Sistema', val: processo.sistema_nome, icon: ShieldAlert },
                             { label: 'Formato', val: processo.formato_nome, icon: FileText }
                          ]" :key="field.label">
                             <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block flex items-center gap-2">
                                <component :is="field.icon" class="w-3 h-3" /> {{ field.label }}
                             </label>
                             <p class="text-sm font-bold text-slate-800">{{ field.val || 'Não informado' }}</p>
                          </div>
                          <div v-if="processo.area_direito">
                             <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block flex items-center gap-2">
                                <Scale class="w-3 h-3" /> Área do Direito
                             </label>
                             <p class="text-sm font-bold text-slate-800">{{ processo.area_direito }}</p>
                          </div>
                          <div v-if="processo.polo">
                             <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block flex items-center gap-2">
                                <Users class="w-3 h-3" /> Polo Assistido
                             </label>
                             <p class="text-sm font-bold text-slate-800">{{ processo.polo }}</p>
                          </div>
                          <div v-if="processo.servico">
                             <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block flex items-center gap-2">
                                <BadgeDollarSign class="w-3 h-3" /> Serviço Vinculado
                             </label>
                             <p class="text-sm font-bold text-slate-800">{{ processo.servico.descricao || 'Serviço sem descrição' }}</p>
                          </div>
                       </div>
                       <div class="mt-10 pt-8 border-t border-slate-50">
                          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Descrição / Notas Internas</label>
                          <p class="text-sm text-slate-600 leading-relaxed font-medium bg-slate-50 p-6 rounded-2xl italic">
                             {{ processo.descricao || 'Nenhuma descrição interna adicionada a este processo.' }}
                          </p>
                       </div>
                    </div>
                 </div>
                 <!-- Stats Sidebar -->
                 <div class="space-y-6">
                    <div class="bg-gradient-to-br from-primary-600 to-indigo-700 p-8 rounded-[40px] text-white shadow-xl shadow-primary-500/20">
                       <h4 class="text-white/70 text-[10px] font-black uppercase tracking-widest mb-6">Datas Chave</h4>
                       <div class="space-y-6">
                          <div class="flex items-center gap-4">
                             <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center"><Calendar class="w-5 h-5" /></div>
                             <div>
                                <p class="text-[10px] text-white/60 font-bold uppercase">Distribuição</p>
                                <p class="text-lg font-black">{{ formatDate(processo.data_ajuizamento || processo.data_criacao) }}</p>
                             </div>
                          </div>
                          <div class="flex items-center gap-4">
                             <div class="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center"><Clock class="w-5 h-5" /></div>
                             <div>
                                <p class="text-[10px] text-white/60 font-bold uppercase">Último Check</p>
                                <p class="text-lg font-black">{{ formatDate(processo.data_atualizacao, true) }}</p>
                             </div>
                          </div>
                       </div>
                    </div>
                    
                    <div v-if="processo.valor_causa" class="bg-white p-8 rounded-[40px] border border-slate-100 shadow-sm">
                       <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 block">Valor da Causa</label>
                       <p class="text-2xl font-black text-emerald-600">R$ {{ processo.valor_causa.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) }}</p>
                    </div>
                 </div>
              </div>

              <!-- Tab Content: Timeline -->
              <div v-show="activeTab === 'timeline'" class="bg-white p-8 rounded-[40px] shadow-sm ring-1 ring-slate-100 animate-fade-in-up">
                 <div class="flex items-center justify-between mb-10">
                    <h3 class="text-lg font-black text-slate-900 flex items-center gap-2">
                       <History class="w-5 h-5 text-primary-500" /> Histórico de Movimentações
                    </h3>
                    <div class="flex gap-2">
                       <button class="px-4 py-2 bg-slate-50 text-slate-600 font-bold text-xs rounded-xl hover:bg-slate-100 transition-all border border-slate-100">
                          Filtrar Eventos
                       </button>
                    </div>
                 </div>

                 <div class="relative pl-8 space-y-12 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
                    <div v-for="mov in (processo.movimentacoes || [])" :key="mov.id" class="relative group">
                       <div :class="['absolute -left-[25px] top-1.5 w-3 h-3 rounded-full ring-4 ring-white shadow-sm transition-all group-hover:scale-125 z-10', mov.tipo === 'externa' ? 'bg-primary-500' : 'bg-emerald-500']"></div>
                       <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-4">
                          <div class="max-w-2xl">
                             <h4 class="text-sm font-black text-slate-900 group-hover:text-primary-700 transition-colors">{{ mov.nome_movimento }}</h4>
                             <p v-if="mov.descricao" class="text-xs text-slate-500 mt-1 font-medium leading-relaxed">{{ mov.descricao }}</p>
                             <div v-if="mov.complementos_json" class="mt-2 flex flex-wrap gap-2">
                                <span v-for="(val, key) in JSON.parse(mov.complementos_json || '{}')" :key="key" class="text-[9px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-lg border border-slate-200 font-bold">
                                   {{ val.valor || val.descricao || val }}
                                </span>
                             </div>
                          </div>
                          <div class="text-right flex-shrink-0">
                             <span class="text-[10px] font-black text-slate-400 block uppercase">{{ formatDate(mov.data_hora, true) }}</span>
                             <span :class="['text-[8px] font-bold px-1.5 py-0.5 rounded uppercase mt-1 inline-block', mov.tipo === 'externa' ? 'text-blue-600 bg-blue-50' : 'text-emerald-600 bg-emerald-50']">
                                {{ mov.tipo === 'externa' ? 'Tribunal' : 'Interno' }}
                             </span>
                          </div>
                       </div>
                    </div>
                    <div v-if="!(processo.movimentacoes?.length)" class="text-center py-20">
                       <p class="text-slate-400 font-bold text-sm">Nenhuma movimentação registrada.</p>
                    </div>
                 </div>
              </div>

              <!-- Tab Content: Tarefas -->
              <div v-show="activeTab === 'tarefas'" class="bg-white p-8 rounded-[40px] shadow-sm ring-1 ring-slate-100 animate-fade-in-up">
                 <div class="flex items-center justify-between mb-10">
                    <h3 class="text-lg font-black text-slate-900 flex items-center gap-2">
                       <CheckSquare class="w-5 h-5 text-primary-500" /> Tarefas do Processo
                    </h3>
                    <button @click="openNewTarefa" class="px-6 py-3 bg-primary-600 text-white font-black text-xs rounded-2xl hover:bg-primary-700 transition-all flex items-center gap-2 shadow-lg shadow-primary-500/20 active:scale-95">
                       <Plus class="w-4 h-4" /> Nova Tarefa
                    </button>
                 </div>

                 <div class="space-y-4">
                    <div v-for="tarefa in tarefas" :key="tarefa.id" 
                         class="p-6 bg-slate-50/50 rounded-3xl border border-slate-100 group transition-all hover:bg-white hover:shadow-xl hover:shadow-slate-200/40 relative overflow-hidden">
                       
                       <!-- Barra Lateral de Prioridade -->
                       <div :class="['absolute left-0 top-0 bottom-0 w-1.5 transition-all', 
                          tarefa.prioridade === 'Urgente' ? 'bg-red-500' : 
                          tarefa.prioridade === 'Alta' ? 'bg-orange-500' : 
                          tarefa.prioridade === 'Normal' ? 'bg-sky-500' : 'bg-slate-300']"></div>

                       <div class="flex items-center gap-6">
                          <!-- Checkbox Custom -->
                          <button @click="toggleTarefaStatus(tarefa)" 
                                  :class="['w-8 h-8 rounded-xl border-2 flex items-center justify-center transition-all', 
                                  tarefa.status === 'Concluída' ? 'bg-emerald-500 border-emerald-500 text-white shadow-lg shadow-emerald-500/30' : 'bg-white border-slate-200 text-slate-200 hover:border-primary-500']">
                             <Check class="w-5 h-5" />
                          </button>

                          <div class="flex-1">
                             <div class="flex items-center gap-3 mb-1">
                                <h4 :class="['text-base font-black transition-all', tarefa.status === 'Concluída' ? 'text-slate-400 line-through' : 'text-slate-900']">
                                   {{ tarefa.titulo }}
                                </h4>
                                <TarefaBadge type="prioridade" :value="tarefa.prioridade" />
                                <TarefaBadge type="status" :value="tarefa.status" />
                             </div>
                             <p v-if="tarefa.descricao" class="text-xs text-slate-500 font-medium line-clamp-1">{{ tarefa.descricao }}</p>
                             
                             <div class="mt-4 flex items-center gap-6">
                                <div v-if="tarefa.data_vencimento" class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                   <Calendar class="w-3.5 h-3.5" /> 
                                   Vence {{ formatDate(tarefa.data_vencimento) }}
                                </div>
                                <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                   <User class="w-3.5 h-3.5" /> 
                                   Responsável: {{ tarefa.responsavel_id ? 'Atribuído' : 'Não atribuído' }}
                                </div>
                             </div>
                          </div>

                          <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                             <button @click="openEditTarefa(tarefa)" class="p-2 hover:bg-slate-100 rounded-xl text-slate-400 hover:text-primary-600 transition-colors">
                                <Edit2 class="w-4 h-4" />
                             </button>
                             <button @click="deleteTarefa(tarefa.id)" class="p-2 hover:bg-red-50 rounded-xl text-slate-400 hover:text-red-600 transition-colors">
                                <Trash2 class="w-4 h-4" />
                             </button>
                          </div>
                       </div>
                    </div>

                    <div v-if="!tarefas.length" class="text-center py-20 bg-slate-50/30 rounded-[40px] border-2 border-dashed border-slate-100">
                       <div class="w-16 h-16 bg-white rounded-2xl shadow-sm border border-slate-100 flex items-center justify-center mx-auto mb-4">
                          <CheckSquare class="w-8 h-8 text-slate-200" />
                       </div>
                       <p class="text-slate-400 font-bold text-sm">Nenhuma tarefa vinculada a este processo.</p>
                       <button @click="openNewTarefa" class="mt-4 text-primary-600 font-black text-xs uppercase tracking-widest hover:text-primary-700">
                          Criar Primeira Tarefa
                       </button>
                    </div>
                 </div>
              </div>

              <!-- Tab Content: Partes e Assuntos -->
              <div v-show="activeTab === 'partes'" class="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up">
                 <!-- Partes -->
                 <div class="bg-white p-8 rounded-[40px] shadow-sm ring-1 ring-slate-100">
                    <h3 class="text-lg font-black text-slate-900 mb-8 flex items-center gap-2">
                       <Users class="w-5 h-5 text-primary-500" /> Partes do Processo
                    </h3>
                    <div class="space-y-4">
                       <div v-for="parte in (processo.partes || [])" :key="parte.id" class="p-5 bg-slate-50/50 rounded-3xl border border-slate-100 group transition-all hover:bg-white hover:shadow-lg hover:shadow-slate-200/50">
                          <div class="flex items-center justify-between">
                             <div class="flex items-center gap-4">
                                <div class="w-10 h-10 rounded-2xl bg-white border border-slate-200 flex items-center justify-center text-slate-400 font-bold">
                                   {{ parte.nome.charAt(0) }}
                                </div>
                                <div>
                                   <h4 class="text-sm font-black text-slate-900">{{ parte.nome }}</h4>
                                   <p class="text-[10px] font-bold text-primary-600 uppercase tracking-widest">{{ parte.tipo_parte }}</p>
                                </div>
                             </div>
                          </div>
                          <div v-if="parte.advogado_nome" class="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2">
                             <div class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center"><Briefcase class="w-3 h-3 text-slate-400" /></div>
                             <span class="text-[10px] font-bold text-slate-500">{{ parte.advogado_nome }} <span v-if="parte.advogado_oab" class="text-slate-300">| {{ parte.advogado_oab }}</span></span>
                          </div>
                       </div>
                       <div v-if="!(processo.partes?.length)" class="text-center py-10 text-slate-400 text-xs font-bold">
                          Nenhuma parte vinculada oficialmente via DataJud.
                       </div>
                    </div>
                 </div>
                 <!-- Assuntos -->
                 <div class="bg-white p-8 rounded-[40px] shadow-sm ring-1 ring-slate-100">
                    <h3 class="text-lg font-black text-slate-900 mb-8 flex items-center gap-2">
                       <BookOpen class="w-5 h-5 text-primary-500" /> Assuntos (TPU)
                    </h3>
                    <div class="flex flex-wrap gap-3">
                       <div v-for="assunto in (processo.assuntos || [])" :key="assunto.id" :class="[assunto.principal ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-slate-50 border-slate-200 text-slate-600', 'px-4 py-3 rounded-2xl border font-bold text-xs flex items-center gap-2 shadow-sm']">
                          <component :is="assunto.principal ? ShieldAlert : BookOpen" class="w-4 h-4" />
                          {{ assunto.nome }}
                          <span v-if="assunto.codigo_tpu" class="text-[9px] opacity-60 font-black">#{{ assunto.codigo_tpu }}</span>
                       </div>
                       <div v-if="!(processo.assuntos?.length)" class="text-center py-10 text-slate-400 text-xs font-bold w-full">
                          Nenhum assunto TPU importado.
                       </div>
                    </div>
                 </div>
              </div>

              <!-- Tab Content: Documentos -->
              <div v-show="activeTab === 'documentos'" class="animate-fade-in-up">
                  <FileExplorer 
                      contextType="processo" 
                      :contextId="processo.id" 
                      :clienteId="processo.cliente_id"
                      title="Pasta Digital do Processo"
                  />
              </div>
           </template>

        </div>
      </main>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[999] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up">
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

    <TarefaFormModal :show="showTarefaModal" 
                     :tarefa="selectedTarefa" 
                     :isEditing="isEditingTarefa" 
                     :isSubmitting="isSubmittingTarefa" 
                     :processoId="Number(route.params.id)" 
                     :clienteId="processo?.cliente_id"
                     @close="showTarefaModal = false" 
                     @submit="handleTarefaSubmit" />
  </div>
</template>

<style scoped>
.animate-fade-in-down { animation: fade-in-down 0.4s ease-out; }
.animate-fade-in-up { animation: fade-in-up 0.4s ease-out; }

@keyframes fade-in-down {
  0% { opacity: 0; transform: translateY(-20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>
