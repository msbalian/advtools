<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  FileText, 
  UploadCloud, 
  Trash2, 
  RefreshCw, 
  Search,
  Plus,
  Download,
  Folder,
  FolderPlus,
  ChevronRight,
  X,
  Sparkles,
  Loader2,
  ChevronDown,
  Wand2
} from 'lucide-vue-next'
import { apiFetch } from '../utils/api'

const props = defineProps({
  contextType: {
    type: String,
    required: true, // 'cliente', 'processo', 'escritorio'
  },
  contextId: {
    type: [Number, String],
    required: true,
  },
  clienteId: {
    type: [Number, String],
    required: false, // Necessário para salvar arquivos em contexto de processo
  },
  title: {
    type: String,
    default: 'Documentos e Arquivos'
  }
})

const router = useRouter()

// Estado
const loading = ref(true)
const isUploading = ref(false)
const isOrganizing = ref(false)
const searchQuery = ref('')
const sortBy = ref('nome')
const currentFolderId = ref(-1)
const breadcrumbs = ref([{ id: -1, nome: 'Raiz' }])
const pastas = ref([])
const documentos = ref([])
const showDocMenu = ref(false)
const showNewFolderModal = ref(false)
const newFolderName = ref('')
const isSavingFolder = ref(false)
const fileInput = ref(null)
const replaceInput = ref(null)
const replacingId = ref(null)

// Job Progress (Organizador)
const progressModalOpen = ref(false)
const currentJobId = ref(null)
const jobProgress = ref({ status: '', progress: 0, message: '' })

// Notificações locais simples
const localMessage = ref({ show: false, text: '', type: 'success' })
const showLocalMessage = (text, type = 'success') => {
  localMessage.value = { show: true, text, type }
  setTimeout(() => localMessage.value.show = false, 3000)
}

// Confirm Dialog Customizado
const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'primary' })
const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'primary') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}

// Configuração de Endpoints baseada no contexto
const getEndpoints = () => {
  if (props.contextType === 'escritorio') {
    return {
      docs: props.title === 'Modelos de Automação' 
        ? `/api/documentos/escritorio?tags=modelo` 
        : `/api/documentos/escritorio?pasta_id=${currentFolderId.value}`,
      pastas: props.title === 'Modelos de Automação'
        ? `/api/pastas?cliente_id=0&parent_id=-999` // Força lista vazia de pastas se for modelos
        : `/api/pastas?cliente_id=0&parent_id=${currentFolderId.value}`,
      upload: `/api/documentos/escritorio`,
      createFolder: `/api/pastas`
    }
  }
  if (props.contextType === 'cliente') {
    return {
      docs: `/api/clientes/${props.contextId}/documentos?pasta_id=${currentFolderId.value}`,
      pastas: `/api/pastas?cliente_id=${props.contextId}&parent_id=${currentFolderId.value}`,
      upload: `/api/clientes/${props.contextId}/documentos`,
      createFolder: `/api/pastas`
    }
  }
  if (props.contextType === 'processo') {
    // Para processos, listamos documentos da pasta específica que pertence ao processo
    const pIdParam = currentFolderId.value === -1 ? 'null' : currentFolderId.value
    return {
        docs: `/api/clientes/${props.clienteId}/documentos?pasta_id=${pIdParam}`,
        pastas: `/api/pastas?processo_id=${props.contextId}&parent_id=${pIdParam}`,
        upload: `/api/clientes/${props.clienteId}/documentos`,
        createFolder: `/api/pastas`
    }
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const endpoints = getEndpoints()
    const [resDocs, resPastas] = await Promise.all([
      apiFetch(endpoints.docs),
      apiFetch(endpoints.pastas)
    ])
    
    if (resDocs.ok) {
        const data = await resDocs.json()
        if (props.contextType === 'processo') {
            // No processo, filtramos apenas o que pertence à pasta (que já é filtrada na query do parent_id para pastas)
            documentos.value = data.filter(d => d.pasta_id === (currentFolderId.value === -1 ? null : currentFolderId.value))
        } else {
            documentos.value = data
        }
    }
    if (resPastas.ok) pastas.value = await resPastas.json()
  } catch (err) {
    showLocalMessage('Erro ao carregar arquivos', 'error')
  } finally {
    loading.value = false
  }
}

// Navegação
const openFolder = (folder) => {
  currentFolderId.value = folder.id
  breadcrumbs.value.push({ id: folder.id, nome: folder.nome })
  loadData()
}

const navToBreadcrumb = (index, bc) => {
  if (index === breadcrumbs.value.length - 1) return
  currentFolderId.value = bc.id
  breadcrumbs.value = breadcrumbs.value.slice(0, index + 1)
  loadData()
}

// Ações
const triggerUpload = () => fileInput.value?.click()
const triggerReplace = (id) => {
  replacingId.value = id
  replaceInput.value?.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  isUploading.value = true
  try {
    const endpoints = getEndpoints()
    const formData = new FormData()
    formData.append('file', file)
    formData.append('nome', file.name.split('.').slice(0, -1).join('.'))
    
    // Define pasta_id correta para o backend
    const pId = currentFolderId.value === -1 ? -1 : currentFolderId.value
    formData.append('pasta_id', pId)
    
    const res = await apiFetch(endpoints.upload, {
      method: 'POST',
      body: formData
    })

    if (res.ok) {
      showLocalMessage('Arquivo enviado com sucesso!')
      loadData()
    } else {
      const err = await res.json()
      showLocalMessage(err.detail || 'Erro no upload', 'error')
    }
  } catch (e) {
    showLocalMessage('Erro de conexão no upload', 'error')
  } finally {
    isUploading.value = false
    event.target.value = ''
  }
}

const handleReplaceUpload = async (event) => {
    const file = event.target.files[0]
    if (!file || !replacingId.value) return

    isUploading.value = true
    try {
        const formData = new FormData()
        formData.append('file', file)
        const res = await apiFetch(`/api/documentos/${replacingId.value}`, {
            method: 'PUT',
            body: formData
        })
        if (res.ok) {
            showLocalMessage('Arquivo substituído com sucesso!')
            loadData()
        } else {
            showLocalMessage('Erro ao substituir arquivo', 'error')
        }
    } catch (e) {
        showLocalMessage('Erro de conexão', 'error')
    } finally {
        isUploading.value = false
        replacingId.value = null
        event.target.value = ''
    }
}

const handleCreateFolder = async () => {
  if (!newFolderName.value.trim()) return
  isSavingFolder.value = true
  try {
    const payload = {
      nome: newFolderName.value,
      cliente_id: props.contextType === 'cliente' ? props.contextId : (props.contextType === 'processo' ? props.clienteId : null),
      processo_id: props.contextType === 'processo' ? props.contextId : null,
      parent_id: currentFolderId.value === -1 ? null : currentFolderId.value
    }
    const res = await apiFetch(`/api/pastas`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      showLocalMessage('Pasta criada!')
      showNewFolderModal.value = false
      newFolderName.value = ''
      loadData()
    } else {
      const err = await res.json()
      showLocalMessage(err.detail || 'Erro ao criar pasta', 'error')
    }
  } catch (e) {
    showLocalMessage('Erro de conexão', 'error')
  } finally {
    isSavingFolder.value = false
  }
}

const deleteDocumento = async (id) => {
    confirmAction('Deseja excluir este documento permanentemente?', async () => {
        try {
            const res = await apiFetch(`/api/documentos/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showLocalMessage('Documento excluído')
                loadData()
            }
        } catch (e) {
            showLocalMessage('Erro ao excluir', 'error')
        }
    }, 'Excluir Documento', 'red')
}

const deleteFolder = async (id) => {
    confirmAction('Excluir esta pasta? Só é possível se estiver vazia.', async () => {
        try {
            const res = await apiFetch(`/api/pastas/${id}`, { method: 'DELETE' })
            if (res.ok) {
                showLocalMessage('Pasta excluída')
                loadData()
            } else {
                const err = await res.json()
                showLocalMessage(err.detail || 'Erro ao excluir pasta', 'error')
            }
        } catch (e) {
            showLocalMessage('Erro de conexão', 'error')
        }
    }, 'Excluir Pasta', 'red')
}

// Auxiliares
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
        'PNG': 'bg-purple-50 text-purple-600 border-purple-100',
        'JPG': 'bg-purple-50 text-purple-600 border-purple-100',
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

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('pt-BR')
}

const getDocumentUrl = (doc, assinado = false) => {
    const path = assinado ? doc.arquivo_assinado_path : doc.arquivo_path
    if (!path) return '#'
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    let cleanPath = path
    if (!cleanPath.startsWith('armazenamento/') && !cleanPath.startsWith('static/')) {
        cleanPath = `armazenamento/${cleanPath}`
    }
    return `${baseUrl}/static/${cleanPath}`
}

// Organizador Inteligente
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
                showLocalMessage('Organização concluída!')
                loadData()
                setTimeout(() => { progressModalOpen.value = false }, 2000)
                return
            }
            if (job.status === 'failed') {
                isOrganizing.value = false
                currentJobId.value = null
                showLocalMessage('Erro: ' + job.message, 'error')
                setTimeout(() => { progressModalOpen.value = false }, 3000)
                return
            }
            setTimeout(pollJobStatus, 1500)
        }
    } catch (e) {
        setTimeout(pollJobStatus, 3000)
    }
}

const organizarPasta = async () => {
    if (currentFolderId.value === -1) return
    isOrganizing.value = true
    progressModalOpen.value = true
    jobProgress.value = { status: 'pending', progress: 0, message: 'Solicitando organização...' }
    try {
        const response = await apiFetch(`/api/pastas/${currentFolderId.value}/organizar`, { method: 'POST' })
        if (response.ok) {
            const data = await response.json()
            currentJobId.value = data.job_id
            pollJobStatus()
        } else {
            const err = await response.json()
            throw new Error(err.detail || 'Erro ao organizar')
        }
    } catch (e) {
        showLocalMessage(e.message, 'error')
        isOrganizing.value = false
        progressModalOpen.value = false
    }
}

// Ordenação e Filtro
const sortedContent = computed(() => {
    const query = searchQuery.value.toLowerCase()
    let filteredPastas = pastas.value.filter(p => p.nome.toLowerCase().includes(query))
    let filteredDocs = documentos.value.filter(d => d.nome.toLowerCase().includes(query))
    
    // Filtro especial para Modelos de Automação (apenas .docx)
    if (props.title === 'Modelos de Automação') {
        filteredDocs = filteredDocs.filter(d => {
            const ext = getFileExtension(d.arquivo_path).toLowerCase()
            return ext === 'docx' || ext === 'doc'
        })
    }
    
    const sorter = (a, b) => {
        if (sortBy.value === 'data') {
            const dateA = new Date(a.data_alteracao || a.data_criacao || 0)
            const dateB = new Date(b.data_alteracao || b.data_criacao || 0)
            return dateB - dateA
        }
        return a.nome.localeCompare(b.nome)
    }
    
    return {
        pastas: [...filteredPastas].sort(sorter),
        docs: [...filteredDocs].sort(sorter)
    }
})

// Lifecycle & Watchers
onMounted(loadData)
watch(() => props.contextId, loadData)
watch(() => props.contextType, loadData)

</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm ring-1 ring-slate-200 overflow-hidden">
    <!-- Header do Explorador -->
    <div class="px-5 py-5 sm:px-6 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
      <h3 class="text-base font-semibold leading-6 text-slate-900 flex items-center gap-2">
        <FileText class="w-5 h-5 text-sky-600" /> {{ title }}
      </h3>
      <div class="relative flex gap-2">
        <div class="relative">
          <button @click="showDocMenu = !showDocMenu" @blur="setTimeout(() => showDocMenu = false, 200)" class="text-xs font-medium text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1">
            Novo <ChevronDown class="w-3 h-3" />
          </button>
          
          <div v-if="showDocMenu" class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 py-1 z-20">
            <button @click="showNewFolderModal = true; showDocMenu = false" class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
              <FolderPlus class="w-4 h-4" /> Nova Pasta
            </button>
            <button @click="triggerUpload" class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
              <UploadCloud class="w-4 h-4" /> Enviar Arquivo
            </button>
            <router-link v-if="props.contextType === 'cliente'" :to="`/redator?cliente=${props.contextId}`" class="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-sky-600 flex items-center gap-2">
              <Wand2 class="w-4 h-4 text-purple-600" /> Redator Inteligente
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Barra de Ferramentas / Breadcrumbs -->
    <div class="px-5 py-3 bg-slate-50 border-b border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center text-sm font-medium text-slate-600 overflow-x-auto w-full sm:w-auto">
        <div class="flex items-center whitespace-nowrap" v-for="(bc, index) in breadcrumbs" :key="bc.id">
          <button @click="navToBreadcrumb(index, bc)" 
                  :class="index === breadcrumbs.length - 1 ? 'text-sky-700 font-bold' : 'hover:text-sky-600 transition-colors'">
            {{ bc.nome }}
          </button>
          <ChevronRight v-if="index < breadcrumbs.length - 1" class="w-4 h-4 mx-1 text-slate-400" />
        </div>
      </div>

      <div class="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
        <!-- Busca Rápida -->
        <div class="relative max-w-[180px]">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
          <input v-model="searchQuery" type="text" placeholder="Buscar..." 
                 class="w-full pl-8 pr-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs focus:ring-1 focus:ring-sky-500 outline-none" />
        </div>
        
        <!-- Ordem -->
        <div class="flex bg-white rounded-lg border border-slate-200 p-0.5">
          <button @click="sortBy = 'nome'" :class="['px-2 py-1 rounded-md text-[10px] font-bold transition-all', sortBy === 'nome' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-600']">
            A-Z
          </button>
          <button @click="sortBy = 'data'" :class="['px-2 py-1 rounded-md text-[10px] font-bold transition-all', sortBy === 'data' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-600']">
            DATA
          </button>
        </div>
      </div>
    </div>

    <!-- Organizador Inteligente (Se em pasta) -->
    <div v-if="currentFolderId !== -1" class="px-5 py-2.5 bg-purple-50/50 border-b border-purple-100 flex items-center justify-between">
      <div class="flex items-center gap-2">
         <Sparkles class="w-4 h-4 text-purple-600" />
         <span class="text-[10px] font-bold text-purple-700 uppercase tracking-wider">Pasta: {{ breadcrumbs[breadcrumbs.length-1]?.nome }}</span>
      </div>
      <button @click="organizarPasta" :disabled="isOrganizing" class="px-3 py-1 bg-purple-600 text-white rounded-lg text-[10px] font-black uppercase hover:bg-purple-700 transition-all disabled:opacity-50 flex items-center gap-1.5">
        {{ isOrganizing ? 'Processando...' : 'Organizar com IA' }}
      </button>
    </div>

    <!-- Upload Progress Overlay -->
    <div v-if="isUploading" class="px-5 py-3 bg-sky-50 border-b border-sky-100 flex justify-center items-center gap-2">
      <Loader2 class="animate-spin h-4 w-4 text-sky-600" />
      <span class="text-xs font-semibold text-sky-700">Aguarde, processando arquivo...</span>
    </div>

    <!-- Mensagem Local -->
    <div v-if="localMessage.show" :class="localMessage.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'" class="px-5 py-2 text-xs font-bold border-b transition-all">
      {{ localMessage.text }}
    </div>

    <!-- Listagem -->
    <div class="overflow-x-auto">
      <ul v-if="sortedContent.pastas.length > 0 || sortedContent.docs.length > 0" class="divide-y divide-slate-100 min-w-[600px]">
        <!-- Render Pastas -->
        <li v-for="pasta in sortedContent.pastas" :key="'p'+pasta.id" @click.self="openFolder(pasta)" class="px-5 py-3 hover:bg-slate-50 transition-colors cursor-pointer group flex items-center justify-between border-l-4 border-transparent hover:border-sky-400">
          <div class="flex items-center gap-3 w-full" @click="openFolder(pasta)">
            <div class="p-2 bg-slate-100 text-slate-500 rounded-lg group-hover:bg-sky-100 group-hover:text-sky-600 transition-colors">
              <Folder class="w-5 h-5" />
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-semibold text-slate-800 group-hover:text-sky-700 transition-colors">{{ pasta.nome }}</span>
              <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{{ formatSize(pasta.tamanho_total) }} • Pasta</span>
            </div>
          </div>
          <div class="flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
            <button @click.stop="deleteFolder(pasta.id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </li>

        <!-- Render Documentos -->
        <li v-for="doc in sortedContent.docs" :key="doc.id" class="px-5 py-4 hover:bg-slate-50 transition-colors group">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-lg flex items-center justify-center border font-black text-[9px] tracking-tighter"
                   :class="getExtensionColor(getFileExtension(doc.arquivo_path))">
                {{ getFileExtension(doc.arquivo_path) }}
              </div>
              <div class="flex flex-col">
                <span class="text-sm font-semibold text-slate-900">{{ doc.nome }}</span>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                    {{ formatSize(doc.tamanho) }} • {{ formatDate(doc.data_alteracao || doc.data_criacao) }}
                  </span>
                  <span v-if="doc.status_assinatura && doc.status_assinatura !== 'Aguardando'"
                        :class="[
                          doc.status_assinatura === 'Concluido' ? 'bg-green-50 text-green-700 border-green-200' : 
                          (doc.status_assinatura === 'Pendente' || doc.status_assinatura === 'Parcial') ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-50 text-slate-500 border-slate-200'
                        ]"
                        class="inline-flex items-center gap-1 text-[9px] font-black uppercase px-2 py-0.5 rounded-full border">
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
                <a v-if="doc.status_assinatura === 'Concluido' && doc.arquivo_assinado_path" 
                   :href="getDocumentUrl(doc, true)" target="_blank" 
                   class="px-3 py-1.5 text-[10px] font-black uppercase text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors shadow-sm whitespace-nowrap">
                   Assinado
                </a>
                <button v-if="doc.status_assinatura !== 'Parcial' && doc.status_assinatura !== 'Concluido'" 
                        @click="triggerReplace(doc.id)" 
                        class="p-2 text-slate-400 hover:text-amber-500 hover:bg-amber-50 rounded-lg transition-colors" 
                        title="Substituir Arquivo">
                  <UploadCloud class="w-4 h-4" />
                </button>
              </div>

              <!-- Link Assinaturas -->
              <router-link :to="{ name: 'gerenciar_assinaturas', params: { id: doc.id } }" 
                           class="px-2 py-1.5 text-[10px] font-bold text-sky-600 border border-sky-200 rounded-lg hover:bg-sky-50 transition-colors">
                Assinaturas
              </router-link>

              <button @click="deleteDocumento(doc.id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </li>
      </ul>
      <div v-else class="px-5 py-20 text-center flex flex-col items-center">
        <Loader2 v-if="loading" class="h-8 w-8 text-sky-400 animate-spin mb-2" />
        <div v-else>
            <Folder class="h-10 w-10 text-slate-200 mx-auto mb-2" />
            <p class="text-sm text-slate-400 font-medium">Nenhum arquivo ou pasta encontrada.</p>
        </div>
      </div>
    </div>

    <!-- Hidden Inputs -->
    <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" />
    <input type="file" ref="replaceInput" class="hidden" @change="handleReplaceUpload" />

    <!-- Modal Nova Pasta -->
    <div v-if="showNewFolderModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm" @click="showNewFolderModal = false"></div>
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 z-10 border border-slate-200 scale-in">
        <h3 class="text-lg font-bold text-slate-900 mb-4">Nova Pasta</h3>
        <input v-model="newFolderName" type="text" placeholder="Nome da pasta" 
               class="w-full px-4 py-2 border border-slate-200 rounded-xl mb-6 outline-none focus:ring-2 focus:ring-sky-500"
               @keyup.enter="handleCreateFolder" />
        <div class="flex justify-end gap-3">
          <button @click="showNewFolderModal = false" class="px-4 py-2 text-sm font-bold text-slate-500 hover:text-slate-700">Cancelar</button>
          <button @click="handleCreateFolder" :disabled="isSavingFolder" class="px-6 py-2 bg-primary-600 text-white rounded-xl text-sm font-bold disabled:opacity-50">
            {{ isSavingFolder ? 'Criando...' : 'Criar Pasta' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Progress Organizador -->
    <div v-if="progressModalOpen" class="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md"></div>
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg p-8 z-10 text-center border border-slate-100">
        <div class="mb-6 relative inline-block">
          <div class="h-20 w-20 rounded-2xl bg-purple-100 flex items-center justify-center mx-auto animate-pulse">
            <Sparkles class="h-10 w-10 text-purple-600" />
          </div>
          <div class="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-purple-600 flex items-center justify-center">
            <Loader2 class="h-3 w-3 text-white animate-spin" />
          </div>
        </div>
        
        <h3 class="text-2xl font-black text-slate-900 mb-2">Organizador Inteligente</h3>
        <p class="text-slate-500 text-sm mb-8 font-medium px-4">{{ jobProgress.message || 'Iniciando processamento com IA...' }}</p>
        
        <div class="w-full bg-slate-100 rounded-full h-3 mb-4 overflow-hidden p-0.5">
          <div class="bg-gradient-to-r from-purple-500 to-indigo-600 h-full rounded-full transition-all duration-500" 
               :style="{ width: jobProgress.progress + '%' }"></div>
        </div>
        <div class="text-xs font-black text-purple-700 uppercase tracking-widest">{{ jobProgress.progress }}% Concluído</div>
      </div>
    </div>

    <!-- Modal de Confirmação Customizado (Padrão do Projeto) -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up">
        <div class="text-center">
          <div :class="['mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4', confirmDialog.type === 'purple' ? 'bg-purple-100' : (confirmDialog.type === 'red' ? 'bg-red-100' : 'bg-primary-100')]">
            <Sparkles v-if="confirmDialog.type === 'purple'" class="h-6 w-6 text-purple-600" />
            <Trash2 v-else-if="confirmDialog.type === 'red'" class="h-6 w-6 text-red-600" />
            <FileText v-else class="h-6 w-6 text-primary-600" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
          <p class="text-sm text-slate-500 mb-6 font-medium leading-relaxed">{{ confirmDialog.message }}</p>
          <div class="flex gap-3 justify-center">
            <button @click="confirmDialog.show = false" class="px-5 py-2 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-colors">Cancelar</button>
            <button @click="executeConfirm" :class="['px-5 py-2 rounded-xl font-bold text-white transition-all', confirmDialog.type === 'purple' ? 'bg-purple-600 hover:bg-purple-700' : (confirmDialog.type === 'red' ? 'bg-red-600 hover:bg-red-700' : 'bg-primary-600 hover:bg-primary-700')]">
                Confirmar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scale-in {
    animation: scaleIn 0.2s ease-out;
}
@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}
</style>
