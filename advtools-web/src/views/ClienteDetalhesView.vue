<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import { Menu as MenuIcon } from 'lucide-vue-next'
import {
  ArrowLeft,
  User,
  MapPin,
  Briefcase,
  Phone,
  Mail,
  Calendar,
  Pencil,
  Plus,
  BadgeDollarSign,
  FileText,
  X,
  LogOut,
  Settings,
  ChevronDown,
  AlertCircle,
  CheckCircle2,
  Users,
  Trash2,
  Download,
  UploadCloud,
  Wand2,
  Folder,
  FolderPlus,
  ChevronRight,
  Sparkles,
  RefreshCw,
  Loader2
} from 'lucide-vue-next'
import ClienteForm from '../components/ClienteForm.vue'
import ServicoForm from '../components/ServicoForm.vue'
import ParteEnvolvidaForm from '../components/ParteEnvolvidaForm.vue'

const route = useRoute()
const router = useRouter()

const notification = ref({ show: false, message: '', type: 'success' })
const showMessage = (msg, type = 'success') => {
    notification.value = { show: true, message: msg, type }
    setTimeout(() => { notification.value.show = false }, 4000)
}

const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'primary' })
const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'primary') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

const cliente = ref(null)
const servicos = ref([])
const partes = ref([])
const documentos = ref([])
const pastas = ref([])
const currentFolderId = ref(-1)
const breadcrumbs = ref([{ id: -1, nome: 'Raiz' }])
const isLoading = ref(true)
const showProfileMenu = ref(false)
const currentUser = ref(null)
const sortBy = ref('nome') // 'nome' ou 'data'

const carregarUsuario = async () => {
    try {
        const res = await apiFetch('/api/me')
        if (res.ok) {
            currentUser.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar usuario", e)
    }
}

const handleLogout = () => {
    localStorage.removeItem('advtools_token')
    router.push('/')
}

const sidebarOpen = ref(false)

const loadDetalhes = async () => {
  isLoading.value = true
  try {
    // Fetch Cliente
    const resCliente = await apiFetch(`/api/clientes/${route.params.id}`)
    if (!resCliente.ok) throw new Error('Cliente não encontrado')
    cliente.value = await resCliente.json()

    // Fetch Serviços do Cliente
    const resServicos = await apiFetch(`/api/clientes/${route.params.id}/servicos`)
    if (resServicos.ok) {
        servicos.value = await resServicos.json()
    }

    // Fetch Partes Envolvidas
    const resPartes = await apiFetch(`/api/clientes/${route.params.id}/partes`)
    if (resPartes.ok) {
        partes.value = await resPartes.json()
    }

    // Fetch Documentos
    const resDocs = await apiFetch(`/api/clientes/${route.params.id}/documentos?pasta_id=${currentFolderId.value}`)
    if (resDocs.ok) {
        documentos.value = await resDocs.json()
    }

    // Fetch Pastas
    const resPastas = await apiFetch(`/api/pastas?cliente_id=${route.params.id}&parent_id=${currentFolderId.value}`)
    if (resPastas.ok) {
        pastas.value = await resPastas.json()
    }

  } catch (error) {
    if (error.message.includes('Sessão expirada')) return;
    console.error(error)
    showMessage("Erro ao carregar os dados do cliente.", "error")
    router.push('/clientes')
  } finally {
    isLoading.value = false
  }
}

// Lógica de Edição de Cliente (Modal)
const showEditClientModal = ref(false)
const isSavingClient = ref(false)
const formDataClient = ref({})

const openEditClient = () => {
    formDataClient.value = { ...cliente.value }
    showEditClientModal.value = true
}

const saveCliente = async (dados) => {
    isSavingClient.value = true
    try {
        const response = await apiFetch(`/api/clientes/${route.params.id}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao atualizar')
        
        await loadDetalhes()
        showEditClientModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar: " + e.message, "error")
    } finally {
        isSavingClient.value = false
    }
}

// Lógica de Criação/Edição de Serviço Contextualizado
const showNewServiceModal = ref(false)
const isSavingService = ref(false)
const isEditingService = ref(false)
const formDataService = ref({})

const escritorio = ref(null)

const carregarEscritorio = async () => {
    try {
        const res = await apiFetch('/api/escritorio')
        if (res.ok) {
            escritorio.value = await res.json()
        }
    } catch (e) {
        console.error("Erro ao carregar escritório", e)
    }
}

const getEmptyService = () => ({
  cliente_id: Number(route.params.id), 
  descricao: '', 
  data_contrato: '', 
  valor_total: 0, 
  qtd_parcelas: 1, 
  condicoes_pagamento: '', 
  porcentagem_exito: ''
})

const openNewService = () => {
    isEditingService.value = false
    formDataService.value = getEmptyService()
    showNewServiceModal.value = true
}

const openEditService = (servico) => {
    isEditingService.value = true
    formDataService.value = { ...servico }
    showNewServiceModal.value = true
}

const saveServico = async (dados) => {
    isSavingService.value = true
    try {
        let url = `/api/servicos`
        let method = 'POST'
        
        if (isEditingService.value) {
            url = `/api/servicos/${dados.id}`
            method = 'PUT'
        }

        const response = await apiFetch(url, {
            method: method,
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao salvar serviço')
        
        showMessage(isEditingService.value ? 'Serviço atualizado com sucesso!' : 'Serviço adicionado com sucesso!', 'success')
        await loadDetalhes() // Recarrega para mostrar o novo serviço
        showNewServiceModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar serviço: " + e.message, "error")
    } finally {
        isSavingService.value = false
    }
}

// Lógica de Partes Envolvidas
const showParteModal = ref(false)
const isSavingParte = ref(false)
const isEditingParte = ref(false)
const formDataParte = ref({})

const getEmptyParte = () => ({
    cliente_id: Number(route.params.id),
    nome: '',
    papel: '',
    documento: '',
    email: '',
    telefone: '',
    rg: '',
    data_nascimento: '',
    nacionalidade: '',
    estado_civil: '',
    profissao: '',
    cep: '',
    endereco: '',
    bairro: '',
    cidade: '',
    uf: ''
})

const openNewParte = () => {
    isEditingParte.value = false
    formDataParte.value = getEmptyParte()
    showParteModal.value = true
}

const openEditParte = (parte) => {
    isEditingParte.value = true
    formDataParte.value = { ...parte }
    showParteModal.value = true
}

const saveParte = async (dados) => {
    isSavingParte.value = true
    try {
        let url = `/api/partes`
        let method = 'POST'
        
        if (isEditingParte.value) {
            url = `/api/partes/${dados.id}`
            method = 'PUT'
        }

        const response = await apiFetch(url, {
            method: method,
            body: JSON.stringify(dados)
        })
        if (!response.ok) throw new Error('Falha ao salvar parte envolvida')
        
        showMessage(isEditingParte.value ? 'Parte atualizada com sucesso!' : 'Parte adicionada com sucesso!', 'success')
        await loadDetalhes()
        showParteModal.value = false
    } catch (e) {
        if (e.message.includes('Sessão expirada')) return;
        showMessage("Erro ao salvar parte: " + e.message, "error")
    } finally {
        isSavingParte.value = false
    }
}

const deleteParte = async (id) => {
    confirmAction("Tem certeza que deseja remover esta parte envolvida? Esta ação não pode ser desfeita.", async () => {
        try {
            const res = await apiFetch(`/api/partes/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Parte removida com sucesso!")
                await loadDetalhes()
            } else {
                throw new Error("Erro ao excluir")
            }
        } catch (e) {
            showMessage("Erro ao excluir parte envolvida", "error")
        }
    })
}

// Lógica de Documentos
const fileInput = ref(null)
const isUploadingDoc = ref(false)
const showDocMenu = ref(false)

const triggerUpload = () => {
    fileInput.value.click()
    showDocMenu.value = false
}

const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    isUploadingDoc.value = true
    const formData = new FormData()
    formData.append('file', file)
    let docName = file.name
    // remove extensão do nome para salvar bonito no banco
    const lastDot = docName.lastIndexOf('.')
    if (lastDot !== -1) docName = docName.substring(0, lastDot)
    
    // Usa o nome original sem perguntar
    formData.append('nome', docName)
    if (currentFolderId.value !== -1) {
        formData.append('pasta_id', currentFolderId.value)
    }

    try {
        const token = localStorage.getItem('advtools_token')
        const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        
        const response = await fetch(`${VITE_API_URL}/api/clientes/${route.params.id}/documentos`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
        })

        if (!response.ok) throw new Error('Falha no upload')
        showMessage("Upload concluído com sucesso!")
        await loadDetalhes()
    } catch (e) {
        showMessage("Erro no envio do documento", "error")
    } finally {
        isUploadingDoc.value = false
        event.target.value = ''
    }
}

const replaceInput = ref(null)
const replacingDocId = ref(null)

const triggerReplace = (docId) => {
    replacingDocId.value = docId
    replaceInput.value.click()
}

const handleReplaceUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    isUploadingDoc.value = true
    const formData = new FormData()
    formData.append('file', file)

    try {
        const token = localStorage.getItem('advtools_token')
        const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        
        const response = await fetch(`${VITE_API_URL}/api/documentos/${replacingDocId.value}`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
        })

        if (!response.ok) throw new Error('Falha ao substituir')
        showMessage("Documento substituído com sucesso!")
        await loadDetalhes()
    } catch (e) {
        showMessage("Erro ao substituir o documento", "error")
    } finally {
        isUploadingDoc.value = false
        replacingDocId.value = null
        event.target.value = ''
    }
}

const deleteDocumento = async (id) => {
    confirmAction("Tem certeza que deseja remover este documento?", async () => {
        try {
            const res = await apiFetch(`/api/documentos/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Documento removido sucesso!")
                await loadDetalhes()
            } else {
                throw new Error("Erro ao excluir")
            }
        } catch (e) {
            showMessage("Erro ao excluir documento", "error")
        }
    })
}

const getDocumentUrl = (doc, isAssinado = false) => {
    const path = isAssinado ? doc.arquivo_assinado_path : doc.arquivo_path
    if (!path) return '#'
    
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    let cleanPath = path.startsWith('static/') ? path.replace('static/', '', 1) : path
    
    // Se não for um caminho legado completo e não tiver o prefixo de armazenamento, adicionamos
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('http')) {
        cleanPath = `armazenamento/${cleanPath}`
    }
    
    return `${baseURL}/static/${cleanPath}`
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    if (dateString.includes('/')) return dateString
    if (dateString.includes('-')) {
        const parts = dateString.split('-')
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`
        }
    }
    return dateString
}

const getFileExtension = (path) => {
    if (!path) return 'FILE'
    const parts = path.split('.')
    return parts.length > 1 ? parts.pop().toUpperCase() : 'FILE'
}

const getExtensionColor = (ext) => {
    const colors = {
        'PDF': 'bg-red-50 text-red-600 border-red-100',
        'DOCX': 'bg-blue-50 text-blue-600 border-blue-100',
        'DOC': 'bg-blue-50 text-blue-600 border-blue-100',
        'XLSX': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'XLS': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'CSV': 'bg-emerald-50 text-emerald-600 border-emerald-100',
        'TXT': 'bg-slate-50 text-slate-600 border-slate-100',
        'PNG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPEG': 'bg-purple-50 text-purple-600 border-purple-100',
        'ZIP': 'bg-amber-50 text-amber-600 border-amber-100',
        'RAR': 'bg-amber-50 text-amber-600 border-amber-100'
    }
    return colors[ext] || 'bg-slate-50 text-slate-500 border-slate-100'
}
const formatSize = (bytes) => {
    if (!bytes && bytes !== 0) return '-'
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
const sortedContent = computed(() => {
    const query = '' // Aqui não tem busca global, mas podemos adicionar se quiser
    
    // Ordenação
    const sorter = (a, b) => {
        if (sortBy.value === 'data') {
            const dateA = new Date(a.data_alteracao || a.data_criacao || 0)
            const dateB = new Date(b.data_alteracao || b.data_criacao || 0)
            return dateB - dateA
        } else {
            return (a.nome || '').localeCompare(b.nome || '')
        }
    }
    
    return {
        pastas: [...pastas.value].sort(sorter),
        documentos: [...documentos.value].sort(sorter)
    }
})

// Lógica de Pastas
const openFolder = async (folder) => {
    currentFolderId.value = folder.id
    breadcrumbs.value.push({ id: folder.id, nome: folder.nome })
    await loadDetalhes()
}

const navToBreadcrumb = async (index, breadcrumb) => {
    if (index === breadcrumbs.value.length - 1) return
    currentFolderId.value = breadcrumb.id
    breadcrumbs.value = breadcrumbs.value.slice(0, index + 1)
    await loadDetalhes()
}

const showNewFolderModal = ref(false)
const formDataFolder = ref({ nome: '' })
const isSavingFolder = ref(false)

const handleCreateFolder = async () => {
    if (!formDataFolder.value.nome.trim()) {
        showMessage('Digite um nome para a pasta.', 'error')
        return
    }
    isSavingFolder.value = true
    try {
        const payload = {
            nome: formDataFolder.value.nome,
            cliente_id: Number(route.params.id),
            parent_id: currentFolderId.value === -1 ? null : currentFolderId.value
        }
        const response = await apiFetch(`/api/pastas`, {
            method: 'POST',
            body: JSON.stringify(payload)
        })
        if (!response.ok) throw new Error('Falha ao criar pasta')
        
        showMessage('Pasta criada com sucesso!')
        showNewFolderModal.value = false
        formDataFolder.value.nome = ''
        await loadDetalhes()
    } catch (e) {
        showMessage("Erro ao criar pasta: " + e.message, "error")
    } finally {
        isSavingFolder.value = false
    }
}

const deleteFolder = async (id) => {
    confirmAction("Deseja mesmo remover esta pasta? Só é possível remover pastas vazias.", async () => {
        try {
            const res = await apiFetch(`/api/pastas/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showMessage("Pasta removida!")
                await loadDetalhes()
            } else {
                const err = await res.json()
                throw new Error(err.detail || "Erro ao excluir pasta")
            }
        } catch (e) {
            showMessage(e.message, "error")
        }
    })
}

const isOrganizing = ref(false)
const currentJobId = ref(null)
const jobProgress = ref({ status: '', progress: 0, message: '' })
const progressModalOpen = ref(false)

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
                showMessage("Organização concluída com sucesso!")
                await loadDetalhes()
                setTimeout(() => { progressModalOpen.value = false }, 2000)
                return
            }
            
            if (job.status === 'failed') {
                isOrganizing.value = false
                currentJobId.value = null
                showMessage("Erro na organização: " + job.message, "error")
                setTimeout(() => { progressModalOpen.value = false }, 3000)
                return
            }
            
            // Continua polling
            setTimeout(pollJobStatus, 1500)
        }
    } catch (e) {
        console.error("Erro ao consultar job", e)
        setTimeout(pollJobStatus, 3000)
    }
}

const organizarPasta = async () => {
    if (currentFolderId.value === -1) return
    
    confirmAction("O Organizador Inteligente irá analisar seus arquivos, convertê-los para PDF e renomeá-los. Deseja iniciar?", async () => {
        isOrganizing.value = true
        progressModalOpen.value = true
        jobProgress.value = { status: 'pending', progress: 0, message: 'Solicitando organização...' }
        
        try {
            const response = await apiFetch(`/api/pastas/${currentFolderId.value}/organizar`, {
                method: 'POST'
            })
            if (!response.ok) {
                const err = await response.json()
                throw new Error(err.detail || "Erro ao organizar pasta")
            }
            const data = await response.json()
            currentJobId.value = data.job_id
            pollJobStatus()
        } catch (e) {
            showMessage(e.message, "error")
            isOrganizing.value = false
            progressModalOpen.value = false
        }
    }, "Organizador Inteligente", "purple")
}

onMounted(async () => {
  carregarEscritorio()
  carregarUsuario()
  await loadDetalhes()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex">
    <!-- Sidebar Centralizado -->
    <Sidebar :escritorio="escritorio" v-model:sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col overflow-hidden">

    <!-- Top Header -->
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 z-10 sticky top-0">
        <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-500 focus:outline-none">
                <MenuIcon class="w-6 h-6" />
            </button>
            <button @click="$router.push('/clientes')" class="flex items-center gap-2 text-slate-500 hover:text-primary-600 transition-colors text-sm font-medium">
                <ArrowLeft class="w-4 h-4" /> Voltar para Clientes
            </button>
        </div>

        <!-- Profile Dropdown -->
        <div class="relative ml-2">
          <button @click="showProfileMenu = !showProfileMenu" @blur="setTimeout(() => showProfileMenu = false, 200)" class="flex items-center gap-2 p-1.5 rounded-full hover:bg-slate-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
             <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center border border-primary-200 text-primary-700">
               <span class="text-xs font-bold">{{ currentUser ? currentUser.nome.charAt(0).toUpperCase() : 'U' }}</span>
             </div>
             <span class="hidden md:block text-sm font-medium text-slate-700">{{ currentUser ? currentUser.nome : 'Carregando...' }}</span>
             <ChevronDown class="hidden md:block w-4 h-4 text-slate-400" />
          </button>
          
          <!-- Dropdown Menu -->
          <div v-if="showProfileMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 focus:outline-none z-50 animate-fade-in-up" role="menu">
            <div class="px-4 py-3">
              <p class="text-sm text-slate-900 truncate">{{ currentUser ? currentUser.nome : 'Carregando...' }}</p>
              <p class="text-xs font-medium text-slate-500 truncate">{{ currentUser ? currentUser.email : '' }}</p>
            </div>
            <div class="py-1" role="none">
              <a href="#" class="group flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors" role="menuitem">
                <User class="mr-3 h-4 w-4 text-slate-400 group-hover:text-primary-500" aria-hidden="true" />
                Meu Perfil
              </a>
              <router-link to="/configuracoes" class="group flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-primary-600 transition-colors" role="menuitem">
                <Settings class="mr-3 h-4 w-4 text-slate-400 group-hover:text-primary-500" aria-hidden="true" />
                Configurações
              </router-link>
            </div>
            <div class="py-1" role="none">
              <button @click="handleLogout" class="group flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors" role="menuitem">
                <LogOut class="mr-3 h-4 w-4 text-red-500 group-hover:text-red-600" aria-hidden="true" />
                Sair do Sistema
              </button>
            </div>
          </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
        
        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="text-slate-500">Carregando painel do cliente...</div>
        </div>

        <div v-else-if="cliente" class="space-y-6 animate-fade-in-up">
            <!-- Controles de Ordenação (Global para Documentos/Pastas abaixo) -->
             <!-- Deslocado para perto da seção de documentos se preferir, mas aqui fica central -->
            
            <!-- Dashboard Cover & Header -->
            <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden relative">
                <div class="h-24 bg-gradient-to-r from-primary-600 to-indigo-600"></div>
                <div class="px-6 py-5 sm:flex sm:items-end sm:justify-between relative">
                    <div class="sm:flex sm:space-x-5">
                        <div class="relative -mt-16 flex h-24 w-24 items-center justify-center rounded-2xl bg-white ring-4 ring-white shadow-md overflow-hidden">
                            <User class="h-12 w-12 text-slate-300" />
                        </div>
                        <div class="mt-4 sm:mt-0 sm:pt-1">
                            <p class="text-xs font-medium text-primary-600 uppercase tracking-widest">Painel do Cliente</p>
                            <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">{{ cliente.nome }}</h1>
                            <p class="text-sm font-medium text-slate-500 mt-1">Cadastrado em {{ new Date(cliente.data_cadastro).toLocaleDateString('pt-BR') }}</p>
                        </div>
                    </div>
                    <div class="mt-5 flex justify-stretch space-x-3 sm:mt-0 sm:justify-end">
                        <button @click="openEditClient" type="button" class="btn-secondary inline-flex items-center justify-center gap-2">
                            <Pencil class="h-4 w-4" aria-hidden="true" />
                            Editar Cliente
                        </button>
                        <button @click="openNewService" type="button" class="btn-primary inline-flex items-center justify-center gap-2">
                            <Plus class="h-4 w-4" aria-hidden="true" />
                            Novo Serviço
                        </button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Coluna Esquerda: Dados Rápidos -->
                <div class="space-y-6 md:col-span-1">
                    
                    <!-- Card Contato -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 p-5">
                        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-4">Informações de Contato</h3>
                        <dl class="space-y-4">
                            <div class="flex items-start gap-3">
                                <Phone class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">Telefone / WhatsApp</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.telefone || 'Não informado' }}</dd>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <Mail class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">E-mail</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.email || 'Não informado' }}</dd>
                                </div>
                            </div>
                            <div class="flex items-start gap-3">
                                <MapPin class="w-5 h-5 text-slate-400 mt-0.5" />
                                <div>
                                    <dt class="text-xs font-medium text-slate-500">Endereço</dt>
                                    <dd class="text-sm font-medium text-slate-900 mt-0.5">
                                        {{ cliente.endereco ? `${cliente.endereco}, ${cliente.bairro || ''}. ${cliente.cidade || ''}/${cliente.uf || ''}` : 'Não informado' }}
                                    </dd>
                                </div>
                            </div>
                        </dl>
                    </div>

                    <!-- Card Documentação -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 p-5">
                        <h3 class="text-base font-semibold leading-6 text-slate-900 border-b border-slate-100 pb-3 mb-4">Documentação Pessoal</h3>
                        <dl class="grid grid-cols-2 gap-y-4 gap-x-2">
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">CPF / CNPJ</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.documento || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">RG</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.rg || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">Nascimento</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ formatDate(cliente.data_nascimento) || '-' }}</dd>
                            </div>
                            <div class="col-span-2 sm:col-span-1">
                                <dt class="text-xs font-medium text-slate-500">Estado Civil</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.estado_civil || '-' }}</dd>
                            </div>
                            <div class="col-span-2">
                                <dt class="text-xs font-medium text-slate-500">Profissão</dt>
                                <dd class="text-sm font-medium text-slate-900 mt-0.5">{{ cliente.profissao || '-' }}</dd>
                            </div>
                        </dl>
                    </div>

                </div>

                <!-- Coluna Direita: Serviços, Processos, Histórico -->
                <div class="space-y-6 md:col-span-2">
                    
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <BadgeDollarSign class="w-5 h-5 text-primary-600" /> Serviços Ativos
                            </h3>
                            <button @click="openNewService" class="text-xs font-medium text-primary-600 hover:text-primary-800 bg-primary-50 px-2 py-1 rounded-md transition-colors">
                                + Novo
                            </button>
                        </div>
                        <ul role="list" class="divide-y divide-slate-100">
                            <li v-if="servicos.length === 0" class="px-5 py-8 text-center text-sm text-slate-500">
                                Este cliente não possui nenhum serviço cadastrado.
                            </li>
                            <li v-for="servico in servicos" :key="servico.id" @click="openEditService(servico)" class="px-5 py-4 hover:bg-slate-50 transition-colors cursor-pointer group">
                                <div class="flex items-center justify-between">
                                    <div class="flex flex-col group-hover:pl-1 transition-all">
                                        <span class="text-sm font-semibold text-primary-600 group-hover:text-primary-800">{{ servico.descricao }}</span>
                                        <span class="text-xs text-slate-500 flex items-center mt-1">
                                            <Calendar class="w-3 h-3 mr-1 inline-block" /> 
                                            Registrado em: {{ new Date(servico.data_contratacao).toLocaleDateString() }} 
                                            | Honorários: R$ {{ servico.valor_total.toFixed(2) }}
                                        </span>
                                    </div>
                                    <div class="flex items-center">
                                       <span class="inline-flex items-center rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Ativo</span>
                                    </div>
                                </div>
                            </li>
                        </ul>
                    </div>

                    <!-- Card Partes Envolvidas -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <Users class="w-5 h-5 text-indigo-600" /> Partes Envolvidas
                            </h3>
                            <button @click="openNewParte" class="text-xs font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2 py-1 rounded-md transition-colors">
                                + Adicionar
                            </button>
                        </div>
                        <div class="overflow-x-auto">
                            <table v-if="partes.length > 0" class="min-w-full divide-y divide-slate-100">
                                <thead class="bg-slate-50/30">
                                    <tr>
                                        <th scope="col" class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Nome / Papel</th>
                                        <th scope="col" class="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Documento</th>
                                        <th scope="col" class="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Ações</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100">
                                    <tr v-for="parte in partes" :key="parte.id" class="hover:bg-slate-50 transition-colors group">
                                        <td class="px-5 py-4 whitespace-nowrap">
                                            <div class="flex flex-col">
                                                <span class="text-sm font-semibold text-slate-900">{{ parte.nome }}</span>
                                                <span class="text-xs text-indigo-600 font-medium">{{ parte.papel }}</span>
                                            </div>
                                        </td>
                                        <td class="px-5 py-4 whitespace-nowrap text-sm text-slate-500">
                                            {{ parte.documento || '-' }}
                                        </td>
                                        <td class="px-5 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div class="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button @click="openEditParte(parte)" class="p-1.5 text-slate-400 hover:text-primary-600 transition-colors">
                                                    <Pencil class="w-4 h-4" />
                                                </button>
                                                <button @click="deleteParte(parte.id)" class="p-1.5 text-slate-400 hover:text-red-600 transition-colors">
                                                    <Trash2 class="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div v-else class="px-5 py-8 text-center text-sm text-slate-500">
                                Nenhuma parte envolvida cadastrada para este cliente.
                            </div>
                        </div>
                    </div>

                    <!-- Card Documentos & Assinaturas -->
                    <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
                        <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
                            <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
                                <FileText class="w-5 h-5 text-sky-600" /> Documentos e Assinaturas
                            </h3>
                            <div class="relative">
                                <button @click="showDocMenu = !showDocMenu" @blur="setTimeout(() => showDocMenu = false, 200)" class="text-xs font-medium text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
                                    Novo Documento <ChevronDown class="w-3 h-3" />
                                </button>
                                
                                <div v-if="showDocMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 py-1 z-10">
                                    <button @click="showNewFolderModal = true; showDocMenu = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
                                        <FolderPlus class="w-4 h-4" /> Nova Pasta
                                    </button>
                                    <button @click="triggerUpload" class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
                                        <UploadCloud class="w-4 h-4" /> Enviar do PC
                                    </button>
                                    <router-link :to="`/redator?cliente=${cliente.id}`" class="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
                                        <Wand2 class="w-4 h-4 text-purple-600" /> Redator Inteligente
                                    </router-link>
                                </div>
                                <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" accept=".pdf,.doc,.docx" />
                                <input type="file" ref="replaceInput" class="hidden" @change="handleReplaceUpload" accept=".pdf,.doc,.docx" />
                            </div>
                        </div>
                        
                        <div v-if="isUploadingDoc" class="px-5 py-4 bg-sky-50 border-b border-sky-100 flex justify-center items-center gap-2">
                            <div class="animate-spin h-4 w-4 border-2 border-sky-600 border-t-transparent rounded-full"></div>
                            <span class="text-sm font-medium text-sky-700">Fazendo upload do documento...</span>
                        </div>

                        <!-- Breadcrumbs Pastas -->
                        <div class="px-5 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between overflow-x-auto">
                            <div class="flex items-center text-sm font-medium text-slate-600">
                                <div class="flex items-center" v-for="(bc, index) in breadcrumbs" :key="bc.id">
                                    <button @click="navToBreadcrumb(index, bc)" 
                                            :class="index === breadcrumbs.length - 1 ? 'text-sky-700' : 'hover:text-sky-600 transition-colors'">
                                        {{ bc.nome }}
                                    </button>
                                    <ChevronRight v-if="index < breadcrumbs.length - 1" class="w-4 h-4 mx-1 text-slate-400" />
                                </div>
                            </div>
                            <!-- Controles de Ordenação -->
                            <div class="flex items-center gap-2">
                                <button @click="sortBy = 'nome'" :class="['px-2 py-1 rounded text-[10px] font-bold transition-all', sortBy === 'nome' ? 'bg-sky-600 text-white' : 'bg-white text-slate-400 border border-slate-200 hover:bg-slate-50']">
                                    A-Z
                                </button>
                                <button @click="sortBy = 'data'" :class="['px-2 py-1 rounded text-[10px] font-bold transition-all', sortBy === 'data' ? 'bg-sky-600 text-white' : 'bg-white text-slate-400 border border-slate-200 hover:bg-slate-50']">
                                    Data
                                </button>
                            </div>
                        </div>

                        <div v-if="currentFolderId !== -1" class="px-5 py-3 bg-white border-b border-slate-100 flex items-center justify-between">
                            <span class="text-xs text-slate-400 font-medium">Pasta: {{ breadcrumbs[breadcrumbs.length-1]?.nome }}</span>
                            <button @click="organizarPasta" :disabled="isOrganizing" class="flex items-center gap-2 px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-100 rounded-lg text-xs font-bold hover:bg-purple-100 transition-all disabled:opacity-50">
                                <Sparkles class="w-3.5 h-3.5" /> {{ isOrganizing ? 'Organizando...' : 'Organizador Inteligente' }}
                            </button>
                        </div>

                        <div class="overflow-x-auto">
                            <ul v-if="documentos.length > 0 || pastas.length > 0" role="list" class="divide-y divide-slate-100">
                                <!-- Render Pastas -->
                                <li v-for="pasta in sortedContent.pastas" :key="'p'+pasta.id" @click.self="openFolder(pasta)" class="px-5 py-3 hover:bg-slate-50 transition-colors cursor-pointer group flex items-center justify-between border-l-4 border-transparent hover:border-sky-400">
                                    <div class="flex items-center gap-3 w-full" @click="openFolder(pasta)">
                                        <div class="p-2 bg-slate-100 text-slate-500 rounded-lg group-hover:bg-sky-100 group-hover:text-sky-600 transition-colors">
                                           <Folder class="w-5 h-5 flex-shrink-0" />
                                        </div>
                                        <div class="flex flex-col">
                                            <span class="text-sm font-semibold text-slate-800 group-hover:text-sky-700 transition-colors">{{ pasta.nome }}</span>
                                            <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{{ formatSize(pasta.tamanho_total) }} • Pasta</span>
                                        </div>
                                    </div>
                                    <div class="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button @click.stop="deleteFolder(pasta.id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Excluir Pasta">
                                            <Trash2 class="w-4 h-4" />
                                        </button>
                                    </div>
                                </li>
                                <!-- Render Documentos -->
                                <li v-for="doc in sortedContent.documentos" :key="doc.id" class="px-5 py-4 hover:bg-slate-50 transition-colors group">
                                    <div class="flex items-center justify-between">
                                        <div class="flex items-center gap-3">
                                            <div class="h-10 w-10 rounded-lg flex items-center justify-center border font-black text-[9px] tracking-tighter"
                                                 :class="getExtensionColor(getFileExtension(doc.arquivo_path))">
                                                {{ getFileExtension(doc.arquivo_path) }}
                                            </div>
                                            <div class="flex flex-col">
                                                <div class="flex items-center gap-2">
                                                    <span class="text-sm font-semibold text-slate-900">{{ doc.nome }}</span>
                                                </div>
                                                <div class="flex items-center gap-2 mt-1 flex-wrap">
                                                    <span class="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                                                        {{ formatSize(doc.tamanho) }} • {{ formatDate(doc.data_alteracao || doc.data_criacao) }}
                                                    </span>
                                                    <!-- Badge de status de assinatura -->
                                                    <span
                                                        v-if="doc.status_assinatura && doc.status_assinatura !== 'Aguardando'"
                                                        :class="{
                                                            'bg-amber-50 text-amber-700 border-amber-200': doc.status_assinatura === 'Pendente',
                                                            'bg-blue-50 text-blue-700 border-blue-200': doc.status_assinatura === 'Parcial',
                                                            'bg-green-50 text-green-700 border-green-200': doc.status_assinatura === 'Concluido',
                                                            'bg-red-50 text-red-700 border-red-200': doc.status_assinatura === 'Cancelado',
                                                            'bg-slate-50 text-slate-600 border-slate-200': !['Pendente','Parcial','Concluido','Cancelado'].includes(doc.status_assinatura),
                                                        }"
                                                        class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border"
                                                    >
                                                        <i class="fas fa-pen-nib" style="font-size:0.65rem"></i>
                                                        {{ doc.status_assinatura }}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="flex items-center gap-2">
                                           <div class="flex items-center gap-1">
                                               <a :href="getDocumentUrl(doc)" target="_blank" class="p-2 text-slate-400 hover:text-sky-600 hover:bg-sky-50 rounded-lg transition-colors" title="Baixar Original">
                                                   <Download class="w-4 h-4" />
                                               </a>
                                               <a v-if="doc.status_assinatura === 'Concluido' && doc.arquivo_assinado_path" :href="getDocumentUrl(doc, true)" target="_blank" class="px-3 py-1.5 text-xs font-semibold text-white bg-green-600 border border-green-700 rounded-md hover:bg-green-700 transition-colors flex items-center gap-1 shadow-sm" style="white-space: nowrap;" title="Baixar Arquivo Finalizado e Assinado">
                                                   <i class="fas fa-file-signature"></i> Baixar Assinado
                                               </a>
                                               <button v-if="doc.status_assinatura !== 'Parcial' && doc.status_assinatura !== 'Concluido'" 
                                                       @click="triggerReplace(doc.id)" 
                                                       class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors" 
                                                       title="Substituir Arquivo">
                                                   <UploadCloud class="w-4 h-4" />
                                               </button>
                                           </div>
                                           <!-- Gerenciar Assinaturas -->
                                           <router-link :to="{ name: 'gerenciar_assinaturas', params: { id: doc.id }, query: { clienteId: cliente.id, clienteNome: cliente.nome } }" class="px-3 py-1 text-xs font-medium text-sky-600 border border-sky-200 rounded-md hover:bg-sky-50 transition-colors flex items-center gap-1">
                                               <i class="fas fa-pen-nib"></i> Assinaturas
                                           </router-link>
                                           <button @click="deleteDocumento(doc.id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors ml-2" title="Excluir">
                                               <Trash2 class="w-4 h-4" />
                                           </button>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                            <div v-else class="px-5 py-8 text-center text-sm text-slate-500">
                                Nenhum documento gerado ou enviado ainda.
                            </div>
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </main>
    </div>

    <!-- Modal Editar Cliente -->
    <div v-if="showEditClientModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showEditClientModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2"><User class="w-5 h-5 text-primary-600" /> Editar Cliente</h3>
            <button @click="showEditClientModal = false" class="text-slate-400 hover:text-slate-500 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ClienteForm v-model="formDataClient" :is-submitting="isSavingClient" :is-editing="true" @submit="saveCliente" @cancel="showEditClientModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Serviço (Contextual) -->
    <div v-if="showNewServiceModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showNewServiceModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-primary-50">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <BadgeDollarSign class="w-5 h-5 text-primary-600" /> 
                {{ isEditingService ? 'Formulário de Serviço' : 'Novo Serviço Privado' }}: <span class="text-primary-700">{{ cliente?.nome }}</span>
            </h3>
            <button @click="showNewServiceModal = false" class="text-slate-500 hover:text-slate-900 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ServicoForm v-model="formDataService" :clientes="[cliente]" :is-submitting="isSavingService" :is-editing="isEditingService" @submit="saveServico" @cancel="showNewServiceModal = false" />
          </div>
        </div>
      </div>
    </div>
    <!-- Modal Parte Envolvida -->
    <div v-if="showParteModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showParteModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-slate-50 rounded-2xl text-left shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full overflow-hidden border border-slate-200">
          <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-indigo-50">
            <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                <Users class="w-5 h-5 text-indigo-600" /> 
                {{ isEditingParte ? 'Editar Parte Envolvida' : 'Nova Parte Envolvida' }}
            </h3>
            <button @click="showParteModal = false" class="text-slate-500 hover:text-slate-900 rounded-full p-1"><X class="w-5 h-5" /></button>
          </div>
          <div class="px-6 py-6 max-h-[80vh] overflow-y-auto">
             <ParteEnvolvidaForm v-model="formDataParte" :is-submitting="isSavingParte" :is-editing="isEditingParte" @submit="saveParte" @cancel="showParteModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[999] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up">
        <div class="text-center">
          <div :class="['mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4', confirmDialog.type === 'purple' ? 'bg-purple-100' : 'bg-red-100']">
            <Sparkles v-if="confirmDialog.type === 'purple'" class="h-6 w-6 text-purple-600" />
            <Trash2 v-else class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
          <p class="text-sm text-slate-500 mb-6">{{ confirmDialog.message }}</p>
          <div class="flex gap-3 justify-center">
            <button @click="confirmDialog.show = false" class="btn-secondary px-5 py-2">Cancelar</button>
            <button @click="executeConfirm" :class="['px-5 py-2 rounded-lg font-bold text-white transition-all', confirmDialog.type === 'purple' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-red-600 hover:bg-red-700']">
                Confirmar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Nova Pasta -->
    <div v-if="showNewFolderModal" class="fixed inset-0 z-[60] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" aria-hidden="true" @click="showNewFolderModal = false"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="relative inline-block align-bottom bg-white rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md w-full">
          <div class="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
             <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2"><FolderPlus class="w-5 h-5 text-sky-600" /> Nova Pasta</h3>
             <button @click="showNewFolderModal = false" class="text-slate-400 hover:text-slate-500 transition-colors"><X class="w-5 h-5" /></button>
          </div>
          <div class="p-6">
             <div class="space-y-4">
                 <div>
                     <label class="block text-sm font-medium text-slate-700 mb-1">Nome da Pasta</label>
                     <input v-model="formDataFolder.nome" type="text" class="block w-full rounded-xl border-0 py-2.5 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-sky-600 sm:text-sm sm:leading-6" placeholder="ex: Procurações" @keyup.enter="handleCreateFolder" />
                 </div>
             </div>
          </div>
          <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
             <button @click="showNewFolderModal = false" type="button" class="btn-secondary">Cancelar</button>
             <button @click="handleCreateFolder" :disabled="isSavingFolder" type="button" class="btn-primary">
                 {{ isSavingFolder ? 'Salvando...' : 'Criar Pasta' }}
             </button>
          </div>
        </div>
      </div>
    </div>

  </div>
    <!-- Modal de Progresso da Organização -->
    <div v-if="progressModalOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in-up">
            <div class="p-8 text-center">
                <div class="mb-6 relative flex justify-center">
                    <div class="absolute inset-0 bg-primary-100 rounded-full animate-ping opacity-20"></div>
                    <div class="relative bg-primary-50 p-5 rounded-full ring-8 ring-primary-50/50">
                        <Sparkles v-if="jobProgress.status !== 'completed'" class="w-10 h-10 text-primary-600 animate-pulse" />
                        <CheckCircle2 v-else class="w-10 h-10 text-emerald-600" />
                    </div>
                </div>
                
                <h3 class="text-xl font-black text-slate-900 mb-2">Organizador Inteligente</h3>
                <p class="text-slate-500 text-sm font-medium mb-8 leading-relaxed">
                    {{ jobProgress.message }}
                </p>

                <!-- Barra de Progresso -->
                <div class="relative pt-1">
                    <div class="flex mb-2 items-center justify-between">
                        <div>
                            <span class="text-xs font-black inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-50">
                                {{ jobProgress.status === 'completed' ? 'Finalizado' : 'Em andamento' }}
                            </span>
                        </div>
                        <div class="text-right">
                            <span class="text-xs font-black inline-block text-primary-600">
                                {{ jobProgress.progress }}%
                            </span>
                        </div>
                    </div>
                    <div class="overflow-hidden h-3 mb-4 text-xs flex rounded-full bg-slate-100">
                        <div :style="{ width: jobProgress.progress + '%' }" 
                             class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-primary-500 to-indigo-600 transition-all duration-500">
                        </div>
                    </div>
                </div>
                
                <div v-if="jobProgress.status === 'running' || jobProgress.status === 'pending'" class="mt-4 flex items-center justify-center gap-2 text-xs font-bold text-slate-400">
                    <Loader2 class="w-4 h-4 animate-spin" />
                    A IA está processando seus documentos...
                </div>
                
                <button v-if="jobProgress.status === 'completed' || jobProgress.status === 'failed'"
                        @click="progressModalOpen = false" 
                        class="mt-6 w-full py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-colors shadow-lg">
                    Fechar
                </button>
            </div>
        </div>
    </div>
</template>
