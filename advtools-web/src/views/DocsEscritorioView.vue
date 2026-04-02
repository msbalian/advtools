<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  FileText, 
  UploadCloud, 
  Trash2, 
  RefreshCw, 
  Search,
  Tag,
  Copy,
  CheckCircle2,
  Plus,
  PenTool,
  FileSpreadsheet,
  FileCode,
  FileDigit,
  FileBox,
  FileType,
  FileCheck,
  FileJson,
  FileVideo,
  FileImage,
  Music,
  FileDown,
  Building2,
  Wand2,
  Folder,
  FolderPlus,
  ChevronRight,
  X,
  Sparkles,
  Loader2
} from 'lucide-vue-next'
import { apiFetch, downloadFile } from '../utils/api'
import Sidebar from '../components/Sidebar.vue'
import FileExplorer from '../components/FileExplorer.vue'

const route = useRoute()
const router = useRouter()

// Estado Geral
const currentTab = ref(route.query.tab || 'modelos') // 'modelos' ou 'internos'
const loading = ref(true)
const searchQuery = ref('')
const sidebarOpen = ref(false)
const currentUser = ref(null)
const escritorio = ref(null)
const sortBy = ref('nome') // 'nome' ou 'data'

const confirmDialog = ref({ show: false, message: '', onConfirm: null, title: 'Confirmar Ação', type: 'primary' })
const confirmAction = (message, onConfirm, title = 'Confirmar Ação', type = 'primary') => {
    confirmDialog.value = { show: true, message, onConfirm, title, type }
}
const executeConfirm = async () => {
    if (confirmDialog.value.onConfirm) await confirmDialog.value.onConfirm()
    confirmDialog.value.show = false
}
const carregarDadosBase = async () => {
  try {
    const [resUser, resEsc] = await Promise.all([
      apiFetch('/api/me'),
      apiFetch('/api/escritorio')
    ])
    if (resUser.ok) currentUser.value = await resUser.json()
    if (resEsc.ok) escritorio.value = await resEsc.json()
  } catch (e) {
    console.error("Erro ao carregar dados base", e)
  }
}

// ==========================================
// ESTADO MODELOS
// ==========================================
const modelos = ref([])
const loadModelos = async () => {
  if (currentTab.value !== 'modelos') return
  loading.value = true
  try {
    const res = await apiFetch('/api/modelos')
    const data = await res.json()
    modelos.value = data
  } catch (err) {
    showToast('Erro ao carregar modelos', 'error')
  } finally {
    loading.value = false
  }
}

// Estado de Pastas e Documentos Internos removido: Gerenciado pelo FileExplorer
const currentFolderId = ref(-1)
const breadcrumbs = ref([{ id: -1, nome: 'Raiz' }])

// Lógica de Pastas e Auto-Organização removida: Gerenciada agora pelo componente FileExplorer


// ==========================================
// ESTADO UPLOAD / GESTÃO
// ==========================================
const isUploading = ref(false)
const fileInput = ref(null)
const replaceInput = ref(null)
const replacingId = ref(null)

const triggerUpload = () => {
  fileInput.value.click()
}

const triggerReplace = (id) => {
  replacingId.value = id
  replaceInput.value.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const isModelo = currentTab.value === 'modelos'
  if (isModelo && !file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos para modelos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('nome', file.name.split('.').slice(0, -1).join('.'))
  if (currentTab.value === 'internos' && currentFolderId.value !== -1) {
      formData.append('pasta_id', currentFolderId.value)
  }

  isUploading.value = true
  try {
    const endpoint = isModelo ? '/api/modelos' : '/api/documentos/escritorio'
    const res = await apiFetch(endpoint, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Erro ao enviar arquivo')
    }
    showToast('Arquivo enviado com sucesso')
    if (isModelo) loadModelos() 
    else {
        // Recarregar via componente será automático ou emitido?
        // Como o FileExplorer gerencia seu próprio estado, 
        // recarregar aqui não é necessário se usarmos FileExplorer
    }
  } catch (err) {
    showToast(err.message || 'Erro ao enviar arquivo', 'error')
  } finally {
    isUploading.value = false
    event.target.value = '' 
  }
}

const handleReplaceUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (currentTab.value === 'modelos' && !file.name.endsWith('.docx')) {
    return showToast('Apenas arquivos .docx são permitidos para modelos', 'error')
  }

  const formData = new FormData()
  formData.append('file', file)

  isUploading.value = true
  try {
    const res = await apiFetch(`/api/documentos/${replacingId.value}`, {
      method: 'PUT',
      body: formData
    })
    if (!res.ok) throw new Error('Erro ao substituir arquivo')
    
    showToast('Arquivo substituído com sucesso')
    if (currentTab.value === 'modelos') loadModelos()
  } catch (err) {
    showToast('Erro ao substituir arquivo', 'error')
  } finally {
    isUploading.value = false
    replacingId.value = null
    event.target.value = ''
  }
}

const deleteItem = async (id) => {
  confirmAction('Tem certeza que deseja excluir este modelo permanentemente?', async () => {
    try {
      const endpoint = currentTab.value === 'modelos' ? `/api/modelos/${id}` : `/api/documentos/${id}`
      const res = await apiFetch(endpoint, { method: 'DELETE' })
      if(!res.ok) throw new Error('Erro')
      showToast('Excluído com sucesso')
      if (currentTab.value === 'modelos') loadModelos()
    } catch (err) {
      showToast('Erro ao excluir', 'error')
    }
  }, 'Excluir Modelo', 'red')
}

// ==========================================
// TAGS E AUXILIARES
// ==========================================
const tags = [
  { group: 'Dados do Escritório', items: [
    { label: 'Nome do Escritório', tag: '{{ escritorio_nome }}' },
    { label: 'CNPJ/CPF Escritório', tag: '{{ escritorio_doc }}' },
  ]},
  { group: 'Dados do Cliente', items: [
    { label: 'Nome', tag: '{{ cliente_nome }}' },
    { label: 'Documento (CPF/CNPJ)', tag: '{{ cliente_doc }}' },
    { label: 'Endereço', tag: '{{ cliente_endereco }}' },
    { label: 'E-mail', tag: '{{ cliente_email }}' },
    { label: 'Profissão', tag: '{{ cliente_profissao }}' },
  ]},
  { group: 'Datas e Outros', items: [
    { label: 'Data Hoje', tag: '{{ data_hoje }}' },
    { label: 'Data Extenso', tag: '{{ data_extenso }}' },
    { label: 'IA Conteúdo', tag: '{{ conteudo_ia }}' },
  ]},
]

const copiedTag = ref('')
const copyToClipboard = async (tag) => {
  try {
    await navigator.clipboard.writeText(tag)
    copiedTag.value = tag
    setTimeout(() => copiedTag.value = '', 2000)
  } catch (err) {
    showToast('Erro ao copiar tag', 'error')
  }
}

const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (msg, type = 'success') => {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

const handleDownload = async (item) => {
    try {
        await downloadFile(item.arquivo_path, item.nome + '.' + getFileExtension(item.arquivo_path).toLowerCase())
    } catch (e) {
        showToast(e.message, 'error')
    }
}

const filteredItems = computed(() => {
  const items = modelos.value
  if (!searchQuery.value) return items
  const query = searchQuery.value.toLowerCase()
  return items.filter(m => m.nome.toLowerCase().includes(query))
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const irParaRedator = () => {
    router.push('/redator?context=escritorio')
}

const irParaAssinaturas = (id) => {
    router.push(`/documentos/${id}/assinaturas`)
}

const getStatusClass = (status) => {
    if (status === 'Concluido') return 'bg-emerald-100 text-emerald-700'
    if (status === 'Parcial' || status === 'Pendente') return 'bg-amber-100 text-amber-700'
    return 'bg-slate-100 text-slate-600'
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
    // Mescla pastas e documentos para aplicação da ordenação, 
    // mas mantendo pastas sempre no topo.
    const query = searchQuery.value.toLowerCase()
    
    // Filtragem
    const filteredPastas = [] // Pastas geridas pelo FileExplorer no tab 'internos'
    const currentDocs = modelos.value
    const filteredDocs = currentDocs.filter(d => d.nome.toLowerCase().includes(query))
    
    // Ordenação
    const sorter = (a, b) => {
        if (sortBy.value === 'data') {
            const dateA = new Date(a.data_alteracao || a.data_criacao || 0)
            const dateB = new Date(b.data_alteracao || b.data_criacao || 0)
            return dateB - dateA // Recentes primeiro
        } else {
            return a.nome.localeCompare(b.nome)
        }
    }
    
    return {
        pastas: [...filteredPastas].sort(sorter),
        docs: [...filteredDocs].sort(sorter)
    }
})

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

onMounted(() => {
  if (currentTab.value === 'modelos') loadModelos()
  carregarDadosBase()
})
</script>

<template>
  <div class="h-screen flex bg-slate-50 font-sans overflow-hidden">
    <Sidebar :escritorio="escritorio" :usuario="currentUser" :sidebarOpen="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden relative">
      <!-- HEADER -->
      <header class="bg-white border-b border-slate-200 px-4 sm:px-8 py-5 flex flex-col gap-4 z-10">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div class="flex items-center gap-4">
            <button @click="sidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-500 hover:text-slate-900 focus:outline-none">
                <FileText class="h-6 w-6" />
            </button>
            <div class="min-w-0">
                <h1 class="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2 truncate">
                    <Building2 class="w-6 h-6 text-primary-600 flex-shrink-0" /> Docs do Escritório
                </h1>
                <p class="text-xs sm:text-sm text-slate-500 font-medium truncate">Gestão centralizada de modelos e documentos internos</p>
            </div>
            </div>
            
            <div class="flex flex-wrap items-center gap-2 sm:gap-3">
                <button @click="triggerUpload" :disabled="isUploading" class="flex items-center gap-2 px-3 sm:px-5 py-2 sm:py-2.5 bg-primary-600 text-white rounded-xl text-xs sm:text-sm font-bold shadow-sm hover:shadow-md hover:bg-primary-700 transition-all disabled:opacity-50">
                    <Plus class="w-4 h-4" /> <span>Novo Modelo</span>
                </button>
            </div>
        </div>

        <!-- TABS (Corrigido para evitar remoção de botões do FileExplorer) -->
        <div class="flex gap-8 border-b border-slate-100 -mb-5 pt-2">
            <button @click="currentTab = 'modelos'; loadModelos()" 
                    :class="[currentTab === 'modelos' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-400 hover:text-slate-600', 'pb-4 border-b-2 font-bold text-sm transition-all']">
                Modelos de Automação
            </button>
            <button @click="currentTab = 'internos'" 
                    :class="[currentTab === 'internos' ? 'border-primary-500 text-primary-600' : 'border-transparent text-slate-400 hover:text-slate-600', 'pb-4 border-b-2 font-bold text-sm transition-all']">
                Documentos Internos
            </button>
        </div>
      </header>

      <!-- CONTENT -->
      <div class="flex-1 flex overflow-hidden">
        <main class="flex-1 overflow-y-auto p-8">
          <div class="max-w-5xl mx-auto space-y-6">
            
            <!-- Conteúdo da Aba Internos (Componentizado) -->
            <div v-show="currentTab === 'internos'" class="animate-fade-in-up">
                <FileExplorer 
                    contextType="escritorio" 
                    :contextId="escritorio?.id || 0"
                    title="Documentos Internos do Escritório"
                />
            </div>

            <div v-show="currentTab === 'modelos'" class="space-y-6">
                <!-- Busca e Ordenação Modelos -->
                <div class="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                    <div class="relative max-w-md w-full">
                        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <input v-model="searchQuery" type="text" placeholder="Pesquisar modelos..." 
                               class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 transition-all text-sm font-medium" />
                    </div>
                    <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
                        <button @click="sortBy = 'nome'" :class="['px-3 py-1.5 rounded-lg text-xs font-black transition-all', sortBy === 'nome' ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">
                            A-Z
                        </button>
                        <button @click="sortBy = 'data'" :class="['px-3 py-1.5 rounded-lg text-xs font-black transition-all', sortBy === 'data' ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">
                            Recentes
                        </button>
                    </div>
                </div>

                <div v-if="loading" class="flex flex-col items-center justify-center py-20">
                    <RefreshCw class="h-8 w-8 text-primary-500 animate-spin mb-4" />
                    <p class="text-slate-500 font-medium">Carregando modelos...</p>
                </div>

                <div v-else-if="filteredItems.length === 0" class="text-center bg-white rounded-3xl border border-slate-200 border-dashed p-20">
                    <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
                        <FileText class="h-8 w-8 text-slate-300" />
                    </div>
                    <h3 class="text-xl font-black text-slate-900 mb-2">Sem modelos cadastrados</h3>
                    <p class="text-slate-500 mb-8 max-w-sm mx-auto">Envie seus arquivos .docx com as tags de automação para começar.</p>
                    <button @click="triggerUpload" class="px-8 py-3 bg-primary-600 text-white font-black rounded-2xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-500/20 active:scale-95">
                        Enviar Primeiro Modelo
                    </button>
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- Itens Modelos -->
                    <div v-for="item in sortedContent.docs" :key="item.id" 
                         class="bg-white rounded-[30px] border border-slate-200 shadow-sm hover:shadow-xl hover:border-primary-200 transition-all group flex flex-col overflow-hidden relative">
                        
                        <div class="p-6 flex items-start gap-5">
                            <div class="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 border-2 font-black text-xs tracking-tighter shadow-sm"
                                 :class="getExtensionColor(getFileExtension(item.arquivo_path))">
                                {{ getFileExtension(item.arquivo_path) }}
                            </div>
                            <div class="min-w-0 flex-1">
                                <h3 class="text-slate-900 font-black truncate text-lg mb-1" :title="item.nome">{{ item.nome }}</h3>
                                <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                                    {{ formatSize(item.tamanho) }} • {{ formatDate(item.data_alteracao || item.data_criacao) }}
                                </p>
                            </div>
                        </div>

                        <div class="mt-auto px-6 py-5 border-t border-slate-50 bg-slate-50/50 flex items-center justify-between">
                            <div class="flex gap-2">
                                <button @click="handleDownload(item)" class="p-3 bg-white text-slate-400 hover:text-primary-600 rounded-2xl transition-all border border-slate-100 shadow-sm hover:shadow-md" title="Download">
                                    <FileDown class="w-5 h-5" />
                                </button>
                                <button @click="triggerReplace(item.id)" class="p-3 bg-white text-slate-400 hover:text-amber-500 rounded-2xl transition-all border border-slate-100 shadow-sm hover:shadow-md" title="Substituir">
                                    <UploadCloud class="w-5 h-5" />
                                </button>
                            </div>
                            <button @click="deleteItem(item.id)" class="p-3 bg-white text-slate-400 hover:text-red-500 rounded-2xl transition-all border border-slate-100 shadow-sm hover:shadow-md" title="Excluir">
                                <Trash2 class="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </main>

        <!-- Sidebar TAGS -->
        <aside v-if="currentTab === 'modelos'" class="w-80 border-l border-slate-200 bg-white flex flex-col flex-shrink-0 hidden xl:flex">
          <div class="px-6 py-6 border-b border-slate-100 bg-slate-50/30">
            <h2 class="text-base font-bold text-slate-900 flex items-center gap-2">
              <Tag class="w-4 h-4 text-primary-500" /> Tags de Automação
            </h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed font-medium">
              Cole estas tags no seu documento Word. O Redator Inteligente as preencherá automaticamente.
            </p>
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-8">
            <div v-for="grupo in tags" :key="grupo.group" class="space-y-4">
              <h3 class="text-[10px] font-black text-slate-300 uppercase tracking-widest px-2">
                {{ grupo.group }}
              </h3>
              <div class="space-y-1">
                <button v-for="item in grupo.items" :key="item.tag" @click="copyToClipboard(item.tag)"
                        class="w-full flex flex-col items-start px-3 py-2.5 rounded-xl text-left hover:bg-primary-50 group transition-all">
                  <div class="w-full flex items-center justify-between">
                    <span class="text-sm font-bold text-slate-700 group-hover:text-primary-700">{{ item.label }}</span>
                    <CheckCircle2 v-if="copiedTag === item.tag" class="w-3.5 h-3.5 text-emerald-500" />
                    <Copy v-else class="w-3.5 h-3.5 text-slate-300 group-hover:text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                  <code :class="['text-[10px] mt-1.5 px-2 py-0.5 rounded font-mono', 
                                 copiedTag === item.tag ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500 group-hover:bg-primary-100 group-hover:text-primary-600']">
                    {{ item.tag }}
                  </code>
                </button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Hidden Inputs para Modelos -->
    <input type="file" ref="fileInput" class="hidden" @change="handleFileUpload" />
    <input type="file" ref="replaceInput" class="hidden" @change="handleReplaceUpload" />

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-xl p-6 max-w-sm w-full mx-4 animate-fade-in-up">
        <div class="text-center">
          <div :class="['mx-auto flex items-center justify-center h-12 w-12 rounded-full mb-4', confirmDialog.type === 'purple' ? 'bg-purple-100' : 'bg-red-100']">
            <Sparkles v-if="confirmDialog.type === 'purple'" class="h-6 w-6 text-purple-600" />
            <Trash2 v-else class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg font-bold text-slate-900 mb-2">{{ confirmDialog.title }}</h3>
          <p class="text-sm text-slate-500 mb-6">{{ confirmDialog.message }}</p>
          <div class="flex gap-3 justify-center">
            <button @click="confirmDialog.show = false" class="px-5 py-2 bg-slate-100 text-slate-700 rounded-xl font-bold hover:bg-slate-200 transition-colors">Cancelar</button>
            <button @click="executeConfirm" :class="['px-5 py-2 rounded-lg font-bold text-white transition-all', confirmDialog.type === 'purple' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-red-600 hover:bg-red-700']">
                Confirmar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in-up { animation: fade-in-up 0.4s ease-out; }
@keyframes fade-in-up {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
