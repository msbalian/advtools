<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import ProcessoForm from '../components/ProcessoForm.vue'
import FileExplorer from '../components/FileExplorer.vue'
import TarefaBadge from '../components/TarefaBadge.vue'
import TarefaFormModal from '../components/TarefaFormModal.vue'
import TarefaCard from '../components/TarefaCard.vue'
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
  User,
  Brain,
  Zap,
  Cpu
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
                
                // Carregar análise persistida se houver
                if (processo.value.analise_ia) {
                    try {
                        analiseIaResult.value = JSON.parse(processo.value.analise_ia)
                    } catch (e) {
                        console.error("Erro ao dar parse na analise salva", e)
                    }
                }
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

const aprovarSugestaoIA = async (tarefa) => {
    try {
        const res = await apiFetch(`/api/tarefas/${tarefa.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'Pendente' })
        })
        if (res.ok) {
            const updated = await res.json()
            const index = tarefas.value.findIndex(t => t.id === tarefa.id)
            if (index !== -1) tarefas.value[index] = updated
            showMessage("Tarefa aprovada e movida para o fluxo de trabalho!", "success")
        }
    } catch (e) {
        showMessage("Erro ao aprovar tarefa.", "error")
    }
}

const descartarSugestaoIA = async (tarefaId) => {
    confirmAction("Deseja descartar esta sugestão da IA?", async () => {
        try {
            const res = await apiFetch(`/api/tarefas/${tarefaId}`, { method: 'DELETE' })
            if (res.ok) {
                tarefas.value = tarefas.value.filter(t => t.id !== tarefaId)
                showMessage("Sugestão descartada.", "success")
            }
        } catch (e) {
            showMessage("Erro ao descartar sugestão.", "error")
        }
    }, "Descartar Sugestão", "danger")
}

// ==========================
// Estado da Análise IA
// ==========================
const isAnalyzingIa = ref(false)
const analiseIaResult = ref(null)

const handleAnaliseIa = async () => {
    if (!processo.value?.id) return
    isAnalyzingIa.value = true
    try {
        const res = await apiFetch(`/api/processos/${processo.value.id}/analisar-ia`, {
            method: 'POST'
        })
        if (res.ok) {
            const data = await res.json()
            if (data.erro) {
                analiseIaResult.value = data
                showMessage(data.erro, "error")
            } else {
                analiseIaResult.value = data
                showMessage("Análise IA concluída e sugestões de tarefas geradas!", "success")
                // Recarrega o processo para pegar as novas tarefas criadas pela IA
                await carregarDados()
            }
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro inesperado na análise IA.", "error")
        }
    } catch (e) {
        showMessage("Erro ao conectar com o serviço de IA.", "error")
    } finally {
        isAnalyzingIa.value = false
    }
}

const isGeneratingTasks = ref(false)
const handleGerarTarefasIA = async () => {
    isGeneratingTasks.value = true
    try {
        const res = await apiFetch(`/api/processos/${processo.value.id}/gerar-tarefas-ia`, { method: 'POST' })
        if (res.ok) {
            showMessage("Tarefas geradas com sucesso a partir da análise!", "success")
            await carregarDados()
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro ao gerar tarefas.", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão.", "error")
    } finally {
        isGeneratingTasks.value = false
    }
}

const isTJGO = computed(() => {
    if (!processo.value?.numero_processo) return false
    const limpo = processo.value.numero_processo.replace(/[.-]/g, '')
    if (limpo.length !== 20) return false
    return limpo[13] === '8' && limpo.substring(14, 16) === '09'
})

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

const handleAtualizarProcesso = async () => {
    if (!processo.value?.numero_processo || isNew.value) return
    isUpdating.value = true
    try {
        const endpoint = isTJGO.value ? `/api/processos/${processo.value.id}/atualizar-mni` : `/api/processos/${processo.value.id}/atualizar-datajud`
        const res = await apiFetch(endpoint, {
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
    { id: 'analise', name: 'Análise IA', icon: Brain },
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
                            @click="handleAtualizarProcesso" 
                            :disabled="isUpdating"
                            :class="['px-6 py-3 font-black rounded-2xl transition-all flex items-center gap-2 border shadow-sm active:scale-95 disabled:opacity-50',
                                     isTJGO ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border-emerald-200 shadow-emerald-500/10' : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-indigo-200 shadow-indigo-500/10']">
                       <RefreshCw :class="['w-5 h-5', isUpdating ? 'animate-spin' : '']" />
                       {{ isUpdating ? 'Sincronizando...' : (isTJGO ? 'Atualizar PROJUDI' : 'Atualizar DataJud') }}
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

              <!-- Tab Content: Análise IA -->
              <div v-show="activeTab === 'analise'" class="bg-gradient-to-br from-amber-50 to-orange-50 p-8 rounded-[40px] shadow-sm ring-1 ring-amber-100 animate-fade-in-up">
                 <div class="flex items-center justify-between mb-10">
                    <div>
                        <h3 class="text-lg font-black text-amber-900 flex items-center gap-2">
                           <Brain class="w-6 h-6 text-amber-600" /> Inteligência Artificial
                        </h3>
                        <p class="text-xs text-amber-700 font-medium mt-1">Análise de prazos e extração de insights usando o Gemini</p>
                        <p v-if="processo?.data_analise_ia && !isAnalyzingIa" class="text-[10px] text-amber-600 font-black mt-1 uppercase tracking-widest bg-amber-100/50 px-2 py-0.5 rounded-full inline-block">
                            Última atualização: {{ formatDate(processo.data_analise_ia, true) }}
                        </p>
                    </div>
                     <div class="flex gap-3">
                        <button v-if="analiseIaResult && !isAnalyzingIa" 
                                @click="handleGerarTarefasIA" 
                                :disabled="isGeneratingTasks"
                                class="px-6 py-3 bg-white text-amber-600 font-bold text-xs rounded-2xl hover:bg-amber-50 transition-all flex items-center gap-2 border border-amber-200 active:scale-95 disabled:opacity-50">
                           <Sparkles v-if="!isGeneratingTasks" class="w-4 h-4" />
                           <RefreshCw v-else class="w-4 h-4 animate-spin" />
                           Sincronizar Tarefas
                        </button>
                        <button @click="handleAnaliseIa" :disabled="isAnalyzingIa" class="px-6 py-3 bg-amber-500 text-white font-black text-xs rounded-2xl hover:bg-amber-600 transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20 active:scale-95 disabled:opacity-50">
                           <Cpu v-if="!isAnalyzingIa" class="w-4 h-4" />
                           <RefreshCw v-else class="w-4 h-4 animate-spin" />
                           {{ isAnalyzingIa ? 'Analisando...' : (analiseIaResult ? 'Atualizar Análise' : 'Gerar Análise') }}
                        </button>
                     </div>
                 </div>

                 <!-- Estado Vazio -->
                 <div v-if="!analiseIaResult && !isAnalyzingIa" class="text-center py-20 bg-white/50 backdrop-blur-sm rounded-[30px] border border-amber-200/50">
                    <Zap class="w-12 h-12 text-amber-300 mx-auto mb-4" />
                    <h4 class="text-xl font-black text-amber-900">Nenhuma análise disponível</h4>
                    <p class="text-sm text-amber-700 mt-2 max-w-md mx-auto">Solicite à inteligência artificial para examinar todo o histórico do processo e identificar prazos, tarefas e pontos de atenção urgentes.</p>
                 </div>

                 <!-- Loading State -->
                 <div v-if="isAnalyzingIa" class="py-20 text-center">
                    <div class="relative w-24 h-24 mx-auto mb-6">
                        <div class="absolute inset-0 border-4 border-amber-200 rounded-full animate-pulse"></div>
                        <div class="absolute inset-0 border-4 border-amber-500 rounded-full animate-spin border-t-transparent"></div>
                        <Brain class="w-10 h-10 text-amber-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                    </div>
                    <h4 class="text-lg font-black text-amber-900 animate-pulse">Lendo milhares de páginas...</h4>
                    <p class="text-sm text-amber-700 mt-2 font-medium">O modelo Gemini está raciocinando sobre as peças judiciais.</p>
                 </div>

                 <!-- Resultados -->
                 <div v-if="analiseIaResult && !isAnalyzingIa" class="space-y-6">
                     <!-- Mensagem de Erro da IA -->
                     <div v-if="analiseIaResult.erro" class="p-6 bg-red-50 border border-red-200 rounded-[30px] flex items-center gap-4 text-red-700">
                         <ShieldAlert class="w-8 h-8 flex-shrink-0" />
                         <div>
                             <h4 class="font-black uppercase text-xs tracking-widest mb-1">Falha na Inteligência Artificial</h4>
                             <p class="text-sm font-medium">{{ analiseIaResult.erro }}</p>
                             <p class="text-[10px] mt-2 opacity-70">Verifique sua Chave do Gemini nas configurações do escritório ou no arquivo de ambiente.</p>
                         </div>
                     </div>

                     <!-- Card Resumo (Somente se não houver erro crítico) -->
                     <div v-if="!analiseIaResult.erro || analiseIaResult.resumoHistoria" class="bg-white p-6 rounded-[30px] border border-amber-100 shadow-sm">
                         <h4 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-3">Resumo Processual</h4>
                         <p v-if="analiseIaResult.resumoHistoria" class="text-slate-700 text-sm leading-relaxed font-medium whitespace-pre-wrap">{{ analiseIaResult.resumoHistoria }}</p>
                         <p v-else-if="analiseIaResult.textoRaw" class="text-slate-700 text-sm leading-relaxed font-medium whitespace-pre-wrap">{{ analiseIaResult.textoRaw }}</p>
                         <p v-else class="text-slate-400 text-sm italic">O resumo não pôde ser estruturado para este processo.</p>
                     </div>

                     <!-- Alertas Grid -->
                     <div v-if="analiseIaResult.alertas?.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                         <div v-for="(alerta, index) in analiseIaResult.alertas" :key="'alerta-'+index" 
                              :class="['p-5 rounded-2xl border', alerta.urgencia === 'ALTA' ? 'bg-red-50 border-red-200' : 'bg-orange-50 border-orange-200']">
                             <div class="flex items-start gap-3">
                                 <ShieldAlert :class="['w-5 h-5 flex-shrink-0', alerta.urgencia === 'ALTA' ? 'text-red-500' : 'text-orange-500']" />
                                 <div>
                                     <h5 :class="['text-xs font-black uppercase mb-1', alerta.urgencia === 'ALTA' ? 'text-red-800' : 'text-orange-800']">{{ alerta.tipo }}</h5>
                                     <p :class="['text-sm font-medium leading-snug', alerta.urgencia === 'ALTA' ? 'text-red-900' : 'text-orange-900']">{{ alerta.mensagem }}</p>
                                 </div>
                             </div>
                         </div>
                     </div>

                     <!-- Tarefas Recomendadas -->
                     <div v-if="analiseIaResult.tarefasPendentes?.length > 0">
                         <h4 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 mt-8">Ações Recomendadas</h4>
                         <div class="space-y-3">
                             <div v-for="(tarefa, index) in analiseIaResult.tarefasPendentes" :key="'taref-'+index" 
                                  class="flex items-center justify-between p-5 bg-white border border-slate-100 rounded-2xl shadow-sm group">
                                 <div>
                                     <div class="flex items-center gap-2 mb-1">
                                         <BadgeDollarSign v-if="tarefa.acao.toLowerCase().includes('pagar') || tarefa.acao.toLowerCase().includes('custas')" class="w-4 h-4 text-emerald-500" />
                                         <FileSearch v-else class="w-4 h-4 text-indigo-500" />
                                         <span class="text-sm font-black text-slate-800">{{ tarefa.acao }}</span>
                                     </div>
                                     <p v-if="tarefa.observacao" class="text-xs text-slate-500 font-medium ml-6">{{ tarefa.observacao }}</p>
                                 </div>
                                 <div class="text-right flex-shrink-0">
                                     <div v-if="tarefa.prazoDataFim || tarefa.prazoDiasUteis" class="bg-amber-100 text-amber-800 text-[10px] font-black px-2 py-1 rounded-lg uppercase">
                                         <span v-if="tarefa.prazoDataFim">Prazo: {{ tarefa.prazoDataFim }}</span>
                                         <span v-else>{{ tarefa.prazoDiasUteis }} dias úteis</span>
                                     </div>
                                 </div>
                             </div>
                         </div>
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

                 <div class="grid grid-cols-1 gap-4">
                       <TarefaCard 
                          v-for="tarefa in tarefas" 
                          :key="tarefa.id" 
                          :tarefa="tarefa"
                          :showProcessInfo="false"
                          @edit="openEditTarefa"
                          @delete="deleteTarefa"
                          @toggle-status="toggleTarefaStatus"
                          @aprovar-ia="aprovarSugestaoIA"
                          @descartar-ia="descartarSugestaoIA"
                       />
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
