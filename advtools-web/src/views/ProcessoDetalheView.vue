<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import ProcessoForm from '../components/ProcessoForm.vue'
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
  Wand2
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

// Watch for route changes (e.g. from /novo to /:id)
watch(() => route.params.id, (newId) => {
    if (newId) carregarDados()
})

// Lógica de Pastas e Documentos
const loadPastasDocs = async () => {
    if (isNew.value || !processo.value) return
    
    try {
        const pId = currentFolderId.value === -1 ? null : currentFolderId.value
        // Usamos null literal na query se for raiz para o backend entender filter(parent_id == None)
        const pIdParam = pId === null ? 'null' : pId
        const [resP, resD] = await Promise.all([
            apiFetch(`/api/pastas?processo_id=${processo.value.id}&parent_id=${pIdParam}`),
            apiFetch(`/api/clientes/${processo.value.cliente_id}/documentos?pasta_id=${pIdParam}`)
        ])
        
        if (resP.ok) pastas.value = await resP.json()
        if (resD.ok) {
            const allDocs = await resD.json()
            // Filtramos documentos que pertencem a este processo especificamente
            documentos.value = allDocs.filter(d => d.pasta_id === (pId || null))
        }
    } catch (e) {
        console.error("Erro ao carregar arquivos:", e)
    }
}

const openFolder = async (folder) => {
    currentFolderId.value = folder.id
    breadcrumbs.value.push({ id: folder.id, nome: folder.nome })
    await loadPastasDocs()
}

const navToBreadcrumb = async (index, breadcrumb) => {
    if (index === breadcrumbs.value.length - 1) return
    currentFolderId.value = breadcrumb.id
    breadcrumbs.value = breadcrumbs.value.slice(0, index + 1)
    await loadPastasDocs()
}

const triggerUpload = () => fileInput.value?.click()

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    isUploadingDoc.value = true
    try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('nome', file.name)
        formData.append('pasta_id', currentFolderId.value === -1 ? -1 : currentFolderId.value)
        
        const res = await apiFetch(`/api/clientes/${processo.value.cliente_id}/documentos`, {
            method: 'POST',
            body: formData
        })

        if (res.ok) {
            showMessage("Documento enviado com sucesso!")
            await loadPastasDocs()
        } else {
            const err = await res.json()
            showMessage(err.detail || "Erro no upload", "error")
        }
    } catch (e) {
        showMessage("Erro de conexão no upload", "error")
    } finally {
        isUploadingDoc.value = false
        if (event.target) event.target.value = ''
    }
}

const showNewFolderModal = ref(false)
const newFolderName = ref('')
const isSavingFolder = ref(false)

const handleCreateFolder = async () => {
    if (!newFolderName.value.trim()) return
    isSavingFolder.value = true
    try {
        const payload = {
            nome: newFolderName.value,
            cliente_id: processo.value.cliente_id,
            processo_id: processo.value.id,
            parent_id: currentFolderId.value === -1 ? null : currentFolderId.value
        }
        const res = await apiFetch('/api/pastas', {
            method: 'POST',
            body: JSON.stringify(payload)
        })
        if (res.ok) {
            showMessage("Pasta criada!")
            newFolderName.value = ''
            showNewFolderModal.value = false
            await loadPastasDocs()
        }
    } catch (e) {
        showMessage("Erro ao criar pasta", "error")
    } finally {
        isSavingFolder.value = false
    }
}

// Organizador Inteligente
const organizarPasta = async () => {
    if (currentFolderId.value === -1) {
        showMessage("Selecione uma pasta para organizar", "error")
        return
    }
    isOrganizing.value = true
    progressModalOpen.value = true
    try {
        const res = await apiFetch(`/api/pastas/${currentFolderId.value}/organizar`, { method: 'POST' })
        if (res.ok) {
            const job = await res.json()
            currentJobId.value = job.job_id
            pollJobStatus()
        } else {
            const err = await res.json()
            throw new Error(err.detail || "Erro ao iniciar organização")
        }
    } catch (e) {
        showMessage(e.message, "error")
        isOrganizing.value = false
        progressModalOpen.value = false
    }
}

const pollJobStatus = async () => {
    if (!currentJobId.value) return
    try {
        const res = await apiFetch(`/api/pastas/jobs/${currentJobId.value}`)
        if (res.ok) {
            const job = await res.json()
            jobProgress.value = job
            if (job.status === 'completed') {
                isOrganizing.value = false
                currentJobId.value = null
                showMessage("Organização concluída!")
                await loadPastasDocs()
                setTimeout(() => { progressModalOpen.value = false }, 2000)
            } else if (job.status === 'failed') {
                isOrganizing.value = false
                showMessage("Falha na organização: " + job.message, "error")
            } else {
                setTimeout(pollJobStatus, 2000)
            }
        }
    } catch (e) {
        console.error("Erro ao checar job", e)
    }
}

// Helpers
const getFileExtension = (path) => path?.split('.').pop().toLowerCase() || 'file'
const formatSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
const getDocumentUrl = (doc) => {
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    let path = doc.arquivo_path
    if (!path) return '#'
    let cleanPath = path.startsWith('static/') ? path.replace('static/', '', 1) : path
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('http')) {
        cleanPath = `armazenamento/${cleanPath}`
    }
    return `${baseURL}/static/${cleanPath}`
}

watch(activeTab, (val) => {
    if (val === 'documentos') loadPastasDocs()
})

onMounted(carregarDados)

const tabs = [
    { id: 'resumo', name: 'Resumo', icon: Scale },
    { id: 'timeline', name: 'Movimentações', icon: History },
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
               <div v-show="activeTab === 'documentos'" class="space-y-6 animate-fade-in-up">
                  <!-- Toolbar -->
                  <div class="bg-white p-4 rounded-3xl shadow-sm border border-slate-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                     <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
                        <template v-for="(b, idx) in breadcrumbs" :key="b.id">
                           <button @click="navToBreadcrumb(idx, b)" 
                                   :class="[idx === breadcrumbs.length - 1 ? 'text-primary-700 font-black' : 'text-slate-500 hover:text-slate-800 font-bold', 'text-xs whitespace-nowrap px-2 py-1 rounded-lg hover:bg-slate-50 transition-all']">
                              {{ b.nome }}
                           </button>
                           <ChevronRight v-if="idx < breadcrumbs.length - 1" class="w-3 h-3 text-slate-300" />
                        </template>
                     </div>
                     <div class="flex flex-wrap items-center gap-2">
                        <button @click="organizarPasta" :disabled="isOrganizing" class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 rounded-xl text-xs font-black shadow-sm hover:bg-purple-200 transition-all active:scale-95 disabled:opacity-50">
                           <Sparkles class="w-4 h-4" /> {{ isOrganizing ? 'Organizando...' : 'Auto-Organizar' }}
                        </button>
                        <router-link :to="`/redator?cliente=${processo.cliente_id}`" class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-black shadow-lg shadow-indigo-500/20 hover:bg-indigo-700 transition-all active:scale-95">
                           <Wand2 class="w-4 h-4" /> Gerar Documento
                        </router-link>
                        <button @click="showNewFolderModal = true" class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-slate-100 text-slate-700 rounded-xl text-xs font-black hover:bg-slate-200 transition-all active:scale-95">
                           <FolderPlus class="w-4 h-4" /> Nova Pasta
                        </button>
                        <button @click="triggerUpload" :disabled="isUploadingDoc" class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl text-xs font-black shadow-lg shadow-primary-500/20 hover:bg-primary-700 transition-all active:scale-95 disabled:opacity-50">
                           <FileUp class="w-4 h-4" /> {{ isUploadingDoc ? 'Enviando...' : 'Upload' }}
                        </button>
                        <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" />
                     </div>
                  </div>

                  <!-- Folder & Files Grid -->
                  <div v-if="pastas.length === 0 && documentos.length === 0" class="bg-white rounded-[40px] border border-slate-200 border-dashed p-12 sm:p-20 text-center">
                     <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FileText class="w-8 h-8 text-slate-300" />
                     </div>
                     <h3 class="text-slate-900 font-black text-xl mb-2">Sua pasta de documentos está vazia</h3>
                     <p class="text-slate-500 text-sm font-medium mt-1 mb-10 max-w-sm mx-auto">Comece a organizar este processo agora. Você pode criar pastas, enviar arquivos ou gerar documentos com IA.</p>
                     
                     <div class="flex flex-wrap justify-center gap-4">
                        <button @click="showNewFolderModal = true" class="flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 text-slate-700 rounded-2xl text-sm font-black hover:bg-slate-50 transition-all shadow-sm">
                           <FolderPlus class="w-5 h-5 text-amber-500" /> Criar Primeira Pasta
                        </button>
                        <button @click="triggerUpload" class="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-2xl text-sm font-black hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/20">
                           <FileUp class="w-5 h-5" /> Fazer Upload de Arquivos
                        </button>
                        <router-link :to="`/redator?cliente=${processo.cliente_id}`" class="flex items-center gap-2 px-6 py-3 bg-indigo-50 text-indigo-700 rounded-2xl text-sm font-black hover:bg-indigo-100 transition-all border border-indigo-100">
                           <Wand2 class="w-5 h-5 text-purple-600" /> Gerar Petição com IA
                        </router-link>
                     </div>
                  </div>
                  
                  <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                     <!-- Pastas -->
                     <div v-for="pasta in pastas" :key="'p'+pasta.id" @click="openFolder(pasta)" class="group bg-white p-5 rounded-[30px] shadow-sm border border-slate-100 hover:shadow-xl hover:shadow-slate-200/50 hover:border-primary-200 transition-all cursor-pointer relative overflow-hidden">
                        <div class="flex items-center gap-4">
                           <div class="w-12 h-12 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-500 group-hover:scale-110 transition-transform duration-500">
                              <Folder class="w-6 h-6 fill-amber-500/20" />
                           </div>
                           <div class="flex-1 min-w-0">
                              <h3 class="text-sm font-black text-slate-900 truncate" :title="pasta.nome">{{ pasta.nome }}</h3>
                              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{{ formatSize(pasta.tamanho_total) }} • Pasta</p>
                           </div>
                        </div>
                     </div>

                     <!-- Documentos -->
                     <div v-for="doc in documentos" :key="'d'+doc.id" class="group bg-white p-5 rounded-[30px] shadow-sm border border-slate-100 hover:shadow-xl hover:shadow-slate-200/50 hover:border-primary-200 transition-all relative overflow-hidden">
                        <div class="flex items-center gap-4">
                           <div class="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-500 group-hover:scale-110 transition-transform duration-500">
                              <FileText class="w-6 h-6" />
                           </div>
                           <div class="flex-1 min-w-0">
                              <h3 class="text-sm font-black text-slate-900 truncate" :title="doc.nome">{{ doc.nome }}</h3>
                              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{{ formatSize(doc.tamanho) }} • {{ getFileExtension(doc.arquivo_path) }}</p>
                           </div>
                        </div>
                        <div class="absolute inset-0 bg-white/95 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center gap-2">
                           <a :href="getDocumentUrl(doc)" target="_blank" class="p-3 bg-primary-50 text-primary-600 rounded-2xl hover:bg-primary-600 hover:text-white transition-all shadow-sm">
                              <Download class="w-5 h-5" />
                           </a>
                           <button class="p-3 bg-slate-50 text-slate-600 rounded-2xl hover:bg-slate-200 transition-all shadow-sm">
                              <ExternalLink class="w-5 h-5" />
                           </button>
                        </div>
                     </div>
                  </div>
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
    <!-- Modal Nova Pasta -->
    <div v-if="showNewFolderModal" class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/60 backdrop-blur-md">
      <div class="bg-white rounded-[40px] shadow-2xl p-10 max-w-lg w-full mx-4 animate-fade-in-up border border-slate-100">
         <div class="flex items-center justify-between mb-8">
            <h3 class="text-2xl font-black text-slate-900 flex items-center gap-3">
               <FolderPlus class="w-8 h-8 text-primary-600" /> Nova Pasta
            </h3>
            <button @click="showNewFolderModal = false" class="p-2 hover:bg-slate-100 rounded-full transition-colors"><X class="w-6 h-6 text-slate-400" /></button>
         </div>
         <div class="space-y-6">
            <div>
               <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Nome da Pasta</label>
               <input v-model="newFolderName" type="text" placeholder="Ex: Documentos da Inicial" 
                      class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-primary-500/10 focus:border-primary-500 outline-none transition-all font-bold" />
            </div>
            <div class="flex gap-4 pt-4">
               <button @click="showNewFolderModal = false" class="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-black hover:bg-slate-200 transition-all">Cancelar</button>
               <button @click="handleCreateFolder" :disabled="isSavingFolder" 
                       class="flex-1 py-4 bg-primary-600 text-white rounded-2xl font-black shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 transition-all disabled:opacity-50">
                  {{ isSavingFolder ? 'Criando...' : 'Criar Pasta' }}
               </button>
            </div>
         </div>
      </div>
    </div>

    <!-- Modal Progresso Organizador Inteligente -->
    <div v-if="progressModalOpen" class="fixed inset-0 z-[1010] flex items-center justify-center bg-slate-900/70 backdrop-blur-lg">
      <div class="bg-white rounded-[40px] shadow-2xl p-12 max-w-xl w-full mx-4 animate-fade-in-up text-center relative overflow-hidden">
         <div class="absolute top-0 left-0 right-0 h-2 bg-slate-100 overflow-hidden">
            <div class="h-full bg-gradient-to-r from-purple-500 via-indigo-500 to-primary-500 transition-all duration-500 ease-out" 
                 :style="{ width: jobProgress.progress + '%' }"></div>
         </div>
         
         <div class="mt-4 mb-10 inline-flex items-center justify-center w-24 h-24 rounded-[35px] bg-purple-50 text-purple-600 shadow-inner">
            <Sparkles :class="['w-12 h-12', isOrganizing ? 'animate-pulse' : '']" />
         </div>

         <h3 class="text-3xl font-black text-slate-900 mb-2">Organizador Inteligente</h3>
         <p class="text-slate-500 font-bold mb-10 italic">"Analisando, classificando e renomeando seus documentos judiciais..."</p>
         
         <div class="bg-slate-50 rounded-3xl p-8 mb-10 border border-slate-100">
            <div class="flex items-center justify-between mb-2">
               <span class="text-[10px] font-black uppercase text-slate-400 tracking-widest">Progresso IA</span>
               <span class="text-sm font-black text-primary-600">{{ Math.round(jobProgress.progress) }}%</span>
            </div>
            <div class="w-full h-3 bg-slate-200 rounded-full overflow-hidden mb-6">
                <div class="h-full bg-primary-500 transition-all duration-500" :style="{ width: jobProgress.progress + '%' }"></div>
            </div>
            <p class="text-sm font-bold text-slate-700">{{ jobProgress.message || 'Iniciando análise...' }}</p>
         </div>

         <button @click="progressModalOpen = false" v-if="!isOrganizing" class="w-full py-5 bg-slate-100 text-slate-700 rounded-3xl font-black hover:bg-slate-200 transition-all">
            Fechar
         </button>
      </div>
    </div>
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
